"""Diagnostic endpoint to verify the LLM layer end-to-end.

This is intentionally thin — a smoke test that the client wiring works. Real
strategy generation arrives in a later module with proper prompt templates.
"""

from fastapi import APIRouter, Depends

from app.ai.client import LLMClient
from app.ai.fake_client import FakeLLMClient
from app.ai.models import CompletionRequest, Message, Role
from app.api.deps import get_llm_client
from app.schemas.ai import CompletionRequestBody, CompletionResponseBody

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