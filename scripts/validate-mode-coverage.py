"""Self-validating mode coverage tracker.

Validates docs/mode-coverage.yaml for internal consistency:
  - Each listed run_log_path exists on disk
  - Each run log passes validate-run-log.py validation
  - steps_completed matches actual counted steps in the log
  - validators_exercised match the log's validator_stack entries
  - repeatable_boundaries_detected matches the failure ledger
  - system_tools references point to existing files
  - All artifact IDs claimed as validated exist in artifact-contracts.yaml

Usage:
    python scripts/validate-mode-coverage.py [--repo-root PATH]
    python scripts/validate-mode-coverage.py --list-codes
"""

import os
import re
import sys
import json
import subprocess
import argparse

from _validator_utils import format_error, load_yaml, load_artifact_contracts

# Stable error codes
COVERAGE_FILE_NOT_FOUND = "COVERAGE_FILE_NOT_FOUND"
COVERAGE_YAML_INVALID = "COVERAGE_YAML_INVALID"
MISSING_MODE_KEY = "MISSING_MODE_KEY"
RUN_LOG_NOT_FOUND = "RUN_LOG_NOT_FOUND"
RUN_LOG_VALIDATION_FAILED = "RUN_LOG_VALIDATION_FAILED"
STEPS_COMPLETED_MISMATCH = "STEPS_COMPLETED_MISMATCH"
STEPS_TOTAL_MISMATCH = "STEPS_TOTAL_MISMATCH"
VALIDATOR_EXERCISED_MISMATCH = "VALIDATOR_EXERCISED_MISMATCH"
GATE_COUNT_MISMATCH = "GATE_COUNT_MISMATCH"
REPEATABLE_BOUNDARY_MISMATCH = "REPEATABLE_BOUNDARY_MISMATCH"
SYSTEM_TOOL_NOT_FOUND = "SYSTEM_TOOL_NOT_FOUND"
ARTIFACT_NOT_IN_CONTRACTS = "ARTIFACT_NOT_IN_CONTRACTS"
MISSING_WORKFLOW_ID = "MISSING_WORKFLOW_ID"
MISSING_LAST_RUN = "MISSING_LAST_RUN"
MISSING_STEPS_COMPLETED = "MISSING_STEPS_COMPLETED"
MISSING_STEPS_TOTAL = "MISSING_STEPS_TOTAL"


def _resolve_run_log_path(path_spec: str, repo_root: str) -> str | None:
    """Resolve a run_log_path entry (may contain a parenthetical note)."""
    # Strip trailing notes like "(feature branch ...)" or "(yolo_execution)"
    clean = re.sub(r"\s*\(.*?\)\s*$", "", path_spec).strip()
    candidate = os.path.join(repo_root, clean)
    if os.path.exists(candidate):
        return candidate
    # Try relative to repo root directly
    candidate2 = os.path.join(repo_root, clean.lstrip("/"))
    if os.path.exists(candidate2):
        return candidate2
    return None


def _count_steps_in_run_log(filepath: str) -> int | None:
    """Count the number of Step entries in a run log markdown file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        steps = re.findall(r"^### Step\s+\d+", content, re.MULTILINE)
        return len(steps)
    except Exception:
        return None


def _extract_validator_names_from_log(filepath: str) -> list[str]:
    """Extract validator display names from a run log (all sections)."""
    names = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # Match all validate-X.py references anywhere in the log
        for m in re.finditer(r"(validate-[\w-]+\.py)", content):
            fname = m.group(1)
            if fname not in names:
                names.append(fname)
    except Exception:
        pass
    return sorted(names)


def _run_log_validates(filepath: str, repo_root: str) -> tuple[bool, str]:
    """Run validate-run-log.py against a log file. Returns (passed, output)."""
    validator = os.path.join(repo_root, "scripts", "validate-run-log.py")
    if not os.path.exists(validator):
        return False, "validate-run-log.py not found"
    result = subprocess.run(
        [sys.executable, validator, filepath, "--repo-root", repo_root],
        capture_output=True, text=True, timeout=30,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output[:500] if result.returncode != 0 else ""


def _get_failure_ledger_repeatable_count(repo_root: str) -> int | None:
    """Run analyze-run-failures.py --json and extract repeatable count."""
    analyzer = os.path.join(repo_root, "scripts", "analyze-run-failures.py")
    if not os.path.exists(analyzer):
        return None
    result = subprocess.run(
        [sys.executable, analyzer, "--logs-dir",
         os.path.join(repo_root, "artifacts"), "--json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode > 2:
        return None
    try:
        data = json.loads(result.stdout)
        return len(data.get("repeatable_failures", {}))
    except (json.JSONDecodeError, KeyError):
        return None


def validate_mode_coverage(repo_root: str = ".") -> list[str]:
    """Validate docs/mode-coverage.yaml for internal consistency."""
    errors: list[str] = []

    coverage_path = os.path.join(repo_root, "docs", "mode-coverage.yaml")
    if not os.path.exists(coverage_path):
        errors.append(
            format_error(COVERAGE_FILE_NOT_FOUND, f"mode-coverage.yaml not found: {coverage_path}")
        )
        return errors

    coverage = load_yaml(coverage_path)
    if coverage is None:
        errors.append(format_error(COVERAGE_YAML_INVALID, "mode-coverage.yaml is empty or unparseable"))
        return errors

    mode_entries = coverage.get("mode_coverage", [])
    if not mode_entries:
        errors.append(format_error(COVERAGE_YAML_INVALID, "mode_coverage list is empty or missing"))

    # Build a set of known artifact IDs from contracts
    contracts = load_artifact_contracts(repo_root)
    known_artifact_ids: set[str] = set()
    if contracts:
        known_artifact_ids = {a["id"] for a in contracts.get("artifacts", [])}

    # ── Validate each mode entry ──────────────────────────────────────
    for entry in mode_entries:
        mode = entry.get("mode", "?")
        workflow = entry.get("workflow_id", "?")
        label = f"{mode}/{workflow}"

        # Required fields
        if not entry.get("mode"):
            errors.append(format_error(MISSING_MODE_KEY, f"Entry missing 'mode': {entry}"))
        if not entry.get("workflow_id"):
            errors.append(format_error(MISSING_WORKFLOW_ID, f"Entry '{mode}' missing 'workflow_id'"))

        if not entry.get("last_run"):
            errors.append(format_error(MISSING_LAST_RUN, f"Entry '{label}' missing 'last_run'"))

        steps_completed = entry.get("steps_completed")
        if steps_completed is None:
            errors.append(format_error(MISSING_STEPS_COMPLETED, f"Entry '{label}' missing 'steps_completed'"))

        steps_total = entry.get("steps_total")
        if steps_total is None:
            errors.append(format_error(MISSING_STEPS_TOTAL, f"Entry '{label}' missing 'steps_total'"))

        # ── Run log path exists ───────────────────────────────────────
        path_spec = entry.get("run_log_path", "")
        if not path_spec:
            errors.append(format_error(RUN_LOG_NOT_FOUND, f"Entry '{label}' missing 'run_log_path'"))
            continue

        resolved = _resolve_run_log_path(str(path_spec), repo_root)
        if resolved is None:
            errors.append(
                format_error(RUN_LOG_NOT_FOUND, f"Entry '{label}' run_log_path not found: {path_spec}")
            )
            continue

        # ── Run log validates ─────────────────────────────────────────
        log_valid, log_output = _run_log_validates(resolved, repo_root)
        if not log_valid:
            errors.append(
                format_error(
                    RUN_LOG_VALIDATION_FAILED,
                    f"Entry '{label}' run log failed validation:\n{log_output}",
                )
            )

        # ── Steps completed matches log ───────────────────────────────
        actual_steps = _count_steps_in_run_log(resolved)
        if actual_steps is not None and steps_completed is not None:
            if actual_steps != steps_completed:
                errors.append(
                    format_error(
                        STEPS_COMPLETED_MISMATCH,
                        f"Entry '{label}' declares steps_completed={steps_completed} "
                        f"but run log has {actual_steps} steps",
                    )
                )

            # ── Steps total consistency ───────────────────────
            if steps_total is not None and steps_completed > steps_total:
                errors.append(
                    format_error(
                        STEPS_TOTAL_MISMATCH,
                        f"Entry '{label}' steps_completed={steps_completed} > "
                        f"steps_total={steps_total}",
                    )
                )

        # ── Validators exercised match log ────────────────────────────
        raw_validators = entry.get("validators_exercised", [])
        if raw_validators:
            log_validators = set(_extract_validator_names_from_log(resolved))
            # Normalize: entries may be strings like "level_2: validate-artifact.py (brief)"
            # or dicts like {"level_2": "validate-artifact.py (brief)"}
            claimed_basenames = set()
            for v in raw_validators:
                # Dict case (YAML parses "level_X: name" as key: value)
                if isinstance(v, dict):
                    for val in v.values():
                        for name in re.findall(r"validate-[\w-]+\.py", str(val)):
                            claimed_basenames.add(name)
                # String case
                elif isinstance(v, str):
                    for name in re.findall(r"validate-[\w-]+\.py", v):
                        claimed_basenames.add(name)

            # Check each claimed validator appears in log
            for claimed in claimed_basenames:
                if claimed not in log_validators:
                    errors.append(
                        format_error(
                            VALIDATOR_EXERCISED_MISMATCH,
                            f"Entry '{label}' claims validator '{claimed}' "
                            f"but it was not found in the run log's validator_stack. "
                            f"Found: {sorted(log_validators)}",
                        )
                    )

            # Check if log has validators not claimed (informational only -
            # narrative text in Gates, Decisions, and cross-check tables
            # may mention validators not listed as exercised)
            unclaimed = log_validators - claimed_basenames
            if unclaimed:
                print(
                    f"INFO: Entry '{label}' log mentions validators "
                    f"{sorted(unclaimed)} not in validators_exercised "
                    f"(likely from narrative text, not step-level invocation)"
                )

        # ── Gate count consistency ────────────────────────────────────
        gates_note = entry.get("gates_note", "")
        claimed_gates = entry.get("gates_exercised", False)
        if claimed_gates:
            # Count gate_result entries in the run log (gates are inline within steps)
            try:
                with open(resolved, "r", encoding="utf-8") as f:
                    log_content = f.read()
                gate_results = re.findall(
                    r"\*?\*?gate_result\*?\*?:\s*\S+", log_content
                )
                if not gate_results:
                    errors.append(
                        format_error(
                            GATE_COUNT_MISMATCH,
                            f"Entry '{label}' claims gates_exercised=true "
                            f"but no gate_result entries found in run log",
                        )
                    )
            except Exception:
                pass

    # ── Validate system_tools ─────────────────────────────────────────
    system_tools = coverage.get("system_tools", [])
    for tool_entry in system_tools:
        tool_name = tool_entry.get("tool", "?")
        run_logs = tool_entry.get("run_logs_validated", [])
        for rl_spec in run_logs:
            # Strip trailing parenthetical like "(yolo_execution)"
            resolved = _resolve_run_log_path(str(rl_spec), repo_root)
            if resolved is None:
                errors.append(
                    format_error(
                        RUN_LOG_NOT_FOUND,
                        f"system_tool '{tool_name}' references non-existent log: {rl_spec}",
                    )
                )

        # Validate output.py artifacts claims
        if tool_name == "validate-output.py":
            validated_artifacts = tool_entry.get("artifacts_validated", [])
            for art_id in validated_artifacts:
                if known_artifact_ids and art_id not in known_artifact_ids:
                    errors.append(
                        format_error(
                            ARTIFACT_NOT_IN_CONTRACTS,
                            f"validate-output.py claims to have validated '{art_id}' "
                            f"but no contract exists for it in artifact-contracts.yaml. "
                            f"Known: {sorted(known_artifact_ids)}",
                        )
                    )

    # ── Validate validator_live_coverage references exist on disk ─────
    live_coverage = coverage.get("validator_live_coverage", {})
    for val_key, val_data in live_coverage.items():
        fixture_tested = val_data.get("fixture_tested", False)
        if fixture_tested and fixture_tested != "excluded":
            # Convert key like "validate_repo_py" -> "validate-repo.py"
            # Strip trailing "_py", then replace remaining "_" with "-"
            base_name = val_key
            if base_name.endswith("_py"):
                base_name = base_name[:-3]
            script_name = base_name.replace("_", "-") + ".py"
            script_path = os.path.join(repo_root, "scripts", script_name)
            if not os.path.exists(script_path):
                errors.append(
                    format_error(
                        SYSTEM_TOOL_NOT_FOUND,
                        f"validator_live_coverage references '{val_key}' -> "
                        f"expected '{script_name}' but not found in scripts/",
                    )
                )

    # ── Cross-check: repeatable_boundaries_detected vs failure ledger ─
    ledger_repeatable = _get_failure_ledger_repeatable_count(repo_root)
    if ledger_repeatable is not None:
        for entry in mode_entries:
            hardening = entry.get("hardening_triggered", "none")
            mode_name = entry.get("mode", "?")
            # If the ledger says we have repeatable boundaries but a mode claims "none",
            # that's only a problem if the mode actually contributed failures
            if hardening == "none" and ledger_repeatable > 0:
                # Only flag if this mode's run log actually exists and has failures
                path_spec = entry.get("run_log_path", "")
                if path_spec:
                    resolved = _resolve_run_log_path(str(path_spec), repo_root)
                    if resolved:
                        try:
                            with open(resolved, "r", encoding="utf-8") as f:
                                content = f.read()
                            if "FAILED" in content or "TDD Cycle" in content:
                                errors.append(
                                    format_error(
                                        REPEATABLE_BOUNDARY_MISMATCH,
                                        f"Entry '{mode_name}' says hardening_triggered=none "
                                        f"but failure ledger reports {ledger_repeatable} "
                                        f"repeatable boundary(ies). Cross-check run log: "
                                        f"'{path_spec}' contains failures.",
                                    )
                                )
                        except Exception:
                            pass

        # Also check the system_tools.analyze-run-failures claim
        for tool_entry in system_tools:
            if tool_entry.get("tool") == "analyze-run-failures.py":
                declared_rb = tool_entry.get("repeatable_boundaries_detected", 0)
                if declared_rb != ledger_repeatable:
                    errors.append(
                        format_error(
                            REPEATABLE_BOUNDARY_MISMATCH,
                            f"analyze-run-failures.py declares "
                            f"repeatable_boundaries_detected={declared_rb} "
                            f"but current failure ledger says {ledger_repeatable}. "
                            f"Update mode-coverage.yaml to match the live ledger.",
                        )
                    )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Self-validating mode coverage tracker for docs/mode-coverage.yaml"
    )
    parser.add_argument("--repo-root", default=".", help="Root directory of the repository")
    parser.add_argument("--list-codes", action="store_true", help="List all error codes and exit")
    args = parser.parse_args(argv)

    if args.list_codes:
        codes = [
            COVERAGE_FILE_NOT_FOUND, COVERAGE_YAML_INVALID, MISSING_MODE_KEY,
            RUN_LOG_NOT_FOUND, RUN_LOG_VALIDATION_FAILED, STEPS_COMPLETED_MISMATCH,
            STEPS_TOTAL_MISMATCH, VALIDATOR_EXERCISED_MISMATCH, GATE_COUNT_MISMATCH,
            REPEATABLE_BOUNDARY_MISMATCH, SYSTEM_TOOL_NOT_FOUND, ARTIFACT_NOT_IN_CONTRACTS,
            MISSING_WORKFLOW_ID, MISSING_LAST_RUN, MISSING_STEPS_COMPLETED, MISSING_STEPS_TOTAL,
        ]
        print("Stable error codes for mode-coverage validation:")
        for code in codes:
            print(f"  {code}")
        return 0

    errs = validate_mode_coverage(args.repo_root)
    if errs:
        for e in errs:
            print(f"ERROR {e}")
        return 1
    else:
        print("Mode coverage validation passed! All entries are internally consistent.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
