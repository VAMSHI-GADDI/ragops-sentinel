# Databricks-Style Batch Job Notes

## Purpose

This folder documents how the M12 document-version preprocessing job can be adapted to a Databricks or Spark runtime.

## Job Entry Point

scripts/run_spark_document_job.py

## Example Spark Mode

python scripts/run_spark_document_job.py --engine spark --input-dir data/raw --input-dir data/drift --output-dir data/processed

## Outputs

- document_versions.jsonl
- document_version_manifest.json
- document_versions.parquet when Spark mode is available
- Spark JSON output directory when Spark mode is available

## Honest Limitation

This milestone adds a PySpark-compatible preprocessing job and Databricks-style packaging notes. It does not claim a production Databricks workspace deployment.
