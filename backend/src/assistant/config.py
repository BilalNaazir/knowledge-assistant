"""Application configuration, loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All settings come from ASSISTANT_* environment variables (or a local .env file)."""

    model_config = SettingsConfigDict(
        env_prefix="ASSISTANT_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "knowledge-assistant"
    environment: Literal["local", "test", "staging", "production"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # SecretStr hides the value if the settings object is ever printed or logged.
    # The defaults match docker-compose.yml.
    database_url: SecretStr = SecretStr(
        "postgresql+asyncpg://assistant:assistant@localhost:5432/assistant"
    )
    readiness_timeout_seconds: float = 2.0


@lru_cache
def get_settings() -> Settings:
    """Return the settings, parsed once and cached for the life of the process."""
    return Settings()
