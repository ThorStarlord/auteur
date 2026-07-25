"""Revision reconciliation — impact, freshness, and re-evaluation after application.

This module is the reconciliation layer of the Structural Revision pipeline.
It provides three deterministic, read-only-where-possible functions that run
*after* a revision plan has been applied:

1. :func:`reconcile_impact` — measure actual impact against what was predicted.
2. :func:`propagate_freshness` — refresh provenance and dependency records.
3. :func:`reevaluate` — re-run critics on the revised artifact.

All functions accept a
:class:`~auteur.structure.revision_models.RevisionApplication` and a
*project_root* path, and return structured result models.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.impact.analyzer import ImpactAnalyzer
from auteur.impact.models import ImpactSeverity
from auteur.provenance.store import ArtifactStore, canonical_content_hash
from auteur.reasoning.blueprint_coherence import run_blueprint_analysis
from auteur.structure.revision_models import (
    RevisionApplication,
    RevisionFreshnessResult,
    RevisionImpactResult,
    RevisionReevaluationResult,
    RevisionTargetResult,
)

# ---------------------------------------------------------------------------
# Helpers
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


# ---------------------------------------------------------------------------
# 1. reconcile_impact
# ---------------------------------------------------------------------------


def reconcile_impact(
    application: RevisionApplication,
    project_root: str | Path,
) -> RevisionImpactResult:
    """Compute actual impact of the applied revision using the existing
    :class:`~auteur.impact.analyzer.ImpactAnalyzer`.

    This is a **read-only** operation: it builds the dependency graph, detects
    changes between the provenance store and current file state, classifies
    those changes, and reports which artifacts were directly or transitively
    affected.

    Parameters
    ----------
    application:
        The revision application whose *target_results* identify which
        artifacts were mutated.
    project_root:
        Root directory of the project, used to locate the provenance store and
        artifact files.

    Returns
    -------
    RevisionImpactResult
        A structured report of changed, directly-affected, and
        transitively-affected artifact IDs together with predicted-vs-observed
        data.
    """
    project_path = Path(project_root)
    analyzer = ImpactAnalyzer(project_path)

    # Build a graph of all known artifact dependencies
    graph = analyzer.build_graph()

    # Detect all current changes between provenance records and disk
    changes = analyzer.detect_changes(graph)

    # Classify those changes into ImpactFinding records
    findings = analyzer.analyze(graph, changes)

    # Separate findings that correspond to this application's targets vs
    # transitively-affected downstream artifacts
    applied_target_ids = {tr.target_id for tr in application.target_results if tr.success}

    directly_affected: list[str] = []
    transitively_affected: list[str] = []
    changed_artifact_ids: list[str] = []
    invalidated_assumptions: list[str] = []

    for finding in findings:
        if not finding.affected_artifact:
            continue
        aid = finding.affected_artifact.artifact_id
        if aid not in changed_artifact_ids:
            changed_artifact_ids.append(aid)
        if aid in applied_target_ids:
            directly_affected.append(aid)
        else:
            transitively_affected.append(aid)
        if finding.severity in (ImpactSeverity.RECONCILE, ImpactSeverity.BLOCKED):
            msg = f"{aid}: {finding.reason}"
            if msg not in invalidated_assumptions:
                invalidated_assumptions.append(msg)

    # Build predicted-vs-observed map from application target results
    predicted_vs_observed: dict[str, Any] = {}
    for tr in application.target_results:
        predicted_vs_observed[tr.target_id] = {
            "before_hash": tr.before_hash,
            "after_hash": tr.after_hash,
            "success": tr.success,
            "error": tr.error,
            "diff": tr.diff,
        }

    return RevisionImpactResult(
        changed_artifact_ids=changed_artifact_ids,
        directly_affected=directly_affected,
        transitively_affected=transitively_affected,
        invalidated_assumptions=invalidated_assumptions,
        predicted_vs_observed=predicted_vs_observed,
    )


# ---------------------------------------------------------------------------
# 2. propagate_freshness
# ---------------------------------------------------------------------------


def propagate_freshness(
    application: RevisionApplication,
    project_root: str | Path,
) -> RevisionFreshnessResult:
    """Refresh provenance store records after a revision is applied.

    This function:

    1. Reads current freshness state for every target artifact from the
       provenance store (``freshness_before``).
    2. Calls ``store.accept()`` on every successfully-applied target to bump
       its revision and recompute its content hash.
    3. Updates downstream dependency records that point to any changed
       artifact so they reflect the new revision and hash.
    4. Re-reads freshness state (``freshness_after``).
    5. Identifies artifacts that became stale vs those that remain unchanged.

    Parameters
    ----------
    application:
        The revision application with *target_results* listing which artifacts
        were successfully mutated.
    project_root:
        Root directory of the project, used to locate the provenance store.

    Returns
    -------
    RevisionFreshnessResult
        Before/after freshness maps, affected stale artifact IDs, unaffected
        artifact IDs, and IDs eligible for automatic refresh.
    """
    project_path = Path(project_root)
    store = ArtifactStore(project_path)

    # Classify successful vs failed targets
    successful_targets = [tr for tr in application.target_results if tr.success]

    # --- Freshness before ---
    freshness_before: dict[str, str] = {}
    for tr in successful_targets:
        meta = store.current(tr.target_id)
        freshness_before[tr.target_id] = (
            meta.lifecycle.value if meta and hasattr(meta.lifecycle, "value")
            else (str(meta.lifecycle) if meta else "unknown")
        )

    # --- Accept each successfully-applied artifact in the store ---
    for tr in successful_targets:
        target_path = _resolve_target_path(tr.target_id, project_path)
        if target_path and target_path.exists():
            store.accept(target_path, tr.target_type)

    # Update downstream dependency records for every changed artifact
    updated_hashes: dict[str, str] = {}
    for tr in successful_targets:
        target_path = _resolve_target_path(tr.target_id, project_path)
        if not target_path or not target_path.exists():
            continue
        new_hash = _compute_content_hash(target_path)
        updated_hashes[tr.target_id] = new_hash

    if updated_hashes:
        _refresh_downstream_dependencies(store, updated_hashes)

    # --- Freshness after ---
    freshness_after: dict[str, str] = {}
    for tr in successful_targets:
        meta = store.current(tr.target_id)
        freshness_after[tr.target_id] = (
            meta.content_hash if meta else "unknown"
        )

    # --- Identify stale vs unaffected artifacts ---
    affected_stale: list[str] = []
    unaffected_unchanged: list[str] = []
    eligible_refresh: list[str] = []

    for sidecar_file in sorted(store.root.glob("*.yaml")):
        meta = store._load(sidecar_file.stem)
        if meta is None:
            continue
        # Check if any dependency is among the changed targets
        has_stale_dep = any(
            d.artifact_id in updated_hashes for d in meta.dependencies
        )
        if has_stale_dep:
            affected_stale.append(meta.artifact_id)
        elif meta.artifact_id in updated_hashes:
            continue
        else:
            unaffected_unchanged.append(meta.artifact_id)

    # Artifacts whose dependency changed but don't have blockers are eligible
    # for auto-refresh
    from auteur.impact.models import ImpactSeverity as _ImpactSeverity

    for aid in affected_stale:
        target_path = _resolve_target_path(aid, project_path)
        if target_path and target_path.exists():
            eligible_refresh.append(aid)

    return RevisionFreshnessResult(
        freshness_before=freshness_before,
        freshness_after=freshness_after,
        affected_stale=affected_stale,
        unaffected_unchanged=unaffected_unchanged,
        eligible_refresh=eligible_refresh,
    )


def _refresh_downstream_dependencies(
    store: ArtifactStore,
    updated_hashes: dict[str, str],
) -> None:
    """Update dependency records of downstream artifacts so their dependency
    pointers match the new content hashes of the changed artifacts."""
    for sidecar_file in sorted(store.root.glob("*.yaml")):
        dep_meta = store._load(sidecar_file.stem)
        if dep_meta is None:
            continue
        changed = False
        for dep in dep_meta.dependencies:
            if dep.artifact_id in updated_hashes:
                dep.full_content_hash = updated_hashes[dep.artifact_id]
                dep.projected_hash = updated_hashes[dep.artifact_id]
                changed = True
        if changed:
            store._write(dep_meta, snapshot=False)


# ---------------------------------------------------------------------------
# 3. reevaluate
# ---------------------------------------------------------------------------


def reevaluate(
    application: RevisionApplication,
    project_root: str | Path,
) -> RevisionReevaluationResult:
    """Re-run the blueprint.coherence critic on the revised blueprint artifact.

    This is a **read-only** re-evaluation: it loads the current blueprint file
    on disk, runs the deterministic ``blueprint_coherence`` critic, and
    compares findings against the original findings predicted by the revision
    plan (if any were recorded).

    Parameters
    ----------
    application:
        The revision application.  If the blueprint was one of the
        successfully-applied targets, the critic is invoked; otherwise the
        result indicates no critic was run.
    project_root:
        Root directory of the project, used to locate the blueprint file.

    Returns
    -------
    RevisionReevaluationResult
        Original vs new findings, resolved vs remaining finding IDs, and the
        source hash of the artifact the critic was run against.
    """
    project_path = Path(project_root)

    # Determine whether the blueprint was successfully applied
    blueprint_results = [
        tr for tr in application.target_results
        if tr.target_type == "blueprint" and tr.success
    ]

    if not blueprint_results:
        return RevisionReevaluationResult(
            critic_id="",
            original_findings=[],
            new_findings=[],
            resolved_finding_ids=[],
            remaining_finding_ids=[],
            source_hash_used="",
        )

    # Load the current blueprint file
    blueprint_path = project_path / "blueprint.yaml"
    if not blueprint_path.exists():
        return RevisionReevaluationResult(
            critic_id="",
            original_findings=[],
            new_findings=[],
            resolved_finding_ids=[],
            remaining_finding_ids=[],
            source_hash_used="",
        )

    source_hash = _compute_content_hash(blueprint_path)

    # Load raw YAML — run_blueprint_analysis accepts Any and uses dict-key
    # access via the _get / _resolve helpers, so no Pydantic round-trip.
    try:
        import yaml as _yaml
        blueprint_data: Any = _yaml.safe_load(blueprint_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return RevisionReevaluationResult(
            critic_id="",
            original_findings=[],
            new_findings=[],
            resolved_finding_ids=[],
            remaining_finding_ids=[],
            source_hash_used=source_hash,
        )

    # Run the blueprint coherence critic
    new_findings = run_blueprint_analysis(blueprint=blueprint_data)


    # Collect original predicted finding IDs if the plan carried predictions
    original_finding_ids: list[str] = []
    for op in getattr(application, "_plan_operations", []):
        for pred in op.predicted_consequences:
            if pred not in original_finding_ids:
                original_finding_ids.append(pred)

    # Classify findings as resolved (gone) or remaining (still present)
    new_finding_ids: list[str] = []
    for f in new_findings:
        rule_id = f.get("rule", f.get("finding_id", ""))
        if rule_id and rule_id not in new_finding_ids:
            new_finding_ids.append(rule_id)

    resolved_finding_ids = [
        fid for fid in original_finding_ids if fid not in new_finding_ids
    ]
    remaining_finding_ids = [
        fid for fid in new_finding_ids if fid in original_finding_ids
    ]

    return RevisionReevaluationResult(
        critic_id="blueprint.coherence",
        original_findings=[{"finding_id": fid} for fid in original_finding_ids],
        new_findings=new_findings,
        resolved_finding_ids=resolved_finding_ids,
        remaining_finding_ids=remaining_finding_ids,
        source_hash_used=source_hash,
    )
