"""Immutable decision snapshot persistence with version-aware storage.

All snapshots carry a ``schema_version`` field for forward/backward
compatibility. v0.7.0 metadata-only snapshots (no schema_version) are
detected and upgraded on load via a compatibility transform.
"""

from __future__ import annotations

import enum
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from auteur.decision.contracts import (
    SCHEMA_VERSION,
    compute_snapshot_id,
    upgrade_if_needed,
)
from auteur.decision.models import (
    AuthorDecision,
    CandidateSummary,
    DecisionAction,
    DecisionConflict,
    DecisionEvidence,
    DecisionReadiness,
    DecisionTrigger,
    EvidenceFreshness,
    LifecycleState,
    UnresolvedChoice,
)
from auteur.workflow.models import AuthorityLevel


# =========================================================================
# Deserialization helpers
# =========================================================================


def _deserialize_evidence(data: dict[str, Any]) -> DecisionEvidence:
    """Deserialize evidence from dict, handling ISO datetime strings."""
    return DecisionEvidence(
        evidence_id=data["evidence_id"],
        source_subsystem=data["source_subsystem"],
        source_artifact_id=data["source_artifact_id"],
        claim=data["claim"],
        evidence_type=data["evidence_type"],
        classification=data["classification"],
        freshness=data["freshness"],
        confidence=data.get("confidence"),
        supporting_reference=data.get("supporting_reference"),
        candidate_id=data.get("candidate_id"),
        authority=AuthorityLevel(data.get("authority", "read_only")),
        created_at=_parse_dt(data.get("created_at")),
    )


def _deserialize_candidate(data: dict[str, Any]) -> CandidateSummary:
    """Deserialize candidate summary from dict."""
    return CandidateSummary(
        candidate_id=data["candidate_id"],
        status=data["status"],
        freshness=EvidenceFreshness(data.get("freshness", "current")),
        lineage=data.get("lineage"),
        obligations_satisfied=data.get("obligations_satisfied", []),
        obligations_unsatisfied=data.get("obligations_unsatisfied", []),
        preserved_regions=data.get("preserved_regions", []),
        continuity_conflicts=data.get("continuity_conflicts", []),
        reasoning_evidence=data.get("reasoning_evidence", []),
        reconciliation_status=data.get("reconciliation_status"),
        acceptance_blockers=data.get("acceptance_blockers", []),
    )


def _deserialize_conflict(data: dict[str, Any]) -> DecisionConflict:
    """Deserialize conflict from dict."""
    return DecisionConflict(
        conflict_id=data["conflict_id"],
        title=data["title"],
        claim_a=data["claim_a"],
        claim_b=data["claim_b"],
        affected_candidates=data.get("affected_candidates", []),
        resolution_options=data.get("resolution_options", []),
    )


def _deserialize_choice(data: dict[str, Any]) -> UnresolvedChoice:
    """Deserialize unresolved choice from dict."""
    return UnresolvedChoice(
        choice_id=data["choice_id"],
        question=data["question"],
        options=data.get("options"),
        affected_candidates=data.get("affected_candidates", []),
        supporting_evidence=data.get("supporting_evidence", []),
        tradeoffs=data.get("tradeoffs", []),
        required_authority=AuthorityLevel(data.get("required_authority", "authority_bearing")),
        blocking_status=data.get("blocking_status", True),
        created_at=_parse_dt(data.get("created_at")),
    )


def _deserialize_safe_action(data: dict[str, Any]) -> DecisionAction:
    """Deserialize safe action from dict."""
    return DecisionAction(
        action_id=data["action_id"],
        title=data["title"],
        reason=data.get("reason", ""),
        command=data.get("command"),
        prerequisites=data.get("prerequisites", []),
        safe_to_execute=data.get("safe_to_execute", False),
        authority_level=AuthorityLevel(data.get("authority_level", "read_only")),
        expected_result_state=data.get("expected_result_state", ""),
    )


def _parse_dt(value: Any) -> datetime:
    """Parse ISO datetime string or return current UTC."""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            pass
    return datetime.now(timezone.utc)


def _serialize_enums(obj: Any) -> Any:
    """Recursively serialize Enum values to their .value, leaving others unchanged."""
    if isinstance(obj, dict):
        return {k: _serialize_enums(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_enums(item) for item in obj]
    elif isinstance(obj, enum.Enum):
        return obj.value
    return obj


# =========================================================================
# DecisionStore
# =========================================================================


class DecisionStore:
    """Store and retrieve immutable decision snapshots.

    Storage layout::

        .auteur/decisions/
            snapshots/
                <decision_id>.json      # immutable snapshots (v1 schema)
            latest/
                latest.json             # pointer to highest-priority decision
                latest-by-target-<id>.json  # pointer per target
            lineage/
                <lineage_root>.json     # ordered list of snapshot IDs in chain
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.snapshots_dir = project_root / ".auteur" / "decisions" / "snapshots"
        self.latest_dir = project_root / ".auteur" / "decisions" / "latest"
        self.lineage_dir = project_root / ".auteur" / "decisions" / "lineage"

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save_snapshot(
        self,
        decision: AuthorDecision,
        *,
        preceding_snapshot_id: str | None = None,
    ) -> str:
        """Save immutable snapshot of decision.

        Computes a fresh ``snapshot_id`` when this is a new snapshot in the
        lineage. Re-saves (same snapshot_id) are idempotent and skip duplication.

        Returns:
            The ``snapshot_id`` of the saved snapshot.
        """
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        # Determine snapshot_id: if the decision already has one that matches
        # the last entry in the lineage, this is a re-save (idempotent).
        # Otherwise compute a fresh one.
        snapshot_id = self._resolve_snapshot_id(decision, preceding_snapshot_id)

        snapshot_path = self.snapshots_dir / f"{decision.decision_id}.json"

        # Check for conflicting content:
        # - Lineage mode (preceding_snapshot_id provided): allow state transitions
        # - Legacy mode (no preceding): enforce v0.7.0 conflict detection
        if snapshot_path.exists():
            existing = json.loads(snapshot_path.read_text())
            is_lineage_mode = preceding_snapshot_id is not None

            if not is_lineage_mode or existing.get("snapshot_id") == snapshot_id:
                existing_state = existing.get("readiness")
                new_state = decision.readiness.value if isinstance(decision.readiness, enum.Enum) else decision.readiness
                if existing_state != new_state:
                    raise ValueError(
                        f"Conflicting write for {decision.decision_id}: "
                        f"existing state {existing_state}, new state {new_state}"
                    )

        # Build full serialization
        snapshot_json = self._serialize_full_decision(
            decision,
            snapshot_id=snapshot_id,
            preceding_snapshot_id=preceding_snapshot_id,
        )

        # Write atomically
        temp_path = snapshot_path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(snapshot_json, indent=2, default=str))
        temp_path.replace(snapshot_path)

        # Update lineage
        self._append_to_lineage(
            decision.decision_id,
            snapshot_id,
            preceding_snapshot_id,
        )

        return snapshot_id

    def _resolve_snapshot_id(
        self,
        decision: AuthorDecision,
        preceding_snapshot_id: str | None,
    ) -> str:
        """Determine the snapshot_id to use when saving.

        - If the decision already carries a snapshot_id that appears as the
          last entry in the lineage, reuse it (idempotent re-save).
        - Otherwise compute a fresh one.
        """
        stored = decision.snapshot_id
        if stored and preceding_snapshot_id is not None:
            lineage = self.load_lineage(decision.decision_id)
            if lineage and lineage[-1].get("snapshot_id") == stored:
                return stored
        if stored and preceding_snapshot_id is None:
            # No preceding means it's the first save — check lineage too
            lineage = self.load_lineage(decision.decision_id)
            if not lineage:
                return stored
        # Fresh computation
        return compute_snapshot_id(
            decision.decision_id,
            datetime.now(timezone.utc).isoformat(),
            preceding_snapshot_id,
        )

    def _serialize_full_decision(
        self,
        decision: AuthorDecision,
        *,
        snapshot_id: str,
        preceding_snapshot_id: str | None = None,
    ) -> dict[str, Any]:
        """Serialize decision with full evidence to JSON-safe dict."""
        def _val(v: Any) -> Any:
            return v.value if isinstance(v, enum.Enum) else v

        return {
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": snapshot_id,
            "preceding_snapshot_id": preceding_snapshot_id,
            "decision_id": decision.decision_id,
            "project": decision.project,
            "chapter_index": decision.chapter_index,
            "scene_id": decision.scene_id,
            "beat_ids": decision.beat_ids,
            "target_artifact_id": decision.target_artifact_id,
            "trigger_type": _val(decision.trigger_type),
            "trigger_ids": decision.trigger_ids,
            "readiness": _val(decision.readiness),
            "lifecycle_state": _val(decision.lifecycle_state),
            "freshness": _val(decision.freshness),
            "authority_required": _val(decision.authority_required),
            "blockers": decision.blockers,
            "evidence": _serialize_enums([vars(e) for e in decision.evidence]),
            "candidates": _serialize_enums([vars(c) for c in decision.candidates]),
            "conflicts": _serialize_enums([vars(c) for c in decision.conflicts]),
            "unresolved_choices": _serialize_enums([vars(c) for c in decision.unresolved_choices]),
            "safe_actions": _serialize_enums([vars(a) for a in decision.safe_actions]),
            "source_snapshot": decision.source_snapshot,
            "created_at": decision.created_at.isoformat(),
            "last_updated_at": decision.last_updated_at.isoformat(),
        }

    def save_latest_pointer(self, decision: AuthorDecision) -> None:
        """Update latest pointer atomically."""
        self.latest_dir.mkdir(parents=True, exist_ok=True)

        latest_path = self.latest_dir / "latest.json"
        target_path = self.latest_dir / f"latest-by-target-{decision.target_artifact_id}.json"

        readiness = decision.readiness.value if isinstance(decision.readiness, enum.Enum) else decision.readiness

        pointer_data = {
            "decision_id": decision.decision_id,
            "snapshot_id": decision.snapshot_id,
            "readiness": readiness,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        for path in [latest_path, target_path]:
            temp_path = path.with_suffix(".tmp")
            temp_path.write_text(json.dumps(pointer_data, indent=2))
            temp_path.replace(path)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def load_snapshot(self, decision_id: str) -> AuthorDecision | None:
        """Load and reconstruct full decision from snapshot.

        Handles backward-compatible upgrade from v0.7.0 format.
        Returns None if snapshot does not exist.
        """
        data = self.load_snapshot_raw(decision_id)
        if data is None:
            return None
        return self._rebuild_decision(data)

    def load_snapshot_raw(self, decision_id: str) -> dict[str, Any] | None:
        """Load raw snapshot dict with automatic version upgrade.

        Returns upgraded dict, or None if snapshot does not exist.
        """
        snapshot_path = self.snapshots_dir / f"{decision_id}.json"
        if not snapshot_path.exists():
            return None

        data: dict[str, Any] = json.loads(snapshot_path.read_text())

        try:
            data = upgrade_if_needed(data)
        except ValueError:
            # Unrecognized version — return as-is for manual handling
            return data

        return data

    def _rebuild_decision(self, data: dict[str, Any]) -> AuthorDecision:
        """Rebuild AuthorDecision from a (possibly upgraded) snapshot dict."""
        return AuthorDecision(
            decision_id=data["decision_id"],
            project=data["project"],
            chapter_index=data["chapter_index"],
            scene_id=data.get("scene_id"),
            beat_ids=data.get("beat_ids", []),
            target_artifact_id=data["target_artifact_id"],
            trigger_type=DecisionTrigger(data.get("trigger_type", "impact_finding")),
            trigger_ids=data.get("trigger_ids", []),
            candidates=[_deserialize_candidate(c) for c in data.get("candidates", [])],
            evidence=[_deserialize_evidence(e) for e in data.get("evidence", [])],
            conflicts=[_deserialize_conflict(c) for c in data.get("conflicts", [])],
            unresolved_choices=[_deserialize_choice(c) for c in data.get("unresolved_choices", [])],
            blockers=data.get("blockers", []),
            readiness=DecisionReadiness(data.get("readiness", "blocked")),
            lifecycle_state=LifecycleState(data.get("lifecycle_state", "open")),
            freshness=EvidenceFreshness(data.get("freshness", "current")),
            authority_required=AuthorityLevel(data.get("authority_required", "authority_bearing")),
            safe_actions=[_deserialize_safe_action(a) for a in data.get("safe_actions", [])],
            schema_version=data.get("schema_version", SCHEMA_VERSION),
            snapshot_id=data.get("snapshot_id"),
            preceding_snapshot_id=data.get("preceding_snapshot_id"),
            created_at=_parse_dt(data.get("created_at")),
            last_updated_at=_parse_dt(data.get("last_updated_at")),
            source_snapshot=data.get("source_snapshot", {}),
        )

    # ------------------------------------------------------------------
    # Lineage
    # ------------------------------------------------------------------

    def _append_to_lineage(
        self,
        decision_id: str,
        snapshot_id: str,
        preceding_snapshot_id: str | None,
    ) -> None:
        """Append snapshot_id to the decision's lineage file."""
        self.lineage_dir.mkdir(parents=True, exist_ok=True)
        lineage_path = self.lineage_dir / f"{decision_id}.json"

        lineage: list[dict[str, Any]] = []
        if lineage_path.exists():
            try:
                lineage = json.loads(lineage_path.read_text())
            except (json.JSONDecodeError, FileNotFoundError):
                lineage = []

        # Avoid duplicates
        if any(entry.get("snapshot_id") == snapshot_id for entry in lineage):
            return

        lineage.append({
            "snapshot_id": snapshot_id,
            "preceding_snapshot_id": preceding_snapshot_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        })

        temp_path = lineage_path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(lineage, indent=2))
        temp_path.replace(lineage_path)

    def load_lineage(self, decision_id: str) -> list[dict[str, Any]]:
        """Load lineage chain for a decision.

        Returns ordered list of ``{snapshot_id, preceding_snapshot_id, recorded_at}``.
        Empty list if no lineage exists.
        """
        lineage_path = self.lineage_dir / f"{decision_id}.json"
        if not lineage_path.exists():
            return []
        try:
            return json.loads(lineage_path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def list_lineages(self) -> dict[str, list[str]]:
        """Map lineage_root (decision_id) → [snapshot_id, …]."""
        if not self.lineage_dir.exists():
            return {}
        result: dict[str, list[str]] = {}
        for path in self.lineage_dir.glob("*.json"):
            try:
                entries = json.loads(path.read_text())
                root = path.stem
                result[root] = [e["snapshot_id"] for e in entries]
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        return result

    def get_lineage_root(self, decision_id: str) -> str | None:
        """Get the first snapshot ID in a decision's lineage."""
        entries = self.load_lineage(decision_id)
        if entries:
            return entries[0].get("snapshot_id")
        return None

    # ------------------------------------------------------------------
    # Pointers
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_snapshots(self) -> list[str]:
        """List all decision IDs with snapshots."""
        if not self.snapshots_dir.exists():
            return []
        return sorted([p.stem for p in self.snapshots_dir.glob("*.json")])

    def snapshot_exists(self, decision_id: str, snapshot_id: str | None = None) -> bool:
        """Check if a snapshot exists, optionally matching specific snapshot_id."""
        path = self.snapshots_dir / f"{decision_id}.json"
        if not path.exists():
            return False
        if snapshot_id is None:
            return True
        try:
            data = json.loads(path.read_text())
            return data.get("snapshot_id") == snapshot_id
        except (json.JSONDecodeError, FileNotFoundError):
            return False
