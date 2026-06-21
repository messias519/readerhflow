from __future__ import annotations

import os

os.environ.setdefault("ADMIN_EMAIL", "phase3-admin@example.com")
os.environ.setdefault("ADMIN_PASSWORD", "Phase3AdminPassword123")
os.environ.setdefault("JWT_SECRET", "phase3-test-jwt-secret-change-me")
os.environ.setdefault("DATABASE_URL", "postgresql://panelflow:change-me@postgres:5432/panelflow")
os.environ.setdefault("REDIS_URL", "redis://redis:6379/0")
os.environ.setdefault("SUWAYOMI_URL", "http://suwayomi:4567")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient

from app.auth import ensure_initial_admin
from app.config import get_settings
from app.database import init_database
from app.main import app
from app.suwayomi import SearchResponse, SearchResult, SourceSummary, get_suwayomi_client

pytestmark = pytest.mark.anyio


class FakeSuwayomiClient:
    async def list_sources(self) -> list[SourceSummary]:
        return [
            SourceSummary(
                id="123",
                name="mangadex",
                display_name="MangaDex",
                language="en",
                status="installed",
            )
        ]

    async def search(self, source_id: str, query: str, page: int = 1) -> SearchResponse:
        return SearchResponse(
            source_id=source_id,
            query=query,
            has_next_page=False,
            results=[
                SearchResult(
                    title="Test Manga",
                    source_id=source_id,
                    source_name="MangaDex",
                    external_id="999",
                    external_url="https://example.test/manga/999",
                    cover_url="/api/v1/manga/999/thumbnail",
                    status="ONGOING",
                )
            ],
        )


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def prepared_database():
    settings = get_settings()
    await init_database(settings)
    connection = await asyncpg.connect(settings.database_url)
    try:
        await connection.execute("delete from users where email = $1", settings.admin_email.lower())
    finally:
        await connection.close()

    await ensure_initial_admin(settings)
    return settings


@pytest.fixture(autouse=True)
def fake_suwayomi_client():
    app.dependency_overrides[get_suwayomi_client] = lambda: FakeSuwayomiClient()
    yield
    app.dependency_overrides.clear()


async def auth_headers(client: AsyncClient, settings) -> dict[str, str]:
    response = await client.post(
        "/api/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_sources_requires_authentication(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/sources")

    assert response.status_code == 401


async def test_sources_with_authenticated_user(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await auth_headers(client, prepared_database)
        response = await client.get("/api/sources", headers=headers)

    assert response.status_code == 200
    assert response.json()[0]["display_name"] == "MangaDex"


async def test_search_requires_source_id(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await auth_headers(client, prepared_database)
        response = await client.get("/api/search?query=one-piece", headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "source_id_required"


async def test_add_external_library_item(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await auth_headers(client, prepared_database)
        response = await client.post(
            "/api/library/external",
            headers=headers,
            json={
                "title": "Test Manga",
                "item_type": "manga",
                "source_id": "123",
                "external_id": "999",
                "external_url": "https://example.test/manga/999",
                "cover_url": "/api/v1/manga/999/thumbnail",
                "status": "ONGOING",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Test Manga"
    assert payload["source_type"] == "external_suwayomi"
    assert payload["source_id"] == "123"


async def test_external_library_item_is_not_duplicated(prepared_database):
    payload = {
        "title": "Duplicate Manga",
        "item_type": "manga",
        "source_id": "123",
        "external_id": "duplicate-999",
        "status": "ONGOING",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await auth_headers(client, prepared_database)
        first = await client.post("/api/library/external", headers=headers, json=payload)
        second = await client.post("/api/library/external", headers=headers, json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
