"""Tests for the unified Story State Manager — run_all_diagnostics()."""

from pathlib import Path

from auteur.bible import StoryBible
from auteur.structure import DiagnosticLayer, DiagnosticSeverity
from auteur.structure.bible_audit import audit_bible_locations
from auteur.structure.analyzer import analyze_structure, run_all_diagnostics

# Layer name map for assertions
_LAYER_NAMES = {
    DiagnosticLayer.TARGET_EXPERIENCE: "Target Experience",
    DiagnosticLayer.CONSTRAINTS: "Constraints",
    DiagnosticLayer.SCOPE: "Scope",
    DiagnosticLayer.STRUCTURAL_FORCES: "Structural Forces",
    DiagnosticLayer.THREADS: "Threads",
    DiagnosticLayer.THEME: "Theme",
    DiagnosticLayer.CARRIERS: "Carriers",
}


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


def test_unified_audit_merges_diagnostics_from_structure_and_bible(tmp_path):
    """Given a blueprint with a structural gap (missing story_engine)
    and a Bible with a carrier inconsistency (location teleportation),
    run_all_diagnostics should return diagnostics from both sources
    in a single combined list.
    """
    from auteur.blueprint import StoryBlueprint

    # --- Blueprint: no story_engine → triggers structure diagnostic ---
    blueprint = StoryBlueprint.model_validate(_minimal_blueprint_data())
    structure_diags = analyze_structure(blueprint)
    assert len(structure_diags) >= 1
    assert structure_diags[0].rule == "story_engine.missing"

    # --- Bible: location teleportation → triggers carriers diagnostic ---
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)
    bible.record_event(
        chapter_index=1,
        summary="Aldric enters the throne room.",
        deltas={
            "character_state_changes": [
                {"character": "Aldric", "field": "location", "before": None, "after": "Throne Room"},
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")
    bible.record_event(
        chapter_index=2,
        summary="Aldric wakes in the dungeon.",
        deltas={
            "character_state_changes": [
                {"character": "Aldric", "field": "location", "before": "Dungeon", "after": "Dungeon"},
            ]
        },
    )
    bible.upsert_character("Aldric", location="Dungeon")
    bible.save()

    bible_diags = audit_bible_locations(bible)
    assert len(bible_diags) >= 1
    assert bible_diags[0].rule == "carriers.location_teleportation"

    # --- Unified runner: should return both ---
    combined = run_all_diagnostics(blueprint, bible)

    # Must contain diagnostics from both sources
    layers = {d.layer for d in combined}
    assert DiagnosticLayer.STRUCTURAL_FORCES in layers, (
        "Expected a structure-layer diagnostic from the blueprint analyzer"
    )
    assert DiagnosticLayer.CARRIERS in layers, (
        "Expected a carriers-layer diagnostic from the Bible audit"
    )

    # Each diagnostic carries its source rule
    rules = {d.rule for d in combined}
    assert "story_engine.missing" in rules
    assert "carriers.location_teleportation" in rules


def test_layers_flag_filters_to_carriers_only(tmp_path):
    """Running auteur audit --layers 6 should show only carrier-layer
    (Layer 6) diagnostics, filtering out structure-layer diagnostics.
    """
    import subprocess
    import sys

    from auteur.blueprint import StoryBlueprint
    blueprint = StoryBlueprint.model_validate(_minimal_blueprint_data())
    yaml_path = tmp_path / "blueprint.yaml"
    import yaml
    yaml_path.write_text(yaml.safe_dump(blueprint.model_dump(mode="json"), sort_keys=False), encoding="utf-8")

    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)
    bible.record_event(
        chapter_index=1,
        summary="Aldric enters the throne room.",
        deltas={
            "character_state_changes": [
                {"character": "Aldric", "field": "location", "before": None, "after": "Throne Room"},
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")
    bible.record_event(
        chapter_index=2,
        summary="Aldric wakes in the dungeon.",
        deltas={
            "character_state_changes": [
                {"character": "Aldric", "field": "location", "before": "Dungeon", "after": "Dungeon"},
            ]
        },
    )
    bible.upsert_character("Aldric", location="Dungeon")
    bible.save()

    # Run auteur audit --layers 6 — should show only carriers
    result = subprocess.run(
        [sys.executable, "-m", "auteur.cli", "audit", str(tmp_path), "--layers", "6"],
        capture_output=True, text=True, timeout=10,
    )

    # Should exit successfully (returncode 0 or 1 — 1 means errors found)
    # The key assertion: stdout should contain carriers but not structure rules
    assert "location_teleportation" in result.stdout, (
        f"Expected carrier diagnostic, got stdout:\n{result.stdout}"
    )
    assert "story_engine.missing" not in result.stdout, (
        f"Structure diagnostic should be filtered out, got stdout:\n{result.stdout}"
    )
    assert "Found 1 unresolved error(s)" in result.stdout, (
        f"Expected 1 error (carriers only, structure filtered), got stdout:\n{result.stdout}"
    )


def test_grouped_report_shows_layer_headers(tmp_path, capsys):
    """Running auteur audit should group diagnostics by layer with headers
    like 'Layer 5 — Structural Forces (1 finding)'.
    """
    import yaml
    from auteur.blueprint import StoryBlueprint
    from auteur.cli import main

    blueprint = StoryBlueprint.model_validate(_minimal_blueprint_data())
    yaml_path = tmp_path / "blueprint.yaml"
    yaml_path.write_text(
        yaml.safe_dump(blueprint.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )

    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)
    bible.record_event(
        chapter_index=1,
        summary="Aldric enters the throne room.",
        deltas={
            "character_state_changes": [
                {"character": "Aldric", "field": "location", "before": None, "after": "Throne Room"},
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")
    bible.record_event(
        chapter_index=2,
        summary="Aldric wakes in the dungeon.",
        deltas={
            "character_state_changes": [
                {"character": "Aldric", "field": "location", "before": "Dungeon", "after": "Dungeon"},
            ]
        },
    )
    bible.upsert_character("Aldric", location="Dungeon")
    bible.save()

    rc = main(["audit", str(tmp_path)])

    captured = capsys.readouterr()
    assert "Layer 5 — Structural Forces (1 finding)" in captured.out, (
        f"Expected structural forces layer header in:\n{captured.out}"
    )
    assert "Layer 6 — Carriers (1 finding)" in captured.out, (
        f"Expected carriers layer header in:\n{captured.out}"
    )
    assert rc in (0, 1)
