"""Beginner-facing CLI for Story Design Packs and decision-oriented Tutor guidance."""
from __future__ import annotations

import json
import sys
from argparse import _SubParsersAction
from pathlib import Path
from typing import Any, Iterable

from .composition import compose_packs
from .handoff import DecisionAuthorityHandoff, derive_decision_handoff
from .models import AuthorAction, TutorDepth, source_fingerprint
from .proposal_bridge import generate_structure_proposal_from_tutor
from .registry import get_design_pack_registry
from .session import TutorSession, TutorSessionStore, create_session
from .tutor import decision_card_from_guidance, tutor_recommend


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
    for name, help_text in (
        ("recommend", "Recommend a design choice."),
        ("explain", "Explain a design choice."),
        ("alternatives", "Show alternatives to a design choice."),
    ):
        p = tutor_sub.add_parser(name, help=help_text)
        p.add_argument("--pack", action="append", required=True, dest="pack_ids")
        p.add_argument("--decision", default="next creative decision")
        p.add_argument("--premise", default="your story")
        p.add_argument("--json", action="store_true")

    root_tutor = subparsers.add_parser("tutor", help="Work through one derived author decision.")
    root_sub = root_tutor.add_subparsers(dest="tutor_command", required=True)
    for name, help_text in (
        ("next", "Show the next eligible derived Decision Card."),
        ("explain", "Explain the same derived decision in more depth."),
    ):
        p = root_sub.add_parser(name, help=help_text)
        p.add_argument("--pack", action="append", required=True, dest="pack_ids")
        p.add_argument("--decision", default="next creative decision")
        p.add_argument("--premise", default="your story")
        p.add_argument(
            "--project",
            type=Path,
            default=None,
            help="Persist a local advisory session beneath this project.",
        )
        p.add_argument(
            "--source",
            action="append",
            default=[],
            metavar="NAME=PATH",
            help="Project-local source artifact used for freshness checks; repeatable.",
        )
        if name == "next":
            p.add_argument(
                "--depth",
                choices=[depth.value for depth in TutorDepth],
                default=TutorDepth.RECOMMEND.value,
                help="Presentation depth only; does not change the semantic decision.",
            )
        p.add_argument("--json", action="store_true")

    p = root_sub.add_parser("show", help="Inspect a saved local Tutor session.")
    p.add_argument("session_id")
    p.add_argument("--project", type=Path, default=Path("."))
    p.add_argument("--json", action="store_true")

    p = root_sub.add_parser("choose", help="Record an advisory response to a Tutor session.")
    p.add_argument("session_id")
    p.add_argument("action", choices=[action.value for action in AuthorAction])
    p.add_argument("--value", default=None)
    p.add_argument("--project", type=Path, default=Path("."))
    p.add_argument("--json", action="store_true")

    p = root_sub.add_parser(
        "handoff",
        help="Derive the existing story-authority workflow that owns a resolved choice.",
    )
    p.add_argument("session_id")
    p.add_argument("--project", type=Path, default=Path("."))
    p.add_argument("--json", action="store_true")

    p = root_sub.add_parser(
        "propose",
        help="Generate a validated noncanonical StructureProposal from a routed Tutor choice.",
    )
    p.add_argument("session_id")
    p.add_argument("--project", type=Path, default=Path("."))
    p.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p.add_argument("--model", default=None)
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


def _normalized_source_spec(project_root: Path, source_spec: str) -> tuple[str, Path]:
    if "=" not in source_spec:
        raise ValueError("--source must use NAME=PATH, for example story=story_identity.yaml")
    name, raw_path = source_spec.split("=", 1)
    if not name.strip() or not raw_path.strip():
        raise ValueError("--source requires non-empty NAME and PATH")

    root = project_root.resolve()
    raw = Path(raw_path)
    candidate = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Tutor source must be inside the selected project")
    if not candidate.is_file():
        raise ValueError(f"Tutor source does not exist or is not a file: {raw_path}")
    relative = candidate.relative_to(root).as_posix()
    return f"{name.strip()}={relative}", candidate


def _resolve_source_fingerprints(
    project_root: Path,
    source_specs: Iterable[str],
) -> dict[str, str]:
    fingerprints: dict[str, str] = {}
    for source_spec in source_specs:
        normalized, path = _normalized_source_spec(project_root, source_spec)
        if normalized in fingerprints:
            raise ValueError(f"Duplicate Tutor source: {normalized}")
        fingerprints[normalized] = source_fingerprint(path.read_bytes())
    return fingerprints


def _current_fingerprints_for_session(
    store: TutorSessionStore,
    session: TutorSession,
    *,
    inspect_only: bool,
) -> dict[str, str]:
    if not session.source_fingerprints:
        return {}
    try:
        return _resolve_source_fingerprints(store.project_root, session.source_fingerprints.keys())
    except ValueError:
        if inspect_only:
            return {}
        raise


def _card_for_command(args: Any):
    composition = compose_packs(args.pack_ids)
    if not composition.applicable_design_priors:
        return None
    guidance = tutor_recommend(args.pack_ids, decision=args.decision, premise=args.premise)
    card = decision_card_from_guidance(guidance, source_subject=args.premise)
    depth = TutorDepth.EXPLAIN if args.tutor_command == "explain" else TutorDepth(args.depth)
    return card.with_depth(depth)


def _print_card(card, session_id: str | None = None) -> None:
    print("Decision Card")
    print(f"Decision: {card.decision}")
    print(f"Why it matters: {card.why_it_matters}")
    print(f"Recommended: {card.recommendation}")
    print(f"Alternatives: {', '.join(card.alternatives) or 'None recorded.'}")
    print(f"Depth: {card.depth.value}")
    print(f"Authority: {card.authority_status}")
    if session_id is not None:
        print(f"Session: {session_id} (LOCAL / NONCANONICAL)")


def _print_handoff(handoff: DecisionAuthorityHandoff) -> None:
    print("Decision-to-Authority Handoff")
    print(f"Status: {handoff.status}")
    if handoff.target_layer is not None:
        print(f"Owning layer: {handoff.target_layer}")
    if handoff.workflow is not None:
        print(f"Existing workflow: {handoff.workflow}")
    print(f"Why: {handoff.rationale}")
    for step in handoff.steps:
        print(f"{step.kind.title()}: {step.command} [{step.authority.value}]")
    if handoff.prerequisites:
        print("Prerequisites: " + "; ".join(handoff.prerequisites))
    print(f"Authority: {handoff.authority_status}")
    print("Story mutation: no")


def _print_proposal_result(result) -> None:
    print("Tutor-to-Structure Proposal")
    print(f"Proposal: {result.proposal_id}")
    print(f"Artifact: {result.proposal_path}")
    print(f"Selected Tutor intent: {result.selected_tutor_value}")
    print("Proposal selection: required before revision planning")
    print(f"Inspect: {result.inspect_command}")
    print(f"After selection: {result.next_command_after_selection}")
    print(f"Authority: {result.authority_status}")
    print("Story mutation: no")


def dispatch_tutor_commands(args: Any) -> int:
    """Dispatch the root Tutor workflow without mutating narrative authority."""
    try:
        if args.tutor_command in {"next", "explain"}:
            card = _card_for_command(args)
            if card is None:
                data = {"status": "no_decision", "card": None}
                if args.json:
                    print(json.dumps(data, indent=2))
                else:
                    print("No eligible Tutor decision is available from the supplied source.")
                    print("Authority: DERIVED / NOT CANON")
                return 0

            session_id = None
            if args.project is not None:
                if not args.source:
                    raise ValueError(
                        "Persisted Tutor sessions require at least one --source NAME=PATH "
                        "so currentness can be established later"
                    )
                fingerprints = _resolve_source_fingerprints(args.project, args.source)
                session = create_session(card, fingerprints)
                store = TutorSessionStore(args.project)
                try:
                    existing = store.load(session.session_id)
                except FileNotFoundError:
                    store.save(session)
                else:
                    session = existing
                session_id = session.session_id

            data = card.model_dump(mode="json")
            if session_id is not None:
                data = {"session_id": session_id, "card": data}
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                _print_card(card, session_id)
            return 0

        store = TutorSessionStore(args.project)
        session = store.load(args.session_id)
        if args.tutor_command == "show":
            current = _current_fingerprints_for_session(store, session, inspect_only=True)
            if session.source_fingerprints:
                session = store.refresh_status(session.session_id, current)
        elif args.tutor_command == "handoff":
            current = _current_fingerprints_for_session(store, session, inspect_only=True)
            if session.source_fingerprints:
                session = store.refresh_status(session.session_id, current)
            handoff = derive_decision_handoff(session)
            data = handoff.model_dump(mode="json")
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                _print_handoff(handoff)
            return 0
        elif args.tutor_command == "propose":
            current = _current_fingerprints_for_session(store, session, inspect_only=True)
            if session.source_fingerprints:
                session = store.refresh_status(session.session_id, current)
            handoff = derive_decision_handoff(session)
            if handoff.status != "route_identified" or handoff.workflow != "structure_revision":
                raise ValueError("Tutor session does not have a current supported Structure authority route")
            from auteur.llm.factory import build_client

            client = build_client(args.provider, args.model)
            result = generate_structure_proposal_from_tutor(args.project, session, client)
            data = result.model_dump(mode="json")
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                _print_proposal_result(result)
            return 0
        else:
            current = _current_fingerprints_for_session(store, session, inspect_only=False)
            session = store.record_response(
                session.session_id,
                args.action,
                args.value,
                current_source_fingerprints=current,
            )

        data = session.model_dump(mode="json")
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(f"Tutor session {session.session_id}: {session.status}")
            if session.response_action is not None:
                print(f"Response: {session.response_action.value}")
            if session.stale_reason:
                print(f"Stale reason: {session.stale_reason}")
            if args.tutor_command == "choose" and session.status == "resolved":
                print(
                    "Next: derive the owning authority route with "
                    f"`auteur tutor handoff {session.session_id} --project {args.project}`."
                )
            print(f"Session authority: {session.authority_status}")
            print(f"Decision authority: {session.card.authority_status}")
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
