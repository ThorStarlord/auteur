"""Author Dashboard — unified project overview.

Composes workspace status, decision lifecycle data, author attention, and
workflow alerts into a single author-facing summary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_dashboard(project_root: Path) -> dict[str, Any]:
    """Build a unified dashboard dict by composing read-only project projections."""
    dashboard: dict[str, Any] = {
        "project": str(project_root),
        "status": {},
        "lifecycle": {},
        "alerts": [],
        "commitment": {},
        "author_attention": [],
    }

    from auteur.status import gather_status
    try:
        dashboard["status"] = gather_status(project_root)
    except Exception as exc:
        dashboard["alerts"].append({"severity": "error", "message": f"Status failed: {exc}"})

    from auteur.lifecycle.service import LifecycleService
    try:
        lc_summary = LifecycleService(project_root).summary()
        dashboard["lifecycle"] = (
            lc_summary.to_dict() if hasattr(lc_summary, "to_dict") else {"total_decisions": 0}
        )
    except Exception as exc:
        dashboard["alerts"].append({"severity": "warning", "message": f"Lifecycle data unavailable: {exc}"})

    from auteur.commitment.service import CommitmentService
    try:
        dashboard["commitment"] = CommitmentService(project_root).status()
    except Exception as exc:
        dashboard["alerts"].append({"severity": "info", "message": f"Commitment data unavailable: {exc}"})

    # Newer decision surfaces remain projections over their existing stores.
    # Building the dashboard must never refresh, select, validate, or apply them.
    from auteur.ui.author_attention import build_author_attention
    try:
        dashboard["author_attention"] = build_author_attention(project_root)
    except Exception as exc:
        dashboard["alerts"].append({"severity": "warning", "message": f"Author attention unavailable: {exc}"})

    lc_data = dashboard.get("lifecycle", {})
    if isinstance(lc_data, dict):
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
    lines: list[str] = ["# Auteur Dashboard", f"Project: {data.get('project', '?')}", ""]

    alerts = data.get("alerts", [])
    if alerts:
        lines.append("## Alerts")
        for alert in alerts:
            tag = {"error": "✗", "warning": "⚠", "info": "·"}.get(alert.get("severity", "info"), "·")
            lines.append(f"  {tag} {alert['message']}")
        lines.append("")

    status = data.get("status", {})
    lines.append("## Workspace Status")
    if isinstance(status, dict):
        for key in ["stage", "current_stage", "health", "summary", "current"]:
            value = status.get(key)
            if value:
                lines.append(f"  {key.replace('_', ' ').title()}: {value}")
    lines.append("")

    lifecycle = data.get("lifecycle", {})
    lines.append("## Decision Lifecycle")
    total = lifecycle.get("total_decisions", 0) if isinstance(lifecycle, dict) else 0
    if total > 0:
        lines.append(f"  Total decisions:    {total}")
        by_stage = lifecycle.get("by_stage", {}) if isinstance(lifecycle, dict) else {}
        for stage in ["open", "evidence_gathered", "simulated", "portfolio", "under_review", "acceptance_ready", "accepted", "committed"]:
            count = by_stage.get(stage, 0)
            if count > 0:
                lines.append(f"    {stage.replace('_', ' ').title():<20} {count}")
    else:
        lines.append("  No decisions tracked.")
    lines.append("")

    commitment = data.get("commitment", {})
    lines.append("## Commitments")
    cm_total = commitment.get("total_commitments", 0) if isinstance(commitment, dict) else 0
    if cm_total > 0:
        lines.append(f"  Total commitments:  {cm_total}")
        cm_state = commitment.get("state", "")
        if cm_state:
            lines.append(f"  State:              {cm_state}")
        if commitment.get("has_commitments"):
            lines.append("  Active:             yes")
    else:
        lines.append("  No active commitments.")
    lines.append("")

    attention = data.get("author_attention", [])
    lines.append("## Author Attention")
    if attention:
        for item in attention:
            lines.append(f"  -> [{item['kind']}] {item['state']}: {item['reason']}")
            lines.append(f"     Authority: {item['authority_status']}")
            if item.get("next_command"):
                lines.append(f"     Next: {item['next_command']}")
    else:
        lines.append("  No pending Tutor/proposal/revision item requires attention.")
    lines.append("")

    lines.append("## Recommended Actions")
    try:
        from auteur.workflow.cli import handle_workflow_next

        result = handle_workflow_next(Path(data["project"]))
        if result.is_success and isinstance(result.data, dict):
            action = result.data.get("action", {})
            if action:
                label = action.label if hasattr(action, "label") else action.get("label", "")
                lines.append(f"  -> {label}")
    except Exception:
        lines.append("  Run 'auteur workflow next' for the next action.")

    return "\n".join(lines)
