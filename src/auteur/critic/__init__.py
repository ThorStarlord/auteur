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
    from auteur.critic import contract as contract_mod
    from auteur.critic import arc as arc_mod
    from auteur.critic import tension as tension_mod
    from auteur.critic import slop as slop_mod
    from auteur.critic import theme as theme_mod

    runners = [
        contract_mod.run,
        arc_mod.run,
        tension_mod.run,
        slop_mod.run,
        theme_mod.run,
    ]

    kwargs = dict(
        draft=draft,
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=chapter_index,
        llm=llm,
    )

    findings: list[CriticFinding] = []
    with ThreadPoolExecutor(max_workers=len(runners)) as ex:
        futures = [ex.submit(r, **kwargs) for r in runners]
        for f in futures:
            findings.extend(f.result())

    return ValidationReport(
        chapter_index=chapter_index,
        iteration=iteration,
        findings=findings,
        passed=not any(f.severity == "error" for f in findings),
    )


__all__ = ["CriticFinding", "ValidationReport", "run_critics"]
