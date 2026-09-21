from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from assistant.config import Settings
from assistant.main import create_app


@pytest.fixture
def app() -> FastAPI:
    """An app built with explicit test settings."""
    return create_app(Settings(environment="test"))


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
