"""Focused tests for scripts/release_evidence.py.

Covers the two implementation invariants:
1. candidate provenance: candidate-invalidating dirt fails closed;
   permitted non-candidate changes are classified, not fatal.
2. pytest accounting: exactly one terminal outcome per node; setup errors,
   teardown failures after a pass, and xfail/xpass are handled with pytest
   semantics; reconciliation is sum(outcomes) == collected.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import release_evidence as re  # noqa: E402


def report(nodeid, when, outcome="passed", wasxfail=None, failed=False):
    return SimpleNamespace(
        nodeid=nodeid, when=when, outcome=outcome,
        wasxfail=wasxfail, failed=failed,
    )


class TestTerminalOutcomeCollapsing:
    """One terminal outcome per collected node; raw phases never double-count."""

    def test_pass_call(self):
        plugin = re.PytestEvidencePlugin()
        plugin.pytest_runtest_logreport(report("t.py::a", "call", "passed"))
        assert plugin.dispositions == {"t.py::a": "passed"}

    def test_fail_call(self):
        plugin = re.PytestEvidencePlugin()
        plugin.pytest_runtest_logreport(report("t.py::a", "call", "failed", failed=True))
        assert plugin.dispositions == {"t.py::a": "failed"}

    def test_skip_call(self):
        plugin = re.PytestEvidencePlugin()
        plugin.pytest_runtest_logreport(report("t.py::a", "call", "skipped"))
        assert plugin.dispositions == {"t.py::a": "skipped"}

    def test_xfail_from_metadata(self):
        plugin = re.PytestEvidencePlugin()
        plugin.pytest_runtest_logreport(report("t.py::a", "call", "skipped", wasxfail=True))
        assert plugin.dispositions == {"t.py::a": "xfailed"}

    def test_xpass_from_metadata(self):
        plugin = re.PytestEvidencePlugin()
        plugin.pytest_runtest_logreport(report("t.py::a", "call", "passed", wasxfail=True))
        assert plugin.dispositions == {"t.py::a": "xpassed"}

    def test_setup_error_no_call(self):
        plugin = re.PytestEvidencePlugin()
        plugin.pytest_runtest_logreport(report("t.py::a", "setup", "failed", failed=True))
        assert plugin.dispositions == {"t.py::a": "errors"}

    def test_teardown_failure_after_pass_upgrades_to_error_not_double_count(self):
        plugin = re.PytestEvidencePlugin()
        plugin.pytest_runtest_logreport(report("t.py::a", "call", "passed"))
        plugin.pytest_runtest_logreport(report("t.py::a", "teardown", "failed", failed=True))
        assert plugin.dispositions == {"t.py::a": "errors"}
        assert plugin.outcomes()["passed"] == 0
        assert plugin.outcomes()["errors"] == 1

    def test_teardown_failure_after_fail_keeps_failed(self):
        plugin = re.PytestEvidencePlugin()
        plugin.pytest_runtest_logreport(report("t.py::a", "call", "failed", failed=True))
        plugin.pytest_runtest_logreport(report("t.py::a", "teardown", "failed", failed=True))
        assert plugin.dispositions == {"t.py::a": "failed"}


class TestReconciliation:
    def test_sum_equals_collected(self):
        plugin = re.PytestEvidencePlugin()
        plugin.collected = 3
        plugin.dispositions = {"a": "passed", "b": "xfailed", "c": "errors"}
        accounting = re.suite_accounting(plugin)
        assert accounting["reconciles"] is True

    def test_sum_mismatch(self):
        plugin = re.PytestEvidencePlugin()
        plugin.collected = 4
        plugin.dispositions = {"a": "passed", "b": "xfailed", "c": "errors"}
        accounting = re.suite_accounting(plugin)
        assert accounting["reconciles"] is False

    def test_failure_nodes_and_xpassed_nodes(self):
        plugin = re.PytestEvidencePlugin()
        plugin.dispositions = {
            "a": "failed", "b": "errors", "c": "xpassed", "d": "passed",
        }
        accounting = re.suite_accounting(plugin)
        assert accounting["failure_nodes"] == ["a", "b"]
        assert accounting["xpassed_nodes"] == ["c"]


class TestCandidateProvenance:
    def test_clean_candidate(self, monkeypatch):
        monkeypatch.setattr(
            re, "_git",
            lambda *args: SimpleNamespace(
                returncode=0,
                stdout="30529b99ea5198ec91eeaf76bb4073d9d89c77f8\n"
                       if args[0] == "rev-parse"
                       else " M .claude/settings.json\n?? .codex/\n",
                stderr="",
            ),
        )
        sha, invalidating, permitted = re.candidate_provenance()
        assert sha.startswith("30529b99")
        assert invalidating == []
        assert ".claude/settings.json" in permitted

    def test_candidate_invalidating_dirt_fails_closed(self, monkeypatch):
        monkeypatch.setattr(
            re, "_git",
            lambda *args: SimpleNamespace(
                returncode=0,
                stdout="30529b99ea5198ec91eeaf76bb4073d9d89c77f8\n"
                       if args[0] == "rev-parse"
                       else " M src/auteur/cli.py\n M tests/test_x.py\n M pyproject.toml\n",
                stderr="",
            ),
        )
        sha, invalidating, permitted = re.candidate_provenance()
        assert invalidating == ["pyproject.toml", "src/auteur/cli.py", "tests/test_x.py"]
        assert permitted == []


class TestBaseline:
    def test_no_reference_first_run(self):
        section = re.baseline_section(None, ["a", "b"])
        assert section["reference_candidate"] is None
        assert section["current_failure_nodes"] == ["a", "b"]
        assert section["added_failures"] == []

    def test_reference_deltas(self, tmp_path):
        ref = tmp_path / "ref.json"
        ref.write_text(json.dumps({
            "candidate": {"sha": "AAAA"},
            "suite": {"failure_nodes": ["a", "b"]},
        }))
        section = re.baseline_section(str(ref), ["b", "c"])
        assert section["reference_candidate"] == "AAAA"
        assert section["added_failures"] == ["c"]
        assert section["removed_failures"] == ["a"]
        assert section["unchanged_failures"] == ["b"]

    def test_missing_reference_raises(self, tmp_path):
        with pytest.raises(RuntimeError):
            re.baseline_section("does-not-exist", [])
