"""Format functions for expression CLI output — separates presentation from dispatch.

Each ``format_*`` function returns a string to be printed by the caller.
JSON mode returns ``json.dumps(…)``; human mode returns multi-line text.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any

import yaml


def _to_json(data: Any, *, default: Callable[[Any], Any] = str) -> str:
    """Serialize *data* to JSON, handling both plain dicts and Pydantic models."""
    if hasattr(data, "model_dump"):
        return json.dumps(data.model_dump(mode="json"), indent=2, default=default)
    return json.dumps(data, indent=2, default=default)


# ---------------------------------------------------------------------------
# Basic subcommand formatters
# ---------------------------------------------------------------------------


def format_generate(candidate_id: str) -> str:
    """Format a ``generate`` result — just the candidate ID."""
    return candidate_id


def format_compose_chapter(artifact_id: str) -> str:
    """Format a ``compose-chapter`` result — just the artifact ID."""
    return artifact_id


def format_inspect(
    metadata: Any,
    status: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format an ``inspect`` result (single prose candidate).

    Always includes both human-readable summary and full JSON (matching
    the original CLI behavior).
    """
    actions = "; ".join(status.get("recommended_actions", []))
    summary = (
        f"Candidate {metadata.candidate_id} ({metadata.source_scene.artifact_id})\n"
        f"Status: {status['lifecycle']}; freshness: {status['freshness']}; "
        f"review: {status['review_state']}\n"
        f"Recommended actions: {actions}"
    )
    payload = json.dumps(
        {"metadata": metadata.model_dump(mode="json"), "status": status},
        indent=2,
    )
    return f"{summary}\n{payload}"


def format_compare(data: Mapping[str, Any]) -> str:
    """Format a ``compare`` result as JSON."""
    return json.dumps(data, indent=2)


def format_reject_accept(metadata: Any) -> str:
    """Format a ``reject`` / ``accept`` / ``revalidate`` / ``acknowledge`` result."""
    return json.dumps(metadata.model_dump(mode="json"), indent=2)


def format_inspect_chapter(
    metadata: Any,
    status: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format an ``inspect-chapter`` result."""
    if json_mode or verbose:
        return json.dumps(
            {"metadata": metadata.model_dump(mode="json"), "status": status},
            indent=2,
        )
    lines = [
        f"Chapter {metadata.source_chapter['artifact_id']} | "
        f"assembly revision {metadata.revision} | {metadata.lifecycle.value} | "
        f"{status['freshness']} | {status['health']}",
    ]
    for scene in metadata.source_scenes:
        lines.append(
            f"  {scene['scene_id']} -> prose_v{scene['expression_revision']:03d} "
            f"({scene['freshness']})"
        )
    for transition in metadata.transitions:
        lines.append(
            f"  transition {transition['transition_id']} "
            f"({transition['before_scene']} -> {transition['after_scene']})"
        )
    if status.get("stale_reasons"):
        lines.append("Recommended action: recompose or review the affected dependencies.")
    return "\n".join(lines)


def format_accept_chapter(metadata: Any) -> str:
    """Format an ``accept-chapter`` result."""
    return json.dumps(metadata.model_dump(mode="json"), indent=2)


def format_inspect_manuscript(data: Mapping[str, Any]) -> str:
    """Format an ``inspect-manuscript`` result."""
    return json.dumps(data, indent=2)


def format_compare_chapters(report: Mapping[str, Any]) -> str:
    """Format a ``compare-chapters`` result."""
    return json.dumps(report, indent=2)


# ---------------------------------------------------------------------------
# Reconciliation subcommand formatters
# ---------------------------------------------------------------------------


def format_reconcile_plan(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a reconciliation ``plan`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    lines = [
        "Reconciliation application plan",
        f"Status: {result['readiness']}",
        "Selected proposals:",
    ]
    for proposal_id in result["proposal_ids"]:
        lines.append(f"- {proposal_id}")
    lines.append("Planned outputs:")
    for output in result["planned_outputs"]:
        lines.append(
            f"- {output['output_type']} for "
            f"{output.get('target_scene', output.get('target_transition'))}"
        )
    lines.append("No canonical artifacts will be changed.")
    if result["readiness"] != "ready":
        lines.append(
            "Resolve the listed freshness or conflict findings before proceeding."
        )
    return "\n".join(lines)


def format_reconcile_show_plan(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a reconciliation ``show-plan`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    if verbose:
        return yaml.safe_dump(result, sort_keys=False)
    return (
        f"Reconciliation application plan {result['application_set_id']}\n"
        f"Status: {result['readiness']}\n"
        f"Selected proposals: {len(result['proposal_ids'])}\n"
        "No canonical artifacts will be changed."
    )


def format_reconcile_publish_error(
    exc: ValueError,
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a reconciliation ``publish`` rejection error."""
    result = getattr(exc, "result", {
        "status": "rejected_stale",
        "message": str(exc),
        "visible_outputs_created": False,
    })
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    lines = ["Publication stopped: application plan is stale."]
    for reason in result.get("stale_reasons", []):
        lines.append(
            f"- {reason.get('code')}: "
            f"{reason.get('recommended_action', reason.get('detail', 'dependency changed'))}"
        )
    lines.extend([
        "No candidates or Chapter preview were created.",
        "Next action: Create a new reconciliation inspection and application plan.",
    ])
    return "\n".join(lines)


def format_reconcile_publish(
    result: Mapping[str, Any],
    json_mode: bool = False,
) -> str:
    """Format a reconciliation ``publish`` success result."""
    if json_mode:
        return json.dumps(result, indent=2)
    return (
        f"Reconciliation publication {result['publication_id']}\n"
        f"Status: published\n"
        f"Published candidates remain unaccepted.\n"
        "No canonical artifacts were changed."
    )


def format_reconcile_inspect_publication(
    result: Mapping[str, Any],
    json_mode: bool = False,
) -> str:
    """Format a reconciliation ``inspect-publication`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    return (
        f"Reconciliation publication {result['publication_id']}\n"
        f"Status: {result['status']}\n"
        f"Chapter candidate: {result['chapter_expression']}"
    )


def format_reconcile_review(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a reconciliation ``review`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    if verbose:
        return yaml.safe_dump(result, sort_keys=False)
    lines = [
        "Reconciliation publication review",
        "",
        f"Publication: {result['publication_id']}",
        f"Status: {result['status']}",
    ]
    for candidate in result["candidates"]:
        lines.append(
            f"- {candidate['owner']}: {candidate['candidate_id']} \u2014 "
            f"{candidate['status']} ({candidate['freshness']})"
        )
    lines.append("")
    lines.append("Next actions:")
    for action in result["next_actions"]:
        lines.append(f"- {action}")
    return "\n".join(lines)


def format_reconcile_decide(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a reconciliation ``decide`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    if verbose:
        return yaml.safe_dump(result, sort_keys=False)
    return (
        f"Candidate: {result['candidate_id']}\n"
        f"Decision: {result['decision']}\n"
        f"Accepted pointer changed: "
        f"{result['result']['accepted_pointer_changed']}\n"
        "Next action: review the publication summary."
    )


def format_reconcile_decisions(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a reconciliation ``decisions`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    if verbose:
        return yaml.safe_dump(result, sort_keys=False)
    return (
        f"Publication {result.get('_requested_publication_id', result.get('publication_id', ''))}\n"
        f"Status: {result['review']['status']}\n"
        f"Decisions: {len(result['decisions'])}"
    )


def format_reconcile_recompose(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a reconciliation ``recompose`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    if verbose:
        return yaml.safe_dump(result, sort_keys=False)
    return (
        f"Canonical-source Chapter recomposition\n"
        f"Chapter Expression: {result['chapter_expression']}\n"
        f"Status: {result['status']}\n"
        f"Sources: accepted only\n"
        "Canonical Chapter acceptance is not performed."
    )


def format_reconcile_accept_chapter(
    result: Mapping[str, Any],
    json_mode: bool = False,
) -> str:
    """Format a reconciliation ``accept-chapter`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    return (
        f"Accepted Chapter Expression {result['chapter_expression']} "
        "from accepted sources. Reconciliation remains separately completable."
    )


def format_reconcile_complete(
    result: Mapping[str, Any],
    json_mode: bool = False,
    publication_id: str = "",
    status: str = "",
) -> str:
    """Format a reconciliation ``complete`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    return f"Reconciliation {publication_id} completed as {status}."


def format_reconcile_inspect(
    report: Mapping[str, Any],
    json_mode: bool = False,
) -> str:
    """Format a reconciliation ``inspect`` result."""
    if json_mode:
        return json.dumps(report, indent=2)
    lines = [
        f"Chapter reconciliation inspection {report['inspection_id']}",
        f"Status: {report['status']}",
    ]
    if report["status"] == "no_changes":
        lines.append("No changes detected.")
        for transition in report.get("recognized_transitions", []):
            lines.append(
                f"Transition {transition['transition_id']}: "
                f"{transition['classification']} \u2014 Owner: {transition['owner']}"
            )
    elif any(f["classification"] == "markerless" for f in report["findings"]):
        lines.extend([
            "Chapter manuscript cannot be reconciled automatically.",
            "Reason: No Auteur Scene or transition markers were found.",
        ])
        consequences = report["findings"][0].get("detail", {}).get("consequences", [])
        for consequence in consequences:
            ids = consequence.get("scene_ids", consequence.get("transition_ids", []))
            lines.append(f"  - {consequence['code']}: {', '.join(ids)}")
    else:
        for finding in report["findings"]:
            lines.append(
                f"{finding['classification']}: "
                f"{finding.get('source_section') or 'chapter'} \u2014 "
                f"{finding['evidence']}"
            )
            lines.append(f"  Owner: {finding['owner']}")
    lines.append(f"Proposals: {len(report.get('proposal_ids', []))}")
    return "\n".join(lines)


def format_reconcile_propose(
    result: Mapping[str, Any],
    json_mode: bool = False,
) -> str:
    """Format a reconciliation ``propose`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    lines = [
        f"Reconciliation proposals for {result.get('inspection_id', '')}: "
        f"{len(result['proposal_ids'])} created.",
    ]
    for proposal in result["proposals"]:
        lines.append(
            f"- {proposal['proposal_type']} \u2192 "
            f"{proposal.get('target_artifact_id') or 'Chapter transition'}"
        )
        lines.append(
            f"  Source revision: {proposal['target_revision']}; "
            f"Status: {proposal['status']}; Next action: review before applying"
        )
    return "\n".join(lines)


def format_reconcile_show(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
    identifier: str = "",
) -> str:
    """Format a reconciliation ``show`` or ``proposal_status`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    if verbose:
        return yaml.safe_dump(result, sort_keys=False)
    if identifier.startswith("proposal_"):
        proposal = result.get("proposal", result)
        return (
            f"Proposal {proposal['proposal_id']}: {proposal['proposal_type']}\n"
            f"Target: {proposal.get('target_artifact_id') or 'Chapter transition'}\n"
            f"Source revision: {proposal.get('target_revision')}; "
            f"Status: {result.get('status', proposal.get('status'))}\n"
            "Next action: review the proposal before applying it."
        )
    return (
        f"Chapter reconciliation inspection "
        f"{result.get('inspection_id', result.get('run_id', identifier))}\n"
        f"Status: {result.get('status', 'unknown')}\n"
        f"Findings: {len(result.get('findings', []))}; "
        f"Proposals: {len(result.get('proposal_ids', []))}"
    )


# ---------------------------------------------------------------------------
# Book subcommand formatters
# ---------------------------------------------------------------------------


def format_book_decision(
    result: Mapping[str, Any],
    success: bool,
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a Book candidate decision result (approve / reject / defer)."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    if not success:
        lines = ["Book candidate decision rejected: stale sources"]
        for reason in result.get("reasons", []):
            lines.append(f"  - {reason['code']}")
        lines.extend([
            "No decision was recorded. Publish a fresh Book candidate and decide again.",
        ])
        return "\n".join(lines)
    decision = result
    lines = [
        "Book candidate decision",
        f"Candidate: {decision['candidate_id']}",
        f"Decision: {decision['decision']['status']} | "
        f"\"{decision['decision']['reason']}\" "
        f"(sequence {decision['decision_sequence']})",
    ]
    if decision.get("supersedes"):
        lines.append(f"Supersedes: {decision['supersedes']}")
    if decision.get("accepted_source_id"):
        lines.append(f"Accepted Book-owned source: {decision['accepted_source_id']}")
    if decision.get("pointer_moved"):
        ptr = decision["pointer"]
        lines.append(
            f"Accepted-source pointer: {ptr['owned_kind']}/{ptr['element_id']} "
            f"-> revision {ptr['current_revision']}"
        )
    else:
        lines.append("Accepted-source pointer: unchanged")
    lines.extend([
        f"Decided at: {decision['decided_at']}",
        "Preview updated: yes",
        "Book pointer changed: no",
    ])
    return "\n".join(lines)


def format_book_candidate_history(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a ``book-candidate-history`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    lines = [
        f"Book candidate {result['candidate_id']}",
        f"Active status: {result['active_status']}",
        f"Decisions ({len(result['decisions'])}):",
    ]
    for d in result["decisions"]:
        lines.append(
            f"  {d['decision_sequence']}. {d['decision']['status']} | "
            f"\"{d['decision']['reason']}\" @ {d['decided_at']}"
        )
    return "\n".join(lines)


def format_book_show_candidate_decision(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a ``show-book-candidate-decision`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    lines = [
        "Book candidate decision",
        f"Candidate: {result['candidate_id']}",
        f"Decision: {result['decision']['status']} | "
        f"\"{result['decision']['reason']}\" "
        f"(sequence {result.get('decision_sequence', 1)})",
    ]
    if result.get("supersedes"):
        lines.append(f"Supersedes: {result['supersedes']}")
    if result.get("accepted_source_id"):
        lines.append(f"Accepted Book-owned source: {result['accepted_source_id']}")
    lines.extend([
        f"Decided at: {result['decided_at']}",
        f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']}",
    ])
    return "\n".join(lines)


def format_book_plan(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a ``plan-book-reconciliation`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    lines = [
        f"Book reconciliation application plan {result['plan_id']}",
        f"Source Book: {result['source_book_expression']} "
        f"(revision {result['source_book_revision']})",
        f"Selected proposals: {len(result['selected_proposals'])}",
        f"Readiness: {result['readiness']['status']}",
    ]
    if result.get("conflicts"):
        codes = sorted({c["conflict_code"] for c in result["conflicts"]})
        lines.append(f"Conflicts: {', '.join(codes)}")
    lines.append("No candidates, preview, or pointers were created.")
    if result["readiness"]["status"] == "ready":
        lines.append("Recommended next action: publish this plan into unaccepted candidates")
    else:
        lines.append("Recommended next action: resolve readiness issues, then re-plan")
    return "\n".join(lines)


def format_book_show_plan(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a ``show-book-plan`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    return (
        f"Book reconciliation application plan {result['plan_id']}\n"
        f"Source Book: {result['source_book_expression']} "
        f"(revision {result['source_book_revision']})\n"
        f"Selected proposals: {len(result['selected_proposals'])}\n"
        f"Planned candidates: {len(result['planned_outputs'])}\n"
        f"Readiness: {result['readiness']['status']}"
    )


def format_book_publish_error(
    exc: Any,
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a Book ``publish-book-reconciliation`` rejection error."""
    exc_result = exc.result if hasattr(exc, "result") else {}
    if json_mode or verbose:
        return json.dumps(exc_result, indent=2)
    lines = [f"Book publication rejected: {exc_result.get('status', 'unknown')}"]
    for reason in exc_result.get("reasons", []):
        lines.append(
            f"  - {reason.get('code')}: {reason.get('recommended_action')}"
        )
    lines.append(
        f"Visible outputs created: {exc_result.get('visible_outputs_created')}"
    )
    return "\n".join(lines)


def format_book_publish(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a Book ``publish-book-reconciliation`` success result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    return (
        f"Book reconciliation publication {result['publication_id']}\n"
        f"Source Book: {result['source_book_expression']} "
        f"(revision {result['source_book_revision']})\n"
        f"Published candidates: {len(result['published_candidates'])}\n"
        f"Preview status: {result['preview']['role']} "
        f"({result['preview']['lifecycle']}, noncanonical)\n"
        "Acceptance status: none\n"
        "Accepted Book pointer changed: no\n"
        "Recommended next action: review the published candidates "
        "(acceptance is a separate, future step)"
    )


def format_book_inspect_publication(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format an ``inspect-book-publication`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    return (
        f"Book reconciliation publication {result['publication_id']}\n"
        f"Source Book: {result['source_book_expression']} "
        f"(revision {result['source_book_revision']})\n"
        f"Published candidates: {len(result['published_candidates'])}\n"
        f"Preview status: {result['preview']['role']} "
        f"({result['preview']['lifecycle']}, noncanonical)\n"
        f"Acceptance status: {result['acceptance_status']}\n"
        f"Accepted Book pointer changed: "
        f"{'yes' if result['accepted_book_pointer_changed'] else 'no'}"
    )


def format_book_recompose_error(
    result: Any,
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a Book recomposition error result."""
    if json_mode or verbose:
        return json.dumps(result.result if hasattr(result, "result") else result, indent=2)
    lines = [
        f"Book recomposition blocked: {result.status}",
        f"Primary reason: {result.reason}",
    ]
    for reason in (result.result if hasattr(result, "result") else {}).get("reasons", []):
        lines.append(f"  - {reason.get('code')}: {reason.get('recommended_action')}")
    lines.extend([
        "No recomposition artifact was created.",
        f"Recommended action: {result.recommended_action}",
    ])
    return "\n".join(lines)


def format_book_recompose(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a ``recompose-book-from-accepted`` success result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    owned = result["source_pointers"]["book_owned"]
    return (
        f"Book recomposition (derived, noncanonical)\n"
        f"Publication: {result['publication_id']}\n"
        f"Source Book: {result['source_book_expression']} "
        f"(revision {result['source_book_revision']})\n"
        f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']} | "
        f"Role: {result['role']} | Canonical: {result['canonical']}\n"
        f"Chapters: {len(result['chapters'])} in order {result['order']}\n"
        f"Separator pointer: {'yes' if owned['separator_pointer_id'] else 'default'}\n"
        f"Order pointer: {'yes' if owned['order_pointer_id'] else 'default'}\n"
        f"Title pointer: {'yes' if owned['title_rendering_pointer_id'] else 'default'}\n"
        f"Inserted material pointers: {len(owned['inserted_material_pointer_ids'])}\n"
        f"Content hash: {result['content_hash']}\n"
        "Accepted Book pointer changed: no"
    )


def format_book_show_recomposition(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a ``show-book-recomposition`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    owned = result["source_pointers"]["book_owned"]
    return (
        f"Book recomposition (derived, noncanonical)\n"
        f"Publication: {result['publication_id']}\n"
        f"Inspection: {result['inspection_id']}\n"
        f"Role: {result['role']} | Canonical: {result['canonical']}\n"
        f"Chapters: {len(result['chapters'])} in order {result['order']}\n"
        f"Book-owned pointers used: "
        f"separator={bool(owned['separator_pointer_id'])}, "
        f"order={bool(owned['order_pointer_id'])}, "
        f"title={bool(owned['title_rendering_pointer_id'])}, "
        f"material={len(owned['inserted_material_pointer_ids'])}\n"
        f"Content hash: {result['content_hash']}\n"
        f"Recomposed at: {result['recomposed_at']}"
    )


def format_book_compare_recomposition_error(
    result: Any,
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a Book recomposition comparison error."""
    if json_mode or verbose:
        return json.dumps(result.result if hasattr(result, "result") else result, indent=2)
    lines = [
        f"Book comparison blocked: {result.status}",
        f"Primary reason: {result.reason}",
    ]
    for reason in (result.result if hasattr(result, "result") else {}).get("reasons", []):
        lines.append(f"  - {reason.get('code')}: {reason.get('recommended_action')}")
    lines.extend([
        "No comparison report was created.",
        f"Recommended action: {result.recommended_action}",
    ])
    return "\n".join(lines)


def format_book_compare_recomposition(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a ``compare-book-recomposition`` success result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    counts = result["summary"]["residual_counts"]
    owned_types = sorted({
        s["owned_kind"] for s in result["book_owned_sources"] if s.get("owned_kind")
    })
    if result["summary"]["ready_for_book_acceptance"]:
        action = "accept Book"
    elif counts["chapter_owned_residual"] or counts["structural_residual"] or counts["unresolved_residual"]:
        action = "re-examine residuals"
    else:
        action = "re-approve sources"
    return (
        f"Book recomposition comparison (derived, evaluated, noncanonical)\n"
        f"Comparison: {result['comparison_id']}\n"
        f"Exact match: {counts['exact_match']}\n"
        f"Ready for Book acceptance: "
        f"{'yes' if result['summary']['ready_for_book_acceptance'] else 'no'}\n"
        "Residuals:\n"
        f"  Book-owned: {counts['book_owned_residual']} "
        f"({', '.join(owned_types) or 'none'})\n"
        f"  Chapter-owned: {counts['chapter_owned_residual']}\n"
        f"  Structural: {counts['structural_residual']}\n"
        f"  Marker: {counts['marker_residual']}\n"
        f"  Unresolved: {counts['unresolved_residual']}\n"
        "Accepted pointers changed: no\n"
        f"Recommended next action: {action}"
    )


def format_book_inspect_comparison(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format an ``inspect-book-comparison`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    counts = result["summary"]["residual_counts"]
    return (
        f"Book recomposition comparison\n"
        f"Comparison: {result['comparison_id']}\n"
        f"Recomposition: {result['source_recomposition_id']}\n"
        f"External manuscript: {result['external_manuscript']['path']}\n"
        f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']} | "
        f"Role: {result['role']} | Canonical: {result['canonical']}\n"
        f"Exact match: {result['summary']['exact_match']}\n"
        f"Ready for Book acceptance: "
        f"{'yes' if result['summary']['ready_for_book_acceptance'] else 'no'}\n"
        f"Findings: {len(result['findings'])} "
        f"(exact={counts['exact_match']}, "
        f"book-owned={counts['book_owned_residual']}, "
        f"chapter-owned={counts['chapter_owned_residual']}, "
        f"structural={counts['structural_residual']}, "
        f"marker={counts['marker_residual']}, "
        f"unresolved={counts['unresolved_residual']})"
    )


def format_book_accept_recomposed_error(
    result: Any,
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format an ``accept-recomposed-book`` error result."""
    if json_mode or verbose:
        d = result.result if hasattr(result, "result") else result
        return json.dumps(d, indent=2, default=str)
    lines = [
        f"Book acceptance blocked: {result.status}",
        f"Primary reason: {result.reason}",
        "No accepted Book revision, acceptance record, or pointer move was created.",
        f"Recommended action: {result.recommended_action}",
    ]
    return "\n".join(lines)


def format_book_accept_recomposed_duplicate(result: Mapping[str, Any], json_mode: bool = False) -> str:
    """Format a duplicate ``accept-recomposed-book`` result."""
    if json_mode:
        return _to_json(result)
    return (
        f"Book accepted: yes (duplicate)\n"
        f"Prior acceptance: {result['prior_acceptance_id']}\n"
        f"Accepted revision: {result['accepted_book_revision']}\n"
        "No new Book revision or acceptance record created.\n"
        "Recommended next action: inspect the prior acceptance"
    )


def format_book_accept_recomposed(
    result: Mapping[str, Any],
    counts_source: Mapping[str, int] | None = None,
    json_mode: bool = False,
) -> str:
    """Format an ``accept-recomposed-book`` success result."""
    if json_mode:
        return _to_json(result)
    revision = result["accepted_book_revision"]
    record = result["acceptance_record"]
    total_residual = (
        sum(v for k, v in counts_source.items() if k != "exact_match")
        if counts_source else 0
    )
    return (
        f"Book accepted: yes\n"
        f"Previous revision: {record['previous_book_revision']}\n"
        f"Accepted revision: {revision['revision']}\n"
        "Comparison exact match: yes\n"
        f"Residual findings: {total_residual}\n"
        "Accepted Book pointer moved: yes\n"
        "Chapter pointers changed: no\n"
        "Book-owned pointers changed: no\n"
        "Reconciliation completed: no\n"
        "Recommended next action: verify reconciliation completion eligibility"
    )


def format_book_inspect_acceptance(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format an ``inspect-book-acceptance`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2, default=str)
    transition = result["pointer_transition"]
    return (
        f"Book reconciliation acceptance\n"
        f"Acceptance: {result['acceptance_id']}\n"
        f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']}\n"
        f"Accepted Book: {result['accepted_book_expression_id']} "
        f"(revision {result['accepted_book_revision']})\n"
        f"Previous Book: {result['previous_book_expression_id']} "
        f"(revision {result['previous_book_revision']})\n"
        f"Source comparison: {result['source_comparison_id']}\n"
        f"Source recomposition: {result['source_recomposition_id']}\n"
        f"Chapter sources: {len(result['accepted_chapter_sources'])} | "
        f"Book-owned sources: {len(result['accepted_book_owned_sources'])}\n"
        f"Pointer moved: {transition['previous_pointer_id']} -> "
        f"{transition['current_pointer_id']}"
    )


def format_book_complete_error(
    result: Any,
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format a ``complete-book-reconciliation`` error result."""
    if json_mode or verbose:
        d = result.result if hasattr(result, "result") else result
        return json.dumps(d, indent=2, default=str)
    lines = [
        f"Reconciliation completion blocked: {result.status}",
        f"Primary reason: {result.reason}",
        "No completion record was created.",
        f"Recommended action: {result.recommended_action}",
    ]
    return "\n".join(lines)


def format_book_complete_duplicate(result: Mapping[str, Any], json_mode: bool = False) -> str:
    """Format a duplicate ``complete-book-reconciliation`` result."""
    if json_mode:
        return _to_json(result)
    return (
        f"Reconciliation completed: yes (duplicate)\n"
        f"Prior completion: {result['prior_completion_id']}\n"
        "No new completion record created.\n"
        "Recommended next action: inspect the prior completion"
    )


def format_book_complete(result: Mapping[str, Any], json_mode: bool = False) -> str:
    """Format a ``complete-book-reconciliation`` success result."""
    if json_mode:
        return _to_json(result)
    record = result["completion_record"]
    ch = record.get("chapter_reconciliations", [])
    ch_done = sum(1 for c in ch if "completed" in (c.get("status") or ""))
    bo = record.get("book_owned_resolutions", [])
    deferred = sum(1 for r in bo if "deferred" in (r.get("resolution") or ""))
    return (
        f"Reconciliation completed: yes\n"
        f"Accepted Book revision: {record['accepted_book']['revision']}\n"
        "Comparison exact match: yes\n"
        "Residual findings: 0\n"
        f"Chapter reconciliations complete: {ch_done}/{len(ch)}\n"
        f"Book-owned proposals resolved: {len(bo)}/{len(bo)}\n"
        f"Deferred items remaining: {deferred}\n"
        "Accepted Book pointer changed: no\n"
        "Narrative artifacts mutated: no"
    )


def format_book_inspect_completion(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format an ``inspect-book-reconciliation-completion`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2, default=str)
    book = result["accepted_book"]
    ch = result.get("chapter_reconciliations", [])
    bo = result.get("book_owned_resolutions", [])
    return (
        f"Book reconciliation completion\n"
        f"Completion: {result['completion_id']}\n"
        f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']}\n"
        f"Accepted Book: {book['expression_id']} (revision {book['revision']})\n"
        f"Source acceptance: {result['source_acceptance_id']}\n"
        f"Comparison exact match: {result['verification']['exact_match']}\n"
        f"Chapters: {len(ch)} | Book-owned resolutions: {len(bo)}"
    )


def format_book_inspect_manuscript(
    result: Mapping[str, Any],
    json_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Format an ``inspect-book-manuscript`` result."""
    if json_mode or verbose:
        return json.dumps(result, indent=2)
    return (
        f"Book edit inspection\n"
        f"Book: {result['book_expression_id']}\n"
        f"Source revision: {result['book_revision']}\n"
        f"Status: {result['status']}\n"
        f"Chapter-local changes: {len(result['chapter_findings'])}\n"
        f"Book-owned changes: {len(result['book_findings'])}\n"
        f"Unresolved: {len(result['unresolved_findings'])}\n"
        "No canonical artifacts were changed."
    )


def format_book_route_inspection(
    result: Mapping[str, Any],
    json_mode: bool = False,
) -> str:
    """Format a ``route-book-inspection`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    return (
        f"Book inspection routing\n"
        f"Status: {result['status']}\n"
        f"Chapter routes: {len(result.get('chapter_routes', []))}\n"
        f"Book proposals: {len(result.get('book_proposals', []))}\n"
        f"Unresolved: {len(result.get('unresolved', []))}"
    )


def format_book_show_inspection(
    result: Mapping[str, Any],
    json_mode: bool = False,
) -> str:
    """Format a ``show-book-inspection`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    return (
        f"Book edit inspection {result['inspection_id']}\n"
        f"Status: {result['status']}\n"
        f"Chapter-local changes: {len(result['chapter_findings'])}\n"
        f"Book-owned changes: {len(result['book_findings'])}\n"
        f"Unresolved: {len(result['unresolved_findings'])}"
    )


def format_book_compose(book_expression_id: str) -> str:
    """Format a ``compose-book`` result."""
    return book_expression_id


def format_book_inspect(
    result: Mapping[str, Any],
    json_mode: bool = False,
) -> str:
    """Format an ``inspect-book`` result."""
    if json_mode:
        return json.dumps(result, indent=2)
    meta = result["metadata"]
    lines = [
        f"Book {meta['book_id']} | revision {meta['revision']} | "
        f"{meta['lifecycle']} | {result['freshness']}",
    ]
    for chapter in meta["chapters"]:
        lines.append(
            f"  {chapter['position']}: {chapter['chapter_id']} -> "
            f"{chapter['chapter_expression_id']} v{chapter['accepted_revision']:03d}"
        )
    if result.get("stale_sources"):
        lines.append(f"Recommended action: {result['recommended_action']}")
    return "\n".join(lines)


def format_book_compare(data: Mapping[str, Any]) -> str:
    """Format a ``compare-books`` result."""
    return json.dumps(data, indent=2)


def format_book_accept(data: Mapping[str, Any]) -> str:
    """Format an ``accept-book`` result."""
    return json.dumps(data, indent=2)


def format_book_export(output_path: str) -> str:
    """Format an ``export-book`` result."""
    return output_path


# ---------------------------------------------------------------------------
# Error formatting
# ---------------------------------------------------------------------------


def format_not_found(resource_type: str, identifier: str, next_action: str) -> str:
    """Format a resource-not-found error message."""
    return (
        f"No {resource_type} found: {identifier}\n"
        f"Recommended action: {next_action}"
    )
