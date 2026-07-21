"""CLI for Author Decision Workspace — argparse subcommand registration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.decision.persistence import DecisionStore


def register_decision_subcommands(sub) -> None:
    """Register decision subcommands under 'decision'."""
    p = sub.add_parser("decision", help="Author Decision Workspace — composition of impact, convergence, reasoning, and reconciliation state.")
    ds = p.add_subparsers(dest="decision_command", required=True)

    p_status = ds.add_parser("status", help="Show workspace status and open decisions.")
    p_status.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_status.add_argument("--json", action="store_true", help="Output JSON.")

    p_list = ds.add_parser("list", help="List decisions with filters.")
    p_list.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_list.add_argument("--chapter", type=int, default=None, help="Filter by chapter.")
    p_list.add_argument("--json", action="store_true", help="Output JSON.")

    p_inspect = ds.add_parser("inspect", help="Inspect decision detail.")
    p_inspect.add_argument("decision_id", type=str, help="Decision ID.")
    p_inspect.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_inspect.add_argument("--json", action="store_true", help="Output JSON.")

    p_evidence = ds.add_parser("evidence", help="Show decision evidence breakdown.")
    p_evidence.add_argument("decision_id", type=str, help="Decision ID.")
    p_evidence.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")

    p_compare = ds.add_parser("compare", help="Compare candidates for decision.")
    p_compare.add_argument("decision_id", type=str, help="Decision ID.")
    p_compare.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")

    p_next = ds.add_parser("next", help="Show recommended next action.")
    p_next.add_argument("decision_id", type=str, help="Decision ID.")
    p_next.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")

    p_accept = ds.add_parser("prepare-acceptance", help="Verify acceptance readiness without accepting.")
    p_accept.add_argument("decision_id", type=str, help="Decision ID.")
    p_accept.add_argument("--candidate", type=str, required=True, help="Candidate ID to prepare.")
    p_accept.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")


def handle_decision_status(args) -> int:
    """Handle 'decision status' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        store = DecisionStore(args.project)
        decision_ids = store.list_snapshots()

        if not decision_ids:
            print("No open decisions")
            return 0

        if args.json:
            data = {"decisions": decision_ids, "count": len(decision_ids)}
            print(json.dumps(data, indent=2))
        else:
            print(f"Open decisions: {len(decision_ids)}")
            for did in decision_ids:
                print(f"  - {did}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_list(args) -> int:
    """Handle 'decision list' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        store = DecisionStore(args.project)
        decision_ids = store.list_snapshots()

        if not decision_ids:
            print("No open decisions")
            return 0

        if args.json:
            data = {"decisions": decision_ids, "count": len(decision_ids)}
            print(json.dumps(data, indent=2))
        else:
            print("Decisions:")
            for did in decision_ids:
                print(f"  {did}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_inspect(args) -> int:
    """Handle 'decision inspect' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        print(f"Decision: {args.decision_id}")
        print("(Detail inspection not yet implemented)")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_evidence(args) -> int:
    """Handle 'decision evidence' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        print(f"Evidence for {args.decision_id}:")
        print("(Evidence inspection not yet implemented)")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_compare(args) -> int:
    """Handle 'decision compare' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        print(f"Candidate comparison for {args.decision_id}:")
        print("(Comparison not yet implemented)")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_next(args) -> int:
    """Handle 'decision next' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        print(f"Next action for {args.decision_id}:")
        print("(Action recommendation not yet implemented)")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_prepare_acceptance(args) -> int:
    """Handle 'decision prepare-acceptance' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        print(f"Acceptance preparation for {args.decision_id} / {args.candidate}:")
        print("(Acceptance preparation not yet implemented)")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def dispatch_decision(args) -> int:
    """Dispatch to the appropriate decision handler."""
    handlers = {
        "status": handle_decision_status,
        "list": handle_decision_list,
        "inspect": handle_decision_inspect,
        "evidence": handle_decision_evidence,
        "compare": handle_decision_compare,
        "next": handle_decision_next,
        "prepare-acceptance": handle_decision_prepare_acceptance,
    }

    handler = handlers.get(args.decision_command)
    if handler is None:
        print(f"Error: Unknown decision command: {args.decision_command}", file=sys.stderr)
        return 1

    return handler(args)
