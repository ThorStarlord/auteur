"""Structured prior-author-intent contract for Story Discovery.

A DiscoveryBrief is input context, not a new semantic layer and not canonical state.
It separates what the author declared before candidate generation from fields an LLM
may propose inside a StoryIdentity candidate.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
    def from_yaml(cls, path: str | Path) -> "DiscoveryBrief":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(data)

    @staticmethod
    def _explicit_fields(model: BaseModel) -> dict[str, Any]:
        return model.model_dump(
            mode="json",
            include=model.model_fields_set,
            exclude_none=True,
        )

    def declared_intent(self) -> dict[str, object]:
        """Return only prior intent that was explicitly present in the brief.

        This intentionally avoids serializing model defaults as author commitments.
        The existing TargetExperience model may backfill compatibility fields during
        validation; those fields can appear when needed to represent the same declared
        promise, but unrelated omitted optional fields remain absent.
        """
        declared: dict[str, object] = {"premise": self.premise}
        if self.story_type is not None:
            story_type = self._explicit_fields(self.story_type)
            if story_type:
                declared["story_type"] = story_type
        if self.target_experience is not None:
            target_experience = self._explicit_fields(self.target_experience)
            if target_experience:
                declared["target_experience"] = target_experience
        if self.architecture_preferences is not None:
            preferences = self._explicit_fields(self.architecture_preferences)
            if preferences:
                declared["architecture_preferences"] = preferences
        if "hard_constraints" in self.model_fields_set:
            declared["hard_constraints"] = list(self.hard_constraints)
        return declared


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
