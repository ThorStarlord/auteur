"""Deterministic, genre-neutral Beginner guidance and adapter routing."""

from __future__ import annotations

import json
import hashlib
from enum import Enum
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import (
    AcceptedMilestoneReference,
    DecisionStage,
    DimensionCategory,
    LifecycleStatus,
    SessionEnvelope,
    StageAvailability,
)
from auteur.story_design_packs.models import DecisionCard, PackProvenance
from auteur.story_design_packs.session import TutorSession


class QualificationStage(str, Enum):
    DISCOVER = "discover"
    STORY_IDENTITY = "story_identity"
    STRUCTURE = "structure"


class EvidenceSource(Protocol):
    def validate(self, reference: EvidenceReference) -> None: ...


_EVIDENCE_SOURCES: dict[str, EvidenceSource] = {}


def register_evidence_source(name: str, source: EvidenceSource, *, replace: bool = False) -> None:
    if name in _EVIDENCE_SOURCES and not replace:
        raise ValueError(f"evidence source already registered: {name}")
    _EVIDENCE_SOURCES[name] = source


def unregister_evidence_source(name: str) -> None:
    _EVIDENCE_SOURCES.pop(name, None)


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
        source = _EVIDENCE_SOURCES.get(self.source)
        if source is None:
            raise ValueError(f"unknown evidence source: {self.source}")
        source.validate(self)
        return self


class SemanticArea(str, Enum):
    """Auteur semantic layer touched by a derived narrative consequence."""

    IDENTITY = "Identity"
    STRUCTURE = "Structure"
    REALIZATION = "Realization"
    EXPRESSION = "Expression"


class GuidanceContext(BaseModel):
    """Relevant domain knowledge used to teach one decision."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    reader_experience: str | None = None
    emotional_promise: str | None = None
    narrative_promise: str | None = None
    genre_conventions: tuple[str, ...] = Field(default_factory=tuple)
    patterns: tuple[str, ...] = Field(default_factory=tuple)
    craft_principle: str | None = None
    common_failure_mode: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_collections(cls, data: object) -> object:
        if isinstance(data, dict):
            for name in ("genre_conventions", "patterns"):
                if name in data and type(data[name]) is not tuple:
                    raise ValueError(f"{name} must be a tuple")
        return data

    @model_validator(mode="after")
    def reject_blank_context(self) -> GuidanceContext:
        values = (
            self.reader_experience,
            self.emotional_promise,
            self.narrative_promise,
            self.craft_principle,
            self.common_failure_mode,
            *self.genre_conventions,
            *self.patterns,
        )
        if any(value is not None and not value.strip() for value in values):
            raise ValueError("GuidanceContext fields must be nonblank")
        return self


class NarrativeConsequence(BaseModel):
    """Relevance-driven, derived effect of choosing one option."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    semantic_area: SemanticArea
    summary: str = Field(min_length=1)
    implications: tuple[str, ...] = Field(default_factory=tuple)
    what_becomes_easier: tuple[str, ...] = Field(default_factory=tuple)
    what_becomes_harder: tuple[str, ...] = Field(default_factory=tuple)
    risks: tuple[str, ...] = Field(default_factory=tuple)
    compensating_requirements: tuple[str, ...] = Field(default_factory=tuple)

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for name in (
                "implications",
                "what_becomes_easier",
                "what_becomes_harder",
                "risks",
                "compensating_requirements",
            ):
                if name in data and type(data[name]) is not tuple:
                    raise ValueError(f"{name} must be a tuple")
        return data

    @model_validator(mode="after")
    def reject_blank_fields(self) -> NarrativeConsequence:
        values = (
            self.summary,
            *self.implications,
            *self.what_becomes_easier,
            *self.what_becomes_harder,
            *self.risks,
            *self.compensating_requirements,
        )
        if any(not value.strip() for value in values):
            raise ValueError("NarrativeConsequence fields must be nonblank")
        return self


class OptionImpact(BaseModel):
    """Deterministic, derived explanation of what choosing an option changes."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    audience_experience: str = Field(min_length=1)
    aesthetic_framing: str = Field(min_length=1)
    expected_tropes: tuple[str, ...] = Field(min_length=1)
    narrative_structure: str = Field(min_length=1)
    tradeoffs: tuple[str, ...] = Field(min_length=1)
    narrative_consequences: tuple[NarrativeConsequence, ...] = Field(default_factory=tuple)
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_fields(cls, data: object) -> object:
        if isinstance(data, dict) and "expected_tropes" in data and type(data["expected_tropes"]) is not tuple:
            raise ValueError("expected_tropes must be a tuple")
        if isinstance(data, dict) and "tradeoffs" in data and type(data["tradeoffs"]) is not tuple:
            raise ValueError("tradeoffs must be a tuple")
        if isinstance(data, dict) and "narrative_consequences" in data and type(data["narrative_consequences"]) is not tuple:
            raise ValueError("narrative_consequences must be a tuple")
        return data


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
    downstream_consequences: tuple[str, ...] = Field(min_length=1)
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
        if any(not consequence.strip() for consequence in self.downstream_consequences):
            raise ValueError("downstream_consequences must not contain blank strings")
        return self


class QualificationInventory(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    cards: tuple[QualificationCard, ...]

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
        return self

    @property
    def stage_counts(self) -> dict[QualificationStage, int]:
        return {stage: sum(card.stage is stage for card in self.cards) for stage in QualificationStage}

    def card(self, card_id: str) -> QualificationCard:
        for card in self.cards:
            if card.card_id == card_id:
                return card
        raise KeyError(card_id)


class GuidanceAdapter(Protocol):
    genre: str

    def inventory(self) -> QualificationInventory: ...

    def validate_inventory(self, inventory: QualificationInventory) -> None: ...

    def pack_sources(self) -> tuple[PackProvenance, ...]: ...

    def tutor_session_fingerprints(self) -> dict[str, str]: ...


_GUIDANCE_ADAPTERS: dict[str, GuidanceAdapter] = {}


def register_guidance_adapter(adapter: GuidanceAdapter, *, replace: bool = False) -> None:
    if adapter.genre in _GUIDANCE_ADAPTERS and not replace:
        raise ValueError(f"guidance adapter already registered: {adapter.genre}")
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
    recommendation_rationale: str = Field(min_length=1)
    context_summary: str = Field(min_length=1)
    alternatives: tuple[str, ...] = Field(min_length=1)
    tradeoffs: tuple[str, ...] = Field(min_length=1)
    downstream_consequences: tuple[str, ...] = Field(min_length=1)
    warnings_or_tensions: tuple[str, ...] = Field(min_length=1)
    context_guidance: GuidanceContext = Field(default_factory=GuidanceContext)
    option_impacts: dict[str, OptionImpact] = Field(default_factory=dict)
    evidence_references: tuple[EvidenceReference, ...] = Field(min_length=1)
    pack_sources: tuple[PackProvenance, ...] = Field(min_length=1)
    tutor_session_fingerprints: dict[str, str] = Field(min_length=1)
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            if "stage" in data and type(data["stage"]) is not QualificationStage:
                raise ValueError("stage must be a QualificationStage")
            for name in (
                "alternatives", "tradeoffs", "downstream_consequences",
                "warnings_or_tensions", "evidence_references", "pack_sources",
            ):
                if name in data and type(data[name]) is not tuple:
                    raise ValueError(f"{name} must be a tuple")
        return data

    @model_validator(mode="after")
    def validate_renderable_consequences(self) -> BeginnerGuidance:
        if not self.downstream_consequences or any(
            not consequence.strip() for consequence in self.downstream_consequences
        ):
            raise ValueError("downstream_consequences must contain nonblank entries")
        return self

    def to_decision_card(self) -> DecisionCard:
        """Project this coordinator view into the established Tutor DecisionCard contract."""
        from auteur.story_design_packs.models import TutorDepth

        if not self.downstream_consequences or any(
            not consequence.strip() for consequence in self.downstream_consequences
        ):
            raise ValueError("downstream_consequences must contain nonblank entries")
        evidence = [reference.field or reference.rule_id or reference.source for reference in self.evidence_references]
        return DecisionCard(
            decision=self.question,
            orientation=f"Choose how {self.question.rstrip('?').lower()} in the current story.",
            why_it_matters=self.why_this_matters,
            craft_concept=self.narrative_principle,
            recommendation=self.recommendation,
            alternatives=list(self.alternatives),
            tradeoffs=list(self.tradeoffs),
            beginner_trap="Treating derived guidance as a canonical decision.",
            downstream_consequences=list(self.downstream_consequences),
            evidence=evidence,
            pack_sources=list(self.pack_sources),
            depth=TutorDepth.RECOMMEND,
            author_actions=["choose", "keep_unresolved", "request_alternatives"],
            authority_status="DERIVED / NOT CANON",
        )

    def to_tutor_session(self) -> TutorSession:
        """Create the established TutorSession using this guidance's provenance."""
        from auteur.story_design_packs.session import create_session

        context_fingerprint = hashlib.sha256(self.context_summary.encode("utf-8")).hexdigest()
        fingerprints = {
            **self.tutor_session_fingerprints,
            "beginner.guidance.context": context_fingerprint,
        }
        return create_session(
            self.to_decision_card(),
            fingerprints,
        )

    create_tutor_session = to_tutor_session


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
    stage_labels = {
        DecisionStage.DISCOVER: "Discovery",
        DecisionStage.STORY_IDENTITY: "Story identity",
        DecisionStage.STORY_STRUCTURE: "Story structure",
    }
    lifecycle_labels = {
        LifecycleStatus.NOT_STARTED: "not started",
        LifecycleStatus.WORKING: "in progress",
        LifecycleStatus.COMPLETE: "complete",
        LifecycleStatus.BLOCKED: "blocked",
    }
    availability_labels = {
        StageAvailability.AVAILABLE: "available",
        StageAvailability.LOCKED: "locked",
    }
    statuses = []
    for stage in stage_order[: current_index + 1]:
        status = session.stages[stage]
        statuses.append(
            f"{stage_labels[stage]} is {availability_labels[status.availability]} and "
            f"{lifecycle_labels[status.lifecycle]}"
        )
        decision = status.working_decision
        if (
            status.availability is StageAvailability.AVAILABLE
            and status.lifecycle in (LifecycleStatus.WORKING, LifecycleStatus.COMPLETE)
            and decision is not None
            and decision.selected_option is not None
        ):
            commitments.append(f"{stage_labels[stage]}: {decision.selected_option}")
    accepted = [milestone for milestone in _latest_accepted_milestones(session) if milestone.selected_option is not None]
    if accepted:
        commitments.extend(
            f"an accepted commitment: {milestone.selected_option}"
            for milestone in accepted
        )
    if not commitments:
        commitment_text = "This is the curated default for the cited Howdunit domain option; no explicit commitment is present yet."
    else:
        commitment_text = "It reinforces the current premise and commitments: " + "; ".join(commitments) + "."
    return commitment_text + " Sanitized stage status: " + "; ".join(statuses) + "."


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
            stage_label = {DecisionStage.DISCOVER: "Discovery", DecisionStage.STORY_IDENTITY: "story identity", DecisionStage.STORY_STRUCTURE: "story structure"}[stage]
            return decision.selected_option, f"It reinforces the current {stage_label} choice."
    for milestone in _latest_accepted_milestones(session):
        if milestone.selected_option in card.options:
            return milestone.selected_option, "It reinforces an accepted commitment."
    return card.recommendation, "It is the curated default for the cited Howdunit domain option."


def _option_impacts(card: QualificationCard) -> dict[str, OptionImpact]:
    if card.card_id == "discover.story-experience":
        return {
            "Detective procedural": OptionImpact(
                audience_experience="Follow the investigator's reasoning and case progression.",
                aesthetic_framing="Analytical and investigative.",
                expected_tropes=("interviews", "clues", "deductions"),
                narrative_structure="The investigation process organizes the story's progression.",
                tradeoffs=("Emphasizes process over impossible-mechanism puzzle solving.",),
                narrative_consequences=_narrative_consequences(
                    card.card_id,
                    "Detective procedural",
                    ("Follow the investigator's reasoning and case progression.", "Analytical and investigative.", "The investigation process organizes the story's progression.", "Emphasizes process over impossible-mechanism puzzle solving."),
                ),
            ),
            "Police/investigation procedural": OptionImpact(
                audience_experience="Follow an institutional investigation with visible procedures.",
                aesthetic_framing="Grounded and procedural.",
                expected_tropes=("teams", "evidence handling", "official process"),
                narrative_structure="Procedural stages shape how the case advances.",
                tradeoffs=("Adds institutional realism but can reduce the intimate suspect focus.",),
                narrative_consequences=_narrative_consequences(
                    card.card_id,
                    "Police/investigation procedural",
                    ("Follow an institutional investigation with visible procedures.", "Grounded and procedural.", "Procedural stages shape how the case advances.", "Adds institutional realism but can reduce the intimate suspect focus."),
                ),
            ),
            "Locked-room puzzle": OptionImpact(
                audience_experience="Actively solve an apparently impossible contained crime.",
                aesthetic_framing="Contained, precise, and puzzle-oriented.",
                expected_tropes=("impossible access", "constrained suspects", "spatial clues"),
                narrative_structure="Eliminating impossibilities becomes the central progression.",
                tradeoffs=("Strengthens the puzzle contract but demands precise mechanics and clues.",),
                narrative_consequences=_narrative_consequences(
                    card.card_id,
                    "Locked-room puzzle",
                    ("Actively solve an apparently impossible contained crime.", "Contained, precise, and puzzle-oriented.", "Eliminating impossibilities becomes the central progression.", "Strengthens the puzzle contract but demands precise mechanics and clues."),
                ),
            ),
            "Intricate puzzle structure": OptionImpact(
                audience_experience="Reconstruct a complex designed solution from layered evidence.",
                aesthetic_framing="Cerebral and engineered.",
                expected_tropes=("layered clues", "reversals", "hidden patterns"),
                narrative_structure="Clue architecture and information timing dominate the structure.",
                tradeoffs=("Offers richer reinterpretation but increases reader processing demands.",),
                narrative_consequences=_narrative_consequences(
                    card.card_id,
                    "Intricate puzzle structure",
                    ("Reconstruct a complex designed solution from layered evidence.", "Cerebral and engineered.", "Clue architecture and information timing dominate the structure.", "Offers richer reinterpretation but increases reader processing demands."),
                ),
            ),
        }
    contexts = {
        "discover.personal-stakes": {
            "Stakes: Justice served": ("A case driven by accountability and a satisfying reckoning.", "Moral urgency and consequence.", "Evidence must lead toward a culprit whose actions can be judged.", "Justice makes the ending decisive but narrows the emotional resolution."),
            "Stakes: Order restored": ("A case driven by repairing the disruption inside the elevator.", "Contained, social, and restorative.", "The investigation must show how the group can regain a workable order.", "Restoration broadens the ending beyond identifying the killer."),
        },
        "discover.investigation-approach": {
            "Logical deduction": ("The reader follows a chain of inferences from physical and behavioral clues.", "Analytical and clue-forward.", "Each discovery should make the next deduction possible without removing uncertainty.", "Deduction rewards close attention but requires fair clue placement."),
            "Intuitive investigation": ("The investigation follows hunches, impressions, and interpersonal reads.", "Psychological and impressionistic.", "Revelations should test whether intuition notices truths that evidence alone misses.", "Intuition creates character texture but makes the reasoning contract less explicit."),
            "By-the-book procedure": ("The reader sees the group impose rules and process on a chaotic closed case.", "Grounded and methodical.", "Interviews, evidence handling, and procedure organize the investigation's turns.", "Procedure adds realism but can slow the intimate pressure among suspects."),
        },
        "story_identity.protagonist-want": {
            "Want: Solve the puzzle": ("The protagonist pursues the hidden mechanism and meaning of the crime.", "Cerebral and investigative.", "The plot must keep presenting questions that reward sustained inquiry.", "Solving emphasizes the puzzle over a narrower personal outcome."),
            "Want: Identify the culprit": ("The protagonist's immediate goal is naming who killed the victim.", "Direct and accusatory.", "Suspect pressure and elimination become the main forward motion.", "A culprit-focused goal is clear but may reduce space for wider reinterpretation."),
            "Want: Restore order": ("The protagonist tries to make the trapped group safe and functional again.", "Social and stabilizing.", "Investigation beats must change the group's behavior, not only reveal facts.", "Restoration gives the mystery communal stakes but delays a purely deductive payoff."),
        },
        "story_identity.relationship-pressure": {
            "Conflict: Deduction vs. misdirection": ("Trust erodes as every useful clue may also be a deliberate diversion.", "Suspicious and adversarial.", "Each revelation should alter both the case theory and a relationship.", "Misdirection raises tension but must remain distinguishable from arbitrary withholding."),
            "Conflict: Logic vs. chaos": ("The protagonist must investigate while the trapped group becomes increasingly unpredictable.", "Volatile and pressured.", "Character disruptions interrupt clean deduction and force new investigative choices.", "Chaos intensifies the human drama but can make causality harder to track."),
        },
        "story_identity.information-contract": {
            "High confidence reader could solve it": ("The reader receives enough fair evidence to form and test a solution.", "Transparent and participatory.", "Clues must arrive early enough for the audience to reason alongside the protagonist.", "Fairness invites active solving but exposes any gap in clue logic."),
            "Medium confidence (possible on rereads)": ("The first read emphasizes suspense while a second read rewards reconstruction.", "Layered and reflective.", "Important evidence can carry a surface meaning before its deeper pattern becomes clear.", "Reread value supports ambiguity but reduces immediate solving confidence."),
            "Challenging but fair puzzle": ("The reader must work, but the final explanation remains supportable from what was shown.", "Tense and intellectually demanding.", "Reversals should narrow the possibilities without making the answer obvious too soon.", "Challenge sustains suspense but requires disciplined reveal timing."),
        },
        "story_identity.truth-opposition": {
            "Resistance: Misleading clues": ("The truth is protected by evidence that points convincingly in the wrong direction.", "Deceptive and clue-centered.", "Reversals must reframe earlier evidence rather than introduce an unrelated answer.", "Misdirection creates reread value but risks feeling unfair if motives are absent."),
            "Resistance: False suspects": ("The truth is protected by credible passengers who each appear capable of the murder.", "Suspicious and ensemble-driven.", "Interrogation and shifting suspicion structure the middle of the story.", "False suspects distribute pressure across the cast but require distinct motives."),
            "Resistance: Hidden motives": ("The truth is protected by private reasons passengers cannot safely disclose.", "Psychological and intimate.", "Revelations should expose motive layers that change how relationships are read.", "Hidden motives deepen character drama but can multiply explanatory threads."),
        },
        "structure.investigation-disruption": {
            "Clues accelerate toward solution": ("Each new clue makes the case move faster toward a confrontation.", "Urgent and escalating.", "The investigation should compress time and options as the elevator remains sealed.", "Acceleration delivers momentum but leaves less room for reflective suspect work."),
            "Steady rhythm of discovery": ("The reader receives a measured sequence of questions, clues, and revised theories.", "Balanced and methodical.", "Each turn should open one question while answering or reframing another.", "A steady rhythm supports comprehension but needs reversals to avoid feeling flat."),
            "Forward progress with setbacks": ("Every apparent advance creates a new obstacle or damaged relationship.", "Uneasy and volatile.", "The structure alternates clue gains with reversals that change the investigation's cost.", "Setbacks intensify pressure but must still preserve a visible causal trail."),
        },
        "structure.clue-distribution": {
            "Heavy clues early, light late": ("The audience gets a rich evidence field and spends the ending interpreting it.", "Dense and analytical.", "Early clues must support multiple live theories before the final pattern emerges.", "Early density rewards deduction but can make later discovery feel less surprising."),
            "Even clue distribution": ("Evidence arrives in a balanced stream that keeps solving possible throughout.", "Fair and controlled.", "Each section adds enough information to revise the current theory.", "Balance supports the reader's agency but requires careful pacing."),
            "Light clues early, heavy late": ("The story withholds most evidence until pressure and suspicion are high.", "Withheld and suspenseful.", "Late discoveries must pay off earlier questions without becoming an unexplained information dump.", "Late density heightens suspense but risks making the solution feel delivered rather than earned."),
        },
        "structure.final-revelation": {
            "Solution barely derivable from clues": ("The ending asks the reader to make a difficult but possible final inference.", "Oblique and demanding.", "The final reveal must connect scattered details through a precise causal explanation.", "Difficulty creates lingering interpretation but can frustrate without strong setup."),
            "Solution is one of several reasonable readings": ("The evidence supports a deliberate ambiguity after the central mystery is resolved.", "Ambiguous and resonant.", "The climax must close the major causal questions while leaving meaning open.", "Ambiguity extends discussion but may weaken the promise of a single culprit."),
            "Solution obvious once clues are gathered": ("The final explanation feels inevitable when the evidence is assembled.", "Crisp and satisfying.", "The climax should reveal the pattern rather than add a last-minute mechanism.", "Clarity rewards the reader but shifts suspense toward how characters react."),
        },
    }
    selected = contexts.get(card.card_id)
    if selected is None:
        raise ValueError(f"missing curated Mystery option impacts for {card.card_id}")
    return {
        option: OptionImpact(
            audience_experience=selected[option][0],
            aesthetic_framing=selected[option][1],
            expected_tropes=(card.title, "clues", "suspect pressure"),
            narrative_structure=selected[option][2],
            tradeoffs=(selected[option][3],),
            narrative_consequences=_narrative_consequences(
                card.card_id,
                option,
                selected[option],
            ),
        )
        for option in card.options
    }


def _guidance_context(card: QualificationCard, impact: OptionImpact) -> GuidanceContext:
    consequences = impact.narrative_consequences
    failure_mode = next(
        (risk for consequence in consequences for risk in consequence.risks),
        None,
    )
    return GuidanceContext(
        reader_experience=impact.audience_experience,
        narrative_promise=impact.narrative_structure,
        genre_conventions=impact.expected_tropes,
        craft_principle=card.narrative_principle,
        common_failure_mode=failure_mode,
    )


def compose_guidance_context(
    card: QualificationCard,
    session: SessionEnvelope,
    base_context: GuidanceContext,
) -> GuidanceContext:
    """Add only confirmed, relevant working dimensions to derived guidance."""
    composition = session.working_composition
    if composition is None:
        return base_context
    confirmed = tuple(
        dimension
        for dimension in composition.dimensions
        if dimension.status.value == "CONFIRMED"
    )
    if not confirmed:
        return base_context

    conventions = list(base_context.genre_conventions)
    patterns = list(base_context.patterns)
    emotional_promise = base_context.emotional_promise
    for dimension in confirmed:
        if dimension.category is DimensionCategory.SETTING_WORLD:
            conventions.append(f"{dimension.label} shapes the social pressure around the case.")
            patterns.append(dimension.label)
        elif dimension.category is DimensionCategory.RELATIONSHIP_THEMATIC:
            emotional_promise = (
                f"The investigation should intensify {dimension.label.lower()} while the truth emerges."
            )
            patterns.append(dimension.label)
        elif dimension.category is DimensionCategory.EMOTIONAL_AESTHETIC:
            emotional_promise = dimension.label
            patterns.append(dimension.label)
    return base_context.model_copy(
        update={
            "emotional_promise": emotional_promise,
            "genre_conventions": tuple(dict.fromkeys(conventions)),
            "patterns": tuple(dict.fromkeys(patterns)),
        }
    )


def _compose_option_impacts(
    card: QualificationCard,
    impacts: dict[str, OptionImpact],
    session: SessionEnvelope,
) -> dict[str, OptionImpact]:
    """Make relevant supporting dimensions change derived consequences."""
    composition = session.working_composition
    if composition is None:
        return impacts
    confirmed = tuple(
        dimension
        for dimension in composition.dimensions
        if dimension.status.value == "CONFIRMED"
    )
    supporting = tuple(
        dimension for dimension in confirmed
        if dimension.category in {
            DimensionCategory.SETTING_WORLD,
            DimensionCategory.RELATIONSHIP_THEMATIC,
            DimensionCategory.EMOTIONAL_AESTHETIC,
        }
    )
    if not supporting:
        return impacts
    labels = tuple(dimension.label for dimension in supporting)
    enriched: dict[str, OptionImpact] = {}
    for option, impact in impacts.items():
        enriched[option] = impact.model_copy(
            update={
                "tradeoffs": impact.tradeoffs + (
                    "Supporting lenses add pressure from: " + ", ".join(labels) + ".",
                ),
                "narrative_consequences": impact.narrative_consequences
                + (
                    NarrativeConsequence(
                        semantic_area=SemanticArea.IDENTITY,
                        summary="Confirmed supporting dimensions reshape how the investigation affects identity and relationships.",
                        implications=("Keep the mystery engine primary while honoring the confirmed supporting lens.",),
                        risks=("A supporting lens can become decorative if later decisions never put it under pressure.",),
                    ),
                ),
            }
        )
    return enriched
def _why_this_matters(card: QualificationCard) -> str:
    return {
        "discover.story-experience": "This choice sets the reader contract for how the mystery unfolds.",
        "discover.personal-stakes": "This choice connects the mystery's solution to a consequence that matters.",
        "discover.investigation-approach": "This choice determines how the author and reader make progress through the investigation.",
        "story_identity.protagonist-want": "This choice gives the protagonist a direction beyond solving the case.",
        "story_identity.relationship-pressure": "This choice turns the investigation into pressure on a relationship.",
        "story_identity.information-contract": "This choice sets how much the reader can infer before the revelation.",
        "story_identity.truth-opposition": "This choice determines what keeps the truth from becoming easy.",
        "structure.investigation-disruption": "This choice sets the rhythm that turns the premise into forward motion.",
        "structure.clue-distribution": "This choice determines when evidence becomes usable to the reader.",
        "structure.final-revelation": "This choice sets what the final revelation must explain and satisfy.",
    }[card.card_id]


def article_for(phrase: str) -> str:
    """Return a readable indefinite-article phrase for curated guidance copy."""
    normalized = phrase.strip().lower().rstrip(".!?")
    if normalized.startswith(("a ", "an ", "the ")):
        return normalized
    article = "an" if normalized[:1] in "aeiou" else "a"
    return f"{article} {normalized}"


def _narrative_consequences(
    card_id: str,
    option: str,
    impact: tuple[str, str, str, str],
) -> tuple[NarrativeConsequence, ...]:
    """Map curated Mystery impact copy onto relevant Auteur semantic layers."""
    audience, framing, structure, tradeoff = impact
    focus = {
        "discover.story-experience": "reader-facing mystery contract",
        "discover.personal-stakes": "story's emotional reason to investigate",
        "discover.investigation-approach": "method by which the mystery becomes knowable",
        "story_identity.protagonist-want": "protagonist's practical engine",
        "story_identity.relationship-pressure": "relationship pressure surrounding the truth",
        "story_identity.information-contract": "reader's information contract",
        "story_identity.truth-opposition": "force that protects the hidden truth",
        "structure.investigation-disruption": "investigation's escalation pattern",
        "structure.clue-distribution": "timing of usable evidence",
        "structure.final-revelation": "causal shape of the final explanation",
    }[card_id]
    identity_cards = {
        "discover.story-experience",
        "discover.personal-stakes",
        "story_identity.protagonist-want",
        "story_identity.relationship-pressure",
        "story_identity.information-contract",
        "story_identity.truth-opposition",
    }
    consequences = [
        NarrativeConsequence(
            semantic_area=SemanticArea.IDENTITY,
            summary=f"Choosing {option} commits the {focus} to {article_for(framing)} promise.",
            implications=(f"The story must deliver this reader experience: {audience.lower()}",),
            what_becomes_easier=(f"Maintaining a consistent {focus}",),
            risks=(tradeoff,),
            compensating_requirements=(f"Preserve this {focus} when later decisions add pressure.",),
        )
    ] if card_id in identity_cards else []
    consequences.append(
        NarrativeConsequence(
            semantic_area=SemanticArea.STRUCTURE,
            summary=f"{structure}",
            implications=(f"Later beats must make {focus} visible through the investigation's causal turns.",),
            what_becomes_harder=(f"Changing {option} later without reworking dependent beats",),
            risks=(tradeoff,),
            compensating_requirements=("Make each reversal or reveal pay off the selected direction.",),
        )
    )
    if card_id in {
        "story_identity.relationship-pressure",
        "story_identity.truth-opposition",
        "structure.investigation-disruption",
        "structure.clue-distribution",
        "structure.final-revelation",
    }:
        consequences.append(
            NarrativeConsequence(
                semantic_area=SemanticArea.REALIZATION,
                summary=f"Scenes must embody {option.lower()} through observable pressure and changed knowledge.",
                implications=("Character actions and revealed facts must reflect the selected constraint.",),
                what_becomes_easier=("Planning concrete investigation beats around the chosen pressure",),
                risks=("A scene can feel arbitrary if it does not change the investigation or a relationship.",),
            )
        )
    return tuple(consequences)


def guidance_for(card_id: str, session: SessionEnvelope) -> BeginnerGuidance:
    """Compose one deterministic guidance card from a current session snapshot."""
    adapter = _adapter_for(session.guidance_genre)
    inventory = adapter.inventory()
    adapter.validate_inventory(inventory)
    card = inventory.card(card_id)
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
    impacts = _compose_option_impacts(card, _option_impacts(card), session)
    recommended_impact = impacts[recommendation]
    context_guidance = compose_guidance_context(
        card,
        session,
        _guidance_context(card, recommended_impact),
    )
    rationale = (
        f"This deterministic recommendation starts with {recommendation.lower()} "
        f"for the current premise, {session.premise!r}. {recommendation_reason} "
        f"{commitment_summary} "
        "Apply it as a teaching projection, not as a canonical selection."
    )
    recommendation_rationale = (
        f"The {recommendation.lower()} choice is intended to deliver this reader experience: "
        f"{context_guidance.reader_experience} "
        f"{recommendation_reason}"
    )
    return BeginnerGuidance(
        card_id=card.card_id,
        stage=card.stage,
        question=card.question,
        why_this_matters=(
            _why_this_matters(card)
        ),
        narrative_principle=card.narrative_principle,
        recommendation=recommendation,
        rationale=rationale,
        recommendation_rationale=recommendation_rationale,
        context_summary=context_summary,
        alternatives=tuple(option for option in card.options if option != recommendation),
        tradeoffs=card.warnings_or_tensions,
        downstream_consequences=card.downstream_consequences,
        warnings_or_tensions=card.warnings_or_tensions,
        context_guidance=context_guidance,
        option_impacts=impacts,
        evidence_references=tuple(
            reference.model_copy(update={"option_labels": (recommendation,)})
            if reference.claim == "recommendation" else reference
            for reference in card.evidence_references
        ),
        pack_sources=tuple(
            dict.fromkeys(
                (*adapter.pack_sources(), *(
                    source
                    for dimension in (session.working_composition.dimensions if session.working_composition else ())
                    for source in dimension.source_provenance
                ))
            )
        ),
        tutor_session_fingerprints=adapter.tutor_session_fingerprints(),
    )


get_guidance = guidance_for
