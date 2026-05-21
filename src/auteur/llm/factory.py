"""LLM client factory — constructs provider clients with RetryingClient wrapping.

The factory is the single point of construction for LLMClient instances.
Every client returned by build_client() is automatically wrapped in
RetryingClient for transient error resilience.
"""

from __future__ import annotations

from auteur.llm import LLMClient, LLMRequest, LLMResponse

__all__ = ["build_client"]


def build_client(
    provider: str,
    model: str | None,
    agent_type: str | None = None,
    *,
    blueprint: "StoryBlueprint | None" = None,
) -> LLMClient:
    """Construct a production client wrapped in RetryingClient.

    Args:
        provider: One of "anthropic" or "openai".
        model: Optional model override.  Falls back to provider default.
        agent_type: Optional agent role ("cartographer", "bard", "critic").
            When set, reads the corresponding model from *blueprint* if available.
        blueprint: Optional StoryBlueprint with per-agent model overrides.

    Returns:
        An LLMClient whose .complete() calls are retried on transient errors.

    Raises:
        ValueError: Unknown provider.
    """
    # Resolve per-agent model override from blueprint
    resolved_model = model
    if blueprint is not None and agent_type is not None and resolved_model is None:
        resolved_model = getattr(blueprint, f"{agent_type}_model", None)

    if provider == "anthropic":
        from auteur.llm.anthropic import AnthropicClient

        delegate: LLMClient = AnthropicClient(
            default_model=resolved_model or "claude-sonnet-4-6"
        )
    elif provider == "openai":
        from auteur.llm.openai import OpenAIClient

        delegate = OpenAIClient(default_model=resolved_model or "gpt-4o")
    else:
        raise ValueError(f"Unknown provider: {provider}")

    from auteur.llm.retrying import RetryingClient

    return RetryingClient(delegate, max_retries=3, base_delay=1.0)
