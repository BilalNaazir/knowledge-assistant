"""Structured JSON logging with a per-request correlation ID."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

# Holds the correlation ID of the request currently being handled. A ContextVar is
# like a global that is safe under async: each request sees only its own value.
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# Attributes every LogRecord already has. Anything else on a record was passed by the
# caller through `extra={...}` and should appear in the JSON output.
_STANDARD_ATTRS = frozenset(logging.makeLogRecord({}).__dict__) | {"message", "asctime"}

_HANDLER_NAME = "assistant-json"


class JsonFormatter(logging.Formatter):
    """Render each log record as a single line of JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        for key, value in record.__dict__.items():
            if key not in _STANDARD_ATTRS:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str) -> None:
    """Send all logs to stdout as JSON. Safe to call more than once."""
    root = logging.getLogger()

    # Remove only the handler we installed earlier, so repeated calls (for example in
    # tests) don't stack duplicate handlers or remove other tools' handlers.
    for existing in list(root.handlers):
        if existing.get_name() == _HANDLER_NAME:
            root.removeHandler(existing)

    handler = logging.StreamHandler(sys.stdout)
    handler.set_name(_HANDLER_NAME)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(level)

    # Route uvicorn's own messages through our handler so they are JSON too.
    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    # We log every request ourselves (with a request ID), so silence uvicorn's version.
    logging.getLogger("uvicorn.access").disabled = True
