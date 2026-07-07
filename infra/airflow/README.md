# RAGOps Sentinel Airflow Orchestration

## Purpose

This folder contains an optional Apache Airflow DAG for scheduled RAGOps Sentinel evaluation and artifact-generation workflows.

## DAG

ragops_nightly_eval runs this pipeline:

1. reset_state
2. ingest_docs
3. ingest_drift_fixture
4. run_baseline_evaluation
5. run_drift_benchmark
6. run_repair_benchmark
7. run_observability_smoke
8. generate_research_artifacts

## Why Airflow

Airflow is used as a workflow orchestration layer for repeatable RAG ingestion, evaluation, repair benchmarking, observability checks, and research artifact generation.

## Validation Without Installing Airflow

Run from project root:

python scripts/validate_airflow_dag.py

Expected result: passed true

## Optional Runtime Note

The main project virtual environment currently uses Python 3.13. For actually running Airflow, use Python 3.11 or an official Airflow Docker image.

## Limitation

This milestone adds an Airflow DAG and static validation. It does not claim a production Airflow deployment.
