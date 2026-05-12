"""Anthropic SDK client for the LLM Protocol.

Defaults to claude-sonnet-4-6. Caches the system prompt so repeated calls
within a chapter (especially the five critics on the same draft) share
cached input.

Requires `pip install auteur[anthropic]`.
"""

from __future__ import annotations

import os

from auteur.llm import LLMRequest, LLMResponse
from auteur.llm import RetriableError


_DEFAULT_MODEL = "claude-sonnet-4-6"


class AnthropicClient:
    def __init__(self, *, api_key: str | None = None, default_model: str = _DEFAULT_MODEL):
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "AnthropicClient requires the anthropic SDK. "
                "Install with: pip install auteur[anthropic]"
            ) from exc
        self._sdk = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self._default_model = default_model

    def complete(self, req: LLMRequest) -> LLMResponse:
        model = req.model or self._default_model
        try:
            result = self._sdk.messages.create(
                model=model,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
                system=[{
                    "type": "text",
                    "text": req.system,
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=[{"role": "user", "content": req.user}],
            )
        except Exception as exc:
            raise RetriableError(str(exc)) from exc
        text = "".join(block.text for block in result.content if block.type == "text")
        return LLMResponse(
            text=text,
            input_tokens=result.usage.input_tokens,
            output_tokens=result.usage.output_tokens,
        )