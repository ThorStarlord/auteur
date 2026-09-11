"""RetryingClient — LLMClient wrapper with exponential backoff and jitter."""

from __future__ import annotations

import random
import time

from auteur.llm import (
    LLMClient,
    LLMRequest,
    LLMResponse,
    RetriableError,
    RetryExhaustedError,
)


class RetryingClient:
    """Retry transient normalized failures and expose retry exhaustion explicitly."""

    def __init__(
        self,
        delegate: LLMClient,
        *,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> None:
        self._delegate = delegate
        self._max_retries = max_retries
        self._base_delay = base_delay

    def complete(self, req: LLMRequest) -> LLMResponse:
        last_exc: RetriableError | None = None
        attempts = self._max_retries + 1
        for attempt in range(attempts):
            try:
                return self._delegate.complete(req)
            except RetriableError as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    raise RetryExhaustedError(exc, attempts) from exc
                delay = random.uniform(
                    0, min(self._base_delay * (2**attempt), 30.0)
                )
                time.sleep(delay)
        assert last_exc is not None
        raise RetryExhaustedError(last_exc, attempts)
