"""CLI adapter for deterministic Story Discovery review."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_review_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auteur story-discovery review",
        description=(
            "Reconstruct the current Story Discovery recommendation and evidence "
            "without calling a provider or changing project state."
        ),
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=Path("."),
        help="Project root containing story_discovery artifacts.",
    )
    return parser


def parse_review_args(argv: list[str]) -> argparse.Namespace:
    args = build_review_parser().parse_args(argv)
    setattr(args, "command", "story-discovery")
    setattr(args, "story_discovery_command", "review")
    return args


def dispatch_review_argv(argv: list[str]) -> int:
    from auteur.story_discovery_review import dispatch_story_discovery_review

    return dispatch_story_discovery_review(parse_review_args(argv))
