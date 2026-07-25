"""Tests for the spec generation service against the fake client."""

import pytest

from app.ai.fake_client import FakeLLMClient
from app.ai.spec_generator import SpecGenerationError, SpecGenerator


@pytest.mark.anyio
async def test_generate_parses_valid_spec(valid_spec_json: str) -> None:
    """A valid JSON reply is parsed into a StrategySpec and the prompt is sent."""
    client = FakeLLMClient(reply=valid_spec_json)
    generator = SpecGenerator(client)

    spec = await generator.generate("momentum BTC with RSI and EMA")

    assert spec.symbol == "BTC-USD"
    assert len(spec.indicators) == 2
    assert client.last_request is not None
    assert client.last_request.system is not None
    assert client.last_request.metadata["prompt_version"]


@pytest.mark.anyio
async def test_generate_tolerates_code_fences(valid_spec_json: str) -> None:
    """JSON wrapped in markdown fences is still extracted and parsed."""
    fenced = f"```json\n{valid_spec_json}\n```"
    generator = SpecGenerator(FakeLLMClient(reply=fenced))

    spec = await generator.generate("anything")

    assert spec.name == "BTC Momentum RSI+EMA"


@pytest.mark.anyio
async def test_generate_rejects_non_json() -> None:
    """A non-JSON reply raises a domain error, not a raw decode error."""
    generator = SpecGenerator(FakeLLMClient(reply="I cannot help with that."))

    with pytest.raises(SpecGenerationError):
        await generator.generate("anything")


@pytest.mark.anyio
async def test_generate_rejects_structurally_invalid_spec() -> None:
    """Valid JSON that violates the schema raises a domain error."""
    bad = '{"name": "x", "symbol": "BTC", "timeframe": "1h", "indicators": [], "entry_rules": []}'
    generator = SpecGenerator(FakeLLMClient(reply=bad))

    with pytest.raises(SpecGenerationError):
        await generator.generate("anything")