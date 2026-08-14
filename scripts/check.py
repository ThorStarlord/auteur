from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_COMMANDS = (
    (sys.executable, "scripts/test-validators.py"),
    (sys.executable, "scripts/validate-repo.py"),
    (sys.executable, "-m", "ruff", "check", "src", "tests"),
    (sys.executable, "-m", "pytest", "tests", "-q", "--tb=no"),
)


def run_checks(skip_pytest: bool = False, qualify: bool = False) -> int:
    if qualify:
        commands = [
            c for c in CHECK_COMMANDS
            if not (len(c) > 1 and c[1] == "-m" and c[2] == "pytest")
        ]
        commands.append((sys.executable, "scripts/release_evidence.py"))
    elif skip_pytest:
        commands = CHECK_COMMANDS[:-1]
    else:
        commands = CHECK_COMMANDS
    for command in commands:
        print(f"$ {' '.join(command)}", flush=True)
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Auteur verification stack.")
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Skip the embedded pytest run (CI runs pytest separately on a matrix).",
    )
    parser.add_argument(
        "--qualify",
        action="store_true",
        help="Produce durable release-qualification evidence: runs the suite once "
        "via scripts/release_evidence.py instead of the plain pytest entry.",
    )
    args = parser.parse_args(argv)
    return run_checks(skip_pytest=args.skip_pytest, qualify=args.qualify)


if __name__ == "__main__":
    raise SystemExit(main())
