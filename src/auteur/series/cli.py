from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.series.bible import compile_series_bible
from auteur.series.compiler import write_book_identities
from auteur.series.diagnostics import diagnose_series
from auteur.series.graph import build_dependency_graph
from auteur.series.models import SeriesIdentity


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
        diagnostics = diagnose_series(series)
        errors = [d for d in diagnostics if getattr(d.severity, "value", d.severity) == "error"]
        if errors:
            print(f"Error: SeriesIdentity {args.series} failed validation.")
            return 1
        print(f"Success: SeriesIdentity {args.series} is valid.")
        return 0

    if args.series_command == "compile":
        try:
            written = write_book_identities(series, args.output)
        except Exception as exc:
            print(f"Error: failed to compile series: {exc}")
            return 1
        for path in written:
            print(f"Wrote {path}")
        return 0

    if args.series_command == "diagnose":
        diagnostics = diagnose_series(series)
        output = args.output or Path("series") / "diagnostics" / "series_report.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps({"diagnostics": [d.model_dump(mode="json") for d in diagnostics]}, indent=2),
            encoding="utf-8",
        )
        print(f"Series diagnostics written to {output}")
        return 1 if [d for d in diagnostics if getattr(d.severity, "value", d.severity) == "error"] else 0

    if args.series_command == "graph":
        graph = build_dependency_graph(series)
        output = args.output or Path("series") / "dependency_graph.yaml"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(yaml.safe_dump(graph.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
        print(f"Series dependency graph written to {output}")
        return 0

    if args.series_command == "bible":
        bible = compile_series_bible(series)
        output = args.output or Path("series_bible.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(bible, indent=2), encoding="utf-8")
        print(f"Series bible written to {output}")
        return 0

    return 1
