# Milestone 11 - Airflow Orchestration

## Objective

Add an optional Apache Airflow orchestration layer for scheduled RAGOps Sentinel evaluation workflows.

## Added Capabilities

- Airflow DAG for nightly RAGOps evaluation
- Scheduled ingestion and drift-fixture loading
- Baseline evaluation orchestration
- Evidence-drift benchmark orchestration
- Repair benchmark orchestration
- Observability smoke-test orchestration
- Research artifact generation orchestration
- Static DAG validation without forcing Airflow into the main CI dependency set

## Skills Demonstrated

- Apache Airflow
- DAG orchestration
- Scheduled ML/RAG evaluation pipelines
- Batch workflow automation
- Reproducible evaluation workflow design

## Validation

Run:

python scripts/validate_airflow_dag.py

Expected: passed true

Run tests:

python -m pytest

Expected result after M11: 22 passed

## Limitation

This milestone adds Airflow workflow code and static DAG validation. It does not claim production Airflow deployment.
