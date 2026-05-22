from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_validate_repo_exits_nonzero_on_errors() -> None:
    """validate-repo.py should exit non-zero when critical validation errors exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        critical_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate-repo.py")],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        # When running from empty dir, core files are missing -> critical errors
        assert critical_result.returncode != 0, "should exit non-zero when critical errors exist"
        assert "Validation errors" in critical_result.stdout or "Missing core file" in critical_result.stdout

def test_validate_repo_warnings_only_exits_zero() -> None:
    """validate-repo.py should exit 0 when no critical validation errors exist."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate-repo.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, "should exit 0 when no critical errors exist"
    assert "Validation errors" not in result.stdout

