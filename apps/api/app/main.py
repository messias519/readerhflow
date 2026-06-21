from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.status import check_database, check_redis, check_storage, check_suwayomi

settings = get_settings()

app = FastAPI(
    title="PanelFlow API",
    description="Infrastructure status API for reader.hflow Phase 1.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "panelflow-api"}


@app.get("/api/suwayomi/status")
async def suwayomi_status() -> dict[str, Any]:
    result = await check_suwayomi(settings)
    return {
        "checked_at": datetime.now(UTC).isoformat(),
        "suwayomi": result,
    }


@app.get("/api/status")
async def api_status() -> dict[str, Any]:
    database, redis, suwayomi, storage = await asyncio.gather(
        check_database(settings),
        check_redis(settings),
        check_suwayomi(settings),
        check_storage(settings),
    )

    services = {
        "app": {"name": "app", "status": "ok"},
        "database": database,
        "redis": redis,
        "suwayomi": suwayomi,
        "storage": storage,
    }
    overall = "ok" if all(service["status"] == "ok" for service in services.values()) else "degraded"

    return {
        "app": "PanelFlow",
        "environment": "phase-1",
        "status": overall,
        "checked_at": datetime.now(UTC).isoformat(),
        "services": services,
    }
