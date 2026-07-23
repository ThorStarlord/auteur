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
    p_list.add_argument("--readiness", type=str, default=None, help="Filter by readiness (blocked, needs_evaluation, etc).")
    p_list.add_argument("--stale", action="store_true", help="Show only stale decisions.")
    p_list.add_argument("--fresh", action="store_true", help="Show only non-stale decisions.")
    p_list.add_argument("--requires-author", action="store_true", help="Show only decisions needing author input.")
    p_list.add_argument("--bypass-low-priority", action="store_true", help="Suppress info-level findings.")
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

    p_impact = ds.add_parser("impact-preview", help="Simulate downstream impact of accepting a candidate.")
    p_impact.add_argument("decision_id", type=str, help="Decision ID.")
    p_impact.add_argument("--candidate", type=str, required=True, help="Candidate ID to evaluate.")
    p_impact.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_impact.add_argument("--json", action="store_true", help="Output JSON.")

    p_history = ds.add_parser("history", help="Show decision snapshot history.")
    p_history.add_argument("decision_id", type=str, help="Decision ID.")
    p_history.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_history.add_argument("--json", action="store_true", help="Output JSON.")

    p_lineage = ds.add_parser("lineage", help="Show decision lineage chain.")
    p_lineage.add_argument("decision_id", type=str, help="Decision ID.")
    p_lineage.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_lineage.add_argument("--json", action="store_true", help="Output JSON.")

    p_diff = ds.add_parser("diff", help="Compare two decision snapshots.")
    p_diff.add_argument("snapshot_a", type=str, help="First snapshot ID.")

    p_refresh = ds.add_parser("refresh", help="Refresh decision snapshots from latest state.")
    p_refresh.add_argument("--decision", type=str, default=None, help="Specific decision ID to refresh (default: all).")
    p_refresh.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_refresh.add_argument("--json", action="store_true", help="Output JSON.")

    p_revalidate = ds.add_parser("revalidate", help="Run deterministic validation on a decision.")
    p_revalidate.add_argument("decision_id", type=str, help="Decision ID.")
    p_revalidate.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_revalidate.add_argument("--json", action="store_true", help="Output JSON.")
    p_diff.add_argument("snapshot_b", type=str, help="Second snapshot ID.")

    p_conflicts = ds.add_parser("conflicts", help="Show active conflicts for a decision.")
    p_conflicts.add_argument("decision_id", type=str, help="Decision ID.")
    p_conflicts.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_conflicts.add_argument("--json", action="store_true", help="Output JSON.")
    p_diff.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_diff.add_argument("--json", action="store_true", help="Output JSON.")


def handle_decision_history(args) -> int:
    """Handle 'decision history' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        entries = service.history(args.decision_id)

        if not entries:
            print(f"No history found for decision: {args.decision_id}")
            return 0

        if args.json:
            print(json.dumps({"decision_id": args.decision_id, "entries": entries}, indent=2))
        else:
            print(f"Decision History — {args.decision_id}")
            for i, entry in enumerate(entries, 1):
                print(f"  {i}. [{entry['snapshot_id'][:8]}…] "
                      f"readiness={entry['readiness']}, "
                      f"state={entry['lifecycle_state']}, "
                      f"freshness={entry['freshness']}")
                if entry.get("recorded_at"):
                    print(f"     recorded: {entry['recorded_at']}")
                if entry.get("preceding_snapshot_id"):
                    print(f"     parent: {entry['preceding_snapshot_id'][:8]}…")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_lineage(args) -> int:
    """Handle 'decision lineage' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        decisions = service.lineage(args.decision_id)

        if not decisions:
            print(f"No lineage found for decision: {args.decision_id}")
            return 0

        if args.json:
            print(json.dumps({
                "decision_id": args.decision_id,
                "snapshots": [d.snapshot_id for d in decisions],
            }, indent=2))
        else:
            print(f"Decision Lineage — {args.decision_id}")
            print(f"  Depth: {len(decisions)} snapshot(s)")
            for i, d in enumerate(decisions, 1):
                sid = d.snapshot_id or "unknown"
                prev = d.preceding_snapshot_id or "(root)"
                print(f"  {i}. snapshot={sid[:16]}…")
                print(f"       preceding={prev[:16]}…")
                print(f"       readiness={d.readiness.value}, state={d.lifecycle_state.value}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_diff(args) -> int:
    """Handle 'decision diff' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        result = service.diff(args.snapshot_a, args.snapshot_b)

        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            return 1

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if not result["has_changes"]:
                print("No differences between snapshots.")
            else:
                print(f"Differences — {result['decision_id']}")
                print(f"  {result['snapshot_a'][:8]}… → {result['snapshot_b'][:8]}…")
                for field, change in result["changes"].items():
                    print(f"  {field}: {change['from']} → {change['to']}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


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
    """Handle 'decision list' command with filters."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)

        # Build filter parameters
        stale_filter = None
        if hasattr(args, "stale") and args.stale:
            stale_filter = True
        if hasattr(args, "fresh") and args.fresh:
            stale_filter = False

        decisions = service.list_decisions(
            chapter_index=getattr(args, "chapter", None),
            readiness=getattr(args, "readiness", None),
            stale=stale_filter,
            requires_author=getattr(args, "requires_author", None) or None,
            bypass_low_priority=getattr(args, "bypass_low_priority", None) or None,
        )
        if not decisions:
            if getattr(args, "json", False):
                print(json.dumps({"decisions": [], "count": 0}))
            else:
                print("No decisions match the current filters")
            return 0

        # Build JSON response when --json is set
        json_data = {
            "decisions": [
                {
                    "decision_id": d.decision_id,
                    "chapter_index": d.chapter_index,
                    "target_artifact_id": d.target_artifact_id,
                    "readiness": d.readiness.value,
                    "lifecycle_state": d.lifecycle_state.value,
                    "freshness": d.freshness.value,
                    "trigger_type": d.trigger_type.value,
                    "candidate_count": len(d.candidates),
                }
                for d in decisions
            ],
            "count": len(decisions),
        }

        if getattr(args, "json", False):
            print(json.dumps(json_data, indent=2))
        else:
            print(f"Decisions ({len(decisions)}):")
            for d in decisions:
                print(
                    f"  {d.decision_id[:8]}... "
                    f"ch{d.chapter_index} {d.target_artifact_id[:24]:24s} "
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

        if getattr(args, "json", False):
            import dataclasses, json as _json
            print(_json.dumps(decision, indent=2, default=str))
        else:
            print(f"Decision: {decision.decision_id}")
            print(f"  Chapter: {decision.chapter_index}")
            print(f"  Target: {decision.target_artifact_id}")
            print(f"  Readiness: {decision.readiness.value}")
            print(f"  Lifecycle: {decision.lifecycle_state.value}")
            print(f"  Freshness: {decision.freshness.value}")
            print(f"  Candidates: {len(decision.candidates)}")
            print(f"  Evidence: {len(decision.evidence)} items")
            if decision.blockers:
                print(f"  Blockers:")
                for b in decision.blockers:
                    print(f"    - {b}")
            if decision.unresolved_choices:
                print(f"  Open choices:")
                for c in decision.unresolved_choices:
                    print(f"    - {c.question}")
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




def handle_decision_impact_preview(args) -> int:
    """Handle 'decision impact-preview' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        preview = service.impact_preview(args.decision_id, args.candidate)

        if getattr(args, "json", False):
            import dataclasses, json as _json
            print(_json.dumps(dataclasses.asdict(preview), indent=2, default=str))
        else:
            print(f"Impact Preview — {args.decision_id}")
            print(f"  Candidate: {preview.candidate_id}")
            print(f"  Target: {preview.target_artifact_id}")
            print(f"  Summary: {preview.downstream_work_summary}")
            if preview.definite_impacts:
                print(f"\n  Definite impacts ({len(preview.definite_impacts)}):")
                for imp in preview.definite_impacts:
                    ch = f"ch{imp.chapter_index} " if imp.chapter_index else ""
                    print(f"    - {ch}{imp.artifact_id} ({imp.artifact_type})")
            if preview.inferred_impacts:
                print(f"\n  Inferred impacts ({len(preview.inferred_impacts)}):")
                for imp in preview.inferred_impacts:
                    ch = f"ch{imp.chapter_index} " if imp.chapter_index else ""
                    print(f"    - {ch}{imp.artifact_id} ({imp.artifact_type})")
            print(f"\n  Cost score: {preview.total_cost_score()}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def handle_decision_refresh(args) -> int:
    """Handle 'decision refresh' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        result = service.refresh_snapshots(decision_id=getattr(args, "decision", None))

        if getattr(args, "json", False):
            import json as _json
            print(_json.dumps(result, indent=2))
        else:
            if result.get("status") == "ok":
                saved = result.get("saved", result.get("snapshot_id", "?"))
                print(f"Refresh OK — saved {saved}")
            else:
                print(f"Refresh failed: {result.get('error', 'unknown')}")
                return 1
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_decision_revalidate(args) -> int:
    """Handle 'decision revalidate' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        result = service.run_validation(args.decision_id)

        if getattr(args, "json", False):
            import json as _json
            print(_json.dumps(result, indent=2))
        else:
            if result.get("status") == "ok":
                issues = result.get("issues", [])
                if issues:
                    print(f"Validation issues ({len(issues)}):")
                    for issue in issues:
                        print(f"  - {issue}")
                else:
                    print(f"Validation OK — no issues for {args.decision_id}")
            else:
                print(f"Validation failed: {result.get('error', 'unknown')}")
                return 1
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def handle_decision_conflicts(args) -> int:
    """Handle 'decision conflicts' command."""
    try:
        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
            return 1

        service = DecisionWorkspaceService(args.project)
        conflicts = service.conflicts(args.decision_id)

        if getattr(args, "json", False):
            import dataclasses, json as _json
            print(_json.dumps([dataclasses.asdict(c) for c in conflicts], indent=2, default=str))
        else:
            if not conflicts:
                print(f"No active conflicts for decision: {args.decision_id}")
                return 0
            print(f"Active Conflicts — {args.decision_id} ({len(conflicts)} total)")
            for i, c in enumerate(conflicts, 1):
                print(f"\n  {i}. [{c.conflict_type.value}] {c.title}")
                print(f"     Boundary: {c.resolution_boundary.value}")
                print(f"     Source: {c.source_subsystem.value if c.source_subsystem else 'unknown'}")
                for claim in c.claims:
                    print(f"     · [{claim.get('subsystem','?')}] {claim.get('claim','')[:100]}")
        return 0
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
        "impact-preview": handle_decision_impact_preview,
        "conflicts": handle_decision_conflicts,
        "refresh": handle_decision_refresh,
        "revalidate": handle_decision_revalidate,
        "history": handle_decision_history,
        "lineage": handle_decision_lineage,
        "diff": handle_decision_diff,
    }

    handler = handlers.get(args.decision_command)
    if handler is None:
        print(f"Error: Unknown decision command: {args.decision_command}", file=sys.stderr)
        return 1

    return handler(args)
