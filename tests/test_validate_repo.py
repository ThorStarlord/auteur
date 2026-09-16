from __future__ import annotations

import subprocess
import sys
import tempfile
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_repo_validator():
    spec = importlib.util.spec_from_file_location("validate_repo", ROOT / "scripts" / "validate-repo.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

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


def test_root_package_manifest_is_allowed_but_derived_report_is_rejected(tmp_path: Path) -> None:
    validator = _load_repo_validator()
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    assert validator.root_level_derived_json_files(str(tmp_path)) == []
    (tmp_path / "report.json").write_text("{}", encoding="utf-8")
    assert validator.root_level_derived_json_files(str(tmp_path)) == ["report.json"]
