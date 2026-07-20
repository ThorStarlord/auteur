"""Tests for workflow rules — stage detection, blockers, recommendations."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.workflow.models import (
    BlockerCategory,
    BlockerSeverity,
    WorkflowStage,
)
from auteur.workflow.rules import (
    collect_blockers,
    current_stage,
    detect_stages,
    recommend_actions,
)


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _write_text(path: Path, content: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def empty_project(tmp_path: Path) -> Path:
    return tmp_path / "empty"


@pytest.fixture
def identity_project(tmp_path: Path) -> Path:
    root = tmp_path / "identity_only"
    _write_yaml(root / "story_identity.yaml", {"title": "Test"})
    return root


@pytest.fixture
def blueprint_project(tmp_path: Path) -> Path:
    root = tmp_path / "blueprint_only"
    _write_yaml(root / "story_identity.yaml", {"title": "Test"})
    _write_yaml(root / "blueprint.yaml", {
        "project_identity": {"title": "Test", "genre": "fantasy"},
        "chapters": [],
    })
    return root


@pytest.fixture
def outline_project(tmp_path: Path) -> Path:
    root = tmp_path / "with_outlines"
    _write_yaml(root / "story_identity.yaml", {"title": "Test"})
    _write_yaml(root / "blueprint.yaml", {
        "project_identity": {"title": "Test", "genre": "fantasy"},
        "chapters": [{"index": 1, "title": "Ch1"}],
    })
    _write_yaml(root / "chapters" / "1" / "outline.yaml", {"chapter_index": 1})
    return root


@pytest.fixture
def drafting_project(tmp_path: Path) -> Path:
    root = tmp_path / "drafting"
    _write_yaml(root / "story_identity.yaml", {"title": "Test"})
    _write_yaml(root / "blueprint.yaml", {
        "project_identity": {"title": "Test", "genre": "fantasy"},
        "chapters": [{"index": 1, "title": "Ch1"}],
    })
    _write_yaml(root / "chapters" / "1" / "outline.yaml", {"chapter_index": 1})
    _write_text(root / "chapters" / "1" / "draft_v1.md", "# Chapter 1")
    return root


@pytest.fixture
def accepted_project(tmp_path: Path) -> Path:
    root = tmp_path / "accepted"
    _write_yaml(root / "story_identity.yaml", {"title": "Test"})
    _write_yaml(root / "blueprint.yaml", {
        "project_identity": {"title": "Test", "genre": "fantasy"},
        "chapters": [{"index": 1, "title": "Ch1"}],
    })
    _write_yaml(root / "chapters" / "1" / "outline.yaml", {"chapter_index": 1})
    _write_text(root / "chapters" / "1" / "draft_v1.md", "# Chapter 1")
    _write_yaml(root / "chapters" / "1" / "expression" / "accepted.yaml", {
        "revision": 1, "source_chapter": {"artifact_id": "chapter_01"},
    })
    return root


@pytest.fixture
def reconciled_project(tmp_path: Path) -> Path:
    root = tmp_path / "reconciled"
    _write_yaml(root / "story_identity.yaml", {"title": "Test"})
    _write_yaml(root / "blueprint.yaml", {
        "project_identity": {"title": "Test", "genre": "fantasy"},
        "chapters": [{"index": 1, "title": "Ch1"}],
    })
    _write_yaml(root / "chapters" / "1" / "outline.yaml", {"chapter_index": 1})
    _write_text(root / "chapters" / "1" / "draft_v1.md", "# Chapter 1")
    _write_yaml(root / "chapters" / "1" / "expression" / "accepted.yaml", {
        "revision": 1, "source_chapter": {"artifact_id": "chapter_01"},
    })
    _write_yaml(
        root / ".auteur" / "book" / "expression" / "reconciliation"
        / "completions" / "completion_001.yaml",
        {"completion_status": "completed"},
    )
    _write_yaml(root / "book" / "expression" / "accepted.yaml", {"revision": 1})
    return root


# ---------------------------------------------------------------------------
# Tests: detect_stages
# ---------------------------------------------------------------------------


class TestDetectStages:
    def test_empty_project(self, empty_project: Path) -> None:
        stages = detect_stages(empty_project)
        assert len(stages) == 9
        assert stages[0].stage == WorkflowStage.IDENTITY
        assert not stages[0].is_complete

    def test_identity_present(self, identity_project: Path) -> None:
        stages = detect_stages(identity_project)
        assert stages[0].is_complete
        assert not stages[1].is_complete  # blueprint missing

    def test_blueprint_present(self, blueprint_project: Path) -> None:
        stages = detect_stages(blueprint_project)
        assert stages[0].is_complete
        assert stages[1].is_complete

    def test_outlines_present(self, outline_project: Path) -> None:
        stages = detect_stages(outline_project)
        assert stages[0].is_complete
        assert stages[1].is_complete
        assert stages[2].is_complete  # realization

    def test_drafting_stage(self, drafting_project: Path) -> None:
        stages = detect_stages(drafting_project)
        assert stages[3].is_complete  # drafting

    def test_reasoning_stage(self, accepted_project: Path) -> None:
        stages = detect_stages(accepted_project)
        assert stages[4].is_complete  # reasoning (has accepted)

    def test_reconciled_stage(self, reconciled_project: Path) -> None:
        stages = detect_stages(reconciled_project)
        assert stages[4].is_complete  # reasoning
        assert stages[5].is_complete  # reconciliation


# ---------------------------------------------------------------------------
# Tests: current_stage
# ---------------------------------------------------------------------------


class TestCurrentStage:
    def test_empty(self, empty_project: Path) -> None:
        stages = detect_stages(empty_project)
        assert current_stage(stages) == WorkflowStage.IDENTITY

    def test_identity_only(self, identity_project: Path) -> None:
        stages = detect_stages(identity_project)
        assert current_stage(stages) == WorkflowStage.STRUCTURE

    def test_blueprint(self, blueprint_project: Path) -> None:
        stages = detect_stages(blueprint_project)
        assert current_stage(stages) == WorkflowStage.REALIZATION

    def test_outline(self, outline_project: Path) -> None:
        stages = detect_stages(outline_project)
        assert current_stage(stages) == WorkflowStage.DRAFTING

    def test_all_complete(self, reconciled_project: Path) -> None:
        stages = detect_stages(reconciled_project)
        # Last 3 stages (acceptance, assembly, publishing) may be incomplete
        cs = current_stage(stages)
        assert cs is not None

    def test_reconciled_reasoning_done(self, reconciled_project: Path) -> None:
        stages = detect_stages(reconciled_project)
        assert stages[4].is_complete  # reasoning
        assert stages[5].is_complete  # reconciliation


# ---------------------------------------------------------------------------
# Tests: collect_blockers
# ---------------------------------------------------------------------------


class TestCollectBlockers:
    def test_empty_project_blockers(self, empty_project: Path) -> None:
        stages = detect_stages(empty_project)
        blockers = collect_blockers(stages)
        assert len(blockers) >= 1
        assert any(b.category == BlockerCategory.MISSING_PREREQUISITE for b in blockers)

    def test_identity_project_no_identity_blocker(self, identity_project: Path) -> None:
        stages = detect_stages(identity_project)
        blockers = collect_blockers(stages)
        id_blockers = [b for b in blockers if b.artifact == "story_identity.yaml"]
        assert len(id_blockers) == 0  # identity present, no blocker

    def test_blueprint_project_no_struct_blocker(self, blueprint_project: Path) -> None:
        stages = detect_stages(blueprint_project)
        blockers = collect_blockers(stages)
        bp_blockers = [b for b in blockers if b.artifact == "blueprint.yaml"]
        assert len(bp_blockers) == 0


# ---------------------------------------------------------------------------
# Tests: recommend_actions
# ---------------------------------------------------------------------------


class TestRecommendActions:
    def test_empty_project(self, empty_project: Path) -> None:
        stages = detect_stages(empty_project)
        actions = recommend_actions(stages)
        assert len(actions) >= 1
        assert "identity" in actions[0].label.lower()

    def test_identity_stage(self, identity_project: Path) -> None:
        stages = detect_stages(identity_project)
        actions = recommend_actions(stages)
        assert any("Blueprint" in a.label or "blueprint" in a.command for a in actions)

    def test_blueprint_stage(self, blueprint_project: Path) -> None:
        stages = detect_stages(blueprint_project)
        actions = recommend_actions(stages)
        assert any("outline" in a.label.lower() or "cartographer" in a.command for a in actions)

    def test_outline_stage(self, outline_project: Path) -> None:
        stages = detect_stages(outline_project)
        actions = recommend_actions(stages)
        assert any("Draft" in a.label for a in actions)

    def test_all_complete_no_actions(self) -> None:
        from auteur.workflow.models import StageProgress, WorkflowStage
        stages = [
            StageProgress(stage=s, is_complete=True)
            for s in WorkflowStage
        ]
        actions = recommend_actions(stages)
        assert len(actions) == 1
        assert "complete" in actions[0].label.lower()
