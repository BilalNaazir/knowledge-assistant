from collections.abc import Iterator, Mapping

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from assistant.api.health import ReadinessCheck, get_readiness_checks
from assistant.config import Settings
from assistant.main import create_app


async def _healthy() -> None:
    """A fake dependency check that always succeeds."""


@pytest.fixture
def app() -> FastAPI:
    """An app with test settings and fake, always-healthy dependency checks."""
    test_app = create_app(Settings(environment="test"))
    healthy_checks: Mapping[str, ReadinessCheck] = {"postgres": _healthy}
    test_app.dependency_overrides[get_readiness_checks] = lambda: healthy_checks
    return test_app


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
