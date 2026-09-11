"""CLI adapter for explicit review and selection of noncanonical Structure proposals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from auteur.structure.proposal_service import ProposalReviewService


def parse_proposal_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="auteur structure proposal")
    sub = parser.add_subparsers(dest="proposal_command", required=True)

    inspect = sub.add_parser("inspect", help="Inspect one noncanonical Structure proposal.")
    inspect.add_argument("proposal", type=Path)
    inspect.add_argument("--project", type=Path, default=Path("."))
    inspect.add_argument("--json", action="store_true")

    select = sub.add_parser("select", help="Select one proposal option without applying it.")
    select.add_argument("proposal", type=Path)
    select.add_argument("--option", required=True)
    select.add_argument("--author", default=None)
    select.add_argument("--project", type=Path, default=Path("."))
    select.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def _print_human(data: dict[str, object]) -> None:
    print(f"Proposal: {data['proposal_id']}")
    print(f"Status: {data['authority_status']}")
    print(f"Summary: {data['summary']}")
    print("Options:")
    for option in data["options"]:  # type: ignore[union-attr]
        marker = "*" if option["id"] == data["selected_option_id"] else "-"
        print(f"  {marker} {option['id']}: {option['summary']}")
        print(f"    Tradeoffs: {option['tradeoffs']}")
    if data["source_current"] is False:
        print("Source currentness: STALE / UNRESOLVED")
    if data["next_command"]:
        print(f"Next authoritative workflow: {data['next_command']}")
    elif data["select_command"]:
        print(f"Selection command: {data['select_command']}")
    print("No accepted story artifact was changed by this review/selection step.")


def dispatch_proposal_argv(argv: list[str]) -> int:
    args = parse_proposal_args(argv)
    service = ProposalReviewService(args.project)
    try:
        if args.proposal_command == "select":
            data = service.select(args.proposal, args.option, author=args.author)
        else:
            data = service.inspect(args.proposal)
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=__import__("sys").stderr)
        return 1

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        _print_human(data)
    return 0
