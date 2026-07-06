from __future__ import annotations
import re

_WORD_RE = re.compile(r"[A-Za-z0-9_]+")


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def tokenize(text: str) -> set[str]:
    return {m.group(0).lower() for m in _WORD_RE.finditer(text)}


def keyword_coverage(text: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    normalized = normalize_text(text)
    hits = sum(1 for kw in keywords if normalize_text(kw) in normalized)
    return hits / len(keywords)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
