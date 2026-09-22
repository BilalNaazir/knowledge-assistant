"""Integration tests: real Postgres, real SQL, real pgvector extension."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from assistant.db import check_database

pytestmark = pytest.mark.integration


async def test_check_database_succeeds_against_a_real_database(engine: AsyncEngine) -> None:
    await check_database(engine)  # raises on failure, so no assertion needed


async def test_pgvector_extension_can_be_enabled(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        result = await connection.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        assert result.scalar_one() == "vector"


async def test_a_basic_table_round_trip(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(text("CREATE TABLE greeting (message TEXT NOT NULL)"))
        await connection.execute(
            text("INSERT INTO greeting (message) VALUES (:message)"),
            {"message": "hello from a real database"},
        )
        result = await connection.execute(text("SELECT message FROM greeting"))
        assert result.scalar_one() == "hello from a real database"
