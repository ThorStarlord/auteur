"""Failure ledger builder for repeatable failure boundary detection.

Scans all run logs in a directory, extracts failure/TDD-cycle entries,
and produces a consolidated failure ledger. Detects repeatable failure
boundaries (same error code across 2+ independent runs).

Usage:
    python scripts/analyze-run-failures.py [--logs-dir PATH] [--ledger-out PATH]
    python scripts/analyze-run-failures.py --help
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime
from collections import defaultdict


def _find_run_logs(logs_dir: str) -> list[str]:
    """Discover all run log markdown files in a directory tree."""
    matches = []
    if not os.path.isdir(logs_dir):
        return matches
    for root, _dirs, files in os.walk(logs_dir):
        for f in files:
            if f.endswith(".md") and ("run_log" in f.lower() or "_run_" in f.lower() or "completion_log" in f.lower()):
                matches.append(os.path.join(root, f))
    return sorted(matches)


def _extract_failures(content: str, source: str) -> list[dict]:
    """Extract TDD cycle failures and ERROR lines from a run log."""
    failures = []

    # TDD Cycle entries
    tdd_blocks = re.findall(
        r"- \*\*RED\*\*:(.*?)- \*\*GREEN\*\*:(.*?)- \*\*REFACTOR\*\*:(.*?)(?=\n\n|\n###|\Z)",
        content, re.DOTALL
    )
    for red, green, refactor in tdd_blocks:
        red_text = red.strip()
        green_text = green.strip()
        refactor_text = refactor.strip()

        # Extract error codes from RED block
        codes_found = re.findall(r"\b([A-Z][A-Z_]+)\b", red_text)
        failures.append({
            "source": source,
            "type": "tdd_cycle",
            "red": red_text,
            "green": green_text,
            "refactor": refactor_text,
            "codes": codes_found,
        })

    # Validator failure entries (FAILED result in validator_stack)
    step_blocks = re.findall(
        r"### Step \d+.*?validator_stack:(.*?)(?=\n\n|\n###|\Z)",
        content, re.DOTALL
    )
    for vb in step_blocks:
        failed_validators = re.findall(
            r"level:\s*(.+?)\s*\n\s*command:\s*(.+?)\s*\n\s*result:\s*FAILED",
            vb
        )
        for level, command in failed_validators:
            failures.append({
                "source": source,
                "type": "validator_failure",
                "level": level.strip(),
                "command": command.strip(),
                "codes": ["VALIDATOR_FAILED"],
            })

    return failures


def _extract_session_id(content: str, filepath: str) -> str:
    """Extract the session ID from a run log header."""
    match = re.search(r"\*\*Session ID\*\*:\s*(\S+)", content)
    if match:
        return match.group(1)
    # Fall back to filename
    return os.path.splitext(os.path.basename(filepath))[0]


def _extract_mode(content: str) -> str:
    """Extract the execution mode from a run log header."""
    match = re.search(r"\*\*Orchestrator Mode\*\*:\s*(\S+)", content)
    return match.group(1) if match else "unknown"


def build_failure_ledger(logs_dir: str) -> dict:
    """Scan run logs and build a consolidated failure ledger.

    Returns a dict with:
      - total_runs: number of run logs scanned
      - runs_with_failures: count of runs that had failures
      - failures: list of all failure entries
      - repeatable_failures: dict of error_code -> list of occurrences
        where the code appeared in 2+ independent runs
      - ledger_timestamp: when this analysis was run
    """
    ledger = {
        "ledger_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_runs": 0,
        "runs_with_failures": 0,
        "failures": [],
        "repeatable_failures": {},
        "unique_error_codes": {},
    }

    run_logs = _find_run_logs(logs_dir)
    ledger["total_runs"] = len(run_logs)

    # code -> set of session_ids
    code_runs: dict[str, set[str]] = defaultdict(set)
    # code -> list of full entries
    code_entries: dict[str, list[dict]] = defaultdict(list)

    for rl_path in run_logs:
        with open(rl_path, "r", encoding="utf-8") as f:
            content = f.read()

        session_id = _extract_session_id(content, rl_path)
        mode = _extract_mode(content)

        failures = _extract_failures(content, rl_path)
        if failures:
            ledger["runs_with_failures"] += 1

        for entry in failures:
            entry["session_id"] = session_id
            entry["mode"] = mode
            ledger["failures"].append(entry)

            for code in entry.get("codes", []):
                code_runs[code].add(session_id)
                code_entries[code].append(entry)

    # Determine repeatable failure boundaries
    for code, sessions in code_runs.items():
        if len(sessions) >= 2:
            ledger["repeatable_failures"][code] = {
                "occurrence_count": len(code_entries[code]),
                "independent_runs": sorted(sessions),
                "severity": "repeatable_failure_boundary",
            }

        # Track uniqueness
        ledger["unique_error_codes"][code] = {
            "occurrence_count": len(code_entries[code]),
            "independent_run_count": len(sessions),
            "independent_runs": sorted(sessions),
            "is_repeatable": len(sessions) >= 2,
        }

    return ledger


def format_ledger_report(ledger: dict) -> str:
    """Format the failure ledger as a human-readable markdown report."""
    lines = [
        "# Failure Ledger & Repeatable Failure Boundary Report",
        "",
        f"Generated: {ledger['ledger_timestamp']}",
        "",
        "## Summary",
        f"- Run logs scanned: {ledger['total_runs']}",
        f"- Runs with failures: {ledger['runs_with_failures']}",
        f"- Total failure entries: {len(ledger['failures'])}",
        f"- Repeatable failure boundaries: {len(ledger['repeatable_failures'])}",
        "",
    ]

    if ledger["repeatable_failures"]:
        lines.append("## Repeatable Failure Boundaries Detected")
        lines.append("")
        lines.append(
            "| Error Code | Occurrences | Independent Runs | Severity |"
        )
        lines.append(
            "| :--- | :---: | :---: | :--- |"
        )
        for code, data in sorted(ledger["repeatable_failures"].items()):
            lines.append(
                f"| `{code}` | {data['occurrence_count']} | "
                f"{len(data['independent_runs'])} | "
                f"{data['severity']} |"
            )
        lines.append("")
        lines.append(
            "**Action required:** These error codes have appeared in "
            "2+ independent runs and warrant systemic hardening per the "
            "Repeatable Failure Boundary principle."
        )
        lines.append("")
    else:
        lines.append("## Repeatable Failure Boundaries")
        lines.append("")
        lines.append(
            "No repeatable failure boundaries detected. "
            "All failure occurrences are single-occurrence data issues "
            "and do not warrant systemic hardening."
        )
        lines.append("")

    # Unique error codes table
    lines.append("## Error Code Registry")
    lines.append("")
    lines.append(
        "| Code | Occurrences | Independent Runs | Repeatable? |"
    )
    lines.append(
        "| :--- | :---: | :---: | :--- |"
    )
    for code in sorted(ledger["unique_error_codes"].keys()):
        data = ledger["unique_error_codes"][code]
        repeatable = "⚠️ Yes" if data["is_repeatable"] else "No"
        lines.append(
            f"| `{code}` | {data['occurrence_count']} | "
            f"{data['independent_run_count']} | {repeatable} |"
        )
    lines.append("")

    # Recent failures detail
    if ledger["failures"]:
        lines.append("## Failure Detail")
        lines.append("")
        for entry in ledger["failures"][-20:]:  # last 20 entries
            lines.append(f"- **Session**: {entry['session_id']}")
            lines.append(f"  - **Type**: {entry['type']}")
            lines.append(f"  **Mode**: {entry.get('mode', '?')}")
            if entry["type"] == "tdd_cycle":
                lines.append(f"  - **RED**: {entry['red'][:120]}")
                lines.append(f"  - **GREEN**: {entry['green'][:120]}")
                lines.append(f"  - **REFACTOR**: {entry['refactor'][:120]}")
                codes = entry.get("codes", [])
                if codes:
                    lines.append(f"  - **Codes**: {', '.join(codes)}")
            elif entry["type"] == "validator_failure":
                lines.append(f"  - **Level**: {entry.get('level', '?')}")
                lines.append(f"  - **Command**: {entry.get('command', '?')}")
            lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build failure ledger and detect repeatable failure boundaries."
    )
    parser.add_argument(
        "--logs-dir", default="artifacts",
        help="Directory containing run logs (default: artifacts/)"
    )
    parser.add_argument(
        "--ledger-out", default=None,
        help="Output path for the ledger report markdown file"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON instead of markdown"
    )
    args = parser.parse_args(argv)

    if not os.path.isdir(args.logs_dir):
        print(f"Logs directory not found: {args.logs_dir}", file=sys.stderr)
        return 1

    ledger = build_failure_ledger(args.logs_dir)

    if args.json:
        print(json.dumps(ledger, indent=2, default=str))
    else:
        report = format_ledger_report(ledger)
        if args.ledger_out:
            with open(args.ledger_out, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Failure ledger written to {args.ledger_out}")
        else:
            print(report)

    # Exit with repeatable-boundary status
    if ledger["repeatable_failures"]:
        print(
            f"\n⚠️  {len(ledger['repeatable_failures'])} repeatable failure "
            "boundary(ies) detected. Systemic hardening warranted.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
