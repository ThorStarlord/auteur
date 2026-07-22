"""CLI for Author Decision Workspace — argparse subcommand registration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.decision.persistence import DecisionStore
from auteur.decision.service import DecisionWorkspaceService


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

        service = DecisionWorkspaceService(args.project)
        status = service.status()

        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"Decision Workspace Status — {status['project']}")
            print(f"  Total decisions: {status['total_decisions']}")
            if status["highest_priority_readiness"] != "none":
                print(f"  Highest priority: {status['highest_priority_readiness']}")
            if status["ready_for_acceptance"] > 0:
                print(f"  Ready for acceptance: {status['ready_for_acceptance']}")
            if status["blocked_decisions"] > 0:
                print(f"  Blocked: {status['blocked_decisions']}")
            if status["open_impact_findings"] > 0:
                print(f"  Open impact findings: {status['open_impact_findings']}")

            for readiness, count in sorted(status.get("decisions_by_readiness", {}).items()):
                if count > 0:
                    print(f"    {readiness}: {count}")

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

        service = DecisionWorkspaceService(args.project)
        chapter_filter = args.chapter if hasattr(args, "chapter") else None
        decisions = service.list_decisions(chapter_index=chapter_filter)

        if not decisions:
            print("No open decisions")
            return 0

        if args.json:
            data = {
                "decisions": [
                    {
                        "decision_id": d.decision_id,
                        "chapter_index": d.chapter_index,
                        "target_artifact_id": d.target_artifact_id,
                        "readiness": d.readiness.value,
                        "trigger_type": d.trigger_type.value,
                        "candidate_count": len(d.candidates),
                    }
                    for d in decisions
                ],
                "count": len(decisions),
            }
            print(json.dumps(data, indent=2))
        else:
            print(f"Decisions ({len(decisions)}):")
            for d in decisions:
                print(
                    f"  {d.decision_id[:8]}... "
                    f"ch{d.chapter_index} {d.target_artifact_id} "
                    f"({d.readiness.value})"
                )

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

        service = DecisionWorkspaceService(args.project)
        decision = service.inspect(args.decision_id)

        if args.json:
            data = {
                "decision_id": decision.decision_id,
                "project": decision.project,
                "chapter_index": decision.chapter_index,
                "target_artifact_id": decision.target_artifact_id,
                "scene_id": decision.scene_id,
                "trigger_type": decision.trigger_type.value,
                "trigger_ids": decision.trigger_ids,
                "readiness": decision.readiness.value,
                "lifecycle_state": decision.lifecycle_state.value,
                "freshness": decision.freshness.value,
                "candidates": [
                    {
                        "candidate_id": c.candidate_id,
                        "status": c.status,
                        "freshness": c.freshness.value,
                        "obligations_satisfied": c.obligations_satisfied,
                        "obligations_unsatisfied": c.obligations_unsatisfied,
                    }
                    for c in decision.candidates
                ],
                "evidence_count": len(decision.evidence),
                "blocker_count": len(decision.blockers),
                "unresolved_choices": len(decision.unresolved_choices),
            }
            print(json.dumps(data, indent=2))
        else:
            print(f"Decision: {decision.decision_id}")
            print(f"  Project: {decision.project}")
            print(f"  Chapter: {decision.chapter_index}")
            print(f"  Target: {decision.target_artifact_id}")
            print(f"  Readiness: {decision.readiness.value}")
            print(f"  Status: {decision.lifecycle_state.value}")
            print(f"  Freshness: {decision.freshness.value}")
            print(f"  Trigger: {decision.trigger_type.value} ({len(decision.trigger_ids)} IDs)")
            print(f"  Candidates: {len(decision.candidates)}")
            print(f"  Evidence: {len(decision.evidence)} pieces")
            if decision.blockers:
                print(f"  Blockers: {len(decision.blockers)}")
                for blocker in decision.blockers:
                    print(f"    - {blocker}")
            if decision.unresolved_choices:
                print(f"  Unresolved choices: {len(decision.unresolved_choices)}")
                for choice in decision.unresolved_choices:
                    print(f"    - {choice.question}")

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_evidence(args) -> int:
    """Handle 'decision evidence' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        evidence_list = service.evidence_for_decision(args.decision_id)

        if not evidence_list:
            print(f"No evidence for decision {args.decision_id}")
            return 0

        print(f"Evidence for {args.decision_id}:")
        print()

        # Group by classification
        by_classification = {}
        for e in evidence_list:
            key = e.classification.value
            if key not in by_classification:
                by_classification[key] = []
            by_classification[key].append(e)

        for classification in ["fact", "derived_inference", "recommendation", "author_choice"]:
            items = by_classification.get(classification, [])
            if items:
                print(f"  {classification.upper().replace('_', ' ')} ({len(items)}):")
                for e in items:
                    print(f"    [{e.source_subsystem.value}] {e.claim}")
                    if e.supporting_reference:
                        print(f"      ref: {e.supporting_reference}")
                    if e.freshness.value != "current":
                        print(f"      [{e.freshness.value}]")
                print()

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_compare(args) -> int:
    """Handle 'decision compare' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        comparison = service.compare_candidates(args.decision_id)

        if args.json:
            print(json.dumps(comparison, indent=2))
        else:
            print(f"Candidate Comparison for {args.decision_id}:")
            print()
            if not comparison.get("comparison_available"):
                print(f"  No comparison available: {comparison.get('reason')}")
                print(f"  Candidates: {', '.join(comparison.get('candidates', []))}")
            else:
                print(f"  Comparison ID: {comparison.get('comparison_id')}")
                print(f"  Candidates: {', '.join(comparison.get('candidates', []))}")
                if comparison.get("dimensions"):
                    print(f"  Dimensions compared: {len(comparison.get('dimensions', []))}")
                    for dim in comparison.get("dimensions", []):
                        print(f"    - {dim.get('name')}")
                if comparison.get("conflicts"):
                    print(f"  Conflicts: {len(comparison.get('conflicts', []))}")
                    for conf in comparison.get("conflicts", []):
                        print(f"    - {conf.get('description')}")
                if comparison.get("recommended_candidate"):
                    print(f"  Recommended: {comparison.get('recommended_candidate')}")

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_next(args) -> int:
    """Handle 'decision next' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        next_action = service.next_action(args.decision_id)

        if next_action.get("action") is None:
            print(f"No further action for {args.decision_id}")
            print(f"  Readiness: {next_action.get('readiness')}")
            print(f"  {next_action.get('reason')}")
            return 0

        if args.json:
            print(json.dumps(next_action, indent=2))
        else:
            print(f"Next Action for {args.decision_id}:")
            print(f"  {next_action.get('title')}")
            print(f"  Reason: {next_action.get('reason')}")
            if next_action.get("command"):
                print(f"  Command: {next_action.get('command')}")
            print(f"  Safe to execute: {next_action.get('safe_to_execute')}")
            print(f"  Authority level: {next_action.get('authority_level')}")
            if next_action.get("expected_result_state"):
                print(f"  Expected result: {next_action.get('expected_result_state')}")

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_prepare_acceptance(args) -> int:
    """Handle 'decision prepare-acceptance' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        preparation = service.prepare_acceptance(args.decision_id, args.candidate)

        if args.json:
            data = {
                "decision_id": preparation.decision_id,
                "candidate_id": preparation.candidate_id,
                "is_ready": preparation.is_ready,
                "blockers": preparation.blockers,
                "verification_results": preparation.verification_results,
                "affected_downstream": preparation.affected_downstream,
            }
            print(json.dumps(data, indent=2))
        else:
            status_str = "READY FOR ACCEPTANCE" if preparation.is_ready else "NOT READY"
            print(f"Acceptance Preparation: {status_str}")
            print(f"  Decision: {preparation.decision_id}")
            print(f"  Candidate: {preparation.candidate_id}")
            print()

            if preparation.blockers:
                print("Blockers:")
                for blocker in preparation.blockers:
                    print(f"  - {blocker}")
                print()

            print("Verification:")
            for check, passed in sorted(preparation.verification_results.items()):
                status = "✓" if passed else "✗"
                print(f"  {status} {check}")

            if preparation.affected_downstream:
                print()
                print("Affected downstream:")
                for affected in preparation.affected_downstream:
                    print(f"  - {affected}")

        return 0 if preparation.is_ready else 1

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
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
