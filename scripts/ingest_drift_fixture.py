from __future__ import annotations
import argparse
import sys
from pathlib import Path

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ragops.db import Chunk, DocumentVersion, SessionLocal, init_db
from ragops.ingestion.versioning import ingest_document
from ragops.retrieval.vector_qdrant import QdrantRetriever


def upsert_all_versions_for_document(session, retriever: QdrantRetriever, document_id: str) -> int:
    chunks = list(
        session.scalars(
            select(Chunk)
            .join(DocumentVersion, Chunk.version_id == DocumentVersion.version_id)
            .where(DocumentVersion.document_id == document_id)
        )
    )
    retriever.upsert_chunks(chunks)
    return len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest old and current evidence-drift fixture versions.")
    parser.add_argument("--fixture-dir", default="data/drift")
    parser.add_argument("--old-valid-from", default="2026-01-01")
    parser.add_argument("--new-valid-from", default="2026-06-01")
    args = parser.parse_args()

    init_db()
    retriever = QdrantRetriever()
    retriever.ensure_collection()
    fixture_dir = Path(args.fixture_dir)
    old_path = fixture_dir / "v1" / "ragops_retention_policy.md"
    new_path = fixture_dir / "v2" / "ragops_retention_policy.md"

    with SessionLocal() as session:
        old_version, _ = ingest_document(session, old_path, old_path.read_text(encoding="utf-8"), valid_from=args.old_valid_from)
        old_count = upsert_all_versions_for_document(session, retriever, old_version.document_id)
        print(f"Ingested OLD version {old_version.version_id}; re-indexed {old_count} chunks for document {old_version.document_id}.")

        new_version, _ = ingest_document(session, new_path, new_path.read_text(encoding="utf-8"), valid_from=args.new_valid_from)
        new_count = upsert_all_versions_for_document(session, retriever, new_version.document_id)
        print(f"Ingested CURRENT version {new_version.version_id}; re-indexed {new_count} chunks for document {new_version.document_id}.")

        versions = list(session.scalars(select(DocumentVersion).where(DocumentVersion.document_id == new_version.document_id)))
        for v in versions:
            print(f"Version status: {v.version_id} latest={v.is_latest} valid_from={v.valid_from} valid_to={v.valid_to}")


if __name__ == "__main__":
    main()
