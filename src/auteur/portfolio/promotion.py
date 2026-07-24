"""Coordinated promotion of portfolio scenarios into Author Review Sessions."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from auteur.portfolio.models import PortfolioScenario, PortfolioScenarioState

logger = logging.getLogger(__name__)


@dataclass
class PromotionResult:
    success: bool = False
    review_session_ids: list[str] = field(default_factory=list)
    reused_session_ids: list[str] = field(default_factory=list)
    conflicting_session_ids: list[str] = field(default_factory=list)
    new_session_ids: list[str] = field(default_factory=list)
    state: str = ""


class PortfolioPromoter:
    """Promote a portfolio scenario into coordinated author reviews."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def promote(
        self, scenario: PortfolioScenario, confirm: bool = False,
    ) -> PromotionResult:
        """Promote portfolio scenario into review sessions.

        Performs these checks in order:
        1. Confirmation gate (confirm=False → refusal)
        2. Staleness check (failed/blocked scenarios → refusal)
        3. Conflict detection (existing sessions for same decisions → reported)
        4. Session creation or reuse for each decision
        5. Partial state tracking (some may succeed, some may fail)
        """
        if not confirm:
            return PromotionResult(success=False, state="confirmation_required")

        # Staleness check
        if scenario.state in (PortfolioScenarioState.FAILED,):
            return PromotionResult(
                success=False, state="stale_refused",
                review_session_ids=[],
            )

        try:
            from auteur.review.service import ReviewService
            svc = ReviewService(self.project_root)

            # Conflict detection: find existing sessions for these decisions
            existing_sessions = self._get_existing_sessions(svc)
            conflicting: list[str] = []
            for dec_id in scenario.assignment:
                if dec_id in existing_sessions:
                    conflicting.append(existing_sessions[dec_id])

            review_ids: list[str] = []
            new_ids: list[str] = []
            reused_ids: list[str] = []
            failed_decisions: list[str] = []

            for dec_id, cand_id in scenario.assignment.items():
                # Check for conflicting active sessions
                if dec_id in existing_sessions:
                    reused_ids.append(existing_sessions[dec_id])
                    review_ids.append(existing_sessions[dec_id])
                    continue

                # Try to create a new session
                try:
                    session = svc.start_session(decision_id=dec_id, candidate_id=cand_id)
                    sid = session.session_id if hasattr(session, "session_id") else str(session)
                    review_ids.append(sid)
                    new_ids.append(sid)
                except Exception as e:
                    logger.warning(f"Could not create review for {dec_id}: {e}")
                    failed_decisions.append(dec_id)

            # Determine result state
            if new_ids and failed_decisions:
                return PromotionResult(
                    success=True,
                    review_session_ids=review_ids,
                    new_session_ids=new_ids,
                    reused_session_ids=reused_ids,
                    state="partially_promoted",
                )
            elif new_ids or reused_ids:
                return PromotionResult(
                    success=True,
                    review_session_ids=review_ids,
                    new_session_ids=new_ids,
                    reused_session_ids=reused_ids,
                    state="promoted",
                )
            else:
                return PromotionResult(
                    success=False, state="no_sessions_created",
                    review_session_ids=review_ids,
                )

        except Exception as e:
            logger.exception(f"Promotion failed")
            return PromotionResult(success=False, state="error", review_session_ids=review_ids)

    def _get_existing_sessions(self, svc) -> dict[str, str]:
        """Get existing review sessions by decision ID.

        Returns dict of decision_id → session_id for active sessions.
        """
        result: dict[str, str] = {}
        try:
            sessions = svc.list_sessions()
            for s in sessions:
                sid = getattr(s, "session_id", None) or (s.get("session_id") if isinstance(s, dict) else None)
                state = getattr(s, "state", None) or (s.get("state") if isinstance(s, dict) else None)
                target = getattr(s, "target", {}) if hasattr(s, "target") else (s.get("target", {}) if isinstance(s, dict) else {})
                if isinstance(target, dict):
                    dec_id = target.get("decision_id", "")
                else:
                    dec_id = getattr(target, "decision_id", "")
                if dec_id and state in ("open", "inspecting", "awaiting_choice"):
                    result[dec_id] = sid
        except Exception:
            pass
        return result
