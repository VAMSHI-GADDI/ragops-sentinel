# Reproducibility Checklist

## Artifact Availability
- [x] m2_baseline_eval
- [x] m3_evidence_drift_benchmark
- [x] m5_repair_benchmark
- [x] m6_observability_snapshot
- [x] m7_kubernetes_validation

## Required Commands
```powershell
python -m pytest
python scripts/reset_local_state.py
python scripts/ingest_docs.py --raw-dir data/raw
python scripts/ingest_drift_fixture.py
python scripts/run_repair_benchmark.py --eval-set data/eval/evidence_drift_eval_set.jsonl --top-k 5
python scripts/run_observability_smoke.py --repair-result experiments/results/m5_repair_benchmark.json
python scripts/validate_kubernetes_manifests.py --manifest-dir infra/kubernetes/base
python scripts/generate_research_artifacts.py
```

## Known Limitations to Reproduce
- Current benchmark is synthetic and intentionally small.
- Deterministic hashing embeddings prioritize reproducibility over semantic retrieval quality.
- Results should not be generalized beyond the included benchmark without larger experiments.
