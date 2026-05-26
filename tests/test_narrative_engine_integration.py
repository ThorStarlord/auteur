"""End-to-end integration test for the Narrative Engine layer.

Validates that structural forces and contradictions flow from blueprint
through PlanningCall into the Cartographer prompt, and that all diagnostics
run without error.
"""
from __future__ import annotations

import tempfile

import pytest

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.cartographer_models import PlanningCall, PlanningScope
from auteur.cartographer import _user_message
from auteur.structure.analyzer import run_all_diagnostics


@pytest.fixture
def blueprint_with_psychology() -> StoryBlueprint:
    return StoryBlueprint.model_validate({
        "identity": {
            "title": "The Fractured Mirror",
            "author_intent": "A spy discovers the agency she built her life on is corrupt.",
            "length_class": "novella",
            "genre": "thriller",
                "mode": "noir",
                "target_audience": "adult",
                "pov_type": "third_person_limited_single",
                "target_experience": {
                    "primary": "suspense",
                    "progression": "trust -> doubt -> betrayal -> resolution",
                },
            },
            "contract": {
                "content_rating": "PG-13",
                "mandatory_ending_tone": "ambiguous",
        },
        "emotional_design": {
            "overall_emotional_arc": "trust -> doubt -> betrayal -> resolution",
        },
        "theme": {
            "central_question": "Can loyalty survive the truth?",
            "thesis": "True loyalty requires questioning the institution, not serving it.",
            "motifs": ["mirrors", "files", "rain"],
        },
        "characters": [
            {
                "name": "Nina",
                "role": "protagonist",
                "arc_type": "fall",
                "arc_start_percentage": 100,
                "arc_end_percentage": 0,
            },
                {
                    "name": "Mercer",
                    "role": "antagonist",
                    "arc_type": "growth",
                    "arc_start_percentage": 20,
                    "arc_end_percentage": 80,
                    "current_arc_percentage": 20,
                },
        ],
        "story_engine": {
            "main_thread": {
                "type": "main_plot",
                "want": {
                    "author_text": "Nina wants to expose the agency's corruption",
                    "checkable_claims": [],
                },
                "resistance": {
                    "author_text": "Mercer controls the evidence and the narrative",
                    "checkable_claims": [],
                },
                "conflict": {
                    "author_text": "Truth vs institutional survival",
                    "checkable_claims": [],
                },
                "stakes": {
                    "author_text": "Nina's career, freedom, and identity",
                    "checkable_claims": [],
                },
                "change": {
                    "author_text": "Nina moves from loyal agent to disillusioned whistleblower",
                    "checkable_claims": [],
                },
                "thematic_function": "Tests the thesis through Nina's escalating disillusionment.",
            },
            "threads": [
                {
                    "name": "Nina_arc",
                    "type": "character_arc",
                    "want": {
                        "author_text": "Nina wants to believe the agency can be reformed from within",
                        "checkable_claims": [],
                    },
                    "resistance": {
                        "author_text": "Every investigation reveals deeper rot",
                        "checkable_claims": [],
                    },
                    "conflict": {
                        "author_text": "Hope vs evidence",
                        "checkable_claims": [],
                    },
                    "stakes": {
                        "author_text": "Her faith in the system",
                        "checkable_claims": [],
                    },
                    "change": {
                        "author_text": "From institutional believer to principled defector",
                        "checkable_claims": [],
                    },
                    "supports_main_by": ["pressures_change"],
                    "thematic_function": "Internalises the thesis at personal cost.",
                },
            ],
        },
    })


def test_structural_forces_bridge_to_planning_call(blueprint_with_psychology):
    """Structural forces from story engine main_thread flow into PlanningCall."""
    bp = blueprint_with_psychology
    call = PlanningCall.for_chapter(bp, 1)

    assert call.story_engine_want == "Nina wants to expose the agency's corruption"
    assert call.story_engine_resistance == "Mercer controls the evidence and the narrative"
    assert call.story_engine_conflict == "Truth vs institutional survival"
    assert call.story_engine_stakes == "Nina's career, freedom, and identity"
    assert call.story_engine_change == (
        "Nina moves from loyal agent to disillusioned whistleblower"
    )


def test_character_contradictions_bridge_to_planning_call(blueprint_with_psychology):
    """Character contradictions are collected into PlanningCall."""
    bp = blueprint_with_psychology
    # Add psychology with contradictions to both characters
    bp.characters[0].identity = {
        "psychology": {
            "contradictions": ["loyal_but_skeptical", "idealist_in_cynical_world"],
        },
    }
    bp.characters[1].identity = {
        "psychology": {
            "contradictions": [
                "protector_but_predator",
                "charming_but_manipulative",
                "principled_but_corrupt",
            ],
        },
    }

    call = PlanningCall.for_chapter(bp, 1)

    assert "Nina" in call.character_contradictions
    assert "Mercer" in call.character_contradictions
    assert "loyal_but_skeptical" in call.character_contradictions["Nina"]
    assert "protector_but_predator" in call.character_contradictions["Mercer"]


def test_low_contradictions_not_collected(blueprint_with_psychology):
    """Characters with fewer than 2 contradictions are omitted."""
    bp = blueprint_with_psychology
    bp.characters[0].identity = {
        "psychology": {
            "contradictions": ["loyal_but_skeptical"],
        },
    }

    call = PlanningCall.for_chapter(bp, 1)

    assert "Nina" not in call.character_contradictions


def test_prompt_renders_structural_forces_section(blueprint_with_psychology):
    """User message contains the STRUCTURAL FORCES section with all 5 forces."""
    call = PlanningCall.for_chapter(blueprint_with_psychology, 1)
    msg = _user_message(call)

    assert "## STRUCTURAL FORCES" in msg
    assert "Want: Nina wants to expose the agency's corruption" in msg
    assert "Resistance: Mercer controls the evidence and the narrative" in msg
    assert "Conflict: Truth vs institutional survival" in msg
    assert "Stakes: Nina's career, freedom, and identity" in msg
    assert "Change:" in msg
    assert "disillusioned whistleblower" in msg


def test_prompt_renders_contradictions_section(blueprint_with_psychology):
    """User message contains CHARACTER CONTRADICTIONS section when present."""
    bp = blueprint_with_psychology
    bp.characters[0].identity = {
        "psychology": {
            "contradictions": ["loyal_but_skeptical", "idealist_in_cynical_world"],
        },
    }
    call = PlanningCall.for_chapter(bp, 1)
    msg = _user_message(call)

    assert "## CHARACTER CONTRADICTIONS" in msg
    assert "Nina: loyal_but_skeptical; idealist_in_cynical_world" in msg


def test_prompt_contradictions_section_none(blueprint_with_psychology):
    """Contradictions section shows (none) when no contradictions exist."""
    call = PlanningCall.for_chapter(blueprint_with_psychology, 1)
    msg = _user_message(call)

    assert "## CHARACTER CONTRADICTIONS" in msg
    assert "(none)" in msg


def test_planning_call_scope_and_structure(blueprint_with_psychology):
    """PlanningCall retains its existing fields and structure."""
    call = PlanningCall.for_chapter(blueprint_with_psychology, 1)

    assert call.scope == PlanningScope.CHAPTER
    assert call.chapter_index == 1
    assert call.title == "The Fractured Mirror"
    assert len(call.arc_directives) == 2


def test_diagnostics_run_without_cartographer_outline(blueprint_with_psychology):
    """run_all_diagnostics works when no cartographer_outline is provided."""
    bible_path = tempfile.mktemp(suffix=".json")
    bible = StoryBible(bible_path)
    diags = run_all_diagnostics(blueprint_with_psychology, bible, cartographer_outline=None)
    assert isinstance(diags, list)


def test_empty_story_engine_graceful_fallback():
    """Blueprint with no story engine does not crash during for_chapter."""
    bp = StoryBlueprint.model_validate({
        "identity": {
            "title": "Minimal",
            "author_intent": "A test.",
            "length_class": "short_story",
            "genre": "literary",
                "mode": "other",
                "target_audience": "adult",
                "pov_type": "third_person_limited_single",
                "target_experience": {
                    "primary": "catharsis",
                    "progression": "a -> b",
                },
            },
            "contract": {
                "content_rating": "G",
                "mandatory_ending_tone": "hopeful",
        },
        "emotional_design": {
            "overall_emotional_arc": "a -> b",
        },
        "theme": {
            "central_question": "What?",
            "thesis": "Things happen.",
            "motifs": [],
        },
        "characters": [
            {
                "name": "Test",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
            },
        ],
    })

    # Estimated chapters is auto-filled for short_story; find a valid index
    idx = 1
    call = PlanningCall.for_chapter(bp, idx)

    assert call.story_engine_want is None
    assert call.story_engine_resistance is None
    assert call.story_engine_conflict is None
    assert call.story_engine_stakes is None
    assert call.story_engine_change is None
    assert call.character_contradictions == {}
    assert call.scope == PlanningScope.CHAPTER
