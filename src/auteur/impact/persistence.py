"""Impact report persistence — immutable historical reports with latest pointer."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.impact.models import RepairPlan


class ImpactStore:
    """Persists and retrieves impact analysis reports and repair plans.

    Layout:
        .auteur/impact/
            analyses/<analysis_id>.json   — immutable
            plans/<plan_id>.json          — immutable
            latest.yaml                   — convenience pointer (replaced)
    """

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self.base_dir = self.project_root / ".auteur" / "impact"
        self.analyses_dir = self.base_dir / "analyses"
        self.plans_dir = self.base_dir / "plans"
        self.latest_path = self.base_dir / "latest.yaml"

    def ensure_dirs(self) -> None:
        self.analyses_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    def save_analysis(self, data: dict[str, Any]) -> str:
        """Save an immutable analysis report. Returns the analysis ID."""
        self.ensure_dirs()
        analysis_id = data.get("analysis_id", datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
        # Only write if not already present (immutable)
        path = self.analyses_dir / f"{analysis_id}.json"
        if not path.exists():
            path.write_text(json.dumps(data, indent=2, default=str, sort_keys=True), encoding="utf-8")
        self._write_latest("analysis", analysis_id)
        return analysis_id

    def save_plan(self, plan: RepairPlan) -> str:
        """Save an immutable repair plan. Returns the plan ID."""
        self.ensure_dirs()
        plan_id = plan.plan_id
        path = self.plans_dir / f"{plan_id}.json"
        if not path.exists():
            path.write_text(json.dumps(plan.to_dict(), indent=2, default=str, sort_keys=True), encoding="utf-8")
        self._write_latest("plan", plan_id)
        return plan_id

    def _write_latest(self, kind: str, identifier: str) -> None:
        """Atomically update the latest.yaml convenience pointer."""
        self.ensure_dirs()
        latest = {
            "latest_analysis_id": identifier if kind == "analysis" else self._read_latest().get("latest_analysis_id"),
            "latest_plan_id": identifier if kind == "plan" else self._read_latest().get("latest_plan_id"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "authority": "derived",
            "canonical": False,
        }
        self.base_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.latest_path.with_suffix(".tmp")
        tmp.write_text(yaml.safe_dump(latest, sort_keys=False), encoding="utf-8")
        tmp.replace(self.latest_path)

    def _read_latest(self) -> dict[str, Any]:
        if not self.latest_path.exists():
            return {"latest_analysis_id": None, "latest_plan_id": None}
        try:
            return yaml.safe_load(self.latest_path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            return {"latest_analysis_id": None, "latest_plan_id": None}

    def load_latest_analysis(self) -> dict[str, Any] | None:
        """Load the most recent analysis report."""
        latest = self._read_latest()
        analysis_id = latest.get("latest_analysis_id")
        if not analysis_id:
            return None
        path = self.analyses_dir / f"{analysis_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def load_latest_plan(self) -> RepairPlan | None:
        """Load the most recent repair plan."""
        latest = self._read_latest()
        plan_id = latest.get("latest_plan_id")
        if not plan_id:
            return None
        path = self.plans_dir / f"{plan_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return RepairPlan.from_dict(data)
        except (OSError, json.JSONDecodeError, KeyError):
            return None

    def list_analyses(self) -> list[str]:
        """Return sorted list of analysis IDs."""
        if not self.analyses_dir.exists():
            return []
        return sorted(p.stem for p in self.analyses_dir.glob("*.json") if p.stem != "latest")

    def list_plans(self) -> list[str]:
        """Return sorted list of plan IDs."""
        if not self.plans_dir.exists():
            return []
        return sorted(p.stem for p in self.plans_dir.glob("*.json") if p.stem != "latest")

    def has_any(self) -> bool:
        """Check if any analyses or plans exist."""
        return bool(self.list_analyses()) or bool(self.list_plans())
