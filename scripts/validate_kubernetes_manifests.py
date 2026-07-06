from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

REQUIRED_KINDS = {
    "Namespace",
    "ConfigMap",
    "Secret",
    "Service",
    "Deployment",
    "StatefulSet",
}

REQUIRED_NAMED_RESOURCES = {
    ("Namespace", "ragops-sentinel"),
    ("Deployment", "rag-api"),
    ("Service", "rag-api"),
    ("StatefulSet", "qdrant"),
    ("Service", "qdrant"),
    ("StatefulSet", "postgres"),
    ("Service", "postgres"),
    ("Deployment", "prometheus"),
    ("Service", "prometheus"),
    ("Deployment", "grafana"),
    ("Service", "grafana"),
}


def load_manifest_documents(manifest_dir: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for path in sorted(manifest_dir.glob("*.yaml")):
        for doc in yaml.safe_load_all(path.read_text(encoding="utf-8")):
            if not doc:
                continue
            if doc.get("kind") == "Kustomization":
                continue
            doc["__source_file"] = str(path.relative_to(manifest_dir))
            docs.append(doc)
    return docs


def validate_documents(docs: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    kinds: set[str] = set()
    named: set[tuple[str, str]] = set()

    for doc in docs:
        api_version = doc.get("apiVersion")
        kind = doc.get("kind")
        metadata = doc.get("metadata") or {}
        name = metadata.get("name")
        namespace = metadata.get("namespace", "")
        source = doc.get("__source_file", "unknown")

        if not api_version:
            errors.append(f"{source}: missing apiVersion")
        if not kind:
            errors.append(f"{source}: missing kind")
        if not name:
            errors.append(f"{source}: missing metadata.name")
        if kind:
            kinds.add(kind)
        if kind and name:
            named.add((kind, name))
            key = (kind, namespace, name)
            if key in seen:
                errors.append(f"duplicate resource {kind}/{namespace}/{name}")
            seen.add(key)

        if kind in {"Deployment", "StatefulSet"}:
            spec = doc.get("spec") or {}
            template = (spec.get("template") or {}).get("spec") or {}
            containers = template.get("containers") or []
            if not containers:
                errors.append(f"{source}: {kind}/{name} has no containers")
            for container in containers:
                if not container.get("image"):
                    errors.append(f"{source}: container in {kind}/{name} missing image")
                if not container.get("ports"):
                    warnings.append(f"{source}: container in {kind}/{name} has no ports")
            selector = spec.get("selector", {}).get("matchLabels")
            labels = ((spec.get("template") or {}).get("metadata") or {}).get("labels")
            if selector and labels:
                missing = {k: v for k, v in selector.items() if labels.get(k) != v}
                if missing:
                    errors.append(f"{source}: {kind}/{name} selector labels do not match pod template")

        if kind == "Service":
            spec = doc.get("spec") or {}
            if not spec.get("selector"):
                errors.append(f"{source}: Service/{name} missing selector")
            if not spec.get("ports"):
                errors.append(f"{source}: Service/{name} missing ports")

    missing_kinds = sorted(REQUIRED_KINDS - kinds)
    for kind in missing_kinds:
        errors.append(f"missing required kind: {kind}")

    missing_named = sorted(REQUIRED_NAMED_RESOURCES - named)
    for kind, name in missing_named:
        errors.append(f"missing required resource: {kind}/{name}")

    return {
        "milestone": "M7_KUBERNETES_DEPLOYMENT",
        "documents_loaded": len(docs),
        "kinds": sorted(kinds),
        "required_kinds_present": not missing_kinds,
        "required_resources_present": not missing_named,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate RAGOps Sentinel Kubernetes manifests.")
    parser.add_argument("--manifest-dir", default="infra/kubernetes/base")
    parser.add_argument("--output", default="experiments/results/m7_kubernetes_validation.json")
    args = parser.parse_args()

    manifest_dir = Path(args.manifest_dir)
    docs = load_manifest_documents(manifest_dir)
    result = validate_documents(docs)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Wrote {output}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
