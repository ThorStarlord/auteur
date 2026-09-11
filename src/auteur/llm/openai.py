"""OpenAI SDK client for the normalized Auteur LLM protocol."""

from __future__ import annotations

import os

from auteur.llm import (
    LLMErrorCode,
    LLMProviderError,
    LLMRequest,
    LLMResponse,
    normalize_provider_exception,
)


_DEFAULT_MODEL = "gpt-4o"


class OpenAIClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str = _DEFAULT_MODEL,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "OpenAIClient requires the openai SDK. "
                "Install with: pip install auteur[openai]"
            ) from exc
        resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved_key:
            raise LLMProviderError(
                "OPENAI_API_KEY is required for the OpenAI provider",
                code=LLMErrorCode.AUTH_MISSING,
                provider="openai",
            )
        self._sdk = OpenAI(api_key=resolved_key)
        self._default_model = default_model

    def complete(self, req: LLMRequest) -> LLMResponse:
        model = req.model or self._default_model
        try:
            result = self._sdk.chat.completions.create(
                model=model,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
                messages=[
                    {"role": "system", "content": req.system},
                    {"role": "user", "content": req.user},
                ],
            )
        except Exception as exc:
            raise normalize_provider_exception("openai", exc) from exc
        try:
            choice = result.choices[0].message
            usage = result.usage
            return LLMResponse(
                text=choice.content or "",
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
            )
        except Exception as exc:
            raise LLMProviderError(
                f"Malformed OpenAI response: {exc}",
                code=LLMErrorCode.MALFORMED_RESPONSE,
                provider="openai",
            ) from exc
