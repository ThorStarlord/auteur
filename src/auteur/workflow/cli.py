"""CLI subcommand registration, handlers, and formatters for workflow commands."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from auteur.cli_handlers import HandlerResult
from auteur.workflow.engine import WorkflowEngine
from auteur.workflow.models import (
    SAFE_AUTHORITIES,
    WorkflowState,
)


def register_workflow_subcommands(sub: argparse._SubParsersAction) -> None:
    """Register the ``workflow`` command group on a subparsers object."""
    p = sub.add_parser("workflow", help="Guided Author Workflow — assess project state and get recommendations.")
    ws = p.add_subparsers(dest="workflow_command", required=True)

    p_status = ws.add_parser("status",
        help="Show current workflow stage, blockers, and recommended actions.")
    p_status.add_argument("project", type=Path,
        help="Path to the auteur project.")
    p_status.add_argument("--json", action="store_true",
        help="Output as JSON.")

    p_next = ws.add_parser("next",
        help="Show the single next recommended action.")
    p_next.add_argument("project", type=Path,
        help="Path to the auteur project.")
    p_next.add_argument("--json", action="store_true",
        help="Output as JSON.")
    p_next.add_argument("--execute", action="store_true",
        help="Execute the next action if it is safe (read-only, derived, or candidate).")

    p_explain = ws.add_parser("explain",
        help="Explain why a particular stage or blocker exists.")
    p_explain.add_argument("project", type=Path,
        help="Path to the auteur project.")
    p_explain.add_argument("stage", nargs="?", default=None,
        help="Stage name to explain (e.g. identity, structure, drafting).")
    p_explain.add_argument("--json", action="store_true",
        help="Output as JSON.")


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


@dataclass
class WorkflowStatusData:
    state: WorkflowState
    status_dict: dict[str, Any] = field(default_factory=dict)


def handle_workflow_status(project_path: Path) -> HandlerResult:
    """Analyze project and return full workflow status."""
    try:
        from auteur.lifecycle.service import LifecycleService
        from auteur.commitment.service import CommitmentService
        lc = LifecycleService(project_path)
        cm = CommitmentService(project_path)
        engine = WorkflowEngine(project_path, lifecycle_service=lc, commitment_service=cm)
    except Exception:
        engine = WorkflowEngine(project_path)
    try:
        state = engine.analyze()
    except Exception as exc:
        return HandlerResult.failure(f"Failed to analyze workflow: {exc}")

    return HandlerResult.success(data=WorkflowStatusData(state=state))


def handle_workflow_next(
    project_path: Path,
    *,
    execute: bool = False,
) -> HandlerResult:
    """Analyze project and return the single next recommended action."""
    try:
        from auteur.lifecycle.service import LifecycleService
        from auteur.commitment.service import CommitmentService
        lc = LifecycleService(project_path)
        cm = CommitmentService(project_path)
        engine = WorkflowEngine(project_path, lifecycle_service=lc, commitment_service=cm)
    except Exception:
        engine = WorkflowEngine(project_path)
    try:
        state = engine.analyze()
    except Exception as exc:
        return HandlerResult.failure(f"Failed to analyze workflow: {exc}")
    if not state.actions:
        return HandlerResult.success(
            data=WorkflowStatusData(state=state),
        )

    next_action = state.actions[0]

    # Check for lifecycle alerts
    lc = state.lifecycle or {}
    alerts: list[str] = []
    if lc.get("diverged", 0) > 0:
        alerts.append(f"{lc['diverged']} commitment(s) diverged from live state")
    if lc.get("with_gaps", 0) > 0:
        alerts.append(f"{lc['with_gaps']} decision(s) have lifecycle gaps")

    if execute:
        result = engine.execute(next_action)
        if not result.get("executed"):
            return HandlerResult.failure(
                result.get("error", f"Execution failed (exit {result.get('exit_code')})"),
                exit_code=result.get("exit_code", 4),
            )
        return HandlerResult.success(data={
            **result,
            "alerts": alerts,
        })

    return HandlerResult.success(
        data={
            "action": next_action,
            "executed": False,
            "alerts": alerts,
        }
    )


def handle_workflow_explain(
    project_path: Path,
    stage_name: str | None = None,
) -> HandlerResult:
    """Analyze project and return an explanation of current state or a specific stage."""
    try:
        from auteur.lifecycle.service import LifecycleService
        from auteur.commitment.service import CommitmentService
        lc = LifecycleService(project_path)
        cm = CommitmentService(project_path)
        engine = WorkflowEngine(project_path, lifecycle_service=lc, commitment_service=cm)
    except Exception:
        engine = WorkflowEngine(project_path)
    try:
        state = engine.analyze()
    except Exception as exc:
        return HandlerResult.failure(f"Failed to analyze workflow: {exc}")

    data = {
        "summary": state.status_summary,
        "current_stage": state.current_stage.value if state.current_stage else None,
        "lifecycle": state.lifecycle,
        "commitment": state.commitment,
    }

    if stage_name:
        if stage_name == "lifecycle":
            # Return lifecycle-specific explanation
            lc = state.lifecycle or {}
            data["explanation"] = _explain_lifecycle(lc)
            return HandlerResult.success(data=data)
        match = state.stage_by_name(stage_name)
        if not match:
            return HandlerResult.failure(f"Unknown stage: {stage_name}")
        data.update({
            "stage": match.stage.value,
            "is_complete": match.is_complete,
            "current_artifact": match.current_artifact,
            "blockers": [
                {
                    "category": b.category.value,
                    "severity": b.severity.value,
                    "message": b.message,
                    "artifact": b.artifact,
                }
                for b in match.blockers
            ],
        })
        return HandlerResult.success(data=data)

    return HandlerResult.success(data=data)

# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


def format_workflow_status(result: HandlerResult) -> str | None:
    """Format workflow status for terminal output."""
    if not result.is_success:
        return f"Error: {result.error}"
    if isinstance(result.data, WorkflowStatusData):
        state = result.data.state
    elif isinstance(result.data, dict):
        state = result.data.get("state", result.data)
        return json.dumps(result.data, indent=2, default=str)
    else:
        return json.dumps(result.data, indent=2, default=str) if result.data else ""

    lines = [f"Project: {state.project_path}", f"Summary: {state.status_summary}"]
    lines.append("")

    if state.current_stage:
        lines.append(f"Current Stage: {state.current_stage.value}")
    else:
        lines.append("Current Stage: (complete)")

    lines.append("")
    lines.append("Stages:")
    for sp in state.stages:
        icon = "+" if sp.is_complete else "-"
        blockers = len(sp.blockers)
        b_str = f" ({blockers} blocker(s))" if blockers else ""
        lines.append(f"  [{icon}] {sp.stage.value}{b_str}")


    # Lifecycle section
    lc = state.lifecycle or {}
    total = lc.get("total_decisions", 0)
    if total > 0:
        lines.append("")
        lines.append("Lifecycle:")
        lines.append(f"  Decisions:       {total} total")
        by_stage = lc.get("by_stage", {})
        for stage_key in ["open", "evidence_gathered", "simulated", "portfolio",
                           "under_review", "acceptance_ready", "accepted", "committed"]:
            count = by_stage.get(stage_key, 0)
            if count > 0:
                lines.append(f"    {stage_key.replace('_', ' ').title():<18} {count}")
        if lc.get("diverged", 0) > 0:
            lines.append(f"  Diverged:        {lc['diverged']}")
        if lc.get("with_gaps", 0) > 0:
            lines.append(f"  With gaps:       {lc['with_gaps']}")

    # Commitment section
    cm = state.commitment or {}
    cm_total = cm.get("total_commitments", 0)
    if cm_total > 0 or cm.get("has_commitments"):
        lines.append("")
        lines.append("Commitments:")
        lines.append(f"  Total:           {cm_total}")
        cm_state = cm.get("state", "")
        if cm_state:
            lines.append(f"  State:           {cm_state}")
        cs_done = cm.get("completed_steps", 0)
        cs_total = cm.get("total_steps", 0)
        if cs_total > 0:
            lines.append(f"  Execution:       {cs_done}/{cs_total} steps")
        asgn = cm.get("assignments", 0)
        if asgn > 0:
            lines.append(f"  Assignments:     {asgn}")
        if cm.get("diverged", 0) > 0:
            lines.append(f"  Diverged:        {cm['diverged']}")

    if state.blockers:
        lines.append("")
        lines.append("Blockers:")
        for b in state.blockers:
            lines.append(f"  [{b.severity.value}] {b.category.value}: {b.message}")
            if b.artifact:
                lines.append(f"    artifact: {b.artifact}")

    if state.actions:
        lines.append("")
        lines.append("Recommended actions:")
        for i, a in enumerate(state.actions, 1):
            safe_mark = " [safe]" if a.authority in SAFE_AUTHORITIES else ""
            lines.append(f"  {i}. {a.label}{safe_mark}")
            lines.append(f"     {a.command}")
            if a.description:
                lines.append(f"     {a.description}")

    return "\n".join(lines)


def _explain_lifecycle(lc: dict) -> str:
    """Build a human-readable lifecycle explanation."""
    lines: list[str] = []
    total = lc.get("total_decisions", 0)
    if total == 0:
        lines.append("No decisions in the decision lifecycle.")
        return "\n".join(lines)

    lines.append(f"Decision Lifecycle ({total} total):")
    by_stage = lc.get("by_stage", {})
    for sk in ["open", "evidence_gathered", "simulated", "portfolio",
               "under_review", "acceptance_ready", "accepted", "committed"]:
        c = by_stage.get(sk, 0)
        if c > 0:
            lines.append(f"  {sk.replace('_', ' ').title():<18} {c}")

    gaps = lc.get("with_gaps", 0)
    diverged = lc.get("diverged", 0)
    if gaps or diverged:
        lines.append("")
        lines.append("Issues:")
        if diverged > 0:
            lines.append(f"  ⚠ {diverged} commitment(s) diverged from live state")
        if gaps > 0:
            lines.append(f"  · {gaps} decision(s) with lifecycle gaps")

    return "\n".join(lines)
