"""End-to-end tests for convergence workflow CLI and integration."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

from auteur.convergence.cli import (
    dispatch_realization,
    handle_realization_status,
    handle_realization_revise,
    handle_realization_generate_candidate,
    handle_realization_register_candidate,
    handle_realization_compare,
    handle_realization_reconcile,
)
from auteur.convergence.models import GenerationStrategy
from auteur.convergence.persistence import ConvergenceStore


# =============================================================================
# End-to-end scenario tests
# =============================================================================


def _make_args(**kwargs):
    """Create a simple argparse namespace."""
    class Args:
        pass
    a = Args()
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


@pytest.fixture
def scenario_project(tmp_path: Path) -> Path:
    """Create a project with a changed scene outline needing repair."""
    (tmp_path / ".auteur").mkdir()
    (tmp_path / "story_identity.yaml").write_text(yaml.safe_dump({
        "story_type": {"genre": "mystery", "mode": "dramatic", "medium": "novel"},
    }))
    (tmp_path / "blueprint.yaml").write_text(yaml.safe_dump({
        "chapters": {
            "chapter_03": {"purpose": "Climax and reveal"},
        },
    }))
    (tmp_path / "chapters").mkdir()
    ch3 = tmp_path / "chapters" / "3"
    ch3.mkdir(parents=True)
    (ch3 / "outline.yaml").write_text(yaml.safe_dump({
        "scenes": [
            {"id": "scene_03_04", "purpose": "Archive discovery"},
        ],
    }))
    (ch3 / "scenes").mkdir()
    (ch3 / "scenes" / "scene_03_04.yaml").write_text(yaml.safe_dump({
        "id": "scene_03_04",
        "purpose": "Elena discovers archive tampering",
        "location": "archive room",
        "opening": "Dust motes hung in the dim light",
        "beats": [
            {"id": "B01", "description": "Elena enters archive"},
            {"id": "B02", "description": "Elena finds damaged records"},
            {"id": "B03", "description": "Elena decides to conceal her discovery"},
        ],
    }))
    return tmp_path


class TestScenario:
    """Dogfood: changed scene outline requiring minimal repair."""

    def test_scenario_changed_outline_minimal_repair(self, scenario_project):
        """1. Changed scene outline requiring minimal repair."""
        # Use the same target across all operations
        from auteur.convergence.scope import resolve_target
        from auteur.convergence.candidates import CandidateStore
        from auteur.convergence.obligations import collect_obligations
        from auteur.convergence.preservation import analyze_preservation
        from auteur.convergence.comparison import compare_candidates
        from auteur.convergence.planner import ProposalStore

        target = resolve_target(scenario_project, chapter_index=3, scene_id="scene_03_04")
        store = ConvergenceStore(scenario_project)
        store.save_target(target)
        store.update_latest("target", target.target_id)

        # Generate candidates using the same target
        cstore = CandidateStore(scenario_project)
        obligations = collect_obligations(scenario_project, target)
        preserved = analyze_preservation(scenario_project, target)

        c1 = cstore.generate_candidate(
            target=target,
            strategy=GenerationStrategy.MINIMAL_REPAIR,
            obligations=[o.obligation_id for o in obligations],
            preserved_regions=preserved,
        )
        c2 = cstore.generate_candidate(
            target=target,
            strategy=GenerationStrategy.STRUCTURAL_ALTERNATIVE,
            obligations=[o.obligation_id for o in obligations],
            preserved_regions=preserved,
        )

        # Compare
        comparison = compare_candidates(target, [c1, c2])
        pstore = ProposalStore(scenario_project)
        pstore.save_comparison(comparison)
        assert comparison.target_id == target.target_id
        assert len(comparison.candidate_ids) == 2

        # Reconcile
        proposal = pstore.create_proposal(target, [c1, c2], comparison, obligations)
        assert proposal.target_id == target.target_id
        assert not proposal.canonical

    def test_scenario_external_candidate_registration(self, scenario_project):
        """6. External human-authored candidate registration."""
        args = _make_args(
            project=scenario_project,
            chapter=3,
            scene="scene_03_04",
            json=False,
            realization_command="revise",
        )
        handle_realization_revise(args)

        external_content = scenario_project / "external_revision.yaml"
        external_content.write_text(yaml.safe_dump({
            "revision": "Elena carefully examines the archive records...",
        }))

        args2 = _make_args(
            project=scenario_project,
            chapter=3,
            scene="scene_03_04",
            file=external_content,
            json=False,
            realization_command="register-candidate",
        )
        rc = handle_realization_register_candidate(args2)
        assert rc == 0

        # Candidate should be inspectable via status
        args3 = _make_args(
            project=scenario_project,
            chapter=3,
            scene="scene_03_04",
            json=False,
            realization_command="status",
        )
        rc = handle_realization_status(args3)
        assert rc == 0

    def test_scenario_preserved_opening_beats(self, scenario_project):
        """3. Existing accepted scene with preserved opening beats."""
        from auteur.convergence.preservation import analyze_preservation
        from auteur.convergence.scope import resolve_target

        target = resolve_target(scenario_project, chapter_index=3, scene_id="scene_03_04")
        regions = analyze_preservation(scenario_project, target)
        beat_regions = [r for r in regions if r.beat_id]
        # At least one beat should be PRESERVE or PRESERVE_WITH_REVIEW
        assert any(r.status.value in ("preserve", "preserve_with_review") for r in beat_regions)


    def test_scenario_missing_scene_boundary(self, tmp_path):
        """11. Missing stable scene boundary."""
        (tmp_path / ".auteur").mkdir()
        (tmp_path / "story_identity.yaml").write_text(yaml.safe_dump({
            "story_type": {"genre": "mystery", "mode": "dramatic"},
        }))
        (tmp_path / "chapters").mkdir()
        ch5 = tmp_path / "chapters" / "5"
        ch5.mkdir(parents=True)

        args = _make_args(
            project=tmp_path,
            chapter=5,
            scene=None,
            json=True,
            realization_command="status",
        )
        rc = handle_realization_status(args)
        assert rc == 0  # Should handle gracefully

    def test_scenario_no_affected_target(self, tmp_path):
        """No affected target should show clean status."""
        (tmp_path / ".auteur").mkdir()
        (tmp_path / "story_identity.yaml").write_text("test: true")
        (tmp_path / "blueprint.yaml").write_text("test: true")

        args = _make_args(
            project=tmp_path,
            chapter=1,
            scene=None,
            json=False,
            realization_command="status",
        )
        rc = handle_realization_status(args)
        assert rc == 0

    def test_scenario_json_output(self, scenario_project):
        """JSON output is valid."""
        args = _make_args(
            project=scenario_project,
            chapter=3,
            scene="scene_03_04",
            json=True,
            realization_command="revise",
        )
        rc = handle_realization_revise(args)
        assert rc == 0

    def test_scenario_missing_project(self):
        """Missing project fails cleanly."""
        args = _make_args(
            project=Path("/nonexistent/path"),
            chapter=1,
            scene=None,
            json=False,
            realization_command="status",
        )
        rc = handle_realization_status(args)
        assert rc == 1

    def test_scenario_stale_candidate_visible(self, scenario_project):
        """Stale candidates are visible."""
        from auteur.convergence.candidates import CandidateStore
        from auteur.convergence.scope import resolve_target
        from auteur.convergence.models import CandidateStatus

        target = resolve_target(scenario_project, chapter_index=3, scene_id="scene_03_04")
        store = ConvergenceStore(scenario_project)
        store.save_target(target)
        candidate_store = CandidateStore(scenario_project)
        c = candidate_store.generate_candidate(
            target=target,
            strategy=GenerationStrategy.MINIMAL_REPAIR,
            obligations=[],
            preserved_regions=[],
        )
        candidate_store.mark_stale(c.candidate_id)
        restored = candidate_store.get_candidate(c.candidate_id)
        assert restored is not None
        assert restored.status == CandidateStatus.STALE
