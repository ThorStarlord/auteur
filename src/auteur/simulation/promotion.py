"""Safe promotion of counterfactual scenarios into Author Review Sessions.

Promotion creates a normal v0.9 review session with scenario evidence attached.
It never accepts a candidate, records an author choice, or mutates pointers.
"""

from __future__ import annotations

import logging
from pathlib import Path

from auteur.simulation.models import (
    CounterfactualScenario,
    ScenarioPromotionResult,
)

logger = logging.getLogger(__name__)


class ScenarioPromoter:
    """Promote a counterfactual scenario into a real author review session.

    Delegates to the existing ReviewService for session creation.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def promote(
        self,
        scenario: CounterfactualScenario,
        confirm: bool = False,
    ) -> ScenarioPromotionResult:
        """Promote a scenario into an author review session.

        Args:
            scenario: The scenario to promote.
            confirm: Must be True to proceed (safety gate).

        Returns:
            ScenarioPromotionResult with status and review session ID.
        """
        if not confirm:
            return ScenarioPromotionResult(
                success=False,
                scenario_id=scenario.scenario_id,
                error="Confirmation required. Use --confirm to proceed.",
            )

        if scenario.state.value in ("stale", "failed", "discarded"):
            return ScenarioPromotionResult(
                success=False,
                scenario_id=scenario.scenario_id,
                error=f"Cannot promote scenario in state: {scenario.state.value}",
            )

        try:
            from auteur.review.service import ReviewService

            svc = ReviewService(self.project_root)
            session = svc.start_session(
                decision_id=scenario.decision_id,
                candidate_id=scenario.candidate_id,
            )

            session_id = session.session_id if hasattr(session, "session_id") else str(session)

            return ScenarioPromotionResult(
                success=True,
                review_session_id=session_id,
                scenario_id=scenario.scenario_id,
            )
        except Exception as e:
            logger.exception(f"Promotion failed for {scenario.scenario_id}")
            return ScenarioPromotionResult(
                success=False,
                scenario_id=scenario.scenario_id,
                error=str(e),
            )
