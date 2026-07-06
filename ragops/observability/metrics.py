from __future__ import annotations

from prometheus_client import Counter, Histogram, Gauge

# Core API traffic metrics
QUERY_COUNT = Counter("rag_query_count", "Total RAG queries processed")
QUERY_LATENCY = Histogram("rag_query_latency_seconds", "End-to-end RAG query latency")
RETRIEVAL_LATENCY = Histogram("rag_retrieval_latency_seconds", "Retrieval latency")

# Retrieval/evidence health metrics
STALE_EVIDENCE_RATE = Gauge("rag_stale_evidence_rate", "Fraction of retrieved chunks that are stale")
STALE_CHUNKS = Gauge("rag_stale_chunks", "Number of stale chunks in the latest observed query")
RETRIEVED_CHUNKS = Gauge("rag_retrieved_chunks", "Number of chunks retrieved in the latest observed query")
LOW_SCORE_CHUNKS = Gauge("rag_low_score_chunks", "Number of low-score retrieved chunks in the latest observed query")

# Evaluation quality metrics
CONTEXT_PRECISION = Gauge("rag_context_precision", "Latest observed context precision score")
CONTEXT_RECALL = Gauge("rag_context_recall", "Latest observed context recall score")
ANSWER_RELEVANCE = Gauge("rag_answer_relevance", "Latest observed answer relevance score")
FAITHFULNESS = Gauge("rag_faithfulness", "Latest observed approximate faithfulness score")
UNSUPPORTED_CLAIM_RATE = Gauge("rag_unsupported_claim_rate", "Latest observed unsupported claim rate")

# Failure/repair/diagnosis metrics
FAILURE_COUNT = Counter("rag_failure_count", "Detected RAG failures", ["failure_code"])
REPAIR_COUNT = Counter("rag_repair_count", "Repair actions attempted", ["action", "success"])
REPAIR_LATENCY = Histogram("rag_repair_latency_seconds", "End-to-end repair latency")
REPAIR_STALE_EVIDENCE_DELTA = Gauge(
    "rag_repair_stale_evidence_delta",
    "Change in stale evidence rate after repair; negative is improvement",
)
GRAPH_RISK_SCORE = Gauge("rag_graph_risk_score", "Latest Sentinel Diagnosis Graph risk score")
GRAPH_RISK_LEVEL = Gauge("rag_graph_risk_level", "Latest graph risk level encoded as low=0, medium=1, high=2")


def record_retrieval_observability(*, retrieved_chunks: int, stale_chunks: int, stale_evidence_rate: float, low_score_chunks: int = 0) -> None:
    """Record retrieval/evidence health metrics for Prometheus.

    This helper keeps API code and scripts aligned. It is intentionally simple:
    the milestone is about exposing production signals, not hiding logic in a
    black-box monitor.
    """
    RETRIEVED_CHUNKS.set(float(retrieved_chunks))
    STALE_CHUNKS.set(float(stale_chunks))
    STALE_EVIDENCE_RATE.set(float(stale_evidence_rate))
    LOW_SCORE_CHUNKS.set(float(low_score_chunks))


def record_evaluation_observability(metrics: dict) -> None:
    """Record quality metrics when an evaluation payload is available."""
    if "context_precision" in metrics:
        CONTEXT_PRECISION.set(float(metrics["context_precision"]))
    if "context_recall" in metrics:
        CONTEXT_RECALL.set(float(metrics["context_recall"]))
    if "answer_relevance" in metrics:
        ANSWER_RELEVANCE.set(float(metrics["answer_relevance"]))
    if "faithfulness" in metrics:
        FAITHFULNESS.set(float(metrics["faithfulness"]))
    if "unsupported_claim_rate" in metrics:
        UNSUPPORTED_CLAIM_RATE.set(float(metrics["unsupported_claim_rate"]))


def record_repair_observability(result: dict) -> None:
    """Record repair outcome metrics from a RepairResult.to_dict() payload."""
    action = str(result.get("action", "UNKNOWN"))
    success = str(bool(result.get("repair_success", False))).lower()
    REPAIR_COUNT.labels(action=action, success=success).inc()
    REPAIR_LATENCY.observe(float(result.get("latency_ms", 0.0)) / 1000.0)
    deltas = result.get("deltas", {}) or {}
    if "stale_evidence_rate_delta" in deltas:
        REPAIR_STALE_EVIDENCE_DELTA.set(float(deltas["stale_evidence_rate_delta"]))


def risk_level_to_numeric(level: str) -> float:
    mapping = {"low": 0.0, "medium": 1.0, "high": 2.0}
    return mapping.get(level.lower(), -1.0)
