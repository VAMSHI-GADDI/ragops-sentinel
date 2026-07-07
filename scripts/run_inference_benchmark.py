from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ragops.optimization.inference_optimizer import InferenceOptimizer


def simulated_inference(query: str) -> dict[str, str]:
    time.sleep(0.02)
    return {
        "query": query,
        "answer": f"Simulated optimized answer for: {query}",
    }


def run_inference_benchmark(*, query: str, iterations: int = 5) -> dict[str, Any]:
    optimizer = InferenceOptimizer(ttl_seconds=300)

    results = []
    for _ in range(iterations):
        result = optimizer.run_cached(
            namespace="benchmark_query",
            payload={"query": query},
            fn=lambda: simulated_inference(query),
        )
        results.append(result)

    cold = results[0]
    warm = results[1:]

    warm_latencies = [result.latency_ms for result in warm]

    return {
        "milestone": "M16_HELM_TERRAFORM_INFERENCE_OPTIMIZATION",
        "query": query,
        "iterations": iterations,
        "cold_cache_latency_ms": cold.latency_ms,
        "warm_cache_mean_latency_ms": statistics.mean(warm_latencies) if warm_latencies else 0.0,
        "warm_cache_min_latency_ms": min(warm_latencies) if warm_latencies else 0.0,
        "cache_hits_after_first_request": sum(1 for result in warm if result.cache_hit),
        "cache_entries": optimizer.cache.stats()["entries"],
        "optimization": "response_cache",
        "passed": cold.cache_hit is False and all(result.cache_hit for result in warm),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CI-safe inference optimization benchmark.")
    parser.add_argument("--query", default="What is evidence drift?")
    parser.add_argument("--iterations", type=int, default=5)
    args = parser.parse_args()

    result = run_inference_benchmark(query=args.query, iterations=args.iterations)
    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
