"""Decision and candidate-set validation for portfolio creation."""

from __future__ import annotations

from pathlib import Path


class PortfolioSelection:
    """Validate decisions and candidates for portfolio inclusion."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def validate_decision(self, decision_id: str) -> tuple[bool, str]:
        """Validate that a decision exists and can be included."""
        try:
            from auteur.decision.service import DecisionWorkspaceService
            svc = DecisionWorkspaceService(self.project_root)
            dec = svc.inspect(decision_id)
            if dec is None:
                return False, f"Decision not found: {decision_id}"
            return True, ""
        except Exception as e:
            return False, str(e)

    def validate_candidate(self, decision_id: str, candidate_id: str) -> tuple[bool, str]:
        """Validate that a candidate belongs to a decision."""
        try:
            from auteur.decision.service import DecisionWorkspaceService
            svc = DecisionWorkspaceService(self.project_root)
            dec = svc.inspect(decision_id)
            if dec is None:
                return False, f"Decision not found: {decision_id}"
            candidates = getattr(dec, "candidates", [])
            for c in candidates:
                cid = c.candidate_id if hasattr(c, "candidate_id") else str(c)
                if cid == candidate_id:
                    return True, ""
            return False, f"Candidate {candidate_id} not found in decision {decision_id}"
        except Exception as e:
            return False, str(e)
