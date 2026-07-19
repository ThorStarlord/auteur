"""Tests for concurrent critic execution and deterministic ordering."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from auteur.reasoning.runtime import (
    CriticRegistry,
    CriticSpec,
    ExecutionOutcome,
    ReasoningRuntime,
    RuntimeRequest,
    RuntimeStatus,
)


def _make_registry() -> CriticRegistry:
    """Create a registry with 5 independent critics, each with a controlled delay."""
    reg = CriticRegistry()
    for i, cid in enumerate(["draft.a", "draft.b", "draft.c", "draft.d", "draft.e"]):
        delay = 0.15 + (i * 0.05)  # 0.15, 0.20, 0.25, 0.30, 0.35 seconds

        def make_runner(delay: float = delay, cid: str = cid):
            def runner(**inputs: object) -> list[dict]:
                time.sleep(delay)
                return [{"critic": cid.replace("draft.", ""), "severity": "info", "rule": "timing-test", "evidence": f"delayed {delay}s", "requested_change": ""}]
            return runner

        reg.register(CriticSpec(critic_id=cid, version="0.1.0", requires=(), input_keys=(), run=make_runner()))
    return reg


class TestConcurrentExecution:
    def test_concurrent_is_faster_than_sequential(self, tmp_path: Path) -> None:
        """5 critics with total sequential time ~1.25s should complete well under 1s."""
        reg = _make_registry()
        rt = ReasoningRuntime(reg, tmp_path / "reports", max_workers=5)
        req = RuntimeRequest(critic_ids=["draft.a", "draft.b", "draft.c", "draft.d", "draft.e"], inputs={})
        t0 = time.monotonic()
        result = rt.run(req)
        elapsed = time.monotonic() - t0
        worst = max(0.15, 0.20, 0.25, 0.30, 0.35)
        assert elapsed < worst * 2, f"Expected concurrent time < {worst*2:.2f}s, got {elapsed:.3f}s (sequential would be ~1.25s)"
        assert len(result.outcomes) == 5

    def test_each_critic_executed_once(self, tmp_path: Path) -> None:
        reg = _make_registry()
        rt = ReasoningRuntime(reg, tmp_path / "reports", max_workers=5)
        req = RuntimeRequest(critic_ids=["draft.a", "draft.b", "draft.c", "draft.d", "draft.e"], inputs={})
        result = rt.run(req)
        cids = [o.critic_id for o in result.outcomes]
        assert len(cids) == 5
        assert len(set(cids)) == 5  # no duplicates

    def test_deterministic_ordering(self, tmp_path: Path) -> None:
        """Outcome ordering must be deterministic regardless of completion order."""
        reg = _make_registry()
        rt1 = ReasoningRuntime(reg, tmp_path / "r1", max_workers=5)
        rt2 = ReasoningRuntime(reg, tmp_path / "r2", max_workers=5)
        req = RuntimeRequest(critic_ids=["draft.a", "draft.b", "draft.c", "draft.d", "draft.e"], inputs={})
        r1 = rt1.run(req)
        r2 = rt2.run(req)
        ids1 = [o.critic_id for o in r1.outcomes]
        ids2 = [o.critic_id for o in r2.outcomes]
        assert ids1 == ids2, f"Order differs: {ids1} vs {ids2}"
        # Timestamps should differ but order must be same
        assert r1.outcomes[0].critic_id == r2.outcomes[0].critic_id

    def test_dependency_respected(self, tmp_path: Path) -> None:
        """A critic that depends on another must execute after it."""
        reg = CriticRegistry()
        reg.register(CriticSpec(critic_id="parent", version="0.1.0", requires=(), input_keys=(), run=lambda **i: [{"critic": "parent", "severity": "info", "rule": "dep", "evidence": "", "requested_change": ""}]))
        reg.register(CriticSpec(critic_id="child", version="0.1.0", requires=("parent",), input_keys=(), run=lambda **i: [{"critic": "child", "severity": "info", "rule": "dep", "evidence": "", "requested_change": ""}]))
        rt = ReasoningRuntime(reg, tmp_path / "reports")
        req = RuntimeRequest(critic_ids=["child", "parent"], inputs={})
        result = rt.run(req)
        cids = [o.critic_id for o in result.outcomes]
        assert cids.index("parent") < cids.index("child"), f"Dependency violated: {cids}"

    def test_bounded_workers(self, tmp_path: Path) -> None:
        """max_workers=1 should cause sequential-like timing."""
        reg = _make_registry()
        rt = ReasoningRuntime(reg, tmp_path / "reports", max_workers=1)
        req = RuntimeRequest(critic_ids=["draft.a", "draft.b"], inputs={})
        t0 = time.monotonic()
        result = rt.run(req)
        elapsed = time.monotonic() - t0
        expected_min = 0.15 + 0.20  # sequential sum
        assert elapsed >= expected_min * 0.8, f"Sequential-with-1-worker too fast: {elapsed:.3f}s < {expected_min:.3f}s"
        assert len(result.outcomes) == 2
