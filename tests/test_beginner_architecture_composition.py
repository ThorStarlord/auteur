from __future__ import annotations

from auteur.beginner.architecture_models import ArchitectureActivation, ArchitectureFacet
from auteur.beginner.contracts import GuidanceActivation
from auteur.beginner.dimensions import active_dimensions, composition_from_analysis
from auteur.beginner.discovery import UnavailableDiscoveryRecommender
from auteur.blueprint import TargetExperience
from tests.fixtures.beginner_hybrid_mystery import (
    HYBRID_ANALYSIS,
    HYBRID_DISCOVERY,
    CountingDiscoveryRecommender,
    create_hybrid_app,
)


def test_clear_or_likely_inferred_dimensions_are_active_without_author_confirmation() -> None:
    composition = composition_from_analysis(
        workspace_id="hybrid",
        analysis=HYBRID_ANALYSIS,
        prior=None,
    )
    superhero = next(d for d in composition.dimensions if d.label == "Superhero public identity")
    assert superhero.activation is GuidanceActivation.ACTIVE
    assert superhero.confirmed_by_author is False


def test_uncertain_consequential_component_does_not_silently_enter_working_composition() -> None:
    framing = next(
        component
        for component in HYBRID_ANALYSIS.components
        if component.facet is ArchitectureFacet.AESTHETIC_FRAMING
    )
    assert framing.activation is ArchitectureActivation.SUPPRESSED
    composition = composition_from_analysis(
        workspace_id="hybrid",
        analysis=HYBRID_ANALYSIS,
        prior=None,
    )
    assert "Erotic betrayal melodrama" not in {dimension.label for dimension in composition.dimensions}


def test_active_unconfirmed_dimension_changes_guidance_but_not_canon(tmp_path) -> None:
    app = create_hybrid_app(
        tmp_path,
        discovery_recommender=UnavailableDiscoveryRecommender(
            reason="No reasoning provider configured."
        ),
    )
    architecture = app.projection()
    assert architecture.primary_surface == "architecture"
    assert architecture.guidance_inspector is None

    projection = app.continue_from_architecture(
        command_id="continue-to-degraded-discovery",
        expected_session_version=architecture.session_version,
    )
    assert projection.guidance_inspector is not None
    assert "Superhero public identity" in projection.guidance_inspector.context_guidance.patterns
    assert projection.canonical_refs == ()
    assert not (tmp_path / "story_identity.yaml").exists()


def test_active_dimensions_ignore_review_status_but_respect_activation() -> None:
    composition = composition_from_analysis(
        workspace_id="hybrid",
        analysis=HYBRID_ANALYSIS,
        prior=None,
    )
    active = active_dimensions(composition)
    assert active
    assert all(item.activation is GuidanceActivation.ACTIVE for item in active)
    assert any(item.confirmed_by_author is False for item in active)


def test_projected_composition_tension_has_a_valid_acknowledgement_path(tmp_path) -> None:
    """Regression: a tension that exists only in the refreshed projection must be
    acknowledgeable, otherwise Identity acceptance is blocked with no mutation path."""
    base_direction = HYBRID_DISCOVERY.directions[0]
    tension_direction = base_direction.model_copy(
        update={
            "identity_candidate": base_direction.identity_candidate.model_copy(
                update={
                    "target_experience": TargetExperience(
                        primary="dread",
                        progression="rising",
                        avoid=[],
                    )
                }
            )
        }
    )
    recommendation = HYBRID_DISCOVERY.model_copy(
        update={"directions": (tension_direction, *HYBRID_DISCOVERY.directions[1:])}
    )
    app = create_hybrid_app(
        tmp_path,
        discovery_recommender=CountingDiscoveryRecommender(recommendation),
    )
    app.continue_from_architecture(
        command_id="tension-continue",
        expected_session_version=app.projection().session_version,
    )
    app.select_story_direction(
        direction_id=tension_direction.direction_id,
        command_id="tension-select",
        expected_session_version=app.projection().session_version,
    )
    app.accept_story_direction(
        command_id="tension-accept-direction",
        expected_session_version=app.projection().session_version,
    )

    projection = app.projection()
    assert projection.mapping_preview is not None
    assert "tension_requires_acknowledgement" in projection.mapping_preview.blocking_items
    composition_tension = projection.working_composition.tensions[0]

    app.acknowledge_tension(
        tension_id=composition_tension.tension_id,
        command_id="tension-acknowledge",
        expected_session_version=projection.session_version,
    )

    after = app.projection()
    assert after.mapping_preview is not None
    assert "tension_requires_acknowledgement" not in after.mapping_preview.blocking_items
    assert {ref.milestone_id for ref in after.canonical_refs} == {"story_direction"}
