"""Read-only author-facing commands for derived reasoning reviews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def _freshness_label(review: dict[str, Any]) -> str:
    freshness = review.get("freshness")
    if isinstance(freshness, dict):
        return freshness.get("status", "unknown")
    return str(freshness) if freshness is not None else "unknown"


def format_review(review: dict[str, Any]) -> str:
    lines = [
        f"Reasoning review {review.get('review_id', '(unnamed)')}",
        f"Status: {_freshness_label(review)}",
    ]
    stale = review.get("freshness", {}).get("stale_reports", []) if isinstance(review.get("freshness"), dict) else []
    if stale:
        lines.append(f"Stale reports: {', '.join(stale)}")
    lines.append("Top concerns:")
    for item in sorted(review.get("priorities", []), key=lambda value: value.get("rank", 0)):
        group = next((candidate for candidate in review.get("groups", [])
                      if candidate.get("group_id") == item.get("group_id")), None)
        if group is None:
            continue
        marker = "CONFLICT" if group.get("conflict") else ""
        affected = f" [{', '.join(group.get('affected_artifacts', []))}]" if group.get("affected_artifacts") else ""
        lines.append(f"  {item.get('rank')}. {group.get('summary')} {marker}{affected}".rstrip())
        lines.append(f"     Next: {group.get('next_action', 'Inspect the source reasoning.')}")
    lines.append(f"Source reports: {len(review.get('source_reports', []))}")
    lines.append("Use --json for provenance and full claim references.")
    return "\n".join(lines)


def load_review(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))



def _handle_reasoning_book(project: Path, json_output: bool = False) -> int:
    """Run Book Manuscript reasoning and display findings."""
    from auteur.reasoning.runtime import (
        CriticRegistry,
        ReasoningRuntime,
        RuntimeRequest,
        resolve_report_dir,
    )
    from auteur.reasoning.registrar import register_all_builtins

    report_dir = resolve_report_dir(project)
    registry = CriticRegistry()
    register_all_builtins(registry)
    runtime = ReasoningRuntime(registry, report_dir)

    request = RuntimeRequest(
        request_id="book_reasoning",
        critic_ids=["book.manuscript"],
        inputs={"project": project},
    )
    result = runtime.run(request)
    outcomes = result.outcomes

    if json_output:
        output: list[dict[str, object]] = []
        for outcome in outcomes:
            entry: dict[str, object] = {
                "critic_id": outcome.critic_id,
                "version": outcome.version,
                "status": outcome.status.value,
            }
            if outcome.reason:
                entry["reason"] = outcome.reason
            if outcome.error:
                entry["error"] = outcome.error
            if outcome.report_id:
                report_path = report_dir / f"{outcome.report_id}.json"
                if report_path.exists():
                    entry["report"] = json.loads(
                        report_path.read_text(encoding="utf-8")
                    )
            output.append(entry)
        print(json.dumps(output, indent=2, default=str))
        return 0

    for outcome in outcomes:
        print(f"Critic: {outcome.critic_id} ({outcome.version})")
        print(f"  Status: {outcome.status.value}")
        if outcome.status.value == "failed":
            print(f"  Error: {outcome.error or outcome.reason or 'unknown'}")
            continue
        if outcome.report_id:
            report_path = report_dir / f"{outcome.report_id}.json"
            if report_path.exists():
                report = json.loads(report_path.read_text(encoding="utf-8"))
                findings = report.get("findings", [])
                if not findings:
                    print("  No findings.")
                for index, finding in enumerate(findings, 1):
                    severity = finding.get("severity", "info")
                    print(
                        f"  {index}. [{severity}] "
                        f"{finding.get('message', '(no message)')}"
                    )
                    evidence = finding.get("evidence", {})
                    if evidence:
                        for key, value in evidence.items():
                            if value:
                                print(f"     {key}: {value}")
                    recommendations = finding.get("recommendations", [])
                    if recommendations:
                        print("     Recommendations:")
                        for recommendation in recommendations:
                            print(f"       - {recommendation}")
    return 0


def dispatch_reasoning(
    args: Any,
    error_writer: Callable[[str], None],
) -> int:
    """Dispatch the complete reasoning CLI family behind one bounded owner."""
    if args.reasoning_command == "book":
        return _handle_reasoning_book(args.project, args.json)

    try:
        review = load_review(args.review)
    except FileNotFoundError:
        error_writer(f"reasoning review not found: {args.review}")
        return 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        error_writer(f"invalid reasoning review {args.review}: {exc}")
        return 1

    if args.reasoning_command == "review":
        print(
            json.dumps(review, indent=2, sort_keys=True)
            if args.json
            else format_review(review)
        )
        return 0

    group = next(
        (
            item
            for item in review.get("groups", [])
            if item.get("group_id") == args.group
        ),
        None,
    )
    if group is None:
        group = next(
            (
                summary
                for summary in review.get("critic_summaries", [])
                if summary.get("critic_id") == args.group
                or summary.get("critic_id") == f"draft.{args.group}"
                or summary.get("critic_id", "").replace("draft.", "") == args.group
            ),
            None,
        )
    if group is None:
        error_writer(f"reasoning group not found: {args.group}")
        return 1

    print(
        json.dumps(group, indent=2, sort_keys=True)
        if args.json
        else (
            f"{group.get('group_id', group.get('critic_id'))}: "
            f"{group.get('summary', group.get('status', '?'))}\n"
            f"Basis: {group.get('overlap_basis', '')}\n"
            f"Claims: {group.get('claim_refs', group.get('finding_count', 0))}"
        )
    )
    return 0
