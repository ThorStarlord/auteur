"""Auteur CLI — thin dispatch shell: argparse -> handlers -> formatters/serializers."""

from __future__ import annotations

import argparse
import sys

from auteur.cli_parser import build_parser
from auteur.cli_dispatch import dispatch


def _prepare_argv(argv: list[str] | None) -> tuple[list[str], bool]:
    """Recognize the experimental Story Discovery convergence flag.

    The existing parser remains unchanged while the experiment is opt-in. Only
    ``story-discovery run`` may consume ``--recommend``; every other command is
    parsed exactly as before.
    """
    raw = list(sys.argv[1:] if argv is None else argv)
    is_story_discovery_run = (
        len(raw) >= 2
        and raw[0] == "story-discovery"
        and raw[1] == "run"
    )
    recommend = is_story_discovery_run and "--recommend" in raw
    if recommend:
        raw = [token for token in raw if token != "--recommend"]
    return raw, recommend


def main(argv: list[str] | None = None) -> int:
    raw, recommend = _prepare_argv(argv)
    parser = build_parser()
    args = parser.parse_args(raw)
    if recommend:
        from auteur.story_discovery_recommend import dispatch_story_discovery_recommend

        return dispatch_story_discovery_recommend(args)
    return dispatch(args)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw, recommend = _prepare_argv(argv)
    args = build_parser().parse_args(raw)
    if recommend:
        setattr(args, "recommend", True)
    return args


if __name__ == "__main__":
    raise SystemExit(main())
