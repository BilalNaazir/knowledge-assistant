import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from assistant.api.health import get_readiness_checks
from assistant.config import Settings
from assistant.main import create_app


def test_ready_when_dependencies_are_healthy(client: TestClient) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"postgres": "ok"}}


def test_not_ready_when_a_dependency_fails(app: FastAPI, client: TestClient) -> None:
    async def broken() -> None:
        raise ConnectionError("password=hunter2 host=db.internal")

    app.dependency_overrides[get_readiness_checks] = lambda: {"postgres": broken}

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "checks": {"postgres": "failed"}}
    assert "hunter2" not in response.text  # the failure reason must not leak


def test_not_ready_when_a_dependency_hangs() -> None:
    async def hangs() -> None:
        await asyncio.sleep(5)

    app = create_app(Settings(environment="test", readiness_timeout_seconds=0.05))
    app.dependency_overrides[get_readiness_checks] = lambda: {"postgres": hangs}

    with TestClient(app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 503


def test_liveness_ignores_dependency_failures(app: FastAPI, client: TestClient) -> None:
    async def broken() -> None:
        raise ConnectionError("database down")

    app.dependency_overrides[get_readiness_checks] = lambda: {"postgres": broken}

    assert client.get("/health/live").status_code == 200
