# Milestone 7 — Kubernetes Deployment Layer

## Objective

Add reproducible Kubernetes manifests for RAGOps Sentinel so the project demonstrates containerized deployment, service discovery, and monitoring-oriented infrastructure.

## What this milestone proves

This milestone proves static Kubernetes readiness: manifests are parseable, core resources exist, API probes are present, and supporting services are represented.

## What this milestone does not prove yet

It does not prove production-grade reliability, autoscaling, TLS, cluster security, or cloud-native performance. Those require a running cluster experiment and hardening work.

## Components

- FastAPI `rag-api` Deployment and Service
- Qdrant StatefulSet and Service
- Postgres StatefulSet and Service
- MLflow Deployment and Service
- Prometheus Deployment and Service
- Grafana Deployment and Service
- namespace, ConfigMap, and Secret manifests

## Validation command

```powershell
python scripts/validate_kubernetes_manifests.py --manifest-dir infra/kubernetes/base
```

Expected result: `passed: true` and output file `experiments/results/m7_kubernetes_validation.json`.

## Research relevance

Kubernetes is included because the final system targets production RAGOps rather than notebook-only RAG. The deployment layer is necessary for later experiments involving telemetry, service-level objectives, and failure injection.
