from __future__ import annotations

import os

os.environ.setdefault("ADMIN_EMAIL", "admin-suwayomi@example.com")
os.environ.setdefault("ADMIN_PASSWORD", "AdminSuwayomiPassword123")
os.environ.setdefault("JWT_SECRET", "admin-suwayomi-test-jwt-secret-change-me")
os.environ.setdefault("DATABASE_URL", "postgresql://panelflow:change-me@postgres:5432/panelflow")
os.environ.setdefault("REDIS_URL", "redis://redis:6379/0")
os.environ.setdefault("SUWAYOMI_URL", "http://suwayomi:4567")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

import asyncpg
import pytest
from fastapi import Response
from httpx import ASGITransport, AsyncClient

from app.auth import ensure_initial_admin, hash_password
from app.config import get_settings
from app.database import init_database
from app.main import app
from app.suwayomi import SuwayomiClient, SuwayomiClientError, get_suwayomi_client

pytestmark = pytest.mark.anyio


class FakeSuwayomiWebUiClient:
    async def proxy_webui(self, request, path: str = "") -> Response:
        return Response(
            content=f"proxied:{request.method}:{path}:{request.url.query}",
            media_type="text/plain",
            headers={"x-frame-options": "DENY"},
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
        await connection.execute("delete from users where email in ($1, $2)", settings.admin_email.lower(), "viewer@example.com")
        await connection.execute(
            """
            insert into users (email, password_hash, role, is_active)
            values ($1, $2, 'viewer', true)
            """,
            "viewer@example.com",
            hash_password("ViewerPassword123"),
        )
    finally:
        await connection.close()

    await ensure_initial_admin(settings)
    return settings


@pytest.fixture(autouse=True)
def fake_suwayomi_client():
    app.dependency_overrides[get_suwayomi_client] = lambda: FakeSuwayomiWebUiClient()
    yield
    app.dependency_overrides.clear()


async def login(client: AsyncClient, email: str, password: str) -> dict[str, str]:
    response = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_admin_suwayomi_proxy_requires_authentication(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/suwayomi/")

    assert response.status_code == 401


async def test_admin_suwayomi_proxy_requires_admin(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await login(client, "viewer@example.com", "ViewerPassword123")
        response = await client.get("/api/admin/suwayomi/", headers=headers)

    assert response.status_code == 403


async def test_admin_suwayomi_proxy_forwards_admin_request(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await login(client, prepared_database.admin_email, prepared_database.admin_password)
        response = await client.post("/api/admin/suwayomi/api/graphql?x=1", headers=headers, content=b"{}")

    assert response.status_code == 200
    assert response.text == "proxied:POST:api/graphql:x=1"


def test_suwayomi_proxy_target_rejects_external_hosts():
    client = SuwayomiClient(get_settings())

    with pytest.raises(SuwayomiClientError) as exc_info:
        client._proxy_target("https://evil.example.test/", "")

    assert exc_info.value.code == "invalid_proxy_path"
