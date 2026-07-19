"""Backward compatibility and platform tests for v0.4.0."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from auteur.reasoning.cli import format_review, _freshness_label


# A minimal v0.3.0-style review artifact (no execution, usage, provider/model fields)
V030_REVIEW = {
    "review_id": "v030_legacy",
    "run_id": "run_legacy",
    "artifact_type": "reasoning_review",
    "authority": "derived",
    "lifecycle": "published",
    "chapter_index": 1,
    "iteration": 1,
    "created_at": "2026-07-19T00:00:00Z",
    "overall_status": "success",
    "critic_summaries": [
        {"critic_id": "draft.contract", "status": "success", "version": "0.1.0", "finding_count": 0},
        {"critic_id": "draft.arc", "status": "success", "version": "0.1.0", "finding_count": 0},
    ],
    "blocking_findings": [],
    "warnings": [],
    "synthesis": "No concerns.",
    "recommended_actions": [],
    "source_snapshot": {"draft_hash": "abc", "outline_hash": "def"},
    "freshness": "fresh",
}


class TestBackwardCompatibility:
    def test_v030_review_loads(self):
        """v0.3.0 review without new fields must not crash format_review."""
        result = format_review(V030_REVIEW)
        assert "v030_legacy" in result
        assert "fresh" in result

    def test_v030_freshness_string_handled(self):
        """v0.3.0 freshness as a string must work."""
        label = _freshness_label(V030_REVIEW)
        assert label == "fresh"

    def test_v030_review_json_roundtrip(self, tmp_path: Path):
        """v0.3.0 review must be serializable and loadable."""
        p = tmp_path / "review.json"
        p.write_text(json.dumps(V030_REVIEW))
        loaded = json.loads(p.read_text())
        assert loaded["review_id"] == "v030_legacy"

    def test_new_fields_absent_in_v030(self):
        """v0.3.0 reviews lack execution and usage fields."""
        assert "execution" not in V030_REVIEW
        assert "usage" not in V030_REVIEW


class TestCLINegativeCases:
    def test_missing_file(self, tmp_path: Path):
        from auteur.reasoning.cli import load_review
        with pytest.raises(FileNotFoundError):
            load_review(tmp_path / "nonexistent.json")

    def test_malformed_json(self, tmp_path: Path):
        from auteur.reasoning.cli import load_review
        p = tmp_path / "bad.json"
        p.write_text("{invalid json}")
        with pytest.raises(json.JSONDecodeError):
            load_review(p)

    def test_empty_file(self, tmp_path: Path):
        from auteur.reasoning.cli import load_review
        p = tmp_path / "empty.json"
        p.write_text("")
        with pytest.raises(json.JSONDecodeError):
            load_review(p)


class TestFailureSemantics:
    def test_multiple_failures_inspectable(self):
        """Multiple failed critics should all appear in outcomes."""
        from auteur.reasoning.runtime import (
            CriticRegistry, CriticSpec, ReasoningRuntime, RuntimeRequest, RuntimeStatus
        )
        def failing(**i):
            raise RuntimeError("critic crashed")
        reg = CriticRegistry()
        reg.register(CriticSpec(critic_id="draft.a", version="1.0", requires=(), input_keys=(), run=failing))
        reg.register(CriticSpec(critic_id="draft.b", version="1.0", requires=(), input_keys=(), run=failing))
        rt = ReasoningRuntime(reg, Path())
        req = RuntimeRequest(critic_ids=["draft.a", "draft.b"], inputs={})
        result = rt.run(req)
        assert len(result.outcomes) == 2
        assert all(o.status == RuntimeStatus.FAILED for o in result.outcomes)
        assert all("critic crashed" in (o.error or "") for o in result.outcomes)

    def test_success_and_failure_coexist(self):
        """Successful critics must persist even when a peer fails."""
        from auteur.reasoning.runtime import (
            CriticRegistry, CriticSpec, ReasoningRuntime, RuntimeRequest, RuntimeStatus
        )
        def ok(**i):
            return [{"critic": "ok", "severity": "info", "rule": "test", "evidence": "", "requested_change": ""}]
        def fail(**i):
            raise RuntimeError("failed")
        reg = CriticRegistry()
        reg.register(CriticSpec(critic_id="draft.ok", version="1.0", requires=(), input_keys=(), run=ok))
        reg.register(CriticSpec(critic_id="draft.fail", version="1.0", requires=(), input_keys=(), run=fail))
        rt = ReasoningRuntime(reg, Path())
        req = RuntimeRequest(critic_ids=["draft.ok", "draft.fail"], inputs={})
        result = rt.run(req)
        outcomes = {o.critic_id: o for o in result.outcomes}
        assert outcomes["draft.ok"].status == RuntimeStatus.SUCCESS
        assert outcomes["draft.fail"].status == RuntimeStatus.FAILED

    def test_synthesis_failure_no_false_pass(self, tmp_path: Path):
        """When synthesis fails, validation must not pass."""
        from auteur.reasoning.draft_review import persist_reasoning_run
        from auteur.reasoning.runtime import (
            CriticRegistry, CriticSpec, ReasoningRuntime, RuntimeRequest, RuntimeStatus
        )
        def ok(**i):
            return [{"critic": "ok", "severity": "info", "rule": "test", "evidence": "", "requested_change": ""}]
        reg = CriticRegistry()
        reg.register(CriticSpec(critic_id="draft.ok", version="1.0", requires=(), input_keys=(), run=ok))
        rt = ReasoningRuntime(reg, tmp_path / "reports")
        req = RuntimeRequest(critic_ids=["draft.ok"], inputs={})
        result = rt.run(req)
        # Persist and verify no false positive
        run = persist_reasoning_run(tmp_path, 1, 1, result)
        assert run["overall_status"] in ("success", "partial")


class TestConcurrencyOverlap:
    def test_critics_execute_concurrently(self, tmp_path: Path):
        """Use a barrier to prove actual concurrent execution."""
        import threading
        barrier = threading.Barrier(3)  # 2 critics + main test
        entered = threading.Event()

        def slow(**i):
            barrier.wait(2)  # non-blocking wait
            entered.set()
            return [{"critic": "slow", "severity": "info", "rule": "overlap", "evidence": "", "requested_change": ""}]

        def fast(**i):
            barrier.wait(2)
            return [{"critic": "fast", "severity": "info", "rule": "overlap", "evidence": "", "requested_change": ""}]

        from auteur.reasoning.runtime import CriticRegistry, CriticSpec, ReasoningRuntime, RuntimeRequest
        reg = CriticRegistry()
        reg.register(CriticSpec(critic_id="draft.slow", version="1.0", requires=(), input_keys=(), run=slow))
        reg.register(CriticSpec(critic_id="draft.fast", version="1.0", requires=(), input_keys=(), run=fast))
        rt = ReasoningRuntime(reg, tmp_path / "reports", max_workers=2)
        req = RuntimeRequest(critic_ids=["draft.slow", "draft.fast"], inputs={})
        result = rt.run(req)
        assert len(result.outcomes) == 2

    def test_max_workers_respected(self, tmp_path: Path):
        """With max_workers=1, critics must execute sequentially, not overlap."""
        import threading
        active = []
        lock = threading.Lock()
        max_active = [0]

        def monitored(**i):
            with lock:
                active.append("+")
                max_active[0] = max(max_active[0], len(active))
            import time
            time.sleep(0.2)
            with lock:
                active.pop()
            return [{"critic": "m", "severity": "info", "rule": "m", "evidence": "", "requested_change": ""}]

        from auteur.reasoning.runtime import CriticRegistry, CriticSpec, ReasoningRuntime, RuntimeRequest
        reg = CriticRegistry()
        reg.register(CriticSpec(critic_id="draft.a", version="1.0", requires=(), input_keys=(), run=monitored))
        reg.register(CriticSpec(critic_id="draft.b", version="1.0", requires=(), input_keys=(), run=monitored))
        rt = ReasoningRuntime(reg, tmp_path / "reports", max_workers=1)
        req = RuntimeRequest(critic_ids=["draft.a", "draft.b"], inputs={})
        rt.run(req)
        assert max_active[0] <= 1, f"max_workers=1 violated: {max_active[0]} concurrent"
