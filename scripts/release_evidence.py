"""Canonical durable release-qualification evidence producer for Auteur.

Records mechanically observable release-qualification facts for one candidate
revision into an immutable, candidate-addressed artifact at
docs/qualification-evidence/<candidate-sha>.json, per
docs/engineering/release-qualification.md.

Deliberate boundaries:
- This script records OBSERVATIONS (suite accounting, wheel-qualification
  result, candidate identity, baseline failure-set deltas). It does NOT
  decide whether a release is permitted, whether a known baseline failure
  may be waived, or how acceptance records are worded.
- It consumes scripts/verify_wheel.py as the owner of wheel checks; it does
  not reimplement them.

Candidate provenance invariant: candidate.sha must identify the bytes
actually tested. The producer fails closed (no artifact) when the working
tree contains changes in candidate-invalidating paths (source code, tests,
version metadata, package resources, build configuration - per the
release-qualification candidate-invalidation rule). Permitted non-candidate
changes are recorded in the artifact.

Pytest accounting invariant: exactly one terminal outcome is derived per
collected test node from structured pytest reports (setup/call/teardown are
collapsed; xfail/xpass come from pytest metadata, never from display
formatting). Collection/session errors are recorded separately and fail
qualification regardless. Reconciliation is sum(outcomes) == collected.

Exit codes:
  0  artifact written, internally consistent, suite green, wheel OK
  1  artifact written but the suite is not green (recorded for the release
     authority; conservative gate)
  2  artifact written but the gate failed (collection/session errors,
     reconciliation mismatch, unexpected xpasses, wheel timeout/failure), or
     the reference baseline could not be loaded
  (no artifact is written at all when the candidate is dirty - fail closed)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "docs" / "qualification-evidence"
WHEEL_SCRIPT = ROOT / "scripts" / "verify_wheel.py"
WHEEL_PASS_BANNER = "ALL INSTALLED WHEEL QUALIFICATION MATRIX CHECKS PASSED!"
WHEEL_TIMEOUT_SECONDS = 1800

# Candidate-invalidating paths per release-qualification.md candidate
# invalidation rule (source code, tests, version metadata, package
# resources, build configuration).
CANDIDATE_PREFIXES = ("src/", "tests/")
CANDIDATE_FILES = ("pyproject.toml",)

TERMINAL_OUTCOMES = ("passed", "skipped", "xfailed", "xpassed", "failed", "errors")


# ---------------------------------------------------------------------------
# Candidate provenance
# ---------------------------------------------------------------------------

def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True
    )


def candidate_provenance() -> tuple[str, list[str], list[str]]:
    """Return (sha, invalidating_paths, permitted_non_candidate_paths)."""
    head = _git("rev-parse", "HEAD")
    if head.returncode != 0:
        raise RuntimeError("cannot resolve candidate HEAD: " + head.stderr.strip())
    sha = head.stdout.strip()

    status = _git("status", "--porcelain")
    if status.returncode != 0:
        raise RuntimeError("cannot read working-tree status: " + status.stderr.strip())

    invalidating: list[str] = []
    permitted: list[str] = []
    for line in status.stdout.splitlines():
        path = line[3:].strip()
        if not path:
            continue
        if path.startswith(CANDIDATE_PREFIXES) or path in CANDIDATE_FILES:
            invalidating.append(path)
        else:
            permitted.append(path)
    return sha, sorted(invalidating), sorted(permitted)


# ---------------------------------------------------------------------------
# Structured pytest evidence
# ---------------------------------------------------------------------------

class PytestEvidencePlugin:
    """One terminal outcome per collected test node, from structured reports.

    - setup failure -> ERROR (no call outcome)
    - teardown failure after a passing/skipped call upgrades to ERROR
      (never double-counts a node as passed + errors)
    - xfail/xpass come from pytest's wasxfail metadata, not display text
    """

    def __init__(self) -> None:
        self.collected = 0
        self.dispositions: dict[str, str] = {}
        self.collection_errors: list[str] = []
        self.session_errors: list[str] = []
        self.exit_status = 0

    def pytest_collection_finish(self, session) -> None:
        self.collected = len(session.items)

    def pytest_collectreport(self, report) -> None:
        if report.failed:
            self.collection_errors.append(str(report.longrepr or report.nodeid))

    def pytest_runtest_logreport(self, report) -> None:
        node = report.nodeid
        if report.when == "setup":
            if report.failed:
                self.dispositions[node] = "errors"
            return
        if report.when == "call":
            if report.outcome == "passed":
                self.dispositions[node] = (
                    "xpassed" if getattr(report, "wasxfail", None) else "passed"
                )
            elif report.outcome == "failed":
                self.dispositions[node] = "failed"
            else:  # skipped
                self.dispositions[node] = (
                    "xfailed" if getattr(report, "wasxfail", None) else "skipped"
                )
            return
        if report.when == "teardown":
            if report.failed and self.dispositions.get(node) in (
                None, "passed", "skipped", "xfailed", "xpassed",
            ):
                self.dispositions[node] = "errors"

    def pytest_sessionfinish(self, session, exitstatus) -> None:
        self.exit_status = int(exitstatus)

    def outcomes(self) -> dict[str, int]:
        counts = {outcome: 0 for outcome in TERMINAL_OUTCOMES}
        for disposition in self.dispositions.values():
            counts[disposition] += 1
        return counts


def suite_accounting(plugin: PytestEvidencePlugin) -> dict:
    outcomes = plugin.outcomes()
    return {
        "collected": plugin.collected,
        "outcomes": outcomes,
        "reconciles": sum(outcomes.values()) == plugin.collected,
        "failure_nodes": sorted(
            node for node, d in plugin.dispositions.items() if d in ("failed", "errors")
        ),
        "xpassed_nodes": sorted(
            node for node, d in plugin.dispositions.items() if d == "xpassed"
        ),
        "collection_errors": plugin.collection_errors,
        "session_errors": plugin.session_errors,
    }


# ---------------------------------------------------------------------------
# Wheel qualification (consume verify_wheel.py; do not duplicate its checks)
# ---------------------------------------------------------------------------

def wheel_qualification() -> dict:
    # The isolated venv must test the installed wheel, not a source tree the
    # caller's environment points at: strip PYTHONPATH leakage.
    env = {k: v for k, v in os.environ.items() if k.upper() != "PYTHONPATH"}
    try:
        result = subprocess.run(
            [sys.executable, str(WHEEL_SCRIPT)],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=WHEEL_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {
            "source": "scripts/verify_wheel.py",
            "status": "TIMEOUT",
            "exit_code": None,
            "output_ref": None,
            "sha256": None,
        }
    stdout = result.stdout or ""
    sha256 = None
    for line in stdout.splitlines():
        if line.strip().startswith("Wheel SHA-256"):
            sha256 = line.split(":", 1)[1].strip()
    return {
        "source": "scripts/verify_wheel.py",
        "status": "PASS" if (result.returncode == 0 and WHEEL_PASS_BANNER in stdout) else "FAIL",
        "exit_code": result.returncode,
        "output_ref": (stdout.strip().splitlines() or [""])[-1][:200],
        "sha256": sha256,
    }


# ---------------------------------------------------------------------------
# Baseline failure-set deltas (observations only)
# ---------------------------------------------------------------------------

def baseline_section(
    reference: str | None, current_failure_nodes: list[str]
) -> dict:
    if reference is None:
        return {
            "reference_candidate": None,
            "current_failure_nodes": sorted(current_failure_nodes),
            "baseline_failure_nodes": [],
            "added_failures": [],
            "removed_failures": [],
            "unchanged_failures": [],
        }
    ref_path = Path(reference)
    if not ref_path.exists():
        candidate = reference[:-5] if reference.endswith(".json") else reference
        ref_path = EVIDENCE_DIR / f"{candidate}.json"
    if not ref_path.exists():
        raise RuntimeError(f"reference evidence not found: {ref_path}")
    data = json.loads(ref_path.read_text(encoding="utf-8"))
    base_failures = set(data["suite"]["failure_nodes"])
    current = set(current_failure_nodes)
    return {
        "reference_candidate": data["candidate"]["sha"],
        "current_failure_nodes": sorted(current),
        "baseline_failure_nodes": sorted(base_failures),
        "added_failures": sorted(current - base_failures),
        "removed_failures": sorted(base_failures - current),
        "unchanged_failures": sorted(current & base_failures),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Produce durable, candidate-addressed release-qualification evidence."
    )
    parser.add_argument(
        "--reference",
        help="prior candidate SHA (or path) to diff failure sets against; "
             "first run has no reference",
    )
    parser.add_argument(
        "--out", help="override output path (default docs/qualification-evidence/<sha>.json)"
    )
    parser.add_argument(
        "--skip-wheel", action="store_true",
        help="skip the wheel-qualification subprocess (development only)",
    )
    args = parser.parse_args(argv)

    sha, invalidating, permitted = candidate_provenance()
    if invalidating:
        # Fail closed: candidate.sha would not identify the bytes tested.
        print(
            "FAIL CLOSED: candidate-invalidating working-tree changes: "
            + ", ".join(invalidating)
        )
        return 2

    os.chdir(ROOT)
    plugin = PytestEvidencePlugin()
    pytest_args = ["-q", "--tb=short", "--no-header", "-p", "no:cacheprovider", "tests"]
    pytest_exit = pytest.main(pytest_args, plugins=[plugin])

    accounting = suite_accounting(plugin)
    try:
        baseline = baseline_section(args.reference, accounting["failure_nodes"])
    except RuntimeError as exc:
        print(f"EVIDENCE GATE FAILED: {exc}")
        return 2

    wheel = (
        {"source": "scripts/verify_wheel.py", "status": "NOT_RUN",
         "exit_code": None, "output_ref": None, "sha256": None}
        if args.skip_wheel
        else wheel_qualification()
    )

    artifact = {
        "schema_version": 1,
        "produced_by": "scripts/release_evidence.py",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate": {
            "sha": sha,
            "repository_state": {
                "clean_for_candidate": True,
                "permitted_non_candidate_changes": permitted,
            },
        },
        "suite": accounting,
        "baseline": baseline,
        "wheel": wheel,
        "evidence_note": (
            "Documentation-only evidence per docs/engineering/release-qualification.md: "
            "docs/ is not packaged (pyproject.toml packages only src/auteur), so the "
            "evidence commit does not change the qualified candidate. candidate.sha "
            "attests to the revision whose bytes produced this evidence."
        ),
    }

    out_path = Path(args.out) if args.out else EVIDENCE_DIR / f"{sha}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence written: {out_path}")

    gate_problems = []
    if accounting["reconciles"] is not True:
        gate_problems.append("reconciliation mismatch")
    if accounting["collection_errors"] or accounting["session_errors"]:
        gate_problems.append("collection/session errors")
    if accounting["xpassed_nodes"]:
        gate_problems.append("unexpected xpasses")
    if wheel["status"] in ("FAIL", "TIMEOUT"):
        gate_problems.append(f"wheel qualification {wheel['status']}")
    if gate_problems:
        print("EVIDENCE WRITTEN BUT GATE FAILED: " + "; ".join(gate_problems))
        return 2

    suite_failures = accounting["outcomes"]["failed"] + accounting["outcomes"]["errors"]
    if suite_failures > 0 or pytest_exit != 0:
        print("EVIDENCE WRITTEN; SUITE NOT GREEN (recorded for the release authority)")
        return 1
    print("QUALIFICATION EVIDENCE GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
