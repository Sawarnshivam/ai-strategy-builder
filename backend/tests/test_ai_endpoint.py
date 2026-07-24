"""Integration test for the diagnostic AI endpoint."""

from fastapi.testclient import TestClient


def test_complete_endpoint_uses_fake_provider(client: TestClient) -> None:
    """With no key configured, the endpoint returns a fake completion."""
    response = client.post("/api/v1/ai/complete", json={"prompt": "hello there"})

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "fake"
    assert body["text"]
    assert body["output_tokens"] >= 1