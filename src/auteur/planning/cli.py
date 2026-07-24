"""CLI for Project-Level Narrative Planning — rendering and argument handling only."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from auteur.planning.models import PlanningHorizon


def register_plan_subcommands(sub) -> None:
    """Register plan subcommands under 'plan'."""
    p = sub.add_parser("plan", help="Project-Level Narrative Planning — coordinate decisions, sessions, milestones, and critical paths across an entire manuscript.")
    ps = p.add_subparsers(dest="plan_command", required=True)

    # plan status
    p_status = ps.add_parser("status", help="Show project plan summary.")
    p_status.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_status.add_argument("--json", action="store_true", help="Output JSON.")
    p_status.add_argument("--chapter", type=int, default=None, help="Scope to chapter.")
    p_status.add_argument("--book", action="store_true", help="Scope to book.")

    # plan graph
    p_graph = ps.add_parser("graph", help="Show dependency graph.")
    p_graph.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_graph.add_argument("--json", action="store_true", help="Output JSON.")
    p_graph.add_argument("--chapter", type=int, default=None, help="Scope to chapter.")
    p_graph.add_argument("--book", action="store_true", help="Scope to book.")

    # plan next
    p_next = ps.add_parser("next", help="Show recommended next action.")
    p_next.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_next.add_argument("--json", action="store_true", help="Output JSON.")
    p_next.add_argument("--chapter", type=int, default=None, help="Scope to chapter.")
    p_next.add_argument("--execute", action="store_true", help="Execute safe actions if recommended.")

    # plan critical-path
    p_cp = ps.add_parser("critical-path", help="Show blocking critical path.")
    p_cp.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_cp.add_argument("--json", action="store_true", help="Output JSON.")
    p_cp.add_argument("--chapter", type=int, default=None, help="Scope to chapter.")
    p_cp.add_argument("--book", action="store_true", help="Scope to book.")
    p_cp.add_argument("--act", type=int, default=None, help="Scope to act.")

    # plan milestones
    p_mil = ps.add_parser("milestones", help="Show milestone state.")
    p_mil.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_mil.add_argument("--json", action="store_true", help="Output JSON.")

    # plan explain
    p_exp = ps.add_parser("explain", help="Explain a node or action ID.")
    p_exp.add_argument("node_or_action_id", type=str, help="Node or action ID to explain.")
    p_exp.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_exp.add_argument("--json", action="store_true", help="Output JSON.")

    # plan refresh
    p_refresh = ps.add_parser("refresh", help="Create fresh plan snapshot from current state.")
    p_refresh.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_refresh.add_argument("--json", action="store_true", help="Output JSON.")
    p_refresh.add_argument("--chapter", type=int, default=None, help="Scope to chapter.")
    p_refresh.add_argument("--book", action="store_true", help="Scope to book.")
    p_refresh.add_argument("--save", action="store_true", default=True, help="Save plan snapshot (default: True).")
    p_refresh.add_argument("--no-save", action="store_false", dest="save", help="Skip saving plan snapshot.")

    # plan history
    p_hist = ps.add_parser("history", help="Show plan history.")
    p_hist.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_hist.add_argument("--json", action="store_true", help="Output JSON.")

    # plan list
    p_list = ps.add_parser("list", help="List all plan snapshots.")
    p_list.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_list.add_argument("--json", action="store_true", help="Output JSON.")

    # plan render (backward-compatible Cartographer plan)
    p_render = ps.add_parser("render", help="Render Cartographer prompt for a chapter (no LLM call).")
    p_render.add_argument("blueprint", type=Path)
    p_render.add_argument("chapter", type=int)


def resolve_horizon(args) -> tuple[PlanningHorizon, int | None]:
    """Resolve planning horizon from CLI arguments."""
    if getattr(args, "book", False):
        return PlanningHorizon.BOOK, None
    if getattr(args, "act", None) is not None:
        return PlanningHorizon.ACT, args.act
    if getattr(args, "chapter", None) is not None:
        return PlanningHorizon.CHAPTER, args.chapter
    return PlanningHorizon.PROJECT, None


def _get_service(args) -> Any:
    """Get planning service from args."""
    from auteur.planning.service import PlanningService
    return PlanningService(args.project)


def handle_plan_status(args) -> int:
    """Handle 'plan status' command."""
    try:
        service = _get_service(args)
        horizon, chapter = resolve_horizon(args)
        result = service.status(horizon=horizon, chapter_index=chapter)

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get("has_plan"):
                print(f"Project Plan Status")
                print(f"  Plan ID: {result['plan_id'][:16]}...")
                print(f"  Created: {result.get('created_at', 'unknown')[:19]}")
                print(f"  Horizon: {result.get('horizon', 'project')}")
                print(f"  Title: {result.get('title', '')}")
                print(f"  Open decisions: {result.get('open_decision_count', 0)}")
                print(f"  Active review sessions: {result.get('active_review_session_count', 0)}")
                print(f"  Blocked milestones: {result.get('blocked_milestone_count', 0)}")
                if result.get("is_stale"):
                    print(f"  [STALE] {result.get('stale_reason', '')}")
                print(f"\nRun 'auteur plan refresh' to create a fresh plan.")
            else:
                print(result.get("message", "No plan available."))

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_plan_graph(args) -> int:
    """Handle 'plan graph' command."""
    try:
        service = _get_service(args)
        horizon, chapter = resolve_horizon(args)
        plan = service.refresh(horizon=horizon, chapter_index=chapter, save=False)

        if args.json:
            print(json.dumps({
                "plan_id": plan.plan_id,
                "nodes": [_n_to_dict(n) for n in plan.nodes],
                "edges": [_e_to_dict(e) for e in plan.edges],
                "cycles": plan.cycles,
            }, indent=2, default=str))
        else:
            print(f"Dependency Graph — {plan.title}")
            print(f"  Nodes: {len(plan.nodes)}, Edges: {len(plan.edges)}")
            if plan.cycles:
                print(f"  Cycles: {len(plan.cycles)} DETECTED")
                for i, cycle in enumerate(plan.cycles, 1):
                    print(f"    Cycle {i}: {' → '.join(c[:12] for c in cycle)}")
            print()
            for n in plan.nodes:
                print(f"  [{n.node_type.value.upper()}] {n.node_id[:16]}... {n.label}")
                deps = [e for e in plan.edges if e.target_id == n.node_id]
                if deps:
                    for d in deps:
                        print(f"    <- {d.dependency_type.value} ({d.strength.value}) from {d.source_id[:16]}...")
                rev = [e for e in plan.edges if e.source_id == n.node_id]
                if rev:
                    for d in rev:
                        print(f"    -> {d.dependency_type.value} ({d.strength.value}) to {d.target_id[:16]}...")

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_plan_next(args) -> int:
    """Handle 'plan next' command."""
    try:
        service = _get_service(args)
        horizon, chapter = resolve_horizon(args)
        plan = service.refresh(horizon=horizon, chapter_index=chapter, save=False)

        if args.json:
            action = plan.recommended_next_action
            print(json.dumps({
                "plan_id": plan.plan_id,
                "recommended_next_action": _a_to_dict(action) if action else None,
                "safe_parallel_work": [_p_to_dict(g) for g in plan.safe_parallel_work],
                "authority_required_actions": [_a_to_dict(a) for a in plan.authority_required_actions],
            }, indent=2, default=str))
        else:
            if plan.cycles:
                print(f"⚠  {len(plan.cycles)} hard cycle(s) detected — resolve before proceeding.")
                for i, cycle in enumerate(plan.cycles, 1):
                    print(f"  Cycle {i}: {' → '.join(c[:12] for c in cycle)}")

            action = plan.recommended_next_action
            if action:
                print(f"Recommended Next Action")
                print(f"  Title: {action.title}")
                print(f"  Reason: {action.reason}")
                print(f"  Authority: {action.authority.value}")
                print(f"  Safe to execute: {action.safe_to_execute}")
                if action.command:
                    print(f"  Command: {action.command}")
                if action.blocked_milestones_released:
                    print(f"  Releases: {len(action.blocked_milestones_released)} milestone(s)")
            else:
                print("No next action — all project work is current.")

            if plan.safe_parallel_work:
                print(f"\nSafe parallel work:")
                for g in plan.safe_parallel_work:
                    print(f"  Group: {', '.join(a[:16] for a in g.action_ids)}")

            if plan.authority_required_actions:
                print(f"\nRequires author authority:")
                for a in plan.authority_required_actions:
                    print(f"  {a.title}")

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_plan_critical_path(args) -> int:
    """Handle 'plan critical-path' command."""
    try:
        service = _get_service(args)
        horizon, chapter = resolve_horizon(args)
        plan = service.refresh(horizon=horizon, chapter_index=chapter, save=False)

        if args.json:
            print(json.dumps({
                "plan_id": plan.plan_id,
                "critical_paths": [_cp_to_dict(cp) for cp in plan.critical_paths],
            }, indent=2, default=str))
        else:
            if not plan.critical_paths:
                print("No blocking critical path — no blocked nodes detected.")
                return 0

            for i, cp in enumerate(plan.critical_paths):
                print(f"Critical Path {i + 1} (leverage: {cp.cumulative_leverage:.1f})")
                print(f"  {cp.explanation}")
                if cp.authority_required_steps:
                    print(f"\n  Authority-required steps:")
                    for nid in cp.authority_required_steps:
                        n = next((n for n in plan.nodes if n.node_id == nid), None)
                        label = n.label if n else nid
                        print(f"    {label} [AUTHOR]")
                if cp.blocked_milestone_ids:
                    print(f"\n  Blocked milestones: {len(cp.blocked_milestone_ids)}")
                    for mid in cp.blocked_milestone_ids[:5]:
                        m = next((m for m in plan.milestones if m.milestone_id == mid), None)
                        if m:
                            print(f"    {m.title} ({m.state.value})")
                if i < len(plan.critical_paths) - 1:
                    print()

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_plan_milestones(args) -> int:
    """Handle 'plan milestones' command."""
    try:
        service = _get_service(args)
        plan = service.refresh(save=False)

        if args.json:
            print(json.dumps({
                "plan_id": plan.plan_id,
                "milestones": [_m_to_dict(m) for m in plan.milestones],
            }, indent=2, default=str))
        else:
            if not plan.milestones:
                print("No milestones defined.")
                return 0

            counts = {}
            for m in plan.milestones:
                counts[m.state.value] = counts.get(m.state.value, 0) + 1

            print(f"Milestones — {plan.title}")
            print(f"  {counts.get('completed', 0)} completed")
            print(f"  {counts.get('in_progress', 0)} in progress")
            print(f"  {counts.get('blocked', 0)} blocked")
            print(f"  {counts.get('ready', 0)} ready")
            print(f"  {counts.get('not_started', 0)} not started")
            print(f"  {counts.get('stale', 0)} stale")
            print()

            for m in plan.milestones:
                indicator = {
                    "completed": "✓",
                    "in_progress": "►",
                    "blocked": "✗",
                    "ready": "○",
                    "not_started": "·",
                    "stale": "!",
                }.get(m.state.value, "?")
                print(f"  {indicator} [{m.state.value.upper()}] {m.title}")
                if m.blocked_conditions:
                    for bc in m.blocked_conditions[:2]:
                        print(f"       blocked: {bc}")
                if m.status_reason:
                    print(f"       {m.status_reason}")

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_plan_explain(args) -> int:
    """Handle 'plan explain' command."""
    try:
        service = _get_service(args)
        result = service.explain_node(args.node_or_action_id)

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if not result.get("found"):
                print(f"Not found: {args.node_or_action_id}")
                return 0

            if "node_id" in result and "action_id" not in result:
                print(f"Node: {result.get('label', result['node_id'])}")
                print(f"  ID: {result['node_id']}")
                print(f"  Type: {result.get('node_type', '?')}")
                print(f"  Source: {result.get('source_subsystem', '?')}")
                print(f"  Freshness: {result.get('freshness', '?')}")
                if result.get("in_cycles"):
                    print(f"  [IN CYCLE]")
                if result.get("blocked_milestones"):
                    print(f"  Blocked milestones: {', '.join(result['blocked_milestones'])}")
            else:
                print(f"Action: {result.get('title', '?')}")
                print(f"  ID: {result.get('action_id', '?')}")
                print(f"  Reason: {result.get('reason', '?')}")
                print(f"  Authority: {result.get('authority', '?')}")
                print(f"  Safe to execute: {result.get('safe_to_execute', '?')}")

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_plan_refresh(args) -> int:
    """Handle 'plan refresh' command."""
    try:
        service = _get_service(args)
        horizon, chapter = resolve_horizon(args)
        plan = service.refresh(
            horizon=horizon,
            chapter_index=chapter,
            save=getattr(args, "save", True),
        )

        if args.json:
            print(json.dumps(plan.to_dict(), indent=2, default=str))
        else:
            print(f"Plan refreshed: {plan.title}")
            print(f"  Plan ID: {plan.plan_id}")
            print(f"  Horizon: {plan.horizon.value}")
            print(f"  Open decisions: {plan.open_decision_count}")
            print(f"  Active review sessions: {plan.active_review_session_count}")
            print(f"  Blocked milestones: {plan.blocked_milestone_count}")
            print(f"  Critical paths: {len(plan.critical_paths)}")
            if plan.recommended_next_action:
                print(f"  Next action: {plan.recommended_next_action.title}")
            if plan.cycles:
                print(f"  ⚠  {len(plan.cycles)} hard cycle(s) detected")

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_plan_history(args) -> int:
    """Handle 'plan history' command."""
    try:
        service = _get_service(args)
        entries = service.history()

        if args.json:
            print(json.dumps(entries, indent=2, default=str))
        else:
            if not entries:
                print("No plan history available.")
                return 0

            print(f"Plan History ({len(entries)} entries)")
            for entry in entries[:20]:  # Show last 20
                ts = entry.get("timestamp", "?")[:19]
                ct = entry.get("change_type", "?")
                desc = entry.get("description", "?")
                print(f"  [{ts}] {ct}: {desc}")

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_plan_list(args) -> int:
    """Handle 'plan list' command."""
    try:
        service = _get_service(args)
        snapshots = service.list_plans()

        if args.json:
            print(json.dumps(snapshots, indent=2, default=str))
        else:
            if not snapshots:
                print("No plan snapshots available.")
                return 0

            print(f"Plan Snapshots ({len(snapshots)})")
            for s in snapshots:
                stale = " [STALE]" if s.get("is_stale") else ""
                print(f"  {s.get('plan_id', '?')[:16]}...  {s.get('created_at', '?')[:19]}  "
                      f"decisions={s.get('open_decision_count', 0)}  "
                      f"sessions={s.get('active_review_session_count', 0)}  "
                      f"blocked={s.get('blocked_milestone_count', 0)}{stale}")

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def handle_plan_render(args) -> int:
    """Handle 'plan render' command (backward-compatible Cartographer plan)."""
    try:
        from auteur.blueprint import StoryBlueprint
        from auteur.cli_handlers import handle_plan
        from auteur.cli_formatters import format_plan

        bp = StoryBlueprint.from_yaml(args.blueprint)
        result = handle_plan(bp, args.chapter)
        if not result.is_success:
            print(result.error or "Cartographer plan failed", file=sys.stderr)
            return result.exit_code
        out = format_plan(result)
        if out:
            print(out)
        return 0
    except FileNotFoundError as e:
        print(f"Error: blueprint file not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def dispatch_plan(args) -> int:
    """Dispatch plan command to appropriate handler."""
    handlers = {
        "status": handle_plan_status,
        "graph": handle_plan_graph,
        "next": handle_plan_next,
        "critical-path": handle_plan_critical_path,
        "milestones": handle_plan_milestones,
        "explain": handle_plan_explain,
        "refresh": handle_plan_refresh,
        "history": handle_plan_history,
        "list": handle_plan_list,
        "render": handle_plan_render,
    }
    handler = handlers.get(args.plan_command)
    if handler:
        return handler(args)
    print(f"Unknown plan command: {args.plan_command}", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def _n_to_dict(n) -> dict:
    return {
        "node_id": n.node_id,
        "node_type": n.node_type.value,
        "label": n.label,
        "chapter_index": n.chapter_index,
        "source_subsystem": n.source_subsystem,
        "source_ref": n.source_ref,
        "freshness": n.freshness,
    }


def _e_to_dict(e) -> dict:
    return {
        "edge_id": e.edge_id,
        "source_id": e.source_id,
        "target_id": e.target_id,
        "dependency_type": e.dependency_type.value,
        "strength": e.strength.value,
        "reason": e.reason,
    }


def _m_to_dict(m) -> dict:
    return {
        "milestone_id": m.milestone_id,
        "title": m.title,
        "scope": m.scope.value,
        "state": m.state.value,
        "chapter_index": m.chapter_index,
        "blocked_conditions": m.blocked_conditions,
        "status_reason": m.status_reason,
    }


def _cp_to_dict(cp) -> dict:
    return {
        "path_id": cp.path_id,
        "ordered_node_ids": cp.ordered_node_ids,
        "blocked_milestone_ids": cp.blocked_milestone_ids,
        "cumulative_leverage": cp.cumulative_leverage,
        "authority_required_steps": cp.authority_required_steps,
        "safe_steps": cp.safe_steps,
        "explanation": cp.explanation,
    }


def _a_to_dict(a) -> dict | None:
    if a is None:
        return None
    return {
        "action_id": a.action_id,
        "title": a.title,
        "reason": a.reason,
        "authority": a.authority.value,
        "safe_to_execute": a.safe_to_execute,
        "command": a.command,
        "source_node_id": a.source_node_id,
        "expected_result_state": a.expected_result_state,
        "blocked_milestones_released": a.blocked_milestones_released,
    }


def _p_to_dict(g) -> dict:
    return {
        "group_id": g.group_id,
        "action_ids": g.action_ids,
        "authority_categories": g.authority_categories,
    }
