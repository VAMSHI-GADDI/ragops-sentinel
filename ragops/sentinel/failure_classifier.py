from __future__ import annotations
from dataclasses import dataclass
from ragops.retrieval.types import RetrievedEvidence
from ragops.sentinel.freshness import stale_evidence_rate


@dataclass
class Diagnosis:
    failure_detected: bool
    failure_code: str | None
    root_component: str | None
    confidence: float
    recommended_repair: str | None
    evidence: list[str]


class RuleBasedFailureClassifier:
    """Milestone-1 transparent baseline.

    Later milestones will replace/augment this with a trained classifier using
    retrieval metrics, evaluator signals, telemetry, and version-graph features.
    """

    def diagnose(self, query: str, evidence: list[RetrievedEvidence], answer: str) -> Diagnosis:
        if not evidence:
            return Diagnosis(
                failure_detected=True,
                failure_code="F1_MISSING_EVIDENCE",
                root_component="retrieval_or_ingestion",
                confidence=0.75,
                recommended_repair="REINDEX_OR_EXPAND_CORPUS",
                evidence=["No chunks were retrieved for the query."],
            )

        stale_rate = stale_evidence_rate(evidence)
        if stale_rate > 0:
            return Diagnosis(
                failure_detected=True,
                failure_code="F2_STALE_DOCUMENT",
                root_component="temporal_evidence_layer",
                confidence=min(0.95, 0.60 + stale_rate),
                recommended_repair="TEMPORAL_FILTER_RETRIEVAL",
                evidence=[f"{stale_rate:.2%} of retrieved chunks are not marked as latest."],
            )

        low_scores = [ev.score for ev in evidence if ev.score < 0.15]
        if len(low_scores) == len(evidence):
            return Diagnosis(
                failure_detected=True,
                failure_code="F6_RETRIEVAL_LOW_CONFIDENCE",
                root_component="retriever",
                confidence=0.65,
                recommended_repair="QUERY_REWRITE_OR_HYBRID_RETRIEVAL",
                evidence=["All retrieved chunks have very low similarity scores."],
            )

        return Diagnosis(
            failure_detected=False,
            failure_code=None,
            root_component=None,
            confidence=0.80,
            recommended_repair=None,
            evidence=["No baseline failure rule fired."],
        )
