"""Typed models for Decision Lifecycle Integration (v0.14.0)."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


class LifecycleStage(str, enum.Enum):
    """Stages a decision passes through in order."""
    OPEN = "open"
    EVIDENCE_GATHERED = "evidence_gathered"
    SIMULATED = "simulated"
    PORTFOLIO = "portfolio"
    COMPARED = "compared"
    PROMOTED = "promoted"
    UNDER_REVIEW = "under_review"
    ACCEPTANCE_READY = "acceptance_ready"
    ACCEPTED = "accepted"
    COMMITTED = "committed"


@dataclass
class DecisionLifecycleEntry:
    """Lifecycle state for a single decision."""
    decision_id: str
    stage: LifecycleStage = LifecycleStage.OPEN
    description: str = ""
    simulation_count: int = 0
    portfolio_ids: list[str] = field(default_factory=list)
    review_session_id: str = ""
    commitment_id: str = ""
    expected_candidate: str = ""
    current_candidate: str = ""
    diverged: bool = False
    gaps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "stage": self.stage.value,
            "description": self.description,
            "simulation_count": self.simulation_count,
            "portfolio_ids": self.portfolio_ids,
            "review_session_id": self.review_session_id,
            "commitment_id": self.commitment_id,
            "expected_candidate": self.expected_candidate,
            "current_candidate": self.current_candidate,
            "diverged": self.diverged,
            "gaps": self.gaps,
        }


@dataclass
class LifecycleSummary:
    """Aggregate lifecycle counts."""
    total_decisions: int = 0
    by_stage: dict[str, int] = field(default_factory=dict)
    simulated: int = 0
    in_portfolio: int = 0
    under_review: int = 0
    accepted: int = 0
    committed: int = 0
    diverged: int = 0
    with_gaps: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_decisions": self.total_decisions,
            "by_stage": self.by_stage,
            "simulated": self.simulated,
            "in_portfolio": self.in_portfolio,
            "under_review": self.under_review,
            "accepted": self.accepted,
            "committed": self.committed,
            "diverged": self.diverged,
            "with_gaps": self.with_gaps,
        }
