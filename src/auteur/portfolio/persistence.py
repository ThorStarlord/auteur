"""Immutable portfolio storage."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

from auteur.portfolio.models import NarrativePortfolio, PortfolioFrontier, SCHEMA_VERSION

logger = logging.getLogger(__name__)


class PortfolioStore:
    """Immutable portfolio artifact store."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self._base = self.project_root / ".auteur" / "portfolios"
        self._defs_dir = self._base / "definitions"
        self._frontiers_dir = self._base / "frontiers"
        self._latest_path = self._base / "latest.yaml"

    def ensure_dirs(self) -> None:
        for d in [self._defs_dir, self._frontiers_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def save_portfolio(self, portfolio: NarrativePortfolio) -> Path:
        """Save portfolio (overwrites existing)."""
        self.ensure_dirs()
        path = self._defs_dir / f"{portfolio.portfolio_id}.json"
        data = portfolio.to_dict()
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

    def load_portfolio(self, portfolio_id: str) -> NarrativePortfolio | None:
        path = self._defs_dir / f"{portfolio_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return NarrativePortfolio.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Could not load portfolio {portfolio_id}: {e}")
            return None

    def list_portfolios(self) -> list[dict[str, Any]]:
        if not self._defs_dir.exists():
            return []
        result = []
        for p in sorted(self._defs_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                result.append({"portfolio_id": data.get("portfolio_id", p.stem), "state": data.get("state", "?"), "created_at": data.get("created_at", "")})
            except (json.JSONDecodeError, OSError):
                continue
        return result

    def save_latest(self, portfolio_id: str) -> None:
        self.ensure_dirs()
        data = {"portfolio_id": portfolio_id}
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
            return data.get("portfolio_id") if data else None
        except Exception:
            return None

    def save_frontier(self, frontier: PortfolioFrontier) -> Path:
        self.ensure_dirs()
        path = self._frontiers_dir / f"{frontier.frontier_id}.json"
        if path.exists():
            return path
        data = {"frontier_id": frontier.frontier_id, "portfolio_id": frontier.portfolio_id,
                "dimensions": frontier.dimensions, "non_dominated_ids": frontier.non_dominated_ids,
                "explanations": frontier.explanations, "schema_version": SCHEMA_VERSION,
                "created_at": frontier.created_at}
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(dir=str(self._frontiers_dir), suffix=".json.tmp")
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
        for subdir, kind in [(self._defs_dir, "portfolio"), (self._frontiers_dir, "frontier")]:
            if not subdir.exists():
                continue
            for p in sorted(subdir.glob("*.json"), reverse=True)[:20]:
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    entries.append({"kind": kind, "id": data.get(f"{kind}_id", data.get("portfolio_id", p.stem)),
                                    "created_at": data.get("created_at", "")})
                except (json.JSONDecodeError, OSError):
                    continue
        return sorted(entries, key=lambda x: x.get("created_at", ""), reverse=True)
