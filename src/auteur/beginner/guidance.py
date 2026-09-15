"""Deterministic, non-canonical guidance for the Beginner Mystery adapter."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import DecisionStage, LifecycleStatus, SessionEnvelope
from .mystery_adapter import QualificationStage, mystery_qualification_inventory


class BeginnerGuidance(BaseModel):
    """A contextual teaching projection; it never changes canonical story state."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    card_id: str = Field(min_length=1)
    stage: QualificationStage
    question: str = Field(min_length=1)
    why_this_matters: str = Field(min_length=1)
    narrative_principle: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    context_summary: str = Field(min_length=1)
    alternatives: tuple[str, ...] = Field(min_length=1)
    tradeoffs: tuple[str, ...] = Field(min_length=1)
    downstream_consequences: tuple[str, ...] = Field(min_length=1)
    warnings_or_tensions: tuple[str, ...] = Field(min_length=1)
    evidence_references: tuple[str, ...] = Field(min_length=1)
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            if "stage" in data and type(data["stage"]) is not QualificationStage:
                raise ValueError("stage must be a QualificationStage")
            for field_name in (
                "alternatives",
                "tradeoffs",
                "downstream_consequences",
                "warnings_or_tensions",
                "evidence_references",
            ):
                if field_name in data and type(data[field_name]) is not tuple:
                    raise ValueError(f"{field_name} must be a tuple")
        return data


def _completed_stages(session: SessionEnvelope) -> tuple[str, ...]:
    return tuple(
        stage.value
        for stage, status in session.stages.items()
        if status.lifecycle is LifecycleStatus.COMPLETE
    )


def _progress_context(session: SessionEnvelope) -> str:
    completed = _completed_stages(session)
    if not completed:
        return "No qualification stage is marked complete yet."
    return f"Completed stages currently recorded: {', '.join(completed)}."


def _context_summary(card_stage: QualificationStage, session: SessionEnvelope) -> str:
    stage_map = {
        QualificationStage.DISCOVER: DecisionStage.DISCOVER,
        QualificationStage.STORY_IDENTITY: DecisionStage.STORY_IDENTITY,
        QualificationStage.STRUCTURE: DecisionStage.STORY_STRUCTURE,
    }
    parts = [_progress_context(session)]
    status = session.stages[stage_map[card_stage]]
    if status.working_decision is not None:
        parts.append(
            "Current working decision: "
            f"{status.working_decision.question} "
            f"Options: {', '.join(status.working_decision.options)}."
        )
    if session.accepted_milestones:
        parts.append(
            "Accepted milestones: "
            + ", ".join(milestone.milestone_id for milestone in session.accepted_milestones)
            + "."
        )
    return " ".join(parts)


def _consequences(stage: QualificationStage) -> tuple[str, ...]:
    if stage is QualificationStage.DISCOVER:
        return (
            "The chosen question controls which clues and suspects deserve attention.",
            "The investigation's scope sets the amount of evidence the story must support.",
        )
    if stage is QualificationStage.STORY_IDENTITY:
        return (
            "The investigator's want and stakes shape which leads become meaningful.",
            "Resistance and change determine how discovery affects the person pursuing it.",
        )
    return (
        "The reveal must pay off the evidence trail rather than arrive as an unrelated answer.",
        "The selected structure changes how much reasoning and reinterpretation the reader performs.",
    )


def guidance_for(card_id: str, session: SessionEnvelope) -> BeginnerGuidance:
    """Compose one deterministic guidance card from a current session snapshot."""
    if session.guidance_genre != "mystery":
        raise ValueError(f"unsupported guidance genre: {session.guidance_genre}")
    card = mystery_qualification_inventory().card(card_id)
    alternatives = tuple(option for option in card.options if option != card.recommendation)
    premise = session.premise
    context_summary = _context_summary(card.stage, session)
    rationale = (
        f"For the current premise, {premise!r}, start with {card.recommendation.lower()}. "
        f"{context_summary} This keeps the decision connected to the existing story state."
    )
    return BeginnerGuidance(
        card_id=card.card_id,
        stage=card.stage,
        question=card.question,
        why_this_matters=(
            f"This decision determines how the story's mystery operates for {premise!r}."
        ),
        narrative_principle=card.narrative_principle,
        recommendation=card.recommendation,
        rationale=rationale,
        context_summary=context_summary,
        alternatives=alternatives,
        tradeoffs=card.warnings_or_tensions,
        downstream_consequences=_consequences(card.stage),
        warnings_or_tensions=card.warnings_or_tensions,
        evidence_references=card.evidence_references,
    )


get_guidance = guidance_for
