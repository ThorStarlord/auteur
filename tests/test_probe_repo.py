"""Qualification tests for the repository topology probe."""

import json
import subprocess
import sys
from pathlib import Path


def test_probe_repo_reports_reproducible_repository_metrics() -> None:
    root = Path(__file__).parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/probe-repo.py", "--repo-root", str(root)],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )

    report = json.loads(result.stdout)
    assert report["schema_version"] == 1
    assert report["git_state"]["is_git_repo"] is True
    assert report["git_state"]["head_sha"]
    assert report["test_collection"]["test_file_count"] > 0
    assert report["verification_gap"]["declared_checks"]
