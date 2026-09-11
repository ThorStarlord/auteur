#!/usr/bin/env python
"""Run the hermetic V1 author-journey qualification bundle and record evidence."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from auteur import __version__


_TESTS = [
    "tests/test_beginner_decision_golden_path.py",
    "tests/test_guided_author_workspace.py",
    "tests/test_v1_expression_boundary.py",
    "tests/test_revision_recovery_v1.py",
    "tests/test_llm_failure_contract.py",
    "tests/test_v1_book_scale_topology.py",
    "tests/test_publish_release.py",
]


def _candidate_sha() -> str:
    value = os.environ.get("GITHUB_SHA")
    if value:
        return value
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".auteur/qualification/v1-author-journey.json"),
    )
    args = parser.parse_args()
    command = [sys.executable, "-m", "pytest", "-q", *_TESTS]
    started = datetime.now(timezone.utc).isoformat()
    print("V1 hermetic author-journey qualification")
    print("Command: " + " ".join(command))
    completed = subprocess.run(command, check=False)
    evidence: dict[str, Any] = {
        "schema_version": "auteur-v1-hermetic-author-journey-v1",
        "candidate_sha": _candidate_sha(),
        "package_version": __version__,
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "tests": _TESTS,
        "exit_code": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "claim_scope": (
            "hermetic repository author-journey integration; excludes live-provider "
            "availability and subjective literary quality"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
