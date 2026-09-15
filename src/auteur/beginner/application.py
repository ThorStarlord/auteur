"""Beginner journey orchestration for the vertical slice (Task 4).

BeginnerWorkspaceApplication coordinates the Task 1-3 building blocks: the
SessionEnvelope contract, the BeginnerSessionStore/CommandReceiptStore
durability layer, and the deterministic Mystery adapter behind the guidance
registry. It owns explicit journey commands only:

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
  actual canonical mutation to Task 5 (never touches canonical artifacts).
  Task 5 owns the ``accept_milestone`` naming; this entry point intentionally
  keeps the ``request_acceptance``/``AcceptanceResult`` names.

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
``create_workspace`` type label; widening ``BeginnerCommandType`` with
per-command types is the intended follow-up, not a behavior change here.

Lifecycle per stage is Working -> Review available -> Ready to accept, with
Canonical reserved for Task 5. The persisted session lifecycle mapping is
``WORKING`` (still answering), ``BLOCKED`` (all answered but acceptance
gated), ``COMPLETE`` (review available and ready to accept); locked stages
keep ``NOT_STARTED``. Availability (``AVAILABLE``/``LOCKED``) is never derived
from or mixed into lifecycle. Future stages stay availability-locked until
canonical work lands; ordinary navigation never blocks on tensions or stale
assumptions; only milestone acceptance readiness is gated by unresolved
blocking contradictions or materially stale assumptions.

Tension kinds: a non-recommended selection records a *blocking contradiction*
against guidance (must be acknowledged before acceptance); exploratory
divergence inside a revision records a *nonblocking authorial tension* (never
gates readiness, discarded with the revision on cancel).

Application-owned journey state (answers, tensions, open reviews, the active
revision overlay, per-card digests, cursor) lives in memory and is mirrored to
a ``journey.json`` sidecar next to ``session.json`` for best-effort
durability. The session envelope stays authoritative for concurrency: every
mutating command validates ``expected_session_version`` and persists through
``BeginnerSessionStore.update``, so journey-sidecar writes also advance
``session_version`` atomically and concurrent actors cannot lost-update.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, cast

from .contracts import (
    DecisionStage,
    LifecycleStatus,
    MutationCommand,
    SessionEnvelope,
    StageAvailability,
    WorkingDecision,
)
from .guidance import BeginnerGuidance, QualificationStage, _adapter_for, guidance_for
from .persistence import (
    BeginnerConcurrencyError,
    BeginnerPersistenceError,
    BeginnerSessionStore,
    CommandReceiptStore,
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
                    "question": summary.question,
                    "selected_option": summary.selected_option,
                    "recommendation": summary.recommendation,
                    "follows_recommendation": summary.follows_recommendation,
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
            question=str(item["question"]),
            selected_option=None if item["selected_option"] is None else str(item["selected_option"]),
            recommendation=str(item["recommendation"]),
            follows_recommendation=bool(item["follows_recommendation"]),
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
        },
    }


def _thaw_revision(data: Mapping[str, Any]) -> RevisionProjection:
    raw_stages = data["at_risk_stages"]
    assert isinstance(raw_stages, list)
    raw_base = data["base_session_version"]
    raw_active = data["active_revision_id"]
    return RevisionProjection(
        active_revision_id=None if raw_active is None else str(raw_active),
        is_exploration=bool(data["is_exploration"]),
        at_risk_stages=tuple(DecisionStage(str(stage)) for stage in raw_stages),
        base_session_version=None if raw_base is None else int(raw_base),
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


class BeginnerWorkspaceApplication:
    """Explicit journey commands over the beginner session and its stores."""

    def __init__(self, project_root: Path | str, workspace_id: str) -> None:
        self.session_store = BeginnerSessionStore(Path(project_root), workspace_id)
        self.receipt_store = CommandReceiptStore(Path(project_root), workspace_id)
        self.workspace_id = workspace_id
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
        resolved_exploratory = exploratory or bool(payload.get("exploratory", False))
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
                    "blocking": True,
                    "acknowledged": False,
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
        self.session_store.update(expected, lambda current: self._with_lifecycles(current, targets))
        self._journey["tensions"] = new_tensions
        self._save_journey()
        result = self._tension_view(new_tensions[resolved_tension_id])
        self._complete_command(resolved_command_id, "acknowledge", _freeze_tension(result))
        return result

    def open_revision(
        self,
        *,
        revision_id: str | None = None,
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
        }
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
