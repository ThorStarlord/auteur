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
    decision_to_review: dict[str, str] = field(default_factory=dict)
    failed_decisions: list[str] = field(default_factory=list)
    state: str = ""


class PortfolioPromoter:
    """Promote a portfolio scenario into coordinated author reviews."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def promote(
        self, scenario: PortfolioScenario, confirm: bool = False,
    ) -> PromotionResult:
        """Promote portfolio scenario into review sessions.

        State transitions:
          confirm=False → confirmation_required
          FAILED scenario + confirm → stale_refused
          incompatible active review → review_conflict
          partial success → partially_promoted
          full success → promoted
          complete failure → error / no_sessions_created
        """
        if not confirm:
            return PromotionResult(success=False, state="confirmation_required")

        if scenario.state in (PortfolioScenarioState.FAILED,):
            return PromotionResult(success=False, state="stale_refused")

        try:
            from auteur.review.service import ReviewService
            svc = ReviewService(self.project_root)

            decision_to_review: dict[str, str] = {}
            new_ids: list[str] = []
            reused_ids: list[str] = []
            conflicting_ids: list[str] = []
            failed_list: list[str] = []

            for dec_id, cand_id in scenario.assignment.items():
                # Check for existing reviews
                existing = self._session_for_decision(svc, dec_id)
                if existing:
                    # Incompatible candidate check
                    existing_cand = self._session_candidate(svc, existing)
                    if existing_cand and existing_cand != cand_id:
                        conflicting_ids.append(existing)
                        decision_to_review[dec_id] = existing
                        continue

                    # Compatible — reuse
                    reused_ids.append(existing)
                    decision_to_review[dec_id] = existing
                    continue

                # Create new session
                try:
                    session = svc.start_session(decision_id=dec_id, candidate_id=cand_id)
                    sid = session.session_id if hasattr(session, "session_id") else str(session)
                    new_ids.append(sid)
                    decision_to_review[dec_id] = sid
                except Exception as e:
                    logger.warning(f"Could not create review for {dec_id}: {e}")
                    failed_list.append(dec_id)

            all_ids = list(decision_to_review.values())

            # Determine result state
            if conflicting_ids:
                return PromotionResult(
                    success=False, state="review_conflict",
                    review_session_ids=list(set(all_ids)),
                    new_session_ids=new_ids,
                    reused_session_ids=reused_ids,
                    conflicting_session_ids=conflicting_ids,
                    decision_to_review=decision_to_review,
                    failed_decisions=failed_list,
                )

            if new_ids and failed_list:
                return PromotionResult(
                    success=True, state="partially_promoted",
                    review_session_ids=list(set(all_ids)),
                    new_session_ids=new_ids,
                    reused_session_ids=reused_ids,
                    decision_to_review=decision_to_review,
                    failed_decisions=failed_list,
                )

            if all_ids:
                return PromotionResult(
                    success=True, state="promoted",
                    review_session_ids=list(set(all_ids)),
                    new_session_ids=new_ids,
                    reused_session_ids=reused_ids,
                    decision_to_review=decision_to_review,
                )

            return PromotionResult(
                success=False, state="no_sessions_created",
                review_session_ids=[],
                decision_to_review=decision_to_review,
                failed_decisions=failed_list,
            )

        except Exception:
            logger.exception("Promotion failed")
            return PromotionResult(success=False, state="error")

    def _session_for_decision(self, svc, decision_id: str) -> str | None:
        """Return active session ID for a decision, or None."""
        try:
            sessions = svc.list_sessions()
            for s in sessions:
                sid = getattr(s, "session_id", None)
                if isinstance(s, dict):
                    sid = s.get("session_id", sid)
                state = getattr(s, "state", None)
                if isinstance(s, dict):
                    state = s.get("state", state)
                target = getattr(s, "target", {})
                if isinstance(s, dict):
                    target = s.get("target", target)
                if isinstance(target, dict):
                    dec_id = target.get("decision_id", "")
                else:
                    dec_id = getattr(target, "decision_id", "")
                if dec_id == decision_id and state in ("open", "inspecting", "awaiting_choice"):
                    return sid
        except Exception:
            pass
        return None

    def _session_candidate(self, svc, session_id: str) -> str | None:
        """Return the target candidate for a session, or None."""
        try:
            sessions = svc.list_sessions()
            for s in sessions:
                sid = getattr(s, "session_id", None)
                if isinstance(s, dict):
                    sid = s.get("session_id", sid)
                if sid == session_id:
                    target = getattr(s, "target", {})
                    if isinstance(s, dict):
                        target = s.get("target", target)
                    if isinstance(target, dict):
                        return target.get("candidate_id", "")
                    return getattr(target, "candidate_id", None)
        except Exception:
            pass
        return None
