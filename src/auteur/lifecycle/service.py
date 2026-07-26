"""Lifecycle service — application-service boundary."""

from __future__ import annotations

import logging
from pathlib import Path

from auteur.lifecycle.integrator import LifecycleIntegrator
from auteur.lifecycle.models import DecisionLifecycleEntry, LifecycleSummary

logger = logging.getLogger(__name__)


class LifecycleService:
    """Application-service boundary for decision lifecycle integration."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.integrator = LifecycleIntegrator(self.project_root)

    def status(self) -> list[DecisionLifecycleEntry]:
        """Return lifecycle status for all decisions."""
        return self.integrator.get_lifecycle_entries()

    def inspect(self, decision_id: str) -> DecisionLifecycleEntry | None:
        """Return lifecycle for one decision, or None."""
        entries = self.integrator.get_lifecycle_entries()
        for e in entries:
            if e.decision_id == decision_id:
                return e
        return None

    def summary(self) -> LifecycleSummary:
        """Return aggregate lifecycle counts."""
        return self.integrator.get_summary()
