"""Auteur CLI — thin dispatch shell: argparse -> handlers -> formatters/serializers."""

from __future__ import annotations

import argparse

from auteur.cli_parser import build_parser
from auteur.cli_dispatch import dispatch


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return dispatch(args)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
