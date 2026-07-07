from __future__ import annotations

import json
from pathlib import Path

from ragops.spark.document_version_job import (
    build_document_version_records,
    run_document_version_job,
)
from scripts.validate_spark_job import validate_spark_job


def test_document_version_records_include_hashes_and_versions(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    drift_v1 = tmp_path / "drift" / "v1"
    drift_v2 = tmp_path / "drift" / "v2"

    raw_dir.mkdir(parents=True)
    drift_v1.mkdir(parents=True)
    drift_v2.mkdir(parents=True)

    (raw_dir / "policy.md").write_text("Current policy text.", encoding="utf-8")
    (drift_v1 / "policy.md").write_text("Old policy text.", encoding="utf-8")
    (drift_v2 / "policy.md").write_text("New policy text.", encoding="utf-8")

    records = build_document_version_records([raw_dir, tmp_path / "drift"])

    assert len(records) == 3
    assert all(record.content_hash for record in records)
    assert {"policy:current", "policy:v1", "policy:v2"} == {
        record.version_id for record in records
    }
    assert sum(record.is_drift_fixture for record in records) == 2


def test_document_version_job_local_engine_writes_jsonl_and_manifest(tmp_path: Path):
    input_dir = tmp_path / "raw"
    output_dir = tmp_path / "processed"

    input_dir.mkdir()
    (input_dir / "ragops.md").write_text("RAGOps Sentinel document.", encoding="utf-8")

    manifest = run_document_version_job(
        input_dirs=[input_dir],
        output_dir=output_dir,
        engine="local",
    )

    assert manifest["passed"] is True
    assert manifest["spark_used"] is False
    assert manifest["record_count"] == 1

    jsonl_path = Path(manifest["jsonl_path"])
    assert jsonl_path.exists()

    first_line = jsonl_path.read_text(encoding="utf-8").splitlines()[0]
    payload = json.loads(first_line)
    assert payload["document_id"] == "ragops"
    assert payload["version_id"] == "ragops:current"


def test_validate_spark_job_passes_on_repository_data():
    result = validate_spark_job()

    assert result["passed"] is True
    assert result["errors"] == []
    assert result["record_count"] > 0


def test_spark_runner_script_exists():
    assert Path("scripts/run_spark_document_job.py").exists()
