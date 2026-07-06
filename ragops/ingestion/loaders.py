from __future__ import annotations
from pathlib import Path

SUPPORTED_EXTENSIONS = {".md", ".txt"}


def load_text_files(raw_dir: str | Path) -> list[tuple[Path, str]]:
    raw_path = Path(raw_dir)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data directory not found: {raw_path}")
    files: list[tuple[Path, str]] = []
    for path in sorted(raw_path.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append((path, path.read_text(encoding="utf-8")))
    return files
