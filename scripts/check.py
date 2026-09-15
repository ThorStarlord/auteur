from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_COMMANDS = (
    (sys.executable, "scripts/test-validators.py"),
    (sys.executable, "scripts/validate-repo.py"),
    (sys.executable, "scripts/validate-release-scope.py"),
    (sys.executable, "scripts/verify_vendored_contract.py"),
    (sys.executable, "-m", "ruff", "check", "src", "tests"),
    (sys.executable, "-m", "pytest", "tests", "-q", "--tb=no"),
)


def commands_for(
    *,
    skip_pytest: bool = False,
    qualify: bool = False,
    ruff_paths: tuple[str, ...] | None = None,
) -> tuple[tuple[str, ...], ...]:
    """Build the verification command sequence for the requested evidence scope.

    ``ruff_paths=None`` preserves the historical full ``src tests`` Ruff check.
    Passing an explicit tuple scopes Ruff to those paths; an empty tuple omits
    Ruff, which is useful for a focused CI change with no Python files in the
    historical Ruff scope.
    """

    commands = list(CHECK_COMMANDS)

    if ruff_paths is not None:
        ruff_index = next(
            index
            for index, command in enumerate(commands)
            if len(command) >= 4 and command[1:4] == ("-m", "ruff", "check")
        )
        if ruff_paths:
            commands[ruff_index] = (
                sys.executable,
                "-m",
                "ruff",
                "check",
                *ruff_paths,
            )
        else:
            commands.pop(ruff_index)

    if qualify:
        commands = [
            command
            for command in commands
            if not (
                len(command) > 2
                and command[1:3] == ("-m", "pytest")
            )
        ]
        commands.append((sys.executable, "scripts/release_evidence.py"))
    elif skip_pytest:
        commands = [
            command
            for command in commands
            if not (
                len(command) > 2
                and command[1:3] == ("-m", "pytest")
            )
        ]

    return tuple(commands)


def run_checks(
    skip_pytest: bool = False,
    qualify: bool = False,
    ruff_paths: tuple[str, ...] | None = None,
) -> int:
    for command in commands_for(
        skip_pytest=skip_pytest,
        qualify=qualify,
        ruff_paths=ruff_paths,
    ):
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
        help="Skip the embedded pytest run (CI runs pytest separately).",
    )
    parser.add_argument(
        "--qualify",
        action="store_true",
        help="Produce durable release-qualification evidence: runs the suite once "
        "via scripts/release_evidence.py instead of the plain pytest entry.",
    )
    parser.add_argument(
        "--ruff-paths",
        nargs="*",
        default=None,
        help=(
            "Scope Ruff to the listed paths. Omit this option for the historical "
            "full 'src tests' Ruff check; pass it with no paths to skip Ruff."
        ),
    )
    args = parser.parse_args(argv)
    ruff_paths = None if args.ruff_paths is None else tuple(args.ruff_paths)
    return run_checks(
        skip_pytest=args.skip_pytest,
        qualify=args.qualify,
        ruff_paths=ruff_paths,
    )


if __name__ == "__main__":
    raise SystemExit(main())
