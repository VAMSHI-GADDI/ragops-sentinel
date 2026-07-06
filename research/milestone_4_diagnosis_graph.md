# Milestone 4: Sentinel Diagnosis Graph

## Objective

Create a concrete, inspectable graph object that represents how a RAG answer was produced,
which evidence it used, which document versions were retrieved, what telemetry was observed,
and what failure diagnosis was assigned.

## Novelty boundary

This milestone does not claim that graph-based RAG is novel. The graph is used for
failure diagnosis and experiment logging, not as a generic knowledge-graph retrieval method.

## Graph objects

Node types:

- Query
- RetrievalRun
- EvidenceSet
- Document
- DocumentVersion
- Chunk
- Answer
- FailureDiagnosis
- EvaluationRun
- TelemetryMetrics

Edge types:

- QUERY_TRIGGERED_RETRIEVAL
- RETRIEVAL_PRODUCED_EVIDENCE
- DOCUMENT_HAS_VERSION
- VERSION_HAS_CHUNK
- RETRIEVED_CHUNK
- CHUNK_IN_EVIDENCE_SET
- CHUNK_CITED_BY_ANSWER
- STALE_EVIDENCE_SIGNAL
- ANSWER_DIAGNOSED_AS
- EVALUATION_INFORMS_DIAGNOSIS
- METRICS_INFORM_DIAGNOSIS

## Baseline risk score

The graph risk score is a transparent weighted baseline over stale evidence, conflicting
versions, explicit diagnosis, low retrieval scores, unsupported claim rate, and context miss.
It is not the final algorithm; it exists to support ablation experiments.

## Commands

```powershell
python -m pytest
python scripts/reset_local_state.py
python scripts/ingest_docs.py --raw-dir data/raw
python scripts/ingest_drift_fixture.py
python scripts/run_diagnosis_graph.py --eval-set data/eval/evidence_drift_eval_set.jsonl --top-k 5
```

Expected output directory:

```text
experiments/diagnosis_graphs/
```
