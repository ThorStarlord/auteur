"""Dedicated CLI surface for guided Story Discovery brief capture/refinement."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_start_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auteur story-discovery start",
        description=(
            "Create, resume, refine, or edit a non-canonical Story Discovery brief "
            "in writer-facing language."
        ),
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=Path("."),
        help="Project root directory (default: current directory).",
    )
    parser.add_argument(
        "--brief",
        type=Path,
        default=None,
        help="Working brief path relative to the project (default: story_discovery/brief.yaml).",
    )
    parser.add_argument(
        "--premise",
        type=str,
        default=None,
        help="Preseed a new brief with premise text or a premise file.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--refine",
        action="store_true",
        help=(
            "Optionally add richer target-experience, architecture, medium/mode, "
            "and hard-constraint intent after the minimum brief is adequate."
        ),
    )
    mode.add_argument(
        "--edit",
        action="store_true",
        help=(
            "Edit or clear previously declared intent. Clearing minimum fields may "
            "make the brief intentionally incomplete again."
        ),
    )
    return parser


def parse_start_args(argv: list[str] | None = None) -> argparse.Namespace:
    args = build_start_parser().parse_args(argv)
    setattr(args, "command", "story-discovery")
    setattr(args, "story_discovery_command", "start")
    return args


def dispatch_start_argv(argv: list[str] | None = None) -> int:
    args = parse_start_args(argv)
    if args.refine or args.edit:
        from auteur.story_discovery_refinement import dispatch_story_discovery_refinement

        return dispatch_story_discovery_refinement(args)

    from auteur.story_discovery_guidance import dispatch_story_discovery_start

    return dispatch_story_discovery_start(args)
