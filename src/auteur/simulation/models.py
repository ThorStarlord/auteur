"""Typed models for Counterfactual Narrative Planning."""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ScenarioState(str, enum.Enum):
    CREATED = "created"
    VALIDATING = "validating"
    READY = "ready"
    PROJECTING = "projecting"
    PROJECTED = "projected"
    COMPARABLE = "comparable"
    STALE = "stale"
    BLOCKED = "blocked"
    PROMOTED = "promoted"
    DISCARDED = "discarded"
    FAILED = "failed"


class ConsequenceCategory(str, enum.Enum):
    KNOWN = "known"
    DERIVED = "derived"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class ConfidenceLevel(str, enum.Enum):
    CERTAIN = "certain"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNDETERMINED = "undetermined"


class AssumptionCategory(str, enum.Enum):
    STRUCTURAL = "structural"
    PROCEDURAL = "procedural"
    SEMANTIC = "semantic"


SCHEMA_VERSION = "counterfactual-v1"
"""Current schema version for simulation artifacts."""


# ---------------------------------------------------------------------------
# Identity helpers
# ---------------------------------------------------------------------------


def _stable_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def compute_baseline_id(project: str, timestamp: str) -> str:
    return _stable_id("baseline", project, timestamp)


def compute_scenario_id(
    project: str, baseline_id: str, decision_id: str,
    candidate_id: str, assumptions_hash: str,
) -> str:
    return _stable_id(
        "scenario", project, baseline_id, decision_id, candidate_id, assumptions_hash,
    )


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CounterfactualBaseline:
    """Immutable snapshot of real project state."""
    baseline_id: str
    project: str
    plan_id: str = ""
    decision_ids: list[str] = field(default_factory=list)
    accepted_pointers: dict[str, str] = field(default_factory=dict)
    canonical_pointers: dict[str, str] = field(default_factory=dict)
    provenance_hashes: dict[str, str] = field(default_factory=dict)
    review_session_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = SCHEMA_VERSION
    tool_version: str = "0.11.0"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_id": self.baseline_id,
            "project": self.project,
            "plan_id": self.plan_id,
            "decision_ids": self.decision_ids,
            "accepted_pointers": self.accepted_pointers,
            "canonical_pointers": self.canonical_pointers,
            "provenance_hashes": self.provenance_hashes,
            "review_session_ids": self.review_session_ids,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ScenarioAssumption:
    """An explicit assumption underlying a projection."""
    assumption_id: str
    description: str
    is_default: bool = True
    category: AssumptionCategory = AssumptionCategory.STRUCTURAL


@dataclass(frozen=True)
class CandidateSnapshot:
    """Immutable snapshot of a candidate at scenario creation time."""
    candidate_id: str
    decision_id: str
    label: str = ""
    content_hash: str = ""
    freshness: str = "current"


@dataclass(frozen=True)
class ProjectedConsequence:
    """A single projected consequence of a candidate choice."""
    consequence_id: str
    target: str
    description: str
    classification: ConsequenceCategory = ConsequenceCategory.UNKNOWN
    confidence: ConfidenceLevel = ConfidenceLevel.UNDETERMINED
    supporting_evidence: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    reversibility: str = "unknown"
    projected_action: str = ""


@dataclass(frozen=True)
class ProjectedDecisionChange:
    """Projected change to a decision's state."""
    decision_id: str
    projected_state: str  # resolved, remains_open, blocked, unblocked, stale, newly_required
    trigger_consequence_id: str = ""
    classification: ConsequenceCategory = ConsequenceCategory.DERIVED
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH


@dataclass(frozen=True)
class ProjectedArtifactChange:
    """Projected change to an artifact's state."""
    artifact_id: str
    projected_state: str  # stale, unchanged, requires_regeneration
    trigger_consequence_id: str = ""
    classification: ConsequenceCategory = ConsequenceCategory.DERIVED
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH


@dataclass(frozen=True)
class ProjectedReviewChange:
    """Projected change to a review session's state."""
    session_id: str
    projected_state: str  # valid, stale, superseded, requires_new
    trigger_consequence_id: str = ""
    classification: ConsequenceCategory = ConsequenceCategory.DERIVED
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH


@dataclass(frozen=True)
class ProjectedMilestoneChange:
    """Projected change to a milestone's state."""
    milestone_id: str
    current_state: str
    projected_state: str
    reason: str = ""
    classification: ConsequenceCategory = ConsequenceCategory.DERIVED
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH


@dataclass(frozen=True)
class ProjectedPlan:
    """Projected project plan under a scenario."""
    plan_id: str
    open_decision_count: int = 0
    blocked_milestone_count: int = 0
    milestones: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    cycles: list[list[str]] = field(default_factory=list)


@dataclass(frozen=True)
class ProjectedCriticalPath:
    """Projected blocking critical path under a scenario."""
    path_id: str
    ordered_node_ids: list[str] = field(default_factory=list)
    blocked_milestone_ids: list[str] = field(default_factory=list)
    cumulative_leverage: float = 0.0
    authority_required_steps: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScenarioComparison:
    """Semantic comparison of two counterfactual scenarios."""
    comparison_id: str
    scenario_a_id: str
    scenario_b_id: str
    shared_consequences: list[ProjectedConsequence] = field(default_factory=list)
    a_only_consequences: list[ProjectedConsequence] = field(default_factory=list)
    b_only_consequences: list[ProjectedConsequence] = field(default_factory=list)
    opposing_consequences: list[tuple[ProjectedConsequence, ProjectedConsequence]] = field(default_factory=list)
    milestone_differences: list[dict] = field(default_factory=list)
    critical_path_differences: dict[str, Any] = field(default_factory=dict)
    evidence_asymmetry: str = ""
    uncertainty_asymmetry: str = ""
    unknowns: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = SCHEMA_VERSION


@dataclass(frozen=True)
class ScenarioPromotionRequest:
    """Request to promote a scenario into author review."""
    scenario_id: str
    baseline_id: str
    decision_id: str
    candidate_id: str
    review_session_id: str = ""


@dataclass(frozen=True)
class ScenarioPromotionResult:
    """Result of a promotion attempt."""
    success: bool
    review_session_id: str = ""
    scenario_id: str = ""
    error: str = ""


@dataclass(frozen=True)
class CounterfactualScenario:
    """Complete counterfactual scenario."""
    scenario_id: str
    decision_id: str
    candidate_id: str
    baseline_id: str
    state: ScenarioState = ScenarioState.CREATED
    candidate_snapshot: CandidateSnapshot | None = None
    assumptions: list[ScenarioAssumption] = field(default_factory=list)
    assumptions_hash: str = ""
    projected_consequences: list[ProjectedConsequence] = field(default_factory=list)
    projected_decisions: list[ProjectedDecisionChange] = field(default_factory=list)
    projected_artifacts: list[ProjectedArtifactChange] = field(default_factory=list)
    projected_reviews: list[ProjectedReviewChange] = field(default_factory=list)
    projected_milestones: list[ProjectedMilestoneChange] = field(default_factory=list)
    projected_plan: ProjectedPlan | None = None
    projected_critical_path: ProjectedCriticalPath | None = None
    uncertainty_summary: str = ""
    source_hashes: dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = SCHEMA_VERSION
    tool_version: str = "0.11.0"
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "decision_id": self.decision_id,
            "candidate_id": self.candidate_id,
            "baseline_id": self.baseline_id,
            "state": self.state.value if hasattr(self.state, 'value') else str(self.state),
            "assumptions": [{
                "assumption_id": a.assumption_id,
                "description": a.description,
                "is_default": a.is_default,
                "category": a.category.value if hasattr(a.category, 'value') else str(a.category),
            } for a in self.assumptions],
            "assumptions_hash": self.assumptions_hash,
            "projected_consequences": [{
                "consequence_id": c.consequence_id,
                "target": c.target,
                "description": c.description,
                "classification": c.classification.value if hasattr(c.classification, 'value') else str(c.classification),
                "confidence": c.confidence.value if hasattr(c.confidence, 'value') else str(c.confidence),
            } for c in self.projected_consequences],
            "uncertainty_summary": self.uncertainty_summary,
            "source_hashes": self.source_hashes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
        }
