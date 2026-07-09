from __future__ import annotations

from pathlib import Path

from auteur.roundtrip.handlers import (
    ExportData,
    ImportData,
    confirm_latest_import_proposal,
    handle_export_chapter,
    handle_import_chapter,
)
from auteur.roundtrip.serializers import mark_proposal_accepted, write_export, write_import_artifacts


def register_roundtrip_subcommands(sub) -> None:
    export_parser = sub.add_parser("export", help="Export project artifacts for external editing.")
    export_commands = export_parser.add_subparsers(dest="export_command", required=True)
    p = export_commands.add_parser("chapter", help="Export a chapter draft.")
    p.add_argument("project", type=Path)
    p.add_argument("chapter", type=int)
    p.add_argument("--format", choices=["md"], default="md")
    p.add_argument("--draft", default=None)

    import_parser = sub.add_parser("import", help="Import externally edited project artifacts.")
    import_commands = import_parser.add_subparsers(dest="import_command", required=True)
    p = import_commands.add_parser("chapter", help="Import an edited markdown chapter.")
    p.add_argument("project", type=Path)
    p.add_argument("chapter", type=int)
    p.add_argument("edited_markdown", type=Path)
    p.add_argument("--draft", default=None)

    p = import_commands.add_parser("confirm", help="Accept an import proposal artifact.")
    p.add_argument("project", type=Path)
    p.add_argument("chapter", type=int)
    p.add_argument("--proposal", required=True)


def handle_export_command(args) -> int:
    if args.export_command == "chapter":
        result = handle_export_chapter(args.project, args.chapter, args.format, args.draft)
        if not result.is_success:
            print(f"Error: {result.error}")
            return result.exit_code
        path = write_export(result.data)
        print(f"Exported chapter draft to {path}")
        return result.exit_code
    return 1


def handle_import_command(args) -> int:
    if args.import_command == "chapter":
        result = handle_import_chapter(args.project, args.chapter, args.edited_markdown, args.draft)
        if not result.is_success:
            print(f"Error: {result.error}")
            return result.exit_code
        data: ImportData = result.data
        artifact_dir = write_import_artifacts(data)
        print(f"Import artifacts written to {artifact_dir}")
        return result.exit_code

    if args.import_command == "confirm":
        result = confirm_latest_import_proposal(args.project, args.chapter, args.proposal)
        if not result.is_success:
            print(f"Error: {result.error}")
            return result.exit_code
        try:
            path = mark_proposal_accepted(result.data["artifact_dir"], result.data["proposal_id"])
        except Exception as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Accepted import proposal {args.proposal} in {path}")
        return result.exit_code

    return 1

