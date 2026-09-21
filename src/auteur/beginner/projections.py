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
from typing import Literal, Mapping

from pydantic import BaseModel, ConfigDict

from .architecture_projection import StoryOrientationProjection
from .contracts import (
    AcceptedMilestoneReference,
    DecisionStage,
    LifecycleStatus,
    SessionEnvelope,
    StageStatus,
    WorkingComposition,
)
from .continuation import ContinuationState, accepted_milestone_fingerprint
from .discovery_models import DiscoveryRecommendationStatus
from .guidance import (
    BeginnerGuidance,
    GuidanceContext,
    NarrativeConsequence,
    QualificationCard,
    QualificationInventory,
    QualificationStage,
    _latest_accepted_milestones,
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
    DecisionStage.STORY_IDENTITY: "Story Identity",
    DecisionStage.STORY_STRUCTURE: "Whole-Story Structure",
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
    option_impacts: dict[str, object] = field(default_factory=dict)
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
    label: str
    question: str
    selected_option: str | None
    recommendation: str
    guidance_alignment: str
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
    target_stage: DecisionStage | None = None


@dataclass(frozen=True)
class DecisionFocus:
    """The minimum context needed to understand the current decision."""

    stage: DecisionStage
    position: str
    question: str
    why_this_matters_now: str


@dataclass(frozen=True)
class DecisionOptionProjection:
    """One selectable option with presentation-only guidance alignment."""

    label: str
    selected: bool
    recommended: bool


@dataclass(frozen=True)
class DecisionWorkspaceProjection:
    """Focused center-card projection; all fields are derived, never canonical."""

    current_focus: DecisionFocus
    options: tuple[DecisionOptionProjection, ...]
    immediate_consequence: str | None
    working_state: str
    active_issue_summary: str | None
    next_action: str
    authority_status: str = "DERIVED / NOT CANON"


@dataclass(frozen=True)
class OptionComparisonProjection:
    """Comparable narrative dimensions for one available option."""

    label: str
    reader_experience: str
    narrative_promise: str
    genre_conventions: tuple[str, ...]
    tradeoffs: tuple[str, ...]


@dataclass(frozen=True)
class GuidanceInspectorProjection:
    """On-demand Tutor detail, separated from story-facing consequences."""

    recommendation: str
    recommendation_rationale: str
    selected_choice_relationship: str
    context_guidance: GuidanceContext
    narrative_consequences: tuple[NarrativeConsequence, ...]
    option_comparisons: tuple[OptionComparisonProjection, ...]
    alternatives: tuple[str, ...]
    tradeoffs: tuple[str, ...]
    craft_principles: tuple[str, ...]
    evidence: tuple[str, ...]
    freshness: str
    authority_status: str = "DERIVED / NOT CANON"


PrimaryWorkspaceSurface = Literal[
    "architecture",
    "discovery",
    "story_identity",
    "structure",
    "complete",
]


class DiscoveryDirectionProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction_id: str
    title: str
    summary: str
    recommended: bool
    selected: bool
    tradeoffs: tuple[str, ...]
    risks: tuple[str, ...]
    authority_status: str


class DiscoveryProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    recommendation_id: str
    status: str
    recommended_direction_id: str | None
    selected_direction_id: str | None
    rationale: str
    directions: tuple[DiscoveryDirectionProjection, ...]
    blockers: tuple[str, ...] = ()
    supersedes_recommendation_id: str | None = None
    authority_status: str = "DERIVED / NOT CANON"


class IdentityCandidateProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction_id: str
    title: str
    core_answer: str
    story_type: dict[str, object]
    target_experience: dict[str, object]
    central_engine: dict[str, object]
    source_component_ids: tuple[str, ...]
    authority_status: str = "PROPOSED / NOT CANON"


def _accepted_milestone_ids(session: SessionEnvelope) -> set[str]:
    return {reference.milestone_id for reference in session.accepted_milestones}


def _primary_surface(session: SessionEnvelope) -> PrimaryWorkspaceSurface:
    accepted = _accepted_milestone_ids(session)
    if "whole_story_structure" in accepted:
        return "complete"
    if "story_identity" in accepted:
        return "structure"
    if "story_direction" in accepted:
        return "story_identity"
    recommendation = session.discovery_recommendation
    if recommendation is not None:
        return "discovery"
    if session.architecture_analysis is not None:
        return "architecture"
    return "discovery"


def _discovery_projection(session: SessionEnvelope) -> DiscoveryProjection | None:
    recommendation = session.discovery_recommendation
    if recommendation is None:
        return None
    blockers = (
        (recommendation.rationale,)
        if recommendation.status is DiscoveryRecommendationStatus.UNAVAILABLE
        else ()
    )
    return DiscoveryProjection(
        recommendation_id=recommendation.recommendation_id,
        status=recommendation.status.value,
        recommended_direction_id=recommendation.recommended_direction_id,
        selected_direction_id=recommendation.selected_direction_id,
        rationale=recommendation.rationale,
        directions=tuple(
            DiscoveryDirectionProjection(
                direction_id=direction.direction_id,
                title=direction.title,
                summary=direction.summary,
                recommended=direction.direction_id == recommendation.recommended_direction_id,
                selected=direction.direction_id == recommendation.selected_direction_id,
                tradeoffs=direction.tradeoffs,
                risks=direction.risks,
                authority_status=direction.authority_status,
            )
            for direction in recommendation.directions
        ),
        blockers=blockers,
        supersedes_recommendation_id=recommendation.supersedes_recommendation_id,
        authority_status=recommendation.authority_status,
    )


def _identity_candidate_projection(session: SessionEnvelope) -> IdentityCandidateProjection | None:
    if "story_direction" not in _accepted_milestone_ids(session):
        return None
    recommendation = session.discovery_recommendation
    if recommendation is None or recommendation.selected_direction_id is None:
        return None
    try:
        direction = recommendation.direction(recommendation.selected_direction_id)
    except KeyError:
        return None
    identity = direction.identity_candidate
    return IdentityCandidateProjection(
        direction_id=direction.direction_id,
        title=identity.title,
        core_answer=identity.core_answer,
        story_type=identity.story_type.model_dump(mode="json"),
        target_experience=identity.target_experience.model_dump(mode="json"),
        central_engine=identity.central_engine.model_dump(mode="json"),
        source_component_ids=direction.source_component_ids,
    )


def _suppress_legacy_cards(session: SessionEnvelope) -> bool:
    """Rich interpretation/discovery owns the pre-Identity surface unless unavailable."""
    if session.architecture_analysis is None:
        return False
    if "story_identity" in _accepted_milestone_ids(session):
        return False
    recommendation = session.discovery_recommendation
    return (
        recommendation is None
        or recommendation.status is not DiscoveryRecommendationStatus.UNAVAILABLE
    )


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
    available_actions: tuple[str, ...] = ()
    decision_workspace: DecisionWorkspaceProjection | None = None
    guidance_inspector: GuidanceInspectorProjection | None = None
    working_composition: WorkingComposition | None = None
    mapping_preview: object | None = None
    story_orientation: StoryOrientationProjection | None = None
    primary_surface: PrimaryWorkspaceSurface = "discovery"
    discovery: DiscoveryProjection | None = None
    identity_candidate: IdentityCandidateProjection | None = None
    continuation: ContinuationState | None = None


def cards_for_stage(inventory: QualificationInventory, stage: DecisionStage) -> tuple[QualificationCard, ...]:
    """Return the inventory cards belonging to one decision stage, in order."""
    qualification_stage = QUALIFICATION_STAGE_BY_DECISION[stage]
    return tuple(card for card in inventory.cards if card.stage is qualification_stage)


def evidence_label(card: QualificationCard) -> tuple[str, ...]:
    """Render expandable evidence labels without replaying card content."""
    labels = {
        "genre_contract": "Mystery design model · genre contract",
        "structural_forces": "Mystery design model · structural forces",
        "investigation_style": "Mystery design model · investigation style",
        "pacing_rhythm": "Mystery design model · pacing rhythm",
        "clue_distribution": "Mystery design model · clue distribution",
        "solution_density": "Mystery design model · solution density",
        "fairness_confidence": "Mystery design model · Reader fairness confidence",
    }
    rendered = [labels.get(reference.field or "", reference.field or reference.rule_id or reference.source) for reference in card.evidence_references]
    return tuple(dict.fromkeys(rendered))


def resolve_stage_lifecycle(
    *,
    stage: DecisionStage,
    stage_cards: tuple[QualificationCard, ...],
    answers: Mapping[str, str],
    tensions: tuple[TensionView, ...] = (),
    stale: bool = False,
) -> LifecycleStatus:
    """Derive the persistable per-stage lifecycle for the session envelope.

    Mapping (persisted by the application via ``BeginnerSessionStore.update`` so
    session.json consumers such as Task 5/6 see readiness without reading the
    journey sidecar):

    - ``WORKING``: at least one card unanswered; the stage is still in progress.
    - ``BLOCKED``: every card answered but milestone acceptance is gated
      (unresolved blocking contradiction or materially stale assumptions).
    - ``COMPLETE``: review available and ready to accept.

    Availability is never touched here; locked stages keep whatever lifecycle
    they hold (``NOT_STARTED``) until Task 5 canonical work unlocks them.
    """
    answered = sum(1 for card in stage_cards if card.card_id in answers)
    if not stage_cards or answered < len(stage_cards):
        return LifecycleStatus.WORKING
    blockers = _blockers_for_stage(stage, stage_cards, answers, tensions, stale, True)
    if blockers:
        return LifecycleStatus.BLOCKED
    return LifecycleStatus.COMPLETE


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
    revision_target_stage: DecisionStage | None = None,
    basis_digest: str | None = None,
    current_digest: str | None = None,
    guidance: BeginnerGuidance | None = None,
    cursor_override: str | None = None,
    working_composition: WorkingComposition | None = None,
    mapping_preview: object | None = None,
    story_orientation: StoryOrientationProjection | None = None,
    continuation: ContinuationState | None = None,
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
    if _suppress_legacy_cards(session):
        cursor = None

    # At-risk marks actual exploratory divergence only: the earliest stage touched
    # by the revision overlay. Merely opening a revision (empty overlay) marks
    # nothing at risk; parent answers never count as divergence.
    revised_stage = _earliest_touched_stage(ordered, {}, exploratory)
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
        rich_recommendation = session.discovery_recommendation
        rich_flow = (
            session.architecture_analysis is not None
            and rich_recommendation is not None
            and rich_recommendation.status is not DiscoveryRecommendationStatus.UNAVAILABLE
        )
        if rich_flow and stage is DecisionStage.DISCOVER:
            review_available = rich_recommendation.selected_direction_id is not None
            blockers = (
                ()
                if review_available
                else ("Select a Story Discovery direction before accepting.",)
            )
        elif rich_flow and stage is DecisionStage.STORY_IDENTITY:
            direction_accepted = "story_direction" in _accepted_milestone_ids(session)
            review_available = direction_accepted and mapping_preview is not None
            blockers = ()
            if not direction_accepted:
                blockers = ("Accept a Story Direction before reviewing Story Identity.",)
            elif mapping_preview is None:
                blockers = ("composition_mapping_required",)
            else:
                blockers = tuple(getattr(mapping_preview, "blocking_items", ()))
        else:
            review_available = bool(stage_cards) and answered == len(stage_cards)
            blockers = _blockers_for_stage(
                stage, stage_cards, answers, tensions, stale, review_available
            )
            if stage is DecisionStage.STORY_IDENTITY:
                if mapping_preview is None:
                    blockers = tuple(
                        dict.fromkeys((*blockers, "composition_mapping_required"))
                    )
                else:
                    blockers = tuple(
                        dict.fromkeys(
                            (*blockers, *getattr(mapping_preview, "blocking_items", ()))
                        )
                    )
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
    milestone_slugs = {
        DecisionStage.DISCOVER: "direction",
        DecisionStage.STORY_IDENTITY: "identity",
        DecisionStage.STORY_STRUCTURE: "structure",
    }
    milestone_ids = {
        DecisionStage.DISCOVER: "story_direction",
        DecisionStage.STORY_IDENTITY: "story_identity",
        DecisionStage.STORY_STRUCTURE: "whole_story_structure",
    }
    accepted_ids = {reference.milestone_id for reference in session.accepted_milestones}
    actions: list[str] = []
    for stage, review in reviews.items():
        if stage in available and review.review_available and not review.opened:
            actions.append(f"open-review:{stage.value}")
        composed_identity_ready = (
            stage is not DecisionStage.STORY_IDENTITY
            or (
                mapping_preview is not None
                and bool(getattr(mapping_preview, "ready_to_accept", False))
            )
        )
        if review.opened and review.ready_to_accept and composed_identity_ready and milestone_ids[stage] not in accepted_ids:
            actions.append(f"accept-{milestone_slugs[stage]}")
        if milestone_ids[stage] in accepted_ids:
            if active_revision_id is None:
                actions.append(f"open-revision:{stage.value}")
            elif review.opened and review.ready_to_accept and composed_identity_ready:
                actions.append(
                    "accept-revised-"
                    + ("direction" if stage is DecisionStage.DISCOVER else
                       "identity" if stage is DecisionStage.STORY_IDENTITY else "structure")
                )
    if active_revision_id is not None:
        actions.append("cancel-revision")

    # Once whole-story Structure is accepted, project the empty continuation
    # frontier even before the first continuation command persists state. This
    # keeps the accepted-foundation -> outline transition discoverable without
    # creating authority or mutating the session during a read.
    if continuation is None and "whole_story_structure" in accepted_ids:
        continuation = ContinuationState()

    if continuation is not None:
        current_fingerprint = accepted_milestone_fingerprint(session.accepted_milestones)
        proposal_fingerprint = (
            continuation.outline_proposal.source_fingerprint
            if continuation.outline_proposal is not None
            else ""
        )
        if proposal_fingerprint and proposal_fingerprint != current_fingerprint:
            continuation = continuation.model_copy(
                update={
                    "stale": True,
                    "stale_reason": "Accepted upstream inputs changed after this continuation was proposed.",
                    "draft_handoff": (
                        continuation.draft_handoff.model_copy(update={"status": "stale"})
                        if continuation.draft_handoff is not None
                        else None
                    ),
                    "draft_status": "stale" if continuation.draft_handoff is not None else continuation.draft_status,
                }
            )
            actions.append("review-stale-continuation")
        elif not continuation.stale:
            continuation = continuation.model_copy(update={"stale": False, "stale_reason": None})
        if continuation.outline_proposal is None and "whole_story_structure" in accepted_ids:
            actions.append("propose-outline")
        elif continuation.outline_proposal is not None and not continuation.outline_accepted:
            actions.append("accept-outline")
        elif continuation.outline_accepted and continuation.chapter_plan is None:
            actions.append("propose-chapter-plan")
        elif continuation.chapter_plan is not None and not continuation.chapter_plan_accepted:
            actions.append("accept-chapter-plan")
        elif continuation.chapter_plan_accepted and not continuation.scene_plans:
            actions.append("propose-scene-plans")
        elif continuation.scene_plans and not continuation.scene_plans_accepted:
            actions.append("accept-scene-plans")
        elif continuation.scene_plans_accepted and continuation.draft_handoff is None:
            actions.append("prepare-draft-handoff")
        elif continuation.draft_handoff is not None:
            actions.append("review-chapter-1" if continuation.draft_status == "drafted" else "draft-chapter-1")
    decision_workspace = _decision_workspace_projection(
        cursor=cursor,
        decision_card=decision_card,
        guidance=guidance,
        inventory=inventory,
        navigator=tuple(navigator),
        tensions=tensions,
        stale=stale,
    )
    guidance_inspector = _guidance_inspector_projection(
        cursor=cursor,
        decision_card=decision_card,
        guidance=guidance,
        stale=stale,
    )
    return WorkspaceProjection(
        session_version=session.session_version,
        snapshot_session_version=session.session_version,
        navigator=tuple(navigator),
        decision_card=decision_card,
        stage_status=dict(session.stages),
        warnings=warnings,
        tensions=tensions,
        reviews=reviews,
        canonical_refs=_latest_accepted_milestones(session),
        revision=RevisionProjection(
            active_revision_id=active_revision_id,
            is_exploration=active_revision_id is not None,
            at_risk_stages=at_risk,
            base_session_version=revision_base_version,
            target_stage=revision_target_stage,
        ),
        available_actions=tuple(actions),
        decision_workspace=decision_workspace,
        guidance_inspector=guidance_inspector,
        working_composition=working_composition if working_composition is not None else session.working_composition,
        mapping_preview=mapping_preview,
        story_orientation=story_orientation,
        primary_surface=_primary_surface(session),
        discovery=_discovery_projection(session),
        identity_candidate=_identity_candidate_projection(session),
        continuation=continuation if continuation is not None else session.continuation,
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
            label=card.title,
            question=card.question,
            selected_option=answers.get(card.card_id),
            recommendation=card.recommendation,
            guidance_alignment=(
                "unanswered"
                if answers.get(card.card_id) is None
                else (
                    "follows_guidance"
                    if answers.get(card.card_id) == card.recommendation
                    else "differs_from_guidance"
                )
            ),
            evidence=evidence_label(card),
        )
        for card in stage_cards
    )
    answered = sum(1 for summary in summaries if summary.selected_option is not None)
    following = sum(1 for summary in summaries if summary.guidance_alignment == "follows_guidance")
    blocking = sum(1 for blocker in blockers if "tension" in blocker.lower())
    assumptions = "stale; reassess guidance" if stale else "current"
    if summaries:
        synthesis = (
            f"{STAGE_LABELS[stage]} review: {answered} of {len(summaries)} decisions recorded. "
            f"{following} of {answered} follow guidance. "
            f"{blocking} blocking tension(s). Assumptions {assumptions}. "
            "Expand a card below for its evidence."
        )
    elif stage is DecisionStage.DISCOVER:
        synthesis = "Discovery review is represented by the current Story Discovery direction selection."
    elif stage is DecisionStage.STORY_IDENTITY:
        synthesis = "Story Identity review is represented by the selected direction and its promotion preview."
    else:
        synthesis = "No material curated decisions are required for this stage."
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
        option_impacts=(guidance.option_impacts if guidance is not None and guidance.card_id == cursor.card_id else {}),
        is_exploratory=cursor.card_id in exploratory,
    )


def _decision_workspace_projection(
    *,
    cursor: QualificationCard | None,
    decision_card: DecisionCardProjection | None,
    guidance: BeginnerGuidance | None,
    inventory: QualificationInventory,
    navigator: tuple[NavigatorEntry, ...],
    tensions: tuple[TensionView, ...],
    stale: bool,
) -> DecisionWorkspaceProjection | None:
    if cursor is None or decision_card is None:
        return None
    stage = cursor.stage
    stage_cards = tuple(card for card in inventory.cards if card.stage is stage)
    position = stage_cards.index(cursor) + 1
    selected = decision_card.selected_option
    options = tuple(
        DecisionOptionProjection(
            label=option,
            selected=option == selected,
            recommended=option == decision_card.recommendation,
        )
        for option in decision_card.options
    )
    immediate = None
    if selected is not None:
        impact = decision_card.option_impacts.get(selected)
        if impact is not None:
            immediate = impact.narrative_structure
    current_entry = next(entry for entry in navigator if entry.stage is decision_card.stage)
    if current_entry.review_available:
        next_action = f"Review {STAGE_LABELS[decision_card.stage]}"
    elif selected is None:
        next_action = "Choose an option"
    else:
        next_action = "Continue"
    issue = next(
        (
            tension.detail
            for tension in tensions
            if tension.card_id == cursor.card_id and tension.blocking and not tension.acknowledged
        ),
        None,
    )
    if issue is None and stale:
        issue = "This guidance depends on a story assumption that needs reassessment."
    return DecisionWorkspaceProjection(
        current_focus=DecisionFocus(
            stage=decision_card.stage,
            position=f"Decision {position} of {len(stage_cards)}",
            question=decision_card.question,
            why_this_matters_now=decision_card.why_this_matters,
        ),
        options=options,
        immediate_consequence=immediate,
        working_state=(
            "Exploratory choice saved"
            if decision_card.is_exploratory
            else "Working choice saved"
            if selected is not None
            else "Awaiting a choice"
        ),
        active_issue_summary=issue,
        next_action=next_action,
    )


def _guidance_inspector_projection(
    *,
    cursor: QualificationCard | None,
    decision_card: DecisionCardProjection | None,
    guidance: BeginnerGuidance | None,
    stale: bool,
) -> GuidanceInspectorProjection | None:
    if cursor is None or decision_card is None or guidance is None:
        return None
    selected = decision_card.selected_option
    selected_impact = guidance.option_impacts.get(selected) if selected is not None else None
    consequences = tuple(getattr(selected_impact, "narrative_consequences", ())) if selected_impact else ()
    relationship = (
        "No choice selected yet"
        if selected is None
        else "Follows Auteur's recommendation"
        if selected == guidance.recommendation
        else "Differs from Auteur's recommendation"
    )
    return GuidanceInspectorProjection(
        recommendation=guidance.recommendation,
        recommendation_rationale=guidance.recommendation_rationale,
        selected_choice_relationship=relationship,
        context_guidance=guidance.context_guidance,
        narrative_consequences=consequences,
        option_comparisons=tuple(
            OptionComparisonProjection(
                label=option,
                reader_experience=impact.audience_experience,
                narrative_promise=impact.narrative_structure,
                genre_conventions=impact.expected_tropes,
                tradeoffs=impact.tradeoffs,
            )
            for option, impact in guidance.option_impacts.items()
        ),
        alternatives=guidance.alternatives,
        tradeoffs=guidance.tradeoffs,
        craft_principles=(guidance.narrative_principle,),
        evidence=evidence_label(cursor),
        freshness="stale" if stale else "current",
    )


def _warnings_for_cursor(cursor: QualificationCard | None) -> tuple[str, ...]:
    if cursor is None:
        return ()
    # Card-level guidance is already rendered by the browser from
    # ``warnings_or_tensions``.  Do not manufacture a second, prefixed copy
    # of the same messages for the combined projection.
    return ()
