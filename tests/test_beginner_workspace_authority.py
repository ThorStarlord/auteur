"""Task 5: Beginner milestone acceptance delegates to authority services.

Covers the approved vertical-slice authority behaviors:

- Accept Story Direction creates an accepted direction record only and never
  creates canonical StoryIdentity.
- Accept Story Identity / Whole-Story Structure delegate to the acceptance /
  promotion seam with same-command_id idempotency: receipt begin happens before
  crossing the authority boundary, the result reference is persisted, the
  session is reconciled, and the receipt is marked complete.
- A failed promotion preserves the previous canon (atomic, no partial write).
- Replaying a promotion command_id returns the same result without duplicating
  acceptance (promotion_count == 1).
- Only an accepted revision stales downstream through the existing freshness
  propagation; exploring a revision stays at-risk without staleness.
- Crash recovery: a retry after domain promotion but before session
  persistence reconciles the session without promoting twice.

Optimistic concurrency, the combined projection, and lifecycle-to-Canonical
(COMPLETE plus a recorded acceptance reference) carry over from Task 4.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from auteur.acceptance import AcceptanceRegistry
from auteur.beginner.application import BeginnerWorkspaceApplication
from auteur.beginner.contracts import DecisionStage, LifecycleStatus, StageAvailability
from auteur.beginner.mystery_adapter import mystery_qualification_inventory
from auteur.beginner.persistence import BeginnerConcurrencyError


def make_app(
    tmp_path: Path,
    workspace_id: str = "workspace-1",
    registry: AcceptanceRegistry | None = None,
) -> BeginnerWorkspaceApplication:
    kwargs: dict[str, Any] = {}
    if registry is not None:
        kwargs["authority_registry"] = registry
    app = BeginnerWorkspaceApplication(tmp_path, workspace_id, **kwargs)
    app.create_workspace(
        command_id=f"create-{workspace_id}",
        project_id="project-1",
        premise="A sealed elevator opens on an empty shaft.",
        guidance_genre="mystery",
    )
    return app


def stage_cards(prefix: str) -> list[str]:
    inventory = mystery_qualification_inventory()
    return [card.card_id for card in inventory.cards if card.card_id.startswith(prefix)]


def answer_stage_cleanly(app: BeginnerWorkspaceApplication, prefix: str) -> None:
    """Answer every card of one stage with its recommendation, in order."""
    inventory = mystery_qualification_inventory()
    cards = [card.card_id for card in inventory.cards if card.card_id.startswith(prefix)]
    for position, card_id in enumerate(cards):
        card = inventory.card(card_id)
        app.select_working_option(
            card_id=card_id,
            option=card.recommendation,
            expected_session_version=app.projection().session_version,
        )
        if position + 1 < len(cards):
            app.continue_decision(
                card_id=card_id,
                expected_session_version=app.projection().session_version,
            )


def accept_direction(app: BeginnerWorkspaceApplication, command_id: str = "accept-direction-1"):
    answer_stage_cleanly(app, "discover.")
    app.open_milestone_review(
        stage=DecisionStage.DISCOVER,
        expected_session_version=app.projection().session_version,
    )
    return app.accept_story_direction(
        command_id=command_id,
        expected_session_version=app.projection().session_version,
    )


def accept_identity(app: BeginnerWorkspaceApplication, command_id: str = "accept-identity-1"):
    answer_stage_cleanly(app, "story_identity.")
    app.open_milestone_review(
        stage=DecisionStage.STORY_IDENTITY,
        expected_session_version=app.projection().session_version,
    )
    return app.accept_story_identity(
        command_id=command_id,
        expected_session_version=app.projection().session_version,
    )


class CountingOwner:
    """Test authority owner: pure result, counts real invocations."""

    def __init__(self, fail_on: tuple[str, ...] = ()) -> None:
        self.calls: list[tuple[str, str, bool]] = []
        self.fail_on = fail_on

    def can_accept(self, target_artifact_id: str) -> bool:
        return target_artifact_id.startswith("beginner:")

    def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> dict[str, Any]:
        self.calls.append((target_artifact_id, candidate_id, confirm))
        if target_artifact_id.rsplit(":", 1)[-1] in self.fail_on:
            raise RuntimeError("promotion write interrupted")
        return {"artifact_id": target_artifact_id, "candidate_id": candidate_id, "accepted": True}


def test_accept_direction_records_direction_only_never_identity(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    result = accept_direction(app)

    assert result.accepted is True
    assert result.revision == 1
    session = app.session_store.load()
    milestone_ids = [ref.milestone_id for ref in session.accepted_milestones]
    assert milestone_ids == ["story_direction"]
    assert "story_identity" not in milestone_ids
    assert "whole_story_structure" not in milestone_ids
    # No canonical StoryIdentity artifact may appear anywhere under .auteur.
    identity_files = [
        path
        for path in (tmp_path / ".auteur").rglob("*")
        if "story_identity" in path.name and path.name not in {"session.json", "journey.json"}
        and "commands" not in path.parts
    ]
    assert identity_files == []
    # Reconciliation unlocks the next stage and marks direction Canonical.
    assert session.stages[DecisionStage.DISCOVER].lifecycle is LifecycleStatus.COMPLETE
    assert session.stages[DecisionStage.STORY_IDENTITY].availability is StageAvailability.AVAILABLE
    assert session.stages[DecisionStage.STORY_STRUCTURE].availability is StageAvailability.LOCKED
    assert app.projection().canonical_refs[0].milestone_id == "story_direction"


def test_failed_promotion_preserves_previous_canon(tmp_path: Path) -> None:
    owner = CountingOwner(fail_on=("story_identity",))
    registry = AcceptanceRegistry(tmp_path)
    registry.register(owner)
    app = make_app(tmp_path, registry=registry)
    accept_direction(app)
    canon_before = list(app.session_store.load().accepted_milestones)
    refs_before = list(app.projection().canonical_refs)

    answer_stage_cleanly(app, "story_identity.")
    app.open_milestone_review(
        stage=DecisionStage.STORY_IDENTITY,
        expected_session_version=app.projection().session_version,
    )
    with pytest.raises(RuntimeError, match="promotion write interrupted"):
        app.accept_story_identity(
            command_id="accept-identity-fails",
            expected_session_version=app.projection().session_version,
        )

    session = app.session_store.load()
    assert list(session.accepted_milestones) == canon_before
    assert [ref.milestone_id for ref in session.accepted_milestones] == ["story_direction"]
    assert list(app.projection().canonical_refs) == refs_before
    # The failed command is recorded so the same command_id replays the failure
    # instead of silently promoting on retry; a fresh command retries cleanly.
    replayed_failure = app.accept_story_identity(
        command_id="accept-identity-fails",
        expected_session_version=app.projection().session_version,
    )
    assert replayed_failure.accepted is False
    assert "promotion write interrupted" in (replayed_failure.error or "")
    assert len(owner.calls) == 2

    owner.fail_on = ()
    retry_owner_calls_before = len(owner.calls)
    retry = app.accept_story_identity(
        command_id="accept-identity-retry",
        expected_session_version=app.projection().session_version,
    )
    assert retry.accepted is True
    assert len(owner.calls) == retry_owner_calls_before + 1
    assert [ref.milestone_id for ref in app.session_store.load().accepted_milestones] == [
        "story_direction",
        "story_identity",
    ]


def test_replayed_promotion_returns_same_result_without_duplicate(tmp_path: Path) -> None:
    owner = CountingOwner()
    registry = AcceptanceRegistry(tmp_path)
    registry.register(owner)
    app = make_app(tmp_path, registry=registry)
    accept_direction(app)
    accept_identity(app, command_id="accept-identity-1")

    def identity_promotions() -> int:
        return sum(1 for call in owner.calls if call[0].endswith("story_identity"))

    assert identity_promotions() == 1
    version_after_accept = app.projection().session_version

    replayed = app.accept_story_identity(
        command_id="accept-identity-1",
        expected_session_version=app.projection().session_version,
    )
    assert replayed.accepted is True
    assert replayed.revision == 1
    assert identity_promotions() == 1, "replay must not invoke the authority owner again"
    assert app.projection().session_version == version_after_accept
    assert [ref.milestone_id for ref in app.session_store.load().accepted_milestones].count(
        "story_identity"
    ) == 1


def test_accepted_revision_stales_downstream_but_exploration_does_not(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    accept_direction(app)
    accept_identity(app, command_id="accept-identity-1")
    answer_stage_cleanly(app, "structure.")

    app.open_revision(
        revision_id="revision-identity-2",
        expected_session_version=app.projection().session_version,
    )
    identity_cards = stage_cards("story_identity.")
    app.select_working_option(
        card_id=identity_cards[0],
        option=mystery_qualification_inventory().card(identity_cards[0]).options[-1],
        expected_session_version=app.projection().session_version,
        exploratory=True,
    )

    exploring = app.projection()
    downstream = [entry for entry in exploring.navigator if entry.stage is not DecisionStage.DISCOVER]
    assert downstream, "expected downstream stages in navigator"
    assert any(entry.at_risk_if_accepted for entry in downstream)
    for entry in exploring.navigator:
        assert entry.stale is False, "exploration must stay at-risk, never stale"

    before = app.session_store.load()
    identity_refs_before = [
        ref for ref in before.accepted_milestones if ref.milestone_id == "story_identity"
    ]
    assert len(identity_refs_before) == 1

    result = app.accept_revised_story_identity(
        revision_id="revision-identity-2",
        command_id="accept-identity-rev2",
        expected_session_version=app.projection().session_version,
    )
    assert result.accepted is True
    assert result.revision == 2

    after = app.session_store.load()
    identity_refs = [ref for ref in after.accepted_milestones if ref.milestone_id == "story_identity"]
    assert len(identity_refs) == 2, "previous canonical version must be preserved in provenance"
    assert identity_refs[0].revision.revision == 1
    assert identity_refs[1].revision.revision == 2

    staled = app.projection()
    assert staled.revision.active_revision_id is None
    structure_entry = next(entry for entry in staled.navigator if entry.stage is DecisionStage.STORY_STRUCTURE)
    assert structure_entry.stale is True, "accepting the revision must stale downstream"
    assert structure_entry.at_risk_if_accepted is False


def test_crash_after_promotion_reconciles_without_repromoting(tmp_path: Path) -> None:
    owner = CountingOwner()
    registry = AcceptanceRegistry(tmp_path)
    registry.register(owner)
    app = make_app(tmp_path, registry=registry)
    accept_direction(app)
    answer_stage_cleanly(app, "story_identity.")
    app.open_milestone_review(
        stage=DecisionStage.STORY_IDENTITY,
        expected_session_version=app.projection().session_version,
    )

    real_update = app.session_store.update

    def crash_once(expected: int, mutator):  # type: ignore[no-untyped-def]
        app.session_store.update = real_update  # type: ignore[method-assign]
        raise RuntimeError("crash before session persistence")

    app.session_store.update = crash_once  # type: ignore[method-assign]
    with pytest.raises(RuntimeError, match="crash before session persistence"):
        app.accept_story_identity(
            command_id="accept-identity-crash",
            expected_session_version=app.projection().session_version,
        )

    def identity_promotions() -> int:
        return sum(1 for call in owner.calls if call[0].endswith("story_identity"))

    assert identity_promotions() == 1, "domain promotion ran exactly once before the crash"
    assert "story_identity" not in [
        ref.milestone_id for ref in app.session_store.load().accepted_milestones
    ]

    recovered = app.accept_story_identity(
        command_id="accept-identity-crash",
        expected_session_version=app.projection().session_version,
    )
    assert recovered.accepted is True
    assert len(owner.calls) == 2, "recovery must reconcile without promoting twice"
    assert identity_promotions() == 1
    assert "story_identity" in [
        ref.milestone_id for ref in app.session_store.load().accepted_milestones
    ]

    # A later replay still returns the recorded result without further promotion.
    replayed = app.accept_story_identity(
        command_id="accept-identity-crash",
        expected_session_version=app.projection().session_version,
    )
    assert replayed.accepted is True
    assert identity_promotions() == 1


def test_stale_session_version_rejects_before_promotion(tmp_path: Path) -> None:
    owner = CountingOwner()
    registry = AcceptanceRegistry(tmp_path)
    registry.register(owner)
    app = make_app(tmp_path, registry=registry)
    accept_direction(app)
    accept_identity(app, command_id="accept-identity-1")
    calls_after_identity = len(owner.calls)

    with pytest.raises(BeginnerConcurrencyError):
        app.accept_whole_story_structure(
            command_id="accept-structure-stale",
            expected_session_version=0,
        )
    assert len(owner.calls) == calls_after_identity, "stale commands must not cross the boundary"
