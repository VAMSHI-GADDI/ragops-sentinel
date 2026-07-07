from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(command: list[str], root: Path) -> None:
    print("\n$ " + " ".join(command))
    subprocess.run(command, cwd=root, check=True)


def main() -> None:
    root = Path(__file__).resolve().parents[1]

    commands = [
        [sys.executable, "-m", "pytest"],
        [
            sys.executable,
            "scripts/validate_kubernetes_manifests.py",
            "--manifest-dir",
            "infra/kubernetes/base",
        ],
        [sys.executable, "scripts/validate_airflow_dag.py"],
        [sys.executable, "scripts/validate_spark_job.py"],
        [sys.executable, "scripts/validate_security_guardrails.py"],
        [sys.executable, "scripts/validate_llm_providers.py"],
        [sys.executable, "scripts/validate_fine_tuning_dataset.py"],
        [sys.executable, "scripts/prepare_fine_tuning_artifacts.py"],
        [sys.executable, "scripts/generate_research_artifacts.py"],
    ]

    for command in commands:
        run(command, root)

    print("\nLocal CI checks passed.")


if __name__ == "__main__":
    main()
