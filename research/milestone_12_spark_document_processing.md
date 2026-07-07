# Milestone 12 - PySpark / Databricks-Style Document Processing

## Objective

Add an optional Spark-compatible batch preprocessing layer for RAGOps Sentinel document and evidence-version metadata.

## Added Capabilities

- Document discovery across raw and drift fixture directories
- Content hashing for versioned evidence
- Document ID and version ID extraction
- Source-group tagging
- Word, line, byte, and estimated chunk statistics
- Local JSONL output for lightweight reproducibility
- Optional PySpark Parquet and Spark JSON output
- Static validation in CI without requiring Spark installation
- Databricks-style job notes

## Skills Demonstrated

- PySpark-compatible batch processing
- Spark-style document preprocessing
- Databricks-style job packaging
- Versioned document metadata extraction
- Batch data engineering for RAG pipelines

## Validation

Run:

python scripts/validate_spark_job.py

Expected: passed true

Run tests:

python -m pytest

Expected result after M12: 26 passed

## Limitation

This milestone adds optional Spark-compatible preprocessing. The main CI validates implementation statically and through local-mode tests, but does not require a production Spark or Databricks cluster.
