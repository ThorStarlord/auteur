"""Provider-agnostic LLM client interface and stable failure vocabulary."""

from __future__ import annotations

from enum import Enum
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


class LLMErrorCode(str, Enum):
    """Stable provider-independent operational failure categories."""

    AUTH_MISSING = "auth_missing"
    AUTH_INVALID = "auth_invalid"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    CONNECTION_FAILURE = "connection_failure"
    PROVIDER_5XX = "provider_5xx"
    MALFORMED_RESPONSE = "malformed_response"
    STRUCTURED_OUTPUT_INVALID = "structured_output_invalid"
    RETRY_EXHAUSTED = "retry_exhausted"
    USER_INTERRUPTED = "user_interrupted"
    PROVIDER_ERROR = "provider_error"


class LLMProviderError(Exception):
    """A normalized provider failure that callers can handle without SDK types."""

    def __init__(
        self,
        message: str,
        *,
        code: LLMErrorCode = LLMErrorCode.PROVIDER_ERROR,
        provider: str | None = None,
        retriable: bool = False,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.provider = provider
        self.retriable = retriable
        self.status_code = status_code


class RetriableError(LLMProviderError):
    """Normalized transient provider error caught by :class:`RetryingClient`."""

    def __init__(
        self,
        message: str,
        *,
        code: LLMErrorCode = LLMErrorCode.PROVIDER_ERROR,
        provider: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(
            message,
            code=code,
            provider=provider,
            retriable=True,
            status_code=status_code,
        )


class RetryExhaustedError(RetriableError):
    """Raised after the configured transient-error retry budget is exhausted."""

    def __init__(self, cause: RetriableError, attempts: int) -> None:
        super().__init__(
            f"Retry budget exhausted after {attempts} attempts: {cause}",
            code=LLMErrorCode.RETRY_EXHAUSTED,
            provider=cause.provider,
            status_code=cause.status_code,
        )
        self.cause = cause
        self.attempts = attempts


def normalize_provider_exception(provider: str, exc: Exception) -> LLMProviderError:
    """Classify an SDK exception without depending on optional SDK exception classes."""

    if isinstance(exc, LLMProviderError):
        return exc
    status = getattr(exc, "status_code", None)
    try:
        status_code = int(status) if status is not None else None
    except (TypeError, ValueError):
        status_code = None
    text = str(exc)
    lowered = f"{exc.__class__.__name__} {text}".lower()

    if status_code in {401, 403} or any(
        marker in lowered
        for marker in ("invalid api key", "authentication", "unauthorized", "forbidden")
    ):
        return LLMProviderError(
            text,
            code=LLMErrorCode.AUTH_INVALID,
            provider=provider,
            status_code=status_code,
        )
    if status_code == 429 or "rate limit" in lowered or "ratelimit" in lowered:
        return RetriableError(
            text,
            code=LLMErrorCode.RATE_LIMITED,
            provider=provider,
            status_code=status_code,
        )
    if "timeout" in lowered or "timed out" in lowered:
        return RetriableError(
            text,
            code=LLMErrorCode.TIMEOUT,
            provider=provider,
            status_code=status_code,
        )
    if any(marker in lowered for marker in ("connection", "connecterror", "network")):
        return RetriableError(
            text,
            code=LLMErrorCode.CONNECTION_FAILURE,
            provider=provider,
            status_code=status_code,
        )
    if (status_code is not None and status_code >= 500) or any(
        marker in lowered for marker in ("service unavailable", "internal server error")
    ):
        return RetriableError(
            text,
            code=LLMErrorCode.PROVIDER_5XX,
            provider=provider,
            status_code=status_code,
        )
    # Preserve the historical retry posture for unknown SDK transport failures,
    # while giving callers a stable category instead of an SDK-specific type.
    return RetriableError(text, code=LLMErrorCode.PROVIDER_ERROR, provider=provider)


class LLMClient(Protocol):
    def complete(self, req: LLMRequest) -> LLMResponse: ...


__all__ = [
    "LLMClient",
    "LLMErrorCode",
    "LLMProviderError",
    "LLMRequest",
    "LLMResponse",
    "RetriableError",
    "RetryExhaustedError",
    "normalize_provider_exception",
]
