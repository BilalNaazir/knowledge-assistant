"""Database engine setup and health check."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from assistant.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Create the async engine. This does not connect yet: connections open lazily."""
    return create_async_engine(
        settings.database_url.get_secret_value(),
        pool_size=5,  # connections kept open and reused
        max_overflow=5,  # extra connections allowed during bursts
        pool_pre_ping=True,  # test a connection before use; replace it if it died
    )


async def check_database(engine: AsyncEngine) -> None:
    """Raise if the database can't be reached."""
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
