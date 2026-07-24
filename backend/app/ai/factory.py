"""Chooses and builds the LLM client based on configuration."""

from app.ai.client import LLMClient
from app.ai.fake_client import FakeLLMClient
from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def build_llm_client(settings: Settings) -> LLMClient:
    """Return the real client when a key is set, otherwise the fake one.

    Importing AnthropicClient lazily means the SDK is only required when a key
    is actually configured — the fake path has no dependency on the SDK at all.
    """
    if settings.llm_enabled:
        from app.ai.anthropic_client import AnthropicClient

        logger.info("LLM client: Anthropic (model=%s)", settings.llm_model)
        return AnthropicClient(settings)

    logger.warning("LLM client: fake (no ANTHROPIC_API_KEY set). Responses are canned.")
    return FakeLLMClient()