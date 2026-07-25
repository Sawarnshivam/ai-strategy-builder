"""Service that turns a natural-language request into a validated StrategySpec."""

import json

from pydantic import ValidationError as PydanticValidationError

from app.ai.client import LLMClient
from app.ai.models import CompletionRequest, Message, Role
from app.ai.prompts.strategy_generation import (
    SPEC_PROMPT_VERSION,
    SYSTEM_PROMPT,
    render_user_message,
)
from app.ai.strategy_spec import StrategySpec
from app.core.exceptions import LLMError
from app.core.logging import get_logger

logger = get_logger(__name__)

SPEC_MAX_TOKENS = 2048
SPEC_TEMPERATURE = 0.2


class SpecGenerationError(LLMError):
    """Raised when the LLM response cannot be parsed into a valid StrategySpec."""

    default_message = "The AI returned a strategy that could not be validated."


def _extract_json(raw: str) -> str:
    """Pull the JSON object out of a model response, tolerating stray fences.

    A well-behaved model returns bare JSON, but models occasionally wrap output
    in ```json fences despite instructions. We strip to the outermost braces.
    """
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[len("json"):]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise SpecGenerationError("No JSON object found in the AI response.")
    return text[start : end + 1]


class SpecGenerator:
    """Coordinates prompt, LLM call, and validation into a typed spec."""

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    async def generate(self, description: str) -> StrategySpec:
        """Produce a validated StrategySpec from a plain-language description."""
        request = CompletionRequest(
            messages=[Message(role=Role.USER, content=render_user_message(description))],
            system=SYSTEM_PROMPT,
            max_tokens=SPEC_MAX_TOKENS,
            temperature=SPEC_TEMPERATURE,
            metadata={"prompt_version": SPEC_PROMPT_VERSION},
        )
        result = await self._client.complete(request)

        try:
            payload = json.loads(_extract_json(result.text))
        except json.JSONDecodeError as exc:
            logger.warning("Spec JSON decode failed: %s", exc)
            raise SpecGenerationError("The AI response was not valid JSON.") from exc

        try:
            spec = StrategySpec.model_validate(payload)
        except PydanticValidationError as exc:
            logger.warning("Spec validation failed: %s", exc)
            raise SpecGenerationError() from exc

        logger.info("Generated spec %r (%s)", spec.name, spec.symbol)
        return spec
    
    @property
    def client(self) -> LLMClient:
        """The underlying LLM client (used to report the active provider)."""
        return self._client
