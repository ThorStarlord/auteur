from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROHIBITED_FILE_URL = "file" + ":///"


def _load_suite_module():
    module_path = ROOT / "scripts" / "test-validators.py"
    assert module_path.exists(), "scripts/test-validators.py must exist"

    spec = importlib.util.spec_from_file_location("test_validators", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_clean_repo(root: Path) -> None:
    (root / "README.md").write_text("clean repository contract\n", encoding="utf-8")
    references = root / "docs" / "references"
    references.mkdir(parents=True)
    for name in ["repo-analysis-template.md", "weakness-types.md", "evidence-rules.md"]:
        (references / name).write_text("ok\n", encoding="utf-8")


def _write_case(fixture_dir: Path, data: dict[str, object]) -> None:
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "case.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )


def test_validate_repo_hyphen_wrapper_accepts_explicit_fixture_root(tmp_path: Path) -> None:
    _write_clean_repo(tmp_path)

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate-repo.py"), str(tmp_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Repository contract checks passed." in result.stdout


def test_validator_suite_passes_current_fixture_baseline() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "test-validators.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "# Validator Verification Suite Report" in result.stdout
    assert "validate-repo" in result.stdout
    assert "stale-readme-claim" in result.stdout
    assert PROHIBITED_FILE_URL not in result.stdout


def test_validator_suite_write_report_is_explicit(tmp_path: Path) -> None:
    report_path = tmp_path / "validator-report.md"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "test-validators.py"),
            "--write-report",
            str(report_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert report_path.exists()
    report = report_path.read_text(encoding="utf-8")
    assert "# Validator Verification Suite Report" in report
    assert PROHIBITED_FILE_URL not in report


def test_suite_fails_when_negative_case_lacks_expected_error(tmp_path: Path) -> None:
    fixtures_root = tmp_path / "fixtures"
    fixture_dir = fixtures_root / "validate-repo" / "invalid" / "missing-error"
    _write_case(
        fixture_dir,
        {
            "id": "missing-error",
            "validator": "validate-repo",
            "validator_case": "negative",
            "expected_exit_code": 1,
            "root_arg": ".",
        },
    )
    (fixtures_root / "REGRESSIONS.yaml").write_text("required_cases: []\n", encoding="utf-8")

    module = _load_suite_module()
    result = module.run_suite(repo_root=ROOT, fixtures_root=fixtures_root)

    assert result.exit_code == 1
    assert "missing expected_error_contains" in result.report


def test_suite_rejects_file_url_in_fixture_content(tmp_path: Path) -> None:
    fixtures_root = tmp_path / "fixtures"
    fixture_dir = fixtures_root / "validate-repo" / "valid" / "file-url"
    _write_case(
        fixture_dir,
        {
            "id": "file-url",
            "validator": "validate-repo",
            "validator_case": "positive",
            "expected_exit_code": 0,
            "expected_output_contains": "Repository contract checks passed.",
            "root_arg": ".",
        },
    )
    (fixture_dir / "README.md").write_text(
        f"see {PROHIBITED_FILE_URL}tmp/example\n",
        encoding="utf-8",
    )
    (fixtures_root / "REGRESSIONS.yaml").write_text("required_cases: []\n", encoding="utf-8")

    module = _load_suite_module()
    result = module.run_suite(repo_root=ROOT, fixtures_root=fixtures_root)

    assert result.exit_code == 1
    assert PROHIBITED_FILE_URL in result.report


def test_suite_requires_declared_regression_cases(tmp_path: Path) -> None:
    fixtures_root = tmp_path / "fixtures"
    (fixtures_root).mkdir(parents=True)
    (fixtures_root / "REGRESSIONS.yaml").write_text(
        yaml.safe_dump(
            {
                "required_cases": [
                    {
                        "id": "stale-readme-claim",
                        "validator": "validate-repo",
                        "fixture": "tests/fixtures/validate-repo/invalid/stale-readme",
                        "reason": "Prevent stale README claims from passing.",
                    }
                ],
                "excluded_validators": [],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    module = _load_suite_module()
    result = module.run_suite(repo_root=ROOT, fixtures_root=fixtures_root)

    assert result.exit_code == 1
    assert "Missing required case: stale-readme-claim" in result.report
