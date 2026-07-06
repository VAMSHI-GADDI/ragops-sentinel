from __future__ import annotations
from datetime import date
from pathlib import Path
from sqlalchemy.orm import Session

from ragops.db import Document, DocumentVersion, Chunk
from ragops.ingestion.chunkers import header_aware_chunks
from ragops.ingestion.hash_utils import stable_hash


def make_document_id(path: Path) -> str:
    return path.stem.lower().replace(" ", "_").replace("-", "_")


def ingest_document(session: Session, path: Path, text: str, valid_from: str | None = None) -> tuple[DocumentVersion, list[Chunk]]:
    valid_from = valid_from or date.today().isoformat()
    document_id = make_document_id(path)
    title = path.stem.replace("_", " ").title()
    content_hash = stable_hash(text)
    version_id = f"{document_id}:{content_hash[:12]}"

    doc = session.get(Document, document_id)
    if doc is None:
        doc = Document(document_id=document_id, title=title, source_path=str(path))
        session.add(doc)

    existing = session.get(DocumentVersion, version_id)
    if existing:
        return existing, list(existing.chunks)

    # Mark older versions as not latest.
    for old_version in doc.versions:
        old_version.is_latest = False
        if old_version.valid_to is None:
            old_version.valid_to = valid_from

    version = DocumentVersion(
        version_id=version_id,
        document_id=document_id,
        content_hash=content_hash,
        valid_from=valid_from,
        valid_to=None,
        is_latest=True,
    )
    session.add(version)
    session.flush()

    chunks: list[Chunk] = []
    for idx, chunk in enumerate(header_aware_chunks(text)):
        chunk_hash = stable_hash(chunk.text)
        chunk_id = f"{version_id}:c{idx:04d}"
        db_chunk = Chunk(
            chunk_id=chunk_id,
            version_id=version_id,
            chunk_text=chunk.text,
            section_title=chunk.section_title,
            start_char=chunk.start_char,
            end_char=chunk.end_char,
            content_hash=chunk_hash,
        )
        session.add(db_chunk)
        chunks.append(db_chunk)
    session.commit()
    return version, chunks
