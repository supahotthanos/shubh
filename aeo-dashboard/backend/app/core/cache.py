"""Thin async Redis cache wrapper used by hot endpoints + Celery tasks."""
from __future__ import annotations

import json
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings

_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _client


async def cache_get(key: str) -> Optional[Any]:
    try:
        raw = await get_redis().get(key)
    except Exception:
        return None
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> None:
    ttl = ttl or settings.REDIS_CACHE_TTL_SECONDS
    try:
        await get_redis().set(key, json.dumps(value, default=str), ex=ttl)
    except Exception:
        # Cache failures must never break requests.
        pass


async def cache_invalidate(pattern: str) -> int:
    client = get_redis()
    try:
        count = 0
        async for key in client.scan_iter(match=pattern):
            await client.delete(key)
            count += 1
        return count
    except Exception:
        return 0
