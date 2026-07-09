from __future__ import annotations

from pathlib import Path

from auteur.genre_builder.formatters import format_genre_builder_error, format_genre_builder_success
from auteur.genre_builder.handlers import (
    handle_genre_build,
    handle_genre_explain,
    handle_genre_install,
    handle_genre_validate,
    list_custom_genres,
)
from auteur.genre_builder.serializers import (
    install_custom_genre_contract,
    write_custom_genre_contract,
    write_genre_guide,
)


def register_genre_builder_subcommands(sub) -> None:
    parser = sub.add_parser("genre", help="Build and manage custom genre contracts.")
    commands = parser.add_subparsers(dest="genre_command", required=True)

    p = commands.add_parser("build", help="Compile a structured brief into a custom GenreContract.")
    p.add_argument("brief", type=Path)
    p.add_argument("--output", type=Path, required=True)

    p = commands.add_parser("validate", help="Validate a custom genre contract.")
    p.add_argument("contract", type=Path)

    p = commands.add_parser("explain", help="Render a human-readable guide from a custom genre contract.")
    p.add_argument("contract", type=Path)
    p.add_argument("--output", type=Path, default=None)

    p = commands.add_parser("install", help="Install a custom genre contract into a project.")
    p.add_argument("contract", type=Path)
    p.add_argument("--project", type=Path, required=True)

    p = commands.add_parser("list-custom", help="List project-local custom genre contracts.")
    p.add_argument("project", type=Path)


def handle_genre_builder_command(args) -> int:
    if args.genre_command == "build":
        result = handle_genre_build(args.brief)
        if not result.is_success:
            print(format_genre_builder_error(result.error or "genre build failed"))
            return result.exit_code
        path = write_custom_genre_contract(result.data, args.output)
        print(format_genre_builder_success(f"Custom genre contract written to {path}"))
        return 0

    if args.genre_command == "validate":
        result = handle_genre_validate(args.contract)
        if not result.is_success:
            if result.data:
                print(format_genre_builder_error("genre contract invalid"))
                for diagnostic in result.data:
                    print(f"{diagnostic.rule}: {diagnostic.message}")
            else:
                print(format_genre_builder_error(result.error or "genre contract invalid"))
            return result.exit_code
        print(format_genre_builder_success(f"Validated {args.contract}"))
        return 0

    if args.genre_command == "explain":
        result = handle_genre_explain(args.contract)
        if not result.is_success:
            print(format_genre_builder_error(result.error or "genre explain failed"))
            return result.exit_code
        if args.output:
            write_genre_guide(result.data, args.output)
            print(format_genre_builder_success(f"Genre guide written to {args.output}"))
        else:
            print(result.data)
        return 0

    if args.genre_command == "install":
        result = handle_genre_install(args.contract)
        if not result.is_success:
            print(format_genre_builder_error(result.error or "genre install failed"))
            return result.exit_code
        path = install_custom_genre_contract(result.data, args.project)
        print(format_genre_builder_success(f"Installed custom genre contract to {path}"))
        return 0

    if args.genre_command == "list-custom":
        for genre_id in list_custom_genres(args.project):
            print(genre_id)
        return 0

    return 1
