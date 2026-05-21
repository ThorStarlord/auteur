from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_check_module():
    module_path = ROOT / "scripts" / "check.py"
    assert module_path.exists(), "scripts/check.py must exist"

    spec = importlib.util.spec_from_file_location("check_script", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_check_script_runs_validator_suite_before_repo_validator_and_pytest() -> None:
    module = _load_check_module()

    assert module.CHECK_COMMANDS == (
        (sys.executable, "scripts/test-validators.py"),
        (sys.executable, "scripts/validate-repo.py"),
        (sys.executable, "-m", "pytest", "tests", "-q", "--tb=no"),
    )


def test_readme_uses_single_standard_check_command() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "python scripts/check.py" in readme


def test_github_actions_runs_standard_check_command() -> None:
    workflow_path = ROOT / ".github" / "workflows" / "validation.yml"
    assert workflow_path.exists(), ".github/workflows/validation.yml must exist"

    workflow = workflow_path.read_text(encoding="utf-8")

    assert 'python-version: "3.11"' in workflow
    assert 'python -m pip install -e ".[dev]"' in workflow
    assert "python scripts/check.py" in workflow
    assert "validate-artifact.py" not in workflow


def test_readme_documents_ci_standard_check_command() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "CI runs the same verification entrypoint: `python scripts/check.py`." in readme


def test_regressions_yaml_exists() -> None:
    """Check that REGRESSIONS.yaml exists in the test fixtures directory."""
    regressions_path = ROOT / "tests" / "fixtures" / "REGRESSIONS.yaml"
    assert regressions_path.exists(), "REGRESSIONS.yaml must exist for validator regression tracking"

    import yaml
    data = yaml.safe_load(regressions_path.read_bytes())
    assert isinstance(data, dict), "REGRESSIONS.yaml must contain a mapping"
    assert "excluded_validators" in data, "REGRESSIONS.yaml must have excluded_validators key"
    assert "required_cases" in data, "REGRESSIONS.yaml must have required_cases key"


def test_validate_repo_has_severity_split() -> None:
    """validate-repo.py should separate critical errors from warnings and exit accordingly."""
    import subprocess
    import tempfile
    # Test 1: With current repo state (only warnings), exit should be 0
    result = subprocess.run(
        [sys.executable, "scripts/validate-repo.py"],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, "should exit 0 when only warnings exist"
    assert "Validation warnings" in result.stdout
    assert "Validation errors" not in result.stdout

    # Test 2: Simulate a critical error by using a temp dir with no core files
    with tempfile.TemporaryDirectory() as tmpdir:
        critical_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate-repo.py")],
            cwd=tmpdir, capture_output=True, text=True
        )
        # When running from empty dir, core files are missing -> critical errors
        assert critical_result.returncode != 0, "should exit non-zero when critical errors exist"
        assert "Validation errors" in critical_result.stdout or "Missing core file" in critical_result.stdout