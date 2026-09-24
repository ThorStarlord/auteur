from __future__ import annotations

from auteur.beginner.architecture_analysis import (
    DeterministicArchitectureAnalyzer,
    confirm_component,
    rename_component,
)
from auteur.beginner.story_lenses import (
    StoryLensState,
    StoryLensType,
    build_story_lenses,
)
from tests.fixtures.beginner_hybrid_mystery import (
    HYBRID_ANALYSIS,
    create_hybrid_app,
)


EXPECTED_LENS_ORDER = (
    "story_engine",
    "aesthetic_framing",
    "common_tropes",
    "structural_shape",
    "reader_experience",
)


def _by_id(lenses):
    return {lens.lens_id: lens for lens in lenses}


def test_story_lens_contract_projects_five_connected_default_lenses() -> None:
    lenses, diagnostics = build_story_lenses(
        analysis=HYBRID_ANALYSIS,
        analysis_current=True,
    )

    assert tuple(lens.lens_id for lens in lenses) == EXPECTED_LENS_ORDER
    by_id = _by_id(lenses)

    assert by_id["story_engine"].summary == "Investigation and revelation"
    assert by_id["story_engine"].state is StoryLensState.INFERRED
    assert by_id["aesthetic_framing"].state is StoryLensState.UNESTABLISHED
    assert by_id["aesthetic_framing"].items[0].activation == "suppressed"
    assert "Secret identity" in {
        item.label for item in by_id["common_tropes"].items
    }
    assert by_id["structural_shape"].summary == "Progressive revelation"
    assert "question" in by_id["structural_shape"].detail.casefold()
    assert by_id["reader_experience"].summary.startswith("Curiosity")
    assert by_id["structural_shape"].refinement_mode == "through_sources"

    assert diagnostics.source_mode == "provider"
    assert diagnostics.stale is False
    assert "aesthetic_framing" in diagnostics.unestablished_lens_ids
    assert diagnostics.active_component_count > 0
    assert diagnostics.suppressed_component_count == 1


def test_story_lens_review_state_tracks_existing_component_author_work() -> None:
    confirmed = confirm_component(
        HYBRID_ANALYSIS,
        "engine:investigation-revelation",
        "This is the story engine I want.",
    )
    lenses, diagnostics = build_story_lenses(
        analysis=confirmed,
        analysis_current=True,
    )
    engine = _by_id(lenses)[StoryLensType.STORY_ENGINE.value]

    assert engine.state is StoryLensState.AUTHOR_CONFIRMED
    assert diagnostics.author_adjustment_count == 1

    renamed = rename_component(
        confirmed,
        "engine:investigation-revelation",
        "Investigation, contradiction, and revelation",
        "Use language that better describes the intended engine.",
    )
    lenses, diagnostics = build_story_lenses(
        analysis=renamed,
        analysis_current=True,
    )
    engine = _by_id(lenses)[StoryLensType.STORY_ENGINE.value]

    assert engine.state is StoryLensState.AUTHOR_MODIFIED
    assert "contradiction" in engine.summary.casefold()
    assert diagnostics.author_adjustment_count == 2


def test_story_lenses_fail_honestly_when_premise_does_not_support_a_pattern() -> None:
    analysis = DeterministicArchitectureAnalyzer().analyze(
        premise="A person arrives in an unfamiliar town and decides to begin again.",
        source_provenance=(),
    )
    lenses, diagnostics = build_story_lenses(
        analysis=analysis,
        analysis_current=True,
    )
    by_id = _by_id(lenses)

    assert diagnostics.source_mode == "deterministic_fallback"
    assert set(diagnostics.unestablished_lens_ids) == set(EXPECTED_LENS_ORDER)
    assert by_id["structural_shape"].summary == "Not established yet"
    assert by_id["reader_experience"].summary == "Not established yet"
    assert all(lens.authority_status == "DERIVED / NOT CANON" for lens in lenses)


def test_stale_analysis_marks_every_story_lens_as_needing_review() -> None:
    lenses, diagnostics = build_story_lenses(
        analysis=HYBRID_ANALYSIS,
        analysis_current=False,
    )

    assert diagnostics.stale is True
    assert all(lens.state is StoryLensState.STALE for lens in lenses)
    assert set(diagnostics.needs_attention_lens_ids) == set(EXPECTED_LENS_ORDER)


def test_story_lens_refinement_reuses_existing_idempotent_noncanonical_authority(tmp_path) -> None:
    app = create_hybrid_app(tmp_path)

    discovery = app.continue_from_architecture(
        command_id="story-lens-continue",
        expected_session_version=app.projection().session_version,
    )
    assert discovery.discovery is not None
    assert discovery.canonical_refs == ()

    first = app.confirm_architecture_component(
        component_id="trope:secret-identity",
        rationale="Keep secret identity as a visible trope.",
        command_id="story-lens-confirm",
        expected_session_version=discovery.session_version,
    )

    assert first.primary_surface == "architecture"
    assert first.discovery is None
    assert first.canonical_refs == ()
    assert first.story_orientation is not None
    trope_lens = _by_id(first.story_orientation.story_lenses)["common_tropes"]
    assert trope_lens.state is StoryLensState.AUTHOR_CONFIRMED

    replay = app.confirm_architecture_component(
        component_id="trope:secret-identity",
        rationale="Keep secret identity as a visible trope.",
        command_id="story-lens-confirm",
        expected_session_version=discovery.session_version,
    )
    assert replay.session_version == first.session_version
    assert replay.canonical_refs == ()
    assert replay.story_orientation is not None
    assert replay.story_orientation.lens_diagnostics.author_adjustment_count == 1
