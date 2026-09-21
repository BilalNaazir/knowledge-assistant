from fastapi.testclient import TestClient


def test_generates_request_id_when_none_supplied(client: TestClient) -> None:
    response = client.get("/health/live")

    assert len(response.headers["X-Request-ID"]) == 32  # a uuid4 in hex form


def test_reuses_valid_incoming_request_id(client: TestClient) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "trace-abc-12345"})

    assert response.headers["X-Request-ID"] == "trace-abc-12345"


def test_replaces_unsafe_incoming_request_id(client: TestClient) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "bad id with spaces!"})

    assert response.headers["X-Request-ID"] != "bad id with spaces!"
    assert len(response.headers["X-Request-ID"]) == 32
