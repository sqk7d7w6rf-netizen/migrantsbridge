"""Tests for the Claude client wrapper: text extraction, JSON parsing, errors."""

from __future__ import annotations

import anthropic
import httpx
import pytest

from app.integrations.claude import ClaudeClient, ClaudeError
from tests.conftest import FakeBlock, FakeResponse


# --- _extract_text -----------------------------------------------------------

def test_extract_text_returns_first_text_block():
    response = FakeResponse([FakeBlock("text", "hello world")])
    assert ClaudeClient._extract_text(response) == "hello world"


def test_extract_text_skips_non_text_blocks():
    response = FakeResponse(
        [FakeBlock("thinking"), FakeBlock("text", "the answer")]
    )
    assert ClaudeClient._extract_text(response) == "the answer"


def test_extract_text_raises_when_no_text_block():
    response = FakeResponse([FakeBlock("tool_use")])
    with pytest.raises(ClaudeError):
        ClaudeClient._extract_text(response)


# --- _parse_json -------------------------------------------------------------

def test_parse_json_plain_object():
    assert ClaudeClient._parse_json('{"a": 1}') == {"a": 1}


def test_parse_json_strips_markdown_fence():
    raw = '```json\n{"category": "passport", "confidence": 0.9}\n```'
    assert ClaudeClient._parse_json(raw) == {"category": "passport", "confidence": 0.9}


def test_parse_json_strips_bare_fence():
    assert ClaudeClient._parse_json('```\n{"ok": true}\n```') == {"ok": True}


def test_parse_json_extracts_object_from_surrounding_prose():
    raw = 'Here is the result:\n{"status": "approved"}\nLet me know if you need more.'
    assert ClaudeClient._parse_json(raw) == {"status": "approved"}


def test_parse_json_raises_on_garbage():
    with pytest.raises(ClaudeError):
        ClaudeClient._parse_json("not json at all")


def test_parse_json_raises_on_non_object_json():
    # A bare JSON array is valid JSON but not the dict callers expect.
    with pytest.raises(ClaudeError):
        ClaudeClient._parse_json("[1, 2, 3]")


# --- generate (mocked SDK) ---------------------------------------------------

class _FakeMessages:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        if self._exc is not None:
            raise self._exc
        return self._response


def _client_with(messages) -> ClaudeClient:
    client = ClaudeClient()
    client._client.messages = messages  # type: ignore[attr-defined]
    return client


async def test_generate_returns_text():
    messages = _FakeMessages(response=FakeResponse([FakeBlock("text", "done")]))
    client = _client_with(messages)
    result = await client.generate("system", "user")
    assert result == "done"
    # Default max_tokens from settings should be applied.
    assert messages.calls[0]["max_tokens"] == client._default_max_tokens


async def test_generate_json_parses_response():
    messages = _FakeMessages(response=FakeResponse([FakeBlock("text", '{"x": 1}')]))
    client = _client_with(messages)
    assert await client.generate_json("system", "user") == {"x": 1}


async def test_generate_wraps_api_status_error():
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx.Response(500, request=request)
    exc = anthropic.APIStatusError("boom", response=response, body=None)
    client = _client_with(_FakeMessages(exc=exc))
    with pytest.raises(ClaudeError):
        await client.generate("system", "user")


async def test_generate_wraps_connection_error():
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    exc = anthropic.APIConnectionError(request=request)
    client = _client_with(_FakeMessages(exc=exc))
    with pytest.raises(ClaudeError):
        await client.generate("system", "user")
