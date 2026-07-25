"""CLI for Decision Lifecycle Integration (v0.14.0)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def register_lifecycle_subcommands(sub) -> None:
    p = sub.add_parser(
        "lifecycle",
        help="Decision Lifecycle — see where every decision is across planning, simulation, portfolio, commitment, and review.",
    )
    ps = p.add_subparsers(dest="lifecycle_command", required=True)

    p_status = ps.add_parser("status", help="Show lifecycle for all decisions.")
    p_status.add_argument("--project", type=Path, default=Path("."))
    p_status.add_argument("--json", action="store_true")

    p_inspect = ps.add_parser("inspect", help="Show lifecycle for one decision.")
    p_inspect.add_argument("decision_id", type=str)
    p_inspect.add_argument("--project", type=Path, default=Path("."))
    p_inspect.add_argument("--json", action="store_true")

    p_summary = ps.add_parser("summary", help="Show aggregate lifecycle counts per stage.")
    p_summary.add_argument("--project", type=Path, default=Path("."))
    p_summary.add_argument("--json", action="store_true")

    p_fill = ps.add_parser("fill", help="Fill lifecycle gaps automatically (requires --confirm).")
    p_fill.add_argument("--gap", default=None, choices=["simulate", "portfolio", "promote"],
                        help="Specific gap type to fill.")
    p_fill.add_argument("--confirm", action="store_true", required=True)
    p_fill.add_argument("--project", type=Path, default=Path("."))
    p_fill.add_argument("--json", action="store_true")


def _get_service(args) -> Any:
    from auteur.lifecycle.service import LifecycleService
    return LifecycleService(args.project)


def _handle_fill(args) -> int:
    import json as _json
    try:
        from auteur.lifecycle.filler import LifecycleFiller
        filler = LifecycleFiller(args.project)

        if args.gap:
            results = filler.fill_gap(args.gap, confirm=args.confirm)
        else:
            # Show fillable gaps
            gaps = filler.detect_fillable_gaps()
            if args.json:
                print(_json.dumps(gaps, indent=2, default=str))
            else:
                if not gaps:
                    print("No fillable gaps detected.")
                    return 0
                print("Fillable gaps:")
                for g in gaps:
                    print(f"  [{g['gap_type']}] {g['title']}")
                    print(f"       {g['description']}")
                    print(f"       → {g['command']}")
            return 0

        if args.json:
            print(_json.dumps(results, indent=2, default=str))
        else:
            for r in results:
                status_icon = {"created": "✓", "skipped": "·", "failed": "✗"}.get(r.get("status", ""), "?")
                print(f"  {status_icon} {r.get('action', '?')}: {r.get('message', '')[:80]}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def dispatch_lifecycle(args) -> int:
    """Dispatch lifecycle command to appropriate handler."""
    handlers = {
        "status": _handle_status,
        "inspect": _handle_inspect,
        "summary": _handle_summary,
        "fill": _handle_fill,
    }

    handler = handlers.get(args.lifecycle_command)
    if handler:
        return handler(args)
    print(f"Unknown lifecycle command: {args.lifecycle_command}", file=sys.stderr)
    return 1


def _handle_status(args) -> int:
    try:
        svc = _get_service(args)
        entries = svc.status()
        if args.json:
            print(json.dumps([e.to_dict() for e in entries], indent=2, default=str))
        else:
            if not entries:
                print("No decisions found.")
                return 0
            # Header
            print(f"{'Decision':<28} {'Stage':<20} {'Sim':<5} {'Portfolio':<10} {'Review':<14} {'Commit':<10} {'Diverged':<9}")
            print("-" * 100)
            for e in entries:
                did = e.decision_id[:26] + ".." if len(e.decision_id) > 26 else e.decision_id
                sim = str(e.simulation_count)
                port = "✓" if e.portfolio_ids else "─"
                rv = e.review_session_id[:12] + ".." if len(e.review_session_id) > 12 else (e.review_session_id or "─")
                cm = e.commitment_id[:8] + ".." if len(e.commitment_id) > 8 else (e.commitment_id or "─")
                dv = "⚠" if e.diverged else "─"
                print(f"{did:<28} {e.stage.value:<20} {sim:<5} {port:<10} {rv:<14} {cm:<10} {dv:<9}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_inspect(args) -> int:
    try:
        svc = _get_service(args)
        entry = svc.inspect(args.decision_id)
        if entry is None:
            print(f"Not found: {args.decision_id}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(entry.to_dict(), indent=2, default=str))
        else:
            print(f"Decision: {entry.decision_id}")
            print(f"  Stage:      {entry.stage.value}")
            if entry.description:
                print(f"  Description: {entry.description}")
            print(f"  Simulations: {entry.simulation_count}")
            print(f"  Portfolios:  {entry.portfolio_ids if entry.portfolio_ids else '(none)'}")
            print(f"  Review:      {entry.review_session_id or '(none)'}")
            print(f"  Commitment:  {entry.commitment_id or '(none)'}")
            if entry.commitment_id:
                print(f"  Expected:    {entry.expected_candidate}")
                print(f"  Current:     {entry.current_candidate}")
                print(f"  Diverged:    {'YES' if entry.diverged else 'no'}")
            if entry.gaps:
                print(f"  Gaps:")
                for g in entry.gaps:
                    print(f"    • {g}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_summary(args) -> int:
    try:
        svc = _get_service(args)
        summary = svc.summary()
        if args.json:
            print(json.dumps(summary.to_dict(), indent=2, default=str))
        else:
            print(f"Decision Lifecycle Summary")
            print(f"  Total decisions:  {summary.total_decisions}")
            print(f"  By stage:")
            for stage_key in LifecycleStageOrder:
                count = summary.by_stage.get(stage_key, 0)
                if count > 0:
                    print(f"    {stage_key:<20} {count}")
            print(f"  Simulated:        {summary.simulated}")
            print(f"  In portfolio:     {summary.in_portfolio}")
            print(f"  Under review:     {summary.under_review}")
            print(f"  Accepted:         {summary.accepted}")
            print(f"  Committed:        {summary.committed}")
            print(f"  Diverged:         {summary.diverged}")
            print(f"  With gaps:        {summary.with_gaps}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


LifecycleStageOrder = [
    "open", "evidence_gathered", "simulated", "portfolio",
    "compared", "promoted", "under_review", "acceptance_ready",
    "accepted", "committed",
]
