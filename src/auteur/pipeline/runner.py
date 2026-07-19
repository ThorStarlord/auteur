"""PipelineRunner — orchestrates planning, drafting, validation, iteration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Callable

import yaml

from auteur.bard import draft_chapter as bard_draft
from auteur.bible import StoryBible
from auteur.cartographer import render_cartographer_prompt
from auteur.cartographer_models import PlanningCall
from auteur.blueprint import StoryBlueprint
from auteur.critic import CriticFinding, ValidationReport
from auteur.critic.repair_writer import write_critic_proposals
from auteur.llm import LLMClient, LLMRequest, LLMResponse
from auteur.llm.counting import _CountingClient
from auteur.pipeline.extraction import extract_character_state_changes
from auteur.pipeline.models import DraftResult, PlanResult
from auteur.pipeline.parsing import _parse_outline_yaml
from auteur.reasoning.draft_critics import register_draft_critics
from auteur.reasoning.draft_review import persist_reasoning_run
from auteur.reasoning.runtime import CriticRegistry, ReasoningRuntime, RuntimeRequest


CARTOGRAPHER_TEMPERATURE = 0.4
CARTOGRAPHER_MAX_TOKENS = 4000

# Lazy-global ReasoningRuntime, initialised on first use.
_REASONING_RUNTIME: ReasoningRuntime | None = None
_REASONING_REGISTRY: CriticRegistry | None = None


def _get_reasoning_runtime() -> ReasoningRuntime:
    global _REASONING_RUNTIME, _REASONING_REGISTRY
    if _REASONING_RUNTIME is None:
        _REASONING_REGISTRY = CriticRegistry()
        register_draft_critics(_REASONING_REGISTRY)
        _REASONING_RUNTIME = ReasoningRuntime(_REASONING_REGISTRY, report_dir=Path())
    return _REASONING_RUNTIME


def _run_critics_via_runtime(
    *,
    draft: str,
    outline: dict[str, Any],
    blueprint: StoryBlueprint,
    bible: StoryBible,
    chapter_index: int,
    iteration: int,
    llm: LLMClient,
) -> ValidationReport:
    """Execute the five draft critics through the ReasoningRuntime and project
    outcomes into a legacy-compatible ValidationReport."""
    import json
    from auteur.llm.counting import _CountingClient

    counted = _CountingClient(llm) if not isinstance(llm, _CountingClient) else llm

    runtime = _get_reasoning_runtime()
    req = RuntimeRequest(
        critic_ids=["draft.contract", "draft.arc", "draft.tension", "draft.slop", "draft.theme"],
        inputs={
            "draft": draft,
            "outline": outline,
            "blueprint": blueprint,
            "bible": bible,
            "chapter_index": chapter_index,
            "llm": counted,
        },
    )
    result = runtime.run(req)

    # Convert ExecutionOutcomes into CriticFindings
    findings: list[CriticFinding] = []
    for oc in result.outcomes:
        if oc.status == "success" and oc.report_id:
            report_path = runtime.report_dir / f"{oc.report_id}.json"
            if report_path.exists():
                report = json.loads(report_path.read_text(encoding="utf-8"))
                for f in report.get("findings", []):
                    # Strip 'draft.' prefix to match CriticFinding Literal types
                    raw_critic = f.get("critic", oc.critic_id)
                    critic_name = raw_critic.replace("draft.", "")
                    findings.append(CriticFinding(
                        critic=critic_name,
                        severity=f.get("severity", "error"),
                        rule=f.get("rule", ""),
                        evidence=f.get("evidence", ""),
                        requested_change=f.get("requested_change", ""),
                    ))
        elif oc.status == "failed":
            critic_name = oc.critic_id.replace("draft.", "")
            findings.append(CriticFinding(
                critic=critic_name, severity="error",
                rule="critic.execution_failure",
                evidence=oc.error or "critic execution failed",
                requested_change=f"Resolve execution error in {critic_name} critic",
            ))
        elif oc.status == "stale":
            critic_name = oc.critic_id.replace("draft.", "")
            findings.append(CriticFinding(
                critic=critic_name, severity="error",
                rule="critic.stale_inputs",
                evidence=oc.reason or "stale inputs",
                requested_change=f"Re-run with fresh inputs for {critic_name}",
            ))

    return ValidationReport(
        chapter_index=chapter_index,
        iteration=iteration,
        findings=findings,
        passed=not any(f.severity == "error" for f in findings),
    )


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
        initial_outline: dict[str, Any] | None = None,
        start_iteration: int = 1,
        prior_draft: str | None = None,
        prior_findings: list[Any] | None = None,
    ) -> DraftResult:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1.")
        if start_iteration < 1:
            raise ValueError("start_iteration must be at least 1.")
        if self.bible is None:
            raise ValueError("PipelineRunner needs a StoryBible to draft chapters.")
        bible = self.bible
        counted_llm = _CountingClient(llm)

        if initial_outline is None:
            plan = self.plan_chapter(chapter_index)
            cart_resp = counted_llm.complete(LLMRequest(
                system=plan.system_prompt,
                user=plan.user_message,
                temperature=CARTOGRAPHER_TEMPERATURE,
                max_tokens=CARTOGRAPHER_MAX_TOKENS,
            ))
            outline = _parse_outline_yaml(cart_resp.text)
            project.write_outline(chapter_index, outline)
        else:
            outline = initial_outline

        if outline.get("conflict_report"):
            return DraftResult(
                chapter_index=chapter_index,
                accepted=False,
                iterations=0,
                final_path=None,
                last_validation=None,
                conflict_report=outline["conflict_report"],
                total_input_tokens=counted_llm.input_tokens,
                total_output_tokens=counted_llm.output_tokens,
            )

        last_report: ValidationReport | None = None

        for i in range(start_iteration, start_iteration + max_iterations):
            prose = bard_draft(
                outline=outline,
                bible=bible,
                blueprint=self.blueprint,
                chapter_index=chapter_index,
                llm=counted_llm,
                prior_draft=prior_draft,
                findings=prior_findings,
            )
            project.write_draft(chapter_index, i, prose)

            # Execute critics through ReasoningRuntime instead of direct run_critics
            report = _run_critics_via_runtime(
                draft=prose,
                outline=outline,
                blueprint=self.blueprint,
                bible=bible,
                chapter_index=chapter_index,
                iteration=i,
                llm=counted_llm,
            )
            project.write_validation(chapter_index, i, report)
            last_report = report

            if on_iteration is not None:
                on_iteration(i, report)

            if report.passed:
                final_path = project.write_final(chapter_index, prose)
                state_changes = extract_character_state_changes(outline)
                bible.record_event(
                    chapter_index=chapter_index,
                    summary=outline.get("chapter_summary", ""),
                    deltas={
                        "draft_iterations": i,
                        "character_state_changes": state_changes,
                    },
                )
                for change in state_changes:
                    bible.upsert_character(
                        change["character"],
                        **{change["field"]: change["after"]},
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
                    total_input_tokens=counted_llm.input_tokens,
                    total_output_tokens=counted_llm.output_tokens,
                )

            prior_draft = prose
            prior_findings = report.findings

        # Exhausted — write critic proposals for error findings
        if last_report is not None:
            proposals_dir = project.structure_proposals_dir()
            proposal_paths = write_critic_proposals(
                proposals_dir, last_report, chapter_index,
            )
        else:
            proposal_paths = []

        return DraftResult(
            critic_proposal_paths=proposal_paths,
            chapter_index=chapter_index,
            accepted=False,
            iterations=max_iterations,
            final_path=None,
            last_validation=last_report,
            conflict_report=None,
            total_input_tokens=counted_llm.input_tokens,
            total_output_tokens=counted_llm.output_tokens,
        )
