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



"""LLM utility wrappers for pipeline operations."""


class _CountingClient:
    def __init__(self, inner: LLMClient):
        self._inner = inner
        self._lock = Lock()
        self.input_tokens = 0
        self.output_tokens = 0

    def complete(self, req: LLMRequest) -> LLMResponse:
        resp = self._inner.complete(req)
        with self._lock:
            self.input_tokens += resp.input_tokens
            self.output_tokens += resp.output_tokens
        return resp


