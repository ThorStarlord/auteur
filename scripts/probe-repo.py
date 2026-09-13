"""Emit deterministic, machine-readable repository qualification metrics.

This probe is intentionally observational. It does not modify the repository,
install dependencies, or infer product quality from heuristics.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        return ""
    return result.stdout.strip()


def _files(root: Path, pattern: str) -> list[Path]:
    return sorted(path for path in root.glob(pattern) if path.is_file())


def build_report(root: Path) -> dict[str, object]:
    sha = _git(root, "rev-parse", "HEAD")
    tracked = _git(root, "ls-files").splitlines() if sha else []
    untracked = (
        _git(root, "ls-files", "--others", "--exclude-standard").splitlines()
        if sha
        else []
    )
    dirty = _git(root, "status", "--porcelain").splitlines() if sha else []
    ignored = (
        _git(root, "ls-files", "--others", "--ignored", "--exclude-standard").splitlines()
        if sha
        else []
    )
    test_files = _files(root, "tests/**/*.py")
    validators = _files(root, "scripts/validate-*.py")
    workflow = root / ".github" / "workflows" / "validation.yml"
    declared_checks = [
        str(path.relative_to(root)).replace("\\", "/")
        for path in (
            root / "scripts" / "check.py",
            root / "scripts" / "release_evidence.py",
            root / "scripts" / "verify_wheel.py",
        )
        if path.is_file()
    ]
    declared_in_ci = []
    if workflow.is_file():
        workflow_text = workflow.read_text(encoding="utf-8")
        declared_in_ci = [
            line.strip()[4:].strip()
            for line in workflow_text.splitlines()
            if line.strip().startswith("run:")
        ]

    return {
        "schema_version": 1,
        "probe_tool": "auteur probe-repo v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "repo_root": str(root),
        "git_state": {
            "is_git_repo": bool(sha),
            "branch": _git(root, "branch", "--show-current") if sha else "",
            "head_sha": sha,
            "tracked_file_count": len(tracked),
            "untracked_file_count": len(untracked),
            "dirty_file_count": len(dirty),
        },
        "verification_gap": {
            "declared_checks": declared_checks,
            "declared_in_ci": declared_in_ci,
            "enforced_checks": ["pytest", "ruff", "scripts/check.py"],
            "vg": 0.0 if declared_in_ci else 1.0,
            "notes": "Counts describe repository declarations; execution evidence is recorded separately.",
        },
        "context_entropy": {
            "tracked_volume": len(tracked),
            "untracked_volume": len(untracked),
            "ignored_present_volume": len(ignored),
            "ce": float(len(untracked) + len(ignored)),
            "notes": "This probe reports volume only; it does not assign a subjective entropy score.",
        },
        "test_collection": {
            "test_file_count": len(test_files),
            "pytest_config_present": (root / "pyproject.toml").is_file(),
        },
        "fixtures_coverage": {
            "total_validators": len(validators),
            "covered_validators": 0,
            "missing_fixtures": [],
            "coverage": None,
            "notes": "Validator-to-fixture coverage requires semantic review and is not guessed by filename.",
        },
        "churn": {
            "commits_scanned": 0,
            "changed_files_last_n": 0,
            "top_changed_files": [],
            "notes": "Churn is omitted unless an explicit history window is requested.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    payload = json.dumps(build_report(root), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.resolve().write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
