"""Result models for pipeline operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from auteur.cartographer_models import PlanningCall
from auteur.critic import ValidationReport


@dataclass
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
    critic_proposal_paths: list[Path] = field(default_factory=list)
