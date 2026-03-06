"""
Cache Manager.

Provides a thin abstraction over Redis with an in-memory fallback for
development. Used to cache weather, satellite NDVI, and disease
parameter files for 15 minutes to improve latency and resiliency.

Expected env vars:
- REDIS_URL: Redis connection URL (optional)
Testing tips:
- In tests, rely on the in-memory fallback by omitting REDIS_URL.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Optional, Tuple

try:
    import redis  # type: ignore[import]
except Exception:  # noqa: BLE001
    redis = None  # type: ignore[assignment]

TTL_SECONDS = 15 * 60


class CacheManager:
    def __init__(self) -> None:
        self._client = None
        self._memory_cache: dict[str, Tuple[float, Any]] = {}
        url = os.getenv("REDIS_URL")
        if url and redis is not None:
            try:
                self._client = redis.from_url(url)
            except Exception:
                self._client = None

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        if self._client:
            try:
                raw = self._client.get(key)
                if raw is None:
                    return None
                return json.loads(raw)
            except Exception:
                return None
        # In-memory fallback
        entry = self._memory_cache.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if now > expires_at:
            self._memory_cache.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl: int = TTL_SECONDS) -> None:
        expires_at = time.time() + ttl
        if self._client:
            try:
                self._client.setex(key, ttl, json.dumps(value))
                return
            except Exception:
                # Fall back to memory if Redis fails.
                pass
        self._memory_cache[key] = (expires_at, value)


cache_manager = CacheManager()

