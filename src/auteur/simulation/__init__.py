"""Counterfactual Narrative Planning — candidate-specific downstream projections.

v0.11.0 — lets an author compare the projected consequences of multiple
candidate decisions without mutating accepted, canonical, planning,
decision, impact, or review state.
"""

from auteur.simulation.models import (
    CounterfactualBaseline,
    CounterfactualScenario,
    ScenarioAssumption,
    ScenarioComparison,
    ScenarioState,
    ConfidenceLevel,
    ConsequenceCategory,
    ProjectedConsequence,
    ProjectedPlan,
    ProjectedCriticalPath,
    SCHEMA_VERSION,
)
from auteur.simulation.service import SimulationService

__all__ = [
    "CounterfactualBaseline",
    "CounterfactualScenario",
    "ScenarioAssumption",
    "ScenarioComparison",
    "ScenarioState",
    "ConfidenceLevel",
    "ConsequenceCategory",
    "ProjectedConsequence",
    "ProjectedPlan",
    "ProjectedCriticalPath",
    "SimulationService",
    "SCHEMA_VERSION",
]
