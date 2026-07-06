from __future__ import annotations
import time
import uuid
from fastapi import Depends, FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy.orm import Session

from apps.api.schemas import Citation, DiagnosisGraphRequest, DiagnosisGraphResponse, DiagnosisResponse, EvaluationRequest, EvaluationResponse, QueryRequest, QueryResponse, RepairRequest, RepairResponse
from ragops.db import AnswerRun, QueryRun, RetrievalRun, RetrievedChunk, get_session, init_db
from ragops.evaluation.rag_metrics import answer_relevance as eval_answer_relevance, faithfulness as eval_faithfulness, unsupported_claim_rate as eval_unsupported_claim_rate
from ragops.evaluation.types import EvaluationExample
from ragops.retrieval.types import RetrievedEvidence
from ragops.generation.generator import ExtractiveBaselineGenerator
from ragops.observability.metrics import (
    FAILURE_COUNT,
    GRAPH_RISK_LEVEL,
    GRAPH_RISK_SCORE,
    QUERY_COUNT,
    QUERY_LATENCY,
    RETRIEVAL_LATENCY,
    risk_level_to_numeric,
    record_evaluation_observability,
    record_repair_observability,
    record_retrieval_observability,
)
from ragops.observability.mlflow_logger import log_query_run
from ragops.retrieval.vector_qdrant import QdrantRetriever
from ragops.sentinel.diagnosis_graph import build_diagnosis_graph
from ragops.sentinel.failure_classifier import RuleBasedFailureClassifier
from ragops.sentinel.freshness import stale_evidence_rate
from ragops.sentinel.repair import apply_repair_for_example

app = FastAPI(title="RAGOps Sentinel", version="0.1.0")
retriever = QdrantRetriever()
generator = ExtractiveBaselineGenerator()
classifier = RuleBasedFailureClassifier()


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    retriever.ensure_collection()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ragops-sentinel"}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest, session: Session = Depends(get_session)) -> QueryResponse:
    QUERY_COUNT.inc()
    total_start = time.perf_counter()
    query_id = f"q_{uuid.uuid4().hex[:12]}"
    answer_id = f"a_{uuid.uuid4().hex[:12]}"
    retrieval_run_id = f"r_{uuid.uuid4().hex[:12]}"

    session.add(QueryRun(query_id=query_id, query_text=request.query))
    session.commit()

    retrieval_start = time.perf_counter()
    evidence = retriever.search(session, request.query, top_k=request.top_k, latest_only=request.latest_only)
    retrieval_latency = time.perf_counter() - retrieval_start
    RETRIEVAL_LATENCY.observe(retrieval_latency)

    retrieval_run = RetrievalRun(
        retrieval_run_id=retrieval_run_id,
        query_id=query_id,
        retrieval_type="qdrant_hash_baseline",
        top_k=request.top_k,
        latency_ms=retrieval_latency * 1000,
    )
    session.add(retrieval_run)
    for rank, ev in enumerate(evidence, start=1):
        session.add(
            RetrievedChunk(
                retrieval_run_id=retrieval_run_id,
                chunk_id=ev.chunk_id,
                rank=rank,
                score=ev.score,
                freshness_score=ev.freshness_score,
            )
        )
    session.commit()

    answer = generator.generate(request.query, evidence)
    session.add(AnswerRun(answer_id=answer_id, query_id=query_id, answer_text=answer))
    session.commit()

    diagnosis = classifier.diagnose(request.query, evidence, answer)
    if diagnosis.failure_detected and diagnosis.failure_code:
        FAILURE_COUNT.labels(failure_code=diagnosis.failure_code).inc()

    stale_rate = stale_evidence_rate(evidence)
    record_retrieval_observability(
        retrieved_chunks=len(evidence),
        stale_chunks=sum(1 for ev in evidence if ev.freshness_score < 1.0),
        stale_evidence_rate=stale_rate,
        low_score_chunks=sum(1 for ev in evidence if ev.score < 0.15),
    )

    total_latency = time.perf_counter() - total_start
    QUERY_LATENCY.observe(total_latency)

    metrics_payload = {
        "latency_ms": round(total_latency * 1000, 2),
        "retrieval_latency_ms": round(retrieval_latency * 1000, 2),
        "stale_evidence_rate": round(stale_rate, 4),
        "retrieved_chunks": float(len(evidence)),
    }
    log_query_run(metrics_payload, params={"top_k": request.top_k, "latest_only": request.latest_only})

    return QueryResponse(
        query_id=query_id,
        answer_id=answer_id,
        answer=answer,
        citations=[
            Citation(
                chunk_id=ev.chunk_id,
                document_id=ev.document_id,
                version_id=ev.version_id,
                section_title=ev.section_title,
                score=ev.score,
                freshness_score=ev.freshness_score,
            )
            for ev in evidence
        ],
        diagnosis=DiagnosisResponse(
            failure_detected=diagnosis.failure_detected,
            failure_code=diagnosis.failure_code,
            root_component=diagnosis.root_component,
            confidence=diagnosis.confidence,
            recommended_repair=diagnosis.recommended_repair,
            evidence=diagnosis.evidence,
        ),
        metrics=metrics_payload,
    )


@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate_payload(request: EvaluationRequest) -> EvaluationResponse:
    evidence = [
        RetrievedEvidence(
            chunk_id=f"manual_context_{idx}",
            text=context,
            score=1.0,
            document_id="manual",
            version_id="manual",
            section_title="manual",
            freshness_score=1.0,
        )
        for idx, context in enumerate(request.contexts, start=1)
    ]
    payload = {
        "answer_relevance": round(eval_answer_relevance(request.answer, request.expected_keywords), 4),
        "faithfulness": round(eval_faithfulness(request.answer, evidence), 4),
        "unsupported_claim_rate": round(eval_unsupported_claim_rate(request.answer, evidence), 4),
    }
    record_evaluation_observability(payload)
    return EvaluationResponse(
        context_count=len(evidence),
        answer_relevance=payload["answer_relevance"],
        faithfulness=payload["faithfulness"],
        unsupported_claim_rate=payload["unsupported_claim_rate"],
    )


@app.post("/diagnosis-graph", response_model=DiagnosisGraphResponse)
def diagnosis_graph(request: DiagnosisGraphRequest, session: Session = Depends(get_session)) -> DiagnosisGraphResponse:
    """Return a Sentinel Diagnosis Graph for one query.

    This endpoint is intended for debugging/research artifacts, not for final
    user-facing answers. It builds the same retrieval/generation/diagnosis path
    as /query and returns graph nodes, edges, and risk summary.
    """
    query_id = f"q_{uuid.uuid4().hex[:12]}"
    answer_id = f"a_{uuid.uuid4().hex[:12]}"
    retrieval_run_id = f"r_{uuid.uuid4().hex[:12]}"

    retrieval_start = time.perf_counter()
    evidence = retriever.search(session, request.query, top_k=request.top_k, latest_only=request.latest_only)
    retrieval_latency = time.perf_counter() - retrieval_start
    answer = generator.generate(request.query, evidence)
    diagnosis = classifier.diagnose(request.query, evidence, answer)
    stale_rate = stale_evidence_rate(evidence)

    graph = build_diagnosis_graph(
        query_id=query_id,
        answer_id=answer_id,
        query_text=request.query,
        answer_text=answer,
        evidence=evidence,
        diagnosis=diagnosis,
        retrieval_run_id=retrieval_run_id,
        metrics={
            "retrieval_latency_ms": round(retrieval_latency * 1000, 2),
            "top_k": float(request.top_k),
            "latest_only": float(bool(request.latest_only)),
            "stale_evidence_rate": round(stale_rate, 4),
        },
    )
    graph_payload = graph.to_dict()
    GRAPH_RISK_SCORE.set(float(graph_payload["summary"].get("graph_risk_score", 0.0)))
    GRAPH_RISK_LEVEL.set(risk_level_to_numeric(str(graph_payload["summary"].get("graph_risk_level", "unknown"))))
    return DiagnosisGraphResponse(graph=graph_payload)

@app.post("/repair", response_model=RepairResponse)
def repair_query(request: RepairRequest, session: Session = Depends(get_session)) -> RepairResponse:
    """Diagnose one query and apply the Milestone-5 targeted repair policy.

    This endpoint uses a minimal EvaluationExample because online repair may not
    have ground-truth labels. Offline repair experiments should use
    scripts/run_repair_benchmark.py.
    """
    example = EvaluationExample(
        example_id="online_repair",
        query=request.query,
        expected_document_ids=[],
        expected_keywords=[token for token in request.query.split() if len(token) > 3],
        reference_answer=None,
        failure_type=None,
    )
    result = apply_repair_for_example(session=session, example=example, top_k=request.top_k).to_dict()
    record_repair_observability(result)
    record_evaluation_observability(result.get("after_metrics", {}))
    return RepairResponse(
        query=result["query"],
        action=result["action"],
        repair_applied=result["repair_applied"],
        repair_success=result["repair_success"],
        before_diagnosis=result["before_diagnosis"],
        after_diagnosis=result["after_diagnosis"],
        before_metrics=result["before_metrics"],
        after_metrics=result["after_metrics"],
        deltas=result["deltas"],
        before_version_ids=result["before_version_ids"],
        after_version_ids=result["after_version_ids"],
        latency_ms=result["latency_ms"],
    )

