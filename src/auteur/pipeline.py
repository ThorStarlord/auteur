"""PipelineRunner — orchestrates planning, drafting, validation, iteration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

from auteur.bard import draft_chapter as bard_draft
from auteur.bible import StoryBible
from auteur.blueprint import PlanningCall, StoryBlueprint
from auteur.cartographer import render_cartographer_prompt
from auteur.critic import ValidationReport, run_critics
from auteur.llm import LLMClient, LLMRequest


CARTOGRAPHER_TEMPERATURE = 0.4
CARTOGRAPHER_MAX_TOKENS = 4000


@dataclass
class PlanResult:
    call: PlanningCall
    system_prompt: str
    user_message: str


@dataclass
class DraftResult:
    chapter_index: int
    accepted: bool
    iterations: int
    final_path: Path | None
    last_validation: ValidationReport | None
    conflict_report: str | None
    total_input_tokens: int
    total_output_tokens: int


class PipelineRunner:
    def __init__(self, blueprint: StoryBlueprint, bible: StoryBible | None = None):
        self.blueprint = blueprint
        self.bible = bible

    def plan_chapter(self, chapter_index: int) -> PlanResult:
        call = PlanningCall.for_chapter(self.blueprint, chapter_index)
        system, user = render_cartographer_prompt(call)
        return PlanResult(call=call, system_prompt=system, user_message=user)

    def draft_chapter(
        self,
        chapter_index: int,
        *,
        llm: LLMClient,
        project: Any,
        max_iterations: int = 3,
        on_iteration: Callable[[int, ValidationReport], None] | None = None,
    ) -> DraftResult:
        if self.bible is None:
            raise ValueError("PipelineRunner needs a StoryBible to draft chapters.")
        bible = self.bible

        plan = self.plan_chapter(chapter_index)
        cart_resp = llm.complete(LLMRequest(
            system=plan.system_prompt,
            user=plan.user_message,
            temperature=CARTOGRAPHER_TEMPERATURE,
            max_tokens=CARTOGRAPHER_MAX_TOKENS,
        ))
        outline = _parse_outline_yaml(cart_resp.text)
        project.write_outline(chapter_index, outline)
        total_in = cart_resp.input_tokens
        total_out = cart_resp.output_tokens

        if outline.get("conflict_report"):
            return DraftResult(
                chapter_index=chapter_index,
                accepted=False,
                iterations=0,
                final_path=None,
                last_validation=None,
                conflict_report=outline["conflict_report"],
                total_input_tokens=total_in,
                total_output_tokens=total_out,
            )

        prior_draft: str | None = None
        prior_findings: list[Any] | None = None
        last_report: ValidationReport | None = None

        for i in range(1, max_iterations + 1):
            prose = bard_draft(
                outline=outline,
                bible=bible,
                blueprint=self.blueprint,
                chapter_index=chapter_index,
                llm=llm,
                prior_draft=prior_draft,
                findings=prior_findings,
            )
            project.write_draft(chapter_index, i, prose)

            report = run_critics(
                draft=prose,
                outline=outline,
                blueprint=self.blueprint,
                bible=bible,
                chapter_index=chapter_index,
                iteration=i,
                llm=llm,
            )
            project.write_validation(chapter_index, i, report)
            last_report = report

            if on_iteration is not None:
                on_iteration(i, report)

            if report.passed:
                final_path = project.write_final(chapter_index, prose)
                bible.record_event(
                    chapter_index=chapter_index,
                    summary=outline.get("chapter_summary", ""),
                    deltas={"draft_iterations": i},
                )
                tension_score = outline.get("estimated_chapter_tension")
                if isinstance(tension_score, int):
                    bible.record_tension(chapter_index, tension_score)
                bible.save()
                return DraftResult(
                    chapter_index=chapter_index,
                    accepted=True,
                    iterations=i,
                    final_path=final_path,
                    last_validation=report,
                    conflict_report=None,
                    total_input_tokens=total_in,
                    total_output_tokens=total_out,
                )

            prior_draft = prose
            prior_findings = report.findings

        return DraftResult(
            chapter_index=chapter_index,
            accepted=False,
            iterations=max_iterations,
            final_path=None,
            last_validation=last_report,
            conflict_report=None,
            total_input_tokens=total_in,
            total_output_tokens=total_out,
        )


def _parse_outline_yaml(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        first_nl = stripped.find("\n")
        last_fence = stripped.rfind("```")
        if first_nl != -1 and last_fence > first_nl:
            stripped = stripped[first_nl + 1 : last_fence].strip()
    try:
        data = yaml.safe_load(stripped)
    except yaml.YAMLError as exc:
        raise ValueError(f"Cartographer YAML parse error: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Cartographer response is not a YAML mapping.")
    return data
