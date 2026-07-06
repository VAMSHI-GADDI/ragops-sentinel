# Milestone 5: Cost-Aware Targeted Repair Policy

## Objective

Implement the first measurable repair loop for RAGOps Sentinel. The purpose is to test whether a
component-level diagnosis can trigger a local repair action and improve failure metrics without
blindly rerunning the whole pipeline.

## Implemented repair action

Milestone 5 implements one concrete repair path:

```text
F2_STALE_DOCUMENT -> TEMPORAL_FILTER_RETRIEVAL -> latest-only retrieval -> regenerate answer
```

This is intentionally narrow. It directly targets the evidence-drift failure mode introduced in
Milestone 3 and represented in the Sentinel Diagnosis Graph introduced in Milestone 4.

## What is not claimed

This milestone does not claim a learned repair policy, a patentable repair algorithm, or a complete
Agentic RAG repair system. It is a transparent baseline for measuring repair impact.

## Success condition

A repair is marked successful when:

- stale evidence rate decreases,
- context recall is preserved,
- answer relevance is preserved,
- unsupported claim rate does not get worse.

## Commands

```powershell
python -m pytest
python scripts/reset_local_state.py
python scripts/ingest_docs.py --raw-dir data/raw
python scripts/ingest_drift_fixture.py
python scripts/run_repair_benchmark.py --eval-set data/eval/evidence_drift_eval_set.jsonl --top-k 5
```

Expected output file:

```text
experiments/results/m5_repair_benchmark.json
```

## Research relevance

This milestone begins testing the central hypothesis that production RAG failures should be handled
with targeted, diagnosis-conditioned repair rather than unconditional full reruns.
