"""Provider-agnostic LLM client interface."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    system: str
    user: str
    max_tokens: int = Field(default=4096, ge=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    model: str | None = None


class LLMResponse(BaseModel):
    text: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


class RetriableError(Exception):
    """Raised by provider clients when a transient API error occurs.

    The RetryingClient catches this exception and retries with backoff.
    Providers translate their SDK's transient errors (429, 503, timeout,
    connection reset) into RetriableError.
    """


class LLMClient(Protocol):
    def complete(self, req: LLMRequest) -> LLMResponse: ...


__all__ = ["LLMClient", "LLMRequest", "LLMResponse", "RetriableError"]
