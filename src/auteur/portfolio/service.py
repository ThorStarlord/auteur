"""Portfolio service — application-service boundary."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from auteur.portfolio.models import (
    NarrativePortfolio,
    PortfolioDecision,
    PortfolioFrontier,
    PortfolioScenario,
    PortfolioState,
    _stable_id,
)
from auteur.portfolio.selection import PortfolioSelection
from auteur.portfolio.constraints import ConstraintEngine
from auteur.portfolio.combinations import CombinationGenerator
from auteur.portfolio.projection import PortfolioProjector
from auteur.portfolio.comparison import PortfolioComparator, PortfolioComparison
from auteur.portfolio.frontier import FrontierCalculator
from auteur.portfolio.optionality import OptionalityAnalyzer
from auteur.portfolio.persistence import PortfolioStore
from auteur.portfolio.promotion import PortfolioPromoter, PromotionResult

logger = logging.getLogger(__name__)


class PortfolioService:
    """Application-service boundary for narrative decision portfolios."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self._validate_project()
        self.selection = PortfolioSelection(self.project_root)
        self.constraint_engine = ConstraintEngine()
        self.generator = CombinationGenerator(self.project_root)
        self.projector = PortfolioProjector(self.project_root)
        self.comparator = PortfolioComparator()
        self.frontier_calc = FrontierCalculator()
        self.optionality = OptionalityAnalyzer()
        self.store = PortfolioStore(self.project_root)
        self.promoter = PortfolioPromoter(self.project_root)

    def _validate_project(self) -> None:
        marker = self.project_root / ".auteur"
        if not marker.exists():
            raise ValueError(f"Not an Auteur project: {self.project_root}")

    def create_portfolio(
        self,
        decision_candidates: dict[str, list[str]],
        max_combinations: int = 100,
    ) -> NarrativePortfolio:
        """Create a portfolio from decision→candidates mapping."""
        import logging
        log = logging.getLogger(__name__)
        decisions = [
            PortfolioDecision(decision_id=dec_id, candidate_ids=cands)
            for dec_id, cands in decision_candidates.items()
        ]
        portfolio_id = _stable_id("port", str(list(decision_candidates.keys())))

        # Validate candidates — best-effort, warn on failure
        for dec_id, cands in decision_candidates.items():
            for c in cands:
                ok, msg = self.selection.validate_candidate(dec_id, c)
                if not ok:
                    log.warning(f"Candidate validation: {msg}")

        portfolio = NarrativePortfolio(
            portfolio_id=portfolio_id,
            baseline_id="auto",
            decisions=decisions,
            state=PortfolioState.CREATED,
            max_combinations=max_combinations,
        )
        self.store.save_portfolio(portfolio)
        self.store.save_latest(portfolio_id)
        return portfolio

    def generate_combinations(self, portfolio_id: str) -> NarrativePortfolio:
        """Generate candidate combinations for a portfolio."""
        portfolio = self.store.load_portfolio(portfolio_id)
        if portfolio is None:
            raise ValueError(f"Portfolio not found: {portfolio_id}")

        scenarios, excluded, theoretical = self.generator.generate(
            decisions=portfolio.decisions,
            constraints=portfolio.constraints,
            max_combinations=portfolio.max_combinations,
            portfolio_id=portfolio_id,
        )

        portfolio = NarrativePortfolio(
            portfolio_id=portfolio.portfolio_id,
            baseline_id=portfolio.baseline_id,
            decisions=portfolio.decisions,
            constraints=portfolio.constraints,
            state=PortfolioState.GENERATED,
            max_combinations=portfolio.max_combinations,
            theoretical_count=theoretical,
            valid_count=len(scenarios),
            excluded_combinations=excluded,
            scenarios=scenarios,
        )
        self.store.save_portfolio(portfolio)
        self.store.save_latest(portfolio_id)
        return portfolio

    def project_scenario(self, scenario_id: str, portfolio_id: str) -> PortfolioScenario:
        """Project effects for a portfolio scenario."""
        portfolio = self.store.load_portfolio(portfolio_id)
        if portfolio is None:
            raise ValueError(f"Portfolio not found: {portfolio_id}")

        scenario = next((s for s in portfolio.scenarios if s.scenario_id == scenario_id), None)
        if scenario is None:
            raise ValueError(f"Scenario not found: {scenario_id}")

        projected = self.projector.project(scenario)
        return projected

    def compare_scenarios(
        self, a_id: str, b_id: str, portfolio_id: str,
    ) -> PortfolioComparison:
        """Compare two portfolio scenarios."""
        portfolio = self.store.load_portfolio(portfolio_id)
        if portfolio is None:
            raise ValueError(f"Portfolio not found: {portfolio_id}")
        a = next((s for s in portfolio.scenarios if s.scenario_id == a_id), None)
        b = next((s for s in portfolio.scenarios if s.scenario_id == b_id), None)
        if a is None or b is None:
            raise ValueError("Scenario not found")
        return self.comparator.compare(a, b)

    def calculate_frontier(
        self, portfolio_id: str, dimensions: list[str] | None = None,
    ) -> PortfolioFrontier:
        """Calculate non-dominated frontier for a portfolio."""
        portfolio = self.store.load_portfolio(portfolio_id)
        if portfolio is None:
            raise ValueError(f"Portfolio not found: {portfolio_id}")
        return self.frontier_calc.calculate(
            portfolio.scenarios, dimensions=dimensions, portfolio_id=portfolio_id,
        )

    def promote_scenario(
        self, scenario_id: str, portfolio_id: str, confirm: bool = False,
    ) -> PromotionResult:
        """Promote a portfolio scenario into review."""
        portfolio = self.store.load_portfolio(portfolio_id)
        if portfolio is None:
            return PromotionResult(success=False, state="not_found")
        scenario = next((s for s in portfolio.scenarios if s.scenario_id == scenario_id), None)
        if scenario is None:
            return PromotionResult(success=False, state="scenario_not_found")
        return self.promoter.promote(scenario, confirm=confirm)

    def status(self) -> dict[str, Any]:
        latest_id = self.store.load_latest_id()
        portfolios = self.store.list_portfolios()
        return {
            "has_latest": latest_id is not None,
            "latest_portfolio_id": latest_id or "",
            "total_portfolios": len(portfolios),
        }

    def inspect(self, portfolio_id: str) -> NarrativePortfolio | None:
        return self.store.load_portfolio(portfolio_id)

    def list_portfolios(self) -> list[dict[str, Any]]:
        return self.store.list_portfolios()

    def history(self) -> list[dict[str, Any]]:
        return self.store.list_history()
