from __future__ import annotations

from pathlib import Path

from auteur.relations.formatters import format_relations_error, format_relations_success
from auteur.relations.handlers import (
    handle_relations_apply,
    handle_relations_diagnose,
    handle_relations_graph,
    handle_relations_validate,
)
from auteur.relations.serializers import (
    write_relation_diagnostics,
    write_relation_graph,
    write_relation_map,
)


def register_relations_subcommands(sub) -> None:
    parser = sub.add_parser("relations", help="Manage project relationship state.")
    commands = parser.add_subparsers(dest="relations_command", required=True)

    p = commands.add_parser("validate", help="Validate relations.yaml.")
    p.add_argument("project", type=Path)

    p = commands.add_parser("diagnose", help="Run deterministic relationship diagnostics.")
    p.add_argument("project", type=Path)

    p = commands.add_parser("graph", help="Write relationship graph artifact.")
    p.add_argument("project", type=Path)
    p.add_argument("--output", type=Path, default=None)

    p = commands.add_parser("apply", help="Apply relation_changes.yaml to relation state.")
    p.add_argument("project", type=Path)
    p.add_argument("chapter", type=int)
    p.add_argument("changes", type=Path)
    p.add_argument("--output", type=Path, default=None)


def handle_relations_command(args) -> int:
    if args.relations_command == "validate":
        result = handle_relations_validate(args.project)
        if not result.is_success:
            print(format_relations_error(result.error or "invalid relations"))
            return result.exit_code
        print(format_relations_success(f"Validated {args.project / 'relations.yaml'}"))
        return result.exit_code

    if args.relations_command == "diagnose":
        result = handle_relations_diagnose(args.project)
        if not result.is_success:
            print(format_relations_error(result.error or "diagnostics failed"))
            return result.exit_code
        output = args.project / "relations_diagnostics.json"
        write_relation_diagnostics(result.data, output)
        print(format_relations_success(f"Relationship diagnostics written to {output}"))
        return 1 if any(item.severity == "error" for item in result.data) else 0

    if args.relations_command == "graph":
        result = handle_relations_graph(args.project)
        if not result.is_success:
            print(format_relations_error(result.error or "graph failed"))
            return result.exit_code
        output = args.output or args.project / "relations_graph.yaml"
        write_relation_graph(result.data, output)
        print(format_relations_success(f"Relationship graph written to {output}"))
        return result.exit_code

    if args.relations_command == "apply":
        result = handle_relations_apply(args.project, args.chapter, args.changes)
        if not result.is_success:
            print(format_relations_error(result.error or "apply failed"))
            return result.exit_code
        output = args.output or args.project / "relations.yaml"
        write_relation_map(result.data, output)
        print(format_relations_success(f"Updated relationship state written to {output}"))
        return result.exit_code

    return 1

