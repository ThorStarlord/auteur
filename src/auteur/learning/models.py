from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LearningEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    concept: str
    event: Literal["introduced", "practiced", "demonstrated_independently", "needs_reinforcement"]
    source_ref: str
    observed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LearningState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    concepts: dict[str, set[str]] = Field(default_factory=dict)
    events: list[LearningEvent] = Field(default_factory=list)
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"

