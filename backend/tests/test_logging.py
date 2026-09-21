import json
import logging

from assistant.logging_config import JsonFormatter, request_id_var


def test_json_formatter_includes_request_id_and_extra_fields() -> None:
    record = logging.makeLogRecord(
        {
            "name": "test",
            "levelname": "INFO",
            "levelno": logging.INFO,
            "msg": "hello %s",
            "args": ("world",),
            "tenant": "acme",  # what `extra={"tenant": "acme"}` produces
        }
    )

    token = request_id_var.set("req-123")
    try:
        output = json.loads(JsonFormatter().format(record))
    finally:
        request_id_var.reset(token)

    assert output["message"] == "hello world"
    assert output["level"] == "INFO"
    assert output["request_id"] == "req-123"
    assert output["tenant"] == "acme"
