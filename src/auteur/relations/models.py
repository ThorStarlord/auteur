from __future__ import annotations

from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


RELATION_METRICS = ("trust", "resentment", "dependency", "attraction", "fear", "obligation")


class RelationState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    from_character: str = Field(min_length=1)
    to_character: str = Field(min_length=1)
    public_role: str = ""
    private_truth: str = ""
    trust: int = Field(default=0, ge=0, le=100)
    resentment: int = Field(default=0, ge=0, le=100)
    dependency: int = Field(default=0, ge=0, le=100)
    attraction: int = Field(default=0, ge=0, le=100)
    fear: int = Field(default=0, ge=0, le=100)
    obligation: int = Field(default=0, ge=0, le=100)
    last_changed_in: str | None = None


class RelationMap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relations: list[RelationState] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_relation_ids(self) -> "RelationMap":
        ids = [relation.id for relation in self.relations]
        if len(ids) != len(set(ids)):
            raise ValueError("Relation IDs must be unique")
        return self

    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})

    def to_yaml(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        return path


class RelationChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation: str = Field(min_length=1)
    trust: int | None = None
    resentment: int | None = None
    dependency: int | None = None
    attraction: int | None = None
    fear: int | None = None
    obligation: int | None = None
    reason: str = ""

    def metric_deltas(self) -> dict[str, int]:
        return {
            metric: value
            for metric in RELATION_METRICS
            if (value := getattr(self, metric)) is not None
        }


class RelationChangeSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter: int = Field(ge=1)
    relation_changes: list[RelationChange] = Field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})

