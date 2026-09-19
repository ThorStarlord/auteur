from __future__ import annotations

from auteur.beginner.architecture_projection import build_story_orientation
from tests.fixtures.beginner_hybrid_mystery import HYBRID_ANALYSIS, create_hybrid_app


def test_story_orientation_leads_with_architecture_not_stage_counts() -> None:
    projection = build_story_orientation(
        analysis=HYBRID_ANALYSIS,
        analysis_current=True,
        accepted_milestones=(),
    )
    assert projection is not None
    assert projection.heading == "Here is what Auteur sees"
    assert projection.summary == "A superhero relationship-betrayal mystery."
    assert projection.authority_status == "DERIVED / NOT CANON"
    assert projection.next_action_label == "Continue with this interpretation"


def test_story_map_and_navigator_share_component_ids(tmp_path) -> None:
    app = create_hybrid_app(tmp_path)
    projection = app.projection()
    assert projection.story_orientation is not None
    compact = {
        item.component_id
        for facet in projection.story_orientation.navigator_facets
        for item in facet.components
    }
    expanded = {
        item.component_id
        for facet in projection.story_orientation.story_map_facets
        for item in facet.components
    }
    assert compact <= expanded
    assert compact


def test_suppressed_uncertainty_stays_in_story_map_but_not_compact_navigator() -> None:
    projection = build_story_orientation(
        analysis=HYBRID_ANALYSIS,
        analysis_current=True,
        accepted_milestones=(),
    )
    assert projection is not None
    compact_labels = {
        item.label
        for facet in projection.navigator_facets
        for item in facet.components
    }
    expanded_labels = {
        item.label
        for facet in projection.story_map_facets
        for item in facet.components
    }
    assert "Erotic betrayal melodrama" not in compact_labels
    assert "Erotic betrayal melodrama" in expanded_labels
