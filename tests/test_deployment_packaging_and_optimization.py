from __future__ import annotations

import asyncio
from pathlib import Path

from ragops.optimization.cache import InMemoryTTLCache, make_cache_key
from ragops.optimization.inference_optimizer import (
    InferenceOptimizer,
    optimized_result_to_dict,
)
from scripts.run_inference_benchmark import run_inference_benchmark
from scripts.validate_deployment_packaging import validate_deployment_packaging


def test_cache_key_is_deterministic_for_same_payload():
    left = make_cache_key("query", {"b": 2, "a": 1})
    right = make_cache_key("query", {"a": 1, "b": 2})

    assert left == right
    assert left.startswith("query:")


def test_in_memory_ttl_cache_set_get_and_clear():
    cache = InMemoryTTLCache()
    cache.set("k1", {"answer": "cached"}, ttl_seconds=60)

    assert cache.get("k1") == {"answer": "cached"}
    assert cache.stats()["entries"] == 1

    cache.clear()

    assert cache.get("k1") is None
    assert cache.stats()["entries"] == 0


def test_inference_optimizer_uses_cache_after_first_request():
    optimizer = InferenceOptimizer(ttl_seconds=60)
    calls = {"count": 0}

    def fake_inference():
        calls["count"] += 1
        return {"answer": "ok"}

    first = optimizer.run_cached(
        namespace="unit_test",
        payload={"query": "What is RAGOps?"},
        fn=fake_inference,
    )

    second = optimizer.run_cached(
        namespace="unit_test",
        payload={"query": "What is RAGOps?"},
        fn=fake_inference,
    )

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert first.result == second.result
    assert calls["count"] == 1


def test_async_inference_optimizer_uses_same_cache_path():
    optimizer = InferenceOptimizer(ttl_seconds=60)

    async def run_two_calls():
        first = await optimizer.run_async_cached(
            namespace="async_unit_test",
            payload={"query": "async cache"},
            fn=lambda: {"answer": "async ok"},
        )
        second = await optimizer.run_async_cached(
            namespace="async_unit_test",
            payload={"query": "async cache"},
            fn=lambda: {"answer": "async ok"},
        )
        return first, second

    first, second = asyncio.run(run_two_calls())

    assert first.cache_hit is False
    assert second.cache_hit is True


def test_optimized_result_serializes_to_dict():
    optimizer = InferenceOptimizer(ttl_seconds=60)
    result = optimizer.run_cached(
        namespace="serialize_test",
        payload={"query": "serialize"},
        fn=lambda: {"answer": "serialized"},
    )

    payload = optimized_result_to_dict(result)

    assert payload["cache_hit"] is False
    assert payload["result"] == {"answer": "serialized"}
    assert "latency_ms" in payload
    assert payload["cache_key"].startswith("serialize_test:")


def test_inference_benchmark_passes_with_expected_cache_hits():
    result = run_inference_benchmark(query="Benchmark cache behavior.", iterations=5)

    assert result["passed"] is True
    assert result["cache_hits_after_first_request"] == 4
    assert result["cache_entries"] == 1


def test_deployment_packaging_validator_passes():
    result = validate_deployment_packaging()

    assert result["passed"] is True
    assert result["errors"] == []
    assert result["milestone"] == "M16_HELM_TERRAFORM_INFERENCE_OPTIMIZATION"


def test_helm_chart_contains_api_and_qdrant_templates():
    chart_dir = Path("infra/helm/ragops-sentinel")

    assert (chart_dir / "Chart.yaml").exists()
    assert (chart_dir / "values.yaml").exists()
    assert (chart_dir / "templates/deployment-api.yaml").exists()
    assert (chart_dir / "templates/statefulset-qdrant.yaml").exists()

    chart_text = (chart_dir / "Chart.yaml").read_text(encoding="utf-8")
    deployment_text = (chart_dir / "templates/deployment-api.yaml").read_text(encoding="utf-8")
    qdrant_text = (chart_dir / "templates/statefulset-qdrant.yaml").read_text(encoding="utf-8")

    assert "apiVersion: v2" in chart_text
    assert "kind: Deployment" in deployment_text
    assert "readinessProbe" in deployment_text
    assert "kind: StatefulSet" in qdrant_text
    assert "volumeClaimTemplates" in qdrant_text


def test_terraform_templates_include_core_aws_resources():
    terraform_dir = Path("infra/terraform/aws")

    main_tf = (terraform_dir / "main.tf").read_text(encoding="utf-8")
    outputs_tf = (terraform_dir / "outputs.tf").read_text(encoding="utf-8")

    assert "aws_s3_bucket" in main_tf
    assert "aws_s3_bucket_versioning" in main_tf
    assert "aws_ecr_repository" in main_tf
    assert "aws_cloudwatch_log_group" in main_tf
    assert "artifact_bucket_name" in outputs_tf
    assert "ecr_repository_url" in outputs_tf
