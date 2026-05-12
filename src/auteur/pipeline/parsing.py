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



"""YAML parsing for Cartographer outlines."""


def _parse_outline_yaml(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        first_nl = stripped.find("\n")
        last_fence = stripped.rfind("```")
        if first_nl != -1 and last_fence > first_nl:
            stripped = stripped[first_nl + 1 : last_fence].strip()
    try:
        data = yaml.safe_load(stripped)
    except yaml.YAMLError as exc:
        raise ValueError(f"Cartographer YAML parse error: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Cartographer response is not a YAML mapping.")
    from auteur.cartographer_outline import CartographerOutline
    try:
        CartographerOutline.model_validate(data)
    except Exception as exc:
        raise ValueError(
            f"Cartographer outline validation error: {exc}"
        ) from exc
    return data