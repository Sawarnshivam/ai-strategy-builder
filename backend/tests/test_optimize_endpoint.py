"""Integration test for the optimize sweep endpoint."""

from fastapi.testclient import TestClient

BASE = "/api/v1/optimize/sweep"


def _body() -> dict:
    return {
        "spec": {
            "name": "SMA Trend",
            "symbol": "BTC-USD",
            "timeframe": "1h",
            "indicators": [{"name": "sma", "type": "sma", "params": {"period": 10}}],
            "entry_rules": [{"left": "price", "comparator": "greater_than", "right": "sma"}],
            "exit_rules": [{"left": "price", "comparator": "less_than", "right": "sma"}],
        },
        "indicator_name": "sma",
        "param": "period",
        "start": 5,
        "stop": 20,
        "step": 5,
        "rank_by": "sharpe_ratio",
    }


def test_sweep_returns_ranked_points(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """The endpoint returns a ranked sweep with a best value."""
    response = client.post(BASE, json=_body(), headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body["points"]) == 4
    assert body["best_value"] == body["points"][0]["value"]
    assert body["rank_by"] == "sharpe_ratio"


def test_sweep_rejects_unknown_indicator(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Sweeping an undeclared indicator returns a 422 domain error."""
    body = _body()
    body["indicator_name"] = "rsi"

    response = client.post(BASE, json=body, headers=auth_headers)
    assert response.status_code == 422


def test_sweep_requires_auth(client: TestClient) -> None:
    """The sweep endpoint rejects requests with no token."""
    response = client.post(BASE, json=_body())
    assert response.status_code == 401