from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import asyncpg
import httpx
from redis.asyncio import Redis

from app.config import Settings


StatusPayload = dict[str, Any]


def _ok(name: str, latency_ms: int | None = None, **details: Any) -> StatusPayload:
    payload: StatusPayload = {"name": name, "status": "ok"}
    if latency_ms is not None:
        payload["latency_ms"] = latency_ms
    if details:
        payload["details"] = details
    return payload


def _error(name: str, message: str, latency_ms: int | None = None, **details: Any) -> StatusPayload:
    payload: StatusPayload = {"name": name, "status": "error", "message": message}
    if latency_ms is not None:
        payload["latency_ms"] = latency_ms
    if details:
        payload["details"] = details
    return payload


def _latency_ms(start: float) -> int:
    return round((time.perf_counter() - start) * 1000)


async def check_database(settings: Settings) -> StatusPayload:
    start = time.perf_counter()
    connection: asyncpg.Connection | None = None

    try:
        connection = await asyncpg.connect(settings.database_url, timeout=3)
        value = await connection.fetchval("select 1")
        if value != 1:
            return _error("database", "Unexpected database response", _latency_ms(start))
        return _ok("database", _latency_ms(start))
    except Exception as exc:  # noqa: BLE001 - status endpoint should report dependency failures.
        return _error("database", str(exc), _latency_ms(start))
    finally:
        if connection is not None:
            await connection.close()


async def check_redis(settings: Settings) -> StatusPayload:
    start = time.perf_counter()
    client = Redis.from_url(settings.redis_url, socket_connect_timeout=3, socket_timeout=3)

    try:
        pong = await client.ping()
        if not pong:
            return _error("redis", "Redis ping returned false", _latency_ms(start))
        return _ok("redis", _latency_ms(start))
    except Exception as exc:  # noqa: BLE001
        return _error("redis", str(exc), _latency_ms(start))
    finally:
        await client.aclose()


async def check_suwayomi(settings: Settings) -> StatusPayload:
    start = time.perf_counter()
    url = settings.suwayomi_url.rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=5, follow_redirects=True) as client:
            response = await client.get(url)
        if response.status_code >= 500:
            return _error(
                "suwayomi",
                f"Suwayomi returned HTTP {response.status_code}",
                _latency_ms(start),
                url=url,
                status_code=response.status_code,
            )
        return _ok("suwayomi", _latency_ms(start), url=url, status_code=response.status_code)
    except Exception as exc:  # noqa: BLE001
        return _error("suwayomi", str(exc), _latency_ms(start), url=url)


async def check_storage(settings: Settings) -> StatusPayload:
    start = time.perf_counter()
    storage_path = Path(settings.storage_path)

    try:
        if not storage_path.exists():
            return _error("storage", "Storage path does not exist", _latency_ms(start), path=str(storage_path))
        if not storage_path.is_dir():
            return _error("storage", "Storage path is not a directory", _latency_ms(start), path=str(storage_path))
        if not os.access(storage_path, os.W_OK):
            return _error("storage", "Storage path is not writable", _latency_ms(start), path=str(storage_path))

        test_file = storage_path / ".panelflow-write-test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)

        return _ok("storage", _latency_ms(start), path=str(storage_path), writable=True)
    except Exception as exc:  # noqa: BLE001
        return _error("storage", str(exc), _latency_ms(start), path=str(storage_path))
