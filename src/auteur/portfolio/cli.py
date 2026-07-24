"""CLI for Narrative Decision Portfolio."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def register_portfolio_subcommands(sub) -> None:
    p = sub.add_parser("portfolio", help="Narrative Decision Portfolio — compare coherent candidate combinations across multiple decisions.")
    ps = p.add_subparsers(dest="portfolio_command", required=True)

    p_create = ps.add_parser("create", help="Create a portfolio from decisions and candidates.")
    p_create.add_argument("--project", type=Path, default=Path("."))
    p_create.add_argument("--decision", required=True, action="append", dest="decisions", help="Decision ID (repeatable).")
    p_create.add_argument("--candidate", required=True, action="append", dest="candidates", help="Candidate ID (repeatable, paired with --decision order).")
    p_create.add_argument("--max-combinations", type=int, default=100)
    p_create.add_argument("--json", action="store_true")

    p_gen = ps.add_parser("generate", help="Generate candidate combinations.")
    p_gen.add_argument("portfolio_id", type=str)
    p_gen.add_argument("--project", type=Path, default=Path("."))
    p_gen.add_argument("--json", action="store_true")

    p_proj = ps.add_parser("project", help="Project effects for a scenario.")
    p_proj.add_argument("scenario_id", type=str)
    p_proj.add_argument("portfolio_id", type=str)
    p_proj.add_argument("--project", type=Path, default=Path("."))
    p_proj.add_argument("--json", action="store_true")

    p_comp = ps.add_parser("compare", help="Compare two portfolio scenarios.")
    p_comp.add_argument("scenario_a", type=str)
    p_comp.add_argument("scenario_b", type=str)
    p_comp.add_argument("portfolio_id", type=str)
    p_comp.add_argument("--project", type=Path, default=Path("."))
    p_comp.add_argument("--json", action="store_true")

    p_front = ps.add_parser("frontier", help="Calculate non-dominated frontier.")
    p_front.add_argument("portfolio_id", type=str)
    p_front.add_argument("--dimension", action="append", default=None, dest="dimensions", help="Dimension (repeatable).")
    p_front.add_argument("--project", type=Path, default=Path("."))
    p_front.add_argument("--json", action="store_true")

    p_promo = ps.add_parser("promote", help="Promote a portfolio scenario into review.")
    p_promo.add_argument("scenario_id", type=str)
    p_promo.add_argument("portfolio_id", type=str)
    p_promo.add_argument("--project", type=Path, default=Path("."))
    p_promo.add_argument("--confirm", action="store_true", required=True)
    p_promo.add_argument("--json", action="store_true")

    p_status = ps.add_parser("status", help="Show portfolio status.")
    p_status.add_argument("--project", type=Path, default=Path("."))
    p_status.add_argument("--json", action="store_true")

    p_inspect = ps.add_parser("inspect", help="Inspect a portfolio.")
    p_inspect.add_argument("portfolio_id", type=str)
    p_inspect.add_argument("--project", type=Path, default=Path("."))
    p_inspect.add_argument("--json", action="store_true")

    p_list = ps.add_parser("list", help="List portfolios.")
    p_list.add_argument("--project", type=Path, default=Path("."))
    p_list.add_argument("--json", action="store_true")

    p_hist = ps.add_parser("history", help="Show portfolio history.")
    p_hist.add_argument("--project", type=Path, default=Path("."))
    p_hist.add_argument("--json", action="store_true")

    p_disc = ps.add_parser("discard", help="Discard a portfolio.")
    p_disc.add_argument("portfolio_id", type=str)
    p_disc.add_argument("--project", type=Path, default=Path("."))

    p_refresh = ps.add_parser("refresh", help="Refresh a portfolio (new baseline).")
    p_refresh.add_argument("portfolio_id", type=str)
    p_refresh.add_argument("--project", type=Path, default=Path("."))
    p_refresh.add_argument("--json", action="store_true")


def _get_service(args) -> Any:
    from auteur.portfolio.service import PortfolioService
    return PortfolioService(args.project)


def dispatch_portfolio(args) -> int:
    handlers = {
        "create": _handle_create,
        "generate": _handle_generate,
        "project": _handle_project,
        "compare": _handle_compare,
        "frontier": _handle_frontier,
        "promote": _handle_promote,
        "status": _handle_status,
        "inspect": _handle_inspect,
        "list": _handle_list,
        "history": _handle_history,
        "discard": _handle_discard,
        "refresh": _handle_refresh,
    }
    handler = handlers.get(args.portfolio_command)
    if handler:
        return handler(args)
    print(f"Unknown portfolio command: {args.portfolio_command}", file=sys.stderr)
    return 1


def _handle_create(args) -> int:
    try:
        service = _get_service(args)
        # Pair decisions with candidates
        dec_cands: dict[str, list[str]] = {}
        for d, c in zip(args.decisions, args.candidates):
            dec_cands.setdefault(d, []).append(c)
        portfolio = service.create_portfolio(dec_cands, max_combinations=args.max_combinations)
        if args.json:
            print(json.dumps(portfolio.to_dict(), indent=2, default=str))
        else:
            print(f"Portfolio: {portfolio.portfolio_id}")
            print(f"  Decisions: {len(portfolio.decisions)}")
            print(f"  State: {portfolio.state.value}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_generate(args) -> int:
    try:
        service = _get_service(args)
        portfolio = service.generate_combinations(args.portfolio_id)
        if args.json:
            print(json.dumps(portfolio.to_dict(), indent=2, default=str))
        else:
            print(f"Combinations: {portfolio.theoretical_count} theoretical, {portfolio.valid_count} valid")
            print(f"Excluded: {len(portfolio.excluded_combinations)}")
            for ex in portfolio.excluded_combinations[:5]:
                print(f"  Excluded: {ex.reason}")
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
        projected = service.project_scenario(args.scenario_id, args.portfolio_id)
        if args.json:
            print(json.dumps({
                "scenario_id": projected.scenario_id,
                "state": projected.state.value,
                "stale_artifacts": projected.stale_artifact_count,
                "uncertainty": projected.uncertainty_summary,
            }, indent=2, default=str))
        else:
            print(f"Projected: {projected.scenario_id[:24]}...")
            print(f"  State: {projected.state.value}")
            print(f"  Stale artifacts: {projected.stale_artifact_count}")
            print(f"  Uncertainty: {projected.uncertainty_summary[:80]}")
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
        comp = service.compare_scenarios(args.scenario_a, args.scenario_b, args.portfolio_id)
        if args.json:
            print(json.dumps({
                "comparison_id": comp.comparison_id,
                "staleness_difference": comp.staleness_difference,
                "open_decision_difference": comp.open_decision_difference,
                "blocked_milestone_difference": comp.blocked_milestone_difference,
            }, indent=2, default=str))
        else:
            print(f"Comparison: {comp.comparison_id[:24]}...")
            print(f"  Shared effects: {comp.shared_effects}")
            print(f"  Staleness diff: {comp.staleness_difference}")
            print(f"  Decision diff: {comp.open_decision_difference}")
            print(f"  Milestone diff: {comp.blocked_milestone_difference}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_frontier(args) -> int:
    try:
        service = _get_service(args)
        dims = args.dimensions
        frontier = service.calculate_frontier(args.portfolio_id, dimensions=dims)
        if args.json:
            print(json.dumps({
                "frontier_id": frontier.frontier_id,
                "dimensions": frontier.dimensions,
                "non_dominated_count": len(frontier.non_dominated_ids),
                "non_dominated_ids": frontier.non_dominated_ids,
                "explanations": frontier.explanations,
            }, indent=2, default=str))
        else:
            print(f"Frontier ({', '.join(frontier.dimensions)})")
            print(f"  Non-dominated: {len(frontier.non_dominated_ids)}")
            for e in frontier.explanations[:5]:
                print(f"    {e}")
            print(f"  No artistic winner is selected.")
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
        result = service.promote_scenario(args.scenario_id, args.portfolio_id, confirm=args.confirm)
        if args.json:
            print(json.dumps({
                "success": result.success,
                "review_session_ids": result.review_session_ids,
                "state": result.state,
            }, indent=2, default=str))
        else:
            if result.success:
                print(f"Promoted: {len(result.review_session_ids)} review sessions")
                for sid in result.review_session_ids:
                    print(f"  Review: {sid[:24]}...")
                print("  No acceptance was performed.")
            else:
                print(f"Promotion failed: {result.state}", file=sys.stderr)
                return 1
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
            print(f"Portfolio Status")
            print(f"  Latest: {result.get('latest_portfolio_id', '(none)')[:24]}...")
            print(f"  Total: {result.get('total_portfolios', 0)}")
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
        portfolio = service.inspect(args.portfolio_id)
        if portfolio is None:
            print(f"Not found: {args.portfolio_id}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(portfolio.to_dict(), indent=2, default=str))
        else:
            print(f"Portfolio: {portfolio.portfolio_id}")
            print(f"  State: {portfolio.state.value}")
            print(f"  Decisions: {len(portfolio.decisions)}")
            print(f"  Scenarios: {len(portfolio.scenarios)}")
            print(f"  Excluded: {len(portfolio.excluded_combinations)}")
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
        portfolios = service.list_portfolios()
        if args.json:
            print(json.dumps(portfolios, indent=2, default=str))
        else:
            if not portfolios:
                print("No portfolios.")
                return 0
            print(f"Portfolios ({len(portfolios)})")
            for p in portfolios:
                print(f"  {p.get('portfolio_id', '?')[:24]}... [{p.get('state', '?')}] scenarios={p.get('scenarios', 0)}")
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


def _handle_discard(args) -> int:
    print(f"Discard not implemented for {args.portfolio_id[:24]}...")
    return 0


def _handle_refresh(args) -> int:
    print(f"Refresh not implemented for {args.portfolio_id[:24]}...")
    return 0
