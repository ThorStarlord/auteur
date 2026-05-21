"""Layer 7 (Representation) outline carrier validation.

Validates scene cards in outline.yaml against the last known carrier state
in the StoryBible. Detects cases where an outline scene places a character
at a location that contradicts their most recent Bible event record.

This module complements ``bible_audit.py`` (Layer 6) which validates carrier
state transitions *within* the Bible event log. Layer 7 validates the
*forward-looking* scene outline against the *established* Bible carrier state.

Schema expected for the outline dict (loaded via ``load_outline``):
    {
        "scenes": [
            {
                "scene_id": str,
                "chapter": int,
                "characters": [
                    {"name": str, "location": str},
                    ...
                ]
            },
            ...
        ]
    }

See: CONTEXT.md — Layer 7 (Representation), GenreContractSnapshot
"""

from __future__ import annotations

from auteur.bible import StoryBible
from auteur.structure.bible_audit import BibleAuditDiagnostic
from auteur.structure.diagnostics import DiagnosticLayer, DiagnosticSeverity, RepairOptions


def load_outline(path: str) -> dict:
    """Load and parse an outline.yaml file.

    Args:
        path: Absolute or relative path to the outline.yaml file.

    Returns:
        Parsed outline as a dict with a ``scenes`` key.

    Raises:
        ValueError: If the file does not exist or contains invalid YAML.
    """
    import yaml
    from pathlib import Path

    outline_path = Path(path)
    if not outline_path.exists():
        raise ValueError(
            f"outline.yaml not found at path: {path}. "
            "Pass a valid path or omit --outline to skip Layer 7 validation."
        )

    try:
        text = outline_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Failed to parse outline.yaml at {path}: {exc}"
        ) from exc

    if data is None:
        return {"scenes": []}

    return data


def _build_last_known_locations(bible: StoryBible) -> dict[str, str]:
    """Extract each character's last known location from the Bible event log.

    Iterates events in order and tracks the ``after`` location from each
    character_state_changes entry where field == 'location'.

    Returns:
        Mapping of character name -> last known location string.
    """
    last_location: dict[str, str] = {}
    events: list[dict] = bible.data.get("events", [])

    for event in events:
        deltas: dict = event.get("deltas", {})
        changes: list[dict] = deltas.get("character_state_changes", [])

        for change in changes:
            if change.get("field") != "location":
                continue
            character: str = change.get("character", "")
            after: str | None = change.get("after")
            if character and after is not None:
                last_location[character] = after

    return last_location


def audit_outline_carriers(
    outline: dict | None,
    bible: StoryBible,
) -> list[BibleAuditDiagnostic]:
    """Validate scene cards in the outline against Bible carrier state (Layer 7).

    When ``outline`` is None, emits a single WARNING noting that Scene
    Representation validation was skipped.

    When ``outline`` is provided, checks every scene card's character location
    against the character's last known location from the Bible event log.
    A mismatch produces an ERROR diagnostic with
    rule='representation.carrier_location_mismatch'.

    Characters with no Bible history (first appearance) are never flagged.

    Args:
        outline: Parsed outline dict (from ``load_outline``), or None.
        bible: The StoryBible event log to compare against.

    Returns:
        List of BibleAuditDiagnostic findings (may be empty).
    """
    if outline is None:
        return [
            BibleAuditDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.REPRESENTATION,
                rule="representation.outline_missing",
                message=(
                    "Layer 7 (Scene Representation) validation was skipped because "
                    "no outline was provided. Run with --outline <path> to validate "
                    "scene carrier state against the Bible."
                ),
            )
        ]

    last_known = _build_last_known_locations(bible)
    diagnostics: list[BibleAuditDiagnostic] = []
    scenes: list[dict] = outline.get("scenes", [])

    for scene in scenes:
        scene_id: str = scene.get("scene_id", "<unknown>")
        chapter: int = scene.get("chapter", 0)
        characters: list[dict] = scene.get("characters", [])

        for char_entry in characters:
            name: str = char_entry.get("name", "")
            outline_location: str | None = char_entry.get("location")

            if not name or outline_location is None:
                continue

            if name not in last_known:
                # First appearance — no prior carrier state to compare against.
                continue

            bible_location = last_known[name]

            if outline_location != bible_location:
                diagnostics.append(
                    BibleAuditDiagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        layer=DiagnosticLayer.REPRESENTATION,
                        rule="representation.carrier_location_mismatch",
                        message=(
                            f"Scene '{scene_id}' (chapter {chapter}) places "
                            f"'{name}' at '{outline_location}', but the Bible "
                            f"records their last known location as '{bible_location}'. "
                            f"Add a transition scene or correct the outline."
                        ),
                        evidence=[
                            f"outline.scene_id = {scene_id}",
                            f"outline.character = {name}",
                            f"outline.location = {outline_location}",
                            f"bible.last_known_location[{name}] = {bible_location}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                f"Add a transition scene between the last Bible event "
                                f"and chapter {chapter} moving {name} from "
                                f"'{bible_location}' to '{outline_location}'."
                            ],
                            challenge_intent=[
                                f"Update scene '{scene_id}' to place {name} at "
                                f"'{bible_location}' (their last known location), "
                                f"or update the Bible event log to reflect the move."
                            ],
                        ),
                    )
                )

    return diagnostics
