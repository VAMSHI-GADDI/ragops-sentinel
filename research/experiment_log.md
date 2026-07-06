# Experiment Log

## Milestone 1 — Baseline RAG Skeleton

Status: implemented and locally validated by user on Windows.

Validated signals:
- Unit tests pass.
- FastAPI `/health` returns status ok.
- FastAPI `/metrics` returns Prometheus metrics.
- `/query` returns answer, citations, diagnosis, and metrics.

Known issues fixed in Milestone 2:
- `scripts/ingest_docs.py` now works without manually setting `PYTHONPATH`.
- `ragops/retrieval/vector_qdrant.py` now imports `RetrievedEvidence` explicitly.

## Milestone 2 — Evaluation Layer

Implemented deterministic evaluation baseline:
- context precision
- context recall
- answer relevance
- approximate faithfulness
- unsupported claim rate
- stale evidence rate

Important limitation: the Milestone-2 metrics are transparent deterministic baselines, not final research-grade LLM-as-judge metrics. Later milestones should compare them against RAGAS/ARES-style evaluation and a small human-labeled subset.

## Milestone 3 — Evidence Drift Benchmark

Objective: create a reproducible stale-evidence fixture using two versions of the same technical policy document.

Fixture:
- v1: RAGOps trace retention is 7 days.
- v2: RAGOps trace retention is 90 days and older versions are stale.

Scripts:
- `scripts/reset_local_state.py`
- `scripts/ingest_drift_fixture.py`
- `scripts/run_drift_benchmark.py`

Primary metrics:
- stale evidence rate,
- stale chunk count,
- diagnosis accuracy on labeled failures,
- context precision/recall under stale-prone retrieval versus latest-only temporal retrieval.

Status: scaffold implemented. Local Qdrant validation must be run by the user because the container environment does not run Docker services.

## Milestone 4 — Sentinel Diagnosis Graph

Added a dependency-free graph artifact that links query, retrieval run, evidence chunks,
document versions, answer, diagnosis, evaluator scores, and telemetry into a single
JSON/DOT representation. This does not claim final novelty yet; it is the first
concrete mechanism for component-level failure attribution experiments.

Validation target: `python -m pytest` should report 7 passing tests.

Key artifacts:

- `ragops/sentinel/diagnosis_graph.py`
- `scripts/run_diagnosis_graph.py`
- `tests/test_diagnosis_graph.py`
- API endpoint: `POST /diagnosis-graph`

## Milestone 6 — Observability

Added Prometheus/Grafana observability and an offline SLO snapshot generated from the repair benchmark. This prepares the system for later ablation studies and production-style monitoring experiments.
