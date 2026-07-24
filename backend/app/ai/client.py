"""The LLMClient protocol that every provider implements."""

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from app.ai.models import CompletionRequest, CompletionResult


@runtime_checkable
class LLMClient(Protocol):
    """Provider-agnostic interface for language model completions.

    Depend on this, not on any concrete SDK. A real provider and a fake test
    double both satisfy it, so features and tests share one contract.
    """

    async def complete(self, request: CompletionRequest) -> CompletionResult:
        """Return a full completion for the request."""
        ...

    def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """Yield incremental text chunks as the model produces them."""
        ...