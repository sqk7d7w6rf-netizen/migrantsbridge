"""Claude API client wrapper using the Anthropic SDK.

Centralizes timeout/retry configuration, safe extraction of text from the
response content blocks, and tolerant JSON parsing so that callers in the
service layer get a clean ``str``/``dict`` interface and predictable errors.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import anthropic
from anthropic import AsyncAnthropic

from app.config import settings

logger = logging.getLogger(__name__)


class ClaudeError(RuntimeError):
    """Raised when a Claude API call fails or returns an unusable response."""


class ClaudeClient:
    """Wrapper around the Anthropic AsyncAnthropic client for Claude API calls."""

    def __init__(self) -> None:
        # The SDK retries connection errors, 408/409/429 and >=500 with
        # exponential backoff; `timeout` bounds each attempt.
        self._client = AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            timeout=settings.CLAUDE_TIMEOUT_SECONDS,
            max_retries=settings.CLAUDE_MAX_RETRIES,
        )
        self._model = settings.CLAUDE_MODEL
        self._default_max_tokens = settings.CLAUDE_MAX_TOKENS

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int | None = None,
        temperature: float = 0.3,
    ) -> str:
        """Send a message to Claude and return the text response."""
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens or self._default_max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                temperature=temperature,
            )
        except anthropic.APIStatusError as exc:
            logger.error("Claude API error (status %s): %s", exc.status_code, exc.message)
            raise ClaudeError(f"Claude API request failed: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            logger.error("Claude API connection error: %s", exc)
            raise ClaudeError("Could not reach the Claude API.") from exc

        return self._extract_text(response)

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Return the first text block from a response, not blindly ``content[0]``.

        Thinking or tool-use blocks may precede the text block, so we scan for the
        first block that actually carries text.
        """
        for block in response.content:
            if getattr(block, "type", None) == "text":
                return block.text
        logger.error("Claude response contained no text block: %r", response.content)
        raise ClaudeError("Claude response contained no text content.")

    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Send a message and parse the response as JSON."""
        raw = await self.generate(system_prompt, user_message, max_tokens, temperature)
        return self._parse_json(raw)

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        """Parse JSON from a model response, tolerating markdown fences and prose.

        Tries, in order: the cleaned string, the contents of a ```json``` fenced
        block, and finally the first ``{...}`` span found in the text.
        """
        cleaned = raw.strip()

        # Strip a leading/trailing markdown code fence if present.
        fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, re.DOTALL)
        if fence:
            cleaned = fence.group(1).strip()

        for candidate in (cleaned, _first_json_object(cleaned)):
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed

        logger.error("Failed to parse Claude response as JSON: %s", raw[:500])
        raise ClaudeError(
            f"Claude returned invalid JSON. Raw response starts with: {raw[:200]}"
        )

    async def classify(
        self,
        system_prompt: str,
        content: str,
        categories: list[str],
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """Classify content into one of the given categories."""
        user_message = (
            f"Content to classify:\n\n{content}\n\n"
            f"Valid categories: {', '.join(categories)}\n\n"
            "Respond with JSON: {\"category\": \"...\", \"confidence\": 0.0-1.0, \"reasoning\": \"...\"}"
        )
        return await self.generate_json(system_prompt, user_message, max_tokens)

    async def assess(
        self,
        system_prompt: str,
        data: dict[str, Any],
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Perform an AI assessment on structured data."""
        user_message = f"Data for assessment:\n\n{json.dumps(data, indent=2, default=str)}"
        return await self.generate_json(system_prompt, user_message, max_tokens)


def _first_json_object(text: str) -> str | None:
    """Return the substring from the first ``{`` to the last ``}``, or ``None``."""
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return None


# Singleton instance
claude_client = ClaudeClient()
