from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any
import re

from ragops.evaluation.types import EvaluationScores
from ragops.retrieval.types import RetrievedEvidence
from ragops.sentinel.drift import compute_evidence_drift_features
from ragops.sentinel.failure_classifier import Diagnosis


def _safe_id(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_:\-.]+", "_", value.strip())
    return value[:160] if value else "unknown"


@dataclass
class GraphNode:
    node_id: str
    node_type: str
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphEdge:
    source: str
    target: str
    edge_type: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiagnosisGraph:
    graph_id: str
    created_at: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "created_at": self.created_at,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "summary": self.summary,
        }

    def to_dot(self) -> str:
        """Export a Graphviz DOT string for paper/report figures.

        This keeps the project dependency-free: users can render the DOT later
        with Graphviz, but the research artifact is inspectable as plain text.
        """
        lines = ["digraph SentinelDiagnosisGraph {", "  rankdir=LR;", "  node [shape=box];"]
        for node in self.nodes:
            label = f"{node.node_type}: {node.label}".replace('"', "'")
            lines.append(f'  "{node.node_id}" [label="{label}"];')
        for edge in self.edges:
            label = edge.edge_type.replace('"', "'")
            lines.append(f'  "{edge.source}" -> "{edge.target}" [label="{label}"];')
        lines.append("}")
        return "\n".join(lines)


def _risk_level(score: float) -> str:
    if score >= 0.70:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"


def compute_graph_risk_score(
    evidence: list[RetrievedEvidence],
    diagnosis: Diagnosis,
    evaluation: EvaluationScores | None,
) -> tuple[float, dict[str, float]]:
    """Transparent Milestone-4 risk score.

    This is not claimed as a final novel algorithm. It is a reproducible baseline
    that turns evidence drift, diagnosis, and evaluator signals into a single
    graph-level risk score for experiments and ablations.
    """
    drift = compute_evidence_drift_features(evidence)
    stale_component = drift.stale_evidence_rate
    conflict_component = 1.0 if drift.conflicting_versions_detected else 0.0
    failure_component = 1.0 if diagnosis.failure_detected else 0.0
    low_score_component = 0.0
    if evidence:
        low_score_component = sum(1 for ev in evidence if ev.score < 0.15) / len(evidence)

    unsupported_component = evaluation.unsupported_claim_rate if evaluation else 0.0
    context_miss_component = (1.0 - evaluation.context_recall) if evaluation else 0.0

    components = {
        "stale_component": round(stale_component, 4),
        "conflict_component": round(conflict_component, 4),
        "failure_component": round(failure_component, 4),
        "low_score_component": round(low_score_component, 4),
        "unsupported_component": round(unsupported_component, 4),
        "context_miss_component": round(context_miss_component, 4),
    }
    score = (
        0.25 * stale_component
        + 0.20 * conflict_component
        + 0.20 * failure_component
        + 0.10 * low_score_component
        + 0.15 * unsupported_component
        + 0.10 * context_miss_component
    )
    return round(min(1.0, score), 4), components


def build_diagnosis_graph(
    *,
    query_id: str,
    answer_id: str,
    query_text: str,
    answer_text: str,
    evidence: list[RetrievedEvidence],
    diagnosis: Diagnosis,
    retrieval_run_id: str | None = None,
    metrics: dict[str, float] | None = None,
    evaluation: EvaluationScores | None = None,
) -> DiagnosisGraph:
    """Build the Sentinel Diagnosis Graph for one query/answer run.

    The graph is the core Milestone-4 artifact. It links query, retrieval run,
    chunks, document versions, final answer, diagnosis, evaluation signals, and
    operational metrics into one inspectable object.
    """
    metrics = metrics or {}
    retrieval_run_id = retrieval_run_id or f"retrieval:{query_id}"
    graph_id = f"sdg:{_safe_id(query_id)}:{_safe_id(answer_id)}"
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    query_node = f"query:{_safe_id(query_id)}"
    retrieval_node = f"retrieval:{_safe_id(retrieval_run_id)}"
    answer_node = f"answer:{_safe_id(answer_id)}"
    diagnosis_node = f"diagnosis:{_safe_id(query_id)}"
    evidence_set_node = f"evidence_set:{_safe_id(query_id)}"

    drift = compute_evidence_drift_features(evidence)
    risk_score, risk_components = compute_graph_risk_score(evidence, diagnosis, evaluation)

    nodes.extend(
        [
            GraphNode(query_node, "Query", query_text[:80], {"query_id": query_id, "query_text": query_text}),
            GraphNode(
                retrieval_node,
                "RetrievalRun",
                retrieval_run_id,
                {
                    "retrieved_chunks": len(evidence),
                    "stale_chunks": drift.stale_chunks,
                    "stale_evidence_rate": drift.stale_evidence_rate,
                },
            ),
            GraphNode(evidence_set_node, "EvidenceSet", f"{len(evidence)} retrieved chunks", drift.to_dict()),
            GraphNode(answer_node, "Answer", answer_text[:80], {"answer_id": answer_id, "answer_text": answer_text}),
            GraphNode(
                diagnosis_node,
                "FailureDiagnosis",
                diagnosis.failure_code or "NO_FAILURE",
                {
                    "failure_detected": diagnosis.failure_detected,
                    "failure_code": diagnosis.failure_code,
                    "root_component": diagnosis.root_component,
                    "confidence": diagnosis.confidence,
                    "recommended_repair": diagnosis.recommended_repair,
                    "evidence": diagnosis.evidence,
                },
            ),
        ]
    )

    edges.extend(
        [
            GraphEdge(query_node, retrieval_node, "QUERY_TRIGGERED_RETRIEVAL"),
            GraphEdge(retrieval_node, evidence_set_node, "RETRIEVAL_PRODUCED_EVIDENCE"),
            GraphEdge(evidence_set_node, answer_node, "EVIDENCE_USED_BY_ANSWER"),
            GraphEdge(answer_node, diagnosis_node, "ANSWER_DIAGNOSED_AS"),
        ]
    )

    seen_docs: set[str] = set()
    seen_versions: set[str] = set()
    for rank, ev in enumerate(evidence, start=1):
        doc_node = f"document:{_safe_id(ev.document_id)}"
        version_node = f"version:{_safe_id(ev.version_id)}"
        chunk_node = f"chunk:{_safe_id(ev.chunk_id)}"

        if doc_node not in seen_docs:
            nodes.append(GraphNode(doc_node, "Document", ev.document_id, {"document_id": ev.document_id}))
            seen_docs.add(doc_node)
        if version_node not in seen_versions:
            nodes.append(
                GraphNode(
                    version_node,
                    "DocumentVersion",
                    ev.version_id,
                    {
                        "version_id": ev.version_id,
                        "document_id": ev.document_id,
                        "is_latest_in_retrieval": ev.freshness_score >= 1.0,
                    },
                )
            )
            seen_versions.add(version_node)
            edges.append(GraphEdge(doc_node, version_node, "DOCUMENT_HAS_VERSION"))

        nodes.append(
            GraphNode(
                chunk_node,
                "Chunk",
                ev.section_title or ev.chunk_id,
                {
                    "chunk_id": ev.chunk_id,
                    "rank": rank,
                    "score": ev.score,
                    "freshness_score": ev.freshness_score,
                    "section_title": ev.section_title,
                    "text_preview": ev.text[:220],
                },
            )
        )
        edges.extend(
            [
                GraphEdge(version_node, chunk_node, "VERSION_HAS_CHUNK"),
                GraphEdge(retrieval_node, chunk_node, "RETRIEVED_CHUNK", {"rank": rank, "score": ev.score}),
                GraphEdge(chunk_node, evidence_set_node, "CHUNK_IN_EVIDENCE_SET"),
                GraphEdge(chunk_node, answer_node, "CHUNK_CITED_BY_ANSWER", {"freshness_score": ev.freshness_score}),
            ]
        )
        if ev.freshness_score < 1.0:
            edges.append(GraphEdge(chunk_node, diagnosis_node, "STALE_EVIDENCE_SIGNAL", {"freshness_score": ev.freshness_score}))

    if metrics:
        metrics_node = f"metrics:{_safe_id(query_id)}"
        nodes.append(GraphNode(metrics_node, "TelemetryMetrics", "runtime metrics", metrics))
        edges.append(GraphEdge(metrics_node, diagnosis_node, "METRICS_INFORM_DIAGNOSIS"))

    if evaluation:
        eval_node = f"evaluation:{_safe_id(evaluation.example_id)}"
        nodes.append(GraphNode(eval_node, "EvaluationRun", evaluation.example_id, evaluation.to_dict()))
        edges.append(GraphEdge(eval_node, diagnosis_node, "EVALUATION_INFORMS_DIAGNOSIS"))

    summary = {
        "query_id": query_id,
        "answer_id": answer_id,
        "retrieved_chunks": len(evidence),
        "stale_chunks": drift.stale_chunks,
        "stale_evidence_rate": drift.stale_evidence_rate,
        "conflicting_versions_detected": drift.conflicting_versions_detected,
        "failure_detected": diagnosis.failure_detected,
        "failure_code": diagnosis.failure_code,
        "recommended_repair": diagnosis.recommended_repair,
        "graph_risk_score": risk_score,
        "graph_risk_level": _risk_level(risk_score),
        "risk_components": risk_components,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }
    return DiagnosisGraph(
        graph_id=graph_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        nodes=nodes,
        edges=edges,
        summary=summary,
    )
