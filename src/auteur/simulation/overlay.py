"""Isolated candidate-specific hypothetical state overlay.

The overlay provides a hypothetical view of project state without
mutating any live store. It supplies projected state to existing
planning and impact engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auteur.simulation.models import (
    CounterfactualBaseline,
    ProjectedArtifactChange,
    ProjectedDecisionChange,
    ProjectedMilestoneChange,
    ProjectedReviewChange,
)


@dataclass
class ScenarioOverlay:
    """Hypothetical state view over an immutable baseline.

    The overlay records every hypothetical change so that existing
    planning and impact engines can operate on projected state.
    """

    baseline: CounterfactualBaseline
    resolved_decision_id: str = ""
    selected_candidate_id: str = ""
    stale_artifact_ids: set[str] = field(default_factory=set)
    unchanged_artifact_ids: set[str] = field(default_factory=set)
    projected_new_decisions: list[dict[str, Any]] = field(default_factory=list)
    projected_milestone_changes: dict[str, str] = field(default_factory=dict)
    projected_session_changes: dict[str, str] = field(default_factory=dict)
    projected_decision_changes: dict[str, str] = field(default_factory=dict)

    def record_stale_artifact(self, artifact_id: str) -> None:
        """Mark an artifact as hypothetically stale."""
        self.stale_artifact_ids.add(artifact_id)
        self.unchanged_artifact_ids.discard(artifact_id)

    def record_unchanged_artifact(self, artifact_id: str) -> None:
        """Mark an artifact as hypothetically unchanged."""
        if artifact_id not in self.stale_artifact_ids:
            self.unchanged_artifact_ids.add(artifact_id)

    def record_new_decision(self, decision_ref: dict[str, Any]) -> None:
        """Record a projected new decision."""
        self.projected_new_decisions.append(decision_ref)

    def record_milestone_change(self, milestone_id: str, projected_state: str) -> None:
        """Record a projected milestone transition."""
        self.projected_milestone_changes[milestone_id] = projected_state

    def record_session_change(self, session_id: str, projected_state: str) -> None:
        """Record a projected review session change."""
        self.projected_session_changes[session_id] = projected_state

    def record_decision_change(self, decision_id: str, projected_state: str) -> None:
        """Record a projected decision state change."""
        self.projected_decision_changes[decision_id] = projected_state

    def get_artifact_changes(self) -> list[ProjectedArtifactChange]:
        """Get all projected artifact changes as typed records."""
        changes: list[ProjectedArtifactChange] = []
        for aid in self.stale_artifact_ids:
            changes.append(ProjectedArtifactChange(
                artifact_id=aid,
                projected_state="stale",
                classification="derived",
                confidence="high",
            ))
        return changes

    def get_decision_changes(self) -> list[ProjectedDecisionChange]:
        """Get all projected decision changes."""
        changes: list[ProjectedDecisionChange] = []
        for did, state in self.projected_decision_changes.items():
            changes.append(ProjectedDecisionChange(
                decision_id=did,
                projected_state=state,
                classification="derived",
                confidence="high",
            ))
        return changes

    def get_review_changes(self) -> list[ProjectedReviewChange]:
        """Get all projected review session changes."""
        changes: list[ProjectedReviewChange] = []
        for sid, state in self.projected_session_changes.items():
            changes.append(ProjectedReviewChange(
                session_id=sid,
                projected_state=state,
                classification="derived",
                confidence="high",
            ))
        return changes

    def get_milestone_changes(self) -> list[ProjectedMilestoneChange]:
        """Get all projected milestone changes."""
        changes: list[ProjectedMilestoneChange] = []
        for mid, state in self.projected_milestone_changes.items():
            changes.append(ProjectedMilestoneChange(
                milestone_id=mid,
                current_state="?",
                projected_state=state,
                reason="Projected from candidate selection",
                classification="derived",
                confidence="high",
            ))
        return changes
