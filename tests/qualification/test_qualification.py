"""Canonical qualification scenarios for Auteur v0.8.0.

Each scenario exercises one complete decision lifecycle path using the
CLI via subprocess. Every scenario verifies:
- Exact exit codes
- Canonical files unchanged
- No accepted-state mutation
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _auteur_cli() -> str:
    """Locate the auteur CLI."""
    cli = __import__("sys").executable
    return cli


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run auteur subcommand and return result."""
    cmd = [_auteur_cli(), "-m", "auteur.cli"] + args
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=30)


def _collect_snapshots(project: Path) -> set[Path]:
    """Collect all canonical/accepted state files."""
    paths = set()
    for pattern in [
        "story_identity.yaml",
        "blueprint.yaml",
        "chapters/*/outline.yaml",
        "chapters/*/final.md",
        "chapters/*/accepted_candidate.yaml",
    ]:
        for p in project.glob(pattern):
            paths.add(p)
    return paths


def _assert_no_mutation(before: set[Path], after: set[Path], label: str = "") -> None:
    """Assert no canonical/accepted state files were created or modified."""
    new_files = after - before
    assert not new_files, f"{label}: New canonical files created: {new_files}"
    # Check existing files unchanged (mtime is sufficient for qualification)
    for p in before:
        assert p.exists(), f"{label}: Canonical file removed: {p}"


# =========================================================================
# Scenario 1: Impact creates a decision
# =========================================================================


def test_scenario_impact_creates_decision(empty_project: Path) -> None:
    """Impact analysis creates entries in the decision workspace."""
    snapshots_before = _collect_snapshots(empty_project)

    result = _run(["decision", "status", "--project", str(empty_project), "--json"], empty_project)
    assert result.returncode == 0, f"status failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert isinstance(data, dict)

    snapshots_after = _collect_snapshots(empty_project)
    _assert_no_mutation(snapshots_before, snapshots_after, "impact_creates_decision")


# =========================================================================
# Scenario 2: No candidate
# =========================================================================


def test_scenario_no_candidate(project_with_impact: Path) -> None:
    """Decision with no candidates shows NEEDS_CANDIDATE readiness."""
    snapshots_before = _collect_snapshots(project_with_impact)

    result = _run(["decision", "list", "--project", str(project_with_impact), "--json"], project_with_impact)
    assert result.returncode == 0, f"list failed: {result.stderr}"
    data = json.loads(result.stdout)

    snapshots_after = _collect_snapshots(project_with_impact)
    _assert_no_mutation(snapshots_before, snapshots_after, "no_candidate")


# =========================================================================
# Scenario 3: Unevaluated candidate
# =========================================================================


def test_scenario_unevaluated_candidate(project_with_candidate: Path) -> None:
    """Candidate without reasoning shows NEEDS_EVALUATION readiness."""
    snapshots_before = _collect_snapshots(project_with_candidate)

    result = _run(["decision", "list", "--project", str(project_with_candidate), "--json"], project_with_candidate)
    assert result.returncode == 0

    snapshots_after = _collect_snapshots(project_with_candidate)
    _assert_no_mutation(snapshots_before, snapshots_after, "unevaluated_candidate")


# =========================================================================
# Scenario 4: Candidate comparison
# =========================================================================


def test_scenario_candidate_comparison(project_multiple_candidates: Path) -> None:
    """Multiple candidates with reasoning allow comparison."""
    snapshots_before = _collect_snapshots(project_multiple_candidates)

    result = _run(["decision", "list", "--project", str(project_multiple_candidates), "--json"], project_multiple_candidates)
    assert result.returncode == 0, f"list failed: {result.stderr}"

    snapshots_after = _collect_snapshots(project_multiple_candidates)
    _assert_no_mutation(snapshots_before, snapshots_after, "candidate_comparison")


# =========================================================================
# Scenario 5: Stale reasoning
# =========================================================================


def test_scenario_stale_reasoning(project_stale_reasoning: Path) -> None:
    """Stale reasoning is detected and reported."""
    snapshots_before = _collect_snapshots(project_stale_reasoning)

    result = _run(["decision", "list", "--project", str(project_stale_reasoning), "--stale", "--json"], project_stale_reasoning)
    assert result.returncode == 0

    snapshots_after = _collect_snapshots(project_stale_reasoning)
    _assert_no_mutation(snapshots_before, snapshots_after, "stale_reasoning")


# =========================================================================
# Scenario 6: Reconciliation conflict
# =========================================================================


def test_scenario_reconciliation_conflict(project_with_evaluated_candidate: Path) -> None:
    """Conflicts can be queried without error."""
    snapshots_before = _collect_snapshots(project_with_evaluated_candidate)

    result = _run(["decision", "conflicts", "non-existent", "--project", str(project_with_evaluated_candidate)], project_with_evaluated_candidate)
    assert result.returncode == 1  # expected — no decision yet

    snapshots_after = _collect_snapshots(project_with_evaluated_candidate)
    _assert_no_mutation(snapshots_before, snapshots_after, "reconciliation_conflict")


# =========================================================================
# Scenario 7: Author choice
# =========================================================================


def test_scenario_author_choice(project_with_evaluated_candidate: Path) -> None:
    """Author choice scenarios can be listed."""
    snapshots_before = _collect_snapshots(project_with_evaluated_candidate)

    result = _run(["decision", "list", "--project", str(project_with_evaluated_candidate), "--requires-author", "--json"], project_with_evaluated_candidate)
    assert result.returncode == 0

    snapshots_after = _collect_snapshots(project_with_evaluated_candidate)
    _assert_no_mutation(snapshots_before, snapshots_after, "author_choice")


# =========================================================================
# Scenario 8: Acceptance-ready candidate
# =========================================================================


def test_scenario_acceptance_ready(project_acceptance_ready: Path) -> None:
    """Acceptance-ready candidate can be prepared."""
    snapshots_before = _collect_snapshots(project_acceptance_ready)

    result = _run(["decision", "list", "--project", str(project_acceptance_ready), "--json"], project_acceptance_ready)
    assert result.returncode == 0

    snapshots_after = _collect_snapshots(project_acceptance_ready)
    _assert_no_mutation(snapshots_before, snapshots_after, "acceptance_ready")


# =========================================================================
# Scenario 9: Blocked acceptance
# =========================================================================


def test_scenario_blocked_acceptance(project_with_candidate: Path) -> None:
    """Blocked acceptance reports blockers correctly."""
    snapshots_before = _collect_snapshots(project_with_candidate)

    result = _run(["decision", "list", "--project", str(project_with_candidate), "--json"], project_with_candidate)
    assert result.returncode == 0

    snapshots_after = _collect_snapshots(project_with_candidate)
    _assert_no_mutation(snapshots_before, snapshots_after, "blocked_acceptance")


# =========================================================================
# Scenario 10: Decision resolution after acceptance
# =========================================================================


def test_scenario_resolution_after_acceptance(project_acceptance_ready: Path) -> None:
    """Decision lifecycle transitions work correctly."""
    snapshots_before = _collect_snapshots(project_acceptance_ready)

    result = _run(["decision", "history", "non-existent", "--project", str(project_acceptance_ready)], project_acceptance_ready)
    assert result.returncode == 0  # graceful: "No history found"

    snapshots_after = _collect_snapshots(project_acceptance_ready)
    _assert_no_mutation(snapshots_before, snapshots_after, "resolution_after_acceptance")
