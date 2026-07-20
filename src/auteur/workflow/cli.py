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
    EXECUTABLE_AUTHORITIES,
    SAFE_AUTHORITIES,
    WorkflowAction,
    WorkflowBlocker,
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
        engine = WorkflowEngine(project_path)
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
        engine = WorkflowEngine(project_path)
        state = engine.analyze()
    except Exception as exc:
        return HandlerResult.failure(f"Failed to analyze workflow: {exc}")

    if not state.actions:
        return HandlerResult.success(
            data=WorkflowStatusData(state=state),
        )

    next_action = state.actions[0]

    if execute:
        result = engine.execute(next_action)
        if not result.get("executed"):
            return HandlerResult.failure(
                result.get("error", f"Execution failed (exit {result.get('exit_code')})"),
                exit_code=result.get("exit_code", 4),
            )
        return HandlerResult.success(data=result)

    return HandlerResult.success(
        data={
            "action": next_action,
            "executed": False,
        }
    )


def handle_workflow_explain(
    project_path: Path,
    stage_name: str | None = None,
) -> HandlerResult:
    """Analyze project and return an explanation of current state or a specific stage."""
    try:
        engine = WorkflowEngine(project_path)
        state = engine.analyze()
    except Exception as exc:
        return HandlerResult.failure(f"Failed to analyze workflow: {exc}")

    if stage_name:
        match = state.stage_by_name(stage_name)
        if not match:
            return HandlerResult.failure(f"Unknown stage: {stage_name}")
        return HandlerResult.success(
            data={
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
            }
        )

    return HandlerResult.success(
        data={
            "current_stage": state.current_stage.value if state.current_stage else None,
            "summary": state.status_summary,
        }
    )


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
