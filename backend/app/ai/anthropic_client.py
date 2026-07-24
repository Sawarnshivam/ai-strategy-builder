"""The production LLMClient backed by the Anthropic SDK."""

from collections.abc import AsyncIterator
from typing import Literal, cast

from anthropic import (
    APIConnectionError,
    APIStatusError,
    AsyncAnthropic,
    RateLimitError,
)
from anthropic.types import MessageParam

from app.ai.models import (
    CompletionRequest,
    CompletionResult,
    Message,
    TokenUsage,
)
from app.core.config import Settings
from app.core.exceptions import LLMError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnthropicClient:
    """Adapts the Anthropic async SDK to the LLMClient protocol.

    Owns model choice, token limits, timeout and retry policy so callers pass
    only a CompletionRequest and receive transport-agnostic results.
    """

    def __init__(self, settings: Settings, client: AsyncAnthropic | None = None) -> None:
        self._model = settings.llm_model
        self._default_max_tokens = settings.llm_max_tokens
        self._client = client or AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
        )

    @staticmethod
    def _to_sdk_messages(messages: list[Message]) -> list[MessageParam]:
        """Convert domain messages into the SDK's expected message shape."""
        return [
            MessageParam(
                role=cast(Literal["user", "assistant"], m.role.value),
                content=m.content,
            )
            for m in messages
        ]

    def _resolve_max_tokens(self, request: CompletionRequest) -> int:
        """Prefer the request's limit, falling back to the configured default."""
        return request.max_tokens or self._default_max_tokens

    async def complete(self, request: CompletionRequest) -> CompletionResult:
        """Call the Messages API and return a full completion."""
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._resolve_max_tokens(request),
                temperature=request.temperature,
                system=request.system or NOT_GIVEN_SYSTEM,
                messages=self._to_sdk_messages(request.messages),
            )
        except (APIConnectionError, RateLimitError, APIStatusError) as exc:
            logger.error("Anthropic completion failed: %s", exc)
            raise LLMError() from exc

        text = "".join(block.text for block in response.content if block.type == "text")
        return CompletionResult(
            text=text,
            model=response.model,
            usage=TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            ),
            stop_reason=response.stop_reason,
        )

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """Stream text chunks from the Messages API as they arrive."""
        try:
            async with self._client.messages.stream(
                model=self._model,
                max_tokens=self._resolve_max_tokens(request),
                temperature=request.temperature,
                system=request.system or NOT_GIVEN_SYSTEM,
                messages=self._to_sdk_messages(request.messages),
            ) as stream:
                async for chunk in stream.text_stream:
                    yield chunk
        except (APIConnectionError, RateLimitError, APIStatusError) as exc:
            logger.error("Anthropic stream failed: %s", exc)
            raise LLMError() from exc


# The SDK treats an omitted system prompt via its NOT_GIVEN sentinel; an empty
# string is rejected. Import lazily to keep the sentinel in one place.
from anthropic import NOT_GIVEN as NOT_GIVEN_SYSTEM  # noqa: E402