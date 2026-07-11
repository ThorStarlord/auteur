from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable
from typing import Literal

from auteur.blueprint import Genre, StoryMode
from auteur.genres.models import GenreContract
from pydantic import BaseModel, ConfigDict, Field, field_validator


@dataclass(frozen=True)
class CoreIdentityProfile:
    """Deterministic identity defaults for one emotional core."""

    display_name: str
    default_title: str
    default_mode: StoryMode
    progression: str
    secondary_emotions: tuple[str, ...] = ()
    avoided_experiences: tuple[str, ...] = ()


@dataclass(frozen=True)
class GenrePipelineSpec:
    """Operational contract for one built-in interactive genre pipeline."""

    genre: Genre
    slug: str
    core_ids: tuple[str, ...]
    default_core_id: str
    default_port: int
    browser_title: str
    template_factory: Callable[[str], Any]
    validate_choices: Callable[[Any, dict[int, dict[str, str]]], tuple[bool, list[str], list[str]]]
    contract_loader: Callable[[], GenreContract]
    identity_profile_factory: Callable[[str], CoreIdentityProfile]

    def __post_init__(self) -> None:
        if self.default_core_id not in self.core_ids:
            raise ValueError("default_core_id must be included in core_ids")


class PipelineOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    description: str = ""


class PipelineField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    options: list[PipelineOption] = Field(min_length=1)


class PipelinePhase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    number: int = Field(ge=1, le=9)
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    derived: bool = False
    derived_summary: str = ""
    fields: list[PipelineField] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class GenrePipelineDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    genre: Genre
    slug: str
    core_id: str
    browser_title: str
    default_title: str
    default_mode: StoryMode
    available_modes: list[StoryMode]
    phases: list[PipelinePhase] = Field(min_length=9, max_length=9)


class GenreSessionStatus(str, Enum):
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class GenreSession(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: Literal[1] = 1
    id: str = Field(min_length=1)
    genre: Genre
    core_id: str = Field(min_length=1)
    mode: StoryMode
    working_title: str = Field(min_length=1)
    choices: dict[int, dict[str, str]] = Field(default_factory=dict)
    status: GenreSessionStatus = GenreSessionStatus.INCOMPLETE
    created_at: datetime
    updated_at: datetime

    @field_validator("working_title")
    @classmethod
    def normalize_working_title(cls, value: str) -> str:
        title = value.strip()
        if not title:
            raise ValueError("working_title must not be blank")
        return title
