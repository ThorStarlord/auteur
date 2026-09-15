"""Deterministic, genre-neutral Beginner guidance and adapter routing."""

from __future__ import annotations

import json
from enum import Enum
from typing import ClassVar, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import AcceptedMilestoneReference, DecisionStage, LifecycleStatus, SessionEnvelope, StageAvailability


class QualificationStage(str, Enum):
    DISCOVER = "discover"
    STORY_IDENTITY = "story_identity"
    STRUCTURE = "structure"


class EvidenceSource(Protocol):
    def validate(self, reference: EvidenceReference) -> None: ...


_EVIDENCE_SOURCES: dict[str, EvidenceSource] = {}


def register_evidence_source(name: str, source: EvidenceSource) -> None:
    _EVIDENCE_SOURCES[name] = source


class EvidenceReference(BaseModel):
    """Typed evidence connecting one teaching claim to a domain definition."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    claim: Literal["decision", "recommendation", "option", "consequence"]
    source: str = Field(min_length=1)
    phase: int | None = Field(default=None, ge=1, le=9)
    field: str | None = None
    option_labels: tuple[str, ...] = Field(default_factory=tuple)
    rule_id: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_fields(cls, data: object) -> object:
        if isinstance(data, dict) and "option_labels" in data and type(data["option_labels"]) is not tuple:
            raise ValueError("option_labels must be a tuple")
        return data

    @model_validator(mode="after")
    def validate_reference(self) -> EvidenceReference:
        if self.source == "HowdunitTemplate":
            if self.phase is None or self.field is None or self.rule_id is not None or not self.option_labels:
                raise ValueError("invalid HowdunitTemplate evidence metadata")
        elif self.source == "RuleSet":
            if self.rule_id is None or self.phase is not None or self.field is not None or self.option_labels:
                raise ValueError("invalid RuleSet evidence metadata")
        else:
            raise ValueError(f"unknown evidence source: {self.source}")
        source = _EVIDENCE_SOURCES.get(self.source)
        if source is not None:
            source.validate(self)
        return self


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
    downstream_consequences: tuple[str, ...] = Field(default_factory=tuple)
    evidence_references: tuple[EvidenceReference, ...] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            if "stage" in data and type(data["stage"]) is not QualificationStage:
                raise ValueError("stage must be a QualificationStage")
            for name in ("options", "warnings_or_tensions", "downstream_consequences", "evidence_references"):
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
    evidence_references: tuple[EvidenceReference, ...] = Field(min_length=1)
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
        status = session.stages[stage]
        decision = status.working_decision
        stages.append({
            "stage": stage.value,
            "lifecycle": status.lifecycle.value,
            "availability": status.availability.value,
            "working_decision": None if decision is None else {
                "stage": decision.stage.value,
                "question": decision.question,
                "options": list(decision.options),
                "selected_option": decision.selected_option,
            },
        })
    accepted = [milestone.model_dump(mode="json") for milestone in session.accepted_milestones]
    return json.dumps(
        {
            "schema_version": session.schema_version,
            "session_version": session.session_version,
            "project_id": session.project_id,
            "guidance_genre": session.guidance_genre,
            "premise": session.premise,
            "stages": stages,
            "accepted_milestones": accepted,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _context_summary(session: SessionEnvelope) -> str:
    completed = tuple(
        stage.value for stage in DecisionStage
        if session.stages[stage].lifecycle is LifecycleStatus.COMPLETE
    )
    progress = (
        "No qualification stage is marked complete yet."
        if not completed
        else f"Completed stages currently recorded: {', '.join(completed)}."
    )
    return f"{progress} Full session state: {_json_context(session)}"


def _commitment_summary(card: QualificationCard, session: SessionEnvelope) -> str:
    stage_order = tuple(DecisionStage)
    card_stage = {
        QualificationStage.DISCOVER: DecisionStage.DISCOVER,
        QualificationStage.STORY_IDENTITY: DecisionStage.STORY_IDENTITY,
        QualificationStage.STRUCTURE: DecisionStage.STORY_STRUCTURE,
    }[card.stage]
    current_index = stage_order.index(card_stage)
    commitments = []
    for stage in stage_order[:current_index]:
        status = session.stages[stage]
        decision = status.working_decision
        if (
            status.availability is StageAvailability.AVAILABLE
            and status.lifecycle in (LifecycleStatus.WORKING, LifecycleStatus.COMPLETE)
            and decision is not None
            and decision.selected_option is not None
        ):
            commitments.append(f"{stage.value}: {decision.selected_option}")
    accepted = [milestone for milestone in _latest_accepted_milestones(session) if milestone.selected_option is not None]
    if accepted:
        commitments.extend(
            f"accepted {milestone.milestone_id} ({milestone.revision.artifact_id}@{milestone.revision.revision}): {milestone.selected_option}"
            for milestone in accepted
        )
    if not commitments:
        return "This is the curated default for the cited Howdunit domain option; no upstream commitment is present yet."
    return "It reinforces the current premise and commitments: " + "; ".join(commitments) + "."


def _latest_accepted_milestones(session: SessionEnvelope) -> tuple[AcceptedMilestoneReference, ...]:
    latest_by_milestone: dict[str, AcceptedMilestoneReference] = {}
    accepted_order: list[str] = []
    for milestone in session.accepted_milestones:
        current = latest_by_milestone.get(milestone.milestone_id)
        if current is None or milestone.revision.revision >= current.revision.revision:
            latest_by_milestone[milestone.milestone_id] = milestone
            if milestone.milestone_id in accepted_order:
                accepted_order.remove(milestone.milestone_id)
            accepted_order.append(milestone.milestone_id)
    return tuple(latest_by_milestone[milestone_id] for milestone_id in reversed(accepted_order))


def _select_recommendation(card: QualificationCard, session: SessionEnvelope) -> tuple[str, str]:
    stage_order = tuple(DecisionStage)
    card_stage = {
        QualificationStage.DISCOVER: DecisionStage.DISCOVER,
        QualificationStage.STORY_IDENTITY: DecisionStage.STORY_IDENTITY,
        QualificationStage.STRUCTURE: DecisionStage.STORY_STRUCTURE,
    }[card.stage]
    relevant_stages = stage_order[: stage_order.index(card_stage) + 1]
    for stage in relevant_stages:
        status = session.stages[stage]
        if (
            status.availability is not StageAvailability.AVAILABLE
            or status.lifecycle not in (LifecycleStatus.WORKING, LifecycleStatus.COMPLETE)
        ):
            continue
        decision = status.working_decision
        if decision is not None and decision.selected_option in card.options:
            return decision.selected_option, f"It reinforces the current {stage.value} selected choice."
    for milestone in _latest_accepted_milestones(session):
        if milestone.selected_option in card.options:
            return milestone.selected_option, f"It reinforces accepted milestone {milestone.milestone_id}."
    return card.recommendation, "It is the curated default for the cited Howdunit domain option."


def guidance_for(card_id: str, session: SessionEnvelope) -> BeginnerGuidance:
    """Compose one deterministic guidance card from a current session snapshot."""
    card = _adapter_for(session.guidance_genre).inventory().card(card_id)
    owning_stage = {
        QualificationStage.DISCOVER: DecisionStage.DISCOVER,
        QualificationStage.STORY_IDENTITY: DecisionStage.STORY_IDENTITY,
        QualificationStage.STRUCTURE: DecisionStage.STORY_STRUCTURE,
    }[card.stage]
    if session.stages[owning_stage].availability is not StageAvailability.AVAILABLE:
        raise ValueError(f"guidance card stage is locked: {card.stage.value}")
    context_summary = _context_summary(session)
    recommendation, recommendation_reason = _select_recommendation(card, session)
    commitment_summary = _commitment_summary(card, session)
    rationale = (
        f"This deterministic recommendation starts with {recommendation.lower()} "
        f"for the current premise, {session.premise!r}. {recommendation_reason} "
        f"{commitment_summary} {context_summary} "
        "Apply it as a teaching projection, not as a canonical selection."
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
        recommendation=recommendation,
        rationale=rationale,
        context_summary=context_summary,
        alternatives=tuple(option for option in card.options if option != recommendation),
        tradeoffs=card.warnings_or_tensions,
        downstream_consequences=card.downstream_consequences,
        warnings_or_tensions=card.warnings_or_tensions,
        evidence_references=tuple(
            reference.model_copy(update={"option_labels": (recommendation,)})
            if reference.claim == "recommendation" else reference
            for reference in card.evidence_references
        ),
    )


get_guidance = guidance_for
