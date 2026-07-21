"""Typed models for convergence workflow."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CandidateStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    REGISTERED = "registered"
    EVALUATED = "evaluated"
    RECONCILIATION_PROPOSED = "reconciliation_proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    STALE = "stale"


class ObligationSource(str, Enum):
    STORY_IDENTITY = "story_identity"
    STRUCTURE = "structure"
    CHAPTER_OUTLINE = "chapter_outline"
    SCENE_PURPOSE = "scene_purpose"
    BEAT_DECLARATION = "beat_declaration"
    CHARACTER_STATE = "character_state"
    SETUP_PAYOFF = "setup_payoff"
    CONTINUITY = "continuity"
    WORLD_RULE = "world_rule"
    UPSTREAM_DECISION = "upstream_decision"
    IMPACT_FINDING = "impact_finding"
    DERIVED_OBSERVATION = "derived_observation"


class ObligationKind(str, Enum):
    REQUIRED = "required"
    ADVISORY = "advisory"
    DERIVED = "derived"


class PreservationStatus(str, Enum):
    PRESERVE = "preserve"
    PRESERVE_WITH_REVIEW = "preserve_with_review"
    PARTIAL_PRESERVATION = "partial_preservation"
    REGENERATE = "regenerate"
    UNKNOWN = "unknown"


class TargetScope(str, Enum):
    CHAPTER = "chapter"
    SCENE = "scene"
    BEAT_RANGE = "beat_range"
    STRUCTURAL_OBLIGATION = "structural_obligation"


class GenerationStrategy(str, Enum):
    MINIMAL_REPAIR = "minimal_repair"
    CONTINUITY_PRESERVING = "continuity_preserving"
    STRUCTURAL_ALTERNATIVE = "structural_alternative"
    FULL_REGENERATION = "full_regeneration"


class RevisionTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project: str
    scope: TargetScope
    chapter_index: int
    scene_id: str | None = None
    beat_ids: list[str] = Field(default_factory=list)
    source_artifact: str = ""
    affected_artifact: str = ""
    impact_finding_id: str = ""
    current_accepted_artifact: str = ""
    target_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    resolved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SourceObligation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    obligation_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    source: ObligationSource
    kind: ObligationKind = ObligationKind.REQUIRED
    description: str = ""
    scope: str = ""
    authority: str = "canonical"
    evidence: str = ""
    freshness: str = "fresh"
    source_artifact_id: str = ""
    structured_condition: dict[str, Any] = Field(default_factory=dict)


class PreservedRegion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    region_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    scene_id: str = ""
    beat_id: str = ""
    section_id: str = ""
    artifact_reference: str = ""
    status: PreservationStatus = PreservationStatus.PRESERVE
    reason: str = ""


class CandidateLineage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parent_candidate_id: str | None = None
    source_artifact_id: str = ""
    source_artifact_hash: str = ""
    generation_method: str = ""


class CandidateRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    target_id: str = ""
    status: CandidateStatus = CandidateStatus.DRAFT
    lineage: CandidateLineage = Field(default_factory=CandidateLineage)
    obligations: list[str] = Field(default_factory=list)
    preserved_regions: list[PreservedRegion] = Field(default_factory=list)
    content_artifact_ref: str = ""
    content_artifact_hash: str = ""
    provenance: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    authority: str = "derived"
    canonical: bool = False
    evaluation_references: list[str] = Field(default_factory=list)
    freshness: str = "fresh"
    generation_strategy: str = ""
    obligations_satisfied: list[str] = Field(default_factory=list)
    obligations_unsatisfied: list[str] = Field(default_factory=list)


class ComparisonDimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    candidate_a_value: str = ""
    candidate_b_value: str = ""
    advantage: str = ""
    evidence: str = ""


class ConflictFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conflict_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    candidate_ids: list[str] = Field(default_factory=list)
    description: str = ""
    severity: str = "warning"
    recommended_action: str = ""
    dimension: str = ""


class CandidateComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comparison_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    target_id: str = ""
    candidate_ids: list[str] = Field(default_factory=list)
    dimensions: list[ComparisonDimension] = Field(default_factory=list)
    conflicts: list[ConflictFinding] = Field(default_factory=list)
    recommended_candidate_id: str = ""
    recommendation_disclaimer: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReconciliationProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    target_id: str = ""
    candidate_ids: list[str] = Field(default_factory=list)
    source_obligations: list[SourceObligation] = Field(default_factory=list)
    preserved_regions: list[PreservedRegion] = Field(default_factory=list)
    satisfied_obligations: list[str] = Field(default_factory=list)
    unsatisfied_obligations: list[str] = Field(default_factory=list)
    conflicts: list[ConflictFinding] = Field(default_factory=list)
    continuity_risks: list[str] = Field(default_factory=list)
    recommended_edits: list[str] = Field(default_factory=list)
    authority_required_choices: list[str] = Field(default_factory=list)
    proposed_downstream_invalidations: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    canonical: bool = False


class ConvergenceAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    label: str = ""
    command: str = ""
    authority: str = "read_only"
    safe_to_execute: bool = False
    reason: str = ""


class ConvergenceState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project: str = ""
    target: RevisionTarget | None = None
    obligations: list[SourceObligation] = Field(default_factory=list)
    preserved_regions: list[PreservedRegion] = Field(default_factory=list)
    candidates: list[CandidateRef] = Field(default_factory=list)
    comparisons: list[CandidateComparison] = Field(default_factory=list)
    proposals: list[ReconciliationProposal] = Field(default_factory=list)
    actions: list[ConvergenceAction] = Field(default_factory=list)
    status_summary: str = ""
    recommended_next_action: str = ""
    authority_required: str = "read_only"


class RevisionScope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: RevisionTarget
    obligations: list[SourceObligation] = Field(default_factory=list)
    preserved: list[PreservedRegion] = Field(default_factory=list)
