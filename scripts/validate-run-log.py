"""Level 2+ validator for workflow run logs.

Validates run log artifacts against the run-log-template.md specification.
Checks header fields, sequence log structure, gate recording consistency,
pre-flight documentation, and path hygiene.

Usage:
    python scripts/validate-run-log.py <run_log_path> [--repo-root PATH]
    python scripts/validate-run-log.py --list-codes
"""

import os
import re
import sys
import yaml
import argparse

from _validator_utils import format_error, load_workflow_registry

# Stable error codes
FILE_NOT_FOUND = "FILE_NOT_FOUND"
MISSING_SESSION_ID = "MISSING_SESSION_ID"
MISSING_DATE = "MISSING_DATE"
MISSING_MODE = "MISSING_MODE"
UNKNOWN_MODE = "UNKNOWN_MODE"
MISSING_SEQUENCE_LOG = "MISSING_SEQUENCE_LOG"
MISSING_STEP_ID = "MISSING_STEP_ID"
MISSING_STEP_SKILL = "MISSING_STEP_SKILL"
MISSING_OUTPUT_ARTIFACT = "MISSING_OUTPUT_ARTIFACT"
MISSING_ARTIFACT_PATH = "MISSING_ARTIFACT_PATH"
MISSING_VALIDATOR_STACK = "MISSING_VALIDATOR_STACK"
MISSING_GATE = "MISSING_GATE"
MISSING_STEP_STATUS = "MISSING_STEP_STATUS"
MISSING_FINAL_STATE = "MISSING_FINAL_STATE"
ABSOLUTE_PATH_IN_LOG = "ABSOLUTE_PATH_IN_LOG"
GATE_APPROVED_NO_TIMESTAMP = "GATE_APPROVED_NO_TIMESTAMP"
GATE_APPROVED_NO_USER = "GATE_APPROVED_NO_USER"
GATE_DENIED_NO_RECORD = "GATE_DENIED_NO_RECORD"
GATE_BYPASS_NO_NOTE = "GATE_BYPASS_NO_NOTE"
VALIDATOR_RESULT_MISSING = "VALIDATOR_RESULT_MISSING"
PRE_FLIGHT_MISSING = "PRE_FLIGHT_MISSING"
MISSING_DECISIONS = "MISSING_DECISIONS"
MODE_MODE_MISMATCH = "MODE_MODE_MISMATCH"
BRANCH_NOT_RECORDED = "BRANCH_NOT_RECORDED"


def _parse_run_log(content: str) -> dict:
    """Parse a run log markdown file into structured sections."""
    result = {}

    # Extract header fields
    date_match = re.search(r"\*\*Date\*\*:\s*(\S+)", content)
    if date_match:
        result["date"] = date_match.group(1)

    session_match = re.search(r"\*\*Session ID\*\*:\s*(\S+)", content)
    if session_match:
        result["session_id"] = session_match.group(1)

    mode_match = re.search(r"\*\*Orchestrator Mode\*\*:\s*(\S+)", content)
    if mode_match:
        result["mode"] = mode_match.group(1)

    branch_match = re.search(r"\*\*Branch\*\*:\s*(\S+)", content)
    if branch_match:
        result["branch"] = branch_match.group(1)

    # Extract pre-flight section
    pre_flight = re.search(r"## Pre-flight(.*?)(?=##\s)", content, re.DOTALL)
    if pre_flight:
        result["has_pre_flight"] = True
        pf_text = pre_flight.group(1)
        result["pre_flight_checks"] = bool(re.search(r"PASSED", pf_text))
    else:
        result["has_pre_flight"] = False

    # Extract sequence log steps
    steps = []
    step_blocks = re.findall(
        r"### Step\s+(\d+)\s*\n(.*?)(?=###|\Z)", content, re.DOTALL
    )
    for step_id, step_body in step_blocks:
        step = {"step_id": step_id.strip()}

        skill_match = re.search(r"\*\*skill\*\*:\s*(.+)", step_body)
        if skill_match:
            step["skill"] = skill_match.group(1).strip()

        runtime_match = re.search(r"\*\*runtime\*\*:\s*(.+)", step_body)
        if runtime_match:
            step["runtime"] = runtime_match.group(1).strip()

        output_match = re.search(r"\*\*output_artifact\*\*:\s*(.+)", step_body)
        if output_match:
            step["output_artifact"] = output_match.group(1).strip()

        path_match = re.search(r"\*\*artifact_path\*\*:\s*(.+)", step_body)
        if path_match:
            step["artifact_path"] = path_match.group(1).strip()

        gate_match = re.search(r"\*\*gate\*\*:\s*(.+)", step_body)
        if gate_match:
            gate_text = gate_match.group(1).strip()
            step["gate"] = gate_text
            # Parse gate result if present on next lines
            gate_result = re.search(
                r"\*\*gate\*\*:.*?\n\s*[-*]\s+gate_result:\s*(.+)",
                step_body, re.DOTALL
            )
            if gate_result:
                step["gate_result"] = gate_result.group(1).strip()
            approved_at = re.search(r"approved_at:\s*(.+)", step_body)
            if approved_at:
                step["approved_at"] = approved_at.group(1).strip()
            approved_by = re.search(r"approved_by:\s*(.+)", step_body)
            if approved_by:
                step["approved_by"] = approved_by.group(1).strip()

        status_match = re.search(r"\*\*status\*\*:\s*(.+)", step_body)
        if status_match:
            step["status"] = status_match.group(1).strip()

        # Validator stack
        vstack = re.findall(
            r"level:\s*(.+?)\s*\n\s*command:\s*(.+?)\s*\n\s*result:\s*(.+)",
            step_body
        )
        if vstack:
            step["validator_stack"] = [
                {"level": l, "command": c, "result": r}
                for l, c, r in vstack
            ]
        elif re.search(r"\*\*validator_stack\*\*:\s*none", step_body):
            step["validator_stack"] = "explicit_none"

        steps.append(step)

    result["steps"] = steps

    # Decisions & Overrides
    result["has_decisions"] = bool(
        re.search(r"## Decisions & Overrides", content)
    )

    # Final State
    result["has_final_state"] = bool(
        re.search(r"## Final State", content)
    )

    # TDD cycles
    tdd_cycles = re.findall(
        r"- \*\*RED\*\*:(.*?)- \*\*GREEN\*\*:(.*?)- \*\*REFACTOR\*\*:(.*?)(?=\n\n|\n###|$)",
        content, re.DOTALL
    )
    result["tdd_cycles"] = [
        {"red": r.strip(), "green": g.strip(), "refactor": f.strip()}
        for r, g, f in tdd_cycles
    ]

    return result


def validate_run_log(run_log_path: str, repo_root: str = ".") -> list[str]:
    """Validate a run log file against the template specification."""
    errors = []

    if not os.path.exists(run_log_path):
        errors.append(
            format_error(FILE_NOT_FOUND, f"Run log not found: {run_log_path}")
        )
        return errors

    with open(run_log_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Check absolute paths in the entire log
    if re.search(r"file:///", content):
        errors.append(
            format_error(
                ABSOLUTE_PATH_IN_LOG,
                "Absolute file:/// links are banned in run logs."
            )
        )

    # Check for Windows absolute paths (e.g., H:\\...) anywhere in the log
    if re.search(r"[A-Za-z]:[\\/]", content):
        errors.append(
            format_error(
                ABSOLUTE_PATH_IN_LOG,
                "Windows absolute paths (e.g., D:\\path) are banned in run logs."
            )
        )

    # 2. Parse the log
    log = _parse_run_log(content)

    # 3. Validate header fields
    if not log.get("date"):
        errors.append(format_error(MISSING_DATE, "Missing or unparseable Date header."))

    if not log.get("session_id"):
        errors.append(
            format_error(MISSING_SESSION_ID, "Missing or unparseable Session ID header.")
        )

    mode = log.get("mode")
    if not mode:
        errors.append(format_error(MISSING_MODE, "Missing Orchestrator Mode header."))
    else:
        valid_modes = {
            "plan_only", "prompt_chain", "guided_execution",
            "autonomous_execution", "yolo_execution"
        }
        if mode not in valid_modes:
            errors.append(
                format_error(
                    UNKNOWN_MODE,
                    f"Unknown mode '{mode}'. Valid: {sorted(valid_modes)}"
                )
            )

    # 4. Pre-flight check (required for mutating modes)
    if mode in ("yolo_execution", "autonomous_execution", "guided_execution"):
        if not log.get("has_pre_flight"):
            errors.append(
                format_error(
                    PRE_FLIGHT_MISSING,
                    f"Mode '{mode}' requires a Pre-flight section."
                )
            )
        elif not log.get("pre_flight_checks"):
            errors.append(
                format_error(
                    PRE_FLIGHT_MISSING,
                    "Pre-flight section exists but no PASSED checks found."
                )
            )

    # 5. Branch recording (required for mutating modes)
    branch = log.get("branch")
    if mode in ("yolo_execution", "autonomous_execution") and not branch:
        errors.append(
            format_error(
                BRANCH_NOT_RECORDED,
                f"Mode '{mode}' requires branch to be recorded."
            )
        )

    # 6. Validate each step
    steps = log.get("steps", [])
    if not steps:
        errors.append(
            format_error(MISSING_SEQUENCE_LOG, "No steps found in Sequence Log.")
        )

    for step in steps:
        sid = step.get("step_id", "?")

        if not step.get("skill"):
            errors.append(
                format_error(
                    MISSING_STEP_SKILL,
                    f"Step {sid} missing 'skill' field."
                )
            )

        if not step.get("output_artifact"):
            errors.append(
                format_error(
                    MISSING_OUTPUT_ARTIFACT,
                    f"Step {sid} missing 'output_artifact'."
                )
            )

        artifact_path = step.get("artifact_path", "")
        if not artifact_path:
            errors.append(
                format_error(
                    MISSING_ARTIFACT_PATH,
                    f"Step {sid} missing 'artifact_path'."
                )
            )
        elif artifact_path.startswith("/") or artifact_path.startswith("file:///") or re.match(r"^[A-Za-z]:[\\/]", artifact_path):
            errors.append(
                format_error(
                    ABSOLUTE_PATH_IN_LOG,
                    f"Step {sid} artifact_path must be relative, got: {artifact_path}"
                )
            )

        vstack_check = step.get("validator_stack")
        if not vstack_check:
            errors.append(
                format_error(
                    MISSING_VALIDATOR_STACK,
                    f"Step {sid} missing validator_stack entries."
                )
            )
        elif vstack_check != "explicit_none":
            for i, v in enumerate(vstack_check):
                if v["result"] not in ("PASSED", "FAILED"):
                    errors.append(
                        format_error(
                            VALIDATOR_RESULT_MISSING,
                            f"Step {sid} validator_stack[{i}] result "
                            f"must be PASSED or FAILED, got '{v['result']}'."
                        )
                    )

        gate = step.get("gate", "")
        if not gate:
            errors.append(
                format_error(MISSING_GATE, f"Step {sid} missing 'gate' field.")
            )

        status = step.get("status", "")
        if not status:
            errors.append(
                format_error(
                    MISSING_STEP_STATUS, f"Step {sid} missing 'status' field."
                )
            )

        # Gate recording consistency
        gate_result = step.get("gate_result", "")
        if gate_result == "approved_by_user":
            if not step.get("approved_at"):
                errors.append(
                    format_error(
                        GATE_APPROVED_NO_TIMESTAMP,
                        f"Step {sid} gate approved but missing approved_at timestamp."
                    )
                )
            if not step.get("approved_by"):
                errors.append(
                    format_error(
                        GATE_APPROVED_NO_USER,
                        f"Step {sid} gate approved but missing approved_by."
                    )
                )
        elif gate_result == "denied_by_user":
            if not step.get("approved_at"):
                errors.append(
                    format_error(
                        GATE_DENIED_NO_RECORD,
                        f"Step {sid} gate denied but no denial timestamp found."
                    )
                )

    # 7. Verify gate bypass documentation
    for step in steps:
        gate_text = step.get("gate", "")
        status = step.get("status", "")
        if "N/A" in gate_text and "bypassed" not in gate_text.lower():
            if status == "COMPLETED":
                errors.append(
                    format_error(
                        GATE_BYPASS_NO_NOTE,
                        f"Step {step.get('step_id', '?')} gate is 'N/A' but "
                        "no bypass explanation found. Use "
                        "'gate_behavior: bypassed_by_yolo'."
                    )
                )

    # 8. Verify mode-mode consistency
    if mode and steps:
        first_gate = steps[0].get("gate", "")
        spec_mode_match = re.search(
            r"\(bypassed by (\w+)\)", first_gate, re.IGNORECASE
        )
        if spec_mode_match:
            bypass_source = spec_mode_match.group(1)
            if bypass_source != mode:
                errors.append(
                    format_error(
                        MODE_MODE_MISMATCH,
                        f"Gate bypass references mode '{bypass_source}' "
                        f"but header says '{mode}'."
                    )
                )

    # 9. Decisions section
    if not log.get("has_decisions"):
        # Only warn for non-trivial runs (more than 1 step or any TDD cycle)
        if len(steps) > 1 or log.get("tdd_cycles"):
            errors.append(
                format_error(
                    MISSING_DECISIONS,
                    "Multi-step or TDD cycle runs should include "
                    "a 'Decisions & Overrides' section."
                )
            )

    # 10. Final State section
    if not log.get("has_final_state"):
        errors.append(
            format_error(
                MISSING_FINAL_STATE,
                "Run log must include a Final State section."
            )
        )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a run log against the template specification."
    )
    parser.add_argument("run_log_path", nargs="?", help="Path to the run log .md file")
    parser.add_argument("--repo-root", default=".", help="Root directory of the repository")
    parser.add_argument("--list-codes", action="store_true", help="List all error codes and exit")
    args = parser.parse_args(argv)

    if args.list_codes:
        codes = [
            FILE_NOT_FOUND, MISSING_SESSION_ID, MISSING_DATE, MISSING_MODE,
            UNKNOWN_MODE, MISSING_SEQUENCE_LOG, MISSING_STEP_ID,
            MISSING_STEP_SKILL, MISSING_OUTPUT_ARTIFACT, MISSING_ARTIFACT_PATH,
            MISSING_VALIDATOR_STACK, MISSING_GATE, MISSING_STEP_STATUS,
            MISSING_FINAL_STATE, ABSOLUTE_PATH_IN_LOG,
            GATE_APPROVED_NO_TIMESTAMP, GATE_APPROVED_NO_USER,
            GATE_DENIED_NO_RECORD, GATE_BYPASS_NO_NOTE,
            VALIDATOR_RESULT_MISSING, PRE_FLIGHT_MISSING,
            MISSING_DECISIONS, MODE_MODE_MISMATCH, BRANCH_NOT_RECORDED,
        ]
        print("Stable error codes for run-log validation:")
        for code in codes:
            print(f"  {code}")
        return 0

    if not args.run_log_path:
        parser.print_usage()
        return 1

    errs = validate_run_log(args.run_log_path, args.repo_root)
    if errs:
        for e in errs:
            print(f"ERROR {e}")
        return 1
    else:
        print("Run log validation passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
