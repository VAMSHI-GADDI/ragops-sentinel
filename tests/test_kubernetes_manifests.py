from pathlib import Path

from scripts.validate_kubernetes_manifests import load_manifest_documents, validate_documents


def test_kubernetes_manifests_are_parseable_and_complete():
    docs = load_manifest_documents(Path("infra/kubernetes/base"))
    result = validate_documents(docs)
    assert result["passed"], result
    assert result["documents_loaded"] >= 10
    assert "Deployment" in result["kinds"]
    assert "StatefulSet" in result["kinds"]
    assert "Service" in result["kinds"]


def test_rag_api_has_health_probes():
    docs = load_manifest_documents(Path("infra/kubernetes/base"))
    api = next(doc for doc in docs if doc.get("kind") == "Deployment" and doc.get("metadata", {}).get("name") == "rag-api")
    container = api["spec"]["template"]["spec"]["containers"][0]
    assert container["readinessProbe"]["httpGet"]["path"] == "/health"
    assert container["livenessProbe"]["httpGet"]["path"] == "/health"
