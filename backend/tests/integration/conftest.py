"""Fixtures shared by every integration test: a real, throwaway Postgres."""

from collections.abc import AsyncIterator, Iterator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.community.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """Start one Postgres container for the whole test session, not per test.

    Starting a container takes a second or two; sharing it across tests keeps the
    suite fast. Using pgvector's image (not plain postgres) matches what we run
    in Compose and production.
    """
    with PostgresContainer("pgvector/pgvector:pg17", driver="asyncpg") as container:
        yield container


@pytest.fixture
async def engine(postgres_container: PostgresContainer) -> AsyncIterator[AsyncEngine]:
    """A fresh engine per test, pointed at the shared container."""
    test_engine = create_async_engine(postgres_container.get_connection_url())
    yield test_engine
    await test_engine.dispose()
