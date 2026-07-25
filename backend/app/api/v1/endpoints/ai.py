"""Diagnostic and generation endpoints for the LLM layer.

/complete is a thin smoke test of the client wiring. /generate-spec turns a
plain-language request into a validated StrategySpec.
"""

from fastapi import APIRouter, Depends

from app.ai.client import LLMClient
from app.ai.fake_client import FakeLLMClient
from app.ai.models import CompletionRequest, Message, Role
from app.ai.prompts.strategy_generation import SPEC_PROMPT_VERSION
from app.ai.spec_generator import SpecGenerator
from app.api.deps import get_llm_client, get_spec_generator
from app.schemas.ai import (
    CompletionRequestBody,
    CompletionResponseBody,
    SpecGenerationRequestBody,
    SpecGenerationResponseBody,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
    "/complete",
    response_model=CompletionResponseBody,
    summary="One-shot LLM completion (diagnostic)",
)
async def complete(
    body: CompletionRequestBody,
    client: LLMClient = Depends(get_llm_client),
) -> CompletionResponseBody:
    """Send a single prompt to the configured LLM and return its reply."""
    request = CompletionRequest(
        messages=[Message(role=Role.USER, content=body.prompt)],
        system=body.system,
    )
    result = await client.complete(request)
    provider = "fake" if isinstance(client, FakeLLMClient) else "anthropic"
    return CompletionResponseBody(
        text=result.text,
        model=result.model,
        input_tokens=result.usage.input_tokens,
        output_tokens=result.usage.output_tokens,
        provider=provider,
    )


@router.post(
    "/generate-spec",
    response_model=SpecGenerationResponseBody,
    summary="Generate a structured strategy spec from plain language",
)
async def generate_spec(
    body: SpecGenerationRequestBody,
    generator: SpecGenerator = Depends(get_spec_generator),
) -> SpecGenerationResponseBody:
    """Turn a natural-language strategy description into a validated spec."""
    spec = await generator.generate(body.description)
    provider = "fake" if isinstance(generator.client, FakeLLMClient) else "anthropic"
    return SpecGenerationResponseBody(
        spec=spec,
        prompt_version=SPEC_PROMPT_VERSION,
        provider=provider,
    )