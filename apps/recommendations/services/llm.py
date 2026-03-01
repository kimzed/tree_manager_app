from __future__ import annotations

import anthropic
from anthropic.types import TextBlock


class RecommendationError(Exception):
    """Raised when LLM recommendation generation fails."""


def get_recommendation(prompt: str) -> str:
    """Call Anthropic API with the given prompt and return the response text."""
    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        block = message.content[0]
        if not isinstance(block, TextBlock):
            raise RecommendationError("Unexpected response format from LLM")
        return block.text
    except anthropic.APITimeoutError as exc:
        raise RecommendationError("Recommendation service timed out") from exc
    except anthropic.APIError as exc:
        raise RecommendationError(f"Recommendation service error: {exc}") from exc
