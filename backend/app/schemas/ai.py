"""Pydantic schemas for the AI diagnostic endpoints."""

from pydantic import BaseModel, Field

from app.ai.strategy_spec import StrategySpec


class CompletionRequestBody(BaseModel):
    """Request body for a one-shot completion."""

    prompt: str = Field(..., min_length=1, max_length=8000, examples=["Say hello."])
    system: str | None = Field(default=None, max_length=8000)


class CompletionResponseBody(BaseModel):
    """Response body echoing model output and token usage."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int
    provider: str = Field(..., examples=["fake", "anthropic"])

class SpecGenerationRequestBody(BaseModel):
    """Request body for strategy-spec generation."""

    description: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        examples=["Create a momentum strategy for BTC using RSI and EMA."],
    )


class SpecGenerationResponseBody(BaseModel):
    """Response body wrapping the generated spec and its provenance."""

    spec: StrategySpec
    prompt_version: str
    provider: str = Field(..., examples=["fake", "anthropic"])