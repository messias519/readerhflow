from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import asyncpg
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from app.config import Settings, get_settings
from app.database import connect

password_hasher = PasswordHasher()
bearer_scheme = HTTPBearer(auto_error=False)


class User(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


def user_from_record(record: asyncpg.Record) -> User:
    return User(
        id=record["id"],
        email=record["email"],
        role=record["role"],
        is_active=record["is_active"],
    )


async def get_user_by_email(connection: asyncpg.Connection, email: str) -> asyncpg.Record | None:
    return await connection.fetchrow(
        """
        select id, email, password_hash, role, is_active
        from users
        where email = $1
        """,
        normalize_email(email),
    )


async def get_user_by_id(connection: asyncpg.Connection, user_id: int) -> asyncpg.Record | None:
    return await connection.fetchrow(
        """
        select id, email, password_hash, role, is_active
        from users
        where id = $1
        """,
        user_id,
    )


async def ensure_initial_admin(settings: Settings) -> None:
    connection = await connect(settings)
    try:
        email = normalize_email(settings.admin_email)
        existing = await get_user_by_email(connection, email)
        if existing is not None:
            return

        await connection.execute(
            """
            insert into users (email, password_hash, role, is_active)
            values ($1, $2, 'admin', true)
            """,
            email,
            hash_password(settings.admin_password),
        )
    finally:
        await connection.close()


def create_access_token(user: User, settings: Settings) -> tuple[str, int]:
    expires_delta = timedelta(minutes=settings.jwt_access_token_minutes)
    expires_at = datetime.now(UTC) + expires_delta
    payload: dict[str, Any] = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": expires_at,
        "iat": datetime.now(UTC),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def decode_access_token(token: str, settings: Settings) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        ) from exc


async def authenticate_user(settings: Settings, email: str, password: str) -> User | None:
    connection = await connect(settings)
    try:
        record = await get_user_by_email(connection, email)
        if record is None or not record["is_active"]:
            return None
        if not verify_password(password, record["password_hash"]):
            return None
        return user_from_record(record)
    finally:
        await connection.close()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(credentials.credentials, settings)
    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated") from exc

    connection = await connect(settings)
    try:
        record = await get_user_by_id(connection, user_id)
    finally:
        await connection.close()

    if record is None or not record["is_active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return user_from_record(record)
