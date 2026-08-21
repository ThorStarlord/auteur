"""CLI adapter for direct and guided Story Discovery composition."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_compose_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auteur story-discovery compose",
        description=(
            "Create a candidate by keeping the recommended primary engine and borrowing "
            "only explicitly selected compatible subordinate mechanisms."
        ),
    )
    parser.add_argument(
        "discovery_dir",
        type=Path,
        nargs="?",
        help="Advanced mode: Story Discovery artifact directory.",
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help="Guided mode: project root. Do not combine with advanced composition arguments.",
    )
    parser.add_argument("--primary", default=None, help="Advanced mode: governing candidate ID.")
    parser.add_argument(
        "--borrow",
        action="append",
        default=[],
        help=(
            "Advanced mode: borrow one compatible subordinate mechanism as "
            "candidate_id:mechanism. Repeat for multiple alternatives."
        ),
    )
    parser.add_argument("--output", type=Path, default=None, help="Advanced mode: custom candidate output path.")
    parser.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    parser.add_argument("--model", default=None)
    return parser


def parse_compose_args(argv: list[str]) -> argparse.Namespace:
    parser = build_compose_parser()
    args = parser.parse_args(argv)

    guided = (
        args.project is not None
        and args.discovery_dir is None
        and args.primary is None
        and not args.borrow
        and args.output is None
    )
    if args.project is not None and not guided:
        parser.error(
            "--project selects guided composition and cannot be combined with "
            "discovery_dir, --primary, --borrow, or --output"
        )
    if not guided:
        if args.discovery_dir is None:
            parser.error("advanced composition requires discovery_dir, or use --project for guided mode")
        if not args.primary:
            parser.error("advanced composition requires --primary")
        if not args.borrow:
            parser.error("advanced composition requires at least one --borrow")

    setattr(args, "guided", guided)
    setattr(args, "command", "story-discovery")
    setattr(args, "story_discovery_command", "compose")
    return args


def dispatch_compose_argv(argv: list[str]) -> int:
    args = parse_compose_args(argv)
    if args.guided:
        from auteur.story_discovery_guided_compose import dispatch_story_discovery_guided_compose

        return dispatch_story_discovery_guided_compose(args)

    from auteur.story_discovery_compose import dispatch_story_discovery_compose

    return dispatch_story_discovery_compose(args)
