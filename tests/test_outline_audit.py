"""Tests for Layer 7 (Representation) outline carrier validation — AUTEUR-002.

Validates that audit_outline_carriers() detects scene cards in outline.yaml
that place characters at locations inconsistent with their last known Bible
carrier state.
"""

from pathlib import Path

import pytest

from auteur.bible import StoryBible
from auteur.structure import DiagnosticLayer, DiagnosticSeverity, run_all_diagnostics
from auteur.structure.outline_audit import audit_outline_carriers, load_outline


# ============================================================================
# Test 2a — missing outline emits Layer 7 WARNING
# ============================================================================


def test_run_all_diagnostics_no_outline_emits_representation_warning(tmp_path):
    """AUTEUR-002 RED 2a: when outline=None, a single REPRESENTATION WARNING
    with rule='representation.outline_missing' must be emitted."""
    from auteur.blueprint import StoryBlueprint

    SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)

    diagnostics = run_all_diagnostics(blueprint, bible, outline=None)

    layer7 = [d for d in diagnostics if d.layer == DiagnosticLayer.REPRESENTATION]
    assert len(layer7) == 1
    assert layer7[0].rule == "representation.outline_missing"
    assert layer7[0].severity == DiagnosticSeverity.WARNING


# ============================================================================
# Test 2b — location mismatch detection
# ============================================================================


def _bible_with_aldric_at_throne_room(tmp_path: Path) -> StoryBible:
    """Bible fixture: Aldric's last known location is Throne Room after chapter 1."""
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)
    bible.record_event(
        chapter_index=1,
        summary="Aldric confronts the king.",
        deltas={
            "character_state_changes": [
                {
                    "character": "Aldric",
                    "field": "location",
                    "before": None,
                    "after": "Throne Room",
                }
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")
    bible.save()
    return bible


def _outline_with_aldric_at_dungeon() -> dict:
    """Outline fixture: chapter 2 scene places Aldric at Dungeon — contradicts Bible."""
    return {
        "scenes": [
            {
                "scene_id": "ch2-s1",
                "chapter": 2,
                "characters": [
                    {"name": "Aldric", "location": "Dungeon"},
                ],
            }
        ]
    }


def _outline_with_aldric_at_throne_room() -> dict:
    """Outline fixture: chapter 2 scene places Aldric at Throne Room — matches Bible."""
    return {
        "scenes": [
            {
                "scene_id": "ch2-s1",
                "chapter": 2,
                "characters": [
                    {"name": "Aldric", "location": "Throne Room"},
                ],
            }
        ]
    }


def test_audit_outline_carriers_location_mismatch(tmp_path):
    """AUTEUR-002 RED 2b: when the outline places a character at a location that
    contradicts their last Bible carrier state, an ERROR is emitted with
    rule='representation.carrier_location_mismatch'."""
    bible = _bible_with_aldric_at_throne_room(tmp_path)
    outline = _outline_with_aldric_at_dungeon()

    diagnostics = audit_outline_carriers(outline, bible)

    assert len(diagnostics) == 1
    d = diagnostics[0]
    assert d.rule == "representation.carrier_location_mismatch"
    assert d.severity == DiagnosticSeverity.ERROR
    assert d.layer == DiagnosticLayer.REPRESENTATION
    assert "Aldric" in d.message
    assert "Throne Room" in d.message
    assert "Dungeon" in d.message


# ============================================================================
# Test 2c — aligned outline produces no errors
# ============================================================================


def test_audit_outline_carriers_aligned_produces_no_errors(tmp_path):
    """AUTEUR-002 RED 2c: when the outline places characters at locations that
    match their Bible carrier state, no diagnostics are emitted."""
    bible = _bible_with_aldric_at_throne_room(tmp_path)
    outline = _outline_with_aldric_at_throne_room()

    diagnostics = audit_outline_carriers(outline, bible)

    errors = [d for d in diagnostics if d.severity == DiagnosticSeverity.ERROR]
    assert errors == []


# ============================================================================
# Test 2d — character with no Bible history is not flagged
# ============================================================================


def test_audit_outline_carriers_new_character_not_flagged(tmp_path):
    """A character appearing in the outline who has no Bible event history
    (first appearance) should not produce a mismatch diagnostic."""
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)
    bible.save()

    outline = {
        "scenes": [
            {
                "scene_id": "ch1-s1",
                "chapter": 1,
                "characters": [
                    {"name": "Mara", "location": "Market"},
                ],
            }
        ]
    }

    diagnostics = audit_outline_carriers(outline, bible)
    assert diagnostics == []


# ============================================================================
# Test 2e — multiple characters, only mismatching ones flagged
# ============================================================================


def test_audit_outline_carriers_flags_only_mismatching_characters(tmp_path):
    """When multiple characters are in the outline, only those whose outline
    location contradicts their Bible carrier state should be flagged."""
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)
    bible.record_event(
        chapter_index=1,
        summary="Aldric at Throne Room. Mara at Market.",
        deltas={
            "character_state_changes": [
                {"character": "Aldric", "field": "location", "before": None, "after": "Throne Room"},
                {"character": "Mara", "field": "location", "before": None, "after": "Market"},
            ]
        },
    )
    bible.upsert_character("Aldric", location="Throne Room")
    bible.upsert_character("Mara", location="Market")
    bible.save()

    outline = {
        "scenes": [
            {
                "scene_id": "ch2-s1",
                "chapter": 2,
                "characters": [
                    {"name": "Aldric", "location": "Dungeon"},   # MISMATCH
                    {"name": "Mara", "location": "Market"},       # OK
                ],
            }
        ]
    }

    diagnostics = audit_outline_carriers(outline, bible)

    assert len(diagnostics) == 1
    assert "Aldric" in diagnostics[0].message
    assert "Mara" not in diagnostics[0].message


# ============================================================================
# Test 2f — load_outline raises ValueError on malformed YAML
# ============================================================================


def test_load_outline_raises_on_malformed_yaml(tmp_path):
    """load_outline must raise ValueError with a descriptive message when the
    file contains invalid YAML."""
    bad_yaml = tmp_path / "outline.yaml"
    bad_yaml.write_text("scenes: [\n  - bad: [unclosed", encoding="utf-8")

    with pytest.raises(ValueError, match="outline"):
        load_outline(str(bad_yaml))


def test_load_outline_raises_on_missing_file(tmp_path):
    """load_outline must raise ValueError when the file does not exist."""
    with pytest.raises(ValueError, match="not found"):
        load_outline(str(tmp_path / "nonexistent.yaml"))
