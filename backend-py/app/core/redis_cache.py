from __future__ import annotations

import hashlib
import json
import asyncio
from typing import Any, Optional, Dict

from loguru import logger
from redis.asyncio import Redis, from_url

from app.core.config import settings

_clients: Dict[int, Redis] = {}


def build_cache_key(*parts: Any) -> str:
    prefix = settings.REDIS_CACHE_PREFIX.strip()
    cleaned_parts = [str(part).strip() for part in parts if part is not None and str(part).strip()]
    if prefix:
        return ":".join([prefix, *cleaned_parts])
    return ":".join(cleaned_parts)


def fingerprint_bytes(data: bytes) -> str:
    return hashlib.sha256(data or b"").hexdigest()


def fingerprint_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _get_loop_id() -> Optional[int]:
    try:
        loop = asyncio.get_running_loop()
        return id(loop)
    except RuntimeError:
        return None


def get_redis_client() -> Optional[Redis]:
    """Return a Redis client bound to the current event loop (or a fresh client when no loop).

    This avoids "Future attached to a different loop" errors by keeping one client per running loop.
    """
    if not settings.REDIS_CACHE_ENABLED:
        return None

    loop_id = _get_loop_id()

    # If no running loop (called from sync context), create a transient client (not cached)
    if loop_id is None:
        try:
            client = from_url(
                settings.REDIS_URL,
                decode_responses=True,
                health_check_interval=30,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            return client
        except Exception as exc:
            logger.warning(f"Redis客户端初始化失败 (sync): {exc}")
            return None

    # Return cached client for this loop if exists
    if loop_id in _clients:
        return _clients[loop_id]

    try:
        client = from_url(
            settings.REDIS_URL,
            decode_responses=True,
            health_check_interval=30,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        _clients[loop_id] = client
        return client
    except Exception as exc:
        logger.warning(f"Redis客户端初始化失败: {exc}")
        return None


async def get_cache_json(key: str) -> Any:
    client = get_redis_client()
    if client is None:
        return None

    try:
        raw_value = await client.get(key)
    except Exception as exc:
        logger.warning(f"读取Redis缓存失败 key={key}: {exc}")
        return None

    if not raw_value:
        logger.info(f"Redis MISS key={key}")
        return None

    try:
        logger.info(f"Redis HIT key={key}")
        return json.loads(raw_value)
    except json.JSONDecodeError:
        logger.warning(f"Redis缓存JSON解析失败 key={key}")
        return None


async def set_cache_json(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    client = get_redis_client()
    if client is None:
        return False

    try:
        payload = json.dumps(value, ensure_ascii=False, default=str)
        expire_seconds = ttl if ttl and ttl > 0 else settings.REDIS_CACHE_DEFAULT_TTL
        await client.set(key, payload, ex=expire_seconds)
        logger.info(f"Redis SET key={key} ttl={expire_seconds} bytes={len(payload) if payload is not None else 0}")
        return True
    except Exception as exc:
        logger.warning(f"写入Redis缓存失败 key={key}: {exc}")
        return False


async def delete_cache(key: str) -> bool:
    client = get_redis_client()
    if client is None:
        return False

    try:
        await client.delete(key)
        logger.info(f"Redis DEL key={key}")
        return True
    except Exception as exc:
        logger.warning(f"删除Redis缓存失败 key={key}: {exc}")
        return False


def delete_cache_sync(key: str) -> bool:
    """同步场景下删除缓存；若当前已有事件循环，则异步调度删除任务。"""
    client = get_redis_client()
    if client is None:
        return False

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            res = asyncio.run(delete_cache(key))
            return res
        except Exception as exc:
            logger.warning(f"同步删除Redis缓存失败 key={key}: {exc}")
            return False

    try:
        loop.create_task(delete_cache(key))
        logger.info(f"Redis DEL scheduled key={key}")
    except Exception as exc:
        logger.warning(f"调度异步删除Redis缓存失败 key={key}: {exc}")
        return False
    return True