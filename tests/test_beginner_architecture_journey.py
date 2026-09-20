from __future__ import annotations

from auteur.beginner.contracts import DecisionStage, StageAvailability
from tests.fixtures.beginner_hybrid_mystery import (
    CountingDiscoveryRecommender,
    HYBRID_DISCOVERY,
    app_at_discovery,
    create_hybrid_app,
)


def test_fresh_workspace_starts_with_architecture_not_discovery_card(tmp_path) -> None:
    app = create_hybrid_app(tmp_path)
    projection = app.projection()
    assert projection.story_orientation is not None
    assert projection.primary_surface == "architecture"
    assert projection.discovery is None
    assert projection.decision_card is None


def test_continue_from_architecture_generates_discovery_once(tmp_path) -> None:
    recommender = CountingDiscoveryRecommender(HYBRID_DISCOVERY)
    app = create_hybrid_app(tmp_path, discovery_recommender=recommender)
    result = app.continue_from_architecture(
        command_id="continue-architecture",
        expected_session_version=app.projection().session_version,
    )
    assert recommender.calls == 1
    assert result.primary_surface == "discovery"
    assert result.discovery is not None
    assert result.discovery.recommended_direction_id == "direction-investigative-betrayal"
    assert result.decision_card is None

    replay = app.continue_from_architecture(
        command_id="continue-architecture",
        expected_session_version=result.session_version,
    )
    assert recommender.calls == 1
    assert replay.discovery is not None


def test_select_direction_is_noncanonical_and_projects_selection(tmp_path) -> None:
    app = app_at_discovery(tmp_path)
    projection = app.select_story_direction(
        direction_id="direction-investigative-betrayal",
        command_id="select-direction",
        expected_session_version=app.projection().session_version,
    )
    assert projection.discovery is not None
    assert projection.discovery.selected_direction_id == "direction-investigative-betrayal"
    assert projection.canonical_refs == ()
    assert not (tmp_path / "story_identity.yaml").exists()


def test_accept_direction_unlocks_identity_without_writing_story_identity(tmp_path) -> None:
    app = app_at_discovery(tmp_path)
    app.select_story_direction(
        direction_id="direction-investigative-betrayal",
        command_id="select-direction",
        expected_session_version=app.projection().session_version,
    )
    result = app.accept_story_direction(
        command_id="accept-direction",
        expected_session_version=app.projection().session_version,
    )
    assert result.accepted is True
    assert not (tmp_path / "story_identity.yaml").exists()
    session = app.session_store.load()
    assert session.stages[DecisionStage.STORY_IDENTITY].availability is StageAvailability.AVAILABLE
    projection = app.projection()
    assert projection.primary_surface == "story_identity"
    assert projection.identity_candidate is not None
    assert projection.identity_candidate.direction_id == "direction-investigative-betrayal"
    assert projection.decision_card is None


def test_nonrecommended_selection_records_nonblocking_authorial_divergence(tmp_path) -> None:
    app = app_at_discovery(tmp_path)
    app.select_story_direction(
        direction_id="direction-relationship-drama",
        command_id="select-alt-direction",
        expected_session_version=app.projection().session_version,
    )
    assert any(
        tension.get("source") == "discovery-selection" and tension.get("blocking") is False
        for tension in app._journey["tensions"].values()
    )
