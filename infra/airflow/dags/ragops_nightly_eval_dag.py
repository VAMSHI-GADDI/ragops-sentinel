from __future__ import annotations

import pendulum

from airflow import DAG

try:
    from airflow.providers.standard.operators.bash import BashOperator
except ImportError:  # Airflow 2.x compatibility
    from airflow.operators.bash import BashOperator


PROJECT_ROOT = "/opt/airflow/ragops-sentinel"
PYTHON_EXECUTABLE = "python"
BASE_COMMAND = f"cd {PROJECT_ROOT} && export PYTHONPATH={PROJECT_ROOT}"

DEFAULT_ARGS = {
    "owner": "ragops-sentinel",
    "retries": 1,
}


with DAG(
    dag_id="ragops_nightly_eval",
    description=(
        "Scheduled RAGOps Sentinel ingestion, evidence-drift evaluation, "
        "repair benchmarking, observability smoke testing, and artifact generation."
    ),
    schedule="@daily",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["ragops", "rag", "evaluation", "airflow", "m11"],
) as dag:
    reset_state = BashOperator(
        task_id="reset_state",
        bash_command=f"{BASE_COMMAND} && {PYTHON_EXECUTABLE} scripts/reset_local_state.py",
    )

    ingest_docs = BashOperator(
        task_id="ingest_docs",
        bash_command=f"{BASE_COMMAND} && {PYTHON_EXECUTABLE} scripts/ingest_docs.py --docs-dir data/raw",
    )

    ingest_drift_fixture = BashOperator(
        task_id="ingest_drift_fixture",
        bash_command=f"{BASE_COMMAND} && {PYTHON_EXECUTABLE} scripts/ingest_drift_fixture.py",
    )

    run_baseline_evaluation = BashOperator(
        task_id="run_baseline_evaluation",
        bash_command=f"{BASE_COMMAND} && {PYTHON_EXECUTABLE} scripts/run_evaluation.py",
    )

    run_drift_benchmark = BashOperator(
        task_id="run_drift_benchmark",
        bash_command=f"{BASE_COMMAND} && {PYTHON_EXECUTABLE} scripts/run_drift_benchmark.py",
    )

    run_repair_benchmark = BashOperator(
        task_id="run_repair_benchmark",
        bash_command=f"{BASE_COMMAND} && {PYTHON_EXECUTABLE} scripts/run_repair_benchmark.py",
    )

    run_observability_smoke = BashOperator(
        task_id="run_observability_smoke",
        bash_command=f"{BASE_COMMAND} && {PYTHON_EXECUTABLE} scripts/run_observability_smoke.py",
    )

    generate_research_artifacts = BashOperator(
        task_id="generate_research_artifacts",
        bash_command=f"{BASE_COMMAND} && {PYTHON_EXECUTABLE} scripts/generate_research_artifacts.py",
    )

    (
        reset_state
        >> ingest_docs
        >> ingest_drift_fixture
        >> run_baseline_evaluation
        >> run_drift_benchmark
        >> run_repair_benchmark
        >> run_observability_smoke
        >> generate_research_artifacts
    )
