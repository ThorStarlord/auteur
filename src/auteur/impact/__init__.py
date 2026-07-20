"""Structural Revision Propagation and Impact Planning.

Deterministic subsystem for detecting artifact changes, tracing dependencies,
classifying impact severity, generating preservation guidance, and producing
ordered repair plans.
"""

from auteur.impact.models import (
    ArtifactRef,
    ChangeRecord,
    ChangeType,
    DependencyEdge,
    ImpactFinding,
    ImpactSeverity,
    PreservationStatus,
    RepairAction,
    RepairPlan,
)
from auteur.impact.graph import DependencyGraph
from auteur.impact.analyzer import ImpactAnalyzer
from auteur.impact.rules import RULES
from auteur.impact.planner import RepairPlanner
from auteur.impact.persistence import ImpactStore

__all__ = [
    "ArtifactRef",
    "ChangeRecord",
    "ChangeType",
    "DependencyEdge",
    "DependencyGraph",
    "ImpactAnalyzer",
    "ImpactFinding",
    "ImpactSeverity",
    "PreservationStatus",
    "RULES",
    "RepairAction",
    "RepairPlan",
    "RepairPlanner",
    "ImpactStore",
]
