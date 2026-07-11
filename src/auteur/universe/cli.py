from __future__ import annotations

from pathlib import Path

from auteur.universe.handlers import (
    handle_universe_validate,
    handle_universe_diagnose,
)
from auteur.universe.models import UniverseIdentity
from auteur.universe.formatters import (
    format_universe_validate_success,
    format_universe_diagnostics_success,
    format_universe_error,
)


def register_universe_subcommands(sub) -> None:
    """Register universe subcommands under the main CLI."""
    parser = sub.add_parser("universe", help="Manage universe world-building contracts.")
    commands = parser.add_subparsers(dest="universe_command", required=True)

    p = commands.add_parser("validate", help="Validate a universe_identity.yaml file.")
    p.add_argument("universe", type=Path, help="Path to universe_identity.yaml")

    p = commands.add_parser("diagnose", help="Run diagnostics on a universe_identity.yaml.")
    p.add_argument("universe", type=Path, help="Path to universe_identity.yaml")
    p.add_argument("--output", type=Path, default=None, help="Output diagnostics to file")

    p = commands.add_parser("build", help="Validate and write a canonical universe_identity.yaml.")
    p.add_argument("universe", type=Path, help="Source universe YAML")
    p.add_argument("--output", type=Path, required=True, help="Canonical output path")


def handle_universe_command(args) -> int:
    """Dispatch universe subcommands."""
    if args.universe_command == "validate":
        result = handle_universe_validate(args.universe)
        if not result.is_success:
            print(format_universe_error(result.error or "validation failed"))
            return result.exit_code
        print(format_universe_validate_success(str(args.universe)))
        return 0

    if args.universe_command == "diagnose":
        result = handle_universe_diagnose(args.universe)
        if not result.is_success:
            print(format_universe_error(result.error or "diagnose failed"))
            return result.exit_code

        output = args.output or args.universe.parent / "universe_diagnostics.txt"
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            f.write(result.data)

        print(format_universe_diagnostics_success(str(output)))
        print(result.data)
        return 0

    if args.universe_command == "build":
        try:
            universe = UniverseIdentity.from_yaml(args.universe)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            universe.to_yaml(args.output)
        except Exception as exc:
            print(format_universe_error(f"failed to build universe: {exc}"))
            return 1
        print(f"Wrote {args.output}")
        return 0

    return 1
