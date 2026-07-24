"""Unit tests for the fake LLM client."""

import pytest

from app.ai.fake_client import DEFAULT_REPLY, FakeLLMClient
from app.ai.models import CompletionRequest, Message, Role


def _request(text: str = "hello") -> CompletionRequest:
    return CompletionRequest(messages=[Message(role=Role.USER, content=text)])


@pytest.mark.anyio
async def test_complete_returns_scripted_reply() -> None:
    """A scripted reply is returned verbatim with token accounting."""
    client = FakeLLMClient(reply="pong")

    result = await client.complete(_request("ping"))

    assert result.text == "pong"
    assert result.usage.output_tokens == 1
    assert client.call_count == 1
    assert client.last_request is not None
    assert client.last_request.messages[0].content == "ping"


@pytest.mark.anyio
async def test_default_reply_used_when_unscripted() -> None:
    """Without a script, the documented default is returned."""
    client = FakeLLMClient()

    result = await client.complete(_request())

    assert result.text == DEFAULT_REPLY


@pytest.mark.anyio
async def test_stream_yields_whole_reply() -> None:
    """Streaming reassembles into the same text as complete()."""
    client = FakeLLMClient(reply="one two three")

    chunks = [chunk async for chunk in client.stream(_request())]

    assert "".join(chunks).strip() == "one two three"