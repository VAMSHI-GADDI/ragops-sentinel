from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TextChunk:
    text: str
    section_title: str
    start_char: int
    end_char: int


def header_aware_chunks(text: str, max_chars: int = 900, overlap: int = 120) -> list[TextChunk]:
    """Simple markdown/header-aware chunker.

    This is intentionally deterministic for reproducible experiments.
    """
    if max_chars <= overlap:
        raise ValueError("max_chars must be larger than overlap")

    lines = text.splitlines(keepends=True)
    chunks: list[TextChunk] = []
    current_section = ""
    buffer = ""
    buffer_start = 0
    cursor = 0

    def flush(end_cursor: int) -> None:
        nonlocal buffer, buffer_start
        clean = buffer.strip()
        if clean:
            chunks.append(
                TextChunk(
                    text=clean,
                    section_title=current_section,
                    start_char=buffer_start,
                    end_char=end_cursor,
                )
            )
        if overlap > 0 and len(buffer) > overlap:
            buffer = buffer[-overlap:]
            buffer_start = max(0, end_cursor - overlap)
        else:
            buffer = ""
            buffer_start = end_cursor

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            current_section = stripped.lstrip("#").strip() or current_section
        if not buffer:
            buffer_start = cursor
        buffer += line
        cursor += len(line)
        if len(buffer) >= max_chars:
            flush(cursor)

    if buffer.strip():
        chunks.append(
            TextChunk(
                text=buffer.strip(),
                section_title=current_section,
                start_char=buffer_start,
                end_char=len(text),
            )
        )
    return chunks
