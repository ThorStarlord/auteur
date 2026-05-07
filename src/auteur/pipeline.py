"""PipelineRunner — orchestrates one planning pass.

Phase 1: only the Cartographer runs. The runner returns the rendered prompts
so a caller can decide how to invoke an LLM (or hand them off to tests).

Phase 2 will extend this to: Cartographer outline -> Bard draft -> Critic
validation -> iterate. The shape of `plan_chapter` should not change; new
methods like `draft_chapter` and `validate_chapter` will be added beside it.
"""

from __future__ import annotations

from dataclasses import dataclass

from auteur.bible import StoryBible
from auteur.blueprint import PlanningCall, StoryBlueprint
from auteur.cartographer import render_cartographer_prompt


@dataclass
class PlanResult:
    call: PlanningCall
    system_prompt: str
    user_message: str


class PipelineRunner:
    def __init__(self, blueprint: StoryBlueprint, bible: StoryBible | None = None):
        self.blueprint = blueprint
        self.bible = bible

    def plan_chapter(self, chapter_index: int) -> PlanResult:
        call = PlanningCall.for_chapter(self.blueprint, chapter_index)
        system, user = render_cartographer_prompt(call)
        return PlanResult(call=call, system_prompt=system, user_message=user)
