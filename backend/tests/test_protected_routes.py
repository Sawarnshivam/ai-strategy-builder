"""Verifies write routes require authentication."""

from fastapi.testclient import TestClient

SPEC_BODY = {
    "spec": {
        "name": "Auth Test",
        "symbol": "BTC-USD",
        "timeframe": "1h",
        "indicators": [{"name": "sma", "type": "sma", "params": {"period": 10}}],
        "entry_rules": [{"left": "price", "comparator": "greater_than", "right": "sma"}],
        "exit_rules": [{"left": "price", "comparator": "less_than", "right": "sma"}],
    }
}


def test_backtest_requires_auth(client: TestClient) -> None:
    """Running a backtest without a token is rejected."""
    assert client.post("/api/v1/backtests", json=SPEC_BODY).status_code == 401


def test_backtest_succeeds_with_auth(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """With a token, the backtest runs."""
    response = client.post("/api/v1/backtests", json=SPEC_BODY, headers=auth_headers)
    assert response.status_code == 201


def test_create_strategy_requires_auth(client: TestClient) -> None:
    """Creating a strategy without a token is rejected."""
    body = {"name": "X", "prompt": "test"}
    assert client.post("/api/v1/strategies", json=body).status_code == 401


def test_list_strategies_stays_public(client: TestClient) -> None:
    """Reads remain open — listing needs no token."""
    assert client.get("/api/v1/strategies").status_code == 200