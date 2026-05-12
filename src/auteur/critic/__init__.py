"""Critic system — validation findings and aggregation.

The five built-in critics live in their own modules. run_critics fans
them out in parallel and aggregates into one ValidationReport.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal

from pydantic import BaseModel

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.llm import LLMClient


class CriticFinding(BaseModel):
    critic: Literal["contract", "arc", "tension", "slop", "theme"]
    severity: Literal["error", "warning"]
    rule: str
    evidence: str
    requested_change: str


class ValidationReport(BaseModel):
    chapter_index: int
    iteration: int
    findings: list[CriticFinding]
    passed: bool


def run_critics(
    *,
    draft: str,
    outline: dict[str, Any],
    blueprint: StoryBlueprint,
    bible: StoryBible,
    chapter_index: int,
    iteration: int,
    llm: LLMClient,
) -> ValidationReport:
    from auteur.critic.base import run_critic
    from auteur.critic import contract as contract_mod
    from auteur.critic import arc as arc_mod
    from auteur.critic import tension as tension_mod
    from auteur.critic import slop as slop_mod
    from auteur.critic import theme as theme_mod

    renderers = [
        (contract_mod.render, "contract", contract_mod.TEMPERATURE, contract_mod.MAX_TOKENS),
        (arc_mod.render, "arc", arc_mod.TEMPERATURE, arc_mod.MAX_TOKENS),
        (tension_mod.render, "tension", tension_mod.TEMPERATURE, tension_mod.MAX_TOKENS),
        (slop_mod.render, "slop", slop_mod.TEMPERATURE, slop_mod.MAX_TOKENS),
        (theme_mod.render, "theme", theme_mod.TEMPERATURE, theme_mod.MAX_TOKENS),
    ]

    kwargs = dict(
        draft=draft,
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=chapter_index,
    )

    findings: list[CriticFinding] = []
    with ThreadPoolExecutor(max_workers=len(renderers)) as ex:
        def submit_one(render_fn, name, temp, tokens):
            return ex.submit(
                run_critic, render_fn,
                llm=llm, critic_name=name, temperature=temp, max_tokens=tokens,
                **kwargs,
            )
        futures = [submit_one(*r) for r in renderers]
        for f in futures:
            findings.extend(f.result())

    return ValidationReport(
        chapter_index=chapter_index,
        iteration=iteration,
        findings=findings,
        passed=not any(f.severity == "error" for f in findings),
    )


__all__ = ["CriticFinding", "ValidationReport", "run_critics"]
