"""Smoke tests: verify the CLI boots up without an LLM backend.

These tests only exercise argparse dispatch, help text, and version-like
responses. They require no project directory, no YAML blueprint, and no
API key — just pydantic + pyyaml + the Python standard library.
"""

import sys
from pathlib import Path

import pytest

from auteur.cli import main


def test_cli_help_exits_zero() -> None:
    """--help should print usage and exit 0."""
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_cli_no_args_fails() -> None:
    """No args should exit non-zero (argparse error)."""
    with pytest.raises(SystemExit) as exc:
        main([])
    # argparse exits 2 when required positional args are missing.
    assert exc.value.code == 2


def test_cli_unknown_command_fails() -> None:
    """An unrecognised subcommand should exit 2."""
    with pytest.raises(SystemExit) as exc:
        main(["not-a-real-command"])
    assert exc.value.code == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
