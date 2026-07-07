from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import time
from typing import Any


def make_cache_key(namespace: str, payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str)
    digest = sha256(serialized.encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"


@dataclass
class CacheEntry:
    value: Any
    created_at: float
    ttl_seconds: int


class InMemoryTTLCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)

        if entry is None:
            return None

        if time.time() - entry.created_at > entry.ttl_seconds:
            self._store.pop(key, None)
            return None

        return entry.value

    def set(self, key: str, value: Any, *, ttl_seconds: int = 300) -> None:
        self._store[key] = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl_seconds=ttl_seconds,
        )

    def clear(self) -> None:
        self._store.clear()

    def stats(self) -> dict[str, int]:
        return {"entries": len(self._store)}
