from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from auteur.story_design_packs.models import PackProvenance


class DecisionStage(str, Enum):
    DISCOVER = "discover"
    STORY_IDENTITY = "story_identity"
    STORY_STRUCTURE = "story_structure"


class LifecycleStatus(str, Enum):
    NOT_STARTED = "not_started"
    WORKING = "working"
    COMPLETE = "complete"
    BLOCKED = "blocked"


class StageAvailability(str, Enum):
    AVAILABLE = "available"
    LOCKED = "locked"


class RevisionRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    revision: int = Field(ge=1)


class AcceptedMilestoneReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    milestone_id: str = Field(min_length=1)
    revision: RevisionRef
    accepted_content: str | None = None
    fingerprint: str | None = None
    selected_option: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_snapshot_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for name in ("accepted_content", "fingerprint", "selected_option"):
                if name in data and data[name] is not None and type(data[name]) is not str:
                    raise ValueError(f"{name} must be a string or None")
        return data


class WorkingDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: DecisionStage
    question: str = Field(min_length=1)
    options: list[str] = Field(default_factory=list)
    selected_option: str | None = None

    @model_validator(mode="after")
    def selected_option_is_declared(self) -> Self:
        if self.selected_option is not None and self.selected_option not in self.options:
            raise ValueError("selected_option must be one of options")
        return self


class DimensionCategory(str, Enum):
    PRIMARY_ENGINE = "PRIMARY_ENGINE"
    GENRE_SUBGENRE = "GENRE_SUBGENRE"
    EMOTIONAL_AESTHETIC = "EMOTIONAL_AESTHETIC"
    RELATIONSHIP_THEMATIC = "RELATIONSHIP_THEMATIC"
    SETTING_WORLD = "SETTING_WORLD"


class DimensionOrigin(str, Enum):
    DETECTED_FROM_PACK = "DETECTED_FROM_PACK"
    INFERRED_FROM_STORY = "INFERRED_FROM_STORY"
    AUTHOR_DEFINED = "AUTHOR_DEFINED"
    AUTHOR_MODIFIED = "AUTHOR_MODIFIED"


class DimensionStatus(str, Enum):
    DETECTED = "DETECTED"
    PROPOSED = "PROPOSED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class MappingDisposition(str, Enum):
    MAPS_TO_CANON = "MAPS_TO_CANON"
    CONTRIBUTES_TO_CANON = "CONTRIBUTES_TO_CANON"
    GUIDANCE_CONTEXT = "GUIDANCE_CONTEXT"
    PROVENANCE_ONLY = "PROVENANCE_ONLY"
    REQUIRES_AUTHOR_DECISION = "REQUIRES_AUTHOR_DECISION"
    NOT_REPRESENTABLE_BY_CURRENT_DOMAIN = "NOT_REPRESENTABLE_BY_CURRENT_DOMAIN"
    NOT_RELEVANT_TO_THIS_MILESTONE = "NOT_RELEVANT_TO_THIS_MILESTONE"


class MappingReviewStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    OVERRIDDEN = "OVERRIDDEN"


class MappingStrength(str, Enum):
    DIRECT_DOMAIN_MAPPING = "DIRECT_DOMAIN_MAPPING"
    SUPPORTED_CONTRIBUTION = "SUPPORTED_CONTRIBUTION"
    CONTEXTUAL_INFLUENCE = "CONTEXTUAL_INFLUENCE"
    UNRESOLVED_INTERPRETATION = "UNRESOLVED_INTERPRETATION"


class EvidenceClass(str, Enum):
    DOMAIN_CONTRACT = "DOMAIN_CONTRACT"
    PACK_METADATA = "PACK_METADATA"
    CURATED_COMPOSITION_RULE = "CURATED_COMPOSITION_RULE"
    AUTHOR_CONFIRMED_DECISION = "AUTHOR_CONFIRMED_DECISION"
    EXISTING_CANONICAL_STATE = "EXISTING_CANONICAL_STATE"


class WorkingDimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension_id: str = Field(min_length=1)
    category: DimensionCategory
    origin: DimensionOrigin
    status: DimensionStatus
    label: str = Field(min_length=1)
    author_rationale: str | None = None
    detection_evidence: tuple[str, ...] = ()
    source_provenance: tuple[PackProvenance, ...] = ()
    confirmed_by_author: bool = False


class CompositionTension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tension_id: str = Field(min_length=1)
    dimension_ids: tuple[str, ...] = ()
    explanation: str = Field(min_length=1)
    affected_decision_or_contract: str = Field(min_length=1)
    acknowledged: bool = False
    blocks_acceptance: bool = False


class OverrideValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preflight_result: str = Field(min_length=1)
    final_result: str | None = None
    valid: bool
    diagnostic: str | None = None
    accepted_value: str | None = None


class AuthorOverride(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original_value: str = Field(min_length=1)
    replacement_value: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    affected_dimension_ids: tuple[str, ...] = ()
    validation: OverrideValidationResult


class MappingRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mapping_id: str = Field(min_length=1)
    source_dimension_id: str = Field(min_length=1)
    source_category: DimensionCategory
    source_origin: DimensionOrigin
    source_provenance: tuple[PackProvenance, ...] = ()
    destination_field: str | None = None
    proposed_value: str | None = None
    contribution: str | None = None
    mapping_strength: MappingStrength
    evidence_class: EvidenceClass
    disposition: MappingDisposition
    review_status: MappingReviewStatus = MappingReviewStatus.PROPOSED
    rationale: str = Field(min_length=1)
    unmapped_remainder: tuple[str, ...] = ()
    author_override: AuthorOverride | None = None


class UnmappedRemainder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    remainder_id: str = Field(min_length=1)
    dimension_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    acknowledged: bool = False
    blocks_acceptance: bool = False


class WorkingComposition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str = Field(min_length=1)
    composition_id: str = Field(min_length=1)
    schema_version: int = Field(ge=1)
    revision_id: str | None = None
    base_canonical_refs: tuple[str, ...] = ()
    source_provenance: tuple[PackProvenance, ...] = ()
    dimensions: tuple[WorkingDimension, ...]
    tensions: tuple[CompositionTension, ...] = ()
    mapping_records: tuple[MappingRecord, ...] = ()
    unmapped_remainders: tuple[UnmappedRemainder, ...] = ()


class DimensionProposalSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposals: tuple[WorkingDimension, ...]
    source_provenance: tuple[PackProvenance, ...] = ()


class MappingDomainContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vocabulary: dict[str, tuple[str, ...]]
    source_provenance: tuple[PackProvenance, ...] = ()


class StageStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: DecisionStage
    lifecycle: LifecycleStatus
    availability: StageAvailability
    working_decision: WorkingDecision | None = None

    @model_validator(mode="after")
    def require_consistent_working_decision(self) -> Self:
        if self.working_decision is not None and self.working_decision.stage != self.stage:
            raise ValueError("working_decision.stage must match stage")
        return self


class SessionEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    session_version: int = Field(default=0, ge=0)
    project_id: str = Field(min_length=1)
    guidance_genre: str = Field(min_length=1)
    premise: str = Field(min_length=1)
    stages: dict[DecisionStage, StageStatus]
    accepted_milestones: list[AcceptedMilestoneReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_consistent_stage_graph(self) -> Self:
        expected_stages = set(DecisionStage)
        actual_stages = set(self.stages)
        if actual_stages != expected_stages or len(self.stages) != len(expected_stages):
            raise ValueError("stages must contain exactly one status for every decision stage")
        for stage, status in self.stages.items():
            if status.stage != stage:
                raise ValueError("StageStatus.stage must match its stage mapping key")
        return self

    @classmethod
    def new(cls, project_id: str, guidance_genre: str, premise: str) -> SessionEnvelope:
        return cls(
            project_id=project_id,
            guidance_genre=guidance_genre,
            premise=premise,
            stages={
                DecisionStage.DISCOVER: StageStatus(
                    stage=DecisionStage.DISCOVER,
                    lifecycle=LifecycleStatus.WORKING,
                    availability=StageAvailability.AVAILABLE,
                ),
                DecisionStage.STORY_IDENTITY: StageStatus(
                    stage=DecisionStage.STORY_IDENTITY,
                    lifecycle=LifecycleStatus.NOT_STARTED,
                    availability=StageAvailability.LOCKED,
                ),
                DecisionStage.STORY_STRUCTURE: StageStatus(
                    stage=DecisionStage.STORY_STRUCTURE,
                    lifecycle=LifecycleStatus.NOT_STARTED,
                    availability=StageAvailability.LOCKED,
                ),
            },
        )


class MutationCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str = Field(min_length=1)
    expected_session_version: int = Field(ge=0)
    command_id: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class CreateWorkspaceCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
