from fastapi.testclient import TestClient


def test_liveness(client: TestClient) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_meta_reports_service_details(client: TestClient) -> None:
    response = client.get("/api/v1/meta")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "knowledge-assistant"
    assert body["environment"] == "test"


def test_unknown_route_returns_404(client: TestClient) -> None:
    assert client.get("/api/v1/nope").status_code == 404
