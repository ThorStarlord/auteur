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

    assert "python-version: \"3.11\"" in workflow
    assert "python -m pip install -e \".[dev]\"" in workflow
    assert "python scripts/check.py" in workflow
    assert "validate-artifact.py" not in workflow


def test_readme_documents_ci_standard_check_command() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "CI runs the same verification entrypoint: `python scripts/check.py`." in readme
