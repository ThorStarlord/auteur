from __future__ import annotations

from pathlib import Path

import yaml

from auteur.book.builder import build_book_identity
from auteur.series.models import BookPlan


def register_book_subcommands(sub) -> None:
    parser = sub.add_parser("book", help="Build one book-level StoryIdentity.")
    commands = parser.add_subparsers(dest="book_command", required=True)
    build = commands.add_parser("build", help="Compile a BookPlan YAML file.")
    build.add_argument("book_plan", type=Path)
    build.add_argument("--output", type=Path, required=True)


def handle_book_command(args) -> int:
    try:
        plan = BookPlan.model_validate(yaml.safe_load(args.book_plan.read_text(encoding="utf-8")))
        identity = build_book_identity(plan)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        identity.to_yaml(args.output)
    except Exception as exc:
        print(f"Error: failed to build book identity: {exc}")
        return 1
    print(f"Wrote {args.output}")
    return 0
