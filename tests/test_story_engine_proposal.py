"""Tests for propose_story_engine — TDD for issue #5.

Acceptance criteria:
- A missing story_engine diagnostic can lead to a proposal YAML artifact.
- The proposal offers 2-3 options for the main thread and subordinate thread shape.
- Each option includes a short tradeoff explanation.
- The proposal is grounded in existing blueprint context.
- The blueprint is not mutated when the proposal is produced.
"""

from __future__ import annotations

import pytest
import yaml

from auteur.blueprint import (
    StoryBlueprint,
    StoryEngine,
)
from auteur.structure.proposals import (
    ProposalType,
    StructureProposal,
    propose_story_engine,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_MINIMAL_BLUEPRINT_DATA: dict = {
    "identity": {
        "title": "The Long Road",
        "author_intent": "A war veteran seeks redemption after betraying his unit.",
        "length_class": "novel",
        "genre": "literary",
        "mode": "tragic",
        "target_audience": "adult",
        "pov_type": "third_person_limited_single",
    },
    "contract": {
        "content_rating": "R",
        "mandatory_ending_tone": "bittersweet",
    },
    "emotional_design": {
        "overall_emotional_arc": "guilt -> confrontation -> partial absolution",
    },
    "theme": {
        "central_question": "Can a person be forgiven for a cowardly act they cannot undo?",
        "thesis": "Redemption is possible only when the self-lie is dismantled.",
        "motifs": ["silence", "uniforms", "maps"],
    },
}


def _blueprint_without_engine() -> StoryBlueprint:
    return StoryBlueprint.model_validate(_MINIMAL_BLUEPRINT_DATA)


def _blueprint_with_engine() -> StoryBlueprint:
    data = dict(_MINIMAL_BLUEPRINT_DATA)
    data["story_engine"] = {
        "main_thread": {
            "type": "main_plot",
            "want": {"author_text": "Protagonist wants peace.", "checkable_claims": []},
            "resistance": {"author_text": "His past follows him.", "checkable_claims": []},
            "conflict": {"author_text": "External vs internal.", "checkable_claims": []},
            "stakes": {"author_text": "Sanity and relationships.", "checkable_claims": []},
            "change": {"author_text": "He learns to accept guilt.", "checkable_claims": []},
            "thematic_function": "Tests the price of self-deception.",
        },
        "threads": [],
    }
    return StoryBlueprint.model_validate(data)


# ---------------------------------------------------------------------------
# Core behavior
# ---------------------------------------------------------------------------


def test_returns_structure_proposal():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    assert isinstance(result, StructureProposal)


def test_proposal_type_is_generation():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    assert result.type == ProposalType.GENERATION


def test_source_rule_is_story_engine_missing():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    assert result.source_rule == "story_engine.missing"


def test_proposal_has_two_to_three_options():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    assert 2 <= len(result.options) <= 3


def test_each_option_has_nonempty_tradeoffs():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    for opt in result.options:
        assert opt.tradeoffs.strip(), f"Option {opt.id!r} has empty tradeoffs"


def test_each_option_has_nonempty_summary():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    for opt in result.options:
        assert opt.summary.strip(), f"Option {opt.id!r} has empty summary"


def test_each_option_data_contains_story_engine():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    for opt in result.options:
        assert "story_engine" in opt.data, f"Option {opt.id!r} data missing 'story_engine'"


def test_each_option_story_engine_has_main_thread():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    for opt in result.options:
        assert "main_thread" in opt.data["story_engine"], (
            f"Option {opt.id!r} story_engine missing 'main_thread'"
        )


def test_option_ids_are_unique():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    ids = [opt.id for opt in result.options]
    assert len(ids) == len(set(ids)), "Option IDs are not unique"


# ---------------------------------------------------------------------------
# Blueprint context grounding
# ---------------------------------------------------------------------------


def test_proposal_summary_references_blueprint_context():
    """The summary should reflect author_intent, theme, or genre."""
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    # At least the overall summary should contain some context
    context_signals = [
        blueprint.identity.title,
        blueprint.theme.central_question,
        blueprint.identity.author_intent[:20],
        blueprint.identity.genre.value,
    ]
    combined = result.summary + " ".join(opt.summary for opt in result.options)
    assert any(signal.lower() in combined.lower() for signal in context_signals), (
        "Proposal summary does not appear to reference any blueprint context"
    )


def test_main_thread_want_reflects_author_intent():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    # At least one option's main_thread want should contain a fragment of author_intent
    all_wants = [
        opt.data["story_engine"]["main_thread"].get("want", {}).get("author_text", "")
        for opt in result.options
    ]
    combined_wants = " ".join(all_wants).lower()
    # author_intent: "A war veteran seeks redemption after betraying his unit."
    assert any(
        word in combined_wants
        for word in ["veteran", "redemption", "betray", "unit", "war"]
    ), f"No option want text references author_intent. Got: {all_wants!r}"


# ---------------------------------------------------------------------------
# Non-mutation guarantee
# ---------------------------------------------------------------------------


def test_blueprint_not_mutated():
    blueprint = _blueprint_without_engine()
    original_engine = blueprint.story_engine  # should be None
    propose_story_engine(blueprint)
    assert blueprint.story_engine == original_engine, "propose_story_engine mutated blueprint"


def test_blueprint_fields_unchanged_after_proposal():
    blueprint = _blueprint_without_engine()
    original_title = blueprint.identity.title
    original_theme = blueprint.theme.central_question
    propose_story_engine(blueprint)
    assert blueprint.identity.title == original_title
    assert blueprint.theme.central_question == original_theme


# ---------------------------------------------------------------------------
# Error guard: blueprint already has story_engine
# ---------------------------------------------------------------------------


def test_raises_if_story_engine_already_present():
    blueprint = _blueprint_with_engine()
    assert blueprint.story_engine is not None
    with pytest.raises(ValueError, match="story_engine"):
        propose_story_engine(blueprint)


# ---------------------------------------------------------------------------
# YAML round-trip
# ---------------------------------------------------------------------------


def test_proposal_serialises_to_valid_yaml():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    dumped = yaml.dump(result.model_dump(mode="json"), allow_unicode=True)
    reloaded = yaml.safe_load(dumped)
    recovered = StructureProposal.model_validate(reloaded)
    assert recovered.proposal_id == result.proposal_id
    assert len(recovered.options) == len(result.options)


def test_proposal_has_no_selection_by_default():
    blueprint = _blueprint_without_engine()
    result = propose_story_engine(blueprint)
    assert result.selection.selected_option_id == ""
    assert result.decision is None
