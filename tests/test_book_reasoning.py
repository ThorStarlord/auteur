"""Tests for Book Manuscript reasoning (v0.25.0).

Tests the deterministic BookManuscriptReasonAnalyzer and the 
'auteur reasoning book' CLI command.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True, exist_ok=True)
    (root / ".auteur").mkdir(parents=True, exist_ok=True)
    return root


@pytest.fixture
def book_dir(project_root: Path) -> Path:
    p = project_root / "book" / "expression"
    p.mkdir(parents=True, exist_ok=True)
    return p


# =========================================================================
# BookManuscriptReasonAnalyzer unit tests
# =========================================================================


class TestAnalyzerNoBook:

    def test_no_book_manifest(self, project_root):
        from auteur.reasoning.book_manuscript import run_book_analysis
        findings = run_book_analysis(project=project_root)
        # Should find no-manifest finding
        rules = {f["rule"] for f in findings}
        assert "book.manuscript.no_manifest" in rules

    def test_empty_manifest(self, book_dir):
        (book_dir / "accepted.yaml").write_text("", encoding="utf-8")
        from auteur.reasoning.book_manuscript import run_book_analysis
        findings = run_book_analysis(project=book_dir.parent.parent)
        rules = {f["rule"] for f in findings}
        assert "book.manuscript.empty_manifest" in rules

    def test_unparseable_yaml(self, book_dir):
        (book_dir / "accepted.yaml").write_text(":::\ninvalid yaml\n", encoding="utf-8")
        from auteur.reasoning.book_manuscript import run_book_analysis
        findings = run_book_analysis(project=book_dir.parent.parent)
        rules = {f["rule"] for f in findings}
        assert "book.manifest.unparseable" in rules


class TestAnalyzerWithBook:

    @pytest.fixture
    def with_manifest(self, book_dir):
        import yaml
        manifest = {
            "chapters": [
                {"chapter_id": "1", "title": "Chapter One"},
                {"chapter_id": "2", "title": "Chapter Two"},
            ],
            "chapter_estimate": 5,
            "revision": 1,
        }
        (book_dir / "accepted.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
        return book_dir

    def test_reports_chapter_count(self, with_manifest):
        from auteur.reasoning.book_manuscript import run_book_analysis
        findings = run_book_analysis(project=with_manifest.parent.parent)
        rules = {f["rule"] for f in findings}
        assert "book.manuscript.summary" in rules
        summary = next(f for f in findings if f["rule"] == "book.manuscript.summary")
        assert summary["evidence"]["chapter_count"] == 2

    def test_chapter_gap_estimate(self, with_manifest):
        from auteur.reasoning.book_manuscript import run_book_analysis
        findings = run_book_analysis(project=with_manifest.parent.parent)
        rules = {f["rule"] for f in findings}
        # Should flag that we have 2 of 5 planned chapters
        assert "book.manuscript.chapter_gap" in rules

    def test_no_gap_when_estimate_matches(self, book_dir):
        import yaml
        manifest = {
            "chapters": [
                {"chapter_id": "1", "title": "One"},
                {"chapter_id": "2", "title": "Two"},
            ],
            "chapter_estimate": 2,
            "revision": 1,
        }
        (book_dir / "accepted.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
        from auteur.reasoning.book_manuscript import run_book_analysis
        findings = run_book_analysis(project=book_dir.parent.parent)
        rules = {f["rule"] for f in findings}
        assert "book.manuscript.chapter_gap" not in rules


class TestAnalyzerContinuity:

    @pytest.fixture
    def with_manifest(self, book_dir):
        import yaml
        manifest = {
            "chapters": [
                {"chapter_id": "1", "title": "One"},
                {"chapter_id": "2", "title": "Two"},
                {"chapter_id": "4", "title": "Four"},  # gap: no chapter 3
            ],
            "chapter_estimate": 5,
            "revision": 1,
        }
        (book_dir / "accepted.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
        return book_dir

    def test_sequence_gap_detected(self, with_manifest):
        from auteur.reasoning.book_manuscript import run_book_analysis
        findings = run_book_analysis(project=with_manifest.parent.parent)
        rules = {f["rule"] for f in findings}
        assert "book.manuscript.sequence_gap" in rules

    def test_duplicate_chapter_id(self, book_dir):
        import yaml
        manifest = {
            "chapters": [
                {"chapter_id": "1", "title": "One"},
                {"chapter_id": "1", "title": "One again"},  # duplicate
            ],
            "chapter_estimate": 5,
            "revision": 1,
        }
        (book_dir / "accepted.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
        from auteur.reasoning.book_manuscript import run_book_analysis
        findings = run_book_analysis(project=book_dir.parent.parent)
        rules = {f["rule"] for f in findings}
        assert "book.manuscript.duplicate_chapter_id" in rules

    def test_orphan_acceptance_files(self, book_dir):
        import yaml
        manifest = {
            "chapters": [
                {"chapter_id": "1", "title": "One"},
            ],
            "chapter_estimate": 2,
            "revision": 1,
        }
        (book_dir / "accepted.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
        # Create an orphan acceptance file not in the manifest
        (book_dir / "chapter_99_accepted.yaml").write_text("dummy", encoding="utf-8")
        from auteur.reasoning.book_manuscript import run_book_analysis
        findings = run_book_analysis(project=book_dir.parent.parent)
        rules = {f["rule"] for f in findings}
        assert "book.manuscript.orphan_acceptance" in rules


class TestCriticRegistration:

    def test_register(self):
        from auteur.reasoning.runtime import CriticRegistry
        from auteur.reasoning.book_manuscript import register_book_manuscript_critic
        registry = CriticRegistry()
        register_book_manuscript_critic(registry)
        spec = registry.discover(critic_id="book.manuscript")
        assert spec.critic_id == "book.manuscript"
        assert spec.version == "1.0.0"

    def test_register_via_all_builtins(self):
        from auteur.reasoning.runtime import CriticRegistry
        from auteur.reasoning.registrar import register_all_builtins
        registry = CriticRegistry()
        register_all_builtins(registry)
        spec = registry.discover(critic_id="book.manuscript")
        assert spec.critic_id == "book.manuscript"


class TestRuntimeIntegration:

    def test_runtime_execution(self, project_root):
        from auteur.reasoning.runtime import CriticRegistry, ReasoningRuntime, RuntimeRequest
        from auteur.reasoning.registrar import register_all_builtins
        registry = CriticRegistry()
        register_all_builtins(registry)
        runtime = ReasoningRuntime(registry, project_root / ".auteur" / "reasoning")
        request = RuntimeRequest(
            request_id="test_book",
            critic_ids=["book.manuscript"],
            inputs={"project": project_root},
        )
        result = runtime.run(request)
        assert len(result.outcomes) == 1
        assert result.outcomes[0].critic_id == "book.manuscript"
        assert result.outcomes[0].status.value == "success"


class TestCLI:

    def test_reasoning_book_help(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["reasoning", "book", "--help"])
        assert exc.value.code == 0

    def test_reasoning_book_default(self, project_root):
        from auteur.cli import main
        rc = main(["reasoning", "book", "--project", str(project_root)])
        assert rc == 0

    def test_reasoning_book_json(self, project_root):
        from auteur.cli import main
        rc = main(["reasoning", "book", "--project", str(project_root), "--json"])
        assert rc == 0
