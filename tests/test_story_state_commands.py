"""Integration and unit tests for auteur state CLI commands."""

import json
from pathlib import Path
import pytest
import yaml

from auteur.cli import main
from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible


def _minimal_blueprint_data() -> dict[str, object]:
    return {
        "identity": {
            "title": "Test Story",
            "author_intent": "A test premise.",
            "length_class": "novel",
            "genre": "literary",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "quiet pressure",
        },
        "theme": {
            "central_question": "What does truth cost?",
            "thesis": "Truth costs belonging.",
            "motifs": [],
        },
    }


@pytest.fixture
def test_project(tmp_path):
    """Fixture that initializes a valid blueprint and bible in a temporary directory."""
    bp_data = _minimal_blueprint_data()
    blueprint = StoryBlueprint.model_validate(bp_data)
    
    bp_path = tmp_path / "blueprint.yaml"
    bp_path.write_text(yaml.safe_dump(blueprint.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
    
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)
    bible.upsert_character("Aldric", location="chapter_1", physical="stable", emotional="focused")
    bible.save()
    
    return tmp_path


def test_state_check_empty_blueprint(test_project, capsys):
    """Verify state check reports unresolved structural diagnostics."""
    rc = main(["state", "check", str(test_project)])
    captured = capsys.readouterr()
    
    assert "Story State Report" in captured.out
    assert "findings total" in captured.out
    # Missing story engine should be flagged as structural force error
    assert rc == 4


def test_state_update_blueprint_success(test_project, capsys):
    """Verify that valid updates to blueprint succeed and save correctly."""
    rc = main([
        "state", "update", str(test_project), "blueprint.yaml",
        "--key", "identity.title", "--val", '"A Brand New Odyssey"'
    ])
    captured = capsys.readouterr()
    
    assert rc == 0
    assert "Success: Updated 'identity.title'" in captured.out
    
    # Reload and check
    bp = StoryBlueprint.from_yaml(test_project / "blueprint.yaml")
    assert bp.identity.title == "A Brand New Odyssey"


def test_state_update_blueprint_validation_failure(test_project, capsys):
    """Verify that invalid updates to blueprint fail, roll back, and leave file unchanged."""
    original_title = "Test Story"
    
    rc = main([
        "state", "update", str(test_project), "blueprint.yaml",
        "--key", "identity.length_class", "--val", '"invalid_length_class"'
    ])
    captured = capsys.readouterr()
    
    assert rc == 1
    assert "Error: Schema validation failed" in captured.err
    
    # Verify title and length_class remain completely untouched (transactional rollback)
    bp = StoryBlueprint.from_yaml(test_project / "blueprint.yaml")
    assert bp.identity.title == original_title
    assert bp.identity.length_class.value == "novel"


def test_state_update_bible_success(test_project, capsys):
    """Verify that valid updates to bible succeed and save correctly."""
    rc = main([
        "state", "update", str(test_project), "bible.json",
        "--key", "characters.Aldric.location", "--val", '"Dungeon"'
    ])
    captured = capsys.readouterr()
    
    assert rc == 0
    assert "Success: Updated 'characters.Aldric.location'" in captured.out
    
    # Reload and check
    bible = StoryBible(test_project / "bible.json")
    assert bible.data["characters"]["Aldric"]["location"] == "Dungeon"


def test_state_update_bible_validation_failure(test_project, capsys):
    """Verify that invalid schema updates to bible fail and roll back safely."""
    rc = main([
        "state", "update", str(test_project), "bible.json",
        "--key", "realized_tension", "--val", '"not_a_list"'
    ])
    captured = capsys.readouterr()
    
    assert rc == 1
    assert "Error: Schema validation failed" in captured.err
    
    # Verify realized_tension was not mutated to the string
    bible = StoryBible(test_project / "bible.json")
    assert isinstance(bible.data["realized_tension"], list)


def test_state_prepare_drafting_stdout(test_project, capsys):
    """Verify state prepare drafting compiles the correct Markdown skeleton to stdout."""
    rc = main([
        "state", "prepare", str(test_project), "drafting",
        "--scope", "chapter", "--chapter", "1"
    ])
    captured = capsys.readouterr()
    
    assert rc == 0
    assert "# Phase Handoff: DRAFTING" in captured.out
    assert "**Active Story Object**: Chapter 1" in captured.out
    assert "**Drafting Scope**: CHAPTER" in captured.out
    assert "Aldric (stable, focused)" in captured.out


def test_state_prepare_drafting_file(test_project, capsys):
    """Verify state prepare saving context to an output file works perfectly."""
    out_file = test_project / "handoffs" / "drafting_context.md"
    rc = main([
        "state", "prepare", str(test_project), "drafting",
        "--scope", "prose", "--out", str(out_file)
    ])
    captured = capsys.readouterr()
    
    assert rc == 0
    assert "Success: Prepared handoff context saved to" in captured.out
    assert out_file.exists()
    
    content = out_file.read_text(encoding="utf-8")
    assert "# Phase Handoff: DRAFTING" in content
    assert "**Drafting Scope**: PROSE" in content


def test_state_canon_markdown(test_project, capsys):
    """Verify state canon returns a structured Markdown reference report."""
    rc = main(["state", "canon", str(test_project), "--format", "markdown"])
    captured = capsys.readouterr()
    
    assert rc == 0
    assert "# Canonical Reference Manual" in captured.out
    assert "Character Registry" in captured.out
    assert "Aldric" in captured.out
    assert "chapter_1" in captured.out


def test_state_confirm_recovery_merge(test_project, capsys):
    """Verify recovery confirm merges candidate layers safely into blueprint and bible."""
    recovery_payload = {
        "candidate_locked_layers": {
            "target_experience": "bittersweet",
            "promise_constraints": {
                "genre": "epic_fantasy",
                "mode": "noir"
            },
            "scope_container": {
                "length_class": "novella",
                "estimated_chapters": 12
            },
            "carriers": {
                "characters": {
                    "Aldric": {
                        "location": "Dungeon",
                        "physical": "injured"
                    }
                }
            }
        }
    }
    
    recovery_file = test_project / "recovery_run.yaml"
    recovery_file.write_text(yaml.safe_dump(recovery_payload), encoding="utf-8")
    
    rc = main(["state", "confirm", str(test_project), str(recovery_file)])
    captured = capsys.readouterr()
    
    assert rc == 0
    assert "Success: Recovery candidate layers validated and merged" in captured.out
    
    # Check blueprint updates
    bp = StoryBlueprint.from_yaml(test_project / "blueprint.yaml")
    assert bp.identity.genre.value == "epic_fantasy"
    assert bp.identity.mode.value == "noir"
    assert bp.identity.length_class.value == "novella"
    assert bp.structure.estimated_chapters == 12
    
    # Check bible updates
    bible = StoryBible(test_project / "bible.json")
    assert bible.data["characters"]["Aldric"]["location"] == "Dungeon"
    assert bible.data["characters"]["Aldric"]["physical"] == "injured"


def test_state_confirm_ignores_legacy_scope_scale_key(test_project, capsys):
    """Verify old scope_scale recovery key is no longer accepted as Layer 3 state."""
    recovery_payload = {
        "candidate_locked_layers": {
            "scope_scale": {
                "length_class": "novella",
                "estimated_chapters": 12
            }
        }
    }

    recovery_file = test_project / "legacy_recovery_run.yaml"
    recovery_file.write_text(yaml.safe_dump(recovery_payload), encoding="utf-8")

    rc = main(["state", "confirm", str(test_project), str(recovery_file)])
    captured = capsys.readouterr()

    assert rc == 0
    assert "Success: Recovery candidate layers validated and merged" in captured.out

    bp = StoryBlueprint.from_yaml(test_project / "blueprint.yaml")
    assert bp.identity.length_class.value == "novel"
    assert bp.structure.estimated_chapters == 25


def test_state_prepare_with_dynamic_outline(test_project, capsys):
    """Verify that state prepare drafting/revision dynamically hydrates outline data."""
    outline_data = {
        "chapter_index": 1,
        "chapter_summary": "Aldric confronts the Dark Sorcerer.",
        "estimated_chapter_tension": 8,
        "scenes": [
            {
                "scene_id": "1",
                "pov_character": "Aldric",
                "location": "Throne Room",
                "summary": "The confrontation starts.",
                "key_events": [
                    "The Dark Sorcerer summons shadows.",
                    "Aldric unsheathes his silver sword."
                ],
                "character_state_changes": [
                    {
                        "character": "Aldric",
                        "field": "physical",
                        "before": "stable",
                        "after": "exhausted"
                    }
                ]
            }
        ]
    }
    
    chapter_dir = test_project / "chapters" / "01"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    outline_file = chapter_dir / "outline.yaml"
    outline_file.write_text(yaml.safe_dump(outline_data), encoding="utf-8")
    
    # 1. Test Drafting Phase Handoff
    rc = main(["state", "prepare", str(test_project), "drafting", "--scope", "chapter", "--chapter", "1"])
    captured = capsys.readouterr()
    
    assert rc == 0
    assert "Aldric confronts the Dark Sorcerer." in captured.out
    assert "Peak intensity: 8/10 at mid-scene" in captured.out
    assert "**Target POV Character**: Aldric" in captured.out
    assert "Scene 1 (Aldric @ Throne Room): The confrontation starts." in captured.out
    
    # 2. Test Revision Phase Handoff
    rc = main(["state", "prepare", str(test_project), "revision", "--scope", "chapter", "--chapter", "1"])
    captured = capsys.readouterr()
    
    assert rc == 0
    assert "Aldric confronts the Dark Sorcerer." in captured.out
    assert "Target: 8/10" in captured.out
    assert "The Dark Sorcerer summons shadows." in captured.out
    assert "Aldric unsheathes his silver sword." in captured.out
    assert "Aldric: physical = stable -> exhausted" in captured.out
