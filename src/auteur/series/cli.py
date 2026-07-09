from __future__ import annotations

from pathlib import Path

from auteur.series.formatters import (
    format_series_bible_success,
    format_series_compile_success,
    format_series_diagnostics_success,
    format_series_graph_success,
    format_series_validate_success,
)
from auteur.series.handlers import (
    handle_series_bible,
    handle_series_compile,
    handle_series_diagnose,
    handle_series_graph,
    handle_series_validate,
)
from auteur.series.models import SeriesIdentity
from auteur.series.serializers import (
    serialize_series_bible,
    serialize_series_compile,
    serialize_series_diagnostics,
    serialize_series_graph,
)


def register_series_subcommands(sub) -> None:
    parser = sub.add_parser("series", help="Manage whole-series narrative contracts.")
    commands = parser.add_subparsers(dest="series_command", required=True)

    p = commands.add_parser("validate", help="Validate a series_identity.yaml file.")
    p.add_argument("series", type=Path)

    p = commands.add_parser("compile", help="Compile series book plans into StoryIdentity files.")
    p.add_argument("series", type=Path)
    p.add_argument("--output", type=Path, required=True)

    p = commands.add_parser("diagnose", help="Run deterministic cross-book diagnostics.")
    p.add_argument("series", type=Path)
    p.add_argument("--output", type=Path, default=None)

    p = commands.add_parser("graph", help="Write narrative dependency graph.")
    p.add_argument("series", type=Path)
    p.add_argument("--output", type=Path, default=None)

    p = commands.add_parser("bible", help="Compile series_bible.json.")
    p.add_argument("series", type=Path)
    p.add_argument("--output", type=Path, default=None)


def load_series(path: Path) -> SeriesIdentity:
    if path.is_dir():
        path = path / "series_identity.yaml"
    return SeriesIdentity.from_yaml(path)


def handle_series_command(args) -> int:
    try:
        series = load_series(args.series)
    except Exception as exc:
        print(f"Error: invalid series identity: {exc}")
        return 1

    if args.series_command == "validate":
        result = handle_series_validate(series)
        if not result.is_success:
            print(f"Error: {result.error}")
            return result.exit_code
        print(format_series_validate_success(str(args.series)))
        return result.exit_code

    if args.series_command == "compile":
        result = handle_series_compile(series)
        if not result.is_success:
            print(f"Error: {result.error}")
            return result.exit_code
        written = serialize_series_compile(result, args.output)
        for path in written:
            print(f"Wrote {path}")
        print(format_series_compile_success(len(written), str(args.output)))
        return result.exit_code

    if args.series_command == "diagnose":
        result = handle_series_diagnose(series)
        output = args.output or Path("series") / "diagnostics" / "series_report.json"
        serialize_series_diagnostics(result, output)
        print(format_series_diagnostics_success(str(output)))
        diagnostics = result.data.diagnostics
        return 1 if [d for d in diagnostics if getattr(d.severity, "value", d.severity) == "error"] else 0

    if args.series_command == "graph":
        result = handle_series_graph(series)
        output = args.output or Path("series") / "dependency_graph.yaml"
        serialize_series_graph(result, output)
        print(format_series_graph_success(str(output)))
        return result.exit_code

    if args.series_command == "bible":
        result = handle_series_bible(series)
        output = args.output or Path("series_bible.json")
        serialize_series_bible(result, output)
        print(format_series_bible_success(str(output)))
        return result.exit_code

    return 1
