"""Verifies the browser origin used by the frontend is allowed."""

from fastapi.testclient import TestClient

ALLOWED_ORIGIN = "http://localhost:3000"


def test_preflight_allows_frontend_origin(client: TestClient) -> None:
    """A CORS preflight from the dev frontend is accepted."""
    response = client.options(
        "/api/v1/strategies",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


def test_unknown_origin_is_not_allowed(client: TestClient) -> None:
    """Origins outside the allow-list get no CORS header back."""
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://evil.example"},
    )

    assert "access-control-allow-origin" not in response.headers