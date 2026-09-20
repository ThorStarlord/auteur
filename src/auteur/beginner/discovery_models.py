"""Durable, noncanonical Story Discovery contracts for the beginner flow."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from auteur.identity import StoryIdentity


class DiscoveryRecommendationStatus(str, Enum):
    READY = "ready"
    NEEDS_AUTHOR_CHOICE = "needs_author_choice"
    UNAVAILABLE = "unavailable"


class DiscoveryDirection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    direction_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    identity_candidate: StoryIdentity
    architecture_summary: str = Field(min_length=1)
    tradeoffs: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    source_analysis_id: str = Field(min_length=1)
    source_component_ids: tuple[str, ...]
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"


class DiscoveryRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    recommendation_id: str = Field(min_length=1)
    source_analysis_id: str = Field(min_length=1)
    source_basis_fingerprint: str = Field(min_length=1)
    status: DiscoveryRecommendationStatus
    recommended_direction_id: str | None
    rationale: str = Field(min_length=1)
    directions: tuple[DiscoveryDirection, ...]
    selected_direction_id: str | None = None
    supersedes_recommendation_id: str | None = None
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        ids = [direction.direction_id for direction in self.directions]
        if len(ids) != len(set(ids)):
            raise ValueError("discovery direction IDs must be unique")
        known = set(ids)
        if self.status is DiscoveryRecommendationStatus.UNAVAILABLE:
            if self.directions or self.recommended_direction_id is not None or self.selected_direction_id is not None:
                raise ValueError("unavailable discovery cannot expose directions or selections")
        if self.status is DiscoveryRecommendationStatus.NEEDS_AUTHOR_CHOICE and self.recommended_direction_id is not None:
            raise ValueError("needs_author_choice cannot manufacture a recommended direction")
        if self.recommended_direction_id is not None and self.recommended_direction_id not in known:
            raise ValueError("recommended_direction_id must name a direction")
        if self.selected_direction_id is not None and self.selected_direction_id not in known:
            raise ValueError("selected_direction_id must name a direction")
        if any(direction.source_analysis_id != self.source_analysis_id for direction in self.directions):
            raise ValueError("every discovery direction must reference the recommendation analysis")
        return self

    def direction(self, direction_id: str) -> DiscoveryDirection:
        for direction in self.directions:
            if direction.direction_id == direction_id:
                return direction
        raise KeyError(direction_id)
