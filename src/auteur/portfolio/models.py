"""Typed models for Narrative Decision Portfolio."""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class PortfolioState(str, enum.Enum):
    CREATED = "created"
    VALIDATING = "validating"
    READY = "ready"
    GENERATING = "generating"
    GENERATED = "generated"
    PROJECTING = "projecting"
    PROJECTED = "projected"
    COMPARABLE = "comparable"
    STALE = "stale"
    BLOCKED = "blocked"
    PARTIALLY_PROMOTED = "partially_promoted"
    PROMOTED = "promoted"
    DISCARDED = "discarded"
    FAILED = "failed"


class PortfolioScenarioState(str, enum.Enum):
    CREATED = "created"
    PROJECTED = "projected"
    FAILED = "failed"


class ConstraintType(str, enum.Enum):
    HARD_INCOMPATIBILITY = "hard_incompatibility"
    REQUIRES = "requires"
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"
    IMPLIES = "implies"
    SOFT_TENSION = "soft_tension"
    COMPLEMENTARY = "complementary"
    SHARED_ASSUMPTION = "shared_assumption"


class ConstraintStrength(str, enum.Enum):
    HARD = "hard"
    SOFT = "soft"
    INFORMATIONAL = "informational"


class CrossEffectType(str, enum.Enum):
    INVALIDATES = "invalidates"
    UNLOCKS = "unlocks"
    INCREASES_COST = "increases_cost"
    REDUCES_REPAIR = "reduces_repair"
    JOINTLY_UNLOCKS_MILESTONE = "jointly_unlocks_milestone"
    CREATES_NEW_DECISION = "creates_new_decision"


class ContradictionClass(str, enum.Enum):
    HARD_CONTRADICTION = "hard_contradiction"
    SOFT_TENSION = "soft_tension"
    UNRESOLVED = "unresolved"


class FrontierDimension(str, enum.Enum):
    KNOWN_BLOCKER_COUNT = "known_blockers"
    PROJECTED_STALE_ARTIFACTS = "stale_artifacts"
    AUTHORITY_DECISIONS = "authority_decisions"
    UNCERTAINTY_COUNT = "uncertainty"
    BLOCKED_MILESTONES = "blocked_milestones"
    OPTIONALITY = "optionality"
    REVERSIBILITY = "reversibility"


SCHEMA_VERSION = "portfolio-v1"
MAX_DECISIONS_DEFAULT = 5
MAX_CANDIDATES_PER_DECISION_DEFAULT = 4
MAX_COMBINATIONS_DEFAULT = 100


def _stable_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class PortfolioDecision:
    """A decision and its candidate set in a portfolio."""
    decision_id: str
    candidate_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PortfolioConstraint:
    """A constraint between decisions/candidates in a portfolio."""
    constraint_id: str
    constraint_type: ConstraintType
    strength: ConstraintStrength = ConstraintStrength.HARD
    source_decisions: list[str] = field(default_factory=list)
    source_candidates: list[str] = field(default_factory=list)
    target_decisions: list[str] = field(default_factory=list)
    target_candidates: list[str] = field(default_factory=list)
    reason: str = ""
    evidence_classification: str = "derived"
    confidence: str = "high"
    supporting_references: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExcludedCombination:
    """A combination excluded during generation with reason."""
    assignment: dict[str, str]  # decision_id -> candidate_id
    reason: str
    constraint_id: str = ""
    evidence: str = ""


@dataclass(frozen=True)
class CrossDecisionEffect:
    """An effect that emerges from combining specific decisions."""
    effect_id: str
    effect_type: CrossEffectType
    participating_decisions: list[str] = field(default_factory=list)
    participating_candidates: list[str] = field(default_factory=list)
    description: str = ""
    evidence_classification: str = "derived"
    confidence: str = "high"
    projected_consequence: str = ""


@dataclass(frozen=True)
class PortfolioScenario:
    """One candidate combination within a portfolio."""
    scenario_id: str
    portfolio_id: str
    assignment: dict[str, str] = field(default_factory=dict)  # decision_id -> candidate_id
    state: PortfolioScenarioState = PortfolioScenarioState.CREATED
    component_scenario_ids: list[str] = field(default_factory=list)
    cross_effects: list[CrossDecisionEffect] = field(default_factory=list)
    stale_artifact_count: int = 0
    open_decision_count: int = 0
    blocked_milestone_count: int = 0
    uncertainty_summary: str = ""
    error: str = ""


@dataclass(frozen=True)
class PortfolioFrontier:
    """Non-dominated operational tradeoff frontier."""
    frontier_id: str
    portfolio_id: str
    dimensions: list[str] = field(default_factory=list)
    non_dominated_ids: list[str] = field(default_factory=list)
    explanations: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = SCHEMA_VERSION


@dataclass(frozen=True)
class OptionalityReport:
    """Remaining viable decisions and reversibility."""
    report_id: str
    remaining_candidates: dict[str, list[str]] = field(default_factory=dict)
    irreversible_decisions: list[str] = field(default_factory=list)
    preserved_scenarios: list[str] = field(default_factory=list)
    excluded_scenarios: list[str] = field(default_factory=list)
    summary: str = ""
@dataclass(frozen=True)
class NarrativePortfolio:
    """Complete narrative decision portfolio."""
    portfolio_id: str
    baseline_id: str
    decisions: list[PortfolioDecision] = field(default_factory=list)
    constraints: list[PortfolioConstraint] = field(default_factory=list)
    state: PortfolioState = PortfolioState.CREATED
    max_combinations: int = MAX_COMBINATIONS_DEFAULT
    theoretical_count: int = 0
    valid_count: int = 0
    excluded_combinations: list[ExcludedCombination] = field(default_factory=list)
    scenarios: list[PortfolioScenario] = field(default_factory=list)
    projections: list[PortfolioScenario] = field(default_factory=list)
    frontiers: list[PortfolioFrontier] = field(default_factory=list)
    source_hashes: dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = SCHEMA_VERSION
    tool_version: str = "0.12.0"
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "portfolio_id": self.portfolio_id,
            "baseline_id": self.baseline_id,
            "state": self.state.value,
            "decisions": [{"decision_id": d.decision_id, "candidates": d.candidate_ids} for d in self.decisions],
            "max_combinations": self.max_combinations,
            "theoretical_count": self.theoretical_count,
            "valid_count": self.valid_count,
            "scenarios": [{"scenario_id": s.scenario_id, "portfolio_id": s.portfolio_id, "assignment": s.assignment}
                          for s in self.scenarios],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NarrativePortfolio:
        decisions = [
            PortfolioDecision(decision_id=d["decision_id"], candidate_ids=d.get("candidates", []))
            for d in data.get("decisions", [])
        ]
        scenarios = [
            PortfolioScenario(scenario_id=s["scenario_id"], portfolio_id=s.get("portfolio_id", ""), assignment=s.get("assignment", {}))
            for s in data.get("scenarios", [])
        ]
        return cls(
            portfolio_id=data["portfolio_id"],
            baseline_id=data.get("baseline_id", ""),
            decisions=decisions,
            scenarios=scenarios,
            state=PortfolioState(data.get("state", "created")),
            max_combinations=data.get("max_combinations", MAX_COMBINATIONS_DEFAULT),
            theoretical_count=data.get("theoretical_count", 0),
            valid_count=data.get("valid_count", 0),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
            tool_version=data.get("tool_version", "0.12.0"),
        )
    # end of NarrativePortfolio
