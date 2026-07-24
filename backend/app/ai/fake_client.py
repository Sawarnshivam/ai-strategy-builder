"""A deterministic in-memory LLM client for tests and key-less local runs.

Returns canned text without any network call. Because it satisfies LLMClient,
the whole stack can be exercised end-to-end with no API key and no flakiness.
"""

from collections.abc import AsyncIterator

from app.ai.models import (
    CompletionRequest,
    CompletionResult,
    Message,
    Role,
    TokenUsage,
)

FAKE_MODEL = "fake-model-1"
DEFAULT_REPLY = "This is a canned response from the fake LLM client."


class FakeLLMClient:
    """Configurable stand-in for a real provider.

    Pass a scripted reply to control output, or rely on the default. Records the
    last request so tests can assert on what the feature actually sent.
    """

    def __init__(self, reply: str | None = None) -> None:
        self._reply = reply if reply is not None else DEFAULT_REPLY
        self.last_request: CompletionRequest | None = None
        self.call_count = 0

    def _record(self, request: CompletionRequest) -> None:
        self.last_request = request
        self.call_count += 1

    async def complete(self, request: CompletionRequest) -> CompletionResult:
        """Return the scripted reply with plausible token accounting."""
        self._record(request)
        prompt_text = " ".join(m.content for m in request.messages)
        return CompletionResult(
            text=self._reply,
            model=FAKE_MODEL,
            usage=TokenUsage(
                input_tokens=len(prompt_text.split()),
                output_tokens=len(self._reply.split()),
            ),
            stop_reason="end_turn",
        )

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """Yield the scripted reply word by word to mimic streaming."""
        self._record(request)
        for word in self._reply.split():
            yield f"{word} "


def echo_reply(messages: list[Message]) -> str:
    """Helper for tests: build a reply that echoes the last user message."""
    last_user = next(
        (m.content for m in reversed(messages) if m.role is Role.USER),
        "",
    )
    return f"echo: {last_user}"