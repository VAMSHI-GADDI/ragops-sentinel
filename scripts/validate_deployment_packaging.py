from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from scripts.run_inference_benchmark import run_inference_benchmark


HELM_CHART_DIR = Path("infra/helm/ragops-sentinel")
TERRAFORM_DIR = Path("infra/terraform/aws")


HELM_REQUIRED_FILES = [
    "Chart.yaml",
    "values.yaml",
    "templates/_helpers.tpl",
    "templates/configmap.yaml",
    "templates/deployment-api.yaml",
    "templates/service-api.yaml",
    "templates/statefulset-qdrant.yaml",
    "templates/service-qdrant.yaml",
]


TERRAFORM_REQUIRED_FILES = [
    "versions.tf",
    "variables.tf",
    "main.tf",
    "outputs.tf",
    "terraform.tfvars.example",
]


def validate_deployment_packaging() -> dict[str, object]:
    errors: list[str] = []

    for file_name in HELM_REQUIRED_FILES:
        path = HELM_CHART_DIR / file_name
        if not path.exists():
            errors.append(f"Missing Helm file: {path}")

    for file_name in TERRAFORM_REQUIRED_FILES:
        path = TERRAFORM_DIR / file_name
        if not path.exists():
            errors.append(f"Missing Terraform file: {path}")

    chart_text = (HELM_CHART_DIR / "Chart.yaml").read_text(encoding="utf-8") if (HELM_CHART_DIR / "Chart.yaml").exists() else ""
    values_text = (HELM_CHART_DIR / "values.yaml").read_text(encoding="utf-8") if (HELM_CHART_DIR / "values.yaml").exists() else ""
    deployment_text = (HELM_CHART_DIR / "templates/deployment-api.yaml").read_text(encoding="utf-8") if (HELM_CHART_DIR / "templates/deployment-api.yaml").exists() else ""
    qdrant_text = (HELM_CHART_DIR / "templates/statefulset-qdrant.yaml").read_text(encoding="utf-8") if (HELM_CHART_DIR / "templates/statefulset-qdrant.yaml").exists() else ""

    if "apiVersion: v2" not in chart_text:
        errors.append("Helm Chart.yaml must use apiVersion v2.")

    if "ragops-sentinel" not in chart_text:
        errors.append("Helm chart name should include ragops-sentinel.")

    for expected in ["replicaCount", "image:", "service:", "qdrant:", "prometheus:"]:
        if expected not in values_text:
            errors.append(f"values.yaml missing expected section: {expected}")

    for expected in ["kind: Deployment", "readinessProbe", "livenessProbe", "prometheus.io/scrape"]:
        if expected not in deployment_text:
            errors.append(f"API deployment template missing: {expected}")

    for expected in ["kind: StatefulSet", "qdrant-storage", "volumeClaimTemplates"]:
        if expected not in qdrant_text:
            errors.append(f"Qdrant StatefulSet template missing: {expected}")

    main_tf = (TERRAFORM_DIR / "main.tf").read_text(encoding="utf-8") if (TERRAFORM_DIR / "main.tf").exists() else ""
    variables_tf = (TERRAFORM_DIR / "variables.tf").read_text(encoding="utf-8") if (TERRAFORM_DIR / "variables.tf").exists() else ""
    outputs_tf = (TERRAFORM_DIR / "outputs.tf").read_text(encoding="utf-8") if (TERRAFORM_DIR / "outputs.tf").exists() else ""

    for expected in [
        "aws_s3_bucket",
        "aws_s3_bucket_versioning",
        "aws_s3_bucket_server_side_encryption_configuration",
        "aws_ecr_repository",
        "aws_cloudwatch_log_group",
    ]:
        if expected not in main_tf:
            errors.append(f"Terraform main.tf missing resource: {expected}")

    for expected in ["aws_region", "project_name", "environment", "container_image_tag_mutability"]:
        if expected not in variables_tf:
            errors.append(f"Terraform variables.tf missing variable: {expected}")

    for expected in ["artifact_bucket_name", "ecr_repository_url", "cloudwatch_log_group_name"]:
        if expected not in outputs_tf:
            errors.append(f"Terraform outputs.tf missing output: {expected}")

    benchmark = run_inference_benchmark(query="Validate inference optimization.", iterations=5)

    if not benchmark["passed"]:
        errors.append("Inference optimization benchmark did not pass.")

    if benchmark["cache_hits_after_first_request"] != 4:
        errors.append("Inference benchmark should have 4 warm cache hits after first request.")

    return {
        "milestone": "M16_HELM_TERRAFORM_INFERENCE_OPTIMIZATION",
        "helm_chart_dir": str(HELM_CHART_DIR),
        "terraform_dir": str(TERRAFORM_DIR),
        "helm_files": HELM_REQUIRED_FILES,
        "terraform_files": TERRAFORM_REQUIRED_FILES,
        "inference_benchmark": benchmark,
        "passed": not errors,
        "errors": errors,
    }


def main() -> None:
    result = validate_deployment_packaging()
    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
