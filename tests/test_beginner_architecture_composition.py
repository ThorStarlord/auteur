from __future__ import annotations

from auteur.beginner.architecture_models import ArchitectureActivation, ArchitectureFacet
from auteur.beginner.contracts import GuidanceActivation
from auteur.beginner.dimensions import active_dimensions, composition_from_analysis
from tests.fixtures.beginner_hybrid_mystery import HYBRID_ANALYSIS, create_hybrid_app


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
    app = create_hybrid_app(tmp_path)
    projection = app.projection()
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
