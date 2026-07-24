"""Transport-agnostic value objects for LLM requests and responses.

These deliberately do not mention Anthropic. Features speak in Message and
CompletionResult so the provider can be swapped without touching call sites.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class Role(StrEnum):
    """Who authored a message in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True, slots=True)
class Message:
    """A single turn in a conversation."""

    role: Role
    content: str


@dataclass(frozen=True, slots=True)
class CompletionRequest:
    """A request for a model completion.

    system is optional and kept separate from the turns because Anthropic (and
    most providers) treat the system prompt as a distinct top-level field.
    """

    messages: list[Message]
    system: str | None = None
    max_tokens: int | None = None
    temperature: float = 1.0
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """Token accounting for a completion."""

    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        """Sum of input and output tokens."""
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True, slots=True)
class CompletionResult:
    """The full, non-streamed result of a completion."""

    text: str
    model: str
    usage: TokenUsage
    stop_reason: str | None = None