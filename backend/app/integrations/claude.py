"""Claude API client wrapper using the Anthropic SDK."""

from __future__ import annotations

import json
import logging
from typing import Any

from anthropic import AsyncAnthropic

from app.config import settings

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Wrapper around the Anthropic AsyncAnthropic client for Claude API calls."""

    def __init__(self) -> None:
        self._client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._model = settings.CLAUDE_MODEL

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> str:
        """Send a message to Claude and return the text response."""
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=temperature,
        )
        return response.content[0].text

    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Send a message and parse the response as JSON."""
        raw = await self.generate(system_prompt, user_message, max_tokens, temperature)
        # Strip markdown code blocks if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first and last line (```json and ```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude response as JSON: %s", raw[:500])
            raise ValueError(f"Claude returned invalid JSON. Raw response starts with: {raw[:200]}")

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
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Perform an AI assessment on structured data."""
        user_message = f"Data for assessment:\n\n{json.dumps(data, indent=2, default=str)}"
        return await self.generate_json(system_prompt, user_message, max_tokens)


# Singleton instance
claude_client = ClaudeClient()
