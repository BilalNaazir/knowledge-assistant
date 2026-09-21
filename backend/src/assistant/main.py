"""Application entry point."""

from fastapi import FastAPI

from assistant import __version__
from assistant.api import health
from assistant.api.v1.router import api_router
from assistant.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application.

    A factory (rather than a module-level `app`) means importing this module has no
    side effects, and tests can build an app with their own settings.
    """
    settings = settings or get_settings()

    app = FastAPI(
        title="Knowledge Assistant API",
        version=__version__,
        # Interactive docs are handy locally but shouldn't be exposed in production.
        docs_url=None if settings.environment == "production" else "/docs",
        redoc_url=None,
    )
    app.dependency_overrides[get_settings] = lambda: settings

    app.include_router(health.router)
    app.include_router(api_router)
    return app
