from __future__ import annotations
import sys
from pathlib import Path

from qdrant_client import QdrantClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ragops.config import get_settings


def sqlite_path_from_url(database_url: str) -> Path | None:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return None
    raw = database_url[len(prefix):]
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def main() -> None:
    settings = get_settings()
    sqlite_path = sqlite_path_from_url(settings.database_url)
    if sqlite_path and sqlite_path.exists():
        sqlite_path.unlink()
        print(f"Deleted SQLite DB: {sqlite_path}")
    elif sqlite_path:
        print(f"SQLite DB not present: {sqlite_path}")
    else:
        print("DATABASE_URL is not SQLite; DB reset skipped.")

    client = QdrantClient(url=settings.qdrant_url)
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection in collections:
        client.delete_collection(settings.qdrant_collection)
        print(f"Deleted Qdrant collection: {settings.qdrant_collection}")
    else:
        print(f"Qdrant collection not present: {settings.qdrant_collection}")


if __name__ == "__main__":
    main()
