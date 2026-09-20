from __future__ import annotations

import json

from auteur.beginner.architecture_models import ArchitectureRole
from auteur.beginner.architecture_analysis import premise_fingerprint
from auteur.beginner.contracts import GuidanceActivation
from tests.fixtures.beginner_hybrid_mystery import (
    REVISED_HYBRID_MYSTERY_PREMISE,
    app_at_discovery,
    create_hybrid_app,
)


def _component(projection, label: str):
    assert projection.story_orientation is not None
    return next(
        item
        for facet in projection.story_orientation.story_map_facets
        for item in facet.components
        if item.label == label
    )


def test_suppressing_superhero_changes_guidance_without_touching_canon(tmp_path) -> None:
    app = create_hybrid_app(tmp_path)
    before = app.projection()
    superhero = _component(before, "Superhero fiction")
    app.suppress_architecture_component(
        component_id=superhero.component_id,
        rationale="Keep powers as background only.",
        command_id="suppress-superhero",
        expected_session_version=before.session_version,
    )
    after = app.projection()
    superhero_after = next(
        item
        for facet in after.story_orientation.story_map_facets
        for item in facet.components
        if item.component_id == superhero.component_id
    )
    active_labels = {
        dimension.label
        for dimension in after.working_composition.dimensions
        if dimension.activation is GuidanceActivation.ACTIVE
    }
    assert superhero_after.activation == "suppressed"
    assert "Superhero fiction" not in active_labels
    assert after.canonical_refs == ()


def test_choose_ambiguous_alternative_is_working_only(tmp_path) -> None:
    app = create_hybrid_app(tmp_path)
    framing = _component(app.projection(), "Erotic betrayal melodrama")
    app.choose_architecture_alternative(
        component_id=framing.component_id,
        alternative_label="Campy erotic melodrama",
        rationale="Use the more theatrical framing.",
        command_id="choose-campy-framing",
        expected_session_version=app.projection().session_version,
    )
    projection = app.projection()
    updated = _component(projection, "Campy erotic melodrama")
    assert updated.activation == "active"
    assert "Campy erotic melodrama" in {
        dimension.label for dimension in projection.working_composition.dimensions
    }
    assert projection.canonical_refs == ()


def test_reducing_component_to_flavor_removes_it_from_working_composition(tmp_path) -> None:
    app = create_hybrid_app(tmp_path)
    superhero = _component(app.projection(), "Superhero fiction")
    app.set_architecture_component_role(
        component_id=superhero.component_id,
        role=ArchitectureRole.FLAVOR,
        rationale="Keep superhero elements as background flavor.",
        command_id="reduce-superhero",
        expected_session_version=app.projection().session_version,
    )
    projection = app.projection()
    assert "Superhero fiction" not in {
        dimension.label for dimension in projection.working_composition.dimensions
    }
    assert projection.canonical_refs == ()


def test_refinement_invalidates_discovery_and_records_supersession(tmp_path) -> None:
    app = app_at_discovery(tmp_path)
    before = app.session_store.load()
    assert before.discovery_recommendation is not None
    old_id = before.discovery_recommendation.recommendation_id
    superhero = next(
        component
        for component in before.architecture_analysis.components
        if component.label == "Superhero fiction"
    )
    app.suppress_architecture_component(
        component_id=superhero.component_id,
        rationale="Test a version where superhero context is background only.",
        command_id="suppress-after-discovery",
        expected_session_version=app.projection().session_version,
    )
    changed = app.session_store.load()
    assert changed.discovery_recommendation is None
    assert (
        changed.architecture_analysis.adjustments[-1].invalidated_discovery_recommendation_id
        == old_id
    )
    refreshed = app.continue_from_architecture(
        command_id="regenerate-after-refinement",
        expected_session_version=app.projection().session_version,
    )
    assert refreshed.discovery is not None
    assert refreshed.discovery.supersedes_recommendation_id == old_id


def test_pre_identity_premise_reanalysis_invalidates_old_discovery(tmp_path) -> None:
    app = app_at_discovery(tmp_path)
    old_id = app.session_store.load().discovery_recommendation.recommendation_id
    app.reanalyze_premise(
        premise=REVISED_HYBRID_MYSTERY_PREMISE,
        command_id="reanalyze",
        expected_session_version=app.projection().session_version,
    )
    session = app.session_store.load()
    assert session.premise == REVISED_HYBRID_MYSTERY_PREMISE
    assert session.discovery_recommendation is None
    assert (
        session.architecture_analysis.premise_fingerprint
        == premise_fingerprint(REVISED_HYBRID_MYSTERY_PREMISE)
    )
    assert old_id not in json.dumps(session.model_dump(mode="json"))
