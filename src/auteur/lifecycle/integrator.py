"""Probe each subsystem and compose per-decision lifecycle state.

All probes are read-only — no state is created or mutated.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from auteur.lifecycle.models import (
    DecisionLifecycleEntry,
    LifecycleStage,
    LifecycleSummary,
)

logger = logging.getLogger(__name__)


class LifecycleIntegrator:
    """Compose per-decision lifecycle state from existing subsystems."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    # ── probes ───────────────────────────────────────────────────────

    def _probe_decisions(self) -> dict[str, dict[str, Any]]:
        """Return {decision_id: {description, current_candidate}}."""
        result: dict[str, dict[str, Any]] = {}
        try:
            from auteur.decision.service import DecisionWorkspaceService
            svc = DecisionWorkspaceService(self.project_root)
            decisions = svc.list_decisions() if hasattr(svc, "list_decisions") else []
            if isinstance(decisions, dict):
                for dec_id, dec in decisions.items():
                    result[dec_id] = {
                        "description": getattr(dec, "description", "") if not isinstance(dec, dict) else dec.get("description", ""),
                        "current_candidate": "",
                    }
            else:
                for dec in decisions:
                    dec_id = dec.decision_id if hasattr(dec, "decision_id") else ""
                    if not dec_id:
                        continue
                    info: dict[str, Any] = {
                        "description": getattr(dec, "description", ""),
                        "current_candidate": "",
                    }
                    # Try to extract current candidate from unresolved choices
                    choices = getattr(dec, "unresolved_choices", None) or getattr(dec, "candidates", None) or []
                    if choices and len(choices) > 0:
                        first = choices[0]
                        if hasattr(first, "candidate_id"):
                            info["current_candidate"] = first.candidate_id
                    result[dec_id] = info
        except Exception as e:
            logger.debug(f"Decision probe failed: {e}")
        return result

    def _probe_simulations(self) -> dict[str, int]:
        """Return {decision_id: count}."""
        result: dict[str, int] = {}
        try:
            from auteur.simulation.service import SimulationService
            svc = SimulationService(self.project_root)
            scenarios = svc.list_scenarios() if hasattr(svc, "list_scenarios") else []
            for s in scenarios:
                if isinstance(s, dict):
                    dec_id = s.get("decision_id") or s.get("source_decision_id", "")
                else:
                    dec_id = getattr(s, "decision_id", "") or getattr(s, "source_decision_id", "")
                if dec_id:
                    result[dec_id] = result.get(dec_id, 0) + 1
        except Exception as e:
            logger.debug(f"Simulation probe failed: {e}")
        return result

    def _probe_portfolios(self) -> dict[str, list[str]]:
        """Return {decision_id: [portfolio_id, ...]}."""
        result: dict[str, list[str]] = {}
        try:
            from auteur.portfolio.service import PortfolioService
            svc = PortfolioService(self.project_root)
            portfolios = svc.list_portfolios() if hasattr(svc, "list_portfolios") else []
            for entry in portfolios:
                pid = entry.get("portfolio_id", "") if isinstance(entry, dict) else ""
                if not pid:
                    continue
                portfolio = svc.inspect(pid)
                if portfolio is None:
                    continue
                assignments = portfolio.assignments if hasattr(portfolio, "assignments") else {}
                for dec_id in assignments:
                    result.setdefault(dec_id, []).append(pid)
        except Exception as e:
            logger.debug(f"Portfolio probe failed: {e}")
        return result

    def _probe_commitment(self) -> dict[str, dict[str, str]]:
        """Return {decision_id: {commitment_id, expected_candidate}}."""
        result: dict[str, dict[str, str]] = {}
        try:
            from auteur.commitment.service import CommitmentService
            svc = CommitmentService(self.project_root)
            commitments = svc.list_commitments() if hasattr(svc, "list_commitments") else []
            for entry in commitments:
                cid = entry.get("commitment_id", "") if isinstance(entry, dict) else ""
                if not cid:
                    continue
                c = svc.inspect(cid)
                if c is None:
                    continue
                for dec_id, cand_id in c.assignments.items():
                    if dec_id not in result:
                        result[dec_id] = {"commitment_id": cid, "expected_candidate": cand_id}
        except Exception as e:
            logger.debug(f"Commitment probe failed: {e}")
        return result

    def _probe_reviews(self) -> dict[str, str]:
        """Return {decision_id: session_id}."""
        result: dict[str, str] = {}
        try:
            from auteur.review.service import ReviewService
            svc = ReviewService(self.project_root)
            sessions = svc.list_sessions() if hasattr(svc, "list_sessions") else []
            for s in sessions:
                if isinstance(s, dict):
                    dec_id = s.get("decision_id", "")
                    sid = s.get("session_id", "")
                else:
                    dec_id = getattr(s, "decision_id", "")
                    sid = getattr(s, "session_id", "")
                if dec_id and sid:
                    result[dec_id] = result.get(dec_id, "") or sid
        except Exception as e:
            logger.debug(f"Review probe failed: {e}")
        return result

    # ── lifecycle composition ────────────────────────────────────────

    def get_lifecycle_entries(self) -> list[DecisionLifecycleEntry]:
        """Compose lifecycle state for every known decision."""
        decisions = self._probe_decisions()
        sim_map = self._probe_simulations()
        port_map = self._probe_portfolios()
        commit_map = self._probe_commitment()
        review_map = self._probe_reviews()

        entries: list[DecisionLifecycleEntry] = []

        for dec_id, info in decisions.items():
            desc = info.get("description", "") if isinstance(info, dict) else ""
            entry = DecisionLifecycleEntry(
                decision_id=dec_id,
                description=desc,
                simulation_count=sim_map.get(dec_id, 0),
                portfolio_ids=port_map.get(dec_id, []),
                review_session_id=review_map.get(dec_id, ""),
            )

            # Derive stage
            cm = commit_map.get(dec_id, {})
            if cm:
                entry.commitment_id = cm.get("commitment_id", "")
                entry.expected_candidate = cm.get("expected_candidate", "")
                entry.stage = LifecycleStage.COMMITTED
                cand_info = decisions.get(dec_id, {})
                if isinstance(cand_info, dict):
                    entry.current_candidate = cand_info.get("current_candidate", "")
                    if (entry.expected_candidate
                            and entry.current_candidate
                            and entry.expected_candidate != entry.current_candidate):
                        entry.diverged = True
            elif entry.review_session_id:
                entry.stage = self._resolve_review_stage(dec_id)
            elif entry.portfolio_ids:
                entry.stage = LifecycleStage.PORTFOLIO
            elif entry.simulation_count > 0:
                entry.stage = LifecycleStage.SIMULATED
            else:
                entry.stage = LifecycleStage.OPEN

            entry.gaps = self._detect_gaps(entry)
            entries.append(entry)

        entries.sort(key=lambda e: e.decision_id)
        return entries

    def _resolve_review_stage(self, dec_id: str) -> LifecycleStage:
        """Check if a decision under review is acceptance-ready or accepted."""
        try:
            from auteur.review.service import ReviewService
            svc = ReviewService(self.project_root)
            sessions = svc.list_sessions() if hasattr(svc, "list_sessions") else []
            for s in sessions:
                if isinstance(s, dict):
                    sid = s.get("session_id", "")
                    sdec = s.get("decision_id", "")
                    state = s.get("state", "")
                else:
                    sid = getattr(s, "session_id", "")
                    sdec = getattr(s, "decision_id", "")
                    state = getattr(s, "state", "")
                if sdec == dec_id and sid:
                    if isinstance(state, str) and "accepted" in state.lower():
                        return LifecycleStage.ACCEPTED
                    if isinstance(state, str) and "acceptance_ready" in state.lower():
                        return LifecycleStage.ACCEPTANCE_READY
            return LifecycleStage.UNDER_REVIEW
        except Exception:
            return LifecycleStage.UNDER_REVIEW

    def _detect_gaps(self, entry: DecisionLifecycleEntry) -> list[str]:
        """Detect gaps between current stage and potential next stages."""
        gaps: list[str] = []
        stage = entry.stage

        if stage == LifecycleStage.OPEN:
            gaps.append("no simulation scenarios created")
            gaps.append("not assigned to a portfolio")
        elif stage == LifecycleStage.SIMULATED:
            gaps.append("not assigned to a portfolio")
        elif stage == LifecycleStage.PORTFOLIO:
            gaps.append("portfolio scenario not promoted to review")
        elif stage == LifecycleStage.UNDER_REVIEW:
            gaps.append("not ready for acceptance")
        elif stage == LifecycleStage.ACCEPTANCE_READY:
            gaps.append("not yet accepted")
        elif stage == LifecycleStage.ACCEPTED:
            gaps.append("not committed")

        return gaps

    def get_summary(self) -> LifecycleSummary:
        """Calculate aggregate lifecycle counts."""
        entries = self.get_lifecycle_entries()
        summary = LifecycleSummary(total_decisions=len(entries))

        for e in entries:
            stage_key = e.stage.value
            summary.by_stage[stage_key] = summary.by_stage.get(stage_key, 0) + 1

            if e.simulation_count > 0:
                summary.simulated += 1
            if e.portfolio_ids:
                summary.in_portfolio += 1
            if e.review_session_id:
                summary.under_review += 1
            if e.stage == LifecycleStage.ACCEPTED:
                summary.accepted += 1
            if e.commitment_id:
                summary.committed += 1
            if e.diverged:
                summary.diverged += 1
            if e.gaps:
                summary.with_gaps += 1

        return summary
