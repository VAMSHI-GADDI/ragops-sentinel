from __future__ import annotations

from dataclasses import dataclass, asdict
from time import perf_counter
from typing import Any, TYPE_CHECKING

from sqlalchemy.orm import Session

from ragops.evaluation.rag_metrics import evaluate_example
from ragops.evaluation.types import EvaluationExample
from ragops.generation.generator import ExtractiveBaselineGenerator
from ragops.retrieval.types import RetrievedEvidence
from ragops.sentinel.failure_classifier import Diagnosis, RuleBasedFailureClassifier
from ragops.sentinel.repair_policy import choose_repair

if TYPE_CHECKING:
    from ragops.retrieval.vector_qdrant import QdrantRetriever


@dataclass
class RepairDecision:
    """A transparent repair decision used for Milestone 5.

    The policy is intentionally simple and auditable. Later milestones can replace
    it with a learned policy using diagnosis graph features, telemetry, and cost.
    """

    action: str
    reason: str
    should_retrieve_again: bool
    latest_only: bool
    should_regenerate: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RepairResult:
    query: str
    action: str
    repair_applied: bool
    repair_success: bool
    before_diagnosis: dict[str, Any]
    after_diagnosis: dict[str, Any]
    before_metrics: dict[str, Any]
    after_metrics: dict[str, Any]
    deltas: dict[str, Any]
    before_answer: str
    after_answer: str
    before_version_ids: list[str]
    after_version_ids: list[str]
    latency_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_repair_decision(diagnosis: Diagnosis) -> RepairDecision:
    action = choose_repair(diagnosis)
    if action == "NO_REPAIR":
        return RepairDecision(
            action=action,
            reason="No failure was detected by the current classifier.",
            should_retrieve_again=False,
            latest_only=False,
            should_regenerate=False,
        )
    if action == "TEMPORAL_FILTER_RETRIEVAL":
        return RepairDecision(
            action=action,
            reason="Stale evidence was detected; retrieve only latest valid document versions and regenerate.",
            should_retrieve_again=True,
            latest_only=True,
            should_regenerate=True,
        )
    if action == "QUERY_REWRITE_OR_HYBRID_RETRIEVAL":
        return RepairDecision(
            action=action,
            reason="Retrieval confidence was low. Milestone 5 records the action but does not implement query rewriting yet.",
            should_retrieve_again=False,
            latest_only=False,
            should_regenerate=False,
        )
    if action == "REINDEX_OR_EXPAND_CORPUS":
        return RepairDecision(
            action=action,
            reason="No evidence was retrieved. Milestone 5 records the action but does not modify the corpus automatically.",
            should_retrieve_again=False,
            latest_only=False,
            should_regenerate=False,
        )
    return RepairDecision(
        action=action,
        reason="Fallback repair action selected by policy.",
        should_retrieve_again=False,
        latest_only=False,
        should_regenerate=False,
    )


def _diagnosis_to_dict(diagnosis: Diagnosis) -> dict[str, Any]:
    return {
        "failure_detected": diagnosis.failure_detected,
        "failure_code": diagnosis.failure_code,
        "root_component": diagnosis.root_component,
        "confidence": diagnosis.confidence,
        "recommended_repair": diagnosis.recommended_repair,
        "evidence": diagnosis.evidence,
    }


def _score_delta(after: dict[str, Any], before: dict[str, Any], key: str) -> float:
    return round(float(after.get(key, 0.0)) - float(before.get(key, 0.0)), 4)


def _compute_success(before: dict[str, Any], after: dict[str, Any], action: str) -> bool:
    if action == "NO_REPAIR":
        return False
    stale_reduced = float(after.get("stale_evidence_rate", 0.0)) < float(before.get("stale_evidence_rate", 0.0))
    recall_preserved = float(after.get("context_recall", 0.0)) >= float(before.get("context_recall", 0.0))
    relevance_preserved = float(after.get("answer_relevance", 0.0)) >= float(before.get("answer_relevance", 0.0))
    unsupported_not_worse = float(after.get("unsupported_claim_rate", 1.0)) <= float(before.get("unsupported_claim_rate", 1.0))
    return stale_reduced and recall_preserved and relevance_preserved and unsupported_not_worse


def apply_repair_for_example(
    session: Session,
    example: EvaluationExample,
    retriever: "QdrantRetriever" | None = None,
    generator: ExtractiveBaselineGenerator | None = None,
    classifier: RuleBasedFailureClassifier | None = None,
    top_k: int = 5,
) -> RepairResult:
    """Run diagnosis and targeted repair for one evaluation example.

    Milestone 5 implements one concrete repair path: stale evidence -> latest-only
    temporal retrieval. The function returns before/after metrics so repair impact
    can be measured without hand-waving.
    """

    start = perf_counter()
    if retriever is None:
        from ragops.retrieval.vector_qdrant import QdrantRetriever
        retriever = QdrantRetriever()
    generator = generator or ExtractiveBaselineGenerator()
    classifier = classifier or RuleBasedFailureClassifier()

    before_evidence = retriever.search(session, example.query, top_k=top_k, latest_only=False)
    before_answer = generator.generate(example.query, before_evidence)
    before_diagnosis = classifier.diagnose(example.query, before_evidence, before_answer)
    before_metrics = evaluate_example(example, before_evidence, before_answer, before_diagnosis).to_dict()

    decision = make_repair_decision(before_diagnosis)
    if decision.should_retrieve_again:
        after_evidence = retriever.search(session, example.query, top_k=top_k, latest_only=decision.latest_only)
        after_answer = generator.generate(example.query, after_evidence) if decision.should_regenerate else before_answer
    else:
        after_evidence = before_evidence
        after_answer = before_answer

    after_diagnosis = classifier.diagnose(example.query, after_evidence, after_answer)
    after_metrics = evaluate_example(example, after_evidence, after_answer, after_diagnosis).to_dict()

    deltas = {
        "context_precision_delta": _score_delta(after_metrics, before_metrics, "context_precision"),
        "context_recall_delta": _score_delta(after_metrics, before_metrics, "context_recall"),
        "answer_relevance_delta": _score_delta(after_metrics, before_metrics, "answer_relevance"),
        "faithfulness_delta": _score_delta(after_metrics, before_metrics, "faithfulness"),
        "unsupported_claim_rate_delta": _score_delta(after_metrics, before_metrics, "unsupported_claim_rate"),
        "stale_evidence_rate_delta": _score_delta(after_metrics, before_metrics, "stale_evidence_rate"),
        "stale_chunk_delta": int(after_metrics.get("stale_chunks", 0)) - int(before_metrics.get("stale_chunks", 0)),
    }

    return RepairResult(
        query=example.query,
        action=decision.action,
        repair_applied=decision.action != "NO_REPAIR" and decision.should_retrieve_again,
        repair_success=_compute_success(before_metrics, after_metrics, decision.action),
        before_diagnosis=_diagnosis_to_dict(before_diagnosis),
        after_diagnosis=_diagnosis_to_dict(after_diagnosis),
        before_metrics=before_metrics,
        after_metrics=after_metrics,
        deltas=deltas,
        before_answer=before_answer,
        after_answer=after_answer,
        before_version_ids=[ev.version_id for ev in before_evidence],
        after_version_ids=[ev.version_id for ev in after_evidence],
        latency_ms=round((perf_counter() - start) * 1000, 2),
    )
