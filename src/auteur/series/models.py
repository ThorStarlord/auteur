from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from auteur.blueprint import TargetExperience
from auteur.identity import HighLevelCentralEngine, StoryType


class SeriesType(str, Enum):
    DUOLOGY = "duology"
    TRILOGY = "trilogy"
    QUARTET = "quartet"
    LIMITED_SERIES = "limited_series"
    ONGOING = "ongoing"


class DependencyType(str, Enum):
    SETS_UP = "sets_up"
    PAYS_OFF = "pays_off"
    DEPENDS_ON = "depends_on"
    PRESSURES = "pressures"
    CONTRADICTS = "contradicts"
    TRANSFORMS = "transforms"


class SeriesFunction(str, Enum):
    QUESTION = "question"
    COMPLICATION = "complication"
    COLLAPSE = "collapse"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    COOLDOWN = "cooldown"


class SeriesScope(str, Enum):
    PERSONAL = "personal"
    VILLAGE = "village"
    CITY = "city"
    NATIONAL = "national"
    CIVILIZATIONAL = "civilizational"
    COSMIC = "cosmic"


class GlobalArc(BaseModel):
    model_config = ConfigDict(extra="forbid")

    beginning: str
    midpoint: str
    ending: str | None = None


class BookPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_number: int = Field(ge=1)
    title: str = Field(min_length=1)
    series_function: SeriesFunction
    core_answer: str = Field(min_length=1)
    target_experience: TargetExperience
    story_type: StoryType
    central_engine: HighLevelCentralEngine
    series_threads_carried: list[str] = Field(default_factory=list)
    required_setups: list[str] = Field(default_factory=list)
    required_payoffs: list[str] = Field(default_factory=list)
    scope: SeriesScope = SeriesScope.PERSONAL
    climax_intensity: int = Field(default=5, ge=0, le=10)


class CharacterArc(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    character: str
    start_state: str
    end_state: str
    planned_completion_book: int = Field(ge=1)
    book_states: dict[str, str] = Field(default_factory=dict)
    transitions: dict[str, str] = Field(default_factory=dict)


class RelationshipArc(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    participants: list[str] = Field(min_length=2)
    start_state: str
    end_state: str
    book_states: dict[str, str] = Field(default_factory=dict)


class FactionArc(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    faction: str
    start_state: str
    end_state: str
    book_states: dict[str, str] = Field(default_factory=dict)


class SeriesMystery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    question: str
    introduced_book: int = Field(ge=1)
    expected_payoff_book: int = Field(ge=1)
    actual_payoff_book: int | None = Field(default=None, ge=1)


class DependencyEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    target: str
    type: DependencyType
    description: str = ""


class SeriesIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    series_type: SeriesType
    book_count: int | None = Field(default=None, ge=1)
    core_question: str
    target_experience: TargetExperience
    global_arc: GlobalArc
    book_plans: list[BookPlan] = Field(min_length=1)
    character_arcs: list[CharacterArc] = Field(default_factory=list)
    relationship_arcs: list[RelationshipArc] = Field(default_factory=list)
    faction_arcs: list[FactionArc] = Field(default_factory=list)
    mysteries: list[SeriesMystery] = Field(default_factory=list)
    dependency_edges: list[DependencyEdge] = Field(default_factory=list)
    recurring_symbols: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_series_shape(self) -> Self:
        count = len(self.book_plans)
        expected = {
            SeriesType.DUOLOGY: 2,
            SeriesType.TRILOGY: 3,
            SeriesType.QUARTET: 4,
        }.get(self.series_type)
        if expected is not None and count != expected:
            raise ValueError(f"{self.series_type.value} requires exactly {expected} books")
        if self.series_type == SeriesType.LIMITED_SERIES:
            if self.book_count is None:
                raise ValueError("limited_series requires book_count")
            if count != self.book_count:
                raise ValueError("limited_series book_count must match book_plans")
        if self.series_type == SeriesType.ONGOING and count < 2:
            raise ValueError("ongoing series requires at least 2 books")

        numbers = [book.book_number for book in self.book_plans]
        if numbers != list(range(1, count + 1)):
            raise ValueError("book_plans must be numbered contiguously from 1")

        valid_nodes = self.node_ids()
        for edge in self.dependency_edges:
            if edge.source not in valid_nodes or edge.target not in valid_nodes:
                raise ValueError(f"dependency edge references unknown node: {edge.source}->{edge.target}")
        return self

    def node_ids(self) -> set[str]:
        ids = {"series"}
        ids.update(f"book_{book.book_number}" for book in self.book_plans)
        ids.update(arc.id for arc in self.character_arcs)
        ids.update(arc.id for arc in self.relationship_arcs)
        ids.update(arc.id for arc in self.faction_arcs)
        ids.update(mystery.id for mystery in self.mysteries)
        for book in self.book_plans:
            ids.update(book.required_setups)
            ids.update(book.required_payoffs)
            ids.update(book.series_threads_carried)
        return ids

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(data)

    def to_yaml(self, path: str | Path) -> None:
        Path(path).write_text(
            yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
