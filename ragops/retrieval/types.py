from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RetrievedEvidence:
    chunk_id: str
    text: str
    score: float
    document_id: str
    version_id: str
    section_title: str
    freshness_score: float
