# Milestone 7 Kubernetes Deployment

This folder contains Kubernetes manifests for a local or small-cluster deployment of RAGOps Sentinel.

## What is included

- `rag-api` FastAPI deployment and service
- Qdrant StatefulSet and service
- Postgres StatefulSet and service
- MLflow deployment and service
- Prometheus deployment and service
- Grafana deployment and service
- namespace, config, and basic secret manifests

## Local cluster workflow

Use Docker Desktop Kubernetes, Minikube, Kind, or another local cluster.

```powershell
cd C:\ragops_m7\ragops-sentinel
docker build -t ragops-sentinel-api:local .
python scripts/validate_kubernetes_manifests.py --manifest-dir infra/kubernetes/base
kubectl apply -k infra/kubernetes/base
kubectl -n ragops-sentinel get pods
kubectl -n ragops-sentinel port-forward svc/rag-api 8000:8000
```

Then open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Notes

This milestone validates Kubernetes readiness, but it does not claim production hardening. The manifests intentionally stay simple for one-researcher reproducibility. Future production work should add network policies, persistent storage classes, TLS, non-default secrets, autoscaling, and image scanning.
