from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.auth import (
    LoginRequest,
    LoginResponse,
    User,
    authenticate_user,
    create_access_token,
    ensure_initial_admin,
    get_current_user,
)
from app.config import get_settings
from app.database import init_database
from app.status import check_database, check_redis, check_storage, check_suwayomi

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database(settings)
    await ensure_initial_admin(settings)
    yield


app = FastAPI(
    title="PanelFlow API",
    description="Infrastructure and authentication API for reader.hflow.",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "panelflow-api"}


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    user = await authenticate_user(settings, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token, expires_in = create_access_token(user, settings)
    return LoginResponse(access_token=token, expires_in=expires_in, user=user)


@app.get("/api/auth/me", response_model=User)
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@app.post("/api/auth/logout")
async def logout() -> dict[str, str]:
    return {"status": "ok"}


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
        "environment": "phase-2",
        "status": overall,
        "checked_at": datetime.now(UTC).isoformat(),
        "services": services,
    }
