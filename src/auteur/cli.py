"""Auteur CLI — currently exposes a single 'plan' subcommand.

    auteur plan <blueprint.yaml> <chapter_index>

Loads a YAML blueprint, slices a PlanningCall for the given chapter, and
prints the assembled Cartographer system + user prompt to stdout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.pipeline import PipelineRunner


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="auteur", description="Agentic narrative engineering toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Render the Cartographer prompt for a chapter.")
    plan.add_argument("blueprint", type=Path, help="Path to a StoryBlueprint YAML file.")
    plan.add_argument("chapter", type=int, help="Chapter index (1-based).")

    args = parser.parse_args(argv)

    if args.command == "plan":
        return _cmd_plan(args.blueprint, args.chapter)
    parser.print_help()
    return 2


def _cmd_plan(blueprint_path: Path, chapter_index: int) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint file not found: {blueprint_path}", file=sys.stderr)
        return 1

    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    result = PipelineRunner(blueprint).plan_chapter(chapter_index)

    print("--- SYSTEM PROMPT ---\n")
    print(result.system_prompt)
    print("\n--- USER MESSAGE ---\n")
    print(result.user_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
