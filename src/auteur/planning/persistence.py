"""Plan persistence — immutable snapshots and atomic latest pointers.

Layout:
    .auteur/planning/
        snapshots/           — immutable plan JSON snapshots
        history/             — semantic history entries
        latest.yaml          — atomic pointer to current plan
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.planning.models import (
    PlanHistoryEntry,
    ProjectPlan,
    SCHEMA_VERSION,
    plan_from_dict,
)

logger = logging.getLogger(__name__)


class PlanStore:
    """Immutable plan snapshot store with atomic latest pointer."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self._base = self.project_root / ".auteur" / "planning"
        self._snapshots_dir = self._base / "snapshots"
        self._history_dir = self._base / "history"
        self._latest_path = self._base / "latest.yaml"
        self._user_milestones_path = self._base / "user_milestones.yaml"

    def ensure_dirs(self) -> None:
        """Create storage directories if they don't exist."""
        self._snapshots_dir.mkdir(parents=True, exist_ok=True)
        self._history_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, plan: ProjectPlan) -> Path:
        """Save an immutable plan snapshot.

        Returns the path to the saved snapshot.

        Raises:
            ValueError: If a snapshot with the same plan_id but different
                       content already exists.
        """
        self.ensure_dirs()
        snapshot_path = self._snapshots_dir / f"{plan.plan_id}.json"

        if snapshot_path.exists():
            # Verify idempotency
            existing = json.loads(snapshot_path.read_text(encoding="utf-8"))
            new_data = plan.to_dict()

            # Compare relevant fields (exclude timestamps for idempotency)
            existing_sig = self._signature(existing)
            new_sig = self._signature(new_data)
            if existing_sig != new_sig:
                raise ValueError(
                    f"Snapshot conflict: plan {plan.plan_id} already exists "
                    f"with different content"
                )
            return snapshot_path

        # Write snapshot atomically
        data = plan.to_dict()
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(
                dir=str(self._snapshots_dir),
                suffix=".json.tmp",
            )
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            os.replace(tmp, str(snapshot_path))
            tmp = None
        finally:
            if tmp is not None and os.path.exists(tmp):
                os.unlink(tmp)

        return snapshot_path

    def save_latest(self, plan: ProjectPlan) -> None:
        """Atomically update the latest plan pointer."""
        self.ensure_dirs()

        latest_data = {
            "plan_id": plan.plan_id,
            "project": plan.project,
            "horizon": plan.horizon.value,
            "title": plan.title,
            "created_at": plan.created_at,
            "schema_version": SCHEMA_VERSION,
            "open_decision_count": plan.open_decision_count,
            "active_review_session_count": plan.active_review_session_count,
            "blocked_milestone_count": plan.blocked_milestone_count,
            "is_stale": plan.is_stale,
            "stale_reason": plan.stale_reason,
        }

        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(
                dir=str(self._base),
                suffix=".yaml.tmp",
            )
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.dump(latest_data, f, default_flow_style=False, sort_keys=False)
            os.replace(tmp, str(self._latest_path))
            tmp = None
        finally:
            if tmp is not None and os.path.exists(tmp):
                os.unlink(tmp)

    def save_history(self, plan_id: str, entries: list[PlanHistoryEntry]) -> None:
        """Save plan history entries."""
        self.ensure_dirs()
        if not entries:
            return

        history_path = self._history_dir / f"{plan_id}.json"
        data = [{
            "entry_id": e.entry_id,
            "plan_id": e.plan_id,
            "timestamp": e.timestamp,
            "change_type": e.change_type,
            "description": e.description,
            "before_state": e.before_state,
            "after_state": e.after_state,
            "metadata": e.metadata,
        } for e in entries]

        # Append or create
        if history_path.exists():
            existing = json.loads(history_path.read_text(encoding="utf-8"))
            existing.extend(data)
            history_path.write_text(
                json.dumps(existing, indent=2, default=str, ensure_ascii=False),
                encoding="utf-8",
            )
        else:
            history_path.write_text(
                json.dumps(data, indent=2, default=str, ensure_ascii=False),
                encoding="utf-8",
            )

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def load_snapshot(self, plan_id: str) -> ProjectPlan | None:
        """Load a plan snapshot by ID."""
        snapshot_path = self._snapshots_dir / f"{plan_id}.json"
        if not snapshot_path.exists():
            return None
        try:
            data = json.loads(snapshot_path.read_text(encoding="utf-8"))
            return plan_from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not load snapshot {plan_id}: {e}")
            return None

    def load_latest(self) -> ProjectPlan | None:
        """Load the latest plan snapshot."""
        if not self._latest_path.exists():
            return None
        try:
            data = yaml.safe_load(self._latest_path.read_text(encoding="utf-8"))
            if not data or "plan_id" not in data:
                return None
            return self.load_snapshot(data["plan_id"])
        except Exception as e:
            logger.warning(f"Could not load latest plan: {e}")
            return None

    def load_latest_info(self) -> dict[str, Any] | None:
        """Load latest plan pointer info without loading full snapshot."""
        if not self._latest_path.exists():
            return None
        try:
            return yaml.safe_load(self._latest_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_snapshots(self) -> list[dict[str, Any]]:
        """List all saved snapshots with metadata."""
        if not self._snapshots_dir.exists():
            return []
        snapshots = []
        for p in sorted(self._snapshots_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                snapshots.append({
                    "plan_id": data.get("plan_id", p.stem),
                    "created_at": data.get("created_at", ""),
                    "horizon": data.get("horizon", ""),
                    "title": data.get("title", ""),
                    "open_decision_count": data.get("open_decision_count", 0),
                    "active_review_session_count": data.get("active_review_session_count", 0),
                    "blocked_milestone_count": data.get("blocked_milestone_count", 0),
                    "is_stale": data.get("is_stale", False),
                })
            except (json.JSONDecodeError, OSError):
                continue
        return snapshots

    def load_history(self, plan_id: str) -> list[dict[str, Any]]:
        """Load history entries for a plan."""
        history_path = self._history_dir / f"{plan_id}.json"
        if not history_path.exists():
            # Try to find any history that references this plan
            for hp in self._history_dir.glob("*.json"):
                try:
                    data = json.loads(hp.read_text(encoding="utf-8"))
                    if isinstance(data, list) and any(
                        e.get("plan_id") == plan_id for e in data
                    ):
                        return data
                except (json.JSONDecodeError, OSError):
                    continue
            return []
        try:
            return json.loads(history_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def list_all_history(self) -> list[dict[str, Any]]:
        """List all history entries across all plans."""
        if not self._history_dir.exists():
            return []
        entries = []
        for hp in sorted(self._history_dir.glob("*.json")):
            try:
                data = json.loads(hp.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    entries.extend(data)
            except (json.JSONDecodeError, OSError):
                continue
        return sorted(entries, key=lambda x: x.get("timestamp", ""), reverse=True)

    # ------------------------------------------------------------------
    # User-defined milestones
    # ------------------------------------------------------------------

    def save_user_milestones(self, milestones: list[dict[str, Any]]) -> None:
        """Save user-defined milestones."""
        self.ensure_dirs()
        import yaml
        with open(self._user_milestones_path, "w", encoding="utf-8") as f:
            yaml.dump({"milestones": milestones}, f, default_flow_style=False, sort_keys=False)

    def load_user_milestones(self) -> list[dict[str, Any]]:
        """Load user-defined milestones."""
        import yaml
        if not self._user_milestones_path.exists():
            return []
        try:
            data = yaml.safe_load(self._user_milestones_path.read_text(encoding="utf-8"))
            return data.get("milestones", []) if data else []
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _signature(self, data: dict[str, Any]) -> str:
        """Compute a content signature for conflict detection."""
        import hashlib
        # Only compare structural fields, not timestamps or IDs
        sig_parts = []
        for key in ("open_decision_count", "active_review_session_count", "blocked_milestone_count", "milestones", "edges"):
            if key in data:
                sig_parts.append(json.dumps(data[key], sort_keys=True, default=str))
        return hashlib.sha256("|".join(sig_parts).encode()).hexdigest()[:32]
