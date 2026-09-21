"""ASGI middleware: request correlation IDs and per-request logging."""

import logging
import re
import time
import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from assistant.logging_config import request_id_var

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"

# Only accept incoming IDs that look harmless. Otherwise a caller could inject newlines
# or huge strings into our logs.
_SAFE_REQUEST_ID = re.compile(r"[A-Za-z0-9._-]{8,64}")

# Kubernetes probes hit these every few seconds; logging them would drown real traffic.
_QUIET_PATH_PREFIXES = ("/health",)


def _resolve_request_id(incoming: str | None) -> str:
    if incoming and _SAFE_REQUEST_ID.fullmatch(incoming):
        return incoming
    return uuid.uuid4().hex


class RequestContextMiddleware:
    """Give every request a correlation ID, echo it back, and log one line per request."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _resolve_request_id(Headers(scope=scope).get(REQUEST_ID_HEADER))
        # `scope["state"]` is shared with request handlers and error handlers.
        scope.setdefault("state", {})["request_id"] = request_id
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        status_code = 500  # assumed until a response actually starts

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        except Exception:
            logger.exception("unhandled exception")
            raise
        finally:
            path = scope["path"]
            if not path.startswith(_QUIET_PATH_PREFIXES):
                logger.info(
                    "request completed",
                    extra={
                        "method": scope["method"],
                        "path": path,
                        "status_code": status_code,
                        "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                    },
                )
            request_id_var.reset(token)
