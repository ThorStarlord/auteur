"""Beginner-facing CLI for Story Design Packs and tutor guidance."""
from __future__ import annotations

import json
from argparse import _SubParsersAction
from typing import Any

from .composition import compose_packs
from .registry import get_design_pack_registry
from .tutor import tutor_recommend


def register_story_design_subcommands(subparsers: _SubParsersAction) -> None:
    parser = subparsers.add_parser("design", help="Explore reusable Story Design Packs.")
    subs = parser.add_subparsers(dest="design_command", required=True)
    pack = subs.add_parser("pack", help="List, inspect, or compose design packs.")
    pack_sub = pack.add_subparsers(dest="design_pack_command", required=True)
    p = pack_sub.add_parser("list", help="List built-in Story Design Packs.")
    p.add_argument("--json", action="store_true")
    p = pack_sub.add_parser("inspect", help="Inspect one Story Design Pack.")
    p.add_argument("pack_id")
    p.add_argument("--json", action="store_true")
    p = pack_sub.add_parser("compose", help="Compose multiple Story Design Packs.")
    p.add_argument("--pack", action="append", required=True, dest="pack_ids")
    p.add_argument("--json", action="store_true")
    tutor = subs.add_parser("tutor", help="Generate derived learning guidance.")
    tutor_sub = tutor.add_subparsers(dest="tutor_command", required=True)
    for name, help_text in (("recommend", "Recommend a design choice."), ("explain", "Explain a design choice."), ("alternatives", "Show alternatives to a design choice.")):
        p = tutor_sub.add_parser(name, help=help_text)
        p.add_argument("--pack", action="append", required=True, dest="pack_ids")
        p.add_argument("--decision", default="next creative decision")
        p.add_argument("--premise", default="your story")
        p.add_argument("--json", action="store_true")


def dispatch_story_design_commands(args: Any) -> int:
    registry = get_design_pack_registry()
    if args.command != "design":
        return False
    if args.design_command == "pack":
        if args.design_pack_command == "list":
            data = registry.list()
        elif args.design_pack_command == "inspect":
            pack, digest = registry.get(args.pack_id)
            data = {**pack.model_dump(mode="json"), "content_hash": digest}
        else:
            data = compose_packs(args.pack_ids).model_dump(mode="json")
        if getattr(args, "json", False):
            print(json.dumps(data, indent=2))
        elif isinstance(data, list):
            for item in data:
                print(f"{item['pack_id']} ({item['pack_kind']}) — {item['display_name']}")
        elif args.design_pack_command == "inspect":
            print(f"{data['display_name']} ({data['pack_id']})")
            print(data["description"])
            print("Design options: " + ", ".join(o["name"] for o in data["design_options"]))
        else:
            print("Pack composition")
            for key in ("reinforcing_patterns", "productive_tensions", "actual_conflicts", "unresolved_questions"):
                print(f"{key.replace('_', ' ').title()}: {len(data[key])}")
        return 0
    guidance = tutor_recommend(args.pack_ids, decision=args.decision, premise=args.premise)
    data = guidance.model_dump(mode="json")
    if getattr(args, "json", False):
        print(json.dumps(data, indent=2))
    elif args.tutor_command == "alternatives":
        print("Alternatives: " + ", ".join(guidance.alternatives) or "No alternatives recorded.")
        print("Trade-offs: " + "; ".join(guidance.tradeoffs))
    else:
        print(f"Orient: {guidance.orientation}")
        print(f"Craft principle: {guidance.craft_concept} — {guidance.plain_language_explanation}")
        print(f"Recommended: {guidance.recommendation}")
        print(f"Why: {guidance.why_recommended}")
        print(f"Question: {guidance.question_for_author}")
        print(f"Authority: {guidance.authority_status}")
    return 0
