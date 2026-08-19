"""CLI adapter for candidate-only Story Discovery composition."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_compose_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auteur story-discovery compose",
        description=(
            "Create a new candidate by keeping one Story Discovery primary engine "
            "and borrowing explicitly requested compatible subordinate mechanisms."
        ),
    )
    parser.add_argument("discovery_dir", type=Path)
    parser.add_argument("--primary", required=True)
    parser.add_argument(
        "--borrow",
        action="append",
        required=True,
        help=(
            "Borrow one compatible subordinate mechanism as candidate_id:mechanism. "
            "Repeat for multiple alternatives."
        ),
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    parser.add_argument("--model", default=None)
    return parser


def parse_compose_args(argv: list[str]) -> argparse.Namespace:
    args = build_compose_parser().parse_args(argv)
    setattr(args, "command", "story-discovery")
    setattr(args, "story_discovery_command", "compose")
    return args


def dispatch_compose_argv(argv: list[str]) -> int:
    from auteur.story_discovery_compose import dispatch_story_discovery_compose

    return dispatch_story_discovery_compose(parse_compose_args(argv))
