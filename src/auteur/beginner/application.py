"""Beginner journey orchestration for the vertical slice (Task 5).

BeginnerWorkspaceApplication coordinates the Task 1-3 building blocks: the
SessionEnvelope contract, the BeginnerSessionStore/CommandReceiptStore
durability layer, and the deterministic Mystery adapter behind the guidance
registry. It owns explicit journey commands plus milestone acceptance:

- select_working_option: autosave a selection without advancing the card.
  Selecting an already-answered card in an available stage renavigates to it
  and replaces the active working projection.
- continue_decision: advance to the next card once the current one is answered.
- open_milestone_review: open a whole-first review once every card in the
  stage is answered.
- reassess_guidance: recompute guidance from the current snapshot and refresh
  the recorded assumption basis (global digest plus a per-card digest map).
- acknowledge_tension: mark a recorded contradiction as acknowledged.
- open_revision / cancel_revision: explore inside an isolated revision
  snapshot; cancelling leaves the parent session unchanged and removes the
  orphaned revision snapshot.
- request_acceptance: stage-specific readiness validation that DEFERS the
  actual canonical mutation (kept for Task 4 compatibility; prefer accept_*).
- accept_story_direction: create the authoritative accepted direction record;
  never creates canonical StoryIdentity and never unlocks more than the next
  stage.
- accept_story_identity / accept_whole_story_structure: delegate the canonical
  promotion to the acceptance authority with same-command_id idempotency.
- accept_revised_*: accept an exploratory revision overlay as the new canonical
  milestone revision, preserving the previous version in provenance and
  staling downstream through the existing digest freshness propagation.

Authority-crossing flow (identity/structure/direction alike): the command
requires a caller-supplied ``command_id``; the receipt is begun BEFORE the
authority boundary is crossed; the domain promotion runs through
``AcceptanceRegistry.accept(..., command_id=...)`` so a completed command
replays its recorded result without re-invoking the owner; the session is
reconciled (acceptance reference appended, downstream unlocked, lifecycle to
COMPLETE); then the receipt completes with the domain result reference. A
failed promotion completes the receipt with a failure record and leaves the
previous canon untouched, so no partial write is possible. A retry that finds
an in-progress receipt but a completed authority record reconciles the session
without promoting twice (crash recovery).

Command envelope and idempotency: every existing-workspace journey command
accepts the common ``MutationCommand`` envelope (``workspace_id``,
``expected_session_version``, ``command_id``, ``payload``) either as a
``command=`` envelope or as individual keyword arguments (``command_id=`` plus
the usual fields, preserved for backward compatibility). When a ``command_id``
is supplied, the command runs through ``CommandReceiptStore``
begin/complete/replay: a retried ``command_id`` returns the recorded result
without double-apply, and a command already in progress is rejected. NOTE: the
persistence layer only whitelists ``create_workspace``/``promote_milestone``
receipt types and lives outside this task's edit scope, so journey commands
reuse the generic (durable, crash-safe) receipt mechanism with the
``create_workspace`` type label; direction acceptance (a session record, not a
canonical promotion) reuses the same label, while identity/structure
promotions use the whitelisted ``promote_milestone`` type with the matching
target milestone.

Lifecycle per stage is Working -> Review available -> Ready to accept, with
Canonical represented as COMPLETE plus a recorded acceptance reference for the
stage. The persisted session lifecycle mapping is ``WORKING`` (still
answering), ``BLOCKED`` (all answered but acceptance gated), ``COMPLETE``
(review available and ready to accept, or canonically accepted); locked stages
keep ``NOT_STARTED``. Availability (``AVAILABLE``/``LOCKED``) is never derived
from or mixed into lifecycle. Future stages stay availability-locked until
canonical work lands; ordinary navigation never blocks on tensions or stale
assumptions; only milestone acceptance readiness is gated by unresolved
blocking contradictions or materially stale assumptions.

Tension kinds: a non-recommended selection records a *blocking contradiction*
against guidance (must be acknowledged before acceptance); exploratory
divergence inside a revision records a *nonblocking authorial tension* (never
gates readiness, discarded with the revision on accept or cancel).

Application-owned journey state (answers, tensions, open reviews, the active
revision overlay, per-card digests, the acceptance log, cursor) lives in memory
and is mirrored to a ``journey.json`` sidecar next to ``session.json`` for
best-effort durability. The session envelope stays authoritative for
concurrency: every mutating command validates ``expected_session_version`` and
persists through ``BeginnerSessionStore.update``, so journey-sidecar writes
also advance ``session_version`` atomically and concurrent actors cannot
lost-update.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, cast

from ..acceptance import AcceptanceRegistry
from .contracts import (
    AcceptedMilestoneReference,
    DecisionStage,
    LifecycleStatus,
    MutationCommand,
    RevisionRef,
    SessionEnvelope,
    StageAvailability,
    WorkingDecision,
    WorkingComposition,
)
from .guidance import BeginnerGuidance, QualificationStage, SemanticArea, _adapter_for, guidance_for
from .persistence import (
    BeginnerConcurrencyError,
    BeginnerPersistenceError,
    BeginnerSessionStore,
    CommandReceipt,
    CommandReceiptStore,
    JsonObject,
    JsonValue,
    ReceiptAcquisition,
)
from .projections import (
    STAGE_ORDER,
    ReviewCardSummary,
    ReviewProjection,
    RevisionProjection,
    TensionView,
    WorkspaceProjection,
    build_workspace_projection,
    cards_for_stage,
    resolve_stage_lifecycle,
)


class BeginnerWorkspaceError(RuntimeError):
    """Raised when a journey command is invalid for the current workspace state."""


class LockedStageError(BeginnerWorkspaceError):
    """Raised when a command targets an availability-locked stage."""


@dataclass(frozen=True)
class SelectResult:
    """Outcome of select_working_option: saved in place, never advanced."""

    card_id: str
    selected_option: str
    saved: bool = True
    advanced: bool = False
    exploratory: bool = False
    session_version: int = 0


@dataclass(frozen=True)
class ContinueResult:
    """Outcome of continue_decision: advance or rest on review availability."""

    card_id: str
    advanced: bool
    review_available: bool
    session_version: int = 0


@dataclass(frozen=True)
class AcceptanceResult:
    """Readiness validation only; canonical mutation is deferred to Task 5."""

    stage: DecisionStage
    ready: bool
    accepted: bool = False
    deferred_to_task_5: bool = True
    review_available: bool = False
    blockers: tuple[str, ...] = ()


@dataclass(frozen=True)
class AcceptResult:
    """Outcome of an authority-crossing milestone acceptance.

    ``accepted`` is True only after the authority promotion succeeded AND the
    session was reconciled (acceptance reference persisted, downstream
    unlocked, receipt completed). A recorded failure carries ``accepted=False``
    with the domain error text; replaying it returns the same record without
    re-invoking the authority owner.
    """

    stage: DecisionStage
    accepted: bool
    revision: int = 0
    result_reference: dict[str, Any] | None = None
    session_version: int = 0
    error: str | None = None


# -- milestone authority mapping ------------------------------------------------
#
# Direction acceptance is a session record (never a canonical promotion), so it
# carries no receipt target milestone. Identity/structure acceptance delegates
# to the acceptance authority as a whitelisted ``promote_milestone`` receipt.

_MILESTONE_BY_STAGE: dict[DecisionStage, tuple[str, str | None]] = {
    DecisionStage.DISCOVER: ("story_direction", None),
    DecisionStage.STORY_IDENTITY: ("story_identity", "identity-accepted"),
    DecisionStage.STORY_STRUCTURE: ("whole_story_structure", "structure-accepted"),
}

_NEXT_STAGE: dict[DecisionStage, DecisionStage | None] = {
    DecisionStage.DISCOVER: DecisionStage.STORY_IDENTITY,
    DecisionStage.STORY_IDENTITY: DecisionStage.STORY_STRUCTURE,
    DecisionStage.STORY_STRUCTURE: None,
}

_ACCEPTABLE_MILESTONES = {"story_direction", "story_identity", "whole_story_structure"}


def _milestone_target(workspace_id: str, milestone_id: str) -> str:
    return f"beginner:{workspace_id}:{milestone_id}"


def _milestone_fingerprint(stage_answers: Mapping[str, str]) -> str:
    canonical = json.dumps(dict(sorted(stage_answers.items())), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _milestone_candidate(workspace_id: str, milestone_id: str, revision: int, fingerprint: str) -> str:
    return f"{workspace_id}:{milestone_id}:rev{revision}:{fingerprint[:16]}"


def _revision_from_candidate(candidate_id: str) -> int:
    for part in candidate_id.split(":"):
        if part.startswith("rev"):
            try:
                return max(1, int(part[3:]))
            except ValueError:
                continue
    return 1


class _BeginnerMilestoneOwner:
    """Pure in-slice acceptance owner for beginner milestone targets.

    Computes the acceptance result reference deterministically from the
    target/candidate pair without side effects, so a retried promotion that
    races a crash can never duplicate canonical state: the durable writes
    happen exactly once in the session reconcile and receipt completion steps.
    """

    def can_accept(self, target_artifact_id: str) -> bool:
        return target_artifact_id.startswith("beginner:") and target_artifact_id.rsplit(":", 1)[-1] in (
            _ACCEPTABLE_MILESTONES
        )

    def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> dict[str, Any]:
        if not confirm:
            raise ValueError("beginner milestone acceptance requires explicit confirm")
        milestone = target_artifact_id.rsplit(":", 1)[-1]
        parts = candidate_id.split(":")
        fingerprint = parts[-1] if parts else ""
        return {
            "artifact_id": target_artifact_id,
            "milestone": milestone,
            "revision": _revision_from_candidate(candidate_id),
            "fingerprint": fingerprint,
            "accepted": True,
        }


_JOURNEY_FILENAME = "journey.json"


def _tension_id_for(card_id: str) -> str:
    return f"{card_id}:non-recommended-selection"


def _exploratory_tension_id_for(card_id: str) -> str:
    return f"{card_id}:exploratory-divergence"


# -- receipt record freeze/thaw -------------------------------------------------
#
# Records are JSON-safe dicts stored via CommandReceiptStore so a retried
# command_id replays the recorded result without double-apply.


def _freeze_select_result(result: SelectResult) -> dict[str, Any]:
    return {
        "kind": "select",
        "data": {
            "card_id": result.card_id,
            "selected_option": result.selected_option,
            "saved": result.saved,
            "advanced": result.advanced,
            "exploratory": result.exploratory,
            "session_version": result.session_version,
        },
    }


def _thaw_select_result(data: Mapping[str, Any]) -> SelectResult:
    return SelectResult(
        card_id=str(data["card_id"]),
        selected_option=str(data["selected_option"]),
        saved=bool(data["saved"]),
        advanced=bool(data["advanced"]),
        exploratory=bool(data["exploratory"]),
        session_version=int(data["session_version"]),
    )


def _freeze_continue_result(result: ContinueResult) -> dict[str, Any]:
    return {
        "kind": "continue",
        "data": {
            "card_id": result.card_id,
            "advanced": result.advanced,
            "review_available": result.review_available,
            "session_version": result.session_version,
        },
    }


def _thaw_continue_result(data: Mapping[str, Any]) -> ContinueResult:
    return ContinueResult(
        card_id=str(data["card_id"]),
        advanced=bool(data["advanced"]),
        review_available=bool(data["review_available"]),
        session_version=int(data["session_version"]),
    )


def _freeze_review(review: ReviewProjection) -> dict[str, Any]:
    return {
        "kind": "open_review",
        "data": {
            "stage": review.stage.value,
            "opened": review.opened,
            "review_available": review.review_available,
            "ready_to_accept": review.ready_to_accept,
            "blockers": list(review.blockers),
            "synthesis": review.synthesis,
            "card_summaries": [
                {
                    "card_id": summary.card_id,
                    "label": summary.label,
                    "question": summary.question,
                    "selected_option": summary.selected_option,
                    "recommendation": summary.recommendation,
                    "guidance_alignment": summary.guidance_alignment,
                    "evidence": list(summary.evidence),
                }
                for summary in review.card_summaries
            ],
        },
    }


def _thaw_review(data: Mapping[str, Any]) -> ReviewProjection:
    raw_summaries = data["card_summaries"]
    assert isinstance(raw_summaries, list)
    summaries = tuple(
        ReviewCardSummary(
            card_id=str(item["card_id"]),
            label=str(item["label"]),
            question=str(item["question"]),
            selected_option=None if item["selected_option"] is None else str(item["selected_option"]),
            recommendation=str(item["recommendation"]),
            guidance_alignment=str(item.get("guidance_alignment", "unanswered")),
            evidence=tuple(str(entry) for entry in item["evidence"]),
        )
        for item in raw_summaries
        if isinstance(item, dict)
    )
    raw_blockers = data["blockers"]
    assert isinstance(raw_blockers, list)
    return ReviewProjection(
        stage=DecisionStage(str(data["stage"])),
        opened=bool(data["opened"]),
        review_available=bool(data["review_available"]),
        ready_to_accept=bool(data["ready_to_accept"]),
        blockers=tuple(str(blocker) for blocker in raw_blockers),
        synthesis=str(data["synthesis"]),
        card_summaries=summaries,
    )


def _freeze_guidance(guidance: BeginnerGuidance) -> dict[str, Any]:
    return {"kind": "reassess", "data": guidance.model_dump(mode="json")}


def _thaw_guidance(data: Mapping[str, Any]) -> BeginnerGuidance:
    payload = cast(dict[str, Any], _restore_tuples(data))
    stage = payload["stage"]
    assert isinstance(stage, str)
    payload["stage"] = QualificationStage(stage)
    option_impacts = payload.get("option_impacts", {})
    assert isinstance(option_impacts, dict)
    for impact in option_impacts.values():
        assert isinstance(impact, dict)
        consequences = impact.get("narrative_consequences", ())
        assert isinstance(consequences, tuple)
        for consequence in consequences:
            assert isinstance(consequence, dict)
            semantic_area = consequence.get("semantic_area")
            assert isinstance(semantic_area, str)
            consequence["semantic_area"] = SemanticArea(semantic_area)
    return BeginnerGuidance.model_validate(payload)


def _restore_tuples(value: Any) -> Any:
    """Restore strict-model tuples from a JSON round-trip (lists back to tuples).

    Safe for the BeginnerGuidance tree, which has no genuine list fields:
    every list produced by ``model_dump(mode="json")`` was a tuple.
    """
    if isinstance(value, list):
        return tuple(_restore_tuples(item) for item in value)
    if isinstance(value, dict):
        return {key: _restore_tuples(item) for key, item in value.items()}
    return value


def _freeze_tension(view: TensionView) -> dict[str, Any]:
    return {
        "kind": "acknowledge",
        "data": {
            "tension_id": view.tension_id,
            "card_id": view.card_id,
            "detail": view.detail,
            "blocking": view.blocking,
            "acknowledged": view.acknowledged,
        },
    }


def _thaw_tension(data: Mapping[str, Any]) -> TensionView:
    return TensionView(
        tension_id=str(data["tension_id"]),
        card_id=str(data["card_id"]),
        detail=str(data["detail"]),
        blocking=bool(data["blocking"]),
        acknowledged=bool(data["acknowledged"]),
    )


def _freeze_revision(kind: str, revision: RevisionProjection) -> dict[str, Any]:
    return {
        "kind": kind,
        "data": {
            "active_revision_id": revision.active_revision_id,
            "is_exploration": revision.is_exploration,
            "at_risk_stages": [stage.value for stage in revision.at_risk_stages],
            "base_session_version": revision.base_session_version,
            "target_stage": revision.target_stage.value if revision.target_stage is not None else None,
        },
    }


def _thaw_revision(data: Mapping[str, Any]) -> RevisionProjection:
    raw_stages = data["at_risk_stages"]
    assert isinstance(raw_stages, list)
    raw_base = data["base_session_version"]
    raw_active = data["active_revision_id"]
    raw_target = data.get("target_stage")
    return RevisionProjection(
        active_revision_id=None if raw_active is None else str(raw_active),
        is_exploration=bool(data["is_exploration"]),
        at_risk_stages=tuple(DecisionStage(str(stage)) for stage in raw_stages),
        base_session_version=None if raw_base is None else int(raw_base),
        target_stage=None if raw_target is None else DecisionStage(str(raw_target)),
    )


def _freeze_acceptance(result: AcceptanceResult) -> dict[str, Any]:
    return {
        "kind": "request_acceptance",
        "data": {
            "stage": result.stage.value,
            "ready": result.ready,
            "accepted": result.accepted,
            "deferred_to_task_5": result.deferred_to_task_5,
            "review_available": result.review_available,
            "blockers": list(result.blockers),
        },
    }


def _thaw_acceptance(data: Mapping[str, Any]) -> AcceptanceResult:
    raw_blockers = data["blockers"]
    assert isinstance(raw_blockers, list)
    return AcceptanceResult(
        stage=DecisionStage(str(data["stage"])),
        ready=bool(data["ready"]),
        accepted=bool(data["accepted"]),
        deferred_to_task_5=bool(data["deferred_to_task_5"]),
        review_available=bool(data["review_available"]),
        blockers=tuple(str(blocker) for blocker in raw_blockers),
    )


def _freeze_accept(result: AcceptResult) -> dict[str, Any]:
    return {
        "kind": "accept",
        "data": {
            "stage": result.stage.value,
            "accepted": result.accepted,
            "revision": result.revision,
            "result_reference": result.result_reference,
            "session_version": result.session_version,
            "error": result.error,
        },
    }


def _thaw_accept(data: Mapping[str, Any]) -> AcceptResult:
    raw_reference = data.get("result_reference")
    if raw_reference is not None and not isinstance(raw_reference, dict):
        raise BeginnerWorkspaceError("command receipt mismatch for accept")
    raw_error = data.get("error")
    if raw_error is not None and not isinstance(raw_error, str):
        raise BeginnerWorkspaceError("command receipt mismatch for accept")
    return AcceptResult(
        stage=DecisionStage(str(data["stage"])),
        accepted=bool(data["accepted"]),
        revision=int(data["revision"]),
        result_reference=dict(raw_reference) if isinstance(raw_reference, dict) else None,
        session_version=int(data["session_version"]),
        error=raw_error,
    )


class BeginnerWorkspaceApplication:
    """Explicit journey commands over the beginner session and its stores."""

    def __init__(
        self,
        project_root: Path | str,
        workspace_id: str,
        *,
        authority_registry: AcceptanceRegistry | None = None,
    ) -> None:
        self.session_store = BeginnerSessionStore(Path(project_root), workspace_id)
        self.receipt_store = CommandReceiptStore(Path(project_root), workspace_id)
        self.workspace_id = workspace_id
        if authority_registry is None:
            authority_registry = AcceptanceRegistry(Path(project_root))
            authority_registry.register(_BeginnerMilestoneOwner())
        self.authority = authority_registry
        self._journey_path = self.session_store.session_path.parent / _JOURNEY_FILENAME
        self._journey: dict[str, Any] = self._load_journey()

    # -- workspace lifecycle -------------------------------------------------

    def create_workspace(
        self,
        *,
        command_id: str,
        project_id: str,
        premise: str,
        guidance_genre: str = "mystery",
    ) -> SessionEnvelope:
        """Create the workspace session; replays the recorded result on retry."""
        acquisition = self.receipt_store.begin(command_id, command_type="create_workspace")
        if acquisition.outcome == "completed_replay":
            return self.session_store.load()
        if acquisition.outcome != "owner_claim":
            raise BeginnerWorkspaceError(f"command already in progress: {command_id}")
        try:
            saved = self.session_store.create(
                SessionEnvelope.new(
                    project_id=project_id,
                    guidance_genre=guidance_genre,
                    premise=premise,
                )
            )
        except (BeginnerPersistenceError, ValueError):
            raise
        self._journey["basis_digest"] = self._current_digest(saved)
        self._save_journey()
        self.receipt_store.complete(
            acquisition,
            {"workspace_id": self.workspace_id, "session_version": saved.session_version},
        )
        return saved

    # -- journey commands ----------------------------------------------------

    def select_working_option(
        self,
        *,
        card_id: str | None = None,
        option: str | None = None,
        expected_session_version: int | None = None,
        exploratory: bool = False,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> SelectResult:
        """Autosave one selection without advancing the current card.

        Accepts the common MutationCommand envelope (as ``command=``) or the
        individual fields. Selecting an already-answered card in an available
        stage renavigates to it and replaces the active working projection.
        """
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        resolved_card_id = card_id if card_id is not None else payload.get("card_id")
        resolved_option = option if option is not None else payload.get("option")
        resolved_exploratory = (
            exploratory
            or bool(payload.get("exploratory", False))
            or self._journey.get("active_revision") is not None
        )
        if not isinstance(resolved_card_id, str) or not resolved_card_id:
            raise BeginnerWorkspaceError("card_id is required")
        if not isinstance(resolved_option, str) or not resolved_option:
            raise BeginnerWorkspaceError("option is required")

        if resolved_command_id is not None:
            replayed = self._replay_completed(resolved_command_id, "select")
            if replayed is not None:
                return cast(SelectResult, replayed)

        if resolved_exploratory:
            result = self._select_exploratory(
                card_id=resolved_card_id,
                option=resolved_option,
                expected_session_version=expected,
            )
        else:
            result = self._select_working(
                card_id=resolved_card_id,
                option=resolved_option,
                expected_session_version=expected,
            )
        self._complete_command(resolved_command_id, "select", _freeze_select_result(result))
        return result

    def _select_working(self, *, card_id: str, option: str, expected_session_version: int) -> SelectResult:
        """Persist a working selection; renavigation to answered cards allowed."""
        session = self.session_store.load()
        inventory = self._inventory_for(session)
        card = self._require_card(inventory, card_id)
        stage = self._stage_of(inventory, card_id)
        self._require_available(session, stage)
        if option not in card.options:
            raise BeginnerWorkspaceError(f"unknown option for {card_id}: {option!r}")

        answers = dict(self._journey.get("answers") or {})
        cursor = self._cursor_card(session, inventory)
        is_current = cursor is not None and cursor.card_id == card_id
        if not (is_current or card_id in answers):
            raise BeginnerWorkspaceError(f"not the current card: {card_id}")

        new_answers = dict(answers)
        new_answers[card_id] = option
        new_tensions = dict(self._journey.get("tensions") or {})
        if option == card.recommendation:
            # Revising back to guidance clears the now-stale contradiction.
            new_tensions.pop(_tension_id_for(card_id), None)
        else:
            tension_id = _tension_id_for(card_id)
            detail = f"Selected {option!r} instead of the guided recommendation {card.recommendation!r} for {card_id}."
            existing = new_tensions.get(tension_id)
            if not isinstance(existing, dict) or existing.get("detail") != detail:
                new_tensions[tension_id] = {
                    "tension_id": tension_id,
                    "card_id": card_id,
                    "detail": detail,
                    "blocking": False,
                    "acknowledged": True,
                    "source": "guidance-divergence",
                }
        basis = self._journey.get("basis_digest")
        if basis is None:
            basis = self._current_digest(session)
        targets = self._lifecycle_targets(
            session, inventory, answers=new_answers, tensions=new_tensions, basis_digest=basis
        )

        def mutate(current: SessionEnvelope) -> SessionEnvelope:
            self._require_available(current, stage)
            status = current.stages[stage]
            working = WorkingDecision(
                stage=stage,
                question=card.question,
                options=list(card.options),
                selected_option=option,
            )
            updated = status.model_copy(
                update={
                    "lifecycle": targets.get(stage, LifecycleStatus.WORKING),
                    "working_decision": working,
                }
            )
            stages = dict(current.stages)
            stages[stage] = updated
            return self._with_lifecycles(current.model_copy(update={"stages": stages}), targets, exclude={stage})

        saved = self.session_store.update(expected_session_version, mutate)
        self._journey["answers"] = new_answers
        self._journey["tensions"] = new_tensions
        # Autosave pins the cursor: the current card does not advance on select.
        self._journey["cursor_override"] = card_id
        self._journey["basis_digest"] = basis
        self._save_journey()
        return SelectResult(card_id=card_id, selected_option=option, session_version=saved.session_version)

    def _select_exploratory(self, *, card_id: str, option: str, expected_session_version: int) -> SelectResult:
        """Record an exploratory selection inside the active revision overlay."""
        session = self.session_store.load()
        inventory = self._inventory_for(session)
        card = self._require_card(inventory, card_id)
        stage = self._stage_of(inventory, card_id)
        self._require_available(session, stage)
        if option not in card.options:
            raise BeginnerWorkspaceError(f"unknown option for {card_id}: {option!r}")
        active = self._journey.get("active_revision")
        if active is None:
            raise BeginnerWorkspaceError("exploratory selection requires an active revision")

        answers = dict(self._journey.get("answers") or {})
        overlay = dict(active.get("overlay") or {})
        overlay[card_id] = option
        new_tensions = dict(self._journey.get("tensions") or {})
        baseline = answers.get(card_id, card.recommendation)
        exploratory_id = _exploratory_tension_id_for(card_id)
        if option != baseline:
            detail = (
                f"Exploratory alternative {option!r} differs from the recorded answer "
                f"for {card_id}; the parent session is unchanged."
            )
            existing = new_tensions.get(exploratory_id)
            if not isinstance(existing, dict) or existing.get("detail") != detail:
                new_tensions[exploratory_id] = {
                    "tension_id": exploratory_id,
                    "card_id": card_id,
                    "detail": detail,
                    "blocking": False,
                    "acknowledged": False,
                    "source": "exploratory",
                }
        else:
            new_tensions.pop(exploratory_id, None)
        targets = self._lifecycle_targets(
            session,
            inventory,
            answers=answers,
            tensions=new_tensions,
            basis_digest=self._journey.get("basis_digest"),
        )

        saved = self.session_store.update(
            expected_session_version, lambda current: self._with_lifecycles(current, targets)
        )
        active["overlay"] = overlay
        self._journey["active_revision"] = active
        self._journey["cursor_override"] = card_id
        self._journey["tensions"] = new_tensions
        self._save_journey()
        return SelectResult(
            card_id=card_id,
            selected_option=option,
            exploratory=True,
            session_version=saved.session_version,
        )

    def continue_decision(
        self,
        *,
        card_id: str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> ContinueResult:
        """Advance past an answered card; ordinary navigation never blocks."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        resolved_card_id = card_id if card_id is not None else payload.get("card_id")
        if not isinstance(resolved_card_id, str) or not resolved_card_id:
            raise BeginnerWorkspaceError("card_id is required")

        if resolved_command_id is not None:
            replayed = self._replay_completed(resolved_command_id, "continue")
            if replayed is not None:
                return cast(ContinueResult, replayed)

        session = self.session_store.load()
        inventory = self._inventory_for(session)
        card = self._require_card(inventory, resolved_card_id)
        stage = self._stage_of(inventory, resolved_card_id)
        self._require_available(session, stage)
        cursor = self._cursor_card(session, inventory)
        if cursor is None or cursor.card_id != resolved_card_id:
            raise BeginnerWorkspaceError(f"not the current card: {resolved_card_id}")
        answers = dict(self._journey.get("answers") or {})
        if card.card_id not in answers:
            raise BeginnerWorkspaceError(f"answer the current card before continuing: {resolved_card_id}")

        stage_cards = cards_for_stage(inventory, stage)
        card_ids = [candidate.card_id for candidate in stage_cards]
        position = card_ids.index(resolved_card_id)
        targets = self._lifecycle_targets(
            session,
            inventory,
            answers=answers,
            tensions=dict(self._journey.get("tensions") or {}),
            basis_digest=self._journey.get("basis_digest"),
        )
        if position + 1 >= len(card_ids):

            def rest(current: SessionEnvelope) -> SessionEnvelope:
                return self._with_lifecycles(current, targets)

            saved = self.session_store.update(expected, rest)
            self._journey["cursor_override"] = None
            self._save_journey()
            result = ContinueResult(
                card_id=resolved_card_id,
                advanced=False,
                review_available=True,
                session_version=saved.session_version,
            )
            self._complete_command(resolved_command_id, "continue", _freeze_continue_result(result))
            return result
        next_card = stage_cards[position + 1]

        def mutate(current: SessionEnvelope) -> SessionEnvelope:
            self._require_available(current, stage)
            status = current.stages[stage]
            working = WorkingDecision(
                stage=stage,
                question=next_card.question,
                options=list(next_card.options),
                selected_option=None,
            )
            updated = status.model_copy(
                update={
                    "lifecycle": targets.get(stage, LifecycleStatus.WORKING),
                    "working_decision": working,
                }
            )
            stages = dict(current.stages)
            stages[stage] = updated
            return self._with_lifecycles(current.model_copy(update={"stages": stages}), targets, exclude={stage})

        saved = self.session_store.update(expected, mutate)
        self._journey["cursor_override"] = next_card.card_id
        self._save_journey()
        result = ContinueResult(
            card_id=next_card.card_id,
            advanced=True,
            review_available=False,
            session_version=saved.session_version,
        )
        self._complete_command(resolved_command_id, "continue", _freeze_continue_result(result))
        return result

    def open_milestone_review(
        self,
        *,
        stage: DecisionStage | str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> ReviewProjection:
        """Open the whole-first review once every card in the stage is answered."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        raw_stage = stage if stage is not None else payload.get("stage")
        if raw_stage is None:
            raise BeginnerWorkspaceError("stage is required")
        resolved = self._coerce_stage(cast(DecisionStage | str, raw_stage))

        if resolved_command_id is not None:
            replayed = self._replay_completed(resolved_command_id, "open_review")
            if replayed is not None:
                return cast(ReviewProjection, replayed)

        session = self.session_store.load()
        inventory = self._inventory_for(session)
        self._require_available(session, resolved)
        projection = self.projection()
        review = projection.reviews[resolved]
        if not review.review_available:
            raise BeginnerWorkspaceError(f"review not available for {resolved.value}: answer every card first")
        opened = list(self._journey.get("reviews_open") or [])
        if resolved.value not in opened:
            opened.append(resolved.value)
        targets = self._lifecycle_targets(
            session,
            inventory,
            answers=dict(self._journey.get("answers") or {}),
            tensions=dict(self._journey.get("tensions") or {}),
            basis_digest=self._journey.get("basis_digest"),
        )
        self.session_store.update(expected, lambda current: self._with_lifecycles(current, targets))
        self._journey["reviews_open"] = opened
        self._save_journey()
        result = self.projection().reviews[resolved]
        self._complete_command(resolved_command_id, "open_review", _freeze_review(result))
        return result

    def reassess_guidance(
        self,
        *,
        card_id: str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> BeginnerGuidance:
        """Recompute guidance from the current snapshot and refresh assumptions."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        resolved_card_id = card_id if card_id is not None else payload.get("card_id")
        if not isinstance(resolved_card_id, str) or not resolved_card_id:
            raise BeginnerWorkspaceError("card_id is required")

        if resolved_command_id is not None:
            replayed = self._replay_completed(resolved_command_id, "reassess")
            if replayed is not None:
                return cast(BeginnerGuidance, replayed)

        session = self.session_store.load()
        inventory = self._inventory_for(session)
        self._require_card(inventory, resolved_card_id)
        self._require_available(session, self._stage_of(inventory, resolved_card_id))
        guidance = guidance_for(resolved_card_id, session)
        refreshed_digest = self._current_digest(session)
        reassessed = list(self._journey.get("reassessed_cards") or [])
        if resolved_card_id not in reassessed:
            reassessed.append(resolved_card_id)
        per_card = dict(self._journey.get("basis_digests") or {})
        per_card[resolved_card_id] = refreshed_digest
        targets = self._lifecycle_targets(
            session,
            inventory,
            answers=dict(self._journey.get("answers") or {}),
            tensions=dict(self._journey.get("tensions") or {}),
            basis_digest=refreshed_digest,
        )
        self.session_store.update(expected, lambda current: self._with_lifecycles(current, targets))
        self._journey["basis_digest"] = refreshed_digest
        self._journey["basis_digests"] = per_card
        self._journey["reassessed_cards"] = reassessed
        self._save_journey()
        self._complete_command(resolved_command_id, "reassess", _freeze_guidance(guidance))
        return guidance

    def acknowledge_tension(
        self,
        *,
        tension_id: str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> TensionView:
        """Mark a recorded tension as acknowledged; never rewrites history."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        resolved_tension_id = tension_id if tension_id is not None else payload.get("tension_id")
        if not isinstance(resolved_tension_id, str) or not resolved_tension_id:
            raise BeginnerWorkspaceError("tension_id is required")

        if resolved_command_id is not None:
            replayed = self._replay_completed(resolved_command_id, "acknowledge")
            if replayed is not None:
                return cast(TensionView, replayed)

        session = self.session_store.load()
        inventory = self._inventory_for(session)
        tensions = dict(self._journey.get("tensions") or {})
        if resolved_tension_id not in tensions:
            raise BeginnerWorkspaceError(f"unknown tension: {resolved_tension_id}")
        new_tensions = dict(tensions)
        new_tensions[resolved_tension_id] = {**new_tensions[resolved_tension_id], "acknowledged": True}
        targets = self._lifecycle_targets(
            session,
            inventory,
            answers=dict(self._journey.get("answers") or {}),
            tensions=new_tensions,
            basis_digest=self._journey.get("basis_digest"),
        )
        def persist_acknowledgement(current: SessionEnvelope) -> SessionEnvelope:
            updated = self._with_lifecycles(current, targets)
            composition = current.working_composition
            if composition is not None:
                composition = composition.model_copy(
                    update={
                        "tensions": tuple(
                            tension.model_copy(update={"acknowledged": True})
                            if tension.tension_id == resolved_tension_id
                            else tension
                            for tension in composition.tensions
                        )
                    }
                )
                updated = updated.model_copy(update={"working_composition": composition})
            return updated

        self.session_store.update(expected, persist_acknowledgement)
        self._journey["tensions"] = new_tensions
        self._save_journey()
        result = self._tension_view(new_tensions[resolved_tension_id])
        self._complete_command(resolved_command_id, "acknowledge", _freeze_tension(result))
        return result

    def acknowledge_unmapped_remainder(
        self,
        *,
        remainder_id: str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> WorkingComposition:
        """Persist acknowledgement of one nonrepresentable composition remainder."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        resolved_id = remainder_id if remainder_id is not None else payload.get("remainder_id")
        if not isinstance(resolved_id, str) or not resolved_id:
            raise BeginnerWorkspaceError("remainder_id is required")
        session = self.session_store.load()
        composition = session.working_composition
        if composition is None:
            raise BeginnerWorkspaceError("no working composition exists")
        if not any(item.remainder_id == resolved_id for item in composition.unmapped_remainders):
            raise BeginnerWorkspaceError(f"unknown unmapped remainder: {resolved_id}")
        updated_composition = composition.model_copy(
            update={
                "unmapped_remainders": tuple(
                    item.model_copy(update={"acknowledged": True})
                    if item.remainder_id == resolved_id
                    else item
                    for item in composition.unmapped_remainders
                )
            }
        )
        saved = self.session_store.update(
            expected,
            lambda current: current.model_copy(update={"working_composition": updated_composition}),
        )
        if resolved_command_id is not None:
            self._complete_command(
                resolved_command_id,
                "acknowledge_remainder",
                {"remainder_id": resolved_id, "session_version": saved.session_version},
            )
        return saved.working_composition or updated_composition

    def open_revision(
        self,
        *,
        revision_id: str | None = None,
        stage: DecisionStage | str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> RevisionProjection:
        """Snapshot the session for isolated exploration; parent stays canonical."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        resolved_revision_id = revision_id if revision_id is not None else payload.get("revision_id")
        if not isinstance(resolved_revision_id, str) or not resolved_revision_id:
            raise BeginnerWorkspaceError("revision_id is required")

        if resolved_command_id is not None:
            replayed = self._replay_completed(resolved_command_id, "open_revision")
            if replayed is not None:
                return cast(RevisionProjection, replayed)

        session = self.session_store.load()
        inventory = self._inventory_for(session)
        raw_stage = stage if stage is not None else payload.get("stage")
        target_stage = None if raw_stage is None else self._coerce_stage(cast(DecisionStage | str, raw_stage))
        if target_stage is not None:
            milestone_id = _MILESTONE_BY_STAGE[target_stage][0]
            if not any(ref.milestone_id == milestone_id for ref in session.accepted_milestones):
                raise BeginnerWorkspaceError(f"cannot revise unaccepted milestone: {target_stage.value}")
        if self.session_store.revision_session_path(resolved_revision_id).exists():
            raise BeginnerWorkspaceError(f"revision already exists: {resolved_revision_id}")
        targets = self._lifecycle_targets(
            session,
            inventory,
            answers=dict(self._journey.get("answers") or {}),
            tensions=dict(self._journey.get("tensions") or {}),
            basis_digest=self._journey.get("basis_digest"),
        )
        saved = self.session_store.update(expected, lambda current: self._with_lifecycles(current, targets))
        try:
            self.session_store.save_revision(resolved_revision_id, saved)
        except ValueError:
            raise
        except BeginnerPersistenceError as exc:
            raise BeginnerWorkspaceError(str(exc)) from exc
        self._journey["active_revision"] = {
            "revision_id": resolved_revision_id,
            "base_session_version": saved.session_version,
            "overlay": {},
            "target_stage": target_stage.value if target_stage is not None else None,
        }
        if target_stage is not None:
            target_cards = cards_for_stage(inventory, target_stage)
            self._journey["cursor_override"] = target_cards[0].card_id if target_cards else None
        self._save_journey()
        result = self.projection().revision
        self._complete_command(resolved_command_id, "open_revision", _freeze_revision("open_revision", result))
        return result

    def cancel_revision(
        self,
        *,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> RevisionProjection:
        """Drop the exploration overlay; the parent session is left unchanged."""
        expected, resolved_command_id, _payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )

        if resolved_command_id is not None:
            replayed = self._replay_completed(resolved_command_id, "cancel_revision")
            if replayed is not None:
                return cast(RevisionProjection, replayed)

        session = self.session_store.load()
        inventory = self._inventory_for(session)
        active = self._journey.get("active_revision")
        if active is None:
            raise BeginnerWorkspaceError("no active revision to cancel")
        revision_id = active.get("revision_id")
        tensions = dict(self._journey.get("tensions") or {})
        new_tensions = {
            tension_id: raw
            for tension_id, raw in tensions.items()
            if not (isinstance(raw, dict) and raw.get("source") == "exploratory")
        }
        targets = self._lifecycle_targets(
            session,
            inventory,
            answers=dict(self._journey.get("answers") or {}),
            tensions=new_tensions,
            basis_digest=self._journey.get("basis_digest"),
        )
        self.session_store.update(expected, lambda current: self._with_lifecycles(current, targets))
        self._journey["active_revision"] = None
        self._journey["tensions"] = new_tensions
        self._save_journey()
        # Best-effort orphan cleanup: the revision snapshot is no longer reachable.
        if isinstance(revision_id, str) and revision_id:
            try:
                snapshot_path = self.session_store.revision_session_path(revision_id)
            except ValueError:
                snapshot_path = None
            if snapshot_path is not None:
                try:
                    snapshot_path.unlink(missing_ok=True)
                    try:
                        snapshot_path.parent.rmdir()
                    except OSError:
                        pass
                except OSError:
                    pass
        result = self.projection().revision
        self._complete_command(resolved_command_id, "cancel_revision", _freeze_revision("cancel_revision", result))
        return result

    def request_acceptance(
        self,
        *,
        stage: DecisionStage | str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> AcceptanceResult:
        """Validate readiness without mutating canonical artifacts (Task 5 owns that)."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        raw_stage = stage if stage is not None else payload.get("stage")
        if raw_stage is None:
            raise BeginnerWorkspaceError("stage is required")
        resolved = self._coerce_stage(cast(DecisionStage | str, raw_stage))

        if resolved_command_id is not None:
            replayed = self._replay_completed(resolved_command_id, "request_acceptance")
            if replayed is not None:
                return cast(AcceptanceResult, replayed)

        session = self.session_store.load()
        self._require_available(session, resolved)
        self._check_version(session, expected)
        projection = self.projection()
        review = projection.reviews[resolved]
        if not review.opened:
            raise BeginnerWorkspaceError(f"open a milestone review for {resolved.value} before requesting acceptance")
        result = AcceptanceResult(
            stage=resolved,
            ready=review.ready_to_accept,
            accepted=False,
            deferred_to_task_5=True,
            review_available=review.review_available,
            blockers=review.blockers,
        )
        self._complete_command(resolved_command_id, "request_acceptance", _freeze_acceptance(result))
        return result

    # -- milestone acceptance (authority-crossing) ---------------------------------

    def accept_story_direction(
        self,
        *,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> AcceptResult:
        """Create the authoritative accepted direction record.

        Never creates canonical StoryIdentity and never unlocks more than the
        next stage. Requires an explicit ``command_id`` for idempotency.
        """
        expected, resolved_command_id, _payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        return self._accept_milestone(
            DecisionStage.DISCOVER,
            revision_id=None,
            expected_session_version=expected,
            command_id=resolved_command_id,
        )

    def accept_story_identity(
        self,
        *,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> AcceptResult:
        """Promote canonical StoryIdentity through the acceptance authority."""
        expected, resolved_command_id, _payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        return self._accept_milestone(
            DecisionStage.STORY_IDENTITY,
            revision_id=None,
            expected_session_version=expected,
            command_id=resolved_command_id,
        )

    def accept_composed_identity(
        self,
        *,
        preview: "PromotionPreview",
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> AcceptResult:
        """Accept a validated composition through the existing Identity boundary.

        The preview remains noncanonical.  This adapter only gates the
        authority-crossing command and records the mapping evidence alongside
        the normal accepted milestone reference.
        """
        from .promotion import PromotionPreview

        if not isinstance(preview, PromotionPreview):
            raise BeginnerWorkspaceError("preview must be a PromotionPreview")
        if not preview.ready_to_accept:
            raise BeginnerWorkspaceError(
                "composed Identity is not ready to accept: "
                + "; ".join(preview.blocking_items or ("unknown blocker",))
            )
        expected, resolved_command_id, _payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        provenance = {
            "mapping_ids": [mapping.mapping_id for mapping in preview.mapping_records],
            "semantic_changes": [change.model_dump(mode="json") for change in preview.semantic_changes],
        }
        return self._accept_milestone(
            DecisionStage.STORY_IDENTITY,
            revision_id=None,
            expected_session_version=expected,
            command_id=resolved_command_id,
            promotion_metadata={"composition_mapping_provenance": provenance},
        )

    def accept_whole_story_structure(
        self,
        *,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> AcceptResult:
        """Promote canonical whole-story Structure through the authority."""
        expected, resolved_command_id, _payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        return self._accept_milestone(
            DecisionStage.STORY_STRUCTURE,
            revision_id=None,
            expected_session_version=expected,
            command_id=resolved_command_id,
        )

    def accept_revised_story_direction(
        self,
        *,
        revision_id: str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> AcceptResult:
        """Accept the exploratory direction revision as the new canonical record."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        return self._accept_milestone(
            DecisionStage.DISCOVER,
            revision_id=self._required_revision_id(revision_id, payload),
            expected_session_version=expected,
            command_id=resolved_command_id,
        )

    def accept_revised_story_identity(
        self,
        *,
        revision_id: str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> AcceptResult:
        """Accept the exploratory identity revision as the new canonical revision."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        return self._accept_milestone(
            DecisionStage.STORY_IDENTITY,
            revision_id=self._required_revision_id(revision_id, payload),
            expected_session_version=expected,
            command_id=resolved_command_id,
        )

    def accept_revised_whole_story_structure(
        self,
        *,
        revision_id: str | None = None,
        expected_session_version: int | None = None,
        command_id: str | None = None,
        workspace_id: str | None = None,
        command: MutationCommand | None = None,
    ) -> AcceptResult:
        """Accept the exploratory structure revision as the new canonical revision."""
        expected, resolved_command_id, payload = self._envelope_args(
            command=command,
            workspace_id=workspace_id,
            expected_session_version=expected_session_version,
            command_id=command_id,
        )
        return self._accept_milestone(
            DecisionStage.STORY_STRUCTURE,
            revision_id=self._required_revision_id(revision_id, payload),
            expected_session_version=expected,
            command_id=resolved_command_id,
        )

    @staticmethod
    def _required_revision_id(revision_id: str | None, payload: dict[str, Any]) -> str:
        resolved = revision_id if revision_id is not None else payload.get("revision_id")
        if not isinstance(resolved, str) or not resolved:
            raise BeginnerWorkspaceError("revision_id is required")
        return resolved

    def _accept_milestone(
        self,
        stage: DecisionStage,
        *,
        revision_id: str | None,
        expected_session_version: int,
        command_id: str | None,
        promotion_metadata: Mapping[str, Any] | None = None,
    ) -> AcceptResult:
        """Run the receipt-guarded authority flow for one milestone acceptance."""
        milestone_id, receipt_target = _MILESTONE_BY_STAGE[stage]
        if command_id is None or not command_id:
            raise BeginnerWorkspaceError("command_id is required for milestone acceptance")
        replayed = self._replay_accept(command_id)
        if replayed is not None:
            return replayed

        session = self.session_store.load()
        self._check_version(session, expected_session_version)
        self._require_available(session, stage)
        inventory = self._inventory_for(session)
        stage_cards = cards_for_stage(inventory, stage)
        stage_card_ids = [card.card_id for card in stage_cards]
        answers = dict(self._journey.get("answers") or {})
        tensions = dict(self._journey.get("tensions") or {})
        is_revision = revision_id is not None

        merged = self._acceptance_answers(
            session=session,
            milestone_id=milestone_id,
            revision_id=revision_id,
            answers=answers,
        )
        revision = sum(1 for ref in session.accepted_milestones if ref.milestone_id == milestone_id) + 1
        if not is_revision and revision > 1:
            raise BeginnerWorkspaceError(
                f"{milestone_id} is already accepted; open a revision to revise it"
            )
        if is_revision and revision == 1:
            raise BeginnerWorkspaceError(f"no accepted {milestone_id} to revise; accept it first")

        fingerprint = _milestone_fingerprint({card_id: merged[card_id] for card_id in stage_card_ids})
        target = _milestone_target(self.workspace_id, milestone_id)
        candidate = _milestone_candidate(self.workspace_id, milestone_id, revision, fingerprint)
        promotion_intent: JsonObject | None = None
        if receipt_target is not None:
            promotion_intent = {
                "workspace_id": self.workspace_id,
                "milestone": milestone_id,
                "content_fingerprint": fingerprint,
            }

        # Crash-recovery probe BEFORE gating: a retry that finds an in-progress
        # receipt plus a completed authority record must reconcile without
        # re-promoting, and must not be gated by post-crash staleness.
        try:
            existing = self.receipt_store.load(command_id)
        except BeginnerPersistenceError:
            existing = None
        if existing is not None:
            if existing.status == "complete":
                thawed = self._thaw_accept_record(existing.result)
                if thawed is not None:
                    return thawed
                raise BeginnerWorkspaceError(f"command receipt mismatch for accept: {command_id}")
            recovered = self._try_recover(
                existing,
                command_id=command_id,
                stage=stage,
                milestone_id=milestone_id,
                revision=revision,
                fingerprint=fingerprint,
                target=target,
                candidate=candidate,
                merged=merged,
                is_revision=is_revision,
                revision_id=revision_id,
                promotion_intent=promotion_intent,
            )
            if recovered is not None:
                return recovered
            raise BeginnerWorkspaceError(f"command already in progress: {command_id}")

        if not is_revision:
            self._require_ready_for_accept(stage)
        else:
            self._require_ready_for_revised_accept(
                session=session, stage=stage, merged=merged, tensions=tensions
            )

        if receipt_target is None:
            acquisition = self.receipt_store.begin(command_id, command_type="create_workspace")
        else:
            acquisition = self.receipt_store.begin(
                command_id,
                command_type="promote_milestone",
                target_milestone=cast(Any, receipt_target),
                promotion_intent=promotion_intent,
            )
        if acquisition.outcome == "completed_replay":
            thawed = self._thaw_accept_record(acquisition.result)
            if thawed is not None:
                return thawed
            raise BeginnerWorkspaceError(f"command receipt mismatch for accept: {command_id}")
        if acquisition.outcome == "existing_in_progress":
            # A concurrent actor claimed between our probe and begin.
            raced = self.receipt_store.load(command_id)
            recovered = self._try_recover(
                raced,
                command_id=command_id,
                stage=stage,
                milestone_id=milestone_id,
                revision=revision,
                fingerprint=fingerprint,
                target=target,
                candidate=candidate,
                merged=merged,
                is_revision=is_revision,
                revision_id=revision_id,
                promotion_intent=promotion_intent,
            )
            if recovered is not None:
                return recovered
            raise BeginnerWorkspaceError(f"command already in progress: {command_id}")

        try:
            domain_result = self.authority.accept(target, candidate, confirm=True, command_id=command_id)
        except Exception as exc:
            failure = AcceptResult(
                stage=stage,
                accepted=False,
                revision=revision,
                result_reference=None,
                session_version=session.session_version,
                error=f"{type(exc).__name__}: {exc}",
            )
            self.receipt_store.complete(acquisition, cast(JsonValue, _freeze_accept(failure)))
            raise
        reference = self._domain_reference(
            domain_result, target=target, milestone_id=milestone_id, revision=revision, fingerprint=fingerprint
        )
        if promotion_metadata:
            reference["promotion_metadata"] = dict(promotion_metadata)
        saved = self._reconcile_accepted_session(
            stage=stage,
            milestone_id=milestone_id,
            revision=revision,
            fingerprint=fingerprint,
            target=target,
            merged=merged,
            is_revision=is_revision,
            revision_id=revision_id,
            command_id=command_id,
            expected_session_version=expected_session_version,
        )
        result = AcceptResult(
            stage=stage,
            accepted=True,
            revision=revision,
            result_reference=reference,
            session_version=saved.session_version,
            error=None,
        )
        self.receipt_store.complete(
            acquisition,
            cast(JsonValue, _freeze_accept(result)),
            domain_result_reference=cast(JsonObject, dict(reference)),
        )
        return result

    def _acceptance_answers(
        self,
        *,
        session: SessionEnvelope,
        milestone_id: str,
        revision_id: str | None,
        answers: dict[str, str],
    ) -> dict[str, str]:
        """Resolve the answer view under acceptance: parent or revision overlay."""
        active = self._journey.get("active_revision")
        already = any(ref.milestone_id == milestone_id for ref in session.accepted_milestones)
        if revision_id is None:
            if not already and active is not None:
                raise BeginnerWorkspaceError(
                    "close the active revision before accepting the parent milestone"
                )
            return dict(answers)
        if already:
            overlay = dict(active.get("overlay") or {}) if isinstance(active, dict) else {}
            if active is None or active.get("revision_id") != revision_id:
                # The overlay was already merged by an earlier attempt (crash
                # after journey persistence); the parent answers hold the merge.
                return dict(answers)
            if not overlay:
                raise BeginnerWorkspaceError(f"revision {revision_id} has no exploratory divergence to accept")
            return {**answers, **overlay}
        if active is None or not isinstance(active, dict) or active.get("revision_id") != revision_id:
            raise BeginnerWorkspaceError(f"no active revision to accept: {revision_id}")
        overlay = dict(active.get("overlay") or {})
        if not overlay:
            raise BeginnerWorkspaceError(f"revision {revision_id} has no exploratory divergence to accept")
        return {**answers, **overlay}

    def _require_ready_for_accept(self, stage: DecisionStage) -> None:
        """Gate first-time acceptance on an opened, blocker-free review."""
        review = self.projection().reviews[stage]
        if not review.opened:
            raise BeginnerWorkspaceError(
                f"open a milestone review for {stage.value} before accepting it"
            )
        if not review.ready_to_accept:
            raise BeginnerWorkspaceError(
                f"{stage.value} is not ready to accept: {'; '.join(review.blockers) or 'unknown blocker'}"
            )

    def _require_ready_for_revised_accept(
        self,
        *,
        session: SessionEnvelope,
        stage: DecisionStage,
        merged: Mapping[str, str],
        tensions: Mapping[str, Any],
    ) -> None:
        """Gate revised acceptance on the merged overlay view being blocker-free."""
        from .projections import _blockers_for_stage

        if stage.value not in (self._journey.get("reviews_open") or []):
            raise BeginnerWorkspaceError(
                f"open a milestone review for {stage.value} before accepting its revision"
            )
        inventory = self._inventory_for(session)
        stage_cards = cards_for_stage(inventory, stage)
        views = tuple(self._tension_view(raw) for raw in tensions.values() if isinstance(raw, dict))
        merged_answers = dict(merged)
        basis = self._journey.get("basis_digest")
        stale = bool(merged_answers) and basis is not None and basis != self._current_digest(session)
        review_available = bool(stage_cards) and all(card.card_id in merged_answers for card in stage_cards)
        blockers = _blockers_for_stage(stage, stage_cards, merged_answers, views, stale, review_available)
        if blockers:
            raise BeginnerWorkspaceError(
                f"revised {stage.value} is not ready to accept: {'; '.join(blockers)}"
            )

    def _domain_reference(
        self,
        domain_result: Any,
        *,
        target: str,
        milestone_id: str,
        revision: int,
        fingerprint: str,
    ) -> dict[str, Any]:
        """Normalize the authority result to a JSON-safe canonical reference."""
        if not isinstance(domain_result, Mapping):
            raise BeginnerWorkspaceError(
                f"authority result for {milestone_id} must be a mapping, got {type(domain_result).__name__}"
            )
        try:
            normalized = cast(
                dict[str, Any],
                json.loads(json.dumps(dict(domain_result), allow_nan=False, sort_keys=True, separators=(",", ":"))),
            )
        except (TypeError, ValueError) as exc:
            raise BeginnerWorkspaceError(f"authority result for {milestone_id} must be JSON-compatible") from exc
        normalized["artifact_id"] = target
        normalized["milestone"] = milestone_id
        normalized["revision"] = revision
        normalized["fingerprint"] = fingerprint
        return normalized

    def _reconcile_accepted_session(
        self,
        *,
        stage: DecisionStage,
        milestone_id: str,
        revision: int,
        fingerprint: str,
        target: str,
        merged: Mapping[str, str],
        is_revision: bool,
        revision_id: str | None,
        command_id: str,
        expected_session_version: int,
    ) -> SessionEnvelope:
        """Persist the acceptance reference, unlock downstream, sync the sidecar."""
        inventory = self._inventory_for(self.session_store.load())
        stage_cards = cards_for_stage(inventory, stage)
        stage_card_ids = [card.card_id for card in stage_cards]
        merged_answers = dict(merged)
        content = json.dumps(
            {card_id: merged_answers[card_id] for card_id in stage_card_ids},
            sort_keys=True,
            separators=(",", ":"),
        )
        previous = [ref for ref in self.session_store.load().accepted_milestones if ref.milestone_id == milestone_id]
        previous_fingerprint = previous[-1].fingerprint if previous else None
        new_ref = AcceptedMilestoneReference(
            milestone_id=milestone_id,
            revision=RevisionRef(artifact_id=target, revision=revision),
            accepted_content=content,
            fingerprint=fingerprint,
            selected_option=None,
        )
        pruned_tensions = self._tensions_without_exploratory() if is_revision else None
        basis = self._acceptance_basis(is_revision=is_revision, milestone_id=milestone_id, revision=revision)

        def mutate(current: SessionEnvelope) -> SessionEnvelope:
            refs = list(current.accepted_milestones)
            if not any(
                ref.milestone_id == milestone_id
                and ref.revision.revision == revision
                and ref.fingerprint == fingerprint
                for ref in refs
            ):
                refs.append(new_ref)
            targets = self._lifecycle_targets(
                current,
                inventory,
                answers=merged_answers,
                tensions=pruned_tensions if pruned_tensions is not None else dict(self._journey.get("tensions") or {}),
                basis_digest=basis if is_revision else self._journey.get("basis_digest"),
            )
            stages = dict(current.stages)
            for locked_stage, lifecycle in targets.items():
                if locked_stage is stage:
                    continue
                stages[locked_stage] = stages[locked_stage].model_copy(update={"lifecycle": lifecycle})
            stages[stage] = stages[stage].model_copy(update={"lifecycle": LifecycleStatus.COMPLETE})
            next_stage = _NEXT_STAGE[stage]
            if next_stage is not None and stages[next_stage].availability is StageAvailability.LOCKED:
                stages[next_stage] = stages[next_stage].model_copy(
                    update={"availability": StageAvailability.AVAILABLE, "lifecycle": LifecycleStatus.WORKING}
                )
            return current.model_copy(update={"stages": stages, "accepted_milestones": refs})

        saved = self.session_store.update(expected_session_version, mutate)
        self._sync_journey_after_accept(
            merged=merged_answers,
            is_revision=is_revision,
            revision_id=revision_id,
            milestone_id=milestone_id,
            revision=revision,
            fingerprint=fingerprint,
            previous_fingerprint=previous_fingerprint,
            command_id=command_id,
        )
        return saved

    def _tensions_without_exploratory(self) -> dict[str, Any]:
        return {
            tension_id: raw
            for tension_id, raw in (dict(self._journey.get("tensions") or {}).items())
            if not (isinstance(raw, dict) and raw.get("source") == "exploratory")
        }

    def _acceptance_basis(self, *, is_revision: bool, milestone_id: str, revision: int) -> str | None:
        """Return the post-accept assumption basis.

        First-time accepts keep the recorded basis (nothing downstream is
        answered yet, so nothing can go stale). Revised accepts invalidate the
        basis through the existing digest comparison, which marks answered
        downstream stages stale in the combined projection; a later
        reassessment re-baselines.
        """
        if not is_revision:
            basis = self._journey.get("basis_digest")
            return None if basis is None else str(basis)
        previous_basis = self._journey.get("basis_digest") or "none"
        return f"accepted-revision:{milestone_id}:rev{revision}:{previous_basis}"

    def _sync_journey_after_accept(
        self,
        *,
        merged: dict[str, str],
        is_revision: bool,
        revision_id: str | None,
        milestone_id: str,
        revision: int,
        fingerprint: str,
        previous_fingerprint: str | None,
        command_id: str,
    ) -> None:
        """Mirror acceptance into the journey sidecar (idempotent on retry)."""
        changed = False
        if self._journey.get("cursor_override") is not None:
            # Release the autosave pin so the Decision Card advances to the
            # next stage frontier ("Begin next stage"); the pin is an
            # exploration affordance, not canonical state.
            self._journey["cursor_override"] = None
            changed = True
        if is_revision:
            if self._journey.get("answers") != merged:
                self._journey["answers"] = dict(merged)
                changed = True
            pruned = self._tensions_without_exploratory()
            if pruned != dict(self._journey.get("tensions") or {}):
                self._journey["tensions"] = pruned
                changed = True
            if self._journey.get("active_revision") is not None:
                self._journey["active_revision"] = None
                changed = True
                self._remove_revision_snapshot(revision_id)
            prefix = f"accepted-revision:{milestone_id}:rev{revision}:"
            if not str(self._journey.get("basis_digest") or "").startswith(prefix):
                self._journey["basis_digest"] = prefix + str(self._journey.get("basis_digest") or "none")
                changed = True
        log = list(self._journey.get("acceptance_log") or [])
        if not any(isinstance(entry, dict) and entry.get("command_id") == command_id for entry in log):
            log.append(
                {
                    "milestone": milestone_id,
                    "revision": revision,
                    "fingerprint": fingerprint,
                    "supersedes": previous_fingerprint,
                    "command_id": command_id,
                    "stage": milestone_id,
                }
            )
            self._journey["acceptance_log"] = log
            changed = True
        if changed:
            self._save_journey()

    def _remove_revision_snapshot(self, revision_id: str | None) -> None:
        """Best-effort orphan cleanup for an accepted revision snapshot."""
        if not isinstance(revision_id, str) or not revision_id:
            return
        try:
            snapshot_path = self.session_store.revision_session_path(revision_id)
        except ValueError:
            return
        try:
            snapshot_path.unlink(missing_ok=True)
            try:
                snapshot_path.parent.rmdir()
            except OSError:
                pass
        except OSError:
            pass

    def _try_recover(
        self,
        existing: CommandReceipt,
        *,
        command_id: str,
        stage: DecisionStage,
        milestone_id: str,
        revision: int,
        fingerprint: str,
        target: str,
        candidate: str,
        merged: Mapping[str, str],
        is_revision: bool,
        revision_id: str | None,
        promotion_intent: JsonObject | None,
    ) -> AcceptResult | None:
        """Reconcile after a crash between promotion and receipt completion.

        Returns None when the authority holds no completed record for this
        command (a genuine in-progress collision the caller must reject), so a
        duplicate promotion is impossible: the owner is never invoked here.
        """
        if existing.status != "in_progress":
            return None
        if promotion_intent is not None and existing.promotion_intent != promotion_intent:
            raise BeginnerPersistenceError(f"command intent conflict for existing command_id {command_id}")
        completed = self.authority.journal.find_completed(command_id)
        if (
            completed is None
            or completed.get("target_artifact_id") != target
            or completed.get("candidate_id") != candidate
        ):
            return None
        journal_result = completed.get("result")
        reference = self._domain_reference(
            journal_result if isinstance(journal_result, Mapping) else {},
            target=target,
            milestone_id=milestone_id,
            revision=revision,
            fingerprint=fingerprint,
        )
        fresh = self.session_store.load()
        if any(
            ref.milestone_id == milestone_id
            and ref.revision.revision == revision
            and ref.fingerprint == fingerprint
            for ref in fresh.accepted_milestones
        ):
            version = fresh.session_version
        else:
            saved = self._reconcile_accepted_session(
                stage=stage,
                milestone_id=milestone_id,
                revision=revision,
                fingerprint=fingerprint,
                target=target,
                merged=merged,
                is_revision=is_revision,
                revision_id=revision_id,
                command_id=command_id,
                expected_session_version=fresh.session_version,
            )
            version = saved.session_version
        result = AcceptResult(
            stage=stage,
            accepted=True,
            revision=revision,
            result_reference=reference,
            session_version=version,
            error=None,
        )
        self.receipt_store.complete(
            existing,
            cast(JsonValue, _freeze_accept(result)),
            domain_result_reference=cast(JsonObject, dict(reference)),
        )
        return result

    def _replay_accept(self, command_id: str) -> AcceptResult | None:
        """Return the recorded accept result for a completed command_id, if any."""
        try:
            replayed = self.receipt_store.replay(command_id)
        except BeginnerPersistenceError:
            return None
        if replayed is None:
            return None
        return self._thaw_accept_record(replayed.result)

    def _thaw_accept_record(self, result: JsonValue) -> AcceptResult | None:
        if not isinstance(result, dict) or result.get("kind") != "accept":
            return None
        data = result.get("data")
        if not isinstance(data, dict):
            return None
        return _thaw_accept(cast(dict[str, Any], data))

    # -- command envelope + receipt plumbing -------------------------------------

    def _envelope_args(
        self,
        *,
        command: MutationCommand | None,
        workspace_id: str | None,
        expected_session_version: int | None,
        command_id: str | None,
    ) -> tuple[int, str | None, dict[str, Any]]:
        """Resolve the common envelope from either a MutationCommand or kwargs."""
        if command is not None:
            if command.workspace_id != self.workspace_id:
                raise BeginnerWorkspaceError(
                    f"command targets workspace {command.workspace_id!r}, not {self.workspace_id!r}"
                )
            return command.expected_session_version, command.command_id, dict(command.payload)
        if workspace_id is not None and workspace_id != self.workspace_id:
            raise BeginnerWorkspaceError(f"command targets workspace {workspace_id!r}, not {self.workspace_id!r}")
        if expected_session_version is None:
            raise BeginnerWorkspaceError("expected_session_version is required")
        return expected_session_version, command_id, {}

    def _replay_completed(self, command_id: str, kind: str) -> Any | None:
        """Return the recorded result for a completed command_id, if any.

        Uses CommandReceiptStore.replay: a missing receipt returns None (the
        caller proceeds to claim), while an in-progress receipt raises so a
        concurrent retry cannot double-apply.
        """
        try:
            replayed = self.receipt_store.replay(command_id)
        except BeginnerPersistenceError:
            return None
        if replayed is None:
            raise BeginnerWorkspaceError(f"command already in progress: {command_id}")
        return self._thaw_result(kind, replayed.result)

    def _complete_command(self, command_id: str | None, kind: str, record: dict[str, Any]) -> ReceiptAcquisition | None:
        """Claim and complete the receipt for a newly executed command."""
        if command_id is None:
            return None
        acquisition = self.receipt_store.begin(command_id, command_type="create_workspace")
        if acquisition.outcome == "completed_replay":
            # A concurrent actor completed between our replay check and claim.
            return acquisition
        if acquisition.outcome != "owner_claim":
            raise BeginnerWorkspaceError(f"command already in progress: {command_id}")
        self.receipt_store.complete(acquisition, cast(JsonValue, record))
        return acquisition

    def _thaw_result(self, kind: str, result: JsonValue) -> Any:
        """Rebuild a recorded command result; rejects kind mismatches."""
        if not isinstance(result, dict) or result.get("kind") != kind:
            raise BeginnerWorkspaceError(f"command receipt mismatch for {kind}")
        data = result.get("data")
        if not isinstance(data, dict):
            raise BeginnerWorkspaceError(f"command receipt mismatch for {kind}")
        payload = cast(dict[str, Any], data)
        if kind == "select":
            return _thaw_select_result(payload)
        if kind == "continue":
            return _thaw_continue_result(payload)
        if kind == "open_review":
            return _thaw_review(payload)
        if kind == "reassess":
            return _thaw_guidance(payload)
        if kind == "acknowledge":
            return _thaw_tension(payload)
        if kind in ("open_revision", "cancel_revision"):
            return _thaw_revision(payload)
        if kind == "request_acceptance":
            return _thaw_acceptance(payload)
        if kind == "accept":
            return _thaw_accept(payload)
        raise BeginnerWorkspaceError(f"unknown command receipt kind: {kind}")

    # -- read-only projection --------------------------------------------------

    def projection(self, *, focus_card_id: str | None = None) -> WorkspaceProjection:
        """Render every surface from the same session/domain snapshot."""
        session = self.session_store.load()
        inventory = self._inventory_for(session)
        answers = dict(self._journey.get("answers") or {})
        active = self._journey.get("active_revision") or {}
        exploratory = dict(active.get("overlay") or {})
        tensions = tuple(self._tension_view(raw) for raw in (dict(self._journey.get("tensions") or {}).values()))
        reviews_open = {self._coerce_stage(name) for name in (self._journey.get("reviews_open") or [])}
        cursor = self._cursor_card(session, inventory)
        guidance: BeginnerGuidance | None = None
        if cursor is not None:
            try:
                guidance = guidance_for(cursor.card_id, session)
            except ValueError:
                guidance = None
        return build_workspace_projection(
            session=session,
            inventory=inventory,
            answers=answers,
            exploratory_answers=exploratory,
            tensions=tensions,
            reviews_open=reviews_open,
            active_revision_id=active.get("revision_id"),
            revision_base_version=active.get("base_session_version"),
            revision_target_stage=(
                self._coerce_stage(active["target_stage"])
                if active.get("target_stage") is not None
                else None
            ),
            basis_digest=self._journey.get("basis_digest"),
            current_digest=self._current_digest(session),
            guidance=guidance,
            cursor_override=focus_card_id or self._journey.get("cursor_override"),
        )

    # -- internals ---------------------------------------------------------------

    def _lifecycle_targets(
        self,
        session: SessionEnvelope,
        inventory: Any,
        *,
        answers: dict[str, str],
        tensions: dict[str, Any],
        basis_digest: str | None,
    ) -> dict[DecisionStage, LifecycleStatus]:
        """Compute persistable lifecycles for available stages (never availability)."""
        views = tuple(self._tension_view(raw) for raw in tensions.values() if isinstance(raw, dict))
        current_digest = self._current_digest(session)
        stale = bool(answers) and basis_digest is not None and basis_digest != current_digest
        targets: dict[DecisionStage, LifecycleStatus] = {}
        for stage in STAGE_ORDER:
            if session.stages[stage].availability is not StageAvailability.AVAILABLE:
                continue
            stage_cards = cards_for_stage(inventory, stage)
            stage_stale = bool(stale) and any(card.card_id in answers for card in stage_cards)
            targets[stage] = resolve_stage_lifecycle(
                stage=stage,
                stage_cards=stage_cards,
                answers=answers,
                tensions=views,
                stale=stage_stale,
            )
        return targets

    @staticmethod
    def _with_lifecycles(
        envelope: SessionEnvelope,
        targets: Mapping[DecisionStage, LifecycleStatus],
        exclude: set[DecisionStage] | frozenset[DecisionStage] = frozenset(),
    ) -> SessionEnvelope:
        """Apply lifecycle targets inside a store.update mutator."""
        stages = dict(envelope.stages)
        for stage, lifecycle in targets.items():
            if stage in exclude:
                continue
            stages[stage] = stages[stage].model_copy(update={"lifecycle": lifecycle})
        return envelope.model_copy(update={"stages": stages})

    def _inventory_for(self, session: SessionEnvelope):  # type: ignore[no-untyped-def]
        adapter = _adapter_for(session.guidance_genre)
        inventory = adapter.inventory()
        adapter.validate_inventory(inventory)
        return inventory

    def _current_digest(self, session: SessionEnvelope) -> str:
        adapter = _adapter_for(session.guidance_genre)
        return json.dumps(adapter.tutor_session_fingerprints(), sort_keys=True, separators=(",", ":"))

    def _require_card(self, inventory, card_id: str):  # type: ignore[no-untyped-def]
        try:
            return inventory.card(card_id)
        except KeyError as exc:
            raise BeginnerWorkspaceError(f"unknown card: {card_id}") from exc

    def _stage_of(self, inventory, card_id: str) -> DecisionStage:  # type: ignore[no-untyped-def]
        from .projections import QUALIFICATION_STAGE_BY_DECISION

        card = self._require_card(inventory, card_id)
        for stage, qualification in QUALIFICATION_STAGE_BY_DECISION.items():
            if card.stage is qualification:
                return stage
        raise BeginnerWorkspaceError(f"card has no decision stage: {card_id}")

    def _require_available(self, session: SessionEnvelope, stage: DecisionStage) -> None:
        if session.stages[stage].availability is not StageAvailability.AVAILABLE:
            raise LockedStageError(f"stage is locked: {stage.value}")

    def _check_version(self, session: SessionEnvelope, expected: int) -> None:
        if session.session_version != expected:
            raise BeginnerConcurrencyError(
                f"session version mismatch: expected {expected}, found {session.session_version}"
            )

    def _coerce_stage(self, stage: DecisionStage | str) -> DecisionStage:
        if isinstance(stage, DecisionStage):
            return stage
        try:
            return DecisionStage(stage)
        except ValueError as exc:
            raise BeginnerWorkspaceError(f"unknown stage: {stage!r}") from exc

    def _cursor_card(self, session: SessionEnvelope, inventory):  # type: ignore[no-untyped-def]
        from .projections import _resolve_cursor

        answers = dict(self._journey.get("answers") or {})
        ordered = [(stage, card) for stage in STAGE_ORDER for card in cards_for_stage(inventory, stage)]
        available = {
            stage for stage in STAGE_ORDER if session.stages[stage].availability is StageAvailability.AVAILABLE
        }
        return _resolve_cursor(ordered, available, answers, self._journey.get("cursor_override"))

    @staticmethod
    def _tension_view(raw: Mapping[str, Any]) -> TensionView:
        return TensionView(
            tension_id=str(raw["tension_id"]),
            card_id=str(raw["card_id"]),
            detail=str(raw["detail"]),
            blocking=bool(raw["blocking"]),
            acknowledged=bool(raw["acknowledged"]),
        )

    # -- journey sidecar ---------------------------------------------------------

    def _default_journey(self) -> dict[str, Any]:
        return {
            "version": 1,
            "answers": {},
            "tensions": {},
            "reviews_open": [],
            "reassessed_cards": [],
            "basis_digests": {},
            "active_revision": None,
            "basis_digest": None,
            "cursor_override": None,
            "acceptance_log": [],
        }

    def _load_journey(self) -> dict[str, Any]:
        try:
            payload = json.loads(self._journey_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return self._default_journey()
        except (OSError, ValueError) as exc:
            raise BeginnerWorkspaceError(f"could not load journey state: {exc}") from exc
        if not isinstance(payload, dict):
            raise BeginnerWorkspaceError("could not load journey state: expected an object")
        journey = self._default_journey()
        journey.update({key: payload[key] for key in journey if key in payload})
        return journey

    def _save_journey(self) -> None:
        payload = json.dumps(self._journey, sort_keys=True, separators=(",", ":"))
        try:
            self._journey_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._journey_path.parent,
                prefix=f".{self._journey_path.name}.",
                delete=False,
            ) as temporary:
                temporary.write(payload)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = Path(temporary.name)
            os.replace(temporary_path, self._journey_path)
        except OSError as exc:
            raise BeginnerWorkspaceError(f"could not persist journey state: {exc}") from exc
