"""Author Dashboard — unified project overview.

Composes workspace status, decision lifecycle data, and workflow
alerts into a single author-facing summary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_dashboard(project_root: Path) -> dict[str, Any]:
    """Build a unified dashboard dict by composing status, lifecycle, and alerts.

    Parameters
    ----------
    project_root : Path
        Path to the auteur project.

    Returns
    -------
    dict
        Dashboard data with keys: status, lifecycle, alerts, commitment.
    """
    dashboard: dict[str, Any] = {
        "project": str(project_root),
        "status": {},
        "lifecycle": {},
        "alerts": [],
        "commitment": {},
    }

    # Gather workspace status
    from auteur.status import gather_status
    try:
        status = gather_status(project_root)
        dashboard["status"] = status
    except Exception as exc:
        dashboard["alerts"].append({"severity": "error", "message": f"Status failed: {exc}"})

    # Gather lifecycle data
    from auteur.lifecycle.service import LifecycleService
    try:
        lc = LifecycleService(project_root)
        dashboard["lifecycle"] = lc.get_status()
    except Exception as exc:
        dashboard["alerts"].append({"severity": "warning", "message": f"Lifecycle data unavailable: {exc}"})

    # Gather commitment data
    from auteur.commitment.service import CommitmentService
    try:
        cm = CommitmentService(project_root)
        dashboard["commitment"] = cm.get_status()
    except Exception as exc:
        dashboard["alerts"].append({"severity": "info", "message": f"Commitment data unavailable: {exc}"})

    # Check for divergence and gaps
    lc_data = dashboard.get("lifecycle", {})
    if lc_data.get("diverged", 0) > 0:
        dashboard["alerts"].append({
            "severity": "warning",
            "message": f"{lc_data['diverged']} commitment(s) diverged from live state",
        })
    if lc_data.get("with_gaps", 0) > 0:
        dashboard["alerts"].append({
            "severity": "info",
            "message": f"{lc_data['with_gaps']} decision(s) have lifecycle gaps",
        })

    return dashboard


def format_dashboard(data: dict[str, Any]) -> str:
    """Render dashboard data as human-readable text."""
    lines: list[str] = []
    lines.append(f"# Auteur Dashboard")
    lines.append(f"Project: {data.get('project', '?')}")
    lines.append("")

    # Alerts
    alerts = data.get("alerts", [])
    if alerts:
        lines.append("## Alerts")
        for a in alerts:
            tag = {"error": "✗", "warning": "⚠", "info": "·"}.get(a.get("severity", "info"), "·")
            lines.append(f"  {tag} {a['message']}")
        lines.append("")

    # Status summary
    status = data.get("status", {})
    lines.append("## Workspace Status")
    if isinstance(status, dict):
        for key in ["stage", "current_stage", "health", "summary", "current"]:
            val = status.get(key, None)
            if val:
                lines.append(f"  {key.replace('_', ' ').title()}: {val}")
    lines.append("")

    # Lifecycle
    lc = data.get("lifecycle", {})
    lines.append("## Decision Lifecycle")
    total = lc.get("total_decisions", 0)
    if total > 0:
        lines.append(f"  Total decisions:    {total}")
        by_stage = lc.get("by_stage", {})
        for sk in ["open", "evidence_gathered", "simulated", "portfolio",
                    "under_review", "acceptance_ready", "accepted", "committed"]:
            c = by_stage.get(sk, 0)
            if c > 0:
                lines.append(f"    {sk.replace('_', ' ').title():<20} {c}")
    else:
        lines.append("  No decisions tracked.")
    lines.append("")

    # Commitment
    cm = data.get("commitment", {})
    lines.append("## Commitments")
    cm_total = cm.get("total_commitments", 0)
    if cm_total > 0:
        lines.append(f"  Total commitments:  {cm_total}")
        cm_state = cm.get("state", "")
        if cm_state:
            lines.append(f"  State:              {cm_state}")
        if cm.get("has_commitments"):
            lines.append("  Active:             yes")
    else:
        lines.append("  No active commitments.")
    lines.append("")

    # Next step
    lines.append("## Recommended Actions")
    try:
        from auteur.workflow.cli import handle_workflow_next
        result = handle_workflow_next(Path(data["project"]))
        if result.is_success:
            action = result.data.get("action", {})
            if action:
                label = action.label if hasattr(action, "label") else action.get("label", "")
                lines.append(f"  → {label}")
    except Exception:
        lines.append("  Run 'auteur workflow next' for the next action.")

    return "\n".join(lines)
