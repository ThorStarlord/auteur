"""Tests for the Cartographer outline validation — Phase 2 TDD tests.

Verifies sequence integrity (no index gaps), tension target deviations, and continuous carrier path
checks (no teleportation or inventory drifts within outline scenes).
"""
from __future__ import annotations

from pathlib import Path
import yaml
import pytest

from auteur.cartographer_compiler import validate_outline
from auteur.blueprint import StoryBlueprint

SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def test_validation_passes_for_valid_outline(tmp_path):
    """A valid, continuous outline matching blueprint tension guidelines should pass."""
    outline_data = {
        "title": "A Valid Story",
        "total_chapters": 2,
        "chapters": [
            {
                "index": 1,
                "chapter_summary": "Kael visits the Tavern.",
                "estimated_chapter_tension": 4,  # Sample target is 4
                "scenes": [
                    {
                        "scene_id": "s1",
                        "pov_character": "Kael",
                        "location": "Tavern",
                        "summary": "He arrives at the tavern.",
                        "key_events": [],
                        "character_state_changes": [
                            {
                                "character": "Kael",
                                "field": "location",
                                "before": None,
                                "after": "Tavern",
                            }
                        ]
                    }
                ]
            },
            {
                "index": 2,
                "chapter_summary": "Kael goes home.",
                "estimated_chapter_tension": 4,
                "scenes": [
                    {
                        "scene_id": "s2",
                        "pov_character": "Kael",
                        "location": "Tavern",
                        "summary": "Still at the Tavern.",
                        "key_events": [],
                        "character_state_changes": [
                            {
                                "character": "Kael",
                                "field": "location",
                                "before": "Tavern",
                                "after": "Home",
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    outline_path = tmp_path / "valid_outline.yaml"
    outline_path.write_text(yaml.safe_dump(outline_data), encoding="utf-8")
    
    # Should run cleanly and return True/0
    rc = validate_outline(outline_path, SAMPLE_YAML)
    assert rc is True


def test_validation_fails_on_chapter_index_gaps(tmp_path):
    """An outline with skipped chapters (e.g. 1 then 3) should fail validation."""
    outline_data = {
        "total_chapters": 2,
        "chapters": [
            {
                "index": 1,
                "chapter_summary": "Kael visits the Tavern.",
                "estimated_chapter_tension": 4,
                "scenes": [{"scene_id": "s1", "summary": "Arrives."}]
            },
            {
                "index": 3,  # Gapped! Should be 2
                "chapter_summary": "Kael goes home.",
                "estimated_chapter_tension": 4,
                "scenes": [{"scene_id": "s2", "summary": "Arrives."}]
            }
        ]
    }
    outline_path = tmp_path / "gapped_outline.yaml"
    outline_path.write_text(yaml.safe_dump(outline_data), encoding="utf-8")
    
    with pytest.raises(ValueError, match="Chapter index sequence gap detected"):
        validate_outline(outline_path, SAMPLE_YAML)


def test_validation_fails_on_high_tension_deviation(tmp_path):
    """If the outline tension target deviates by more than 1 from the blueprint,
    it should fail validation."""
    outline_data = {
        "total_chapters": 1,
        "chapters": [
            {
                "index": 1,
                "chapter_summary": "Kael visits the Tavern.",
                "estimated_chapter_tension": 8,  # Target is 4, so 8 is > +1 deviation
                "scenes": [{"scene_id": "s1", "summary": "Arrives."}]
            }
        ]
    }
    outline_path = tmp_path / "tension_drift_outline.yaml"
    outline_path.write_text(yaml.safe_dump(outline_data), encoding="utf-8")
    
    with pytest.raises(ValueError, match="estimated_chapter_tension deviates from blueprint target"):
        validate_outline(outline_path, SAMPLE_YAML)


def test_validation_fails_on_scene_level_carrier_teleportation(tmp_path):
    """If a character teleports across scenes (e.g., in tavern in s1, but starts in dungeon in s2
    with no explanation), it should fail local outline validation."""
    outline_data = {
        "total_chapters": 1,
        "chapters": [
            {
                "index": 1,
                "chapter_summary": "Kael's adventure.",
                "estimated_chapter_tension": 4,
                "scenes": [
                    {
                        "scene_id": "s1",
                        "pov_character": "Kael",
                        "location": "Tavern",
                        "summary": "Kael is at the tavern.",
                        "character_state_changes": [
                            {
                                "character": "Kael",
                                "field": "location",
                                "before": None,
                                "after": "Tavern"
                            }
                        ]
                    },
                    {
                        "scene_id": "s2",
                        "pov_character": "Kael",
                        "location": "Dungeon",
                        "summary": "Kael is suddenly in the dungeon.",
                        "character_state_changes": [
                            {
                                "character": "Kael",
                                "field": "location",
                                "before": "Dungeon",  # Does not match the previous after 'Tavern'!
                                "after": "Dungeon"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    outline_path = tmp_path / "teleportation_outline.yaml"
    outline_path.write_text(yaml.safe_dump(outline_data), encoding="utf-8")
    
    with pytest.raises(ValueError, match="carriers.location_teleportation.*Kael.*Tavern.*Dungeon"):
        validate_outline(outline_path, SAMPLE_YAML)
