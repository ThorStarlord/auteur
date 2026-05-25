"""CLI commands for character categorization."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from auteur.blueprint import StoryBlueprint
from auteur.character.analyzer import analyze_character_categorization
from auteur.character.categorizer import CategorizationEngine


def register_character_subcommands(subparsers) -> None:
    p_char = subparsers.add_parser("character", help="Character categorization and identity commands.")
    char_sub = p_char.add_subparsers(dest="character_command", required=True)

    p_categorize = char_sub.add_parser(
        "categorize",
        help="Automatically propose character identity and categorization from existing blueprint data.",
    )
    p_categorize.add_argument("blueprint", type=Path, help="Path to blueprint.yaml")

    p_diagnose = char_sub.add_parser(
        "diagnose",
        help="Run character categorization diagnostics on a blueprint.",
    )
    p_diagnose.add_argument("blueprint", type=Path, help="Path to blueprint.yaml")

    p_show = char_sub.add_parser(
        "show",
        help="Show character categorization summary for a blueprint.",
    )
    p_show.add_argument("blueprint", type=Path, help="Path to blueprint.yaml")
    p_show.add_argument("--output", type=Path, default=None, help="Output path for report (JSON).")


def handle_character_command(args) -> int:
    if args.character_command == "categorize":
        return _cmd_categorize(args.blueprint)
    elif args.character_command == "diagnose":
        return _cmd_character_diagnose(args.blueprint)
    elif args.character_command == "show":
        return _cmd_character_show(args.blueprint, args.output)
    return 2


def _cmd_categorize(blueprint_path: Path) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint not found: {blueprint_path}", file=sys.stderr)
        return 1
    try:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
    except Exception as exc:
        print(f"Error: invalid blueprint: {exc}", file=sys.stderr)
        return 1

    engine = CategorizationEngine(blueprint)
    categorizations = engine.categorize_all()

    output = {}
    for name, cat in categorizations.items():
        output[name] = cat.model_dump(mode="json")
    print(json.dumps(output, indent=2))
    return 0


def _cmd_character_diagnose(blueprint_path: Path) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint not found: {blueprint_path}", file=sys.stderr)
        return 1
    try:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
    except Exception as exc:
        print(f"Error: invalid blueprint: {exc}", file=sys.stderr)
        return 1

    diagnostics = analyze_character_categorization(blueprint)
    if not diagnostics:
        print("No character categorization issues found.")
        return 0

    report = {"diagnostics": [d.model_dump(mode="json") for d in diagnostics]}
    print(json.dumps(report, indent=2))
    has_error = any(d.severity.value == "error" for d in diagnostics)
    return 4 if has_error else 0


def _cmd_character_show(blueprint_path: Path, output_path: Path | None) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint not found: {blueprint_path}", file=sys.stderr)
        return 1
    try:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
    except Exception as exc:
        print(f"Error: invalid blueprint: {exc}", file=sys.stderr)
        return 1

    report = {"characters": []}
    for char in blueprint.characters:
        entry = {
            "name": char.name,
            "role": char.role.value,
            "arc_type": char.arc_type.value,
            "has_identity": char.identity is not None,
            "milestone_count": len(char.key_milestones),
            "relationship_count": len(char.current_state.relationships),
        }
        if char.identity is not None:
            identity = char.identity if isinstance(char.identity, dict) else {}
            entry["identity"] = {
                "archetype": identity.get("archetype"),
                "moral_alignment": identity.get("moral_alignment"),
                "dramatic_functions": identity.get("dramatic_functions", []),
                "trope_tags": identity.get("trope_tags", []),
            }
        report["characters"].append(entry)

    report_json = json.dumps(report, indent=2)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"{report_json}\n", encoding="utf-8")
    print(report_json)
    return 0
