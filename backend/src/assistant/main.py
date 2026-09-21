"""Application entry point."""

import logging

from fastapi import FastAPI

from assistant import __version__
from assistant.api import health
from assistant.api.error_handlers import register_error_handlers
from assistant.api.v1.router import api_router
from assistant.config import Settings, get_settings
from assistant.logging_config import configure_logging
from assistant.middleware import RequestContextMiddleware

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application.

    A factory (rather than a module-level `app`) means importing this module has no
    side effects, and tests can build an app with their own settings.
    """
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="Knowledge Assistant API",
        version=__version__,
        # Interactive docs are handy locally but shouldn't be exposed in production.
        docs_url=None if settings.environment == "production" else "/docs",
        redoc_url=None,
    )
    app.dependency_overrides[get_settings] = lambda: settings

    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(api_router)

    logger.info(
        "application created",
        extra={"environment": settings.environment, "version": __version__},
    )
    return app
