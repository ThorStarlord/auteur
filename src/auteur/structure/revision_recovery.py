"""Fail-closed recovery for interrupted Structure revision applications."""

from __future__ import annotations

import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.provenance.store import canonical_content_hash
from auteur.structure.revision_application import _resolve_target_path
from auteur.structure.revision_models import RevisionApplication, RevisionPlanState
from auteur.structure.revision_service import StructuralRevisionPlan


def _load_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else None
    except Exception:
        return None


def _atomic_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _applications_for(root: Path, plan_id: str) -> list[RevisionApplication]:
    directory = root / ".auteur" / "structure" / "revision-applications"
    found: list[RevisionApplication] = []
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.yaml")):
        raw = _load_yaml(path)
        if not raw or raw.get("plan_id") != plan_id:
            continue
        try:
            found.append(RevisionApplication.model_validate(raw))
        except Exception:
            continue
    return found


def _target_observations(root: Path, plan: StructuralRevisionPlan) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for target_id, expected in sorted(plan.target_hashes.items()):
        target = _resolve_target_path(target_id, root)
        actual = canonical_content_hash(target) if target and target.is_file() else None
        observations.append(
            {
                "target_id": target_id,
                "expected_before_hash": expected,
                "actual_hash": actual,
                "unchanged": bool(actual) and actual == expected,
            }
        )
    return observations


def _record_recovery_event(root: Path, plan_id: str, data: dict[str, Any]) -> None:
    event_id = hashlib.sha256(f"{plan_id}:recovery-v1".encode("utf-8")).hexdigest()[:16]
    path = root / ".auteur" / "structure" / "revision-events" / f"{event_id}.yaml"
    _atomic_yaml(
        path,
        {
            "event_id": event_id,
            "plan_id": plan_id,
            "event_type": "recovered_interrupted_apply",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        },
    )


def recover_interrupted_revisions(project_root: Path) -> list[dict[str, Any]]:
    """Reconcile plans stranded in APPLYING without guessing about authority.

    Recovery rules are intentionally conservative:

    - a durable successful application record proves ``APPLIED``;
    - a durable mixed application proves ``PARTIALLY_APPLIED``;
    - no application + every target byte/hash unchanged permits ``READY``;
    - changed/missing/unverifiable targets without an application record become
      ``FAILED`` and require inspection rather than automatic replay.
    """
    root = Path(project_root).resolve()
    plans_dir = root / ".auteur" / "structure" / "revision-plans"
    if not plans_dir.is_dir():
        return []

    outcomes: list[dict[str, Any]] = []
    for path in sorted(plans_dir.glob("*.yaml")):
        raw = _load_yaml(path)
        if not raw:
            continue
        try:
            plan = StructuralRevisionPlan.model_validate(raw)
        except Exception:
            continue
        if plan.state is not RevisionPlanState.APPLYING:
            continue

        applications = _applications_for(root, plan.plan_id)
        observations = _target_observations(root, plan)
        if applications:
            application = applications[-1]
            successes = [result.success for result in application.target_results]
            if successes and all(successes):
                state = RevisionPlanState.APPLIED
                reason = "durable successful application record found"
            elif any(successes):
                state = RevisionPlanState.PARTIALLY_APPLIED
                reason = "durable application record contains mixed target results"
            else:
                state = RevisionPlanState.FAILED
                reason = "durable application record contains no successful targets"
        elif observations and all(item["unchanged"] for item in observations):
            state = RevisionPlanState.READY
            reason = "no application record exists and all authority targets remain unchanged"
        else:
            state = RevisionPlanState.FAILED
            reason = (
                "authority target state cannot be proven unchanged after interrupted apply; "
                "automatic replay is forbidden"
            )

        plan.state = state
        plan.updated_at = datetime.now(timezone.utc).isoformat()
        _atomic_yaml(path, plan.model_dump(mode="json"))
        outcome = {
            "plan_id": plan.plan_id,
            "recovered_state": state.value,
            "reason": reason,
            "target_observations": observations,
            "application_records": len(applications),
            "automatic_replay": False,
        }
        _record_recovery_event(root, plan.plan_id, outcome)
        outcomes.append(outcome)
    return outcomes
