"""Adapters that wrap the five existing LLM drafting critics for the
ReasoningRuntime. Each adapter calls the existing prompt renderer and
parser without duplicating prompt logic."""

from __future__ import annotations

from typing import Any

from auteur.critic.base import parse_findings_yaml, run_critic as _run_critic
from auteur.llm import LLMClient
from auteur.reasoning.runtime import CriticRegistry, CriticSpec


def _make_adapter(critic_name: str, render_fn: Any, temperature: float, max_tokens: int):
    """Factory: return a CriticRunner that delegates to the existing critic."""

    def adapter(**inputs: Any) -> list[dict[str, Any]]:
        llm: LLMClient = inputs["llm"]
        kwargs = {k: inputs[k] for k in ("draft", "outline", "blueprint", "bible", "chapter_index") if k in inputs}
        return _run_critic(
            render_fn,
            llm=llm,
            critic_name=critic_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    return adapter


def register_draft_critics(registry: CriticRegistry) -> None:
    """Register all five LLM-based draft critics with the Runtime registry.

    Each adapter preserves the existing prompt renderer, temperature,
    token limit, and finding-parsing behavior.

    Idempotent: re-registering the same critic+version is silently skipped.
    """
    from auteur.critic import arc as arc_mod
    from auteur.critic import contract as contract_mod
    from auteur.critic import slop as slop_mod
    from auteur.critic import tension as tension_mod
    from auteur.critic import theme as theme_mod

    INPUT_KEYS = ("draft", "outline", "blueprint", "bible", "chapter_index", "llm")

    critics = [
        ("draft.contract", contract_mod.render, contract_mod.TEMPERATURE, contract_mod.MAX_TOKENS),
        ("draft.arc", arc_mod.render, arc_mod.TEMPERATURE, arc_mod.MAX_TOKENS),
        ("draft.tension", tension_mod.render, tension_mod.TEMPERATURE, tension_mod.MAX_TOKENS),
        ("draft.slop", slop_mod.render, slop_mod.TEMPERATURE, slop_mod.MAX_TOKENS),
        ("draft.theme", theme_mod.render, theme_mod.TEMPERATURE, theme_mod.MAX_TOKENS),
    ]

    for critic_id, render_fn, temp, tokens in critics:
        adapter = _make_adapter(critic_id, render_fn, temp, tokens)
        try:
            registry.register(CriticSpec(
                critic_id=critic_id,
                version="0.1.0",
                requires=(),
                input_keys=INPUT_KEYS,
                run=adapter,
            ))
        except ValueError:
            pass  # already registered
