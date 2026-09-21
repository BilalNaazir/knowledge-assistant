from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from assistant.config import Settings
from assistant.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A test client bound to an app that uses explicit test settings."""
    app = create_app(Settings(environment="test"))
    with TestClient(app) as test_client:
        yield test_client
