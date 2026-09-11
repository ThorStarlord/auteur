"""V1 provider-independent LLM failure contract tests."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

sys.modules.setdefault("anthropic", MagicMock())
sys.modules.setdefault("openai", MagicMock())

from auteur.llm import (  # noqa: E402
    LLMErrorCode,
    LLMProviderError,
    LLMRequest,
    RetriableError,
    RetryExhaustedError,
    StructuredOutputError,
    normalize_provider_exception,
)
from auteur.llm.anthropic import AnthropicClient  # noqa: E402
from auteur.llm.fake import FakeClient  # noqa: E402
from auteur.llm.openai import OpenAIClient  # noqa: E402
from auteur.llm.retrying import RetryingClient  # noqa: E402
from auteur.story_design_packs.proposal_bridge import _parse_json_object  # noqa: E402


@pytest.mark.parametrize(
    ("message", "status", "code", "retriable"),
    [
        ("invalid API key", 401, LLMErrorCode.AUTH_INVALID, False),
        ("429 rate limit", 429, LLMErrorCode.RATE_LIMITED, True),
        ("request timeout", None, LLMErrorCode.TIMEOUT, True),
        ("connection reset", None, LLMErrorCode.CONNECTION_FAILURE, True),
        ("service unavailable", 503, LLMErrorCode.PROVIDER_5XX, True),
    ],
)
def test_normalize_provider_exception(message, status, code, retriable):
    exc = Exception(message)
    if status is not None:
        exc.status_code = status  # type: ignore[attr-defined]
    normalized = normalize_provider_exception("test", exc)
    assert normalized.code is code
    assert normalized.retriable is retriable
    assert normalized.provider == "test"


def test_retry_exhaustion_has_stable_code_and_preserves_compatibility():
    req = LLMRequest(system="", user="test", max_tokens=10)
    delegate = FakeClient(
        [
            RetriableError("limited", code=LLMErrorCode.RATE_LIMITED),
            RetriableError("limited again", code=LLMErrorCode.RATE_LIMITED),
        ]
    )
    client = RetryingClient(delegate, max_retries=1, base_delay=0.0)
    with pytest.raises(RetryExhaustedError) as captured:
        client.complete(req)
    assert isinstance(captured.value, RetriableError)
    assert captured.value.code is LLMErrorCode.RETRY_EXHAUSTED
    assert captured.value.attempts == 2
    assert captured.value.cause.code is LLMErrorCode.RATE_LIMITED


def test_structured_output_failure_has_stable_code_and_valueerror_compatibility():
    with pytest.raises(StructuredOutputError) as captured:
        _parse_json_object("not json")
    assert isinstance(captured.value, ValueError)
    assert isinstance(captured.value, LLMProviderError)
    assert captured.value.code is LLMErrorCode.STRUCTURED_OUTPUT_INVALID
    assert captured.value.retriable is False


def test_anthropic_missing_credentials_fail_before_sdk_call(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("anthropic.Anthropic") as sdk:
        with pytest.raises(LLMProviderError) as captured:
            AnthropicClient()
    assert captured.value.code is LLMErrorCode.AUTH_MISSING
    sdk.assert_not_called()


def test_openai_missing_credentials_fail_before_sdk_call(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with patch("openai.OpenAI") as sdk:
        with pytest.raises(LLMProviderError) as captured:
            OpenAIClient()
    assert captured.value.code is LLMErrorCode.AUTH_MISSING
    sdk.assert_not_called()


def test_anthropic_malformed_response_is_non_retriable():
    with patch("anthropic.Anthropic") as sdk:
        sdk.return_value.messages.create.return_value = SimpleNamespace(content=[])
        client = AnthropicClient(api_key="test")
        with pytest.raises(LLMProviderError) as captured:
            client.complete(LLMRequest(system="", user="test"))
    assert captured.value.code is LLMErrorCode.MALFORMED_RESPONSE
    assert captured.value.retriable is False


def test_openai_malformed_response_is_non_retriable():
    with patch("openai.OpenAI") as sdk:
        sdk.return_value.chat.completions.create.return_value = SimpleNamespace(
            choices=[]
        )
        client = OpenAIClient(api_key="test")
        with pytest.raises(LLMProviderError) as captured:
            client.complete(LLMRequest(system="", user="test"))
    assert captured.value.code is LLMErrorCode.MALFORMED_RESPONSE
    assert captured.value.retriable is False
