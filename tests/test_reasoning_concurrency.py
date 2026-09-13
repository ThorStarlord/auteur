"""Tests for concurrent critic execution and deterministic ordering."""

from __future__ import annotations

import time
from pathlib import Path


from auteur.reasoning.runtime import (
    CriticRegistry,
    CriticSpec,
    ReasoningRuntime,
    RuntimeRequest,
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
        """The same 5 critics must run clearly faster with 5 workers than with 1.

        Comparing two measured runs of identical work - rather than one run
        against a fixed wall-clock budget - keeps the test meaningful when the
        host is under load: a slow box inflates both the sequential and the
        concurrent timing together, so the ratio holds. (The fixed-budget form
        flaked when three full test suites ran at once - S11 Finding 1.)
        """
        reg = _make_registry()
        req = RuntimeRequest(critic_ids=["draft.a", "draft.b", "draft.c", "draft.d", "draft.e"], inputs={})

        seq_rt = ReasoningRuntime(reg, tmp_path / "seq", max_workers=1)
        t0 = time.monotonic()
        seq = seq_rt.run(req)
        seq_elapsed = time.monotonic() - t0

        con_rt = ReasoningRuntime(reg, tmp_path / "con", max_workers=5)
        t0 = time.monotonic()
        con = con_rt.run(req)
        con_elapsed = time.monotonic() - t0

        # Ideal ratio is ~0.35/1.25 ≈ 0.28; 0.8 is a wide margin that still
        # fails if concurrency is not actually happening.
        assert con_elapsed < seq_elapsed * 0.8, (
            f"Concurrent ({con_elapsed:.3f}s) should be clearly faster than "
            f"sequential ({seq_elapsed:.3f}s) for the same 5 critics"
        )
        assert len(con.outcomes) == 5
        assert len(seq.outcomes) == 5

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
