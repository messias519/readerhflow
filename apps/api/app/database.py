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
        await connection.execute(
            """
            create table if not exists library_items (
                id bigserial primary key,
                user_id bigint not null references users(id) on delete cascade,
                title text not null,
                subtitle text,
                item_type text not null default 'unknown',
                source_type text not null,
                source_id text not null,
                external_id text not null,
                external_url text,
                cover_url text,
                description text,
                status text,
                created_at timestamptz not null default now(),
                updated_at timestamptz not null default now(),
                constraint library_items_user_external_unique
                    unique (user_id, source_type, source_id, external_id)
            );
            """
        )
    finally:
        await connection.close()
