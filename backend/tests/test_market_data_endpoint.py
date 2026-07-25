"""Integration test for the market-data preview endpoint."""

from fastapi.testclient import TestClient


def test_preview_returns_bars(client: TestClient) -> None:
    """The preview endpoint returns a bar count and sample rows."""
    response = client.get(
        "/api/v1/market-data/preview",
        params={"symbol": "BTC-USD", "timeframe": "1h", "days": 10},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "BTC-USD"
    assert body["count"] > 0
    assert len(body["bars"]) >= 1
    first = body["bars"][0]
    assert first["high"] >= first["low"]


def test_preview_rejects_bad_timeframe(client: TestClient) -> None:
    """An unsupported timeframe surfaces as a 502 market-data error."""
    response = client.get(
        "/api/v1/market-data/preview",
        params={"timeframe": "7s", "days": 5},
    )

    assert response.status_code == 502