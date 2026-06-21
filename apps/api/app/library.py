from __future__ import annotations

from datetime import datetime

import asyncpg
from pydantic import BaseModel, Field

from app.config import Settings
from app.database import connect


class ExternalLibraryItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    subtitle: str | None = None
    item_type: str = "manga"
    source_id: str = Field(min_length=1, max_length=200)
    external_id: str = Field(min_length=1, max_length=1000)
    external_url: str | None = None
    cover_url: str | None = None
    thumbnail_url: str | None = None
    description: str | None = None
    status: str | None = None


class LibraryItem(BaseModel):
    id: int
    user_id: int
    title: str
    subtitle: str | None = None
    item_type: str
    source_type: str
    source_id: str
    external_id: str
    external_url: str | None = None
    cover_url: str | None = None
    description: str | None = None
    status: str | None = None
    created_at: datetime
    updated_at: datetime


def library_item_from_record(record: asyncpg.Record) -> LibraryItem:
    return LibraryItem(
        id=record["id"],
        user_id=record["user_id"],
        title=record["title"],
        subtitle=record["subtitle"],
        item_type=record["item_type"],
        source_type=record["source_type"],
        source_id=record["source_id"],
        external_id=record["external_id"],
        external_url=record["external_url"],
        cover_url=record["cover_url"],
        description=record["description"],
        status=record["status"],
        created_at=record["created_at"],
        updated_at=record["updated_at"],
    )


async def add_external_library_item(
    settings: Settings,
    user_id: int,
    payload: ExternalLibraryItemCreate,
) -> LibraryItem:
    connection = await connect(settings)
    try:
        record = await connection.fetchrow(
            """
            insert into library_items (
                user_id,
                title,
                subtitle,
                item_type,
                source_type,
                source_id,
                external_id,
                external_url,
                cover_url,
                description,
                status
            )
            values ($1, $2, $3, $4, 'external_suwayomi', $5, $6, $7, $8, $9, $10)
            on conflict (user_id, source_type, source_id, external_id)
            do update set updated_at = library_items.updated_at
            returning *
            """,
            user_id,
            payload.title.strip(),
            payload.subtitle,
            payload.item_type or "unknown",
            payload.source_id,
            payload.external_id,
            payload.external_url,
            payload.cover_url or payload.thumbnail_url,
            payload.description,
            payload.status,
        )
    finally:
        await connection.close()

    return library_item_from_record(record)


async def list_library_items(settings: Settings, user_id: int) -> list[LibraryItem]:
    connection = await connect(settings)
    try:
        records = await connection.fetch(
            """
            select *
            from library_items
            where user_id = $1
            order by created_at desc, id desc
            """,
            user_id,
        )
    finally:
        await connection.close()

    return [library_item_from_record(record) for record in records]


async def get_library_item(settings: Settings, user_id: int, item_id: int) -> LibraryItem | None:
    connection = await connect(settings)
    try:
        record = await connection.fetchrow(
            """
            select *
            from library_items
            where user_id = $1 and id = $2
            """,
            user_id,
            item_id,
        )
    finally:
        await connection.close()

    return library_item_from_record(record) if record else None
