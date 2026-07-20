"""CLI subcommand registration, handlers, and formatters for impact commands."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from auteur.impact.analyzer import ImpactAnalyzer
from auteur.impact.models import ImpactSeverity, PreservationStatus
from auteur.impact.persistence import ImpactStore
from auteur.impact.planner import RepairPlanner


def register_impact_subcommands(sub: argparse._SubParsersAction) -> None:
    """Register the ``impact`` command group on a subparsers object."""
    p = sub.add_parser("impact",
        help="Structural revision propagation and impact planning — detect changes, "
             "trace dependencies, plan repairs.")
    imp_sub = p.add_subparsers(dest="impact_command", required=True)

    # Status
    ps = imp_sub.add_parser("status",
        help="Show unresolved impact summary for the project.")
    ps.add_argument("--project", type=Path, default=Path("."),
        help="Project root directory (default: current directory).")
    ps.add_argument("--json", action="store_true",
        help="Output as JSON.")

    # Analyze
    pa = imp_sub.add_parser("analyze",
        help="Analyze current project changes and dependencies.")
    pa.add_argument("--project", type=Path, default=Path("."),
        help="Project root directory (default: current directory).")
    pa.add_argument("--chapter", type=int, default=None,
        help="Scope analysis to a specific chapter.")
    pa.add_argument("--artifact", type=str, default=None,
        help="Scope analysis to a specific artifact ID.")
    pa.add_argument("--json", action="store_true",
        help="Output as JSON.")
    pa.add_argument("--save", action="store_true",
        help="Persist the analysis report.")

    # Explain
    pe = imp_sub.add_parser("explain",
        help="Show dependency paths and rules for an artifact or impact finding.")
    pe.add_argument("target", type=str,
        help="Artifact ID or impact finding ID to explain.")
    pe.add_argument("--project", type=Path, default=Path("."),
        help="Project root directory (default: current directory).")
    pe.add_argument("--json", action="store_true",
        help="Output as JSON.")

    # Plan
    pp = imp_sub.add_parser("plan",
        help="Show ordered repair actions and preservation guidance.")
    pp.add_argument("--project", type=Path, default=Path("."),
        help="Project root directory (default: current directory).")
    pp.add_argument("--json", action="store_true",
        help="Output as JSON.")
    pp.add_argument("--save", action="store_true",
        help="Persist the repair plan.")


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


class ProjectRootError(Exception):
    """Raised when the project root cannot be resolved."""


def _project_root(project_arg: Path) -> Path:
    """Resolve the project root directory."""
    root = project_arg.resolve()
    if not root.is_dir():
        raise ProjectRootError(f"not a directory: {root}")
    auteur_marker = root / ".auteur"
    if not auteur_marker.exists():
        raise ProjectRootError(f"not an auteur project (no .auteur directory): {root}")
    return root


def handle_impact_status(project_path: Path, *, as_json: bool = False) -> int:
    """Show impact status for the project."""
    try:
        root = _project_root(project_path)
        analyzer = ImpactAnalyzer(root)
        findings = analyzer.analyze()
        store = ImpactStore(root)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    has_impact = analyzer.has_unresolved_impact(findings)
    blocked = [f for f in findings if f.severity == ImpactSeverity.BLOCKED]
    reconcile = [f for f in findings if f.severity == ImpactSeverity.RECONCILE]
    regenerate = [f for f in findings if f.severity == ImpactSeverity.REGENERATE_CANDIDATE]
    review = [f for f in findings if f.severity == ImpactSeverity.REVIEW]
    preserved = [f for f in findings if f.severity == ImpactSeverity.NONE]

    if as_json:
        data = {
            "project": str(root),
            "has_unresolved_impact": has_impact,
            "total_findings": len(findings),
            "blocked": len(blocked),
            "needs_reconcile": len(reconcile),
            "needs_regenerate": len(regenerate),
            "needs_review": len(review),
            "preserved": len(preserved),
            "has_persisted_analyses": store.has_any(),
        }
        print(json.dumps(data, indent=2, default=str))
    else:
        print(f"Impact Status — {root.name}")
        print(f"  {'!' if has_impact else '✓'} Unresolved impact: {'YES' if has_impact else 'NO'}")
        if blocked:
            print(f"  BLOCKED: {len(blocked)}")
            for f in blocked:
                aid = f.affected_artifact.artifact_id if f.affected_artifact else "?"
                print(f"    {aid}: {f.reason}")
        if reconcile:
            print(f"  Needs reconcile: {len(reconcile)}")
            for f in reconcile:
                aid = f.affected_artifact.artifact_id if f.affected_artifact else "?"
                print(f"    {aid}")
        if regenerate:
            print(f"  Needs regenerate: {len(regenerate)}")
            for f in regenerate:
                aid = f.affected_artifact.artifact_id if f.affected_artifact else "?"
                print(f"    {aid}")
        if review:
            print(f"  Needs review: {len(review)}")
            for f in review:
                aid = f.affected_artifact.artifact_id if f.affected_artifact else "?"
                print(f"    {aid}")
        if preserved and not has_impact:
            print(f"  Preserved: {len(preserved)}")
        if not findings:
            print("  No findings — project is clean.")

    return 0


def handle_impact_analyze(
    project_path: Path,
    *,
    chapter: int | None = None,
    artifact: str | None = None,
    as_json: bool = False,
    save: bool = False,
) -> int:
    """Run impact analysis."""
    try:
        root = _project_root(project_path)
        analyzer = ImpactAnalyzer(root)
        graph = analyzer.build_graph()
        changes = analyzer.detect_changes(graph)
        findings = analyzer.analyze(graph, changes)

        # Filter by chapter or artifact if requested
        if chapter is not None:
            findings = [f for f in findings
                        if f.affected_artifact and f.affected_artifact.chapter_index == chapter]
            changes = [c for c in changes
                       if c.artifact_ref and c.artifact_ref.chapter_index == chapter]
        if artifact is not None:
            findings = [f for f in findings
                        if f.affected_artifact and artifact in f.affected_artifact.artifact_id]
            changes = [c for c in changes
                       if c.artifact_ref and artifact in c.artifact_ref.artifact_id]
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Persist if requested
    if save:
        try:
            store = ImpactStore(root)
            analysis_data = {
                "analysis_id": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
                "project": str(root),
                "changes": [c.to_dict() for c in changes],
                "findings": [f.to_dict() for f in findings],
                "graph": graph.to_dict(),
            }
            store.save_analysis(analysis_data)
        except Exception as exc:
            print(f"Warning: failed to persist analysis: {exc}", file=sys.stderr)

    if as_json:
        data = {
            "project": str(root),
            "changes": [c.to_dict() for c in changes],
            "findings": [f.to_dict() for f in findings],
        }
        print(json.dumps(data, indent=2, default=str))
    else:
        _print_analysis_output(root, changes, findings)

    return 0


def handle_impact_explain(
    project_path: Path,
    target: str,
    *,
    as_json: bool = False,
) -> int:
    """Explain why an artifact or finding has its impact status."""
    try:
        root = _project_root(project_path)
        analyzer = ImpactAnalyzer(root)
        findings = analyzer.analyze()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Try to find by finding_id first, then by artifact_id
    matched = [f for f in findings if f.finding_id == target]
    if not matched:
        matched = [f for f in findings
                   if f.affected_artifact and f.affected_artifact.artifact_id == target]

    if not matched:
        print(f"No findings for: {target}", file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps([f.to_dict() for f in matched], indent=2, default=str))
    else:
        for f in matched:
            aid = f.affected_artifact.artifact_id if f.affected_artifact else "?"
            print(f"Finding: {f.finding_id}")
            print(f"  Affected: {aid}")
            print(f"  Direct: {f.is_direct}")
            print(f"  Severity: {f.severity.value if hasattr(f.severity, 'value') else f.severity}")
            print(f"  Rule: {f.rule_id}")
            print(f"  Reason: {f.reason}")
            print(f"  Path: {' → '.join(f.dependency_path)}")
            print(f"  Preservation: {f.preservation.value if hasattr(f.preservation, 'value') else f.preservation}")
            print(f"  Recommended: {f.recommended_action}")
            if f.source_change:
                print(f"  Source change: {f.source_change.change_type.value if hasattr(f.source_change.change_type, 'value') else f.source_change.change_type}")

    return 0


def handle_impact_plan(
    project_path: Path,
    *,
    as_json: bool = False,
    save: bool = False,
) -> int:
    """Generate and show a repair plan."""
    try:
        root = _project_root(project_path)
        planner = RepairPlanner(root)
        plan = planner.plan()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if save:
        try:
            store = ImpactStore(root)
            store.save_plan(plan)
        except Exception as exc:
            print(f"Warning: failed to persist plan: {exc}", file=sys.stderr)

    if as_json:
        print(json.dumps(plan.to_dict(), indent=2, default=str))
    else:
        _print_plan_output(root, plan)

    return 0


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


def _print_analysis_output(
    root: Path,
    changes: list,
    findings: list,
) -> None:
    """Print human-readable analysis output."""
    print(f"Impact Analysis — {root.name}")

    if changes:
        print(f"\nChanged:")
        for c in changes:
            aid = c.artifact_ref.artifact_id if c.artifact_ref else "?"
            ct = c.change_type.value if hasattr(c.change_type, 'value') else c.change_type
            print(f"  {aid} — {ct}")
    else:
        print(f"\nNo changes detected.")
        return

    # Directly affected
    direct = [f for f in findings if f.is_direct and f.severity != ImpactSeverity.NONE]
    if direct:
        print(f"\nDirectly affected:")
        for f in _sorted_by_chapter(direct):
            aid = f.affected_artifact.artifact_id if f.affected_artifact else "?"
            sev = f.severity.value.upper() if hasattr(f.severity, 'value') else str(f.severity).upper()
            print(f"  {aid} — {sev}")
            print(f"    {f.reason}")

    # Transitively affected
    transitive = [f for f in findings if not f.is_direct and f.severity != ImpactSeverity.NONE]
    if transitive:
        print(f"\nTransitively affected:")
        for f in _sorted_by_chapter(transitive):
            aid = f.affected_artifact.artifact_id if f.affected_artifact else "?"
            sev = f.severity.value.upper() if hasattr(f.severity, 'value') else str(f.severity).upper()
            print(f"  {aid} — {sev}")

    # Preserved
    preserved = [f for f in findings if f.severity == ImpactSeverity.NONE]
    if preserved:
        print(f"\nPreserved:")
        for f in _sorted_by_chapter(preserved):
            aid = f.affected_artifact.artifact_id if f.affected_artifact else "?"
            print(f"  {aid}")


def _print_plan_output(root: Path, plan) -> None:
    """Print human-readable repair plan output."""
    print(f"Repair Plan — {root.name}")

    if not plan.actions:
        print("  No repair actions required.")
        return

    print(f"\nRecommended repair order:")
    for i, action in enumerate(plan.actions, 1):
        blocking_mark = " [BLOCKING]" if action.blocking else ""
        safe_mark = " [safe]" if action.safe_to_execute else ""
        prereq_str = f" (after: {', '.join(action.prerequisites)})" if action.prerequisites else ""
        print(f"  {i}. {action.title}{blocking_mark}{safe_mark}{prereq_str}")
        print(f"     {action.reason}")
        if action.command:
            print(f"     Command: {action.command}")

    if plan.preserved_artifacts:
        print(f"\nPreserved:")
        for ref in _sorted_refs(plan.preserved_artifacts):
            print(f"  {ref.artifact_id}")

    # Next safe action
    safe_actions = [a for a in plan.actions if a.safe_to_execute and not a.blocking]
    if safe_actions:
        print(f"\nNext safe action:")
        print(f"  {safe_actions[0].command or safe_actions[0].title}")
    elif plan.actions:
        print(f"\nNext action:")
        print(f"  {plan.actions[0].command or plan.actions[0].title}")

    print(f"\nAuthority:")
    print(f"  This is a derived analysis. It does not accept prose or mutate artifacts.")


def _sorted_by_chapter(findings: list) -> list:
    """Sort findings by chapter index, then artifact ID."""
    def _key(f):
        if f.affected_artifact:
            ch = f.affected_artifact.chapter_index or 999
            return (ch, f.affected_artifact.artifact_id)
        return (999, "")
    return sorted(findings, key=_key)


def _sorted_refs(refs: list) -> list:
    """Sort artifact refs deterministically."""
    return sorted(refs, key=lambda r: (r.chapter_index or 999, r.artifact_id))


# Import needed for save in handle_impact_analyze
from datetime import datetime, timezone  # noqa: E402
