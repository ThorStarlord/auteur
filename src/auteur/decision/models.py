"""Typed models for Author Decision Workspace."""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from auteur.workflow.models import AuthorityLevel


class DecisionTrigger(str, enum.Enum):
    IMPACT_FINDING = "impact_finding"
    CONVERGENCE_TARGET = "convergence_target"
    REASONING_CONFLICT = "reasoning_conflict"
    RECONCILIATION_CONFLICT = "reconciliation_conflict"
    ACCEPTANCE_BLOCKER = "acceptance_blocker"


class LifecycleState(str, enum.Enum):
    OPEN = "open"
    EVIDENCE_INCOMPLETE = "evidence_incomplete"
    CANDIDATES_REQUIRED = "candidates_required"
    EVALUATION_REQUIRED = "evaluation_required"
    COMPARISON_REQUIRED = "comparison_required"
    RECONCILIATION_REQUIRED = "reconciliation_required"
    AUTHOR_DECISION_REQUIRED = "author_decision_required"
    READY_FOR_ACCEPTANCE = "ready_for_acceptance"
    RESOLVED = "resolved"
    STALE = "stale"
    BLOCKED = "blocked"


class DecisionReadiness(str, enum.Enum):
    BLOCKED = "blocked"
    NEEDS_CANDIDATE = "needs_candidate"
    NEEDS_EVALUATION = "needs_evaluation"
    NEEDS_COMPARISON = "needs_comparison"
    NEEDS_RECONCILIATION = "needs_reconciliation"
    NEEDS_AUTHOR_DECISION = "needs_author_decision"
    READY_FOR_ACCEPTANCE = "ready_for_acceptance"
    RESOLVED = "resolved"
    STALE = "stale"


class EvidenceSource(str, enum.Enum):
    IMPACT = "impact"
    CONVERGENCE = "convergence"
    REASONING = "reasoning"
    RECONCILIATION = "reconciliation"
    WORKFLOW = "workflow"
    PROVENANCE = "provenance"


class EvidenceType(str, enum.Enum):
    STRUCTURAL_FACT = "structural_fact"
    IMPACT_FINDING = "impact_finding"
    OBLIGATION_STATUS = "obligation_status"
    PRESERVATION_STATUS = "preservation_status"
    REASONING_FINDING = "reasoning_finding"
    COMPARISON_RESULT = "comparison_result"
    RECONCILIATION_CONFLICT = "reconciliation_conflict"
    FRESHNESS_WARNING = "freshness_warning"
    ACCEPTANCE_REQUIREMENT = "acceptance_requirement"


class EvidenceClassification(str, enum.Enum):
    FACT = "fact"
    DERIVED_INFERENCE = "derived_inference"
    RECOMMENDATION = "recommendation"
    AUTHOR_CHOICE = "author_choice"
    CONTEXTUAL_OBSERVATION = "contextual_observation"


class EvidenceFreshness(str, enum.Enum):
    CURRENT = "current"
    STALE = "stale"
    UNKNOWN = "unknown"


class ConflictType(str, enum.Enum):
    FACTUAL = "factual"
    STRUCTURAL = "structural"
    INTERPRETIVE = "interpretive"
    CREATIVE = "creative"


class ResolutionBoundary(str, enum.Enum):
    RECOMPUTE = "recompute"
    RECONCILE = "reconcile"
    REQUEST_AUTHOR_CHOICE = "request_author_choice"
    BLOCK_ACCEPTANCE = "block_acceptance"


@dataclass(frozen=True)
class DecisionEvidence:
    """Single piece of evidence in a decision."""
    evidence_id: str  # uuid
    source_subsystem: EvidenceSource
    source_artifact_id: str

    claim: str
    evidence_type: EvidenceType
    classification: EvidenceClassification

    freshness: EvidenceFreshness
    confidence: str | None = None
    supporting_reference: str | None = None

    candidate_id: str | None = None
    authority: AuthorityLevel = AuthorityLevel.READ_ONLY

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        source_subsystem: EvidenceSource,
        source_artifact_id: str,
        claim: str,
        evidence_type: EvidenceType,
        classification: EvidenceClassification,
        freshness: EvidenceFreshness = EvidenceFreshness.CURRENT,
        confidence: str | None = None,
        supporting_reference: str | None = None,
        candidate_id: str | None = None,
        authority: AuthorityLevel = AuthorityLevel.READ_ONLY,
    ) -> DecisionEvidence:
        return cls(
            evidence_id=str(uuid.uuid4()),
            source_subsystem=source_subsystem,
            source_artifact_id=source_artifact_id,
            claim=claim,
            evidence_type=evidence_type,
            classification=classification,
            freshness=freshness,
            confidence=confidence,
            supporting_reference=supporting_reference,
            candidate_id=candidate_id,
            authority=authority,
        )


@dataclass(frozen=True)
class UnresolvedChoice:
    """An author decision point that has not yet been resolved."""
    choice_id: str
    question: str
    options: list[str] | None = None  # None = open-ended

    affected_candidates: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    tradeoffs: list[str] = field(default_factory=list)

    required_authority: AuthorityLevel = AuthorityLevel.AUTHORITY_BEARING
    blocking_status: bool = True

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        question: str,
        options: list[str] | None = None,
        affected_candidates: list[str] | None = None,
        supporting_evidence: list[str] | None = None,
        tradeoffs: list[str] | None = None,
        required_authority: AuthorityLevel = AuthorityLevel.AUTHORITY_BEARING,
        blocking_status: bool = True,
    ) -> UnresolvedChoice:
        return cls(
            choice_id=str(uuid.uuid4()),
            question=question,
            options=options,
            affected_candidates=affected_candidates or [],
            supporting_evidence=supporting_evidence or [],
            tradeoffs=tradeoffs or [],
            required_authority=required_authority,
            blocking_status=blocking_status,
        )


@dataclass(frozen=True)
class CandidateSummary:
    """Multidimensional candidate summary without full content."""
    candidate_id: str
    status: str  # CandidateStatus from convergence
    freshness: EvidenceFreshness
    lineage: str | None = None

    obligations_satisfied: list[str] = field(default_factory=list)
    obligations_unsatisfied: list[str] = field(default_factory=list)
    preserved_regions: list[str] = field(default_factory=list)

    continuity_conflicts: list[str] = field(default_factory=list)
    reasoning_evidence: list[str] = field(default_factory=list)  # reference IDs
    reconciliation_status: str | None = None
    acceptance_blockers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DecisionConflict:
    """Explicit conflict in decision evidence with type and resolution boundary."""
    conflict_id: str
    title: str
    conflict_type: ConflictType = ConflictType.FACTUAL
    resolution_boundary: ResolutionBoundary = ResolutionBoundary.RECOMPUTE
    source_subsystem: EvidenceSource | None = None
    claim_a: str = ""
    claim_b: str = ""
    claims: list[dict[str, Any]] = field(default_factory=list)
    affected_candidates: list[str] = field(default_factory=list)
    resolution_options: list[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        title: str,
        conflict_type: ConflictType = ConflictType.FACTUAL,
        resolution_boundary: ResolutionBoundary = ResolutionBoundary.RECOMPUTE,
        source_subsystem: EvidenceSource | None = None,
        claim_a: str = "",
        claim_b: str = "",
        claims: list[dict[str, Any]] | None = None,
        affected_candidates: list[str] | None = None,
        resolution_options: list[str] | None = None,
    ) -> DecisionConflict:
        return cls(
            conflict_id=str(uuid.uuid4()),
            title=title,
            conflict_type=conflict_type,
            resolution_boundary=resolution_boundary,
            source_subsystem=source_subsystem,
            claim_a=claim_a,
            claim_b=claim_b,
            claims=claims or [],
            affected_candidates=affected_candidates or [],
            resolution_options=resolution_options or [],
        )


@dataclass(frozen=True)
class DecisionAction:
    """Recommended or available action for this decision."""
    action_id: str
    title: str
    reason: str
    command: str | None = None
    prerequisites: list[str] = field(default_factory=list)
    safe_to_execute: bool = False
    authority_level: AuthorityLevel = AuthorityLevel.READ_ONLY
    expected_result_state: str = ""


@dataclass(frozen=True)
class AuthorDecision:
    """Complete decision with all evidence and options."""
    decision_id: str
    project: str
    chapter_index: int
    target_artifact_id: str

    scene_id: str | None = None
    beat_ids: list[str] = field(default_factory=list)

    # Trigger
    trigger_type: DecisionTrigger = DecisionTrigger.IMPACT_FINDING
    trigger_ids: list[str] = field(default_factory=list)

    # Evidence
    candidates: list[CandidateSummary] = field(default_factory=list)
    evidence: list[DecisionEvidence] = field(default_factory=list)
    conflicts: list[DecisionConflict] = field(default_factory=list)
    unresolved_choices: list[UnresolvedChoice] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)

    # State
    readiness: DecisionReadiness = DecisionReadiness.BLOCKED
    lifecycle_state: LifecycleState = LifecycleState.OPEN
    freshness: EvidenceFreshness = EvidenceFreshness.CURRENT

    # Authority
    authority_required: AuthorityLevel = AuthorityLevel.AUTHORITY_BEARING
    safe_actions: list[DecisionAction] = field(default_factory=list)

    # Schema versioning (v0.8.0+)
    schema_version: str = "decision-snapshot-v1"
    snapshot_id: str | None = None
    preceding_snapshot_id: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_snapshot: dict[str, Any] = field(default_factory=dict)

    def is_stale(self) -> bool:
        return self.freshness == EvidenceFreshness.STALE or self.lifecycle_state == LifecycleState.STALE

    def is_ready_for_acceptance(self) -> bool:
        return self.readiness == DecisionReadiness.READY_FOR_ACCEPTANCE

    def has_open_choices(self) -> bool:
        return any(c.blocking_status for c in self.unresolved_choices)


@dataclass(frozen=True)
class AcceptancePreparation:
    """Enhanced acceptance readiness review with prerequisites, tradeoffs, and impact."""
    decision_id: str
    candidate_id: str
    is_ready: bool
    blockers: list[str] = field(default_factory=list)
    satisfied_prerequisites: list[str] = field(default_factory=list)
    unsatisfied_prerequisites: list[str] = field(default_factory=list)
    candidate_tradeoffs: list[str] = field(default_factory=list)
    reasoning_evidence_summary: dict[str, Any] = field(default_factory=dict)
    reconciliation_evidence_summary: dict[str, Any] = field(default_factory=dict)
    downstream_impact: Any | None = None  # ImpactPreview
    stale_after_acceptance: list[str] = field(default_factory=list)
    acceptance_request: dict[str, Any] | None = None
    verification_results: dict[str, bool] = field(default_factory=dict)
    will_change_canonical: bool = False
    affected_downstream: list[str] = field(default_factory=list)
    prepared_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
