"""Beginner journey orchestration for the vertical slice (Task 4).

BeginnerWorkspaceApplication coordinates the Task 1-3 building blocks: the
SessionEnvelope contract, the BeginnerSessionStore/CommandReceiptStore
durability layer, and the deterministic Mystery adapter behind the guidance
registry. It owns explicit journey commands only:

- select_working_option: autosave a selection without advancing the card.
- continue_decision: advance to the next card once the current one is answered.
- open_milestone_review: open a whole-first review once every card in the
  stage is answered.
- reassess_guidance: recompute guidance from the current snapshot and refresh
  the recorded assumption basis.
- acknowledge_tension: mark a recorded contradiction as acknowledged.
- open_revision / cancel_revision: explore inside an isolated revision
  snapshot; cancelling leaves the parent session unchanged.
- request_acceptance: stage-specific readiness validation that DEFERS the
  actual canonical mutation to Task 5 (never touches canonical artifacts).

Lifecycle per stage is Working -> Review available -> Ready to accept, with
Canonical reserved for Task 5. Future stages stay availability-locked until
canonical work lands; ordinary navigation never blocks on tensions or stale
assumptions; only milestone acceptance readiness is gated by unresolved
blocking contradictions or materially stale assumptions.

Application-owned journey state (answers, tensions, open reviews, the active
revision overlay, cursor) lives in memory and is mirrored to a ``journey.json``
sidecar next to ``session.json`` for best-effort durability. The session
envelope stays authoritative for concurrency: every command validates
``expected_session_version`` against the store, and session mutations go
through ``BeginnerSessionStore.update``.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    DecisionStage,
    LifecycleStatus,
    SessionEnvelope,
    StageAvailability,
    WorkingDecision,
)
from .guidance import BeginnerGuidance, _adapter_for, guidance_for
from .persistence import (
    BeginnerConcurrencyError,
    BeginnerPersistenceError,
    BeginnerSessionStore,
    CommandReceiptStore,
)
from .projections import (
    STAGE_ORDER,
    ReviewProjection,
    RevisionProjection,
    TensionView,
    WorkspaceProjection,
    build_workspace_projection,
    cards_for_stage,
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
        card_id: str,
        option: str,
        expected_session_version: int,
        exploratory: bool = False,
    ) -> SelectResult:
        """Autosave one selection without advancing the current card."""
        session = self.session_store.load()
        inventory = self._inventory_for(session)
        card = self._require_card(inventory, card_id)
        stage = self._stage_of(inventory, card_id)
        self._require_available(session, stage)
        if option not in card.options:
            raise BeginnerWorkspaceError(f"unknown option for {card_id}: {option!r}")

        if exploratory:
            active = self._journey.get("active_revision")
            if active is None:
                raise BeginnerWorkspaceError("exploratory selection requires an active revision")
            self._check_version(session, expected_session_version)
            overlay = dict(active.get("overlay") or {})
            overlay[card_id] = option
            active["overlay"] = overlay
            self._save_journey()
            return SelectResult(
                card_id=card_id,
                selected_option=option,
                exploratory=True,
                session_version=session.session_version,
            )

        cursor = self._cursor_card(session, inventory)
        if cursor is None or cursor.card_id != card_id:
            raise BeginnerWorkspaceError(f"not the current card: {card_id}")

        def mutate(current: SessionEnvelope) -> SessionEnvelope:
            status = current.stages[stage]
            working = WorkingDecision(
                stage=stage,
                question=card.question,
                options=list(card.options),
                selected_option=option,
            )
            updated = status.model_copy(update={"lifecycle": LifecycleStatus.WORKING, "working_decision": working})
            stages = dict(current.stages)
            stages[stage] = updated
            return current.model_copy(update={"stages": stages})

        saved = self.session_store.update(expected_session_version, mutate)
        answers = dict(self._journey.get("answers") or {})
        answers[card_id] = option
        self._journey["answers"] = answers
        # Autosave pins the cursor: the current card does not advance on select.
        self._journey["cursor_override"] = card_id
        if option != card.recommendation:
            tensions = dict(self._journey.get("tensions") or {})
            tension_id = _tension_id_for(card_id)
            if tension_id not in tensions:
                tensions[tension_id] = {
                    "tension_id": tension_id,
                    "card_id": card_id,
                    "detail": (
                        f"Selected {option!r} instead of the guided recommendation "
                        f"{card.recommendation!r} for {card_id}."
                    ),
                    "blocking": True,
                    "acknowledged": False,
                }
                self._journey["tensions"] = tensions
        if self._journey.get("basis_digest") is None:
            self._journey["basis_digest"] = self._current_digest(saved)
        self._save_journey()
        return SelectResult(card_id=card_id, selected_option=option, session_version=saved.session_version)

    def continue_decision(self, *, card_id: str, expected_session_version: int) -> ContinueResult:
        """Advance past an answered card; ordinary navigation never blocks."""
        session = self.session_store.load()
        inventory = self._inventory_for(session)
        card = self._require_card(inventory, card_id)
        stage = self._stage_of(inventory, card_id)
        self._require_available(session, stage)
        cursor = self._cursor_card(session, inventory)
        if cursor is None or cursor.card_id != card_id:
            raise BeginnerWorkspaceError(f"not the current card: {card_id}")
        answers = dict(self._journey.get("answers") or {})
        if card.card_id not in answers:
            raise BeginnerWorkspaceError(f"answer the current card before continuing: {card_id}")

        stage_cards = cards_for_stage(inventory, stage)
        card_ids = [candidate.card_id for candidate in stage_cards]
        position = card_ids.index(card_id)
        if position + 1 >= len(card_ids):
            self._journey["cursor_override"] = None
            self._save_journey()
            return ContinueResult(
                card_id=card_id,
                advanced=False,
                review_available=True,
                session_version=session.session_version,
            )
        next_card = stage_cards[position + 1]

        def mutate(current: SessionEnvelope) -> SessionEnvelope:
            status = current.stages[stage]
            working = WorkingDecision(
                stage=stage,
                question=next_card.question,
                options=list(next_card.options),
                selected_option=None,
            )
            updated = status.model_copy(update={"lifecycle": LifecycleStatus.WORKING, "working_decision": working})
            stages = dict(current.stages)
            stages[stage] = updated
            return current.model_copy(update={"stages": stages})

        saved = self.session_store.update(expected_session_version, mutate)
        self._journey["cursor_override"] = next_card.card_id
        self._save_journey()
        return ContinueResult(
            card_id=next_card.card_id,
            advanced=True,
            review_available=False,
            session_version=saved.session_version,
        )

    def open_milestone_review(self, *, stage: DecisionStage | str, expected_session_version: int) -> ReviewProjection:
        """Open the whole-first review once every card in the stage is answered."""
        session = self.session_store.load()
        resolved = self._coerce_stage(stage)
        self._require_available(session, resolved)
        self._check_version(session, expected_session_version)
        projection = self.projection()
        review = projection.reviews[resolved]
        if not review.review_available:
            raise BeginnerWorkspaceError(f"review not available for {resolved.value}: answer every card first")
        opened = list(self._journey.get("reviews_open") or [])
        if resolved.value not in opened:
            opened.append(resolved.value)
            self._journey["reviews_open"] = opened
            self._save_journey()
        return self.projection().reviews[resolved]

    def reassess_guidance(self, *, card_id: str, expected_session_version: int) -> BeginnerGuidance:
        """Recompute guidance from the current snapshot and refresh assumptions."""
        session = self.session_store.load()
        inventory = self._inventory_for(session)
        self._require_card(inventory, card_id)
        self._require_available(session, self._stage_of(inventory, card_id))
        self._check_version(session, expected_session_version)
        guidance = guidance_for(card_id, session)
        self._journey["basis_digest"] = self._current_digest(session)
        reassessed = list(self._journey.get("reassessed_cards") or [])
        if card_id not in reassessed:
            reassessed.append(card_id)
        self._journey["reassessed_cards"] = reassessed
        self._save_journey()
        return guidance

    def acknowledge_tension(self, *, tension_id: str, expected_session_version: int) -> TensionView:
        """Mark a recorded tension as acknowledged; never rewrites history."""
        session = self.session_store.load()
        self._check_version(session, expected_session_version)
        tensions = dict(self._journey.get("tensions") or {})
        if tension_id not in tensions:
            raise BeginnerWorkspaceError(f"unknown tension: {tension_id}")
        tensions[tension_id] = {**tensions[tension_id], "acknowledged": True}
        self._journey["tensions"] = tensions
        self._save_journey()
        return self._tension_view(tensions[tension_id])

    def open_revision(self, *, revision_id: str, expected_session_version: int) -> RevisionProjection:
        """Snapshot the session for isolated exploration; parent stays canonical."""
        session = self.session_store.load()
        self._check_version(session, expected_session_version)
        try:
            self.session_store.save_revision(revision_id, session)
        except ValueError:
            raise
        except BeginnerPersistenceError as exc:
            raise BeginnerWorkspaceError(str(exc)) from exc
        self._journey["active_revision"] = {
            "revision_id": revision_id,
            "base_session_version": session.session_version,
            "overlay": {},
        }
        self._save_journey()
        return self.projection().revision

    def cancel_revision(self, *, expected_session_version: int) -> RevisionProjection:
        """Drop the exploration overlay; the parent session is left unchanged."""
        session = self.session_store.load()
        self._check_version(session, expected_session_version)
        if self._journey.get("active_revision") is None:
            raise BeginnerWorkspaceError("no active revision to cancel")
        self._journey["active_revision"] = None
        self._save_journey()
        return self.projection().revision

    def request_acceptance(self, *, stage: DecisionStage | str, expected_session_version: int) -> AcceptanceResult:
        """Validate readiness without mutating canonical artifacts (Task 5 owns that)."""
        session = self.session_store.load()
        resolved = self._coerce_stage(stage)
        self._require_available(session, resolved)
        self._check_version(session, expected_session_version)
        projection = self.projection()
        review = projection.reviews[resolved]
        if not review.opened:
            raise BeginnerWorkspaceError(f"open a milestone review for {resolved.value} before requesting acceptance")
        return AcceptanceResult(
            stage=resolved,
            ready=review.ready_to_accept,
            accepted=False,
            deferred_to_task_5=True,
            review_available=review.review_available,
            blockers=review.blockers,
        )

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
