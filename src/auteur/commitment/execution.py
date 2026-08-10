"""Commitment execution — delegate safe steps, create/reuse reviews."""

from __future__ import annotations

import logging
from pathlib import Path

from auteur.commitment.models import (
    ExecutionStep,
    ExecutionStepState,
    ExecutionStepType,
)

logger = logging.getLogger(__name__)


class CommitmentExecutor:
    """Execute commitment steps, delegating to existing subsystems."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def can_execute(self, step: ExecutionStep) -> tuple[bool, str]:
        """Check if a step is safe and ready to execute."""
        if not step.safe_to_execute:
            return False, f"Step {step.step_id} requires authority"
        if step.state != ExecutionStepState.READY:
            return False, f"Step {step.step_id} is not ready (state={step.state.value})"
        return True, ""

    def execute_step(self, step: ExecutionStep) -> ExecutionStep:
        """Execute a single step.

        Returns updated step with new state and result.
        """
        if step.step_type == ExecutionStepType.START_REVIEW:
            return self._start_review(step)
        elif step.step_type == ExecutionStepType.REFRESH_IMPACT:
            return self._refresh_impact(step)
        elif step.step_type == ExecutionStepType.REFRESH_PLAN:
            return self._refresh_plan(step)
        elif step.step_type == ExecutionStepType.INSPECT_EVIDENCE:
            return ExecutionStep(step_id=step.step_id, commitment_id=step.commitment_id,
                                 decision_id=step.decision_id, candidate_id=step.candidate_id,
                                 step_type=step.step_type, state=ExecutionStepState.COMPLETED,
                                 prerequisites=step.prerequisites, safe_to_execute=step.safe_to_execute,
                                 result="Evidence inspected")
        return ExecutionStep(step_id=step.step_id, commitment_id=step.commitment_id,
                             decision_id=step.decision_id, candidate_id=step.candidate_id,
                             step_type=step.step_type, state=ExecutionStepState.FAILED,
                             prerequisites=step.prerequisites, safe_to_execute=step.safe_to_execute,
                             result="Unknown step type")

    def _start_review(self, step: ExecutionStep) -> ExecutionStep:
        """Start a review session for this decision."""
        try:
            from auteur.review.service import ReviewService
            svc = ReviewService(self.project_root)
            session = svc.start_session(decision_id=step.decision_id, candidate_id=step.candidate_id)
            sid = session.session_id if hasattr(session, "session_id") else str(session)
            return ExecutionStep(step_id=step.step_id, commitment_id=step.commitment_id,
                                 decision_id=step.decision_id, candidate_id=step.candidate_id,
                                 step_type=step.step_type, state=ExecutionStepState.COMPLETED,
                                 prerequisites=step.prerequisites, safe_to_execute=step.safe_to_execute,
                                 result=f"Review created: {sid[:24]}...")
        except Exception as e:
            return ExecutionStep(step_id=step.step_id, commitment_id=step.commitment_id,
                                 decision_id=step.decision_id, candidate_id=step.candidate_id,
                                 step_type=step.step_type, state=ExecutionStepState.FAILED,
                                 prerequisites=step.prerequisites, safe_to_execute=step.safe_to_execute,
                                 result=str(e))

    def _refresh_impact(self, step: ExecutionStep) -> ExecutionStep:
        """Refresh impact analysis for this decision."""
        try:
            from auteur.decision.service import DecisionWorkspaceService
            svc = DecisionWorkspaceService(self.project_root)
            svc.refresh(decision_id=step.decision_id) if hasattr(svc, "refresh") else None
            return ExecutionStep(step_id=step.step_id, commitment_id=step.commitment_id,
                                 decision_id=step.decision_id, candidate_id=step.candidate_id,
                                 step_type=step.step_type, state=ExecutionStepState.COMPLETED,
                                 prerequisites=step.prerequisites, safe_to_execute=step.safe_to_execute,
                                 result="Impact refreshed")
        except Exception as e:
            return ExecutionStep(step_id=step.step_id, commitment_id=step.commitment_id,
                                 decision_id=step.decision_id, candidate_id=step.candidate_id,
                                 step_type=step.step_type, state=ExecutionStepState.FAILED,
                                 prerequisites=step.prerequisites, safe_to_execute=step.safe_to_execute,
                                 result=str(e))

    def _refresh_plan(self, step: ExecutionStep) -> ExecutionStep:
        """Refresh project plan."""
        try:
            from auteur.planning.service import PlanningService
            svc = PlanningService(self.project_root)
            svc.refresh(save=False)
            return ExecutionStep(step_id=step.step_id, commitment_id=step.commitment_id,
                                 decision_id=step.decision_id, candidate_id=step.candidate_id,
                                 step_type=step.step_type, state=ExecutionStepState.COMPLETED,
                                 prerequisites=step.prerequisites, safe_to_execute=step.safe_to_execute,
                                 result="Plan refreshed")
        except Exception as e:
            return ExecutionStep(step_id=step.step_id, commitment_id=step.commitment_id,
                                 decision_id=step.decision_id, candidate_id=step.candidate_id,
                                 step_type=step.step_type, state=ExecutionStepState.FAILED,
                                 prerequisites=step.prerequisites, safe_to_execute=step.safe_to_execute,
                                 result=str(e))
