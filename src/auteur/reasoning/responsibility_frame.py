"""Advisory review of a proposed research-to-next-responsibility decision.

This module checks the *declared* decision frame; it cannot discover every
material alternative, rank creative value, or authorize the next task.
It never reads or mutates canonical narrative state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GoverningObjective(BaseModel):
    """A source-bound objective that a next-task decision is meant to serve."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    statement: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)
    source_revision: str = Field(min_length=1)


class ResponsibilityOption(BaseModel):
    """One considered action; level is relative to the governing objective."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    option_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    level: Literal["local", "mission", "close", "author_decision"]
    objective_contribution: str | None = None
    decision_value: str | None = None


class ComparativeWarrant(BaseModel):
    """An explicit reason to prefer the selection over one competing option."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    alternative_id: str = Field(min_length=1)
    rationale: str = Field(min_length=1)


class ResponsibilityFrame(BaseModel):
    """One observable, advisory next-responsibility recommendation."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal[1] = 1
    governing_objective: GoverningObjective
    current_question: str = Field(min_length=1)
    decision_boundary: Literal["bounded_task", "mission_continuation"]
    options: tuple[ResponsibilityOption, ...] = Field(min_length=1, strict=False)
    selected_option_id: str = Field(min_length=1)
    selection_rationale: str | None = None
    comparisons: tuple[ComparativeWarrant, ...] = Field(default_factory=tuple, strict=False)

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        ids = [option.option_id for option in self.options]
        if len(ids) != len(set(ids)):
            raise ValueError("responsibility option IDs must be unique")
        if self.selected_option_id not in ids:
            raise ValueError("selected responsibility option is not in the frame")
        compared = [comparison.alternative_id for comparison in self.comparisons]
        if len(compared) != len(set(compared)):
            raise ValueError("comparative warrants must name distinct alternatives")
        if self.selected_option_id in compared:
            raise ValueError("selection cannot be compared with itself")
        if not set(compared).issubset(ids):
            raise ValueError("comparative warrant refers to an unknown alternative")
        return self


FindingCode = Literal[
    "mission_alternative_unrepresented",
    "mission_alternative_uncompared",
    "selected_goal_link_unstated",
    "selected_decision_value_unstated",
    "selection_rationale_unstated",
]


class FrameFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    code: FindingCode
    explanation: str


class ResponsibilityFrameReview(BaseModel):
    """Observable frame completeness, never a correctness or authority verdict."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    review_kind: Literal["advisory_responsibility_frame"] = "advisory_responsibility_frame"
    record_status: Literal["bounded_task_not_reviewed", "no_declared_gaps", "decision_warrant_gaps"]
    selected_option_id: str
    governing_source_ref: str
    governing_source_revision: str
    findings: tuple[FrameFinding, ...]
    mission_reentry_question: str | None = None
    authority: Literal["derived_not_authorizing"] = "derived_not_authorizing"


def review_responsibility_frame(frame: ResponsibilityFrame) -> ResponsibilityFrameReview:
    """Expose omissions at a mission-continuation handoff, not choose a winner.

    A bounded local task need not repeatedly compare itself with the mission.
    When its *recommendation becomes the next mission task*, local and mission
    alternatives should be compared if a material mission alternative exists.
    These checks depend on supplied labels and cannot establish semantic truth.
    """
    selected = next(option for option in frame.options if option.option_id == frame.selected_option_id)
    findings: list[FrameFinding] = []
    question = None

    def add(code: FindingCode, explanation: str) -> None:
        findings.append(FrameFinding(code=code, explanation=explanation))

    if frame.decision_boundary == "mission_continuation":
        if not frame.selection_rationale or not frame.selection_rationale.strip():
            add("selection_rationale_unstated", "The proposed next mission responsibility has no stated rationale.")
        if not selected.objective_contribution or not selected.objective_contribution.strip():
            add("selected_goal_link_unstated", "The selection has no stated contribution to the governing objective.")
        if not selected.decision_value or not selected.decision_value.strip():
            add("selected_decision_value_unstated", "The selection does not say what outcome would change a mission-level judgment.")
        if selected.level == "local":
            mission_ids = {option.option_id for option in frame.options if option.level == "mission"}
            if not mission_ids:
                add(
                    "mission_alternative_unrepresented",
                    "The frame promotes local work as the next mission task without considering a mission-level alternative.",
                )
                question = (
                    "Would returning directly to the governing objective ("
                    + frame.governing_objective.statement
                    + ") offer more decision value than the selected local work?"
                )
            elif not mission_ids.intersection(comparison.alternative_id for comparison in frame.comparisons):
                add(
                    "mission_alternative_uncompared",
                    "A mission-level alternative is represented but no explicit comparison with it is recorded.",
                )

    return ResponsibilityFrameReview(
        record_status=(
            "bounded_task_not_reviewed" if frame.decision_boundary == "bounded_task"
            else "decision_warrant_gaps" if findings
            else "no_declared_gaps"
        ),
        selected_option_id=selected.option_id,
        governing_source_ref=frame.governing_objective.source_ref,
        governing_source_revision=frame.governing_objective.source_revision,
        findings=tuple(findings),
        mission_reentry_question=question,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Advisory review of a next-responsibility decision frame")
    parser.add_argument("frame", type=Path, help="JSON file containing a responsibility frame")
    args = parser.parse_args(argv)
    frame = ResponsibilityFrame.model_validate_json(args.frame.read_text(encoding="utf-8"))
    review = review_responsibility_frame(frame)
    print(json.dumps(review.model_dump(mode="json"), indent=2, ensure_ascii=False))
    # Findings are advisory; a nonzero exit would turn the helper into an implicit permission gate.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
