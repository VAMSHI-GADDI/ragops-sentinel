from __future__ import annotations

from pathlib import Path

from scripts.validate_airflow_dag import validate_airflow_dag


def test_airflow_dag_file_exists():
    assert Path("infra/airflow/dags/ragops_nightly_eval_dag.py").exists()


def test_airflow_dag_static_validation_passes():
    result = validate_airflow_dag()

    assert result["passed"] is True
    assert result["errors"] == []
    assert "reset_state" in result["expected_tasks"]
    assert "generate_research_artifacts" in result["expected_tasks"]


def test_airflow_dag_documents_required_pipeline_scripts():
    dag_content = Path("infra/airflow/dags/ragops_nightly_eval_dag.py").read_text(
        encoding="utf-8"
    )

    required_scripts = [
        "scripts/reset_local_state.py",
        "scripts/ingest_docs.py",
        "scripts/ingest_drift_fixture.py",
        "scripts/run_evaluation.py",
        "scripts/run_drift_benchmark.py",
        "scripts/run_repair_benchmark.py",
        "scripts/run_observability_smoke.py",
        "scripts/generate_research_artifacts.py",
    ]

    for script in required_scripts:
        assert script in dag_content
