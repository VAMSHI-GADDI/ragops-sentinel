from ragops.evaluation.types import EvaluationScores
from ragops.retrieval.types import RetrievedEvidence
from ragops.sentinel.diagnosis_graph import build_diagnosis_graph, compute_graph_risk_score
from ragops.sentinel.failure_classifier import Diagnosis


def _evidence(stale: bool = False):
    return [
        RetrievedEvidence(
            chunk_id="doc:v1:c1",
            text="The current retention period is 90 days.",
            score=0.82,
            document_id="retention_policy",
            version_id="retention_policy:v2",
            section_title="Policy",
            freshness_score=1.0,
        ),
        RetrievedEvidence(
            chunk_id="doc:v0:c1",
            text="The old retention period was 7 days.",
            score=0.31,
            document_id="retention_policy",
            version_id="retention_policy:v1",
            section_title="Policy",
            freshness_score=0.25 if stale else 1.0,
        ),
    ]


def test_diagnosis_graph_contains_core_nodes_and_edges():
    diagnosis = Diagnosis(
        failure_detected=True,
        failure_code="F2_STALE_DOCUMENT",
        root_component="temporal_evidence_layer",
        confidence=0.9,
        recommended_repair="TEMPORAL_FILTER_RETRIEVAL",
        evidence=["One stale chunk was retrieved."],
    )
    evaluation = EvaluationScores(
        example_id="eval_x",
        context_precision=0.5,
        context_recall=1.0,
        answer_relevance=1.0,
        faithfulness=0.8,
        unsupported_claim_rate=0.2,
        stale_evidence_rate=0.5,
        retrieved_chunks=2,
        failure_detected=True,
        failure_code="F2_STALE_DOCUMENT",
        expected_failure_type="F2_STALE_DOCUMENT",
        diagnosis_correct=True,
        stale_chunks=1,
        conflicting_versions_detected=True,
    )
    graph = build_diagnosis_graph(
        query_id="q1",
        answer_id="a1",
        query_text="What is the current retention period?",
        answer_text="The retention period is 90 days.",
        evidence=_evidence(stale=True),
        diagnosis=diagnosis,
        metrics={"latency_ms": 12.0},
        evaluation=evaluation,
    )
    payload = graph.to_dict()
    node_types = {node["node_type"] for node in payload["nodes"]}
    edge_types = {edge["edge_type"] for edge in payload["edges"]}

    assert {"Query", "RetrievalRun", "EvidenceSet", "Answer", "FailureDiagnosis"}.issubset(node_types)
    assert "STALE_EVIDENCE_SIGNAL" in edge_types
    assert payload["summary"]["failure_code"] == "F2_STALE_DOCUMENT"
    assert payload["summary"]["graph_risk_level"] in {"medium", "high"}
    assert "digraph SentinelDiagnosisGraph" in graph.to_dot()


def test_graph_risk_score_increases_with_stale_failure():
    no_failure = Diagnosis(False, None, None, 0.8, None, ["No failure"])
    stale_failure = Diagnosis(True, "F2_STALE_DOCUMENT", "temporal_evidence_layer", 0.9, "TEMPORAL_FILTER_RETRIEVAL", [])
    clean_score, _ = compute_graph_risk_score(_evidence(stale=False), no_failure, None)
    stale_score, components = compute_graph_risk_score(_evidence(stale=True), stale_failure, None)
    assert stale_score > clean_score
    assert components["stale_component"] > 0
    assert components["failure_component"] == 1.0
