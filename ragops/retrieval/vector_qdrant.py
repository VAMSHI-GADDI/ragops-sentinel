from __future__ import annotations
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from sqlalchemy.orm import Session

from ragops.config import get_settings
from ragops.db import Chunk
from ragops.retrieval.embeddings import HashingEmbeddingModel
from ragops.retrieval.types import RetrievedEvidence


class QdrantRetriever:
    def __init__(self):
        settings = get_settings()
        self.settings = settings
        self.client = QdrantClient(url=settings.qdrant_url)
        self.embedder = HashingEmbeddingModel(settings.embedding_dim)
        self.collection = settings.qdrant_collection

    def ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        if any(c.name == self.collection for c in collections):
            return
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=qm.VectorParams(size=self.settings.embedding_dim, distance=qm.Distance.COSINE),
        )

    def upsert_chunks(self, chunks: list[Chunk]) -> None:
        self.ensure_collection()
        texts = [c.chunk_text for c in chunks]
        vectors = self.embedder.embed(texts)
        points = []
        for chunk, vector in zip(chunks, vectors):
            payload: dict[str, Any] = {
                "chunk_id": chunk.chunk_id,
                "version_id": chunk.version_id,
                "document_id": chunk.version.document_id if chunk.version else chunk.version_id.split(":")[0],
                "section_title": chunk.section_title,
                "text": chunk.chunk_text,
                "is_latest": bool(chunk.version.is_latest) if chunk.version else True,
            }
            point_id = abs(hash(chunk.chunk_id)) % (2**63)
            points.append(qm.PointStruct(id=point_id, vector=vector, payload=payload))
        if points:
            self.client.upsert(collection_name=self.collection, points=points)

    def search(self, session: Session, query: str, top_k: int = 5, latest_only: bool = False) -> list[RetrievedEvidence]:
        self.ensure_collection()
        query_vector = self.embedder.embed_one(query)
        query_filter = None
        if latest_only:
            query_filter = qm.Filter(
                must=[qm.FieldCondition(key="is_latest", match=qm.MatchValue(value=True))]
            )

        # qdrant-client has evolved names for search/query APIs. Try query_points first,
        # then fall back to search for older versions.
        try:
            result = self.client.query_points(
                collection_name=self.collection,
                query=query_vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
            ).points
        except Exception:
            result = self.client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
            )

        evidence: list[RetrievedEvidence] = []
        for item in result:
            payload = item.payload or {}
            chunk_id = str(payload.get("chunk_id"))
            chunk = session.get(Chunk, chunk_id)
            if not chunk:
                continue
            freshness_score = 1.0 if payload.get("is_latest", True) else 0.25
            evidence.append(
                RetrievedEvidence(
                    chunk_id=chunk_id,
                    text=chunk.chunk_text,
                    score=float(item.score),
                    document_id=str(payload.get("document_id", "")),
                    version_id=str(payload.get("version_id", "")),
                    section_title=str(payload.get("section_title", "")),
                    freshness_score=freshness_score,
                )
            )
        return evidence
