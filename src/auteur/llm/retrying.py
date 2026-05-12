"""RetryingClient — LLMClient wrapper with exponential backoff and jitter.

Wraps any LLMClient and retries on RetriableError.  Non-retriable exceptions
propagate immediately.  The retry policy (max_retries, base_delay) is
configurable at construction time.
"""

from __future__ import annotations

import random
import time

from auteur.llm import LLMClient, LLMRequest, LLMResponse, RetriableError


class RetryingClient:
    """LLMClient wrapper that retries on RetriableError with backoff.

    Args:
        delegate: The underlying LLMClient to wrap.
        max_retries: Maximum number of retry attempts (default 3).
            The original call plus each retry counts as one attempt.
            Total attempts = 1 + max_retries.
        base_delay: Base delay in seconds for backoff (default 1.0).
            Actual delay = random.uniform(0, min(base_delay * 2**attempt, 30.0)).
            Set to 0.0 in tests for instant retries.
    """

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
        for attempt in range(self._max_retries + 1):
            try:
                return self._delegate.complete(req)
            except RetriableError as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    raise
                delay = random.uniform(
                    0, min(self._base_delay * (2 ** attempt), 30.0)
                )
                time.sleep(delay)
        # Should not be reached — either success or the final raise above
        assert last_exc is not None
        raise last_exc
