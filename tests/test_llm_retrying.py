"""Tests for the LLM RetryingClient and provider RetriableError wrapping."""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock SDK modules before importing clients
sys.modules["anthropic"] = MagicMock()
sys.modules["openai"] = MagicMock()

from auteur.llm import LLMRequest, LLMResponse, RetriableError
from auteur.llm.fake import FakeClient
from auteur.llm.retrying import RetryingClient
from auteur.llm.anthropic import AnthropicClient
from auteur.llm.openai import OpenAIClient


# ---------------------------------------------------------------------------
# Slice 1 — RetryingClient core
# ---------------------------------------------------------------------------


def test_retries_exactly_max_retries_times_then_succeeds():
    request = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)
    success = LLMResponse(text="ok", input_tokens=5, output_tokens=5)
    delegate = FakeClient([RetriableError("fail"), RetriableError("fail2"), success])
    client = RetryingClient(delegate, max_retries=2, base_delay=0.0)
    response = client.complete(request)
    assert response.text == "ok"
    assert len(delegate.calls) == 3


def test_raises_when_retries_exhausted():
    request = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)
    delegate = FakeClient([RetriableError("persistent")] * 3)
    client = RetryingClient(delegate, max_retries=2, base_delay=0.0)
    with pytest.raises(RetriableError, match="persistent"):
        client.complete(request)
    assert len(delegate.calls) == 3


def test_passes_through_non_retriable_errors():
    request = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)
    delegate = FakeClient([ValueError("nope")])
    client = RetryingClient(delegate, max_retries=3, base_delay=0.0)
    with pytest.raises(ValueError, match="nope"):
        client.complete(request)
    assert len(delegate.calls) == 1


# ---------------------------------------------------------------------------
# Slice 2 — Provider RetriableError wrapping
# ---------------------------------------------------------------------------


def test_anthropic_wraps_sdk_error_as_retriable():
    with patch("anthropic.Anthropic") as mock_cls:
        instance = mock_cls.return_value
        instance.messages.create.side_effect = Exception("429 rate limit")
        client = AnthropicClient(api_key="test")
        req = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)
        with pytest.raises(RetriableError, match="429"):
            client.complete(req)


def test_anthropic_wraps_timeout_as_retriable():
    with patch("anthropic.Anthropic") as mock_cls:
        instance = mock_cls.return_value
        instance.messages.create.side_effect = Exception("connection timeout")
        client = AnthropicClient(api_key="test")
        req = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)
        with pytest.raises(RetriableError, match="timeout"):
            client.complete(req)


def test_openai_wraps_sdk_error_as_retriable():
    with patch("openai.OpenAI") as mock_cls:
        instance = mock_cls.return_value
        instance.chat.completions.create.side_effect = Exception("429 rate limit")
        client = OpenAIClient(api_key="test")
        req = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)
        with pytest.raises(RetriableError, match="429"):
            client.complete(req)


def test_openai_wraps_timeout_as_retriable():
    with patch("openai.OpenAI") as mock_cls:
        instance = mock_cls.return_value
        instance.chat.completions.create.side_effect = Exception("connection timeout")
        client = OpenAIClient(api_key="test")
        req = LLMRequest(system="", user="", max_tokens=10, temperature=0.5)
        with pytest.raises(RetriableError, match="timeout"):
            client.complete(req)
