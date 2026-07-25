"""Per-assignment and aggregate commitment progress."""

from __future__ import annotations

from auteur.commitment.models import (
    AssignmentState,
    CommitmentProgress,
    PortfolioCommitment,
)


class CommitmentProgressTracker:
    """Derive per-assignment and aggregate commitment progress."""

    def progress(self, commitment: PortfolioCommitment) -> CommitmentProgress:
        """Calculate aggregate progress."""
        total = len(commitment.assignments)
        accepted = 0
        differently = 0
        in_review = 0
        awaiting = 0
        blocked = 0
        stale = 0
        pending = 0

        # Derive from commitment state
        if commitment.state.value in ("completed",):
            accepted = total
        elif commitment.state.value in ("awaiting_author",):
            awaiting = 1
            in_review = total - 1 if total > 1 else 0
        elif commitment.state.value in ("diverged",):
            blocked = 1
            pending = total - 1 if total > 1 else 0

        return CommitmentProgress(
            commitment_id=commitment.commitment_id,
            total=total,
            accepted_as_committed=accepted,
            accepted_differently=differently,
            under_review=in_review,
            awaiting_author=awaiting,
            blocked=blocked,
            stale=stale,
            pending=pending,
            state=commitment.state.value,
        )
