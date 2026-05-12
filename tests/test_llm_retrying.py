"""Tests for the LLM RetryingClient — exponential backoff with jitter."""

import pytest

from auteur.llm import LLMRequest, LLMResponse, RetriableError
from auteur.llm.fake import FakeClient
from auteur.llm.retrying import RetryingClient


def test_retries_exactly_max_retries_times_then_succeeds():
    """A RetryingClient should retry on RetriableError up to max_retries
    times, and if the delegate finally succeeds, return the response."""
    request = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)
    success = LLMResponse(text="ok", input_tokens=5, output_tokens=5)

    # Fail twice, succeed on third attempt (max_retries=2 → 2 retries + original)
    delegate = FakeClient([
        RetriableError("first failure"),
        RetriableError("second failure"),
        success,
    ])
    client = RetryingClient(delegate, max_retries=2, base_delay=0.0)

    response = client.complete(request)

    assert response.text == "ok"
    assert len(delegate.calls) == 3  # 2 failures + 1 success


def test_raises_when_retries_exhausted():
    """If the delegate raises RetriableError on every call up to
    max_retries+1, the RetryingClient should raise RetriableError."""
    request = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)

    delegate = FakeClient([
        RetriableError("persistent error"),
        RetriableError("persistent error"),
        RetriableError("persistent error"),
    ])
    client = RetryingClient(delegate, max_retries=2, base_delay=0.0)

    with pytest.raises(RetriableError, match="persistent"):
        client.complete(request)

    assert len(delegate.calls) == 3  # original + 2 retries


def test_passes_through_non_retriable_errors():
    """Non-RetriableError exceptions should propagate immediately
    without any retry."""
    request = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)

    delegate = FakeClient([
        ValueError("non-transient error"),
    ])
    client = RetryingClient(delegate, max_retries=3, base_delay=0.0)

    with pytest.raises(ValueError, match="non-transient"):
        client.complete(request)

    assert len(delegate.calls) == 1  # no retries
