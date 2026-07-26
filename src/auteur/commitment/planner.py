"""Convert a selected portfolio commitment into an execution plan."""

from __future__ import annotations

from auteur.commitment.models import (
    ExecutionPlan,
    ExecutionStep,
    ExecutionStepState,
    ExecutionStepType,
    PortfolioCommitment,
    _stable_id,
)


class CommitmentPlanner:
    """Generate coordinated execution plans from commitments."""

    def plan(self, commitment: PortfolioCommitment) -> ExecutionPlan:
        """Generate an execution plan for a commitment.

        Creates steps for each committed assignment in deterministic order.
        """
        plan_id = _stable_id("plan", commitment.commitment_id)
        steps: list[ExecutionStep] = []

        decision_ids = sorted(commitment.assignments.keys())
        for i, dec_id in enumerate(decision_ids):
            cand_id = commitment.assignments[dec_id]

            # Start review step
            start_step = ExecutionStep(
                step_id=_stable_id("step", plan_id, dec_id, "review"),
                commitment_id=commitment.commitment_id,
                decision_id=dec_id,
                candidate_id=cand_id,
                step_type=ExecutionStepType.START_REVIEW,
                state=ExecutionStepState.READY if i == 0 else ExecutionStepState.PENDING,
                prerequisites=[] if i == 0 else [f"step-{decision_ids[i-1]}"],
                safe_to_execute=True,
            )
            steps.append(start_step)

            # Prepare acceptance step (authority required)
            prepare_step = ExecutionStep(
                step_id=_stable_id("step", plan_id, dec_id, "prepare"),
                commitment_id=commitment.commitment_id,
                decision_id=dec_id,
                candidate_id=cand_id,
                step_type=ExecutionStepType.PREPARE_ACCEPTANCE,
                state=ExecutionStepState.PENDING,
                prerequisites=[start_step.step_id],
                safe_to_execute=False,
            )
            steps.append(prepare_step)

            # Refresh impact after acceptance
            refresh_step = ExecutionStep(
                step_id=_stable_id("step", plan_id, dec_id, "refresh"),
                commitment_id=commitment.commitment_id,
                decision_id=dec_id,
                candidate_id=cand_id,
                step_type=ExecutionStepType.REFRESH_IMPACT,
                state=ExecutionStepState.PENDING,
                prerequisites=[prepare_step.step_id],
                safe_to_execute=True,
            )
            steps.append(refresh_step)

        return ExecutionPlan(plan_id=plan_id, commitment_id=commitment.commitment_id, steps=steps)
