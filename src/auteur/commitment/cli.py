"""CLI for Portfolio Commitment and Coordinated Execution."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def register_commit_subcommands(sub) -> None:
    p = sub.add_parser("commit", help="Portfolio Commitment — select a portfolio direction and carry it through review and acceptance.")
    ps = p.add_subparsers(dest="commit_command", required=True)

    p_create = ps.add_parser("create", help="Create a portfolio commitment.")
    p_create.add_argument("--project", type=Path, default=Path("."))
    p_create.add_argument("--assignment", action="append", dest="assignments", help="decision_id=candidate_id (repeatable).")
    p_create.add_argument("--portfolio-scenario", default="")
    p_create.add_argument("--confirm", action="store_true", required=True)
    p_create.add_argument("--json", action="store_true")

    p_status = ps.add_parser("status", help="Show commitment status.")
    p_status.add_argument("--project", type=Path, default=Path("."))
    p_status.add_argument("--json", action="store_true")

    p_inspect = ps.add_parser("inspect", help="Inspect a commitment.")
    p_inspect.add_argument("commitment_id", type=str)
    p_inspect.add_argument("--project", type=Path, default=Path("."))
    p_inspect.add_argument("--json", action="store_true")

    p_plan = ps.add_parser("plan", help="Generate execution plan.")
    p_plan.add_argument("commitment_id", type=str)
    p_plan.add_argument("--project", type=Path, default=Path("."))
    p_plan.add_argument("--json", action="store_true")

    p_exec = ps.add_parser("execute", help="Execute safe steps.")
    p_exec.add_argument("commitment_id", type=str)
    p_exec.add_argument("--step", default=None, help="Specific step ID.")
    p_exec.add_argument("--project", type=Path, default=Path("."))
    p_exec.add_argument("--json", action="store_true")

    p_check = ps.add_parser("check", help="Scan for divergence.")
    p_check.add_argument("commitment_id", type=str)
    p_check.add_argument("--project", type=Path, default=Path("."))
    p_check.add_argument("--json", action="store_true")

    p_list = ps.add_parser("list", help="List commitments.")
    p_list.add_argument("--project", type=Path, default=Path("."))
    p_list.add_argument("--json", action="store_true")

    p_hist = ps.add_parser("history", help="Show commitment history.")
    p_hist.add_argument("--project", type=Path, default=Path("."))
    p_hist.add_argument("--json", action="store_true")


def _get_service(args) -> Any:
    from auteur.commitment.service import CommitmentService
    return CommitmentService(args.project)


def dispatch_commit(args) -> int:
    handlers = {
        "create": _handle_create,
        "status": _handle_status,
        "inspect": _handle_inspect,
        "plan": _handle_plan,
        "execute": _handle_execute,
        "check": _handle_check,
        "list": _handle_list,
        "history": _handle_history,
    }
    handler = handlers.get(args.commit_command)
    if handler:
        return handler(args)
    print(f"Unknown commit command: {args.commit_command}", file=sys.stderr)
    return 1


def _handle_create(args) -> int:
    try:
        service = _get_service(args)
        assignments = {}
        for a in args.assignments:
            parts = a.split("=", 1)
            if len(parts) == 2:
                assignments[parts[0]] = parts[1]
        commitment = service.create_commitment(
            assignments=assignments,
            portfolio_scenario_id=args.portfolio_scenario,
            confirm=args.confirm,
        )
        if args.json:
            print(json.dumps(commitment.to_dict(), indent=2, default=str))
        else:
            print(f"Commitment: {commitment.commitment_id}")
            print(f"  Assignments: {len(commitment.assignments)}")
            print(f"  State: {commitment.state.value}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_status(args) -> int:
    try:
        service = _get_service(args)
        result = service.status()
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"Commitment Status")
            print(f"  Latest: {result.get('latest_commitment_id', '(none)')[:24]}...")
            print(f"  Total: {result.get('total_commitments', 0)}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_inspect(args) -> int:
    try:
        service = _get_service(args)
        c = service.inspect(args.commitment_id)
        if c is None:
            print(f"Not found: {args.commitment_id}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(c.to_dict(), indent=2, default=str))
        else:
            print(f"Commitment: {c.commitment_id}")
            print(f"  State: {c.state.value}")
            print(f"  Assignments: {len(c.assignments)}")
            for d, ca in c.assignments.items():
                print(f"    {d[:24]}... → {ca[:24]}...")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_plan(args) -> int:
    try:
        service = _get_service(args)
        plan = service.plan(args.commitment_id)
        if args.json:
            print(json.dumps({"plan_id": plan.plan_id, "steps": len(plan.steps),
                              "steps_detail": [{"step_id": s.step_id, "type": s.step_type.value,
                                                "state": s.state.value, "safe": s.safe_to_execute}
                                               for s in plan.steps]}, indent=2, default=str))
        else:
            print(f"Execution Plan: {plan.plan_id[:24]}...")
            print(f"  Steps: {len(plan.steps)}")
            for s in plan.steps:
                safe = " [SAFE]" if s.safe_to_execute else " [AUTHOR]"
                print(f"    {s.step_id[:24]}... {s.step_type.value}{safe} ({s.state.value})")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_execute(args) -> int:
    try:
        service = _get_service(args)
        plan = service.execute(args.commitment_id, step_id=args.step)
        if args.json:
            steps_data = [{"step_id": s.step_id, "type": s.step_type.value,
                           "state": s.state.value, "result": s.result} for s in plan.steps]
            print(json.dumps({"plan_id": plan.plan_id, "steps": steps_data}, indent=2, default=str))
        else:
            print(f"Execution: {plan.plan_id[:24]}...")
            for s in plan.steps:
                status = "✓" if s.state.value == "completed" else ("✗" if s.state.value == "failed" else "·")
                print(f"  {status} {s.step_type.value} ({s.state.value})")
                if s.result:
                    print(f"     {s.result[:80]}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_check(args) -> int:
    try:
        service = _get_service(args)
        findings = service.check(args.commitment_id)
        if args.json:
            print(json.dumps([{"type": f.divergence_type.value, "severity": f.severity.value,
                                "description": f.description} for f in findings], indent=2, default=str))
        else:
            if not findings:
                print("No divergence detected.")
            else:
                print(f"Divergence: {len(findings)} finding(s)")
                for f in findings:
                    print(f"  [{f.severity.value.upper()}] {f.divergence_type.value}: {f.description[:80]}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_list(args) -> int:
    try:
        service = _get_service(args)
        commitments = service.list_commitments()
        if args.json:
            print(json.dumps(commitments, indent=2, default=str))
        else:
            if not commitments:
                print("No commitments.")
                return 0
            print(f"Commitments ({len(commitments)})")
            for c in commitments:
                print(f"  {c.get('commitment_id', '?')[:24]}... [{c.get('state', '?')}] assignments={c.get('assignments', 0)}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_history(args) -> int:
    try:
        service = _get_service(args)
        entries = service.history()
        if args.json:
            print(json.dumps(entries[:50], indent=2, default=str))
        else:
            if not entries:
                print("No history.")
                return 0
            print(f"History ({len(entries)} entries)")
            for e in entries[:20]:
                print(f"  [{e.get('created_at', '?')[:19]}] {e.get('kind', '?')}: {e.get('id', '?')[:24]}...")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
