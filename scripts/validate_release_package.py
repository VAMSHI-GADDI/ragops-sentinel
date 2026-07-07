from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


REQUIRED_DOCS = {
    "docs/recruiter_project_summary.md": [
        "One-Line Summary",
        "Best Resume Bullet",
        "Honest Scope",
    ],
    "docs/architecture.md": [
        "High-Level Architecture",
        "mermaid",
        "Major Subsystems",
        "Honest Limitation",
    ],
    "docs/skills_matrix.md": [
        "Skills Matrix",
        "Avoid overclaiming",
        "LoRA/PEFT fine-tuning-ready workflows",
    ],
    "docs/interview_talking_points.md": [
        "30-Second Pitch",
        "If Asked: Is This Production-Deployed?",
        "If Asked: Did You Train the LoRA Model?",
    ],
    "docs/repository_map.md": [
        "Repository Map",
        "Best Files for Recruiters to Read First",
        "scripts/local_ci.py",
    ],
    "release/release_checklist.md": [
        "Release Checklist",
        "Honest Claims Allowed",
        "Do not say unless separately executed",
    ],
}


REQUIRED_MILESTONE_NOTES = [
    "research/milestone_9_ci_cd.md",
    "research/milestone_10_langgraph_workflow.md",
    "research/milestone_11_airflow_orchestration.md",
    "research/milestone_12_spark_document_processing.md",
    "research/milestone_13_ai_security_guardrails.md",
    "research/milestone_14_managed_cloud_ai_services.md",
    "research/milestone_15_lora_peft_fine_tuning.md",
    "research/milestone_16_helm_terraform_inference_optimization.md",
]


README_REQUIRED_PHRASES = [
    "RAGOps Sentinel",
    "M16",
    "Helm, Terraform, and inference optimization",
]


def validate_release_package() -> dict[str, object]:
    errors: list[str] = []

    for relative_path, required_phrases in REQUIRED_DOCS.items():
        path = Path(relative_path)

        if not path.exists():
            errors.append(f"Missing required release document: {relative_path}")
            continue

        text = path.read_text(encoding="utf-8")

        for phrase in required_phrases:
            if phrase not in text:
                errors.append(f"{relative_path} missing required phrase: {phrase}")

    for relative_path in REQUIRED_MILESTONE_NOTES:
        path = Path(relative_path)

        if not path.exists():
            errors.append(f"Missing milestone note: {relative_path}")

    readme_path = Path("README.md")
    if not readme_path.exists():
        errors.append("README.md is missing.")
    else:
        readme = readme_path.read_text(encoding="utf-8")
        for phrase in README_REQUIRED_PHRASES:
            if phrase not in readme:
                errors.append(f"README.md missing required phrase: {phrase}")

    return {
        "milestone": "M17_FINAL_PORTFOLIO_RELEASE_PACKAGE",
        "required_docs": sorted(REQUIRED_DOCS.keys()),
        "required_milestone_notes": REQUIRED_MILESTONE_NOTES,
        "passed": not errors,
        "errors": errors,
    }


def main() -> None:
    result = validate_release_package()
    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
