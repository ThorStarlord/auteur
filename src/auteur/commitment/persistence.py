"""Immutable commitment persistence."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

from auteur.commitment.models import (
    ExecutionPlan,
    PortfolioCommitment,
    SCHEMA_VERSION,
)

logger = logging.getLogger(__name__)


class CommitmentStore:
    """Immutable commitment artifact store."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self._base = self.project_root / ".auteur" / "commitments"
        self._defs_dir = self._base / "definitions"
        self._plans_dir = self._base / "plans"
        self._events_dir = self._base / "events"
        self._latest_path = self._base / "latest.yaml"

    def ensure_dirs(self) -> None:
        for d in [self._defs_dir, self._plans_dir, self._events_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def save_commitment(self, commitment: PortfolioCommitment) -> Path:
        self.ensure_dirs()
        path = self._defs_dir / f"{commitment.commitment_id}.json"
        if path.exists():
            return path
        data = commitment.to_dict()
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=str(self._defs_dir), suffix=".json.tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            os.replace(tmp, str(path))
            tmp = None
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        return path

    def load_commitment(self, commitment_id: str) -> PortfolioCommitment | None:
        path = self._defs_dir / f"{commitment_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return PortfolioCommitment(**data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Could not load commitment {commitment_id}: {e}")
            return None

    def list_commitments(self) -> list[dict[str, Any]]:
        if not self._defs_dir.exists():
            return []
        result = []
        for p in sorted(self._defs_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                result.append({"commitment_id": data.get("commitment_id", p.stem),
                               "state": data.get("state", "?"),
                               "assignments": len(data.get("assignments", {})),
                               "created_at": data.get("created_at", "")})
            except (json.JSONDecodeError, OSError):
                continue
        return result

    def save_latest(self, commitment_id: str) -> None:
        self.ensure_dirs()
        data = {"commitment_id": commitment_id}
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
            return data.get("commitment_id") if data else None
        except Exception:
            return None

    def save_plan(self, plan: ExecutionPlan) -> Path:
        self.ensure_dirs()
        path = self._plans_dir / f"{plan.plan_id}.json"
        if path.exists():
            return path
        data = {"plan_id": plan.plan_id, "commitment_id": plan.commitment_id,
                "steps": [{"step_id": s.step_id, "decision_id": s.decision_id,
                           "step_type": s.step_type.value, "state": s.state.value,
                           "safe_to_execute": s.safe_to_execute}
                          for s in plan.steps],
                "created_at": plan.created_at, "schema_version": SCHEMA_VERSION}
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=str(self._plans_dir), suffix=".json.tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            os.replace(tmp, str(path))
            tmp = None
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        return path

    def list_history(self) -> list[dict[str, Any]]:
        entries = []
        for subdir, kind in [(self._defs_dir, "commitment"), (self._plans_dir, "plan")]:
            if not subdir.exists():
                continue
            for p in sorted(subdir.glob("*.json"), reverse=True)[:20]:
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    entries.append({"kind": kind, "id": data.get(f"{kind}_id", data.get("commitment_id", p.stem)),
                                    "created_at": data.get("created_at", "")})
                except (json.JSONDecodeError, OSError):
                    continue
        return sorted(entries, key=lambda x: x.get("created_at", ""), reverse=True)
