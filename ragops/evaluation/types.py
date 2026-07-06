from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class EvaluationExample:
    example_id: str
    query: str
    expected_document_ids: list[str]
    expected_keywords: list[str]
    reference_answer: str | None = None
    failure_type: str | None = None


@dataclass
class EvaluationScores:
    example_id: str
    context_precision: float
    context_recall: float
    answer_relevance: float
    faithfulness: float
    unsupported_claim_rate: float
    stale_evidence_rate: float
    retrieved_chunks: int
    failure_detected: bool
    failure_code: str | None
    expected_failure_type: str | None = None
    diagnosis_correct: bool | None = None
    stale_chunks: int = 0
    conflicting_versions_detected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
