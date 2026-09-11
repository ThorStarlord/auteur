"""Anthropic SDK client for the normalized Auteur LLM protocol."""

from __future__ import annotations

import os

from auteur.llm import (
    LLMErrorCode,
    LLMProviderError,
    LLMRequest,
    LLMResponse,
    normalize_provider_exception,
)


_DEFAULT_MODEL = "claude-sonnet-4-6"


class AnthropicClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str = _DEFAULT_MODEL,
    ) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "AnthropicClient requires the anthropic SDK. "
                "Install with: pip install auteur[anthropic]"
            ) from exc
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise LLMProviderError(
                "ANTHROPIC_API_KEY is required for the Anthropic provider",
                code=LLMErrorCode.AUTH_MISSING,
                provider="anthropic",
            )
        self._sdk = Anthropic(api_key=resolved_key)
        self._default_model = default_model

    def complete(self, req: LLMRequest) -> LLMResponse:
        model = req.model or self._default_model
        try:
            result = self._sdk.messages.create(
                model=model,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
                system=[
                    {
                        "type": "text",
                        "text": req.system,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": req.user}],
            )
        except Exception as exc:
            raise normalize_provider_exception("anthropic", exc) from exc
        try:
            text = "".join(
                block.text for block in result.content if block.type == "text"
            )
            return LLMResponse(
                text=text,
                input_tokens=result.usage.input_tokens,
                output_tokens=result.usage.output_tokens,
            )
        except Exception as exc:
            raise LLMProviderError(
                f"Malformed Anthropic response: {exc}",
                code=LLMErrorCode.MALFORMED_RESPONSE,
                provider="anthropic",
            ) from exc
