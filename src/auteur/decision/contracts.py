"""Versioned contract schemas for Decision Workspace artifacts.

Each public artifact type has a versioned schema with backward-compatible
loaders and deterministic fixture factories.

Schema versioning:
  - "decision-snapshot-v1" — first versioned schema (v0.8.0)
  - v0.7.0 snapshots have no schema_version field; detected and upgraded
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Version constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "decision-snapshot-v1"
"""Current schema version for decision snapshots."""

SUPPORTED_VERSIONS = frozenset({"decision-snapshot-v1"})
V0_COMPAT_PREFIX = "decision-snapshot-v0"

# ---------------------------------------------------------------------------
# Snapshot ID computation
# ---------------------------------------------------------------------------


def compute_snapshot_id(decision_id: str, timestamp_iso: str, preceding: str | None = None) -> str:
    """Deterministic snapshot ID from decision identity and temporal context."""
    raw = f"{decision_id}|{timestamp_iso}|{preceding or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Schema registry
# ---------------------------------------------------------------------------

_EMPTY_LISTS: frozenset[str] = frozenset({
    "evidence", "candidates", "conflicts", "unresolved_choices",
    "blockers", "beat_ids", "trigger_ids", "safe_actions",
})


def _detect_version(data: dict[str, Any]) -> str | None:
    """Detect schema version from raw data dict.

    Returns:
        Version string if recognized, None if unknown.
    """
    version = data.get("schema_version")
    if version in SUPPORTED_VERSIONS:
        return version
    if version is None:
        # v0.7.0 snapshots have no schema_version field
        # Heuristics:
        # 1. evidence_count present and evidence array absent
        # 2. Minimum fields (decision_id, project, chapter_index, target_artifact_id)
        #    present with no schema_version field (handles minimal exports)
        if "evidence_count" in data and "evidence" not in data:
            return V0_COMPAT_PREFIX
        if (
            "schema_version" not in data
            and "decision_id" in data
            and "project" in data
            and "chapter_index" in data
            and "target_artifact_id" in data
        ):
            return V0_COMPAT_PREFIX
    return None


def upgrade_v0_to_v1(data: dict[str, Any]) -> dict[str, Any]:
    """Upgrade a v0.7.0 snapshot dict to v1 schema in place.

    v0.7.0 stored only metadata (evidence_count, candidate_count, etc.).
    v1 requires evidence/candidates/conflicts arrays, lineage fields,
    and certain required string fields with safe defaults when missing.
    """
    # Add schema version
    data["schema_version"] = SCHEMA_VERSION

    # Add arrays that were stored as counts
    for field in _EMPTY_LISTS:
        data.setdefault(field, [])

    # Add lineage fields
    data.setdefault("snapshot_id", compute_snapshot_id(
        data.get("decision_id", "unknown"),
        data.get("last_updated_at", datetime.now(timezone.utc).isoformat()),
    ))
    data.setdefault("preceding_snapshot_id", None)

    # Add optional fields from AuthorDecision with safe defaults
    data.setdefault("scene_id", None)
    data.setdefault("beat_ids", [])
    data.setdefault("trigger_type", "impact_finding")
    data.setdefault("trigger_ids", [])
    data.setdefault("lifecycle_state", "open")
    data.setdefault("freshness", "current")
    data.setdefault("authority_required", "authority_bearing")
    data.setdefault("source_snapshot", {})
    data.setdefault("safe_actions", [])

    # Remove legacy count-only keys (optional cleanup; harmless to keep)
    for legacy in ("evidence_count", "candidate_count", "conflict_count", "choice_count"):
        data.pop(legacy, None)

    return data


def upgrade_if_needed(data: dict[str, Any]) -> dict[str, Any]:
    """Detect and apply schema upgrade if necessary.

    Returns upgraded data (may be same dict if already current).
    Raises ValueError for unrecognized versions.
    """
    version = _detect_version(data)
    if version is None:
        raise ValueError(
            f"Unrecognized snapshot schema version: {data.get('schema_version')!r}. "
            f"Supported: {sorted(SUPPORTED_VERSIONS)}"
        )
    if version == V0_COMPAT_PREFIX:
        return upgrade_v0_to_v1(data)
    # Already current version
    return data


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_snapshot(data: dict[str, Any]) -> list[str]:
    """Validate a v1 snapshot dict and return list of issues (empty = valid)."""
    issues: list[str] = []

    if data.get("schema_version") != SCHEMA_VERSION:
        issues.append(f"Expected schema_version={SCHEMA_VERSION!r}, got {data.get('schema_version')!r}")

    required_str_fields = ["decision_id", "project", "snapshot_id"]
    for field in required_str_fields:
        if not isinstance(data.get(field), str) or not data[field]:
            issues.append(f"Required string field '{field}' is missing or empty")

    required_int_fields = ["chapter_index"]
    for field in required_int_fields:
        if not isinstance(data.get(field), int):
            issues.append(f"Required int field '{field}' is missing or not an int")

    for field in _EMPTY_LISTS:
        if not isinstance(data.get(field), list):
            issues.append(f"Required list field '{field}' is missing or not a list")

    return issues


# ---------------------------------------------------------------------------
# Fixture factories
# ---------------------------------------------------------------------------


def make_snapshot_fixture(**overrides: Any) -> dict[str, Any]:
    """Create a valid minimal v1 snapshot dict for testing.

    Keys in *overrides* replace the defaults.
    """
    now = datetime.now(timezone.utc).isoformat()
    base = {
        "schema_version": SCHEMA_VERSION,
        "snapshot_id": "test-snapshot-0001",
        "preceding_snapshot_id": None,
        "decision_id": "test-decision-0001",
        "project": "/test/project",
        "chapter_index": 1,
        "scene_id": None,
        "beat_ids": [],
        "target_artifact_id": "target-ch1-scene2",
        "trigger_type": "impact_finding",
        "trigger_ids": ["finding-001"],
        "readiness": "needs_candidate",
        "lifecycle_state": "open",
        "freshness": "current",
        "authority_required": "authority_bearing",
        "blockers": [],
        "evidence": [],
        "candidates": [],
        "conflicts": [],
        "unresolved_choices": [],
        "safe_actions": [],
        "source_snapshot": {},
        "created_at": now,
        "last_updated_at": now,
    }
    base.update(overrides)
    return base


def make_evidence_fixture(**overrides: Any) -> dict[str, Any]:
    """Create a valid evidence dict for testing."""
    base = {
        "evidence_id": "ev-0001",
        "source_subsystem": "impact",
        "source_artifact_id": "finding-001",
        "claim": "Chapter 3 scene 2 character state conflicts with established lore",
        "evidence_type": "impact_finding",
        "classification": "fact",
        "freshness": "current",
        "confidence": None,
        "supporting_reference": "lore/character-arcs.yaml",
        "candidate_id": None,
        "authority": "read_only",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    base.update(overrides)
    return base


def make_candidate_fixture(**overrides: Any) -> dict[str, Any]:
    """Create a valid candidate summary dict for testing."""
    base = {
        "candidate_id": "cand-0001",
        "status": "evaluated",
        "freshness": "current",
        "lineage": None,
        "obligations_satisfied": ["ob-001"],
        "obligations_unsatisfied": [],
        "preserved_regions": [],
        "continuity_conflicts": [],
        "reasoning_evidence": [],
        "reconciliation_status": None,
        "acceptance_blockers": [],
    }
    base.update(overrides)
    return base


def make_acceptance_preparation_fixture(**overrides: Any) -> dict[str, Any]:
    """Create a valid acceptance preparation dict for testing."""
    base = {
        "decision_id": "test-decision-0001",
        "candidate_id": "cand-0001",
        "is_ready": False,
        "blockers": [],
        "verification_results": {},
        "will_change_canonical": False,
        "affected_downstream": [],
        "prepared_at": datetime.now(timezone.utc).isoformat(),
    }
    base.update(overrides)
    return base


def make_next_action_fixture(**overrides: Any) -> dict[str, Any]:
    """Create a valid next-action result dict for testing."""
    base = {
        "decision_id": "test-decision-0001",
        "action_id": "generate-candidate",
        "title": "Generate candidate for target-ch1-scene2",
        "reason": "No viable candidate exists",
        "command": "auteur decision generate-candidate --chapter 1",
        "safe_to_execute": True,
        "authority_level": "candidate_generation",
        "expected_result_state": "needs_evaluation",
    }
    base.update(overrides)
    return base
