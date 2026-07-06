from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Make the script runnable from a fresh checkout on Windows without requiring
# users to set PYTHONPATH manually.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ragops.db import SessionLocal, init_db
from ragops.ingestion.loaders import load_text_files
from ragops.ingestion.versioning import ingest_document
from ragops.retrieval.vector_qdrant import QdrantRetriever


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest raw documents into metadata DB and Qdrant.")
    parser.add_argument("--raw-dir", default="data/raw", help="Directory containing .md/.txt files")
    parser.add_argument("--valid-from", default=None, help="Optional ISO date for document validity start")
    args = parser.parse_args()

    init_db()
    retriever = QdrantRetriever()
    retriever.ensure_collection()

    files = load_text_files(Path(args.raw_dir))
    if not files:
        print(f"No .md or .txt files found in {args.raw_dir}")
        return

    total_chunks = 0
    with SessionLocal() as session:
        for path, text in files:
            version, chunks = ingest_document(session, path, text, valid_from=args.valid_from)
            retriever.upsert_chunks(chunks)
            total_chunks += len(chunks)
            print(f"Ingested {path} -> {version.version_id} ({len(chunks)} chunks)")
    print(f"Done. Indexed {len(files)} files and {total_chunks} chunks.")


if __name__ == "__main__":
    main()
