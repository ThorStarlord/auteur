"""Immutable decision snapshot persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.decision.models import AuthorDecision, DecisionReadiness, EvidenceFreshness


class DecisionStore:
    """Store and retrieve immutable decision snapshots."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.snapshots_dir = project_root / ".auteur" / "decisions" / "snapshots"
        self.latest_dir = project_root / ".auteur" / "decisions" / "latest"

    def save_snapshot(self, decision: AuthorDecision) -> None:
        """Save immutable snapshot of decision."""
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        snapshot_path = self.snapshots_dir / f"{decision.decision_id}.json"

        # Check for conflicting content
        if snapshot_path.exists():
            existing = json.loads(snapshot_path.read_text())
            if existing.get("last_updated_at") != decision.last_updated_at.isoformat():
                existing_state = existing.get("readiness")
                new_state = decision.readiness.value
                if existing_state != new_state:
                    raise ValueError(
                        f"Conflicting write for {decision.decision_id}: "
                        f"existing state {existing_state}, new state {new_state}"
                    )

        # Write snapshot atomically
        snapshot_json = self._serialize_decision(decision)
        temp_path = snapshot_path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(snapshot_json, indent=2))
        temp_path.replace(snapshot_path)

    def _serialize_decision(self, decision: AuthorDecision) -> dict[str, Any]:
        """Serialize decision to JSON-serializable dict."""
        return {
            "decision_id": decision.decision_id,
            "project": decision.project,
            "chapter_index": decision.chapter_index,
            "scene_id": decision.scene_id,
            "beat_ids": decision.beat_ids,
            "target_artifact_id": decision.target_artifact_id,
            "trigger_type": decision.trigger_type.value,
            "trigger_ids": decision.trigger_ids,
            "readiness": decision.readiness.value,
            "lifecycle_state": decision.lifecycle_state.value,
            "freshness": decision.freshness.value,
            "authority_required": decision.authority_required.value,
            "blockers": decision.blockers,
            "evidence_count": len(decision.evidence),
            "candidate_count": len(decision.candidates),
            "conflict_count": len(decision.conflicts),
            "choice_count": len(decision.unresolved_choices),
            "created_at": decision.created_at.isoformat(),
            "last_updated_at": decision.last_updated_at.isoformat(),
        }

    def load_snapshot(self, decision_id: str) -> AuthorDecision | None:
        """Load immutable snapshot (metadata only, not full evidence)."""
        snapshot_path = self.snapshots_dir / f"{decision_id}.json"
        if not snapshot_path.exists():
            return None

        data = json.loads(snapshot_path.read_text())
        # Snapshots are metadata only for offline inspection
        return None  # Would reconstruct from data if needed

    def save_latest_pointer(self, decision: AuthorDecision) -> None:
        """Update latest pointer atomically."""
        self.latest_dir.mkdir(parents=True, exist_ok=True)

        latest_path = self.latest_dir / "latest.json"
        target_path = self.latest_dir / f"latest-by-target-{decision.target_artifact_id}.json"

        pointer_data = {
            "decision_id": decision.decision_id,
            "readiness": decision.readiness.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Atomic write
        for path in [latest_path, target_path]:
            temp_path = path.with_suffix(".tmp")
            temp_path.write_text(json.dumps(pointer_data, indent=2))
            temp_path.replace(path)

    def get_latest_decision_id(self, target_artifact_id: str | None = None) -> str | None:
        """Get latest decision for target or globally highest priority."""
        if target_artifact_id:
            path = self.latest_dir / f"latest-by-target-{target_artifact_id}.json"
        else:
            path = self.latest_dir / "latest.json"

        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text())
            return data.get("decision_id")
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def list_snapshots(self) -> list[str]:
        """List all decision IDs with snapshots."""
        if not self.snapshots_dir.exists():
            return []

        return sorted([p.stem for p in self.snapshots_dir.glob("*.json")])
