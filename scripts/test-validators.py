from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any, NamedTuple

import yaml


PROHIBITED_FILE_URL = "file" + ":///"


class SuiteResult(NamedTuple):
    exit_code: int
    report: str


class ValidatorCase(NamedTuple):
    id: str
    validator: str
    case_type: str
    expected_exit_code: int
    fixture_dir: Path
    case_path: Path
    expected_output_contains: str | None
    expected_error_contains: str | None
    root_arg: str | None
    validator_args: tuple[str, ...]
    cwd: str | None


class CaseResult(NamedTuple):
    case: ValidatorCase
    passed: bool
    expected_exit_code: int | None
    actual_exit_code: int | None
    message: str


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def _discover_cases(fixtures_root: Path) -> tuple[list[ValidatorCase], list[str]]:
    cases: list[ValidatorCase] = []
    failures: list[str] = []

    for case_path in sorted(fixtures_root.rglob("case.yaml")):
        try:
            data = _read_yaml(case_path)
        except Exception as exc:
            failures.append(f"{case_path}: invalid case metadata: {exc}")
            continue

        missing = [
            key
            for key in ["id", "validator", "validator_case", "expected_exit_code"]
            if key not in data
        ]
        if missing:
            failures.append(f"{case_path}: missing required metadata: {', '.join(missing)}")
            continue

        case_type = str(data["validator_case"])
        expected_exit_code = int(data["expected_exit_code"])
        expected_error = data.get("expected_error_contains")
        expected_output = data.get("expected_output_contains")

        if case_type not in {"positive", "negative"}:
            failures.append(f"{case_path}: validator_case must be positive or negative")
            continue
        if case_type == "positive" and expected_exit_code != 0:
            failures.append(f"{case_path}: positive cases must expect exit code 0")
            continue
        if case_type == "negative" and expected_exit_code == 0:
            failures.append(f"{case_path}: negative cases must expect a nonzero exit code")
            continue
        if case_type == "negative" and not expected_error:
            failures.append(f"{case_path}: negative case missing expected_error_contains")
            continue

        raw_args = data.get("validator_args", [])
        if raw_args is None:
            raw_args = []
        if not isinstance(raw_args, list):
            failures.append(f"{case_path}: validator_args must be a list when present")
            continue

        cases.append(
            ValidatorCase(
                id=str(data["id"]),
                validator=str(data["validator"]),
                case_type=case_type,
                expected_exit_code=expected_exit_code,
                fixture_dir=case_path.parent,
                case_path=case_path,
                expected_output_contains=str(expected_output) if expected_output else None,
                expected_error_contains=str(expected_error) if expected_error else None,
                root_arg=str(data["root_arg"]) if data.get("root_arg") is not None else None,
                validator_args=tuple(str(arg) for arg in raw_args),
                cwd=str(data["cwd"]) if data.get("cwd") is not None else None,
            )
        )

    return cases, failures


def _check_file_url_hygiene(fixtures_root: Path, repo_root: Path) -> list[str]:
    failures: list[str] = []
    for path in sorted(p for p in fixtures_root.rglob("*") if p.is_file()):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if PROHIBITED_FILE_URL in text:
            failures.append(
                f"{_repo_relative(repo_root, path)} contains prohibited {PROHIBITED_FILE_URL} text"
            )
    return failures


def _load_required_cases(fixtures_root: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    registry_path = fixtures_root / "REGRESSIONS.yaml"
    if not registry_path.exists():
        return [], [], ["tests/fixtures/REGRESSIONS.yaml is missing"]

    try:
        data = _read_yaml(registry_path)
    except Exception as exc:
        return [], [], [f"tests/fixtures/REGRESSIONS.yaml is invalid: {exc}"]

    required = data.get("required_cases", [])
    excluded = data.get("excluded_validators", [])
    failures: list[str] = []

    if not isinstance(required, list):
        failures.append("REGRESSIONS.yaml required_cases must be a list")
        required = []
    if not isinstance(excluded, list):
        failures.append("REGRESSIONS.yaml excluded_validators must be a list")
        excluded = []

    return required, [str(item) for item in excluded], failures


def _known_validators(repo_root: Path) -> list[str]:
    return sorted(path.stem for path in (repo_root / "scripts").glob("validate-*.py"))


def _resolve_from_fixture(fixture_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (fixture_dir / path).resolve()


def _command_for_case(repo_root: Path, case: ValidatorCase) -> tuple[list[str], Path]:
    script_path = repo_root / "scripts" / f"{case.validator}.py"
    command = [sys.executable, str(script_path)]

    if case.root_arg is not None:
        command.append(str(_resolve_from_fixture(case.fixture_dir, case.root_arg)))
    elif case.validator == "validate-repo":
        command.append(str(case.fixture_dir))

    command.extend(case.validator_args)

    if case.cwd is None:
        cwd = repo_root
    else:
        cwd = _resolve_from_fixture(case.fixture_dir, case.cwd)

    return command, cwd


def _run_case(repo_root: Path, case: ValidatorCase) -> CaseResult:
    script_path = repo_root / "scripts" / f"{case.validator}.py"
    if not script_path.exists():
        return CaseResult(
            case,
            False,
            case.expected_exit_code,
            None,
            f"validator script missing: {_repo_relative(repo_root, script_path)}",
        )

    command, cwd = _command_for_case(repo_root, case)
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    output = completed.stdout + completed.stderr

    if completed.returncode != case.expected_exit_code:
        return CaseResult(
            case,
            False,
            case.expected_exit_code,
            completed.returncode,
            f"expected exit {case.expected_exit_code}, got {completed.returncode}",
        )

    if case.expected_output_contains and case.expected_output_contains not in output:
        return CaseResult(
            case,
            False,
            case.expected_exit_code,
            completed.returncode,
            f"missing expected output: {case.expected_output_contains}",
        )

    if case.expected_error_contains and case.expected_error_contains not in output:
        return CaseResult(
            case,
            False,
            case.expected_exit_code,
            completed.returncode,
            f"missing expected error: {case.expected_error_contains}",
        )

    return CaseResult(case, True, case.expected_exit_code, completed.returncode, "passed")


def _coverage_failures(
    repo_root: Path,
    fixtures_root: Path,
    cases: list[ValidatorCase],
    required_cases: list[dict[str, Any]],
    excluded_validators: list[str],
) -> list[str]:
    failures: list[str] = []
    case_ids = {case.id for case in cases}
    case_validators = {case.validator for case in cases}

    for required in required_cases:
        if not isinstance(required, dict):
            failures.append("REGRESSIONS.yaml required case entries must be mappings")
            continue
        required_id = str(required.get("id", ""))
        if required_id not in case_ids:
            failures.append(f"Missing required case: {required_id}")

    for validator in _known_validators(repo_root):
        if validator in excluded_validators:
            continue
        if validator not in case_validators:
            failures.append(f"Uncovered validator: {validator}")

    if not cases:
        failures.append(f"No validator fixture cases found under {_repo_relative(repo_root, fixtures_root)}")

    return failures


def _render_report(
    repo_root: Path,
    fixtures_root: Path,
    case_results: list[CaseResult],
    setup_failures: list[str],
) -> str:
    passed = sum(1 for result in case_results if result.passed)
    failed_cases = len(case_results) - passed
    total_failures = failed_cases + len(setup_failures)

    lines = [
        "# Validator Verification Suite Report",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Fixtures root | `{_repo_relative(repo_root, fixtures_root)}` |",
        f"| Cases checked | {len(case_results)} |",
        f"| Passed | {passed} |",
        f"| Failed cases | {failed_cases} |",
        f"| Setup failures | {len(setup_failures)} |",
        "",
        "## Cases",
        "",
        "| Case | Validator | Fixture | Expected | Actual | Result |",
        "|---|---|---|---:|---:|---|",
    ]

    for result in case_results:
        case = result.case
        actual = "" if result.actual_exit_code is None else str(result.actual_exit_code)
        status = "PASS" if result.passed else f"FAIL: {result.message}"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{case.id}`",
                    f"`{case.validator}`",
                    f"`{_repo_relative(repo_root, case.fixture_dir)}`",
                    str(case.expected_exit_code),
                    actual,
                    status,
                ]
            )
            + " |"
        )

    if total_failures:
        lines.extend(["", "## Failures", ""])
        for failure in setup_failures:
            lines.append(f"- {failure}")
        for result in case_results:
            if not result.passed:
                lines.append(f"- {result.case.id}: {result.message}")

    lines.append("")
    return "\n".join(lines)


def run_suite(
    repo_root: Path | None = None,
    fixtures_root: Path | None = None,
) -> SuiteResult:
    root = repo_root.resolve() if repo_root is not None else Path(__file__).resolve().parents[1]
    fixture_root = (
        fixtures_root.resolve() if fixtures_root is not None else root / "tests" / "fixtures"
    )

    setup_failures: list[str] = []
    if not fixture_root.exists():
        setup_failures.append(f"Fixture root missing: {_repo_relative(root, fixture_root)}")

    cases, discovery_failures = _discover_cases(fixture_root) if fixture_root.exists() else ([], [])
    setup_failures.extend(discovery_failures)

    required_cases, excluded_validators, registry_failures = _load_required_cases(fixture_root)
    setup_failures.extend(registry_failures)
    setup_failures.extend(_check_file_url_hygiene(fixture_root, root) if fixture_root.exists() else [])
    setup_failures.extend(
        _coverage_failures(root, fixture_root, cases, required_cases, excluded_validators)
    )

    case_results = [_run_case(root, case) for case in cases]
    report = _render_report(root, fixture_root, case_results, setup_failures)

    if PROHIBITED_FILE_URL in report and not any(
        PROHIBITED_FILE_URL in failure for failure in setup_failures
    ):
        setup_failures.append(f"Report contains prohibited {PROHIBITED_FILE_URL} text")
        report = _render_report(root, fixture_root, case_results, setup_failures)

    exit_code = 1 if setup_failures or any(not result.passed for result in case_results) else 0
    return SuiteResult(exit_code=exit_code, report=report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run validator fixtures and report evidence.")
    parser.add_argument(
        "--write-report",
        metavar="PATH",
        help="Write the Markdown report to PATH in addition to stdout.",
    )
    args = parser.parse_args(argv)

    result = run_suite()
    print(result.report, end="")

    if args.write_report:
        report_path = Path(args.write_report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(result.report, encoding="utf-8")

    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
