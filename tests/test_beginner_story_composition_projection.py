from __future__ import annotations

from auteur.beginner.architecture_projection import build_story_orientation
from tests.fixtures.beginner_hybrid_mystery import HYBRID_ANALYSIS


def test_story_orientation_explains_how_detected_dimensions_compose() -> None:
    orientation = build_story_orientation(
        analysis=HYBRID_ANALYSIS,
        analysis_current=True,
        accepted_milestones=(),
    )
    assert orientation is not None

    composition = orientation.composition
    assert composition.main_story_machinery == ("Investigation and revelation",)
    assert composition.genre_traditions == ("Mystery", "Superhero fiction")
    assert "Secret identity" in composition.trope_families
    assert composition.relationship_dynamics == ("Relationship betrayal",)
    # The fixture intentionally keeps its uncertain framing suppressed. The
    # explanation must expose that absence rather than manufacture a style.
    assert composition.aesthetic_framing == ()
    assert "Aesthetic framing is not yet established" in composition.synthesis
    assert "Narrative structure is not established yet" in composition.structure_status
    assert "Secret identity" in composition.synthesis
    assert "Relationship betrayal" in composition.synthesis
