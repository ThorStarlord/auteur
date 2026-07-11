from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator
from auteur.universe.constraints import StructuredConstraint


class SettingType(str, Enum):
    SINGLE_WORLD = "single_world"
    MULTI_WORLD = "multi_world"
    DIMENSION_HOPPING = "dimension_hopping"
    TIME_TRAVEL = "time_travel"
    PARALLEL_UNIVERSES = "parallel_universes"


class ConstraintSeverity(str, Enum):
    REQUIRED = "required"
    WARNING = "warning"
    INFO = "info"


class SettingProfile(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    setting_type: SettingType
    primary_location: str = Field(min_length=1)
    known_locations: list[str] = Field(default_factory=list)
    worldbuilding_scope: Optional[str] = None


class MythologyProfile(BaseModel):
    core_lore: str = Field(default="", min_length=0)
    pantheon_or_cosmology: str = Field(default="", min_length=0)
    key_historical_events: list[str] = Field(default_factory=list)


class TimelineProfile(BaseModel):
    current_era: str = Field(min_length=1)
    era_description: str = Field(default="", min_length=0)
    years_of_history: int = Field(default=0, ge=0)


class CrossStoryConstraint(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    rule: str = Field(min_length=1)
    applies_to_all_stories: bool = True
    severity: ConstraintSeverity = ConstraintSeverity.REQUIRED


class UniverseIdentity(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(min_length=1)
    slug: str = Field(min_length=1, pattern=r"^[a-z0-9_-]+$")
    description: str = Field(default="", min_length=0)
    setting_profile: SettingProfile
    magic_system: str = Field(default="", min_length=0)
    core_mythology: str = Field(default="", min_length=0)
    timeline: TimelineProfile
    forbidden_elements: list[str] = Field(default_factory=list)
    required_elements: list[str] = Field(default_factory=list)
    cross_story_constraints: list[CrossStoryConstraint] = Field(default_factory=list)
    structured_constraints: list[StructuredConstraint] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_name_not_empty(self) -> UniverseIdentity:
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty or whitespace-only")
        return self

    def to_yaml(self, path: Path) -> None:
        """Write UniverseIdentity to YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(mode="json"), f, sort_keys=False, default_flow_style=False)

    @classmethod
    def from_yaml(cls, path: Path) -> UniverseIdentity:
        """Load UniverseIdentity from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
