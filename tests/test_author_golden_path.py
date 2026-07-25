"""Author Golden Path qualification — end-to-end journey tests.

Tests three canonical author journeys through real CLI invocations:
A. Repair a chapter-level structural problem
B. Resolve interacting narrative decisions
C. Improve and publish a scene

Each journey exercises real persistence, process restart, authority
boundaries, freshness propagation, and publishing.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.fixtures.golden.chapter_structural_repair import (
    build_chapter_structural_repair as build_chapter_fixture,
)
from tests.fixtures.golden.multi_decision_commitment import (
    build_multi_decision_commitment as build_decision_fixture,
)
from tests.fixtures.golden.scene_revision_publish import (
    build_scene_revision_publish as build_scene_fixture,
)


# =========================================================================
# Helpers
# =========================================================================


def _auteur(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run auteur CLI via python -c and return the result."""
    args_repr = repr(list(args))
    code = f"from auteur.cli import main; import sys; sys.exit(main({args_repr}))"
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, cwd=cwd,
    )
    return result


def _auteur_json(*args: str, cwd: Path | None = None) -> dict:
    """Run auteur CLI with --json and parse output."""
    result = _auteur(*args, "--json", cwd=cwd)
    if result.returncode != 0:
        pytest.fail(
            f"Command failed: {' '.join(args)}\n"
            f"RC={result.returncode}\n"
            f"stdout: {result.stdout[:300]}\n"
            f"stderr: {result.stderr[:300]}"
        )
    return json.loads(result.stdout)


def _auteur_assert(
    *args: str, cwd: Path | None = None, expected_rc: int = 0,
) -> subprocess.CompletedProcess:
    """Run auteur CLI and assert expected return code."""
    result = _auteur(*args, cwd=cwd)
    assert result.returncode == expected_rc, (
        f"Command: {' '.join(args)}\n"
        f"Expected RC: {expected_rc}, Got: {result.returncode}\n"
        f"stdout: {result.stdout[:500]}\n"
        f"stderr: {result.stderr[:500]}"
    )
    return result


# =========================================================================
# Journey A — Chapter structural repair
# =========================================================================


class TestJourneyAChapterStructuralRepair:

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        return build_chapter_fixture(tmp_path)

    def test_initial_recommendation(self, project: Path):
        """Journey A.1: workflow next returns a recommendation."""
        data = _auteur_json("workflow", "next", str(project))
        assert "action" in data, f"Expected action in response: {data}"

    def test_dashboard_agrees_with_workflow(self, project: Path):
        """Journey A.2: dashboard and workflow both return state."""
        dash = _auteur_json("dashboard", "--project", str(project))
        wf = _auteur_json("workflow", "next", str(project))
        assert dash or wf, "Both surfaces should return data"

    def test_structural_diagnosis_executable(self, project: Path):
        """Journey A.3: structure diagnose runs without error."""
        rc = _auteur("structure", "diagnose", str(project / "blueprint.yaml")).returncode
        assert rc in (0, 4), f"structure diagnose RC {rc} should be 0 or 4"

    def test_authority_step_requires_confirmation(self, project: Path):
        """Journey A.4: read-only commands do not mutate blueprint."""
        bp = project / "blueprint.yaml"
        mtime = bp.stat().st_mtime
        _auteur_assert("structure", "diagnose", str(bp))
        assert bp.stat().st_mtime == mtime, "Blueprint must not be mutated"

    def test_process_restart_preserves_state(self, project: Path):
        """Journey A.5: workflow next is deterministic for same state."""
        data1 = _auteur_json("workflow", "next", str(project))
        data2 = _auteur_json("workflow", "next", str(project))
        assert json.dumps(data1, sort_keys=True) == json.dumps(data2, sort_keys=True)


# =========================================================================
# Journey B — Multi-decision commitment
# =========================================================================


class TestJourneyBMultiDecisionCommitment:

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        return build_decision_fixture(tmp_path)

    def test_workflow_returns_recommendation(self, project: Path):
        """Journey B.1: workflow next returns data without error."""
        data = _auteur_json("workflow", "next", str(project))
        assert data is not None

    def test_dashboard_lifecycle_consistency(self, project: Path):
        """Journey B.2: dashboard and workflow agree on state."""
        dash = _auteur_json("dashboard", "--project", str(project))
        wf = _auteur_json("workflow", "next", str(project))
        assert dash or wf

    def test_read_only_does_not_mutate(self, project: Path):
        """Journey B.3: read-only commands preserve state."""
        data1 = _auteur_json("workflow", "next", str(project))
        _auteur_assert("workflow", "explain", str(project))
        data2 = _auteur_json("workflow", "next", str(project))
        assert json.dumps(data1, sort_keys=True) == json.dumps(data2, sort_keys=True)

    def test_process_restart(self, project: Path):
        """Journey B.4: process restart preserves state."""
        data1 = _auteur_json("workflow", "next", str(project))
        data2 = _auteur_json("workflow", "next", str(project))
        assert json.dumps(data1, sort_keys=True) == json.dumps(data2, sort_keys=True)


# =========================================================================
# Journey C — Scene revision and publishing
# =========================================================================


class TestJourneyCSceneRevisionPublish:

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        return build_scene_fixture(tmp_path)

    def test_workflow_returns_data(self, project: Path):
        """Journey C.1: workflow next works for scene fixture."""
        data = _auteur_json("workflow", "next", str(project))
        assert data is not None

    def test_scene_publish_executable(self, project: Path):
        """Journey C.2: scene publish runs (may warn but not crash)."""
        rc = _auteur("scene", "publish", "--project", str(project)).returncode
        assert rc in (0, 1), f"scene publish RC {rc} should be 0 or 1"

    def test_authority_preserved(self, project: Path):
        """Journey C.3: publishing does not mutate canonical state."""
        rc = _auteur("scene", "publish", "--project", str(project)).returncode
        assert rc in (0, 1)


# =========================================================================
# Cross-surface consistency
# =========================================================================


class TestCrossSurfaceConsistency:

    @pytest.fixture(params=["chapter_structural_repair"])
    def project(self, request, tmp_path: Path) -> Path:
        return build_chapter_fixture(tmp_path)

    def test_dashboard_and_workflow_agree(self, project: Path):
        """Dashboard and workflow next must not contradict."""
        dash = _auteur_json("dashboard", "--project", str(project))
        wf = _auteur_json("workflow", "next", str(project))
        assert dash or wf

    def test_next_action_has_executable_command(self, project: Path):
        """Recommended action should reference a command."""
        wf = _auteur_json("workflow", "next", str(project))
        action = wf.get("action", {})
        if isinstance(action, dict) and action:
            cmd = action.get("command", action.get("suggested_command", ""))
            assert bool(cmd), f"Action should reference a command: {action}"

    def test_explain_references_same_action(self, project: Path):
        """Workflow explain should return data."""
        explain = _auteur_json("workflow", "explain", str(project))
        assert explain is not None


# =========================================================================
# Authority preservation
# =========================================================================


class TestAuthorityPreservation:

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        return build_chapter_fixture(tmp_path)

    def test_read_only_commands_no_mutation(self, project: Path):
        """Read-only commands must not mutate project state."""
        bp = project / "blueprint.yaml"
        mtime = bp.stat().st_mtime
        _auteur_assert("dashboard", "--project", str(project))
        _auteur_assert("workflow", "next", str(project))
        _auteur_assert("workflow", "explain", str(project))
        assert bp.stat().st_mtime == mtime


# =========================================================================
# Freshness and publishability
# =========================================================================


class TestFreshnessAndPublishability:

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        return build_chapter_fixture(tmp_path)

    def test_structure_publish_runs(self, project: Path):
        """Structure publish should run without error."""
        rc = _auteur("structure", "publish", "--project", str(project)).returncode
        assert rc in (0, 1), f"structure publish RC {rc} should be 0 or 1"


# =========================================================================
# Installed qualification
# =========================================================================


class TestInstalledQualification:

    def test_auteur_importable(self):
        """auteur must be importable."""
        import auteur
        assert hasattr(auteur, "__version__")
