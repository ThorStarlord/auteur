"""CLI for Counterfactual Narrative Planning — presentation and argument parsing only."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def register_simulate_subcommands(sub) -> None:
    """Register simulate subcommands under 'simulate'."""
    p = sub.add_parser("simulate", help="Counterfactual Narrative Planning — compare candidate-specific downstream projections without mutating project state.")
    ss = p.add_subparsers(dest="simulate_command", required=True)

    # create
    p_create = ss.add_parser("create", help="Create a counterfactual scenario.")
    p_create.add_argument("--project", type=Path, default=Path("."), help="Project root.")
    p_create.add_argument("--decision", required=True, help="Decision ID.")
    p_create.add_argument("--candidate", required=True, action="append", dest="candidates", help="Candidate ID (repeatable).")
    p_create.add_argument("--assume", action="append", default=None, help="Additional assumption.")
    p_create.add_argument("--baseline", default=None, help="Baseline ID (auto-captured if omitted).")
    p_create.add_argument("--json", action="store_true", help="Output JSON.")

    # status
    p_status = ss.add_parser("status", help="Show simulation status.")
    p_status.add_argument("--project", type=Path, default=Path("."), help="Project root.")
    p_status.add_argument("--json", action="store_true", help="Output JSON.")

    # inspect
    p_inspect = ss.add_parser("inspect", help="Inspect a scenario.")
    p_inspect.add_argument("scenario_id", type=str, help="Scenario ID.")
    p_inspect.add_argument("--project", type=Path, default=Path("."), help="Project root.")
    p_inspect.add_argument("--json", action="store_true", help="Output JSON.")
    p_inspect.add_argument("--evidence", action="store_true", help="Show consequence evidence.")
    p_inspect.add_argument("--uncertainty", action="store_true", help="Show uncertainty details.")
    p_inspect.add_argument("--plan", action="store_true", help="Show projected plan.")
    p_inspect.add_argument("--impact", action="store_true", help="Show projected impact.")

    # project
    p_proj = ss.add_parser("project", help="Run projection on a scenario.")
    p_proj.add_argument("scenario_id", type=str, help="Scenario ID.")
    p_proj.add_argument("--project", type=Path, default=Path("."), help="Project root.")
    p_proj.add_argument("--json", action="store_true", help="Output JSON.")

    # compare
    p_comp = ss.add_parser("compare", help="Compare two scenarios.")
    p_comp.add_argument("scenario_a", type=str, help="First scenario ID.")
    p_comp.add_argument("scenario_b", type=str, help="Second scenario ID.")
    p_comp.add_argument("--project", type=Path, default=Path("."), help="Project root.")
    p_comp.add_argument("--json", action="store_true", help="Output JSON.")

    # refresh
    p_refresh = ss.add_parser("refresh", help="Refresh a stale scenario (creates new lineage).")
    p_refresh.add_argument("scenario_id", type=str, help="Scenario ID.")
    p_refresh.add_argument("--project", type=Path, default=Path("."), help="Project root.")
    p_refresh.add_argument("--json", action="store_true", help="Output JSON.")

    # promote
    p_promo = ss.add_parser("promote", help="Promote a scenario into author review.")
    p_promo.add_argument("scenario_id", type=str, help="Scenario ID.")
    p_promo.add_argument("--project", type=Path, default=Path("."), help="Project root.")
    p_promo.add_argument("--confirm", action="store_true", required=True, help="Confirm promotion.")
    p_promo.add_argument("--json", action="store_true", help="Output JSON.")

    # discard
    p_disc = ss.add_parser("discard", help="Discard a scenario.")
    p_disc.add_argument("scenario_id", type=str, help="Scenario ID.")
    p_disc.add_argument("--project", type=Path, default=Path("."), help="Project root.")

    # history
    p_hist = ss.add_parser("history", help="Show simulation history.")
    p_hist.add_argument("scenario_id", nargs="?", default=None, help="Optional scenario ID.")
    p_hist.add_argument("--project", type=Path, default=Path("."), help="Project root.")
    p_hist.add_argument("--json", action="store_true", help="Output JSON.")

    # list
    p_list = ss.add_parser("list", help="List all scenarios.")
    p_list.add_argument("--project", type=Path, default=Path("."), help="Project root.")
    p_list.add_argument("--json", action="store_true", help="Output JSON.")


def _get_service(args) -> Any:
    from auteur.simulation.service import SimulationService
    return SimulationService(args.project)


def dispatch_simulate(args) -> int:
    """Dispatch simulate command to appropriate handler."""
    handlers = {
        "create": _handle_create,
        "status": _handle_status,
        "inspect": _handle_inspect,
        "project": _handle_project,
        "compare": _handle_compare,
        "refresh": _handle_refresh,
        "promote": _handle_promote,
        "discard": _handle_discard,
        "history": _handle_history,
        "list": _handle_list,
    }
    handler = handlers.get(args.simulate_command)
    if handler:
        return handler(args)
    print(f"Unknown simulate command: {args.simulate_command}", file=sys.stderr)
    return 1


def _handle_create(args) -> int:
    try:
        service = _get_service(args)
        first = True
        for cid in args.candidates:
            scenario = service.create_scenario(
                decision_id=args.decision,
                candidate_id=cid,
                assumptions=args.assume,
                baseline_id=args.baseline,
            )
            # Auto-project
            projected = service.project_scenario(scenario.scenario_id)
            if args.json:
                print(json.dumps(projected.to_dict(), indent=2, default=str))
            else:
                marker = "──" if first else ""
                print(f"{marker}Scenario: {projected.scenario_id}")
                print(f"  Decision: {projected.decision_id[:24]}...")
                print(f"  Candidate: {projected.candidate_id[:24]}...")
                print(f"  State: {projected.state.value}")
                print(f"  Consequences: {len(projected.projected_consequences)}")
                print(f"  Uncertainty: {projected.uncertainty_summary[:80]}")
                if first:
                    first = False
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
            print("Simulation Status")
            print(f"  Latest scenario: {result.get('latest_scenario_id', '(none)')[:24]}...")
            print(f"  Total scenarios: {result.get('total_scenarios', 0)}")
            print(f"  Active: {result.get('active_scenarios', 0)}")
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
        scenario = service.inspect(args.scenario_id)
        if scenario is None:
            print(f"Scenario not found: {args.scenario_id}", file=sys.stderr)
            return 1
        if args.json:
            d = scenario.to_dict()
            if args.evidence or args.impact:
                d["projected_consequences"] = [
                    {"target": c.target, "description": c.description,
                     "classification": c.classification.value, "confidence": c.confidence.value}
                    for c in scenario.projected_consequences
                ]
            if args.plan and scenario.projected_plan:
                d["projected_plan"] = {
                    "plan_id": scenario.projected_plan.plan_id,
                    "open_decision_count": scenario.projected_plan.open_decision_count,
                }
            print(json.dumps(d, indent=2, default=str))
        else:
            print(f"Scenario: {scenario.scenario_id}")
            print(f"  State: {scenario.state.value}")
            print(f"  Decision: {scenario.decision_id[:24]}...")
            print(f"  Candidate: {scenario.candidate_id[:24]}...")
            print(f"  Baseline: {scenario.baseline_id[:16]}...")
            print(f"  Assumptions: {len(scenario.assumptions)}")
            for a in scenario.assumptions:
                default = " (default)" if a.is_default else ""
                print(f"    - {a.description}{default}")
            if args.evidence or not (args.plan or args.impact):
                print(f"\n  Consequences ({len(scenario.projected_consequences)}):")
                for c in scenario.projected_consequences:
                    print(f"    [{c.classification.value.upper()}] [{c.confidence.value}] {c.description[:80]}")
                if scenario.uncertainty_summary:
                    print(f"\n  Uncertainty: {scenario.uncertainty_summary}")
            if args.plan and scenario.projected_plan:
                pp = scenario.projected_plan
                print("\n  Projected Plan:")
                print(f"    Open decisions: {pp.open_decision_count}")
                print(f"    Blocked milestones: {pp.blocked_milestone_count}")
            if args.impact:
                print("\n  Projected Impact:")
                for c in scenario.projected_consequences:
                    print(f"    {c.target[:40]}: {c.description[:60]}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_project(args) -> int:
    try:
        service = _get_service(args)
        projected = service.project_scenario(args.scenario_id)
        if args.json:
            print(json.dumps(projected.to_dict(), indent=2, default=str))
        else:
            print(f"Projection complete: {projected.scenario_id}")
            print(f"  State: {projected.state.value}")
            print(f"  Consequences: {len(projected.projected_consequences)}")
            for c in projected.projected_consequences[:10]:
                print(f"    [{c.classification.value.upper()}] {c.description[:80]}")
            if len(projected.projected_consequences) > 10:
                print(f"    ... and {len(projected.projected_consequences) - 10} more")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_compare(args) -> int:
    try:
        service = _get_service(args)
        comparison = service.compare_scenarios(args.scenario_a, args.scenario_b)
        if args.json:
            print(json.dumps({
                "comparison_id": comparison.comparison_id,
                "scenario_a_id": comparison.scenario_a_id,
                "scenario_b_id": comparison.scenario_b_id,
                "shared_consequences": len(comparison.shared_consequences),
                "a_only_consequences": len(comparison.a_only_consequences),
                "b_only_consequences": len(comparison.b_only_consequences),
                "opposing_consequences": len(comparison.opposing_consequences),
                "evidence_asymmetry": comparison.evidence_asymmetry,
                "uncertainty_asymmetry": comparison.uncertainty_asymmetry,
                "unknowns": comparison.unknowns,
                "milestone_differences": comparison.milestone_differences,
            }, indent=2, default=str))
        else:
            print("Scenario Comparison")
            print(f"  A: {comparison.scenario_a_id[:24]}...")
            print(f"  B: {comparison.scenario_b_id[:24]}...")
            print(f"  Shared consequences: {len(comparison.shared_consequences)}")
            print(f"  A only: {len(comparison.a_only_consequences)}")
            print(f"  B only: {len(comparison.b_only_consequences)}")
            print(f"  Opposing: {len(comparison.opposing_consequences)}")
            if comparison.evidence_asymmetry:
                print(f"  Evidence: {comparison.evidence_asymmetry}")
            if comparison.uncertainty_asymmetry:
                print(f"  Uncertainty: {comparison.uncertainty_asymmetry}")
            if comparison.unknowns:
                print(f"  Unknowns: {len(comparison.unknowns)}")
            if comparison.milestone_differences:
                print(f"  Milestone differences: {len(comparison.milestone_differences)}")
            print("\nThis comparison is not a winner ranking.")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_refresh(args) -> int:
    try:
        service = _get_service(args)
        # Refresh means recreating the scenario with a new baseline
        old = service.inspect(args.scenario_id)
        if old is None:
            print(f"Scenario not found: {args.scenario_id}", file=sys.stderr)
            return 1
        new_scenario = service.create_scenario(
            decision_id=old.decision_id,
            candidate_id=old.candidate_id,
            baseline_id=None,  # Auto-capture fresh baseline
        )
        new_projected = service.project_scenario(new_scenario.scenario_id)
        if args.json:
            print(json.dumps({
                "old_scenario_id": args.scenario_id,
                "new_scenario_id": new_projected.scenario_id,
                "state": new_projected.state.value,
            }, indent=2, default=str))
        else:
            print("Refresh created new lineage:")
            print(f"  Old: {args.scenario_id[:24]}...")
            print(f"  New: {new_projected.scenario_id[:24]}...")
            print(f"  State: {new_projected.state.value}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_promote(args) -> int:
    try:
        service = _get_service(args)
        result = service.promote_scenario(args.scenario_id, confirm=args.confirm)
        if args.json:
            print(json.dumps({
                "success": result.success,
                "review_session_id": result.review_session_id,
                "scenario_id": result.scenario_id,
                "error": result.error,
            }, indent=2, default=str))
        else:
            if result.success:
                print(f"Promoted to review session: {result.review_session_id[:24]}...")
                print(f"  Scenario: {result.scenario_id[:24]}...")
                print("  No acceptance was performed. Author choice remains pending.")
            else:
                print(f"Promotion failed: {result.error}", file=sys.stderr)
                return 1
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_discard(args) -> int:
    try:
        service = _get_service(args)
        service.discard_scenario(args.scenario_id)
        print(f"Discarded: {args.scenario_id[:24]}...")
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
        if args.scenario_id:
            entries = [e for e in entries if e.get("id", "").startswith(args.scenario_id)]
        if args.json:
            print(json.dumps(entries[:50], indent=2, default=str))
        else:
            if not entries:
                print("No simulation history.")
                return 0
            print(f"Simulation History ({len(entries)} entries)")
            for e in entries[:20]:
                ts = e.get("created_at", "?")[:19]
                kind = e.get("kind", "?")
                sid = e.get("id", "?")[:24]
                print(f"  [{ts}] {kind}: {sid}...")
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
        scenarios = service.list_scenarios()
        if args.json:
            print(json.dumps(scenarios, indent=2, default=str))
        else:
            if not scenarios:
                print("No scenarios.")
                return 0
            print(f"Scenarios ({len(scenarios)})")
            for s in scenarios:
                sid = s.get("scenario_id", "?")[:24]
                state = s.get("state", "?")
                dec = s.get("decision_id", "?")[:16]
                cand = s.get("candidate_id", "?")[:16]
                print(f"  {sid}...  [{state}] dec={dec}... cand={cand}...")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
