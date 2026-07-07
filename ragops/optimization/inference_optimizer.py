from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
import time
from typing import Any, Callable

from ragops.optimization.cache import InMemoryTTLCache, make_cache_key


@dataclass(frozen=True)
class OptimizedInferenceResult:
    result: Any
    cache_hit: bool
    latency_ms: float
    cache_key: str


class InferenceOptimizer:
    def __init__(self, *, ttl_seconds: int = 300) -> None:
        self.cache = InMemoryTTLCache()
        self.ttl_seconds = ttl_seconds

    def run_cached(
        self,
        *,
        namespace: str,
        payload: dict[str, Any],
        fn: Callable[[], Any],
    ) -> OptimizedInferenceResult:
        cache_key = make_cache_key(namespace, payload)
        start = time.perf_counter()

        cached = self.cache.get(cache_key)
        if cached is not None:
            return OptimizedInferenceResult(
                result=cached,
                cache_hit=True,
                latency_ms=(time.perf_counter() - start) * 1000,
                cache_key=cache_key,
            )

        result = fn()
        self.cache.set(cache_key, result, ttl_seconds=self.ttl_seconds)

        return OptimizedInferenceResult(
            result=result,
            cache_hit=False,
            latency_ms=(time.perf_counter() - start) * 1000,
            cache_key=cache_key,
        )

    async def run_async_cached(
        self,
        *,
        namespace: str,
        payload: dict[str, Any],
        fn: Callable[[], Any],
    ) -> OptimizedInferenceResult:
        return await asyncio.to_thread(
            self.run_cached,
            namespace=namespace,
            payload=payload,
            fn=fn,
        )


def optimized_result_to_dict(result: OptimizedInferenceResult) -> dict[str, Any]:
    return asdict(result)
