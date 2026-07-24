"""Coordinated promotion of portfolio scenarios into Author Review Sessions."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from auteur.portfolio.models import PortfolioScenario

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
        """Promote portfolio scenario into review sessions."""
        if not confirm:
            return PromotionResult(success=False, state="confirmation_required")

        review_ids: list[str] = []
        new_ids: list[str] = []
        reused_ids: list[str] = []

        try:
            from auteur.review.service import ReviewService
            svc = ReviewService(self.project_root)

            for dec_id, cand_id in scenario.assignment.items():
                try:
                    session = svc.start_session(decision_id=dec_id, candidate_id=cand_id)
                    sid = session.session_id if hasattr(session, "session_id") else str(session)
                    review_ids.append(sid)
                    new_ids.append(sid)
                except Exception as e:
                    logger.warning(f"Could not create review for {dec_id}: {e}")
                    continue

            if review_ids:
                return PromotionResult(
                    success=True,
                    review_session_ids=review_ids,
                    new_session_ids=new_ids,
                    reused_session_ids=reused_ids,
                    state="promoted",
                )
            return PromotionResult(success=False, state="no_sessions_created", review_session_ids=review_ids)

        except Exception as e:
            logger.exception(f"Promotion failed")
            return PromotionResult(success=False, state="error", review_session_ids=review_ids)
