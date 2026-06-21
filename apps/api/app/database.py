from __future__ import annotations

import asyncpg

from app.config import Settings


async def connect(settings: Settings) -> asyncpg.Connection:
    return await asyncpg.connect(settings.database_url, timeout=5)


async def init_database(settings: Settings) -> None:
    connection = await connect(settings)
    try:
        await connection.execute(
            """
            create table if not exists users (
                id bigserial primary key,
                email text not null unique,
                password_hash text not null,
                role text not null default 'admin',
                is_active boolean not null default true,
                created_at timestamptz not null default now(),
                updated_at timestamptz not null default now()
            );
            """
        )
    finally:
        await connection.close()
