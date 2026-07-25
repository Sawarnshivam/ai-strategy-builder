"""Integration test for the spec generation endpoint.

Overrides the LLM client dependency with a fake scripted to return valid spec
JSON, so the full request path is exercised without an API key.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.ai.fake_client import FakeLLMClient
from app.api.deps import get_llm_client
from app.db.session import get_db
from app.main import create_app


@pytest.fixture()
def spec_client(db_session: Session, valid_spec_json: str) -> Iterator[TestClient]:
    """A TestClient whose LLM dependency returns a scripted valid spec."""
    app = create_app()

    def _fake_client() -> FakeLLMClient:
        return FakeLLMClient(reply=valid_spec_json)

    def _override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_llm_client] = _fake_client
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_generate_spec_returns_valid_spec(spec_client: TestClient) -> None:
    """The endpoint returns a parsed spec with provenance."""
    response = spec_client.post(
        "/api/v1/ai/generate-spec",
        json={"description": "momentum BTC using RSI and EMA"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "fake"
    assert body["spec"]["symbol"] == "BTC-USD"
    assert body["prompt_version"]


def test_generate_spec_rejects_empty_description(spec_client: TestClient) -> None:
    """An empty description is rejected by schema validation."""
    response = spec_client.post("/api/v1/ai/generate-spec", json={"description": ""})
    assert response.status_code == 422