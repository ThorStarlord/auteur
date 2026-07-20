"""Tests for WorkflowEngine — composition and safe execution boundary."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.workflow.engine import WorkflowEngine
from auteur.workflow.models import (
    AuthorityLevel,
    WorkflowAction,
    WorkflowStage,
)


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def empty_project(tmp_path: Path) -> Path:
    root = tmp_path / "empty"
    return root


@pytest.fixture
def basic_project(tmp_path: Path) -> Path:
    root = tmp_path / "basic"
    _write_yaml(root / "story_identity.yaml", {"title": "Test"})
    _write_yaml(root / "blueprint.yaml", {
        "project_identity": {"title": "Test", "genre": "fantasy"},
        "chapters": [],
    })
    return root


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWorkflowEngine:
    def test_analyze_empty(self, empty_project: Path) -> None:
        engine = WorkflowEngine(empty_project)
        state = engine.analyze()
        assert state.current_stage == WorkflowStage.IDENTITY
        assert len(state.blockers) >= 1
        assert "Blocked" in state.status_summary or "Current stage" in state.status_summary

    def test_analyze_basic(self, basic_project: Path) -> None:
        engine = WorkflowEngine(basic_project)
        state = engine.analyze()
        assert state.current_stage is not None
        assert len(state.stages) == 9

    def test_stages_all_present(self, basic_project: Path) -> None:
        engine = WorkflowEngine(basic_project)
        state = engine.analyze()
        stage_names = {s.stage.value for s in state.stages}
        expected = {"identity", "structure", "realization", "drafting",
                     "reasoning", "reconciliation", "acceptance", "assembly",
                     "publishing"}
        assert stage_names == expected

    def test_can_execute(self) -> None:
        engine = WorkflowEngine(".")
        read_only = WorkflowAction(
            label="Test", command="echo test",
            authority=AuthorityLevel.READ_ONLY,
        )
        authority = WorkflowAction(
            label="Test", command="echo test",
            authority=AuthorityLevel.AUTHORITY_BEARING,
        )
        assert engine.can_execute(read_only)
        assert not engine.can_execute(authority)

    def test_filter_safe_actions(self) -> None:
        engine = WorkflowEngine(".")
        actions = [
            WorkflowAction(label="A", command="", authority=AuthorityLevel.READ_ONLY),
            WorkflowAction(label="B", command="", authority=AuthorityLevel.DERIVED_ARTIFACT),
            WorkflowAction(label="C", command="", authority=AuthorityLevel.CANDIDATE_GENERATION),
            WorkflowAction(label="D", command="", authority=AuthorityLevel.AUTHORITY_BEARING),
        ]
        safe = engine.filter_safe_actions(actions)
        assert len(safe) == 3
        labels = {a.label for a in safe}
        assert "A" in labels and "B" in labels and "C" in labels
        assert "D" not in labels

    def test_build_summary_empty(self, empty_project: Path) -> None:
        engine = WorkflowEngine(empty_project)
        state = engine.analyze()
        assert "identity" in state.status_summary.lower() or "blocked" in state.status_summary.lower()


class TestExecuteSafety:
    """Subprocess execution safety tests."""

    def test_recursion_prevention_workflow_action(self) -> None:
        """Workflow subcommands are blocked to prevent recursion."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="auteur workflow status .",
            authority=AuthorityLevel.READ_ONLY,
        )
        result = engine.execute(action)
        assert not result["executed"]
        assert "not eligible for automatic dispatch" in result["error"]

    def test_recursion_prevention_workflow_nested(self) -> None:
        """Nested workflow subcommand is also blocked."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="auteur workflow next . --execute",
            authority=AuthorityLevel.READ_ONLY,
        )
        result = engine.execute(action)
        assert not result["executed"]
        assert "not eligible" in result["error"].lower()

    def test_shell_metacharacters_rejected_semicolon(self) -> None:
        """Semicolons in args are rejected."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="auteur structure diagnose blueprint.yaml; rm -rf /",
            authority=AuthorityLevel.READ_ONLY,
        )
        result = engine.execute(action)
        assert not result["executed"]
        assert "shell metacharacter" in result["error"].lower()

    def test_shell_metacharacters_rejected_pipe(self) -> None:
        """Pipe characters in args are rejected."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="auteur structure diagnose blueprint.yaml | other",
            authority=AuthorityLevel.READ_ONLY,
        )
        result = engine.execute(action)
        assert not result["executed"]
        assert "shell metacharacter" in result["error"].lower()

    def test_placeholder_uppercase_rejected(self) -> None:
        """UPPERCASE arguments are rejected as placeholders."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="auteur reasoning review PATH_TO_REVIEW",
            authority=AuthorityLevel.READ_ONLY,
        )
        result = engine.execute(action)
        assert not result["executed"]
        assert "placeholder" in result["error"].lower()

    def test_placeholder_angle_bracket_rejected(self) -> None:
        """<angle bracket> arguments are rejected as placeholders."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="auteur expression inspect-book-manuscript <manuscript_path>",
            authority=AuthorityLevel.READ_ONLY,
        )
        result = engine.execute(action)
        assert not result["executed"]
        assert "placeholder" in result["error"].lower()

    def test_authority_bearing_rejected(self) -> None:
        """AUTHORITY_BEARING actions are rejected by execute()."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="auteur structure diagnose blueprint.yaml",
            authority=AuthorityLevel.AUTHORITY_BEARING,
        )
        result = engine.execute(action)
        assert not result["executed"]
        assert "requires author decision" in result["error"]

    def test_canonical_mutation_rejected(self) -> None:
        """CANONICAL_MUTATION actions are rejected by execute()."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="auteur accept . 1",
            authority=AuthorityLevel.CANONICAL_MUTATION,
        )
        result = engine.execute(action)
        assert not result["executed"]
        assert "requires author decision" in result["error"]

    def test_proposal_generation_not_executable(self) -> None:
        """PROPOSAL_GENERATION is excluded from autonomous execution in v0.4.0."""
        from auteur.workflow.models import EXECUTABLE_AUTHORITIES
        assert AuthorityLevel.PROPOSAL_GENERATION not in EXECUTABLE_AUTHORITIES

    def test_not_auteur_command_rejected(self) -> None:
        """Commands not starting with 'auteur' are rejected."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="rm -rf /",
            authority=AuthorityLevel.READ_ONLY,
        )
        result = engine.execute(action)
        assert not result["executed"]
        assert "Cannot parse command" in result["error"]

    def test_empty_args_rejected(self) -> None:
        """Empty tokens in command are rejected."""
        engine = WorkflowEngine(".")
        action = WorkflowAction(
            label="Test",
            command="auteur   ",
            authority=AuthorityLevel.READ_ONLY,
        )
        result = engine.execute(action)
        assert not result["executed"]


class TestValidateArgSafety:
    """Tests for the argument validation helper."""

    def test_valid_args_pass(self) -> None:
        from auteur.workflow.engine import _validate_arg_safety
        assert _validate_arg_safety(["structure", "diagnose", "blueprint.yaml"]) is None
        assert _validate_arg_safety(["draft", ".", "1"]) is None
        assert _validate_arg_safety(["cartographer", "compile", "--project", "."]) is None
        assert _validate_arg_safety(["publishing", "release", "--format", "epub"]) is None

    def test_semicolon_rejected(self) -> None:
        from auteur.workflow.engine import _validate_arg_safety
        err = _validate_arg_safety(["structure", "diagnose", "blueprint.yaml; rm"])
        assert err is not None
        assert "shell metacharacter" in err

    def test_pipe_rejected(self) -> None:
        from auteur.workflow.engine import _validate_arg_safety
        err = _validate_arg_safety(["diagnose", "file|other"])
        assert err is not None
        assert "shell metacharacter" in err

    def test_backtick_rejected(self) -> None:
        from auteur.workflow.engine import _validate_arg_safety
        err = _validate_arg_safety(["diagnose", "`malicious`"])
        assert err is not None
        assert "shell metacharacter" in err

    def test_dollar_brace_rejected(self) -> None:
        from auteur.workflow.engine import _validate_arg_safety
        err = _validate_arg_safety(["diagnose", "${PATH}"])
        assert err is not None
        assert "shell metacharacter" in err

    def test_relative_paths_allowed(self) -> None:
        from auteur.workflow.engine import _validate_arg_safety
        assert _validate_arg_safety(["structure", "diagnose", "../blueprint.yaml"]) is None
        assert _validate_arg_safety(["draft", "..", "1"]) is None


class TestHasPlaceholders:
    """Tests for the placeholder detection helper."""

    def test_no_placeholders(self) -> None:
        from auteur.workflow.engine import _has_placeholders
        assert _has_placeholders(["structure", "diagnose", "blueprint.yaml"]) == []

    def test_uppercase_placeholder(self) -> None:
        from auteur.workflow.engine import _has_placeholders
        result = _has_placeholders(["reasoning", "review", "PATH_TO_REVIEW"])
        assert len(result) == 1
        assert "PATH_TO_REVIEW" in result

    def test_angle_placeholder(self) -> None:
        from auteur.workflow.engine import _has_placeholders
        result = _has_placeholders(["review", "<review_id>"])
        assert len(result) == 1
        assert "<review_id>" in result

    def test_mixed_placeholders(self) -> None:
        from auteur.workflow.engine import _has_placeholders
        result = _has_placeholders(["complete", "ACCEPTANCE_ID", "--project", "."])
        assert len(result) == 1
        assert "ACCEPTANCE_ID" in result
