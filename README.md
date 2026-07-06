# RAGOps Sentinel

**Evidence-Drift-Aware Failure Diagnosis and Cost-Aware Repair for Production Agentic RAG Systems**

This repository is Milestone 1 of the research project. It provides a runnable baseline RAG skeleton with:

- FastAPI API service
- Versioned document ingestion
- Header-aware chunking
- Qdrant vector index
- SQLite/PostgreSQL metadata through SQLAlchemy
- Baseline retrieval and extractive answer generation
- Basic failure diagnosis hooks
- Optional MLflow logging
- Docker Compose infrastructure for Qdrant, Postgres, MLflow, Prometheus, and Grafana

> This is intentionally a baseline. It is not yet the full Sentinel contribution. The next milestones add evidence drift benchmark, diagnosis graph, failure attribution, cost-aware repair, monitoring, and Kubernetes.

---

## Quickstart: local Python mode

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/ingest_docs.py --raw-dir data/raw
uvicorn apps.api.main:app --reload --port 8000
```

Then test:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is MLflow Tracking used for?","top_k":3}'
```

Open API docs:

```text
http://localhost:8000/docs
```

---

## Quickstart: Docker Compose infrastructure

```bash
docker compose up -d qdrant postgres mlflow prometheus grafana
python scripts/ingest_docs.py --raw-dir data/raw
uvicorn apps.api.main:app --reload --port 8000
```

Default service URLs:

- Qdrant: http://localhost:6333
- MLflow: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

---

## Research milestone status

| Milestone | Status |
|---|---|
| M1 Baseline RAG skeleton | Complete scaffold |
| M2 Evaluation layer | Next |
| M3 Evidence drift dataset | Pending |
| M4 Sentinel Diagnosis Graph | Pending |
| M5 Repair policy | Pending |
| M6 Monitoring dashboards | Pending |
| M7 Kubernetes deployment | Pending |
| M8 Paper + patent screening | Pending |

---

## Repository layout

```text
apps/api/              FastAPI app and routes
ragops/                Core Python package
scripts/               CLI utilities
data/raw/              Seed documents
infra/                 Docker, Prometheus, Grafana, Kubernetes placeholders
tests/                 Unit tests
research/              Proposal, experiment log, patent notes
```

---

## Important research boundary

This baseline does **not** claim novelty. The novelty candidate is a later mechanism: evidence-drift-aware failure diagnosis and cost-aware repair using a Sentinel Diagnosis Graph.


## Milestone 2: Evaluation Layer

Run the baseline evaluation after Docker services are running and documents have been ingested:

```powershell
python scripts/run_evaluation.py --eval-set data/eval/baseline_eval_set.jsonl --top-k 3
```

The output is written to:

```text
experiments/results/m2_baseline_eval.json
```

The deterministic baseline metrics include context precision, context recall, answer relevance, faithfulness, unsupported claim rate, and stale evidence rate. These are transparent scaffolding metrics, not final research-grade evaluation. Later milestones should add stronger RAGAS/ARES-style evaluation and a small human-labeled validation subset.

### Windows note

The ingestion and evaluation scripts now add the project root to `sys.path`, so you should not need to set `PYTHONPATH` manually.

## Milestone 3: Evidence Drift Benchmark

Milestone 3 adds a controlled evidence-drift fixture and benchmark.

### What it adds

- `data/drift/v1/ragops_retention_policy.md`: old retention policy, 7 days.
- `data/drift/v2/ragops_retention_policy.md`: current retention policy, 90 days.
- `scripts/reset_local_state.py`: clears local SQLite DB and Qdrant collection.
- `scripts/ingest_drift_fixture.py`: ingests old and current versions of the same document.
- `scripts/run_drift_benchmark.py`: compares stale-prone retrieval against latest-only temporal retrieval.
- `ragops/sentinel/drift.py`: computes evidence-drift features such as stale chunks and conflicting document versions.

### Run Milestone 3 from a clean local state

```powershell
python scripts/reset_local_state.py
python scripts/ingest_docs.py --raw-dir data/raw
python scripts/ingest_drift_fixture.py
python scripts/run_drift_benchmark.py --eval-set data/eval/evidence_drift_eval_set.jsonl --top-k 5
```

The benchmark writes:

```text
experiments/results/m3_evidence_drift_benchmark.json
```

### Interpretation

This milestone does not claim final novelty. It creates the first reproducible failure-injection benchmark for stale and wrong-version evidence. The key comparison is:

- baseline retrieval without temporal filtering,
- temporal retrieval with `latest_only=True`.

If the baseline retrieves stale chunks and the temporal filter removes them, then the evidence-drift layer is functioning as intended.

## Milestone 4: Sentinel Diagnosis Graph

M4 adds the first concrete diagnosis artifact for the research claim. It builds a graph that
connects the user query, retrieval run, retrieved chunks, document versions, answer, failure
diagnosis, evaluation metrics, and telemetry.

Run:

```powershell
python scripts/run_diagnosis_graph.py --eval-set data/eval/evidence_drift_eval_set.jsonl --top-k 5
```

Output:

```text
experiments/diagnosis_graphs/manifest.json
experiments/diagnosis_graphs/*.json
experiments/diagnosis_graphs/*.dot
```

API endpoint:

```text
POST /diagnosis-graph
```

This milestone still does not claim patentability. It creates the mechanism that later
experiments can test for root-cause attribution and repair routing.


## Milestone 5: Targeted Repair Policy

Milestone 5 adds the first measurable repair loop:

- diagnoses stale evidence failures,
- chooses `TEMPORAL_FILTER_RETRIEVAL`,
- reruns retrieval using latest-only evidence,
- regenerates the answer,
- compares before/after metrics,
- writes `experiments/results/m5_repair_benchmark.json`.

Run:

```powershell
python scripts/reset_local_state.py
python scripts/ingest_docs.py --raw-dir data/raw
python scripts/ingest_drift_fixture.py
python scripts/run_repair_benchmark.py --eval-set data/eval/evidence_drift_eval_set.jsonl --top-k 5
```

This is still a transparent baseline, not a final learned repair policy.

## Milestone 6: Observability Layer

Milestone 6 adds production-style observability around the RAG pipeline:

- Prometheus metrics for retrieval, stale evidence, quality signals, failure counts, repair attempts, and repair latency.
- Grafana provisioning for a RAGOps Sentinel dashboard.
- Offline observability snapshot generation from benchmark outputs.
- SLO-style checks for stale evidence, repair success, recall preservation, unsupported-claim rate, and repair latency.

Run after Milestone 5 repair benchmark:

```bash
python scripts/run_observability_smoke.py --repair-result experiments/results/m5_repair_benchmark.json
```

Output:

```text
experiments/results/m6_observability_snapshot.json
```

## Milestone 7 — Kubernetes Deployment Validation

M7 adds Kubernetes manifests under `infra/kubernetes/base` and a static validation script.

Run:

```powershell
python -m pytest
python scripts/validate_kubernetes_manifests.py --manifest-dir infra/kubernetes/base
```

Expected result:

```text
13 passed
Wrote experiments/results/m7_kubernetes_validation.json
```

Optional local cluster deployment:

```powershell
docker build -t ragops-sentinel-api:local .
kubectl apply -k infra/kubernetes/base
kubectl -n ragops-sentinel get pods
kubectl -n ragops-sentinel port-forward svc/rag-api 8000:8000
```

This milestone validates deployment structure. It does not yet claim production hardening.

## Milestone 8 — Publication / Patent-Screening Package

Generate the research artifact package after running the benchmark scripts:

```bash
python scripts/generate_research_artifacts.py
```

Outputs are written to `research/artifacts/`:

- `technical_report.md`
- `ieee_paper_draft.md`
- `patent_screening_memo.md`
- `reproducibility_checklist.md`
- `artifact_summary.json`

Important: the patent memo is a screening aid only. It does not claim patentability.
