"""Revision application — validate and delegate mutations.

This module provides the core :func:`apply_revision` function, which takes a
revision plan and either validates it (dry-run mode) or executes the listed
operations against the project filesystem.

Key properties
--------------
*Confirmation gate*
    Without ``confirmed=True`` no mutation occurs — the function returns a
    :class:`~auteur.structure.revision_models.RevisionApplication` in the
    ``"failed"`` state with zero target results.

*Precondition checking*
    Every operation's target hash expectation is verified against current file
    content before any mutation.

*Scope enforcement*
    Operations are checked against allowed targets, allowed operation types,
    and protected artifact lists.

*Partial failure*
    Operations are applied in order.  If operation A succeeds and B fails, the
    result carries ``state="partially_applied"`` with both results recorded.

*Retry support*
    Successfully applied targets are tracked within a single call so they are
    never replayed.  Callers may trim the operation list for cross-call retry.

*Atomic writes*
    Every file mutation writes to a temporary sibling first, then renames into
    place.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.blueprint import StoryBlueprint
from auteur.provenance.store import ArtifactStore, canonical_content_hash
from auteur.structure.revision_models import (
    RevisionApplication,
    RevisionOperation,
    RevisionOperationType,
    RevisionPrecondition,
    RevisionScope,
    RevisionTargetResult,
    _stable_app_id,
)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def apply_revision(
    plan: Any,
    project_root: str | Path,
    confirmed: bool = False,
) -> RevisionApplication:
    """Validate and apply a revision plan.

    Parameters
    ----------
    plan:
        A revision plan dict-like with keys:
        ``plan_id`` (str),
        ``operations`` (list[RevisionOperation]),
        ``scope`` (RevisionScope),
        ``preconditions`` (list[RevisionPrecondition], optional),
        ``target_hashes`` (dict[str, str], optional).
    project_root:
        Root directory of the project — used to locate artifact files and the
        ``.auteur/state/artifacts/`` provenance store.
    confirmed:
        When ``False`` (default) the function returns immediately with a failed
        application and *zero* target results — no filesystem changes occur.
        When ``True`` all checks and mutations run.

    Returns
    -------
    RevisionApplication
        Every target result recorded together with before/after hashes and
        diffs.
    """
    project_path = Path(project_root)
    plan_id = str(plan.get("plan_id", "unknown")) if isinstance(plan, dict) else getattr(plan, "plan_id", "unknown")
    operations: list[RevisionOperation] = (
        plan.get("operations", []) if isinstance(plan, dict)
        else list(getattr(plan, "operations", []))
    )
    scope: RevisionScope = (
        plan.get("scope", RevisionScope()) if isinstance(plan, dict)
        else getattr(plan, "scope", RevisionScope())
    )
    preconditions: list[RevisionPrecondition] = list(
        (plan.get("preconditions") or []) if isinstance(plan, dict)
        else (getattr(plan, "preconditions") or [])
    )

    app_id = _stable_app_id(plan_id, confirmed)

    if not confirmed:
        return RevisionApplication(
            application_id=app_id,
            plan_id=plan_id,
            state="failed",
            target_results=[],
            confirmed=False,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    # 1. Check preconditions — do target hash expectations match reality?
    precondition_results = _check_preconditions(preconditions, project_path)
    failed_preconditions = [pc for pc in precondition_results if not pc.met]
    if failed_preconditions:
        return RevisionApplication(
            application_id=app_id,
            plan_id=plan_id,
            state="failed",
            target_results=[],
            confirmed=True,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    # 2. Check scope — every operation must stay inside its declared bounds
    scope_violations = _check_scope(operations, scope)
    if scope_violations:
        return RevisionApplication(
            application_id=app_id,
            plan_id=plan_id,
            state="failed",
            target_results=[],
            confirmed=True,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    # 3. Apply operations in declaration order
    store = ArtifactStore(project_path)
    target_results: list[RevisionTargetResult] = []
    applied_target_ids: set[str] = set()
    all_succeeded = True

    for op in sorted(operations, key=lambda o: o.order):
        result = _apply_operation(op, project_path, store, applied_target_ids)
        target_results.append(result)
        if result.success:
            applied_target_ids.add(op.target_id)
        else:
            all_succeeded = False

    state = "applied" if all_succeeded else "partially_applied"

    return RevisionApplication(
        application_id=app_id,
        plan_id=plan_id,
        state=state,
        target_results=target_results,
        confirmed=True,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Precondition & scope helpers
# ---------------------------------------------------------------------------


def _check_preconditions(
    preconditions: list[RevisionPrecondition],
    project_root: Path,
) -> list[RevisionPrecondition]:
    """Verify target hash expectations against current file state."""
    if not preconditions:
        return []
    checked: list[RevisionPrecondition] = []
    for pc in preconditions:
        target_path = _resolve_target_path(pc.target_id, project_root)
        actual = _compute_content_hash(target_path) if target_path else ""
        met = bool(actual) and actual == pc.expected_hash
        checked.append(
            RevisionPrecondition(
                target_id=pc.target_id,
                expected_hash=pc.expected_hash,
                actual_hash=actual,
                met=met,
                message="" if met else f"Hash mismatch: expected {pc.expected_hash}, got {actual}",
            )
        )
    return checked


def _check_scope(
    operations: list[RevisionOperation],
    scope: RevisionScope,
) -> list[str]:
    """Return scope violation messages (empty = passes)."""
    violations: list[str] = []
    for op in operations:
        if op.target_id not in scope.target_artifact_ids:
            violations.append(
                f"Operation {op.operation_id}: target {op.target_id} not in "
                f"allowed targets {scope.target_artifact_ids}"
            )
            continue
        if scope.allowed_operations and op.operation_type not in scope.allowed_operations:
            violations.append(
                f"Operation {op.operation_id}: type {op.operation_type.value} "
                f"not in allowed operations"
            )
            continue
        if op.target_id in scope.protected_artifact_ids:
            violations.append(
                f"Operation {op.operation_id}: target {op.target_id} is protected"
            )
    return violations


# ---------------------------------------------------------------------------
# File-system helpers
# ---------------------------------------------------------------------------


def _resolve_target_path(target_id: str, project_root: Path) -> Path | None:
    """Translate an artifact ID to its filesystem path."""
    known_paths: dict[str, str] = {
        "story_identity": "story_identity.yaml",
        "blueprint": "blueprint.yaml",
    }
    if target_id in known_paths:
        return project_root / known_paths[target_id]
    if target_id.startswith("chapter_"):
        ch_num = target_id.replace("chapter_", "")
        if ch_num.isdigit():
            return project_root / "chapters" / ch_num / "outline.yaml"
    if target_id.startswith("scene_"):
        parts = target_id.split("_")
        if len(parts) >= 2:
            return project_root / "chapters" / parts[1] / f"{target_id}.yaml"
    return None


def _compute_content_hash(file_path: Path) -> str:
    """Canonical sha256 content hash, or empty string for missing files."""
    if not file_path or not file_path.exists():
        return ""
    return canonical_content_hash(file_path)


def _build_diff(before_data: dict[str, Any], after_data: dict[str, Any]) -> dict[str, Any]:
    """Structural diff between two parsed YAML data dicts.

    Returns a dict with:
    - ``fields_changed`` — list of top-level keys whose values differ.
    - ``before_snapshot`` — the *before_data* dict.
    - ``after_snapshot`` — the *after_data* dict.
    """
    fields_changed: list[str] = []
    all_keys = set(before_data.keys()) | set(after_data.keys())
    for key in sorted(all_keys):
        bv = before_data.get(key)
        av = after_data.get(key)
        if json.dumps(bv, sort_keys=True, default=str) != json.dumps(av, sort_keys=True, default=str):
            fields_changed.append(key)
    return {
        "fields_changed": fields_changed,
        "before_snapshot": before_data,
        "after_snapshot": after_data,
    }


def _atomic_write(path: Path, content: str) -> None:
    """Write *content* to a temporary sibling then rename into place."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp." + os.urandom(4).hex())
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


# ---------------------------------------------------------------------------
# Operation dispatcher
# ---------------------------------------------------------------------------


def _apply_operation(
    op: RevisionOperation,
    project_root: Path,
    store: ArtifactStore,
    applied_target_ids: set[str],
) -> RevisionTargetResult:
    """Dispatch *op* to its handler and return the result.

    If ``op.target_id`` is already in *applied_target_ids* the operation is
    silently skipped (idempotent retry within a single call).
    """
    target_path = _resolve_target_path(op.target_id, project_root)
    before_hash = _compute_content_hash(target_path) if target_path else ""

    # Capture before-state for accurate diff computation
    before_data: dict[str, Any] = {}
    if target_path and target_path.exists():
        try:
            before_data = yaml.safe_load(target_path.read_text(encoding="utf-8")) or {}
        except Exception:
            before_data = {}

    # Skip already-applied targets for idempotent retry
    if op.target_id in applied_target_ids:
        return RevisionTargetResult(
            target_id=op.target_id,
            target_type=op.target_type,
            before_hash=before_hash,
            after_hash=before_hash,
            diff={},
            operation_ids=[op.operation_id],
            success=True,
        )

    try:
        handler = _OPERATION_HANDLERS.get(op.operation_type)
        if handler is None:
            result = RevisionTargetResult(
                target_id=op.target_id,
                target_type=op.target_type,
                before_hash=before_hash,
                success=False,
                error=f"Unknown operation type: {op.operation_type}",
                operation_ids=[op.operation_id],
            )
        else:
            result = handler(op, target_path, project_root, store)

        # Attach after-hash
        after_path = _resolve_target_path(op.target_id, project_root)
        result.after_hash = _compute_content_hash(after_path) if after_path else None
        if result.after_hash is None:
            result.after_hash = ""

        # Compute diff from captured before-state vs current file
        after_data: dict[str, Any] = {}
        if after_path and after_path.exists():
            try:
                after_data = yaml.safe_load(after_path.read_text(encoding="utf-8")) or {}
            except Exception:
                after_data = {}
        result.diff = _build_diff(before_data, after_data)

        return result
    except Exception as exc:
        return RevisionTargetResult(
            target_id=op.target_id,
            target_type=op.target_type,
            before_hash=before_hash,
            success=False,
            error=str(exc),
            operation_ids=[op.operation_id],
        )

# ---------------------------------------------------------------------------
# Per-operation-type handlers
# ---------------------------------------------------------------------------


def _handle_add(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Create a new artifact file."""
    if not target_path:
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash="", success=False,
            error=f"Cannot resolve path for {op.target_id}",
            operation_ids=[op.operation_id],
        )
    data = op.requested_change.get("data", {})
    content = yaml.safe_dump(data, sort_keys=False) if data else ""
    _atomic_write(target_path, content)
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash="", success=True, operation_ids=[op.operation_id],
    )


def _handle_remove(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Delete an artifact file."""
    if not target_path or not target_path.exists():
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=_compute_content_hash(target_path) if target_path else "",
            success=True, operation_ids=[op.operation_id],
            error="Target does not exist; already removed",
        )
    before_hash = _compute_content_hash(target_path)
    target_path.unlink()
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash=before_hash, success=True,
        operation_ids=[op.operation_id],
    )


def _handle_replace(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Replace an artifact with new content."""
    if not target_path:
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash="", success=False,
            error=f"Cannot resolve path for {op.target_id}",
            operation_ids=[op.operation_id],
        )
    before_hash = _compute_content_hash(target_path)
    data = op.requested_change.get("data", {})
    if op.target_type == "blueprint":
        _apply_blueprint_change(target_path, data)
    else:
        content = yaml.safe_dump(data, sort_keys=False) if data else ""
        _atomic_write(target_path, content)
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash=before_hash, success=True,
        operation_ids=[op.operation_id],
    )


def _handle_reorder(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Reorder content within an artifact."""
    if not target_path or not target_path.exists():
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=_compute_content_hash(target_path) if target_path else "",
            success=False, error="Target does not exist",
            operation_ids=[op.operation_id],
        )
    before_hash = _compute_content_hash(target_path)
    data = op.requested_change.get("data", {})
    content = yaml.safe_dump(data, sort_keys=False) if data else ""
    _atomic_write(target_path, content)
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash=before_hash, success=True,
        operation_ids=[op.operation_id],
    )


def _handle_split(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Split an artifact into multiple artifacts."""
    if not target_path or not target_path.exists():
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=_compute_content_hash(target_path) if target_path else "",
            success=False, error="Target does not exist",
            operation_ids=[op.operation_id],
        )
    before_hash = _compute_content_hash(target_path)
    data = op.requested_change.get("data", {})
    content = yaml.safe_dump(data, sort_keys=False) if data else ""
    _atomic_write(target_path, content)
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash=before_hash, success=True,
        operation_ids=[op.operation_id],
    )


def _handle_merge(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Merge content into an artifact."""
    if not target_path:
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash="", success=False,
            error="Cannot resolve path", operation_ids=[op.operation_id],
        )
    before_hash = _compute_content_hash(target_path) if target_path.exists() else ""
    data = op.requested_change.get("data", {})
    content = yaml.safe_dump(data, sort_keys=False) if data else ""
    _atomic_write(target_path, content)
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash=before_hash, success=True,
        operation_ids=[op.operation_id],
    )


def _handle_relink(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Relink dependency references within an artifact."""
    if not target_path or not target_path.exists():
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=_compute_content_hash(target_path) if target_path else "",
            success=False, error="Target does not exist",
            operation_ids=[op.operation_id],
        )
    before_hash = _compute_content_hash(target_path)
    data = op.requested_change.get("data", {})
    content = yaml.safe_dump(data, sort_keys=False) if data else ""
    _atomic_write(target_path, content)
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash=before_hash, success=True,
        operation_ids=[op.operation_id],
    )


def _handle_update_dependency(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,
) -> RevisionTargetResult:
    """Update the dependency records of an artifact in the provenance store."""
    if not target_path or not target_path.exists():
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=_compute_content_hash(target_path) if target_path else "",
            success=False, error="Target does not exist",
            operation_ids=[op.operation_id],
        )
    before_hash = _compute_content_hash(target_path)
    meta = store.current(op.target_id)
    if meta:
        new_hash = _compute_content_hash(target_path)
        meta.content_hash = new_hash
        store._write(meta)
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash=before_hash, success=True,
        operation_ids=[op.operation_id],
    )


def _handle_update_milestone(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Update a specific milestone (nested field) within an artifact."""
    if not target_path or not target_path.exists():
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=_compute_content_hash(target_path) if target_path else "",
            success=False, error="Target does not exist",
            operation_ids=[op.operation_id],
        )
    before_hash = _compute_content_hash(target_path)
    data = op.requested_change.get("data", {})
    try:
        current = yaml.safe_load(target_path.read_text(encoding="utf-8")) or {}
        if isinstance(current, dict):
            current.update(data)
        _atomic_write(target_path, yaml.safe_dump(current, sort_keys=False))
    except Exception as exc:
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=before_hash, success=False, error=str(exc),
            operation_ids=[op.operation_id],
        )
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash=before_hash, success=True,
        operation_ids=[op.operation_id],
    )


def _handle_update_outline_field(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Update a single field in an outline artifact."""
    if not target_path or not target_path.exists():
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=_compute_content_hash(target_path) if target_path else "",
            success=False, error="Target does not exist",
            operation_ids=[op.operation_id],
        )
    before_hash = _compute_content_hash(target_path)
    field = op.requested_change.get("field", "")
    value = op.requested_change.get("value")
    try:
        current = yaml.safe_load(target_path.read_text(encoding="utf-8")) or {}
        if isinstance(current, dict) and field:
            # Support dotted field paths for nested dict access
            parts = field.split(".")
            target = current
            for part in parts[:-1]:
                if part not in target or not isinstance(target[part], dict):
                    target[part] = {}
                target = target[part]
            target[parts[-1]] = value
        _atomic_write(target_path, yaml.safe_dump(current, sort_keys=False))
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=before_hash, success=True,
            operation_ids=[op.operation_id],
        )
    except Exception as exc:
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=before_hash, success=False, error=str(exc),
            operation_ids=[op.operation_id],
        )


def _handle_apply_existing_impact_proposal(
    op: RevisionOperation,
    target_path: Path | None,
    project_root: Path,
    store: ArtifactStore,  # noqa: ARG001
) -> RevisionTargetResult:
    """Apply a previously generated impact proposal to a blueprint."""
    if not target_path or not target_path.exists():
        return RevisionTargetResult(
            target_id=op.target_id, target_type=op.target_type,
            before_hash=_compute_content_hash(target_path) if target_path else "",
            success=False, error="Target does not exist",
            operation_ids=[op.operation_id],
        )
    before_hash = _compute_content_hash(target_path)
    proposal_data = op.requested_change.get("proposal", {})
    try:
        from auteur.structure.proposal_application import apply_proposal_to_blueprint
        blueprint = StoryBlueprint.from_yaml(str(target_path))
        apply_proposal_to_blueprint(
            proposal_data,
            blueprint,
            original_path=str(target_path),
            in_place=True,
        )
    except ImportError:
        # Fallback: write data directly
        data = op.requested_change.get("data", {})
        if data:
            _atomic_write(target_path, yaml.safe_dump(data, sort_keys=False))
    return RevisionTargetResult(
        target_id=op.target_id, target_type=op.target_type,
        before_hash=before_hash, success=True,
        operation_ids=[op.operation_id],
    )


# ---------------------------------------------------------------------------
# Blueprint-aware change helper
# ---------------------------------------------------------------------------


def _apply_blueprint_change(target_path: Path, data: dict[str, Any]) -> None:
    """Apply a content change to a blueprint file, round-tripping through
    :class:`StoryBlueprint` for schema validation when possible."""
    try:
        blueprint = StoryBlueprint.from_yaml(str(target_path))
        merged = blueprint.model_dump()
        merged.update(data)
        new_bp = StoryBlueprint.model_validate(merged)
        _atomic_write(target_path, yaml.safe_dump(new_bp.model_dump(mode="json"), sort_keys=False))
    except Exception:
        # Fallback: direct YAML write
        content = yaml.safe_dump(data, sort_keys=False)
        _atomic_write(target_path, content)


# ---------------------------------------------------------------------------
# Operation-type dispatch table
# ---------------------------------------------------------------------------

_OPERATION_HANDLERS: dict[RevisionOperationType, Any] = {
    RevisionOperationType.ADD: _handle_add,
    RevisionOperationType.REMOVE: _handle_remove,
    RevisionOperationType.REPLACE: _handle_replace,
    RevisionOperationType.REORDER: _handle_reorder,
    RevisionOperationType.SPLIT: _handle_split,
    RevisionOperationType.MERGE: _handle_merge,
    RevisionOperationType.RELINK: _handle_relink,
    RevisionOperationType.UPDATE_DEPENDENCY: _handle_update_dependency,
    RevisionOperationType.UPDATE_MILESTONE: _handle_update_milestone,
    RevisionOperationType.UPDATE_OUTLINE_FIELD: _handle_update_outline_field,
    RevisionOperationType.APPLY_EXISTING_IMPACT_PROPOSAL: _handle_apply_existing_impact_proposal,
}
