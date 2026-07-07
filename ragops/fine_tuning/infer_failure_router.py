from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class FailureRouterPrediction:
    failure_code: str
    repair_action: str
    confidence: float
    reason: str


def predict_failure_route(
    *,
    query: str,
    evidence_summary: str,
    metrics: dict[str, Any],
) -> FailureRouterPrediction:
    query_lower = query.lower()
    evidence_lower = evidence_summary.lower()

    if "ignore previous" in query_lower or "system prompt" in query_lower:
        return FailureRouterPrediction(
            failure_code="F20_PROMPT_INJECTION",
            repair_action="BLOCK_OR_HUMAN_REVIEW",
            confidence=0.95,
            reason="prompt_injection_pattern_detected",
        )

    if "token" in query_lower or "shell" in query_lower or "environment" in query_lower:
        return FailureRouterPrediction(
            failure_code="F21_UNSAFE_TOOL_CALL",
            repair_action="BLOCK_TOOL_CALL",
            confidence=0.93,
            reason="unsafe_tool_or_secret_request",
        )

    if metrics.get("pii_detected", 0) or "@" in query or "phone" in query_lower:
        return FailureRouterPrediction(
            failure_code="F23_PII_DETECTED",
            repair_action="REDACT_PII",
            confidence=0.90,
            reason="pii_signal_detected",
        )

    if metrics.get("source_policy_failed", 0) or "untrusted" in evidence_lower:
        return FailureRouterPrediction(
            failure_code="F22_UNTRUSTED_SOURCE",
            repair_action="RETRIEVE_ALLOWLISTED_SOURCES",
            confidence=0.88,
            reason="source_policy_signal_detected",
        )

    if "without citing" in query_lower or metrics.get("missing_citation", 0):
        return FailureRouterPrediction(
            failure_code="F12_MISSING_CITATION",
            repair_action="REQUIRE_CITATIONS",
            confidence=0.86,
            reason="citation_policy_signal_detected",
        )

    if float(metrics.get("stale_evidence_rate", 0.0)) > 0:
        return FailureRouterPrediction(
            failure_code="F2_STALE_DOCUMENT",
            repair_action="TEMPORAL_FILTER_RETRIEVAL",
            confidence=0.84,
            reason="stale_evidence_metric_detected",
        )

    return FailureRouterPrediction(
        failure_code="NO_FAILURE",
        repair_action="NO_REPAIR",
        confidence=0.80,
        reason="no_failure_signal_detected",
    )


def predict_failure_route_dict(**kwargs: Any) -> dict[str, object]:
    return asdict(predict_failure_route(**kwargs))
