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
        (sys.executable, "scripts/validate-release-scope.py"),
        (sys.executable, "scripts/verify_vendored_contract.py"),
        (sys.executable, "-m", "ruff", "check", "src", "tests"),
        (sys.executable, "-m", "pytest", "tests", "-q", "--tb=no"),
    )


def test_focused_check_scopes_ruff_to_changed_python_paths() -> None:
    module = _load_check_module()

    commands = module.commands_for(
        skip_pytest=True,
        ruff_paths=("tests/test_check_script.py",),
    )

    assert (
        sys.executable,
        "-m",
        "ruff",
        "check",
        "tests/test_check_script.py",
    ) in commands
    assert (sys.executable, "-m", "ruff", "check", "src", "tests") not in commands
    assert not any(
        len(command) > 2 and command[1:3] == ("-m", "pytest")
        for command in commands
    )


def test_focused_check_can_skip_ruff_when_no_python_files_changed() -> None:
    module = _load_check_module()

    commands = module.commands_for(skip_pytest=True, ruff_paths=())

    assert not any(
        len(command) >= 4 and command[1:4] == ("-m", "ruff", "check")
        for command in commands
    )


def test_readme_uses_single_standard_check_command() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "python scripts/check.py" in readme


def test_github_actions_uses_focused_standard_check_command() -> None:
    workflow_path = ROOT / ".github" / "workflows" / "validation.yml"
    assert workflow_path.exists(), ".github/workflows/validation.yml must exist"

    workflow = workflow_path.read_text(encoding="utf-8")

    assert 'python-version: "3.12"' in workflow
    assert "matrix.python-version" not in workflow
    assert 'python -m pip install -e ".[dev]"' in workflow
    assert "python -m pytest -q $FOCUSED_TESTS --tb=short" in workflow
    assert "python scripts/check.py --skip-pytest --ruff-paths $RUFF_PATHS" in workflow
    assert "windows-latest" not in workflow
    assert "scripts/release_evidence.py" not in workflow
    assert "validate-artifact.py" not in workflow


def test_readme_documents_ci_standard_check_command() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "CI runs the same verification entrypoint" in readme
    assert "python scripts/check.py --skip-pytest" in readme


def test_regressions_yaml_exists() -> None:
    """Check that REGRESSIONS.yaml exists in the test fixtures directory."""
    regressions_path = ROOT / "tests" / "fixtures" / "REGRESSIONS.yaml"
    assert regressions_path.exists(), "REGRESSIONS.yaml must exist for validator regression tracking"

    import yaml

    data = yaml.safe_load(regressions_path.read_bytes())
    assert isinstance(data, dict), "REGRESSIONS.yaml must contain a mapping"
    assert "excluded_validators" in data, "REGRESSIONS.yaml must have excluded_validators key"
    assert "required_cases" in data, "REGRESSIONS.yaml must have required_cases key"
