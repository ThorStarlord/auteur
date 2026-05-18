"""Tests for applying audit proposals — Phase 1 TDD tests.

Verifies that accepted proposal option data block payloads are programmatically and transactionally
applied to cartographer_outline.yaml or bible.json on disk.
"""
from __future__ import annotations

import json
from pathlib import Path
import yaml
import pytest

from auteur.structure.proposal_resolution import resolve_proposal, load_resolved_rules
from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.project import Project

SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


@pytest.fixture
def test_project(tmp_path) -> Project:
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "test_novel", blueprint)
    
    # Write a dummy bible state
    project.bible.record_event(
        chapter_index=1,
        summary="Aldric enters Throne Room.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": None,
                    "after": "Throne Room",
                }
            ]
        }
    )
    project.bible.upsert_character("Aldric", location="Throne Room")
    project.bible.save()
    return project


def test_resolve_proposal_with_bible_delta_updates_bible_on_disk(test_project):
    """If an accepted proposal contains option.data with delta_type='bible_delta',
    it should update the specific bible event's delta on disk."""
    proposals_dir = test_project.structure_proposals_dir()
    proposal_path = proposals_dir / "repair_teleportation.yaml"
    
    proposal_data = {
        "proposal_id": "repair_teleportation",
        "type": "repair",
        "source_rule": "carriers.location_teleportation",
        "source_domain": "bible_audit",
        "summary": "Fix teleportation by retroactively updating the start location of Aldric.",
        "options": [
            {
                "id": "retroactive_update",
                "summary": "Change Aldric's starting location to Dungeon in event 1.",
                "tradeoffs": "Changes history.",
                "data": {
                    "delta_type": "bible_delta",
                    "action": "update_carrier_state",
                    "event_index": 0,  # 0-indexed reference to first event
                    "character": "Aldric",
                    "field": "location",
                    "before": None,
                    "after": "Dungeon",
                }
            }
        ]
    }
    
    proposal_path.write_text(yaml.safe_dump(proposal_data), encoding="utf-8")
    
    # Run resolution
    rc = resolve_proposal(test_project.path, "repair_teleportation", "retroactive_update")
    assert rc == 0
    
    # Verify proposal marked as resolved
    resolved = load_resolved_rules(test_project.path)
    assert "carriers.location_teleportation" in resolved
    
    # Verify bible.json changed on disk
    updated_bible = StoryBible(test_project.bible.file_path)
    events = updated_bible.data["events"]
    assert len(events) == 1
    changes = events[0]["deltas"]["character_state_changes"]
    assert changes[0]["after"] == "Dungeon"


def test_resolve_proposal_with_cartographer_outline_injects_scene(test_project):
    """If an accepted proposal contains option.data with delta_type='cartographer_outline',
    it should update cartographer_outline.yaml on disk by inserting a new scene card."""
    # Write a dummy cartographer_outline.yaml in project root
    outline_path = test_project.path / "cartographer_outline.yaml"
    outline_data = {
        "title": "The Shattered Crown - Scene Outline",
        "total_chapters": 1,
        "chapters": [
            {
                "index": 1,
                "act": "Act I",
                "title": "The Throne Room",
                "pov_character": "Aldric",
                "location": "Throne Room",
                "threads": ["main_thread"],
                "scenes": [
                    {
                        "scene_id": "s1",
                        "pov_character": "Aldric",
                        "location": "Throne Room",
                        "summary": "Aldric meets the king.",
                    }
                ]
            }
        ]
    }
    outline_path.write_text(yaml.safe_dump(outline_data), encoding="utf-8")
    
    proposals_dir = test_project.structure_proposals_dir()
    proposal_path = proposals_dir / "repair_travel.yaml"
    
    proposal_data = {
        "proposal_id": "repair_travel",
        "type": "repair",
        "source_rule": "carriers.location_teleportation",
        "source_domain": "bible_audit",
        "summary": "Fix teleportation by inserting a transition scene.",
        "options": [
            {
                "id": "insert_travel_scene",
                "summary": "Insert travel scene card.",
                "tradeoffs": "Paces the chapter down.",
                "data": {
                    "delta_type": "cartographer_outline",
                    "action": "insert_scene",
                    "chapter_index": 1,
                    "scene_id": "s1_5",
                    "pov_character": "Aldric",
                    "location": "Road",
                    "summary": "Aldric travels from Tavern to Throne Room.",
                }
            }
        ]
    }
    proposal_path.write_text(yaml.safe_dump(proposal_data), encoding="utf-8")
    
    # Run resolution
    rc = resolve_proposal(test_project.path, "repair_travel", "insert_travel_scene")
    assert rc == 0
    
    # Verify cartographer_outline.yaml on disk has the new scene card inserted
    updated_outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
    scenes = updated_outline["chapters"][0]["scenes"]
    assert len(scenes) == 2
    assert scenes[1]["scene_id"] == "s1_5"
    assert scenes[1]["location"] == "Road"


def test_resolve_proposal_rolls_back_and_fails_on_validation_error(test_project):
    """If a delta application causes a schema validation failure, the transaction
    should roll back safely without modifying the target files on disk, and return 1."""
    proposals_dir = test_project.structure_proposals_dir()
    proposal_path = proposals_dir / "repair_invalid.yaml"
    
    proposal_data = {
        "proposal_id": "repair_invalid",
        "type": "repair",
        "source_rule": "carriers.location_teleportation",
        "source_domain": "bible_audit",
        "summary": "Invalid update delta.",
        "options": [
            {
                "id": "invalid_delta",
                "summary": "Tries to set non-existent field or bad type in bible.",
                "data": {
                    "delta_type": "bible_delta",
                    "action": "update_carrier_state",
                    "event_index": 0,
                    "character": "Aldric",
                    "field": "invalid_field_name",  # Invalid field per schema
                    "before": None,
                    "after": "Dungeon",
                }
            }
        ]
    }
    proposal_path.write_text(yaml.safe_dump(proposal_data), encoding="utf-8")
    
    # Run resolution
    rc = resolve_proposal(test_project.path, "repair_invalid", "invalid_delta")
    assert rc == 1  # Should fail due to schema validation check!
    
    # Verify bible event delta remains unchanged on disk
    updated_bible = StoryBible(test_project.bible.file_path)
    events = updated_bible.data["events"]
    assert len(events) == 1
    changes = events[0]["deltas"]["character_state_changes"]
    assert changes[0]["after"] == "Throne Room"
