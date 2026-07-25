"""Commitment service — application-service boundary."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from auteur.commitment.models import (
    ExecutionPlan,
    ExecutionStep,
    ExecutionStepState,
    PortfolioCommitment,
    CommitmentState,
    _stable_id,
)
from auteur.commitment.planner import CommitmentPlanner
from auteur.commitment.execution import CommitmentExecutor
from auteur.commitment.progress import CommitmentProgressTracker
from auteur.commitment.divergence import DivergenceDetector
from auteur.commitment.persistence import CommitmentStore

logger = logging.getLogger(__name__)


class CommitmentService:
    """Application-service boundary for portfolio commitments."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self._validate_project()
        self.planner = CommitmentPlanner()
        self.executor = CommitmentExecutor(self.project_root)
        self.progress = CommitmentProgressTracker()
        self.divergence = DivergenceDetector(self.project_root)
        self.store = CommitmentStore(self.project_root)

    def _validate_project(self) -> None:
        marker = self.project_root / ".auteur"
        if not marker.exists():
            raise ValueError(f"Not an Auteur project: {self.project_root}")

    def create_commitment(
        self,
        assignments: dict[str, str],
        portfolio_scenario_id: str = "",
        confirm: bool = False,
    ) -> PortfolioCommitment:
        """Create a portfolio commitment. Requires confirm=True."""
        if not confirm:
            raise ValueError("Confirmation required. Pass confirm=True.")

        cid = _stable_id("commit", str(sorted(assignments.items())))
        commitment = PortfolioCommitment(
            commitment_id=cid,
            portfolio_scenario_id=portfolio_scenario_id,
            assignments=assignments,
            state=CommitmentState.CREATED,
        )
        self.store.save_commitment(commitment)
        self.store.save_latest(cid)
        return commitment

    def plan(self, commitment_id: str) -> ExecutionPlan:
        """Generate execution plan for a commitment."""
        commitment = self.store.load_commitment(commitment_id)
        if commitment is None:
            raise ValueError(f"Commitment not found: {commitment_id}")
        plan = self.planner.plan(commitment)
        self.store.save_plan(plan)
        return plan

    def execute(self, commitment_id: str, step_id: str | None = None) -> ExecutionPlan:
        """Execute safe steps for a commitment.

        If step_id is given, executes only that step.
        Otherwise, executes all ready safe steps.
        """
        commitment = self.store.load_commitment(commitment_id)
        if commitment is None:
            raise ValueError(f"Commitment not found: {commitment_id}")

        plan = self.planner.plan(commitment)
        updated_steps = list(plan.steps)

        for i, step in enumerate(plan.steps):
            if step_id and step.step_id != step_id:
                continue
            if not step.safe_to_execute:
                continue
            if step.state != ExecutionStepState.READY and step.state != ExecutionStepState.PENDING:
                continue

            can, _ = self.executor.can_execute(step)
            if can:
                result = self.executor.execute_step(step)
                updated_steps[i] = result

        updated_plan = ExecutionPlan(
            plan_id=plan.plan_id,
            commitment_id=plan.commitment_id,
            steps=updated_steps,
        )
        self.store.save_plan(updated_plan)
        return updated_plan

    def check(self, commitment_id: str) -> list:
        """Scan for divergence."""
        commitment = self.store.load_commitment(commitment_id)
        if commitment is None:
            raise ValueError(f"Commitment not found: {commitment_id}")
        return self.divergence.check(commitment)

    def status(self) -> dict[str, Any]:
        latest_id = self.store.load_latest_id()
        commitments = self.store.list_commitments()
        return {"has_latest": latest_id is not None,
                "latest_commitment_id": latest_id or "",
                "total_commitments": len(commitments)}

    def inspect(self, commitment_id: str) -> PortfolioCommitment | None:
        return self.store.load_commitment(commitment_id)

    def list_commitments(self) -> list[dict[str, Any]]:
        return self.store.list_commitments()

    def history(self) -> list[dict[str, Any]]:
        return self.store.list_history()

    def batch_accept(
        self,
        commitment_id: str,
        assignment_filter: str | None = None,
        confirm: bool = False,
    ) -> list[dict[str, Any]]:
        """Accept one or all committed assignments through review service.

        Args:
            commitment_id: The commitment to accept assignments from.
            assignment_filter: If set, only accept this specific decision_id.
            confirm: Must be True to proceed.

        Returns:
            List of per-assignment results with status, decision_id, candidate_id, message.
        """
        if not confirm:
            raise ValueError("Confirmation required. Pass confirm=True.")

        commitment = self.store.load_commitment(commitment_id)
        if commitment is None:
            raise ValueError(f"Commitment not found: {commitment_id}")

        from auteur.review.service import ReviewService
        rv = ReviewService(self.project_root)

        results: list[dict[str, Any]] = []

        for dec_id, cand_id in commitment.assignments.items():
            if assignment_filter and dec_id != assignment_filter:
                continue

            # Find review session for this decision
            sessions = rv.list_sessions() if hasattr(rv, "list_sessions") else []
            session_id = ""
            for s in sessions:
                s_dec = s.get("decision_id", "") if isinstance(s, dict) else getattr(s, "decision_id", "")
                if s_dec == dec_id:
                    session_id = s.get("session_id", "") if isinstance(s, dict) else getattr(s, "session_id", "")
                    break

            if not session_id:
                results.append({
                    "decision_id": dec_id,
                    "candidate_id": cand_id,
                    "status": "skipped",
                    "message": f"No review session found for decision {dec_id[:16]}...",
                })
                continue

            try:
                # Prepare acceptance
                rv.prepare_acceptance(session_id, cand_id)
                # Accept as committed
                result = rv.accept(session_id, cand_id, as_committed=True)
                results.append({
                    "decision_id": dec_id,
                    "candidate_id": cand_id,
                    "status": "accepted",
                    "message": f"Accepted as committed",
                    "session_id": session_id,
                })
            except Exception as e:
                results.append({
                    "decision_id": dec_id,
                    "candidate_id": cand_id,
                    "status": "failed",
                    "message": str(e),
                })

        return results
