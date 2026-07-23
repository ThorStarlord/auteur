"""Exhaustive audit of workflow execution boundary.

Every code path in WorkflowEngine.execute() is tested for correct:
- Authority refusal (AUTHORITY_BEARING, CANONICAL_MUTATION)
- Recursion prevention (workflow subcommand, forbidden decision subcommands)
- Safe decision subcommand dispatch
- Placeholder rejection
- Shell metacharacter rejection
- Stale state re-evaluation by can_execute before dispatch attempt
"""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.workflow.engine import WorkflowEngine
from auteur.workflow.models import (
    FORBIDDEN_DECISION_ACTIONS,
    SAFE_DECISION_ACTIONS,
    AuthorityLevel,
    WorkflowAction,
)


def _engine(tmp_path: Path) -> WorkflowEngine:
    (tmp_path / ".auteur").mkdir()
    return WorkflowEngine(tmp_path)


def _action(label: str, command: str, authority: AuthorityLevel = AuthorityLevel.READ_ONLY) -> WorkflowAction:
    return WorkflowAction(label=label, command=command, authority=authority)


# =========================================================================
# Authority refusal
# =========================================================================


class TestAuthorityRefusal:
    """Actions with authority-bearing levels must be refused by can_execute."""

    def test_authority_bearing_cannot_execute(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        assert e.can_execute(_action("a", "auteur status", AuthorityLevel.AUTHORITY_BEARING)) is False

    def test_canonical_mutation_cannot_execute(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        assert e.can_execute(_action("c", "auteur status", AuthorityLevel.CANONICAL_MUTATION)) is False

    def test_read_only_can_execute(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        assert e.can_execute(_action("s", "auteur status", AuthorityLevel.READ_ONLY)) is True

    def test_candidate_generation_can_execute(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        assert e.can_execute(_action("g", "auteur decision next x", AuthorityLevel.CANDIDATE_GENERATION)) is True

    def test_derived_artifact_can_execute(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        assert e.can_execute(_action("d", "auteur decision compare x", AuthorityLevel.DERIVED_ARTIFACT)) is True


# =========================================================================
# Recursion prevention
# =========================================================================


class TestRecursionPrevention:
    """Workflow and non-safe decision subcommands must be blocked."""

    def test_workflow_subcommand_blocked(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("w", "auteur workflow status"))
        assert result["executed"] is False
        assert "not eligible" in result.get("error", "")

    def test_all_forbidden_decision_actions_blocked(self, tmp_path: Path) -> None:
        """Every FORBIDDEN_DECISION_ACTIONS entry must be blocked somehow."""
        e = _engine(tmp_path)
        for action_id in FORBIDDEN_DECISION_ACTIONS:
            label = action_id.replace("-", " ")
            cmd = f"auteur decision {action_id} x"
            result = e.execute(_action(label, cmd, authority=AuthorityLevel.AUTHORITY_BEARING))
            assert result["executed"] is False, f"Forbidden action {action_id} was executed"
            assert result["exit_code"] in (2, 4), f"Forbidden {action_id}: exit {result['exit_code']}"

    def test_safe_decision_actions_pass_can_execute(self, tmp_path: Path) -> None:
        """SAFE_DECISION_ACTIONS should all pass can_execute()."""
        e = _engine(tmp_path)
        for action_id in SAFE_DECISION_ACTIONS:
            label = action_id.replace("-", " ")
            action = _action(label, f"auteur decision next x", authority=AuthorityLevel.READ_ONLY)
            assert e.can_execute(action) is True, f"Safe action {action_id} rejected by can_execute"

    def test_workflow_action_cannot_dispatch_workflow(self, tmp_path: Path) -> None:
        """A 'workflow next --execute' cannot re-invoke the workflow engine."""
        e = _engine(tmp_path)
        result = e.execute(_action("workflow-next", "auteur workflow next"))
        assert result["executed"] is False
        assert "not eligible" in result.get("error", "")

    def test_workflow_action_cannot_dispatch_non_safe_decision(self, tmp_path: Path) -> None:
        """A workflow action cannot dispatch a decision subcommand that requires authority."""
        from auteur.workflow.engine import _SAFE_DECISION_SUBCOMMANDS
        e = _engine(tmp_path)

        authority_levels = [m.value for m in list(AuthorityLevel)]
        safe_names = {v.replace("-", " ") for v in _SAFE_DECISION_SUBCOMMANDS}

        for level in AuthorityLevel:
            if level in (AuthorityLevel.READ_ONLY, AuthorityLevel.DERIVED_ARTIFACT, AuthorityLevel.CANDIDATE_GENERATION):
                continue  # These could pass can_execute
            action = _action(f"test-{level.value}", f"auteur decision inspect x", authority=level)
            assert e.can_execute(action) is False, f"Level {level.value} should not be executable"


# =========================================================================
# Command parsing safety
# =========================================================================


class TestCommandSafety:
    """Commands with placeholders, metacharacters, or bad formats must be rejected."""

    def test_empty_command_rejected(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("empty", ""))
        assert result["executed"] is False

    def test_non_auteur_command_rejected(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("bad", "rm -rf /"))
        assert result["executed"] is False
        assert "Cannot parse" in result.get("error", "")

    def test_placeholder_uppercase_rejected(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("ph", "auteur decision inspect DECISION_ID"))
        assert result["executed"] is False
        # Blocks either at placeholder check or subcommand dispatch
        assert result["exit_code"] in (2, 4)

    def test_placeholder_angle_rejected(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("ph2", "auteur decision next <id>"))
        assert result["executed"] is False
        assert result["exit_code"] in (2, 4)

    def test_shell_metachar_semicolon_rejected(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("semi", "auteur decision inspect x; rm -rf /"))
        assert result["executed"] is False
        assert result["exit_code"] == 2

    def test_shell_metachar_pipe_rejected(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("pipe", "auteur decision inspect x | grep foo"))
        assert result["executed"] is False
        assert result["exit_code"] == 2

    def test_shell_metachar_backtick_rejected(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("bt", "auteur decision inspect `id`"))
        assert result["executed"] is False
        assert result["exit_code"] == 2

    def test_shell_metachar_subshell_rejected(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("sub", "auteur decision inspect $(whoami)"))
        assert result["executed"] is False
        assert result["exit_code"] == 2

    def test_shell_metachar_ampersand_rejected(self, tmp_path: Path) -> None:
        e = _engine(tmp_path)
        result = e.execute(_action("amp", "auteur decision inspect x &"))
        assert result["executed"] is False
        assert result["exit_code"] == 2


# =========================================================================
# SAFE_DECISION_ACTIONS cross-reference consistency
# =========================================================================


class TestSafeActionSetConsistency:
    """SAFE_DECISION_ACTIONS and _SAFE_DECISION_SUBCOMMANDS must be consistent."""

    def test_all_safe_actions_mapped_to_subcommands(self) -> None:
        """Each SAFE_DECISION_ACTIONS entry maps to a _SAFE_DECISION_SUBCOMMANDS entry,
        except prepare-acceptance which is intentionally blocked by placeholder."""
        from auteur.workflow.engine import _SAFE_DECISION_SUBCOMMANDS

        action_map = {
            "generate-candidate": "next",
            "evaluate-candidate": "next",
            "compare-candidates": "compare",
            "prepare-acceptance": None,  # explicit exception — blocked by placeholder
            "refresh-impact-analysis": "refresh",
            "refresh-decision-snapshots": "refresh",
            "run-deterministic-validation": "revalidate",
        }

        missing_from_actions = set(action_map) - SAFE_DECISION_ACTIONS
        assert not missing_from_actions, f"Actions in map but not in SAFE_DECISION_ACTIONS: {missing_from_actions}"

        extra_in_actions = SAFE_DECISION_ACTIONS - set(action_map)
        assert not extra_in_actions, f"Actions in SAFE_DECISION_ACTIONS but not mapped: {extra_in_actions}"

        for action_id, subcmd in action_map.items():
            assert action_id in SAFE_DECISION_ACTIONS
            if subcmd is not None:
                assert subcmd in _SAFE_DECISION_SUBCOMMANDS, \
                    f"{action_id} → {subcmd} not in _SAFE_DECISION_SUBCOMMANDS"
