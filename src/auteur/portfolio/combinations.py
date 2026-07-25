"""Bounded deterministic portfolio combination generation."""

from __future__ import annotations

import itertools
from pathlib import Path

from auteur.portfolio.models import (
    ExcludedCombination,
    MAX_COMBINATIONS_DEFAULT,
    PortfolioConstraint,
    PortfolioDecision,
    PortfolioScenario,
    PortfolioScenarioState,
    _stable_id,
)
from auteur.portfolio.constraints import ConstraintEngine


class CombinationGenerator:
    """Generate bounded deterministic candidate combinations.

    The generator never produces an unbounded Cartesian product.
    Hard limits are enforced by default.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.constraint_engine = ConstraintEngine()

    def generate(
        self,
        decisions: list[PortfolioDecision],
        constraints: list[PortfolioConstraint] | None = None,
        max_combinations: int = MAX_COMBINATIONS_DEFAULT,
        portfolio_id: str = "",
    ) -> tuple[list[PortfolioScenario], list[ExcludedCombination], int]:
        """Generate bounded candidate combinations.

        Returns (valid_scenarios, excluded_combinations, theoretical_count).

        Raises ValueError if the theoretical count exceeds limits
        and cannot be bounded.
        """
        constraints = constraints or []
        candidate_lists = [d.candidate_ids for d in decisions]
        decision_ids = [d.decision_id for d in decisions]

        # Theoretical count
        theoretical = 1
        for cl in candidate_lists:
            theoretical *= len(cl)

        # Check limits
        if theoretical > max_combinations * 10:
            raise ValueError(
                f"Theoretical combination count {theoretical} exceeds "
                f"practical limit of {max_combinations * 10}. "
                f"Reduce candidates or increase --max-combinations."
            )

        # Generate only up to max_combinations valid ones
        valid: list[PortfolioScenario] = []
        excluded: list[ExcludedCombination] = []
        count = 0

        for product in itertools.product(*candidate_lists):
            if len(valid) >= max_combinations:
                break

            assignment = dict(zip(decision_ids, product))

            # Check hard constraints
            is_valid = True
            for c in constraints:
                ok, reason = self.constraint_engine.check_incompatibility(assignment, c)
                if not ok:
                    excluded.append(ExcludedCombination(
                        assignment=assignment,
                        reason=reason,
                        constraint_id=c.constraint_id,
                        evidence=c.evidence_classification,
                    ))
                    is_valid = False
                    break

            if not is_valid:
                continue

            # Valid combination
            scenario_id = _stable_id("ps", portfolio_id or "port", str(count))
            scenario = PortfolioScenario(
                scenario_id=scenario_id,
                portfolio_id=portfolio_id or "",
                assignment=assignment,
                state=PortfolioScenarioState.CREATED,
            )
            valid.append(scenario)
            count += 1

        return valid, excluded, theoretical
