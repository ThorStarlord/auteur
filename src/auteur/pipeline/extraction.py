"""PipelineRunner — orchestrates planning, drafting, validation, iteration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Callable

import yaml

from auteur.bard import draft_chapter as bard_draft
from auteur.bible import StoryBible
from auteur.cartographer_models import PlanningCall
from auteur.blueprint import StoryBlueprint
from auteur.cartographer import render_cartographer_prompt
from auteur.critic import ValidationReport, run_critics
from auteur.llm import LLMClient, LLMRequest, LLMResponse


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
