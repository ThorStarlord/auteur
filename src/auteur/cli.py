"""Auteur CLI — thin dispatch shell: argparse -> handlers -> formatters/serializers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from auteur.cli_parser import build_parser
from auteur.cli_dispatch import dispatch


_BRIEF_SENTINEL = "__auteur_structured_discovery_brief__"


def _raw_argv(argv: list[str] | None) -> list[str]:
    return list(sys.argv[1:] if argv is None else argv)


def _is_story_discovery_start(raw: list[str]) -> bool:
    return len(raw) >= 2 and raw[0] == "story-discovery" and raw[1] == "start"


def _is_story_discovery_compose(raw: list[str]) -> bool:
    return len(raw) >= 2 and raw[0] == "story-discovery" and raw[1] == "compose"


def _prepare_story_discovery_argv(
    argv: list[str] | None,
) -> tuple[list[str], bool, Path | None]:
    """Recognize Story Discovery adapter flags without changing the base parser."""
    raw = _raw_argv(argv)
    is_story_discovery_run = (
        len(raw) >= 2
        and raw[0] == "story-discovery"
        and raw[1] == "run"
    )
    recommend = is_story_discovery_run and "--recommend" in raw
    brief_path: Path | None = None

    if is_story_discovery_run and "--brief" in raw:
        if not recommend:
            raise ValueError("story-discovery --brief currently requires --recommend")
        if raw.count("--brief") != 1:
            raise ValueError("story-discovery --brief may be supplied only once")
        index = raw.index("--brief")
        if index + 1 >= len(raw) or raw[index + 1].startswith("--"):
            raise ValueError("story-discovery --brief requires a YAML file path")
        brief_path = Path(raw[index + 1])
        del raw[index:index + 2]
        # The legacy parser still requires the raw brain_dump positional. F2 keeps
        # that parser contract intact and uses this sentinel only inside the adapter.
        raw.append(_BRIEF_SENTINEL)

    if recommend:
        raw = [token for token in raw if token != "--recommend"]
    return raw, recommend, brief_path


def _prepare_argv(argv: list[str] | None) -> tuple[list[str], bool]:
    """Preserve the qualified Phase A adapter contract for existing callers/tests."""
    raw, recommend, _ = _prepare_story_discovery_argv(argv)
    return raw, recommend


def _attach_story_discovery_brief(args: argparse.Namespace, brief_path: Path | None) -> None:
    if args.command == "story-discovery" and args.story_discovery_command == "run":
        # ``brief`` is scoped only to Story Discovery so it cannot clobber the
        # unrelated genre-builder positional argument with the same attribute name.
        setattr(args, "brief", brief_path)
        setattr(args, "discovery_brief", brief_path)


def main(argv: list[str] | None = None) -> int:
    raw_input = _raw_argv(argv)
    if _is_story_discovery_start(raw_input):
        from auteur.story_discovery_start_cli import dispatch_start_argv

        return dispatch_start_argv(raw_input[2:])
    if _is_story_discovery_compose(raw_input):
        from auteur.story_discovery_compose_cli import dispatch_compose_argv

        return dispatch_compose_argv(raw_input[2:])

    try:
        raw, recommend, discovery_brief = _prepare_story_discovery_argv(raw_input)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    parser = build_parser()
    args = parser.parse_args(raw)
    _attach_story_discovery_brief(args, discovery_brief)

    if recommend:
        if discovery_brief is not None:
            # G1a keeps the F2 engine unchanged but replaces its schema-first recovery
            # at the real CLI boundary. This preflight is deterministic and happens
            # before any provider can be constructed.
            from auteur.story_discovery_brief import DiscoveryBrief, assess_intent_adequacy
            from auteur.story_discovery_guidance import print_inadequate_brief_recovery

            try:
                parsed_brief = DiscoveryBrief.from_yaml(discovery_brief)
            except Exception:
                parsed_brief = None
            if parsed_brief is not None:
                adequacy = assess_intent_adequacy(parsed_brief)
                if not adequacy.adequate:
                    print_inadequate_brief_recovery(adequacy)
                    return 1

            from auteur.story_discovery_intent import dispatch_story_discovery_recommend

            return dispatch_story_discovery_recommend(args)

        # Raw-premise recommendation stays on the already-qualified Phase A/B
        # adapter. F2 adds intent-aware ranking without changing legacy raw behavior.
        from auteur.story_discovery_recommend import dispatch_story_discovery_recommend

        return dispatch_story_discovery_recommend(args)
    return dispatch(args)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_input = _raw_argv(argv)
    if _is_story_discovery_start(raw_input):
        from auteur.story_discovery_start_cli import parse_start_args

        return parse_start_args(raw_input[2:])
    if _is_story_discovery_compose(raw_input):
        from auteur.story_discovery_compose_cli import parse_compose_args

        return parse_compose_args(raw_input[2:])

    raw, recommend, discovery_brief = _prepare_story_discovery_argv(raw_input)
    args = build_parser().parse_args(raw)
    _attach_story_discovery_brief(args, discovery_brief)
    if recommend:
        setattr(args, "recommend", True)
    return args


if __name__ == "__main__":
    raise SystemExit(main())
