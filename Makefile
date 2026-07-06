.PHONY: install test validate-k8s artifacts ci docker-build clean

install:
python -m pip install --upgrade pip
pip install -r requirements.txt

test:
python -m pytest

validate-k8s:
python scripts/validate_kubernetes_manifests.py --manifest-dir infra/kubernetes/base

artifacts:
python scripts/generate_research_artifacts.py

ci: test validate-k8s artifacts

docker-build:
docker build -t ragops-sentinel-api:local .

clean:
rm -rf .pytest_cache
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
