from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.auth import (
    LoginRequest,
    LoginResponse,
    User,
    authenticate_user,
    create_access_token,
    ensure_initial_admin,
    get_current_admin_user,
    get_current_user,
)
from app.config import get_settings
from app.database import init_database
from app.library import (
    ExternalLibraryItemCreate,
    LibraryItem,
    add_external_library_item,
    get_library_item,
    list_library_items,
)
from app.status import check_database, check_redis, check_storage, check_suwayomi
from app.suwayomi import (
    SearchResponse,
    SourceDetail,
    SourceSummary,
    SuwayomiClient,
    SuwayomiClientError,
    get_suwayomi_client,
    suwayomi_http_error,
)

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
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
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
        "environment": "phase-3",
        "status": overall,
        "checked_at": datetime.now(UTC).isoformat(),
        "services": services,
    }


@app.get("/api/sources", response_model=list[SourceSummary])
async def sources(
    _current_user: Annotated[User, Depends(get_current_user)],
    client: Annotated[SuwayomiClient, Depends(get_suwayomi_client)],
) -> list[SourceSummary]:
    try:
        return await client.list_sources()
    except SuwayomiClientError as exc:
        raise suwayomi_http_error(exc) from exc


@app.get("/api/sources/{source_id}", response_model=SourceDetail)
async def source_detail(
    source_id: str,
    _current_user: Annotated[User, Depends(get_current_user)],
    client: Annotated[SuwayomiClient, Depends(get_suwayomi_client)],
) -> SourceDetail:
    try:
        return await client.get_source(source_id)
    except SuwayomiClientError as exc:
        raise suwayomi_http_error(exc) from exc


@app.get("/api/search", response_model=SearchResponse)
async def search(
    current_user: Annotated[User, Depends(get_current_user)],
    client: Annotated[SuwayomiClient, Depends(get_suwayomi_client)],
    source_id: str | None = None,
    query: str | None = None,
    page: int = 1,
) -> SearchResponse:
    del current_user
    if not source_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "source_id_required", "message": "Choose a source before searching."},
        )
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "query_required", "message": "Enter a search term."},
        )

    try:
        return await client.search(source_id, query.strip(), page)
    except SuwayomiClientError as exc:
        raise suwayomi_http_error(exc) from exc


@app.post("/api/library/external", response_model=LibraryItem)
async def add_external_to_library(
    payload: ExternalLibraryItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> LibraryItem:
    return await add_external_library_item(settings, current_user.id, payload)


@app.get("/api/library", response_model=list[LibraryItem])
async def library(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[LibraryItem]:
    return await list_library_items(settings, current_user.id)


@app.get("/api/library/{item_id}", response_model=LibraryItem)
async def library_detail(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> LibraryItem:
    item = await get_library_item(settings, current_user.id, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Library item not found")
    return item


@app.get("/api/suwayomi/image")
async def suwayomi_image(
    _current_user: Annotated[User, Depends(get_current_user)],
    client: Annotated[SuwayomiClient, Depends(get_suwayomi_client)],
    image_url: Annotated[str, Query(..., min_length=1, alias="url")],
) -> Response:
    del _current_user
    try:
        content, content_type = await client.fetch_internal_image(image_url)
    except SuwayomiClientError as exc:
        raise suwayomi_http_error(exc) from exc
    return Response(content=content, media_type=content_type)


@app.api_route(
    "/api/admin/suwayomi",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
@app.api_route(
    "/api/admin/suwayomi/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def admin_suwayomi_proxy(
    request: Request,
    _current_user: Annotated[User, Depends(get_current_admin_user)],
    client: Annotated[SuwayomiClient, Depends(get_suwayomi_client)],
    path: str = "",
) -> Response:
    del _current_user
    try:
        return await client.proxy_webui(request, path)
    except SuwayomiClientError as exc:
        raise suwayomi_http_error(exc) from exc
