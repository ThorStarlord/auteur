"""Tests for the CartographerOutline Pydantic model — Slice 1 of outline schema validation."""

import pytest

from auteur.cartographer_outline import CartographerOutline


# ---------------------------------------------------------------------------
# Rejection cases
# ---------------------------------------------------------------------------


def test_rejects_outline_without_scenes():
    """An outline that is missing the required 'scenes' key should fail
    validation with a clear error."""
    data = {
        "scope": "chapter",
        "chapter_index": 1,
        "chapter_summary": "The hero returns to the tavern.",
        "arc_pushes": [],
        "contract_compliance": [],
        "expected_elements_touched": [],
        "forbidden_tropes_avoided": [],
        "estimated_chapter_tension": 4,
        "thematic_reinforcement": "Redemption costs.",
        "conflict_report": None,
    }

    with pytest.raises(Exception):
        CartographerOutline.model_validate(data)


def test_rejects_estimated_tension_out_of_range_high():
    """An estimated_chapter_tension > 10 should fail validation."""
    data = _minimal_outline_data(estimated_tension=15)
    with pytest.raises(Exception):
        CartographerOutline.model_validate(data)


def test_rejects_estimated_tension_out_of_range_low():
    """An estimated_chapter_tension < 1 should fail validation."""
    data = _minimal_outline_data(estimated_tension=0)
    with pytest.raises(Exception):
        CartographerOutline.model_validate(data)


def test_rejects_empty_scenes_list():
    """An empty scenes list ([]) should fail validation."""
    data = _minimal_outline_data()
    data["scenes"] = []
    with pytest.raises(Exception):
        CartographerOutline.model_validate(data)


# ---------------------------------------------------------------------------
# Success case
# ---------------------------------------------------------------------------


def test_valid_outline_passes():
    """A fully-formed outline with one scene should pass validation."""
    data = _valid_outline_data()
    outline = CartographerOutline.model_validate(data)
    assert outline.scope == "chapter"
    assert outline.chapter_index == 1
    assert len(outline.scenes) == 1
    assert outline.scenes[0].scene_id == "s1"
    assert outline.scenes[0].estimated_tension == 4
    assert outline.estimated_chapter_tension == 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_outline_data(*, estimated_tension: int = 4) -> dict:
    return {
        "scope": "chapter",
        "chapter_index": 1,
        "chapter_summary": "The hero returns to the tavern.",
        "scenes": [
            {
                "scene_id": "s1",
                "summary": "The hero sits alone.",
                "key_events": [],
                "character_state_changes": [],
                "arc_advancements": [],
                "estimated_tension": 4,
                "emotional_tone": "unease",
            }
        ],
        "arc_pushes": [],
        "contract_compliance": [],
        "expected_elements_touched": [],
        "forbidden_tropes_avoided": [],
        "estimated_chapter_tension": estimated_tension,
        "thematic_reinforcement": "Redemption costs.",
        "conflict_report": None,
    }


def _valid_outline_data() -> dict:
    return {
        "scope": "chapter",
        "chapter_index": 1,
        "chapter_summary": "Kael returns to the tavern.",
        "scenes": [
            {
                "scene_id": "s1",
                "pov_character": "Kael",
                "location": "taverntown",
                "summary": "He nurses a drink and surveys the room.",
                "key_events": ["broods", "spots a stranger"],
                "character_state_changes": [
                    {
                        "character": "Kael",
                        "field": "location",
                        "before": None,
                        "after": "Tavern",
                    },
                    {
                        "character": "Kael",
                        "field": "emotional",
                        "before": None,
                        "after": "brooding",
                    },
                ],
                "arc_advancements": [
                    {
                        "character": "Kael",
                        "milestone_touched": "confronts_past",
                        "delta_pct": 5,
                    }
                ],
                "estimated_tension": 4,
                "emotional_tone": "subtle unease",
            }
        ],
        "arc_pushes": ["confronts_past"],
        "contract_compliance": [
            {"rule": "no_prophecy", "how_honored": "no prophecy mentioned"}
        ],
        "expected_elements_touched": ["tavern_backstory"],
        "forbidden_tropes_avoided": ["chosen_one_prophecy"],
        "estimated_chapter_tension": 4,
        "thematic_reinforcement": "Redemption costs more than Kael wants to pay.",
        "conflict_report": None,
    }
