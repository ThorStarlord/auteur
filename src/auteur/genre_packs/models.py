"""Typed Pydantic models for Genre Pack schemas, recommendations, and commitments."""

from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class RuleStrength(str, Enum):
    HARD_CONSTRAINT = "HARD_CONSTRAINT"
    STRONG_DEFAULT = "STRONG_DEFAULT"
    COMMON_PATTERN = "COMMON_PATTERN"
    OPTIONAL_TECHNIQUE = "OPTIONAL_TECHNIQUE"
    BOUNDARY_WARNING = "BOUNDARY_WARNING"
    INTENTIONAL_SUBVERSION_POINT = "INTENTIONAL_SUBVERSION_POINT"


class AdherencePosture(str, Enum):
    CONVENTIONAL = "conventional"
    FLEXIBLE = "flexible"
    REVISIONIST = "revisionist"
    SUBVERSIVE = "subversive"
    DECONSTRUCTIVE = "deconstructive"


class GenreErrorCode(str, Enum):
    PACK_NOT_FOUND = "PACK_NOT_FOUND"
    PACK_INVALID = "PACK_INVALID"
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    RECOMMENDATION_NOT_FOUND = "RECOMMENDATION_NOT_FOUND"
    RECOMMENDATION_STALE = "RECOMMENDATION_STALE"
    ACCEPTANCE_REQUIRED = "ACCEPTANCE_REQUIRED"
    INVALID_OVERRIDE = "INVALID_OVERRIDE"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"
    ALREADY_ACCEPTED = "ALREADY_ACCEPTED"


class GenrePackError(Exception):
    """Domain exception for Genre Pack failures."""

    def __init__(self, code: GenreErrorCode, message: str, details: dict[str, Any] | None = None):
        super().__init__(f"[{code.value}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}


class AudiencePromise(BaseModel):
    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    strength: RuleStrength = RuleStrength.STRONG_DEFAULT
    applicable_profiles: list[str] = Field(default_factory=list)


class EmotionalTarget(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    default_weight: float = Field(default=1.0, ge=0.0, le=1.0)


class NarrativeEngineFamily(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    core_conflict: str = Field(min_length=1)


class CoreConvention(BaseModel):
    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    strength: RuleStrength = RuleStrength.STRONG_DEFAULT
    diagnostic_severity: str = "WARNING"
    revision_direction: str = ""


class SceneFunction(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    narrative_impact: str = Field(min_length=1)


class ConflictFamily(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ResolutionPattern(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class EscalationPattern(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class BoundaryRule(BaseModel):
    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    strength: RuleStrength = RuleStrength.BOUNDARY_WARNING
    warning_message: str = Field(min_length=1)


class FailureModeDefinition(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    diagnostic_severity: str = "WARNING"
    revision_direction: str = Field(min_length=1)


class EvaluationRule(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    severity: str = "WARNING"
    evidence_expectation: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    revision_direction: str = Field(min_length=1)


class RevisionStrategy(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class SubgenreProfile(BaseModel):
    profile_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    base_pack_id: str = Field(min_length=1)
    primary_emotions: list[str] = Field(default_factory=list)
    preferred_narrative_engines: list[str] = Field(default_factory=list)
    preferred_framing: str = "romantic"
    resolution_expectations: list[str] = Field(default_factory=list)
    boundary_warnings: list[str] = Field(default_factory=list)
    evaluation_priorities: list[str] = Field(default_factory=list)


class GenrePack(BaseModel):
    pack_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    schema_version: int = Field(default=1, ge=1)
    description: str = Field(min_length=1)
    audience_promises: list[AudiencePromise] = Field(default_factory=list)
    emotional_targets: list[EmotionalTarget] = Field(default_factory=list)
    narrative_engines: list[NarrativeEngineFamily] = Field(default_factory=list)
    core_conventions: list[CoreConvention] = Field(default_factory=list)
    scene_functions: list[SceneFunction] = Field(default_factory=list)
    conflict_families: list[ConflictFamily] = Field(default_factory=list)
    framing_modes: list[str] = Field(default_factory=list)
    subgenre_profiles: list[SubgenreProfile] = Field(default_factory=list)
    resolution_patterns: list[ResolutionPattern] = Field(default_factory=list)
    escalation_patterns: list[EscalationPattern] = Field(default_factory=list)
    boundary_rules: list[BoundaryRule] = Field(default_factory=list)
    failure_modes: list[FailureModeDefinition] = Field(default_factory=list)
    evaluation_rules: list[EvaluationRule] = Field(default_factory=list)
    revision_strategies: list[RevisionStrategy] = Field(default_factory=list)


class FramingCommitment(BaseModel):
    primary: str = "romantic"
    secondary: list[str] = Field(default_factory=list)


class ResolutionContractCommitment(BaseModel):
    pattern: str = "transformative_resolution"
    required_outcomes: list[str] = Field(default_factory=list)
    rejected_outcomes: list[str] = Field(default_factory=list)


class GenreAuthorOverride(BaseModel):
    target_expectation: str = Field(min_length=1)
    recommended_value: str = ""
    replacement_value: str = Field(min_length=1)
    author_rationale: str = Field(min_length=1)
    replacement_function: str = Field(default="")


class GenreProfileCommitment(BaseModel):
    primary_pack_id: str = Field(min_length=1)
    primary_pack_version: str = Field(min_length=1)
    pack_content_hash: str = Field(min_length=1)
    primary_profile_id: str = Field(min_length=1)
    secondary_genres: list[str] = Field(default_factory=list)
    accepted_target_emotions: dict[str, float] = Field(default_factory=dict)
    accepted_narrative_engine: str = Field(min_length=1)
    accepted_framing: FramingCommitment = Field(default_factory=FramingCommitment)
    accepted_resolution_contract: ResolutionContractCommitment = Field(default_factory=ResolutionContractCommitment)
    adherence_posture: AdherencePosture = AdherencePosture.CONVENTIONAL
    source_recommendation_id: str | None = None
    author_overrides: list[GenreAuthorOverride] = Field(default_factory=list)
    accepted_at: str | None = None


class RejectedProfileAnalysis(BaseModel):
    profile_id: str
    display_name: str
    why_rejected: str
    premise_adjustment_to_enable: str


class GenreRecommendation(BaseModel):
    recommendation_id: str = Field(min_length=1)
    recommended_pack_id: str = Field(min_length=1)
    recommended_pack_version: str = Field(min_length=1)
    pack_content_hash: str = Field(min_length=1)
    recommended_profile_id: str = Field(min_length=1)
    recommended_profile_display_name: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    best_basis: str = "GENRE_ALIGNED"
    why_this_is_best: str = Field(min_length=1)
    supporting_evidence: list[str] = Field(default_factory=list)
    recommended_emotional_targets: dict[str, float] = Field(default_factory=dict)
    recommended_narrative_engine: str = Field(min_length=1)
    recommended_framing: FramingCommitment = Field(default_factory=FramingCommitment)
    recommended_resolution_contract: ResolutionContractCommitment = Field(default_factory=ResolutionContractCommitment)
    rejected_profiles: list[RejectedProfileAnalysis] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    questions_or_uncertainties: list[str] = Field(default_factory=list)
    created_at: str | None = None
