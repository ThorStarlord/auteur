"""Structured prior-author-intent contract for Story Discovery.

A DiscoveryBrief is input context, not a new semantic layer and not canonical state.
It separates what the author declared before candidate generation from fields an LLM
may propose inside a StoryIdentity candidate.
"""

from __future__ import annotations

from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, Field

from auteur.blueprint import Genre, StoryMedium, StoryMode, TargetAudience, TargetExperience
from auteur.narrative_ontology.architecture_preferences import NarrativeArchitecturePreferences


class DiscoveryBriefStoryType(BaseModel):
    """Optional StoryType commitments declared before Story Discovery runs."""

    genre: Genre | None = None
    medium: StoryMedium | None = None
    mode: StoryMode | None = None
    target_audience: TargetAudience | None = None


class DiscoveryBrief(BaseModel):
    """Author-declared optimization target for intent-aware Story Discovery.

    Omitted fields stay genuinely unspecified. Candidate-generated values must never
    be treated as substitutes for values omitted here.
    """

    premise: str = Field(min_length=1)
    story_type: DiscoveryBriefStoryType | None = None
    target_experience: TargetExperience | None = None
    architecture_preferences: NarrativeArchitecturePreferences | None = None
    hard_constraints: list[str] = Field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(data)

    def declared_intent(self) -> dict[str, object]:
        """Return only declared prior-author-intent evidence for prompts/artifacts."""
        return self.model_dump(mode="json", exclude_none=True, exclude_defaults=True)


class IntentAdequacy(BaseModel):
    """Deterministic adequacy result for comparative intent-aware ranking."""

    adequate: bool
    missing: list[str] = Field(default_factory=list)


def assess_intent_adequacy(brief: DiscoveryBrief) -> IntentAdequacy:
    """Check whether a brief justifies comparative recommendation language.

    Phase E founder adjudication identified genre/reader promise, audience, and the
    primary target experience as the minimum context needed to call one direction
    better suited to the story the author says they want. Other brief fields remain
    useful but optional.
    """

    missing: list[str] = []
    if brief.story_type is None or brief.story_type.genre is None:
        missing.append("story_type.genre")
    if brief.story_type is None or brief.story_type.target_audience is None:
        missing.append("story_type.target_audience")
    if brief.target_experience is None:
        missing.append("target_experience")
    return IntentAdequacy(adequate=not missing, missing=missing)
