"""Typed, noncanonical premise-interpretation contracts for the beginner flow."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from auteur.story_design_packs.models import PackProvenance


class ArchitectureFacet(str, Enum):
    GENRE_CONSTELLATION = "genre_constellation"
    NARRATIVE_ENGINE = "narrative_engine"
    CHARACTER_FUNCTION = "character_function"
    AESTHETIC_FRAMING = "aesthetic_framing"
    TROPE_FAMILY = "trope_family"
    RELATIONSHIP_DYNAMIC = "relationship_dynamic"
    SETTING_WORLD = "setting_world"
    THEME_MOTIF = "theme_motif"


class ArchitectureCertainty(str, Enum):
    CLEAR = "clear"
    LIKELY = "likely"
    UNCERTAIN = "uncertain"


class ArchitectureDerivation(str, Enum):
    PREMISE_EXPLICIT = "premise_explicit"
    CURATED_MATCH = "curated_match"
    MODEL_INFERENCE = "model_inference"
    AUTHOR_ADDED = "author_added"


class ArchitectureRole(str, Enum):
    PRIMARY = "primary"
    SUPPORTING = "supporting"
    FLAVOR = "flavor"


class ArchitectureActivation(str, Enum):
    ACTIVE = "active"
    SUPPRESSED = "suppressed"


class ArchitectureReviewState(str, Enum):
    UNREVIEWED = "unreviewed"
    AUTHOR_CONFIRMED = "author_confirmed"
    AUTHOR_MODIFIED = "author_modified"


class ArchitectureEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_kind: Literal["premise", "genre_pack", "design_pack", "accepted_state"]
    label: str = Field(min_length=1)
    excerpt: str | None = None
    source_ref: str | None = None


class ArchitectureAlternative(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    label: str = Field(min_length=1)
    rationale: str = Field(min_length=1)


class ArchitectureAdjustment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    action: Literal[
        "confirm",
        "suppress",
        "restore",
        "rename",
        "choose_alternative",
        "set_role",
        "add",
    ]
    component_id: str = Field(min_length=1)
    before_label: str | None = None
    after_label: str | None = None
    rationale: str | None = None
    invalidated_discovery_recommendation_id: str | None = None


class ArchitectureComponent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    component_id: str = Field(min_length=1)
    facet: ArchitectureFacet
    label: str = Field(min_length=1)
    derivation: ArchitectureDerivation
    normalized_concept: str | None = None
    role: ArchitectureRole = ArchitectureRole.SUPPORTING
    certainty: ArchitectureCertainty
    activation: ArchitectureActivation = ArchitectureActivation.ACTIVE
    review_state: ArchitectureReviewState = ArchitectureReviewState.UNREVIEWED
    rationale: str = Field(min_length=1)
    evidence: tuple[ArchitectureEvidence, ...] = ()
    alternatives: tuple[ArchitectureAlternative, ...] = ()
    source_provenance: tuple[PackProvenance, ...] = ()
    author_rationale: str | None = None
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"

    @model_validator(mode="after")
    def alternatives_require_uncertainty(self) -> Self:
        if self.alternatives and self.certainty is not ArchitectureCertainty.UNCERTAIN:
            raise ValueError("alternatives are only valid for uncertain components")
        return self


class NarrativeArchitectureAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    analysis_id: str = Field(min_length=1)
    schema_version: Literal[1] = 1
    premise_fingerprint: str = Field(min_length=1)
    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    provider_id: str | None = None
    model_id: str | None = None
    summary: str = Field(min_length=1)
    components: tuple[ArchitectureComponent, ...]
    source_provenance: tuple[PackProvenance, ...] = ()
    adjustments: tuple[ArchitectureAdjustment, ...] = ()
    stale: bool = False
    availability_note: str | None = None
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"

    @model_validator(mode="after")
    def validate_component_set(self) -> Self:
        ids = [component.component_id for component in self.components]
        if len(ids) != len(set(ids)):
            raise ValueError("architecture component IDs must be unique")
        primary_facets: set[ArchitectureFacet] = set()
        for component in self.components:
            if component.role is not ArchitectureRole.PRIMARY:
                continue
            if component.facet in primary_facets:
                raise ValueError(f"only one primary component is allowed for {component.facet.value}")
            primary_facets.add(component.facet)
        return self

    def component(self, component_id: str) -> ArchitectureComponent:
        for component in self.components:
            if component.component_id == component_id:
                return component
        raise KeyError(component_id)
