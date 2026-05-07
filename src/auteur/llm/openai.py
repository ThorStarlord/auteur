"""OpenAI SDK client for the LLM Protocol.

Defaults to gpt-4o.

Requires `pip install auteur[openai]`.
"""

from __future__ import annotations

import os

from auteur.llm import LLMRequest, LLMResponse


_DEFAULT_MODEL = "gpt-4o"


class OpenAIClient:
    def __init__(self, *, api_key: str | None = None, default_model: str = _DEFAULT_MODEL):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "OpenAIClient requires the openai SDK. "
                "Install with: pip install auteur[openai]"
            ) from exc
        self._sdk = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self._default_model = default_model

    def complete(self, req: LLMRequest) -> LLMResponse:
        model = req.model or self._default_model
        result = self._sdk.chat.completions.create(
            model=model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            messages=[
                {"role": "system", "content": req.system},
                {"role": "user", "content": req.user},
            ],
        )
        choice = result.choices[0].message
        return LLMResponse(
            text=choice.content or "",
            input_tokens=result.usage.prompt_tokens,
            output_tokens=result.usage.completion_tokens,
        )
