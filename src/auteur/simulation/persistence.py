"""Simulation persistence — immutable baselines, scenarios, comparisons."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

from auteur.simulation.models import (
    CounterfactualBaseline,
    CounterfactualScenario,
    ScenarioComparison,
    SCHEMA_VERSION,
)

logger = logging.getLogger(__name__)


class SimulationStore:
    """Immutable simulation artifact store.

    Layout:
        .auteur/simulations/
            baselines/       — immutable baseline JSON snapshots
            scenarios/       — immutable scenario JSON snapshots
            projections/     — immutable projection results
            comparisons/     — immutable comparison JSON snapshots
            promotions/      — promotion records
            latest.yaml      — atomic latest scenario pointer
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self._base = self.project_root / ".auteur" / "simulations"
        self._baselines_dir = self._base / "baselines"
        self._scenarios_dir = self._base / "scenarios"
        self._projections_dir = self._base / "projections"
        self._comparisons_dir = self._base / "comparisons"
        self._promotions_dir = self._base / "promotions"
        self._latest_path = self._base / "latest.yaml"

    def ensure_dirs(self) -> None:
        for d in [self._baselines_dir, self._scenarios_dir, self._projections_dir,
                  self._comparisons_dir, self._promotions_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Baselines
    # ------------------------------------------------------------------

    def save_baseline(self, baseline: CounterfactualBaseline) -> Path:
        self.ensure_dirs()
        path = self._baselines_dir / f"{baseline.baseline_id}.json"
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("baseline_id") != baseline.baseline_id:
                raise ValueError(f"Baseline conflict: {baseline.baseline_id}")
            return path
        data = baseline.to_dict()
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=str(self._baselines_dir), suffix=".json.tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            os.replace(tmp, str(path))
            tmp = None
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        return path

    def load_baseline(self, baseline_id: str) -> CounterfactualBaseline | None:
        path = self._baselines_dir / f"{baseline_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return CounterfactualBaseline(**data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Could not load baseline {baseline_id}: {e}")
            return None

    # ------------------------------------------------------------------
    # Scenarios
    # ------------------------------------------------------------------

    def save_scenario(self, scenario: CounterfactualScenario) -> Path:
        self.ensure_dirs()
        path = self._scenarios_dir / f"{scenario.scenario_id}.json"
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("scenario_id") != scenario.scenario_id:
                raise ValueError(f"Scenario conflict: {scenario.scenario_id}")
            return path
        data = scenario.to_dict()
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=str(self._scenarios_dir), suffix=".json.tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            os.replace(tmp, str(path))
            tmp = None
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        return path

    def load_scenario(self, scenario_id: str) -> CounterfactualScenario | None:
        path = self._scenarios_dir / f"{scenario_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return CounterfactualScenario(**data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Could not load scenario {scenario_id}: {e}")
            return None

    def list_scenarios(self) -> list[dict[str, Any]]:
        if not self._scenarios_dir.exists():
            return []
        scenarios = []
        for p in sorted(self._scenarios_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                scenarios.append({
                    "scenario_id": data.get("scenario_id", p.stem),
                    "decision_id": data.get("decision_id", ""),
                    "candidate_id": data.get("candidate_id", ""),
                    "state": data.get("state", "?"),
                    "created_at": data.get("created_at", ""),
                })
            except (json.JSONDecodeError, OSError):
                continue
        return scenarios

    def save_latest(self, scenario_id: str) -> None:
        self.ensure_dirs()
        data = {"scenario_id": scenario_id, "updated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat()}
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=str(self._base), suffix=".yaml.tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            os.replace(tmp, str(self._latest_path))
            tmp = None
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)

    def load_latest_id(self) -> str | None:
        if not self._latest_path.exists():
            return None
        try:
            data = yaml.safe_load(self._latest_path.read_text(encoding="utf-8"))
            return data.get("scenario_id") if data else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Comparisons
    # ------------------------------------------------------------------

    def save_comparison(self, comparison: ScenarioComparison) -> Path:
        self.ensure_dirs()
        path = self._comparisons_dir / f"{comparison.comparison_id}.json"
        if path.exists():
            return path
        data = {
            "comparison_id": comparison.comparison_id,
            "scenario_a_id": comparison.scenario_a_id,
            "scenario_b_id": comparison.scenario_b_id,
            "shared_consequences": [c.consequence_id for c in comparison.shared_consequences],
            "a_only_consequences": [c.consequence_id for c in comparison.a_only_consequences],
            "b_only_consequences": [c.consequence_id for c in comparison.b_only_consequences],
            "evidence_asymmetry": comparison.evidence_asymmetry,
            "uncertainty_asymmetry": comparison.uncertainty_asymmetry,
            "unknowns": comparison.unknowns,
            "schema_version": SCHEMA_VERSION,
            "created_at": comparison.created_at,
        }
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=str(self._comparisons_dir), suffix=".json.tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            os.replace(tmp, str(path))
            tmp = None
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        return path

    # ------------------------------------------------------------------
    # Promotions
    # ------------------------------------------------------------------

    def save_promotion(self, scenario_id: str, review_session_id: str) -> Path:
        self.ensure_dirs()
        from datetime import datetime, timezone
        prom_id = _stable_id("promo", scenario_id)
        path = self._promotions_dir / f"{prom_id}.json"
        if path.exists():
            return path
        data = {
            "promotion_id": prom_id,
            "scenario_id": scenario_id,
            "review_session_id": review_session_id,
            "promoted_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": SCHEMA_VERSION,
        }
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=str(self._promotions_dir), suffix=".json.tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            os.replace(tmp, str(path))
            tmp = None
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        return path

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def list_history(self) -> list[dict[str, Any]]:
        """List all simulation history entries."""
        entries: list[dict[str, Any]] = []
        for subdir, kind in [
            (self._baselines_dir, "baseline"),
            (self._scenarios_dir, "scenario"),
            (self._comparisons_dir, "comparison"),
            (self._promotions_dir, "promotion"),
        ]:
            if not subdir.exists():
                continue
            for p in sorted(subdir.glob("*.json"), reverse=True)[:20]:
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    entries.append({
                        "kind": kind,
                        "id": data.get(f"{kind}_id", data.get("scenario_id", p.stem)),
                        "created_at": data.get("created_at", data.get("promoted_at", "")),
                        "summary": f"{kind}: {p.stem[:24]}...",
                    })
                except (json.JSONDecodeError, OSError):
                    continue
        return sorted(entries, key=lambda x: x.get("created_at", ""), reverse=True)


def _stable_id(*parts: str) -> str:
    import hashlib
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
