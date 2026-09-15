"""Combined workspace projection for the Beginner Workspace vertical slice.

This module is deliberately free of I/O and mutation. Every surface the
workspace shows (Navigator entries, the current Decision Card, per-stage
status, warnings, tensions, review availability, canonical references, and
revision state) is rendered from one session snapshot plus the
application-owned journey state passed in by the caller, so the surfaces
cannot drift from each other.

Review rendering is whole-first: a short synthesis leads, and per-card
evidence stays expandable detail instead of replaying every card inline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .contracts import (
    AcceptedMilestoneReference,
    DecisionStage,
    SessionEnvelope,
    StageStatus,
)
from .guidance import (
    BeginnerGuidance,
    QualificationCard,
    QualificationInventory,
    QualificationStage,
)


STAGE_ORDER: tuple[DecisionStage, ...] = (
    DecisionStage.DISCOVER,
    DecisionStage.STORY_IDENTITY,
    DecisionStage.STORY_STRUCTURE,
)

QUALIFICATION_STAGE_BY_DECISION: dict[DecisionStage, QualificationStage] = {
    DecisionStage.DISCOVER: QualificationStage.DISCOVER,
    DecisionStage.STORY_IDENTITY: QualificationStage.STORY_IDENTITY,
    DecisionStage.STORY_STRUCTURE: QualificationStage.STRUCTURE,
}

STAGE_LABELS: dict[DecisionStage, str] = {
    DecisionStage.DISCOVER: "Discovery",
    DecisionStage.STORY_IDENTITY: "Story identity",
    DecisionStage.STORY_STRUCTURE: "Story structure",
}


@dataclass(frozen=True)
class NavigatorEntry:
    """One row of the workspace Navigator, derived from the shared snapshot."""

    stage: DecisionStage
    lifecycle: object
    availability: object
    total_cards: int
    answered_cards: int
    current_card_id: str | None
    review_available: bool
    ready_to_accept: bool
    at_risk_if_accepted: bool
    stale: bool
    canonical_ref: str | None = None


@dataclass(frozen=True)
class DecisionCardProjection:
    """The currently focused decision card rendered from the shared snapshot."""

    card_id: str
    stage: DecisionStage
    question: str
    options: tuple[str, ...]
    selected_option: str | None
    recommendation: str
    why_this_matters: str
    narrative_principle: str
    warnings_or_tensions: tuple[str, ...]
    downstream_consequences: tuple[str, ...]
    evidence: tuple[str, ...]
    is_exploratory: bool = False


@dataclass(frozen=True)
class TensionView:
    """A recorded contradiction that can block milestone acceptance."""

    tension_id: str
    card_id: str
    detail: str
    blocking: bool
    acknowledged: bool


@dataclass(frozen=True)
class ReviewCardSummary:
    """Expandable per-card evidence for a milestone review (not a replay)."""

    card_id: str
    question: str
    selected_option: str | None
    recommendation: str
    follows_recommendation: bool
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewProjection:
    """Milestone review state for one stage: synthesis first, evidence nested."""

    stage: DecisionStage
    opened: bool
    review_available: bool
    ready_to_accept: bool
    blockers: tuple[str, ...] = ()
    synthesis: str = ""
    card_summaries: tuple[ReviewCardSummary, ...] = ()


@dataclass(frozen=True)
class RevisionProjection:
    """Revision-exploration state: downstream risk without staleness."""

    active_revision_id: str | None = None
    is_exploration: bool = False
    at_risk_stages: tuple[DecisionStage, ...] = ()
    base_session_version: int | None = None


@dataclass(frozen=True)
class WorkspaceProjection:
    """The full workspace render built from a single snapshot."""

    session_version: int
    snapshot_session_version: int
    navigator: tuple[NavigatorEntry, ...] = ()
    decision_card: DecisionCardProjection | None = None
    stage_status: dict[DecisionStage, StageStatus] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    tensions: tuple[TensionView, ...] = ()
    reviews: dict[DecisionStage, ReviewProjection] = field(default_factory=dict)
    canonical_refs: tuple[AcceptedMilestoneReference, ...] = ()
    revision: RevisionProjection = field(default_factory=RevisionProjection)


def cards_for_stage(inventory: QualificationInventory, stage: DecisionStage) -> tuple[QualificationCard, ...]:
    """Return the inventory cards belonging to one decision stage, in order."""
    qualification_stage = QUALIFICATION_STAGE_BY_DECISION[stage]
    return tuple(card for card in inventory.cards if card.stage is qualification_stage)


def evidence_label(card: QualificationCard) -> tuple[str, ...]:
    """Render expandable evidence labels without replaying card content."""
    return tuple(f"{reference.source}:{reference.field or reference.rule_id}" for reference in card.evidence_references)


def build_workspace_projection(
    *,
    session: SessionEnvelope,
    inventory: QualificationInventory,
    answers: Mapping[str, str],
    exploratory_answers: Mapping[str, str] | None = None,
    tensions: tuple[TensionView, ...] = (),
    reviews_open: frozenset[DecisionStage] | set[DecisionStage] = frozenset(),
    active_revision_id: str | None = None,
    revision_base_version: int | None = None,
    basis_digest: str | None = None,
    current_digest: str | None = None,
    guidance: BeginnerGuidance | None = None,
    cursor_override: str | None = None,
) -> WorkspaceProjection:
    """Build every workspace surface from one session/domain snapshot."""
    exploratory = dict(exploratory_answers or {})
    cards_by_id = {card.card_id: card for card in inventory.cards}
    ordered: list[tuple[DecisionStage, QualificationCard]] = [
        (stage, card) for stage in STAGE_ORDER for card in cards_for_stage(inventory, stage)
    ]
    available = {stage for stage in STAGE_ORDER if session.stages[stage].availability.value == "available"}

    stale = bool(answers) and basis_digest is not None and basis_digest != current_digest

    cursor = _resolve_cursor(ordered, available, answers, cursor_override)

    revised_stage = _earliest_touched_stage(ordered, answers, exploratory)
    at_risk = (
        tuple(stage for stage in STAGE_ORDER if STAGE_ORDER.index(stage) > STAGE_ORDER.index(revised_stage))
        if active_revision_id is not None and revised_stage is not None
        else ()
    )

    navigator: list[NavigatorEntry] = []
    reviews: dict[DecisionStage, ReviewProjection] = {}
    for stage in STAGE_ORDER:
        stage_cards = cards_for_stage(inventory, stage)
        answered = sum(1 for card in stage_cards if card.card_id in answers)
        review_available = bool(stage_cards) and answered == len(stage_cards)
        blockers = _blockers_for_stage(stage, stage_cards, answers, tensions, stale, review_available)
        ready = review_available and not blockers
        status = session.stages[stage]
        stage_stale = stale and answered > 0
        reviews[stage] = _review_for_stage(
            stage=stage,
            stage_cards=stage_cards,
            answers=answers,
            opened=stage in reviews_open,
            review_available=review_available,
            ready_to_accept=ready,
            blockers=blockers,
            stale=stage_stale,
        )
        navigator.append(
            NavigatorEntry(
                stage=stage,
                lifecycle=status.lifecycle,
                availability=status.availability,
                total_cards=len(stage_cards),
                answered_cards=answered,
                current_card_id=cursor.card_id
                if cursor is not None and _stage_of(cursor.card_id, cards_by_id) is stage
                else None,
                review_available=review_available,
                ready_to_accept=ready,
                at_risk_if_accepted=stage in at_risk,
                stale=stage_stale,
            )
        )

    decision_card = _decision_card(cursor, answers, exploratory, guidance, cards_by_id, session)
    warnings = _warnings_for_cursor(cursor)
    return WorkspaceProjection(
        session_version=session.session_version,
        snapshot_session_version=session.session_version,
        navigator=tuple(navigator),
        decision_card=decision_card,
        stage_status=dict(session.stages),
        warnings=warnings,
        tensions=tensions,
        reviews=reviews,
        canonical_refs=tuple(session.accepted_milestones),
        revision=RevisionProjection(
            active_revision_id=active_revision_id,
            is_exploration=active_revision_id is not None,
            at_risk_stages=at_risk,
            base_session_version=revision_base_version,
        ),
    )


def _resolve_cursor(
    ordered: list[tuple[DecisionStage, QualificationCard]],
    available: set[DecisionStage],
    answers: Mapping[str, str],
    cursor_override: str | None,
) -> QualificationCard | None:
    frontier: QualificationCard | None = None
    last_answered: QualificationCard | None = None
    for stage, card in ordered:
        if stage not in available:
            continue
        if frontier is None and card.card_id not in answers:
            frontier = card
        if card.card_id in answers:
            last_answered = card
    computed = frontier if frontier is not None else last_answered
    if cursor_override is not None:
        for stage, card in ordered:
            if card.card_id != cursor_override or stage not in available:
                continue
            if card.card_id in answers or (frontier is not None and card.card_id == frontier.card_id):
                return card
    return computed


def _stage_of(card_id: str, cards_by_id: dict[str, QualificationCard]) -> DecisionStage | None:
    card = cards_by_id.get(card_id)
    if card is None:
        return None
    for stage, qualification in QUALIFICATION_STAGE_BY_DECISION.items():
        if card.stage is qualification:
            return stage
    return None


def _earliest_touched_stage(
    ordered: list[tuple[DecisionStage, QualificationCard]],
    answers: Mapping[str, str],
    exploratory: Mapping[str, str],
) -> DecisionStage | None:
    for stage, card in ordered:
        if card.card_id in answers or card.card_id in exploratory:
            return stage
    return None


def _blockers_for_stage(
    stage: DecisionStage,
    stage_cards: tuple[QualificationCard, ...],
    answers: Mapping[str, str],
    tensions: tuple[TensionView, ...],
    stale: bool,
    review_available: bool,
) -> tuple[str, ...]:
    stage_card_ids = {card.card_id for card in stage_cards}
    blockers: list[str] = []
    if not review_available:
        remaining = sum(1 for card in stage_cards if card.card_id not in answers)
        blockers.append(f"{remaining} unanswered decision(s) in {STAGE_LABELS[stage].lower()}")
    for tension in tensions:
        if tension.card_id in stage_card_ids and tension.blocking and not tension.acknowledged:
            blockers.append(f"Unresolved blocking tension: {tension.tension_id}")
    if stale and any(card.card_id in answers for card in stage_cards):
        blockers.append("Materially stale assumptions: reassess guidance before accepting")
    return tuple(blockers)


def _review_for_stage(
    *,
    stage: DecisionStage,
    stage_cards: tuple[QualificationCard, ...],
    answers: Mapping[str, str],
    opened: bool,
    review_available: bool,
    ready_to_accept: bool,
    blockers: tuple[str, ...],
    stale: bool,
) -> ReviewProjection:
    summaries = tuple(
        ReviewCardSummary(
            card_id=card.card_id,
            question=card.question,
            selected_option=answers.get(card.card_id),
            recommendation=card.recommendation,
            follows_recommendation=answers.get(card.card_id) == card.recommendation,
            evidence=evidence_label(card),
        )
        for card in stage_cards
    )
    answered = sum(1 for summary in summaries if summary.selected_option is not None)
    following = sum(1 for summary in summaries if summary.follows_recommendation)
    blocking = sum(1 for blocker in blockers if "tension" in blocker.lower())
    assumptions = "stale; reassess guidance" if stale else "current"
    synthesis = (
        f"{STAGE_LABELS[stage]} review: {answered} of {len(summaries)} decisions recorded. "
        f"{following} of {answered} follow guidance. "
        f"{blocking} blocking tension(s). Assumptions {assumptions}. "
        "Expand a card below for its evidence."
    )
    return ReviewProjection(
        stage=stage,
        opened=opened,
        review_available=review_available,
        ready_to_accept=ready_to_accept,
        blockers=blockers,
        synthesis=synthesis,
        card_summaries=summaries,
    )


def _decision_card(
    cursor: QualificationCard | None,
    answers: Mapping[str, str],
    exploratory: Mapping[str, str],
    guidance: BeginnerGuidance | None,
    cards_by_id: dict[str, QualificationCard],
    session: SessionEnvelope,
) -> DecisionCardProjection | None:
    if cursor is None:
        return None
    stage = _stage_of(cursor.card_id, cards_by_id)
    assert stage is not None
    selected = exploratory.get(cursor.card_id, answers.get(cursor.card_id))
    if guidance is not None and guidance.card_id == cursor.card_id:
        why = guidance.why_this_matters
    else:
        why = f"This decision determines how the story's central question operates for {session.premise!r}."
    return DecisionCardProjection(
        card_id=cursor.card_id,
        stage=stage,
        question=cursor.question,
        options=tuple(cursor.options),
        selected_option=selected,
        recommendation=cursor.recommendation,
        why_this_matters=why,
        narrative_principle=cursor.narrative_principle,
        warnings_or_tensions=tuple(cursor.warnings_or_tensions),
        downstream_consequences=tuple(cursor.downstream_consequences),
        evidence=evidence_label(cursor),
        is_exploratory=cursor.card_id in exploratory,
    )


def _warnings_for_cursor(cursor: QualificationCard | None) -> tuple[str, ...]:
    if cursor is None:
        return ()
    return tuple(f"{cursor.card_id}: {warning}" for warning in cursor.warnings_or_tensions)
