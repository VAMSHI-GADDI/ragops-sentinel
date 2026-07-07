from __future__ import annotations

import json
from pathlib import Path


DAG_PATH = Path("infra/airflow/dags/ragops_nightly_eval_dag.py")

EXPECTED_TASKS = [
    "reset_state",
    "ingest_docs",
    "ingest_drift_fixture",
    "run_baseline_evaluation",
    "run_drift_benchmark",
    "run_repair_benchmark",
    "run_observability_smoke",
    "generate_research_artifacts",
]

EXPECTED_SCRIPTS = [
    "scripts/reset_local_state.py",
    "scripts/ingest_docs.py",
    "scripts/ingest_drift_fixture.py",
    "scripts/run_evaluation.py",
    "scripts/run_drift_benchmark.py",
    "scripts/run_repair_benchmark.py",
    "scripts/run_observability_smoke.py",
    "scripts/generate_research_artifacts.py",
]


def validate_airflow_dag() -> dict[str, object]:
    errors: list[str] = []

    if not DAG_PATH.exists():
        return {
            "milestone": "M11_AIRFLOW_ORCHESTRATION",
            "dag_path": str(DAG_PATH),
            "passed": False,
            "errors": ["Airflow DAG file is missing."],
        }

    content = DAG_PATH.read_text(encoding="utf-8")

    if 'dag_id="ragops_nightly_eval"' not in content:
        errors.append("DAG id ragops_nightly_eval is missing.")

    if 'schedule="@daily"' not in content:
        errors.append("Daily schedule is missing.")

    if "BashOperator" not in content:
        errors.append("BashOperator usage is missing.")

    for task_id in EXPECTED_TASKS:
        if f'task_id="{task_id}"' not in content:
            errors.append(f"Missing task_id: {task_id}")

    for script in EXPECTED_SCRIPTS:
        if script not in content:
            errors.append(f"Missing script command: {script}")

    if "reset_state" not in content or "generate_research_artifacts" not in content:
        errors.append("Expected first/last tasks are missing.")

    if ">>" not in content:
        errors.append("Task dependency chain is missing.")

    return {
        "milestone": "M11_AIRFLOW_ORCHESTRATION",
        "dag_path": str(DAG_PATH),
        "expected_tasks": EXPECTED_TASKS,
        "expected_scripts": EXPECTED_SCRIPTS,
        "passed": not errors,
        "errors": errors,
    }


def main() -> None:
    result = validate_airflow_dag()
    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
