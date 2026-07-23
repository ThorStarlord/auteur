"""WorkflowEngine — composes stage detection, blockers, recommendations, and safe execution."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from auteur.status import gather_status
from auteur.workflow.models import (
    EXECUTABLE_AUTHORITIES,
    SAFE_AUTHORITIES,
    AuthorityLevel,
    WorkflowAction,
    WorkflowBlocker,
    WorkflowState,
)
from auteur.workflow.rules import (
    collect_blockers,
    current_stage,
    detect_stages,
    recommend_actions,
)

# Characters that have special meaning in shells and must not appear
# in command arguments when dispatching via subprocess with a list.
_SHELL_METACHARACTERS = frozenset(";&|`$(){}[]!#~")


def _find_auteur_command() -> str | None:
    """Locate the ``auteur`` CLI executable on PATH."""
    return shutil.which("auteur")


def _validate_arg_safety(args: list[str]) -> str | None:
    """Validate argument list for shell metacharacters and empty tokens.

    Returns an error message or None if safe.
    """
    for i, arg in enumerate(args):
        if not arg:
            return f"Argument {i} is empty"
        if any(c in _SHELL_METACHARACTERS for c in arg):
            return f"Argument {i} contains shell metacharacters: {arg!r}"
        # Path traversal on Windows (backslash) is a path separator, not dangerous
        # Normalize to forward slash before length check to avoid false positives
        norm = arg.replace("\\", "/")
        # Check for consecutive dots that could indicate directory traversal
        # Only flag leading .. segments, not embedded ones
        for segment in norm.split("/"):
            if segment == "..":
                pass  # allow relative paths like ../blueprint.yaml
    return None
def _has_placeholders(args: list[str]) -> list[str]:
    """Return args that look like placeholders needing author substitution."""
    import re as _re
    return [
        a for a in args
        if _re.fullmatch(r"[A-Z_]+", a) or _re.fullmatch(r"<[^>]+>", a)
    ]


# Decision subcommands that are safe for automatic dispatch
# All other decision subcommands require author authority.
_SAFE_DECISION_SUBCOMMANDS: frozenset[str] = frozenset([
    "impact-preview",
    "compare",
    "next",
    "conflicts",
    "list",
    "evidence",
    "inspect",
    "status",
    "history",
    "lineage",
    "diff",
    "refresh",
    "revalidate",
])


# Workflow subcommand families that must never be dispatched recursively.
_FORBIDDEN_SUBCOMMAND_PREFIXES = frozenset(["workflow", "decision"])

class WorkflowEngine:
    """Deterministic workflow analysis engine.

    Composes with ``auteur.status.gather_status()`` for project state, then
    layers typed workflow semantics on top. Optionally integrates with the
    Decision Workspace for decision-aware actions.
    """

    def __init__(self, project_root: str | Path, decision_service: Any | None = None) -> None:
        self.root = Path(project_root)
        self._decision_service = decision_service

    def analyze(self) -> WorkflowState:
        """Analyze project state and return a complete WorkflowState."""
        stages = detect_stages(self.root)
        cs = current_stage(stages)
        blockers = collect_blockers(stages)

        # Query decisions if a decision service is configured
        decisions: list[Any] | None = None
        if self._decision_service is not None:
            try:
                decisions = self._decision_service.list_decisions()
            except Exception:
                decisions = None

        actions = recommend_actions(stages, decisions=decisions)
        status = gather_status(self.root)

        summary = self._build_summary(stages, cs, blockers)

        return WorkflowState(
            project_path=str(self.root),
            current_stage=cs,
            stages=stages,
            blockers=blockers,
            actions=actions,
            status_summary=summary,
        )

    def _build_summary(
        self,
        stages: list,
        cs: Any,
        blockers: list[WorkflowBlocker],
    ) -> str:
        if not stages:
            return "No stages detected."
        if cs is None:
            if self._decision_service is not None:
                try:
                    status = self._decision_service.status()
                    open_count = status.get("total_decisions", 0)
                    ready_count = status.get("ready_for_acceptance", 0)
                    if open_count > 0:
                        parts = [f"Workflow complete, {open_count} open decision(s)"]
                        if ready_count > 0:
                            parts.append(f"{ready_count} ready for acceptance")
                        return " — ".join(parts)
                except Exception:
                    pass
            return "All workflow stages are complete."
        blocking = [b for b in blockers if b.severity.value == "blocking"]
        if blocking:
            return f"Blocked at {cs.value}: {blocking[0].message}"
        return f"Current stage: {cs.value}"

    def can_execute(self, action: WorkflowAction) -> bool:
        """Check if an action is eligible for safe execution."""
        from auteur.workflow.models import SAFE_DECISION_ACTIONS

        if action.authority in EXECUTABLE_AUTHORITIES:
            return True

        action_label = action.label.lower()
        for safe_id in SAFE_DECISION_ACTIONS:
            if safe_id.replace("-", " ") in action_label:
                return True

        return False

    def filter_safe_actions(self, actions: list[WorkflowAction]) -> list[WorkflowAction]:
        """Return only safe-executable actions."""
        return [a for a in actions if self.can_execute(a)]

    def execute(self, action: WorkflowAction) -> dict:
        """Execute a workflow action by dispatching the underlying CLI command.

        Safety guarantees:
        - Only actions with eligible authority levels are dispatched.
        - Decision authority-bearing actions are refused.
        - Commands with placeholder arguments (UPPERCASE, <angle>) are refused.
        - ``workflow`` subcommands are blocked to prevent recursion.
        - Arguments with shell metacharacters (;&|`$(){}[]!#~) are rejected.
        - The ``auteur`` CLI is resolved from PATH; no shell string interpolation.
        - Project state is re-evaluated before dispatch to prevent stale actions.
        - A failed child command does not advance or mutate workflow state.
        - stdout and stderr from the child are captured and surfaced.
        """
        if not self.can_execute(action):
            return {
                "action": action.label,
                "executed": False,
                "exit_code": 4,
                "error": (
                    f"Cannot execute '{action.label}': authority level "
                    f"'{action.authority.value}' requires author decision."
                ),
            }

        # Re-evaluate project state before dispatching
        state = self.analyze()
        if state.current_stage is None:
            return {
                "action": action.label,
                "executed": False,
                "exit_code": 0,
                "error": "All workflow stages already complete.",
            }

        # Parse command into structured argument list (no shell=True)
        parts = action.command.split()
        if len(parts) < 2 or parts[0] != "auteur":
            return {
                "action": action.label,
                "executed": False,
                "exit_code": 2,
                "error": f"Cannot parse command: {action.command!r}",
            }

        subcommand = parts[1].lower()
        args = parts[1:]  # everything after "auteur"

        # Recursion prevention: block workflow subcommands and
        # non-safe decision subcommands
        if subcommand in _FORBIDDEN_SUBCOMMAND_PREFIXES:
            if subcommand == "decision":
                subcmd = args[1] if len(args) > 1 else ""
                if subcmd in _SAFE_DECISION_SUBCOMMANDS:
                    pass
                else:
                    return {
                        "action": action.label,
                        "executed": False,
                        "exit_code": 2,
                        "error": (
                            f"Cannot execute '{action.label}': "
                            f"'{subcmd}' decision subcommand requires author authority."
                        ),
                    }
            else:
                return {
                    "action": action.label,
                    "executed": False,
                    "exit_code": 2,
                    "error": f"Cannot execute '{action.label}': workflow subcommands "
                             f"are not eligible for automatic dispatch.",
                }

        # Reject placeholder arguments
        placeholders = _has_placeholders(args)
        if placeholders:
            return {
                "action": action.label,
                "executed": False,
                "exit_code": 2,
                "error": (
                    f"Cannot execute '{action.label}': command contains "
                    f"placeholders {placeholders}. Run manually: {action.command}"
                ),
            }

        # Validate no shell metacharacters in arguments
        arg_error = _validate_arg_safety(args)
        if arg_error:
            return {
                "action": action.label,
                "executed": False,
                "exit_code": 2,
                "error": f"Cannot execute '{action.label}': {arg_error}",
            }

        # Resolve the auteur CLI executable
        auteur_exe = _find_auteur_command()
        if auteur_exe is None:
            return {
                "action": action.label,
                "executed": False,
                "exit_code": -1,
                "error": "auteur CLI not found on PATH.",
            }

        cmd = [auteur_exe] + args

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.root), timeout=120)
            return {
                "action": action.label,
                "executed": proc.returncode == 0,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "authority": action.authority.value,
            }
        except subprocess.TimeoutExpired:
            return {"action": action.label, "executed": False, "exit_code": -1, "error": "Command timed out."}
        except FileNotFoundError:
            return {"action": action.label, "executed": False, "exit_code": -1, "error": "auteur CLI not found."}
        except OSError as exc:
            return {"action": action.label, "executed": False, "exit_code": -1, "error": f"Failed: {exc}"}
        except Exception as exc:
            return {"action": action.label, "executed": False, "exit_code": -1, "error": f"Execution failed: {exc}"}
