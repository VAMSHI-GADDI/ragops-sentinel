from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ragops.spark.document_version_job import build_document_version_records


JOB_PATH = Path("ragops/spark/document_version_job.py")
RUNNER_PATH = Path("scripts/run_spark_document_job.py")


REQUIRED_SNIPPETS = [
    "SparkSession",
    "pyspark.sql",
    "parquet",
    "content_hash",
    "version_id",
    "run_document_version_job",
    "build_document_version_records",
]


def validate_spark_job() -> dict[str, object]:
    errors: list[str] = []

    if not JOB_PATH.exists():
        errors.append("Missing ragops/spark/document_version_job.py")

    if not RUNNER_PATH.exists():
        errors.append("Missing scripts/run_spark_document_job.py")

    content = JOB_PATH.read_text(encoding="utf-8") if JOB_PATH.exists() else ""

    for snippet in REQUIRED_SNIPPETS:
        if snippet not in content:
            errors.append(f"Missing required implementation snippet: {snippet}")

    records = build_document_version_records(["data/raw", "data/drift"])

    if not records:
        errors.append("No records discovered from data/raw and data/drift.")

    if records and not any(record.is_drift_fixture for record in records):
        errors.append("No drift fixture records were identified.")

    return {
        "milestone": "M12_PYSPARK_DOCUMENT_PROCESSING",
        "job_path": str(JOB_PATH),
        "runner_path": str(RUNNER_PATH),
        "record_count": len(records),
        "unique_document_ids": len({record.document_id for record in records}),
        "unique_version_ids": len({record.version_id for record in records}),
        "passed": not errors,
        "errors": errors,
    }


def main() -> None:
    result = validate_spark_job()
    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
