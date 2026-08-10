"""Divergence detection between committed direction and live state."""

from __future__ import annotations

from pathlib import Path

from auteur.commitment.models import (
    DivergenceFinding,
    DivergenceSeverity,
    DivergenceType,
    PortfolioCommitment,
    _stable_id,
)


class DivergenceDetector:
    """Compare committed direction against live project state."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def check(self, commitment: PortfolioCommitment) -> list[DivergenceFinding]:
        """Scan for divergence between commitment and live state.

        Read-only — does not mutate any state.
        """
        findings: list[DivergenceFinding] = []

        for dec_id, cand_id in commitment.assignments.items():
            # Check if decision still exists
            try:
                from auteur.decision.service import DecisionWorkspaceService
                svc = DecisionWorkspaceService(self.project_root)
                decision = svc.inspect(dec_id)
                if decision is None:
                    findings.append(DivergenceFinding(
                        finding_id=_stable_id("div", commitment.commitment_id, dec_id),
                        commitment_id=commitment.commitment_id,
                        divergence_type=DivergenceType.DECISION_REMOVED,
                        severity=DivergenceSeverity.COMMITMENT_BREAKING,
                        expected=cand_id,
                        actual="",
                        decision_id=dec_id,
                        description=f"Decision {dec_id[:16]}... no longer available",
                        recommended_action="Remove assignment or supersede commitment",
                    ))
                    continue
            except Exception:
                continue

        return findings
