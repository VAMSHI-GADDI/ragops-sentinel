from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
from typing import Iterable


TEXT_EXTENSIONS = {".md", ".txt", ".json", ".jsonl"}
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache"}


@dataclass(frozen=True)
class DocumentVersionRecord:
    file_path: str
    document_id: str
    version_id: str
    source_group: str
    content_hash: str
    byte_count: int
    line_count: int
    word_count: int
    estimated_chunks: int
    is_drift_fixture: bool
    modified_utc: str


def _safe_read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _contains_excluded_part(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def discover_documents(input_dirs: Iterable[str | Path]) -> list[Path]:
    documents: list[Path] = []

    for input_dir in input_dirs:
        root = Path(input_dir)
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if _contains_excluded_part(path):
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            documents.append(path)

    return sorted(documents, key=lambda item: str(item).lower())


def _infer_source_group(path: Path) -> str:
    parts = [part.lower() for part in path.parts]

    if "drift" in parts:
        return "drift_fixture"
    if "raw" in parts:
        return "raw_docs"
    if "eval" in parts:
        return "evaluation_data"

    return path.parent.name or "unknown"


def _infer_version_id(path: Path) -> tuple[str, str, bool]:
    parts = list(path.parts)
    lower_parts = [part.lower() for part in parts]

    is_drift_fixture = "drift" in lower_parts
    version = "current"

    for part in reversed(parts):
        if part.lower().startswith("v") and part[1:].isdigit():
            version = part.lower()
            break

    document_id = path.stem.lower().replace(" ", "_")
    version_id = f"{document_id}:{version}"

    return document_id, version_id, is_drift_fixture


def build_document_version_records(
    input_dirs: Iterable[str | Path],
    *,
    chunk_size_words: int = 220,
) -> list[DocumentVersionRecord]:
    records: list[DocumentVersionRecord] = []

    for path in discover_documents(input_dirs):
        text = _safe_read_text(path)
        words = text.split()
        word_count = len(words)
        estimated_chunks = max(1, math.ceil(word_count / chunk_size_words))
        document_id, version_id, is_drift_fixture = _infer_version_id(path)

        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

        records.append(
            DocumentVersionRecord(
                file_path=str(path.as_posix()),
                document_id=document_id,
                version_id=version_id,
                source_group=_infer_source_group(path),
                content_hash=_sha256_text(text),
                byte_count=path.stat().st_size,
                line_count=len(text.splitlines()),
                word_count=word_count,
                estimated_chunks=estimated_chunks,
                is_drift_fixture=is_drift_fixture,
                modified_utc=modified.isoformat(),
            )
        )

    return records


def write_jsonl(records: list[DocumentVersionRecord], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")

    return output


def write_spark_outputs(records: list[DocumentVersionRecord], output_dir: str | Path) -> dict[str, str]:
    from pyspark.sql import SparkSession

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    spark = (
        SparkSession.builder.appName("ragops-document-version-preprocessing")
        .master("local[*]")
        .getOrCreate()
    )

    try:
        spark_df = spark.createDataFrame([asdict(record) for record in records])
        parquet_path = output / "document_versions.parquet"
        json_path = output / "document_versions_spark_json"

        spark_df.write.mode("overwrite").parquet(str(parquet_path))
        spark_df.write.mode("overwrite").json(str(json_path))

        return {
            "parquet_path": str(parquet_path),
            "spark_json_path": str(json_path),
        }
    finally:
        spark.stop()


def run_document_version_job(
    *,
    input_dirs: Iterable[str | Path],
    output_dir: str | Path = "data/processed",
    engine: str = "local",
) -> dict[str, object]:
    records = build_document_version_records(input_dirs)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    jsonl_path = write_jsonl(records, output / "document_versions.jsonl")

    spark_outputs: dict[str, str] = {}
    spark_used = False
    spark_error: str | None = None

    if engine not in {"local", "spark", "auto"}:
        raise ValueError("engine must be one of: local, spark, auto")

    if engine in {"spark", "auto"}:
        try:
            spark_outputs = write_spark_outputs(records, output)
            spark_used = True
        except Exception as exc:
            spark_error = str(exc)
            if engine == "spark":
                raise

    manifest = {
        "milestone": "M12_PYSPARK_DOCUMENT_PROCESSING",
        "engine_requested": engine,
        "spark_used": spark_used,
        "spark_error": spark_error,
        "input_dirs": [str(Path(item)) for item in input_dirs],
        "output_dir": str(output),
        "jsonl_path": str(jsonl_path),
        "spark_outputs": spark_outputs,
        "record_count": len(records),
        "unique_document_ids": len({record.document_id for record in records}),
        "unique_version_ids": len({record.version_id for record in records}),
        "drift_fixture_records": sum(1 for record in records if record.is_drift_fixture),
        "passed": len(records) > 0,
    }

    manifest_path = output / "document_version_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return manifest
