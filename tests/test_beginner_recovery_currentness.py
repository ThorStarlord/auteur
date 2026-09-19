from __future__ import annotations

from typing import Any

import pytest

from auteur.beginner.application import BeginnerWorkspaceApplication, BeginnerWorkspaceError
from auteur.beginner.contracts import DimensionCategory, GuidanceActivation
from auteur.beginner.discovery import discovery_basis_fingerprint
from tests.fixtures.beginner_hybrid_mystery import (
    CountingDiscoveryRecommender,
    HYBRID_ANALYSIS,
    HYBRID_DISCOVERY,
    REVISED_HYBRID_MYSTERY_PREMISE,
    StaticArchitectureAnalyzer,
    app_after_direction_acceptance,
    app_at_discovery,
    create_hybrid_app,
)


class _ProcessCrash(BaseException):
    pass


def test_retry_after_discovery_persisted_before_receipt_completion_does_not_regenerate(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recommender = CountingDiscoveryRecommender(HYBRID_DISCOVERY)
    app = create_hybrid_app(tmp_path, discovery_recommender=recommender)
    real_complete = app.receipt_store.complete

    def crash_after_persist(*args: Any, **kwargs: Any) -> Any:
        receipt = args[0]
        if receipt.command_id == "continue-after-analysis":
            raise _ProcessCrash("process terminated after session persistence")
        return real_complete(*args, **kwargs)

    monkeypatch.setattr(app.receipt_store, "complete", crash_after_persist)

    with pytest.raises(_ProcessCrash, match="session persistence"):
        app.continue_from_architecture(
            command_id="continue-after-analysis",
            expected_session_version=app.projection().session_version,
        )

    assert recommender.calls == 1
    assert app.session_store.load().discovery_recommendation is not None

    recovered_app = BeginnerWorkspaceApplication(
        tmp_path,
        app.workspace_id,
        architecture_analyzer=StaticArchitectureAnalyzer(HYBRID_ANALYSIS),
        discovery_recommender=recommender,
    )
    recovered = recovered_app.continue_from_architecture(
        command_id="continue-after-analysis",
        expected_session_version=recovered_app.projection().session_version,
    )

    assert recovered.discovery is not None
    assert recovered.discovery.recommendation_id == HYBRID_DISCOVERY.recommendation_id
    assert recommender.calls == 1
    assert recovered_app.receipt_store.load("continue-after-analysis").status == "complete"


def test_stale_analysis_blocks_discovery_generation(tmp_path) -> None:
    app = create_hybrid_app(tmp_path)
    session = app.session_store.load()
    assert session.architecture_analysis is not None
    app.session_store.update(
        session.session_version,
        lambda current: current.model_copy(
            update={
                "architecture_analysis": current.architecture_analysis.model_copy(
                    update={"premise_fingerprint": "sha256:stale"}
                )
            }
        ),
    )

    with pytest.raises(BeginnerWorkspaceError, match="architecture analysis is stale"):
        app.continue_from_architecture(
            command_id="continue-stale-analysis",
            expected_session_version=app.projection().session_version,
        )


def test_stale_discovery_basis_blocks_story_direction_acceptance(tmp_path) -> None:
    app = app_at_discovery(tmp_path)
    app.select_story_direction(
        direction_id="direction-investigative-betrayal",
        command_id="select-before-stale",
        expected_session_version=app.projection().session_version,
    )
    session = app.session_store.load()
    composition = session.working_composition
    assert composition is not None
    target = next(
        dimension
        for dimension in composition.dimensions
        if dimension.category is DimensionCategory.SETTING_WORLD
    )
    changed = target.model_copy(update={"activation": GuidanceActivation.SUPPRESSED})
    changed_composition = composition.model_copy(
        update={
            "dimensions": tuple(
                changed if item.dimension_id == target.dimension_id else item
                for item in composition.dimensions
            )
        }
    )
    app.session_store.update(
        session.session_version,
        lambda current: current.model_copy(
            update={"working_composition": changed_composition}
        ),
    )

    with pytest.raises(BeginnerWorkspaceError, match="discovery recommendation is stale"):
        app.accept_story_direction(
            command_id="accept-stale-direction",
            expected_session_version=app.projection().session_version,
        )


def test_discovery_basis_ignores_session_version_but_tracks_material_composition(tmp_path) -> None:
    app = create_hybrid_app(tmp_path)
    session = app.session_store.load()
    basis = discovery_basis_fingerprint(
        session.architecture_analysis,
        session.working_composition,
    )
    version_only = session.model_copy(update={"session_version": session.session_version + 99})
    assert discovery_basis_fingerprint(
        version_only.architecture_analysis,
        version_only.working_composition,
    ) == basis

    composition = session.working_composition
    target = composition.dimensions[0]
    changed = target.model_copy(update={"activation": GuidanceActivation.SUPPRESSED})
    changed_composition = composition.model_copy(
        update={
            "dimensions": (
                changed,
                *composition.dimensions[1:],
            )
        }
    )
    assert discovery_basis_fingerprint(
        session.architecture_analysis,
        changed_composition,
    ) != basis


def test_post_identity_reanalysis_requires_identity_revision(tmp_path) -> None:
    app = app_after_direction_acceptance(tmp_path)
    app.accept_story_identity(
        command_id="accept-original-identity",
        expected_session_version=app.projection().session_version,
    )
    with pytest.raises(BeginnerWorkspaceError, match="revision-overlay"):
        app.reanalyze_premise(
            premise=REVISED_HYBRID_MYSTERY_PREMISE,
            command_id="direct-post-identity-reanalysis",
            expected_session_version=app.projection().session_version,
        )


def test_identity_revision_reanalysis_is_isolated_until_authority_acceptance(tmp_path) -> None:
    app = app_after_direction_acceptance(tmp_path)
    app.accept_story_identity(
        command_id="accept-original-identity",
        expected_session_version=app.projection().session_version,
    )
    parent_before = app.session_store.load()
    original_premise = parent_before.premise
    original_analysis = parent_before.architecture_analysis.model_dump_json()

    app.open_revision(
        revision_id="identity-architecture-revision",
        stage="story_identity",
        command_id="open-identity-architecture-revision",
        expected_session_version=app.projection().session_version,
    )
    app.reanalyze_premise(
        premise=REVISED_HYBRID_MYSTERY_PREMISE,
        command_id="reanalyze-in-identity-revision",
        expected_session_version=app.projection().session_version,
    )

    parent_during = app.session_store.load()
    assert parent_during.premise == original_premise
    assert parent_during.architecture_analysis.model_dump_json() == original_analysis
    active = app._journey["active_revision"]
    assert active["premise"] == REVISED_HYBRID_MYSTERY_PREMISE
    assert active["architecture_analysis"]["premise_fingerprint"] != parent_before.architecture_analysis.premise_fingerprint
    assert app.projection().story_orientation.summary

    app.cancel_revision(
        command_id="cancel-identity-architecture-revision",
        expected_session_version=app.projection().session_version,
    )
    parent_after = app.session_store.load()
    assert parent_after.premise == original_premise
    assert parent_after.architecture_analysis.model_dump_json() == original_analysis
