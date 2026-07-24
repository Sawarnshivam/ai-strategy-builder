"""Tests for LLM client selection based on configuration."""

from app.ai.factory import build_llm_client
from app.ai.fake_client import FakeLLMClient
from app.core.config import Settings


def test_factory_returns_fake_without_key() -> None:
    """No API key means the fake client, so the app runs key-less."""
    settings = Settings(anthropic_api_key="")

    client = build_llm_client(settings)

    assert isinstance(client, FakeLLMClient)


def test_factory_returns_real_client_with_key() -> None:
    """A configured key selects the Anthropic client.

    The SDK does not perform any network call at construction time, so building
    the client is safe even with a dummy key.
    """
    from app.ai.anthropic_client import AnthropicClient

    settings = Settings(anthropic_api_key="sk-ant-dummy")

    client = build_llm_client(settings)

    assert isinstance(client, AnthropicClient)