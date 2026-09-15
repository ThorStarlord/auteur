"""Deterministic, genre-neutral Beginner guidance and adapter routing."""

from __future__ import annotations

import json
from enum import Enum
from typing import ClassVar, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import DecisionStage, LifecycleStatus, SessionEnvelope


class QualificationStage(str, Enum):
    DISCOVER = "discover"
    STORY_IDENTITY = "story_identity"
    STRUCTURE = "structure"


class QualificationCard(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    card_id: str = Field(min_length=1)
    stage: QualificationStage
    title: str = Field(min_length=1)
    question: str = Field(min_length=1)
    source_subject: str = Field(min_length=1)
    options: tuple[str, ...] = Field(min_length=2)
    recommendation: str = Field(min_length=1)
    narrative_principle: str = Field(min_length=1)
    warnings_or_tensions: tuple[str, ...] = Field(min_length=1)
    evidence_references: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            if "stage" in data and type(data["stage"]) is not QualificationStage:
                raise ValueError("stage must be a QualificationStage")
            for name in ("options", "warnings_or_tensions", "evidence_references"):
                if name in data and type(data[name]) is not tuple:
                    raise ValueError(f"{name} must be a tuple")
        return data

    @model_validator(mode="after")
    def recommendation_is_an_option(self) -> QualificationCard:
        if self.recommendation not in self.options:
            raise ValueError("recommendation must be one of the card options")
        return self


class QualificationInventory(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    cards: tuple[QualificationCard, ...]
    _expected_counts: ClassVar[dict[QualificationStage, int]] = {
        QualificationStage.DISCOVER: 3,
        QualificationStage.STORY_IDENTITY: 4,
        QualificationStage.STRUCTURE: 3,
    }

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_cards(cls, data: object) -> object:
        if isinstance(data, dict) and "cards" in data and type(data["cards"]) is not tuple:
            raise ValueError("cards must be a tuple")
        return data

    @model_validator(mode="after")
    def validate_inventory(self) -> QualificationInventory:
        ids = [card.card_id for card in self.cards]
        if len(ids) != len(set(ids)):
            raise ValueError("qualification card IDs must be unique")
        counts = {stage: sum(card.stage is stage for card in self.cards) for stage in self._expected_counts}
        if counts != self._expected_counts:
            raise ValueError("qualification inventory has the wrong stage counts")
        return self

    @property
    def stage_counts(self) -> dict[QualificationStage, int]:
        return {stage: sum(card.stage is stage for card in self.cards) for stage in self._expected_counts}

    def card(self, card_id: str) -> QualificationCard:
        for card in self.cards:
            if card.card_id == card_id:
                return card
        raise KeyError(card_id)


class GuidanceAdapter(Protocol):
    genre: str

    def inventory(self) -> QualificationInventory: ...


_GUIDANCE_ADAPTERS: dict[str, GuidanceAdapter] = {}


def register_guidance_adapter(adapter: GuidanceAdapter) -> None:
    _GUIDANCE_ADAPTERS[adapter.genre] = adapter


def unregister_guidance_adapter(genre: str) -> None:
    _GUIDANCE_ADAPTERS.pop(genre, None)


def _adapter_for(genre: str) -> GuidanceAdapter:
    try:
        return _GUIDANCE_ADAPTERS[genre]
    except KeyError as exc:
        raise ValueError(f"unsupported guidance genre: {genre}") from exc


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
            for name in (
                "alternatives", "tradeoffs", "downstream_consequences",
                "warnings_or_tensions", "evidence_references",
            ):
                if name in data and type(data[name]) is not tuple:
                    raise ValueError(f"{name} must be a tuple")
        return data


def _json_context(session: SessionEnvelope) -> str:
    stages: list[object] = []
    for stage in DecisionStage:
        decision = session.stages[stage].working_decision
        if decision is not None:
            stages.append({
                "stage": stage.value,
                "question": decision.question,
                "options": list(decision.options),
            })
    accepted: list[object] = []
    for milestone in session.accepted_milestones:
        accepted.append(milestone.model_dump(mode="json"))
    return json.dumps(
        {"working_decisions": stages, "accepted_milestones": accepted},
        sort_keys=True,
        separators=(",", ":"),
    )


def _context_summary(session: SessionEnvelope) -> str:
    completed = tuple(
        stage.value for stage, status in session.stages.items()
        if status.lifecycle is LifecycleStatus.COMPLETE
    )
    progress = (
        "No qualification stage is marked complete yet."
        if not completed
        else f"Completed stages currently recorded: {', '.join(completed)}."
    )
    return f"{progress} Full session state: {_json_context(session)}"


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
    card = _adapter_for(session.guidance_genre).inventory().card(card_id)
    context_summary = _context_summary(session)
    rationale = (
        f"For the current premise, {session.premise!r}, start with "
        f"{card.recommendation.lower()}. {context_summary} "
        "This keeps the decision connected to the existing story state."
    )
    return BeginnerGuidance(
        card_id=card.card_id,
        stage=card.stage,
        question=card.question,
        why_this_matters=(
            f"This decision determines how the story's central question operates for "
            f"{session.premise!r}."
        ),
        narrative_principle=card.narrative_principle,
        recommendation=card.recommendation,
        rationale=rationale,
        context_summary=context_summary,
        alternatives=tuple(option for option in card.options if option != card.recommendation),
        tradeoffs=card.warnings_or_tensions,
        downstream_consequences=_consequences(card.stage),
        warnings_or_tensions=card.warnings_or_tensions,
        evidence_references=card.evidence_references,
    )


get_guidance = guidance_for
