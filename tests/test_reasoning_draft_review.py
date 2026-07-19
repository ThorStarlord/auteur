"""Tests for the ReasoningRuntime persistence and review module."""

from __future__ import annotations

import yaml
from pathlib import Path
import pytest

from auteur.reasoning.runtime import (
    CriticRegistry,
    CriticSpec,
    ExecutionResult,
    ReasoningRuntime,
    RuntimeRequest,
    RuntimeStatus,
)
from auteur.reasoning.draft_review import (
    load_latest_run,
    load_reasoning_run,
    persist_reasoning_run,
    review_source_freshness,
)


def _stub_contract(**inputs: object) -> list[dict[str, object]]:
    return [{"critic": "draft.contract", "severity": "warning", "rule": "test-rule", "evidence": "stub", "requested_change": "none"}]


def _stub_empty(**inputs: object) -> list[dict[str, object]]:
    return []


def _make_runtime(tmp_path: Path) -> ReasoningRuntime:
    registry = CriticRegistry()
    registry.register(CriticSpec(critic_id="draft.contract", version="0.1.0", requires=(), input_keys=("draft",), run=_stub_contract))
    registry.register(CriticSpec(critic_id="draft.arc", version="0.1.0", requires=(), input_keys=("draft",), run=_stub_empty))
    return ReasoningRuntime(registry, tmp_path / "reports")


def _make_result(tmp_path: Path) -> ExecutionResult:
    runtime = _make_runtime(tmp_path)
    req = RuntimeRequest(
        critic_ids=["draft.contract", "draft.arc"],
        inputs={"draft": "test chapter content", "outline": {}, "blueprint": None, "bible": None, "chapter_index": 1, "llm": None},
    )
    return runtime.run(req)


class TestPersistReasoningRun:
    def test_persist_success(self, tmp_path: Path) -> None:
        result = _make_result(tmp_path)
        run = persist_reasoning_run(tmp_path, chapter_index=1, iteration=1, result=result)
        assert run["chapter_index"] == 1
        assert run["iteration"] == 1
        assert run["overall_status"] in ("success", "partial", "failed")

        root = tmp_path / "chapters" / "01" / "reasoning"
        assert (root / "runs").exists()
        assert (root / "reviews").exists()
        assert (root / "latest.yaml").exists()

    def test_immutable_historical_runs(self, tmp_path: Path) -> None:
        result1 = _make_result(tmp_path)
        run1 = persist_reasoning_run(tmp_path, chapter_index=1, iteration=1, result=result1)
        result2 = _make_result(tmp_path)
        run2 = persist_reasoning_run(tmp_path, chapter_index=1, iteration=2, result=result2)
        root = tmp_path / "chapters" / "01" / "reasoning"
        runs = list((root / "runs").iterdir())
        assert len(runs) >= 2

    def test_mutable_latest_pointer(self, tmp_path: Path) -> None:
        result1 = _make_result(tmp_path)
        persist_reasoning_run(tmp_path, chapter_index=1, iteration=1, result=result1)
        latest1 = load_latest_run(tmp_path, chapter_index=1)
        assert latest1 is not None and latest1["iteration"] == 1

        result2 = _make_result(tmp_path)
        persist_reasoning_run(tmp_path, chapter_index=1, iteration=2, result=result2)
        latest2 = load_latest_run(tmp_path, chapter_index=1)
        assert latest2 is not None and latest2["iteration"] == 2

    def test_load_run(self, tmp_path: Path) -> None:
        result = _make_result(tmp_path)
        run = persist_reasoning_run(tmp_path, chapter_index=1, iteration=1, result=result)
        loaded = load_reasoning_run(tmp_path, chapter_index=1, run_id=run["run_id"])
        assert loaded is not None and loaded["run_id"] == run["run_id"]

    def test_load_run_not_found(self, tmp_path: Path) -> None:
        assert load_reasoning_run(tmp_path, 1, "nonexistent") is None

    def test_load_latest_missing(self, tmp_path: Path) -> None:
        assert load_latest_run(tmp_path, 1) is None


class TestFreshness:
    def test_fresh(self, tmp_path: Path) -> None:
        result = _make_result(tmp_path)
        run = persist_reasoning_run(tmp_path, 1, 1, result, draft_hash="abc", outline_hash="def")
        f = review_source_freshness(tmp_path, 1, run["run_id"], current_draft_hash="abc", current_outline_hash="def")
        assert f["fresh"] is True

    def test_stale(self, tmp_path: Path) -> None:
        result = _make_result(tmp_path)
        run = persist_reasoning_run(tmp_path, 1, 1, result, draft_hash="abc", outline_hash="def")
        f = review_source_freshness(tmp_path, 1, run["run_id"], current_draft_hash="xyz", current_outline_hash="def")
        assert f["fresh"] is False
        assert "draft_hash" in f["stale_sources"]

    def test_run_not_found(self, tmp_path: Path) -> None:
        f = review_source_freshness(tmp_path, 1, "nonexistent")
        assert f["fresh"] is False
        assert "run_not_found" in f["stale_sources"]


class TestRenderMarkdown:
    def test_basic(self) -> None:
        from auteur.reasoning.draft_review import _render_review_markdown
        review = {
            "chapter_index": 1, "run_id": "run_abc", "iteration": 2,
            "overall_status": "success", "freshness": "fresh",
            "critic_summaries": [
                {"critic_id": "draft.contract", "status": "success", "version": "0.1.0", "finding_count": 0},
            ],
            "blocking_findings": [],
            "warnings": [{"critic_id": "draft.arc", "evidence": "Minor pacing issue"}],
            "synthesis": "Chapter reads well.",
            "recommended_actions": ["Tighten opening."],
        }
        md = _render_review_markdown(review)
        assert "Reasoning Review" in md and "draft.contract" in md and "Minor pacing issue" in md

    def test_blocking(self) -> None:
        from auteur.reasoning.draft_review import _render_review_markdown
        review = {
            "chapter_index": 2, "run_id": "run_def", "iteration": 1,
            "overall_status": "failed", "freshness": "fresh",
            "critic_summaries": [{"critic_id": "draft.contract", "status": "failed", "version": "0.1.0", "finding_count": 1}],
            "blocking_findings": [{"critic": "draft.contract", "evidence": "Character motivation unclear"}],
            "warnings": [], "synthesis": "", "recommended_actions": [],
        }
        md = _render_review_markdown(review)
        assert "Blocking Findings" in md and "Character motivation" in md
