"""Integration tests for the backtest endpoints."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.ai.fake_client import FakeLLMClient
from app.api.deps import get_llm_client
from app.db.session import get_db
from app.main import create_app

BASE = "/api/v1/backtests"


@pytest.fixture()
def bt_client(db_session: Session, valid_spec_json: str) -> Iterator[TestClient]:
    """A client whose LLM returns a valid spec; data is synthetic via the app."""
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


def test_run_from_description_returns_result(bt_client: TestClient) -> None:
    """Running from a description returns a full result with an equity curve."""
    response = bt_client.post(BASE, json={"description": "momentum BTC RSI EMA"})

    assert response.status_code == 201
    body = response.json()
    assert body["symbol"] == "BTC-USD"
    assert body["metrics"]["num_trades"] >= 0
    assert len(body["equity_curve"]) > 0
    assert body["id"]


def test_requesting_both_description_and_spec_is_rejected(bt_client: TestClient) -> None:
    """Supplying both sources fails validation."""
    response = bt_client.post(
        BASE,
        json={"description": "x", "spec": {"name": "y"}},
    )
    assert response.status_code == 422


def test_requesting_neither_is_rejected(bt_client: TestClient) -> None:
    """Supplying neither source fails validation."""
    response = bt_client.post(BASE, json={})
    assert response.status_code == 422


def test_get_and_list_runs(bt_client: TestClient) -> None:
    """A run can be listed and fetched by id after creation."""
    created = bt_client.post(BASE, json={"description": "momentum BTC"}).json()

    listing = bt_client.get(BASE, params={"limit": 10})
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1

    fetched = bt_client.get(f"{BASE}/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]


def test_get_unknown_run_returns_404(bt_client: TestClient) -> None:
    """An unknown run id returns a domain 404."""
    response = bt_client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404