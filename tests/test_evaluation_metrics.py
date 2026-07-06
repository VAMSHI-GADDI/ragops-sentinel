from ragops.evaluation.rag_metrics import context_precision, context_recall, answer_relevance, faithfulness
from ragops.retrieval.types import RetrievedEvidence


def ev(doc_id: str, text: str, score: float = 0.9) -> RetrievedEvidence:
    return RetrievedEvidence(
        chunk_id=f"{doc_id}:c1",
        text=text,
        score=score,
        document_id=doc_id,
        version_id=f"{doc_id}:v1",
        section_title="test",
        freshness_score=1.0,
    )


def test_context_precision_and_recall():
    evidence = [ev("mlflow_tracking", "MLflow logs metrics and artifacts"), ev("other", "unrelated")]
    assert context_precision(evidence, ["mlflow_tracking"], ["metrics"]) == 0.5
    assert context_recall(evidence, ["mlflow_tracking"]) == 1.0


def test_answer_relevance_and_faithfulness():
    evidence = [ev("mlflow_tracking", "MLflow Tracking logs parameters metrics artifacts and experiment runs.")]
    answer = "MLflow Tracking logs parameters, metrics, artifacts, and experiment runs."
    assert answer_relevance(answer, ["parameters", "metrics", "artifacts"]) == 1.0
    assert faithfulness(answer, evidence) == 1.0
