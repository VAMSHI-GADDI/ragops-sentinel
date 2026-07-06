# Milestone 6 — Observability Layer

## Objective
Expose measurable production signals for RAGOps Sentinel so failures, repairs, evidence drift, and quality degradation can be monitored instead of inspected manually.

## What this milestone adds

1. Prometheus metrics for:
   - query latency,
   - retrieval latency,
   - stale evidence rate,
   - stale chunk count,
   - retrieved chunk count,
   - failure count by code,
   - repair attempts by action/success,
   - repair latency,
   - evaluation quality metrics,
   - Sentinel Diagnosis Graph risk score.

2. Grafana provisioning files:
   - Prometheus datasource,
   - RAGOps Sentinel dashboard JSON.

3. Offline observability smoke test:
   - reads the Milestone-5 repair benchmark,
   - produces SLO checks,
   - writes `experiments/results/m6_observability_snapshot.json`.

## Research relevance
This milestone does not claim novelty by itself. It supports the research claim by converting evidence drift and repair behavior into measurable operational signals.

## Current limitations
- The SLO thresholds are baseline thresholds, not scientifically optimized.
- The dashboard validates observability plumbing, not real production reliability yet.
- The benchmark remains synthetic and small.
