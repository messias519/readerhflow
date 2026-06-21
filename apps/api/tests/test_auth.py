from __future__ import annotations

import os

os.environ.setdefault("ADMIN_EMAIL", "phase2-admin@example.com")
os.environ.setdefault("ADMIN_PASSWORD", "Phase2AdminPassword123")
os.environ.setdefault("JWT_SECRET", "phase2-test-jwt-secret-change-me")
os.environ.setdefault("DATABASE_URL", "postgresql://panelflow:change-me@postgres:5432/panelflow")
os.environ.setdefault("REDIS_URL", "redis://redis:6379/0")
os.environ.setdefault("SUWAYOMI_URL", "http://suwayomi:4567")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient

from app.auth import ensure_initial_admin, get_user_by_email
from app.config import get_settings
from app.database import init_database
from app.main import app

pytestmark = pytest.mark.anyio


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


async def test_initial_admin_is_created(prepared_database):
    connection = await asyncpg.connect(prepared_database.database_url)
    try:
        record = await get_user_by_email(connection, prepared_database.admin_email)
    finally:
        await connection.close()

    assert record is not None
    assert record["email"] == prepared_database.admin_email.lower()
    assert record["role"] == "admin"
    assert record["password_hash"] != prepared_database.admin_password
    assert record["password_hash"].startswith("$argon2")


async def test_login_valid(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": prepared_database.admin_email,
                "password": prepared_database.admin_password,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["user"]["email"] == prepared_database.admin_email.lower()


async def test_login_invalid(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": prepared_database.admin_email,
                "password": "wrong-password",
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


async def test_me_requires_authentication(prepared_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/auth/me")

    assert response.status_code == 401
