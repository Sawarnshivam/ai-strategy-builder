"""Tests for authentication endpoints and password security."""

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import hash_password, verify_password

BASE = "/api/v1/auth"


def test_password_hash_roundtrip() -> None:
    """A hashed password verifies and differs from the plaintext."""
    hashed = hash_password("supersecret123")

    assert hashed != "supersecret123"
    assert verify_password("supersecret123", hashed)
    assert not verify_password("wrong", hashed)


def test_signup_returns_token(client: TestClient) -> None:
    """Signup creates an account and returns a bearer token."""
    response = client.post(
        f"{BASE}/signup",
        json={"email": "a@example.com", "password": "supersecret123"},
    )

    assert response.status_code == 201
    assert response.json()["access_token"]


def test_duplicate_signup_conflicts(client: TestClient) -> None:
    """Registering the same email twice returns 409."""
    payload = {"email": "dup@example.com", "password": "supersecret123"}
    client.post(f"{BASE}/signup", json=payload)

    response = client.post(f"{BASE}/signup", json=payload)
    assert response.status_code == 409


def test_login_succeeds_and_wrong_password_fails(client: TestClient) -> None:
    """Login returns a token; a bad password is rejected with 401."""
    client.post(
        f"{BASE}/signup",
        json={"email": "b@example.com", "password": "supersecret123"},
    )

    ok = client.post(
        f"{BASE}/login",
        json={"email": "b@example.com", "password": "supersecret123"},
    )
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    bad = client.post(
        f"{BASE}/login",
        json={"email": "b@example.com", "password": "wrongpass"},
    )
    assert bad.status_code == 401


def test_me_requires_token(client: TestClient) -> None:
    """The /me route rejects requests without a token."""
    assert client.get(f"{BASE}/me").status_code == 401


def test_me_returns_current_user(client: TestClient, auth_headers: dict[str, str]) -> None:
    """With a valid token, /me returns the user profile."""
    response = client.get(f"{BASE}/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == "tester@example.com"


def test_expired_secret_rejects_token(client: TestClient) -> None:
    """A token signed with a different secret is rejected."""
    from app.core.security import create_access_token

    forged = create_access_token("00000000-0000-0000-0000-000000000000", get_settings())
    # Tamper: append junk so the signature no longer matches.
    response = client.get(f"{BASE}/me", headers={"Authorization": f"Bearer {forged}x"})
    assert response.status_code == 401