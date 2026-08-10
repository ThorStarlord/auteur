"""Notification scanner — probes all subsystems for author-actionable findings."""

from __future__ import annotations

import logging
from pathlib import Path

from auteur.notify.models import (
    NotificationFinding,
    NotificationSeverity,
    NotificationType,
    _stable_id,
)

logger = logging.getLogger(__name__)


class NotificationScanner:
    """Scan all subsystems for events needing author attention."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self) -> list[NotificationFinding]:
        """Scan all subsystems and return findings."""
        findings: list[NotificationFinding] = []
        findings.extend(self._scan_divergence())
        findings.extend(self._scan_review_readiness())
        findings.extend(self._scan_lifecycle_gaps())
        findings.extend(self._scan_execution_failures())
        return findings

    def _scan_divergence(self) -> list[NotificationFinding]:
        """Check for divergence between committed and live state."""
        findings: list[NotificationFinding] = []
        try:
            from auteur.commitment.service import CommitmentService
            svc = CommitmentService(self.project_root)
            status = svc.status()
            latest_id = status.get("latest_commitment_id", "")
            if not latest_id:
                return findings
            issues = svc.check(latest_id)
            for issue in issues:
                if hasattr(issue, "to_dict"):
                    d = issue.to_dict()
                elif isinstance(issue, dict):
                    d = issue
                else:
                    continue
                findings.append(NotificationFinding(
                    finding_id=_stable_id("div", latest_id, d.get("finding_id", "unknown")),
                    notification_type=NotificationType.DIVERGENCE,
                    severity=NotificationSeverity.WARNING,
                    title="Commitment divergence detected",
                    description=d.get("description", "Committed direction diverged from live state."),
                    subsystem="commitment",
                    command=f"auteur commit check {latest_id} --project .",
                    details=d,
                ))
        except Exception as e:
            logger.debug(f"Divergence scan failed: {e}")
        return findings

    def _scan_review_readiness(self) -> list[NotificationFinding]:
        """Check for review sessions ready for acceptance."""
        findings: list[NotificationFinding] = []
        try:
            from auteur.review.service import ReviewService
            svc = ReviewService(self.project_root)
            sessions = svc.list_sessions() if hasattr(svc, "list_sessions") else []
            for s in sessions:
                if isinstance(s, dict):
                    sid = s.get("session_id", "")
                    state = s.get("state", "")
                    dec_id = s.get("decision_id", "")
                else:
                    sid = getattr(s, "session_id", "")
                    state = getattr(s, "state", "")
                    dec_id = getattr(s, "decision_id", "")
                if not sid:
                    continue
                if isinstance(state, str) and "acceptance_ready" in state.lower():
                    findings.append(NotificationFinding(
                        finding_id=_stable_id("review", sid),
                        notification_type=NotificationType.ACCEPTANCE_READY,
                        severity=NotificationSeverity.INFO,
                        title="Review session ready for acceptance",
                        description=f"Session {sid[:16]}... is ready for acceptance.",
                        subsystem="review",
                        command=f"auteur decision prepare-acceptance {dec_id or sid} --project .",
                        details={"session_id": sid, "decision_id": dec_id},
                    ))
        except Exception as e:
            logger.debug(f"Review scan failed: {e}")
        return findings

    def _scan_lifecycle_gaps(self) -> list[NotificationFinding]:
        """Check for decisions with lifecycle gaps."""
        findings: list[NotificationFinding] = []
        try:
            from auteur.lifecycle.service import LifecycleService
            svc = LifecycleService(self.project_root)
            summary = svc.summary()
            if hasattr(summary, "to_dict"):
                d = summary.to_dict()
            else:
                d = {}
            gaps = d.get("with_gaps", 0)
            if gaps > 0:
                findings.append(NotificationFinding(
                    finding_id=_stable_id("gap", str(gaps)),
                    notification_type=NotificationType.LIFECYCLE_GAP,
                    severity=NotificationSeverity.INFO,
                    title=f"{gaps} decision(s) have lifecycle gaps",
                    description=f"{gaps} decision(s) are missing expected lifecycle steps.",
                    subsystem="lifecycle",
                    command="auteur lifecycle summary --project .",
                    details=d,
                ))
        except Exception as e:
            logger.debug(f"Lifecycle scan failed: {e}")
        return findings

    def _scan_execution_failures(self) -> list[NotificationFinding]:
        """Check for failed commitment execution steps."""
        findings: list[NotificationFinding] = []
        try:
            from auteur.commitment.service import CommitmentService
            svc = CommitmentService(self.project_root)
            status = svc.status()
            latest_id = status.get("latest_commitment_id", "")
            if not latest_id:
                return findings
            try:
                plan = svc.plan(latest_id)
            except Exception:
                return findings  # no plan yet
            steps = getattr(plan, "steps", [])
            failed = [s for s in steps if getattr(s, "state", "") and getattr(s, "state", "").value == "failed"]
            if failed:
                findings.append(NotificationFinding(
                    finding_id=_stable_id("fail", latest_id, str(len(failed))),
                    notification_type=NotificationType.EXECUTION_FAILURE,
                    severity=NotificationSeverity.WARNING,
                    title=f"{len(failed)} execution step(s) failed",
                    description=f"{len(failed)} of {len(steps)} execution steps have failed.",
                    subsystem="commitment",
                    command=f"auteur commit execute {latest_id} --project .",
                    details={"failed": len(failed), "total": len(steps),
                             "failed_steps": [getattr(s, "step_id", "") for s in failed[:5]]},
                ))
        except Exception as e:
            logger.debug(f"Execution scan failed: {e}")
        return findings
