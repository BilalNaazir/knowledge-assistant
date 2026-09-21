from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from assistant.errors import NotFoundError


@pytest.fixture
def error_client(app: FastAPI) -> Iterator[TestClient]:
    """A client for an app with a few deliberately failing test-only routes."""

    async def missing() -> None:
        raise NotFoundError("Document 42 does not exist")

    async def boom() -> None:
        raise RuntimeError("secret internal detail")

    async def get_item(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    app.add_api_route("/_test/missing", missing)
    app.add_api_route("/_test/boom", boom)
    app.add_api_route("/_test/items/{item_id}", get_item)

    # By default the test client re-raises server errors, which would hide the 500
    # response we want to inspect.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_app_error_uses_standard_shape(error_client: TestClient) -> None:
    response = error_client.get("/_test/missing")

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "not_found"
    assert error["message"] == "Document 42 does not exist"
    assert error["request_id"] == response.headers["X-Request-ID"]


def test_unknown_route_uses_standard_shape(client: TestClient) -> None:
    response = client.get("/api/v1/nope")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_validation_error_lists_fields_without_echoing_input(error_client: TestClient) -> None:
    response = error_client.get("/_test/items/not-a-number")

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    detail = error["details"][0]
    assert detail["loc"] == ["path", "item_id"]
    assert "input" not in detail


def test_unhandled_exception_hides_internals(error_client: TestClient) -> None:
    response = error_client.get("/_test/boom")

    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "internal_error"
    assert "secret" not in response.text
    assert error["request_id"] == response.headers["X-Request-ID"]
