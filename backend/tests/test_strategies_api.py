"""Integration tests for the strategy CRUD endpoints."""

from fastapi.testclient import TestClient

BASE = "/api/v1/strategies"

PAYLOAD = {
    "name": "BTC Momentum RSI+EMA",
    "description": "Long when RSI recovers above 30 with price over the 200 EMA.",
    "prompt": "Create a momentum strategy for BTC using RSI and EMA.",
    "parameters": {"rsi_period": 14, "ema_period": 200},
}


def test_create_returns_201_and_persisted_entity(client: TestClient) -> None:
    """A valid payload is stored and echoed back with server-generated fields."""
    response = client.post(BASE, json=PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == PAYLOAD["name"]
    assert body["parameters"]["rsi_period"] == 14
    assert body["id"] and body["created_at"]


def test_duplicate_name_returns_409(client: TestClient) -> None:
    """Names are unique across strategies."""
    client.post(BASE, json=PAYLOAD)
    response = client.post(BASE, json=PAYLOAD)

    assert response.status_code == 409
    assert response.json()["code"] == "ConflictError"


def test_blank_name_returns_422(client: TestClient) -> None:
    """Whitespace-only names are rejected by schema validation."""
    response = client.post(BASE, json={**PAYLOAD, "name": "   "})
    assert response.status_code == 422


def test_list_returns_paginated_envelope(client: TestClient) -> None:
    """Listing returns items plus pagination metadata."""
    client.post(BASE, json=PAYLOAD)
    client.post(BASE, json={**PAYLOAD, "name": "ETH Reversion"})

    response = client.get(BASE, params={"limit": 1, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["total"] == 2
    assert body["limit"] == 1


def test_get_unknown_id_returns_404(client: TestClient) -> None:
    """Unknown ids produce a domain 404, not a 500."""
    response = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["code"] == "NotFoundError"


def test_patch_applies_partial_update(client: TestClient) -> None:
    """Omitted fields are preserved by a PATCH."""
    created = client.post(BASE, json=PAYLOAD).json()

    response = client.patch(
        f"{BASE}/{created['id']}",
        json={"description": "Updated thesis."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "Updated thesis."
    assert body["name"] == PAYLOAD["name"]


def test_delete_removes_strategy(client: TestClient) -> None:
    """Deleting returns 204 and the resource is gone afterwards."""
    created = client.post(BASE, json=PAYLOAD).json()

    assert client.delete(f"{BASE}/{created['id']}").status_code == 204
    assert client.get(f"{BASE}/{created['id']}").status_code == 404