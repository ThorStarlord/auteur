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



"""Result models for pipeline operations."""


class PlanResult:
    call: PlanningCall
    system_prompt: str
    user_message: str


@dataclass

class DraftResult:
    chapter_index: int
    accepted: bool
    iterations: int
    final_path: Path | None
    last_validation: ValidationReport | None
    conflict_report: str | None
    total_input_tokens: int
    total_output_tokens: int


