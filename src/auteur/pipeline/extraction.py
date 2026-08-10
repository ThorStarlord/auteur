"""PipelineRunner — orchestrates planning, drafting, validation, iteration."""

from __future__ import annotations

from typing import Any




CARTOGRAPHER_TEMPERATURE = 0.4
CARTOGRAPHER_MAX_TOKENS = 4000



"""Data extraction — character state changes from Cartographer outlines."""


def extract_character_state_changes(outline: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten character_state_changes from all scenes in a Cartographer outline.

    Returns a list of {character, field, before, after} dicts.
    """
    changes: list[dict[str, Any]] = []
    for scene in outline.get("scenes", []) or []:
        for change in scene.get("character_state_changes", []) or []:
            changes.append(dict(change))
    return changes
