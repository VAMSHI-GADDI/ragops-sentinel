from __future__ import annotations
from ragops.evaluation.text_utils import keyword_coverage, split_sentences, tokenize, jaccard
from ragops.evaluation.types import EvaluationExample, EvaluationScores
from ragops.retrieval.types import RetrievedEvidence
from ragops.sentinel.failure_classifier import Diagnosis
from ragops.sentinel.freshness import stale_evidence_rate
from ragops.sentinel.drift import compute_evidence_drift_features


def context_precision(evidence: list[RetrievedEvidence], expected_document_ids: list[str], expected_keywords: list[str]) -> float:
    """Transparent context precision baseline.

    A retrieved chunk is relevant when it comes from an expected document or contains
    at least one expected keyword. This is intentionally simple so the metric is
    reproducible without paid LLM judges.
    """
    if not evidence:
        return 0.0
    expected_docs = set(expected_document_ids)
    relevant = 0
    for ev in evidence:
        doc_hit = ev.document_id in expected_docs
        keyword_hit = keyword_coverage(ev.text, expected_keywords) > 0
        if doc_hit or keyword_hit:
            relevant += 1
    return relevant / len(evidence)


def context_recall(evidence: list[RetrievedEvidence], expected_document_ids: list[str]) -> float:
    if not expected_document_ids:
        return 0.0
    expected_docs = set(expected_document_ids)
    retrieved_docs = {ev.document_id for ev in evidence}
    return len(expected_docs & retrieved_docs) / len(expected_docs)


def answer_relevance(answer: str, expected_keywords: list[str]) -> float:
    return keyword_coverage(answer, expected_keywords)


def faithfulness(answer: str, evidence: list[RetrievedEvidence]) -> float:
    """Approximate citation-groundedness without an LLM judge.

    For each answer sentence, compute token overlap with the retrieved context. A
    sentence is considered supported when it has moderate lexical overlap. This is
    not a final research metric; it is the Milestone-2 deterministic baseline.
    """
    sentences = [s for s in split_sentences(answer) if not s.lower().startswith("this baseline")]
    if not sentences:
        return 0.0
    context_tokens = tokenize("\n".join(ev.text for ev in evidence))
    if not context_tokens:
        return 0.0
    supported = 0
    for sentence in sentences:
        score = jaccard(tokenize(sentence), context_tokens)
        if score >= 0.08:
            supported += 1
    return supported / len(sentences)


def unsupported_claim_rate(answer: str, evidence: list[RetrievedEvidence]) -> float:
    return 1.0 - faithfulness(answer, evidence)


def evaluate_example(
    example: EvaluationExample,
    evidence: list[RetrievedEvidence],
    answer: str,
    diagnosis: Diagnosis,
) -> EvaluationScores:
    drift_features = compute_evidence_drift_features(evidence)
    diagnosis_correct = None
    if example.failure_type:
        diagnosis_correct = diagnosis.failure_code == example.failure_type
    return EvaluationScores(
        example_id=example.example_id,
        context_precision=round(context_precision(evidence, example.expected_document_ids, example.expected_keywords), 4),
        context_recall=round(context_recall(evidence, example.expected_document_ids), 4),
        answer_relevance=round(answer_relevance(answer, example.expected_keywords), 4),
        faithfulness=round(faithfulness(answer, evidence), 4),
        unsupported_claim_rate=round(unsupported_claim_rate(answer, evidence), 4),
        stale_evidence_rate=round(stale_evidence_rate(evidence), 4),
        retrieved_chunks=len(evidence),
        failure_detected=diagnosis.failure_detected,
        failure_code=diagnosis.failure_code,
        expected_failure_type=example.failure_type,
        diagnosis_correct=diagnosis_correct,
        stale_chunks=drift_features.stale_chunks,
        conflicting_versions_detected=drift_features.conflicting_versions_detected,
    )
