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


def run_checks(skip_pytest: bool = False) -> int:
    commands = CHECK_COMMANDS[:-1] if skip_pytest else CHECK_COMMANDS
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
    args = parser.parse_args(argv)
    return run_checks(skip_pytest=args.skip_pytest)


if __name__ == "__main__":
    raise SystemExit(main())
