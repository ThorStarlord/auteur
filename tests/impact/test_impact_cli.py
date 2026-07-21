"""Tests for impact CLI — subcommand parsing, handlers, formatters."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest
import yaml

from auteur.impact.cli import (
    handle_impact_analyze,
    handle_impact_explain,
    handle_impact_plan,
    handle_impact_status,
    register_impact_subcommands,
)


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    register_impact_subcommands(sub)
    return p


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / ".auteur").mkdir(parents=True)
    (root / ".auteur" / "state" / "artifacts").mkdir(parents=True)
    _write_yaml(root / "story_identity.yaml", {"title": "Test", "genre": "fantasy"})
    _write_yaml(root / "blueprint.yaml", {"project_identity": {"title": "Test"}, "chapters": [{"index": 1}]})
    _write_yaml(root / "chapters" / "1" / "outline.yaml", {"chapter_index": 1, "scenes": [{"id": "s1"}]})
    from auteur.provenance.store import ArtifactStore
    store = ArtifactStore(root)
    store.accept(root / "story_identity.yaml", "story_identity")
    store.accept(root / "blueprint.yaml", "blueprint")
    store.accept(root / "chapters" / "1" / "outline.yaml", "chapter_outline")
    return root


class TestRegisterSubcommands:
    def test_impact_subcommands_registered(self, parser: argparse.ArgumentParser) -> None:
        result = parser.parse_args(["impact", "status", "--project", "."])
        assert result.command == "impact"
        assert result.impact_command == "status"

    def test_impact_analyze(self, parser: argparse.ArgumentParser) -> None:
        result = parser.parse_args(["impact", "analyze", "--project", "."])
        assert result.impact_command == "analyze"

    def test_impact_explain(self, parser: argparse.ArgumentParser) -> None:
        result = parser.parse_args(["impact", "explain", "test_artifact", "--project", "."])
        assert result.impact_command == "explain"

    def test_impact_plan(self, parser: argparse.ArgumentParser) -> None:
        result = parser.parse_args(["impact", "plan", "--project", "."])
        assert result.impact_command == "plan"

    def test_impact_analyze_chapter(self, parser: argparse.ArgumentParser) -> None:
        result = parser.parse_args(["impact", "analyze", "--project", ".", "--chapter", "3"])
        assert result.chapter == 3

    def test_impact_analyze_artifact(self, parser: argparse.ArgumentParser) -> None:
        result = parser.parse_args(["impact", "analyze", "--project", ".", "--artifact", "chapter_03"])
        assert result.artifact == "chapter_03"

    def test_impact_status_json(self, parser: argparse.ArgumentParser) -> None:
        result = parser.parse_args(["impact", "status", "--project", ".", "--json"])
        assert result.json is True


class TestHandlers:
    def test_handle_status(self, project_root: Path) -> None:
        exit_code = handle_impact_status(project_root)
        assert exit_code == 0

    def test_handle_status_json(self, project_root: Path) -> None:
        exit_code = handle_impact_status(project_root, as_json=True)
        assert exit_code == 0

    def test_handle_analyze(self, project_root: Path) -> None:
        exit_code = handle_impact_analyze(project_root)
        assert exit_code == 0

    def test_handle_analyze_json(self, project_root: Path) -> None:
        exit_code = handle_impact_analyze(project_root, as_json=True)
        assert exit_code == 0

    def test_handle_analyze_chapter(self, project_root: Path) -> None:
        exit_code = handle_impact_analyze(project_root, chapter=1)
        assert exit_code == 0

    def test_handle_plan(self, project_root: Path) -> None:
        exit_code = handle_impact_plan(project_root)
        assert exit_code == 0

    def test_handle_plan_json(self, project_root: Path) -> None:
        exit_code = handle_impact_plan(project_root, as_json=True)
        assert exit_code == 0

    def test_handle_explain(self, project_root: Path) -> None:
        exit_code = handle_impact_explain(project_root, "nonexistent")
        assert exit_code == 1  # not found

    def test_handle_explain_json(self, project_root: Path) -> None:
        exit_code = handle_impact_explain(project_root, "nonexistent", as_json=True)
        assert exit_code == 1

    def test_missing_project(self, tmp_path: Path) -> None:
        root = tmp_path / "not_a_project"
        root.mkdir()
        exit_code = handle_impact_status(root)
        assert exit_code == 1

    def test_analyze_save(self, project_root: Path) -> None:
        exit_code = handle_impact_analyze(project_root, save=True)
        assert exit_code == 0
        # Verify persistence was created
        store_dir = project_root / ".auteur" / "impact"
        assert store_dir.exists()
        assert len(list(store_dir.glob("analyses/*.json"))) > 0

    def test_plan_save(self, project_root: Path) -> None:
        exit_code = handle_impact_plan(project_root, save=True)
        assert exit_code == 0
        store_dir = project_root / ".auteur" / "impact"
        assert store_dir.exists()
        assert len(list(store_dir.glob("plans/*.json"))) > 0
