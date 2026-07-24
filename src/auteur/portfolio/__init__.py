"""Narrative Decision Portfolio — compare coherent candidate combinations across multiple decisions.

v0.12.0 — builds on v0.11 counterfactual scenarios to generate bounded
candidate portfolios, detect cross-decision conflicts, project combined
downstream effects, and present an operational tradeoff frontier.
"""

from auteur.portfolio.models import (
    NarrativePortfolio,
    PortfolioConstraint,
    PortfolioDecision,
    PortfolioFrontier,
    PortfolioScenario,
    PortfolioState,
    ConstraintType,
    FrontierDimension,
    SCHEMA_VERSION,
)
from auteur.portfolio.service import PortfolioService

__all__ = [
    "NarrativePortfolio",
    "PortfolioConstraint",
    "PortfolioDecision",
    "PortfolioFrontier",
    "PortfolioScenario",
    "PortfolioState",
    "ConstraintType",
    "FrontierDimension",
    "PortfolioService",
    "SCHEMA_VERSION",
]
