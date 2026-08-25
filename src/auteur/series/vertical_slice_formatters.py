from __future__ import annotations

from auteur.series.vertical_slice_models import (
    AcceptedContinuitySourceRef,
    AcceptedFactRef,
    ArtifactRef,
    BookPlanningContext,
    ContinuityEntry,
    NextDecisionProposal,
    RepeatedBookPlanningContext,
)


def _format_source_ref(source_ref: ArtifactRef) -> str:
    return f"{source_ref.artifact_id} (revision {source_ref.revision})"


def _format_continuity_source_ref(
    source_ref: AcceptedContinuitySourceRef,
) -> str:
    if isinstance(source_ref, AcceptedFactRef):
        return (
            f"{source_ref.artifact_id} (revision {source_ref.revision}, "
            f"fact {source_ref.fact_id})"
        )
    return _format_source_ref(source_ref)


def _append_repeated_entry(
    lines: list[str],
    entry: ContinuityEntry,
    *,
    indent: int,
    detail: bool,
) -> None:
    prefix = " " * indent
    lines.extend(
        [
            f"{prefix}- {entry.summary}",
            f"{prefix}  Why it matters now: {entry.why_matters_now}",
        ]
    )
    if not detail:
        return
    lines.extend(
        [
            f"{prefix}  Entry ID: {entry.entry_id}",
            f"{prefix}  Disposition: {entry.disposition}",
            f"{prefix}  Source references:",
        ]
    )
    lines.extend(
        f"{prefix}    - {_format_continuity_source_ref(source_ref)}"
        for source_ref in entry.source_refs
    )


def format_repeated_series_map(
    context: RepeatedBookPlanningContext,
    *,
    detail: bool = False,
) -> str:
    """Render the compact repeated current-Book Map."""
    lines = [f"Series Map: Book {context.book_number}"]
    grouped_entry_ids: set[str] = set()

    if context.groups:
        lines.extend(["", "Active continuity"])
        for group in context.groups:
            lines.extend(
                [
                    f"- {group.summary}",
                    f"  Why it matters now: {group.why_matters_now}",
                ]
            )
            if detail:
                lines.extend(
                    [
                        f"  Group ID: {group.group_id}",
                        "  Source references:",
                    ]
                )
                lines.extend(
                    "    - " + _format_continuity_source_ref(source_ref)
                    for source_ref in group.source_refs
                )
            lines.append("  Current constraints")
            for entry_id in group.entry_ids:
                entry = context.item(entry_id)
                _append_repeated_entry(
                    lines, entry, indent=4, detail=detail
                )
                grouped_entry_ids.add(entry.entry_id)

    grouped_commitment_ids = set(context.group_ids)
    ungrouped_entries = [
        entry
        for entry in context.entries
        if entry.entry_id not in grouped_entry_ids
        and entry.entry_id not in grouped_commitment_ids
    ]
    if ungrouped_entries:
        lines.extend(["", "Current constraints"])
        for entry in ungrouped_entries:
            _append_repeated_entry(lines, entry, indent=0, detail=detail)

    if detail and context.history_entries:
        lines.extend(["", "Historical continuity"])
        for entry in context.history_entries:
            _append_repeated_entry(lines, entry, indent=0, detail=True)

    return "\n".join(lines)


def format_repeated_series_focus(
    proposal: NextDecisionProposal,
    *,
    detail: bool = False,
) -> str:
    """Render the repeated current-Book Focus proposal."""
    options_by_id = {option.option_id: option for option in proposal.options}
    recommended = options_by_id[proposal.recommended_option_id]
    alternatives = [
        option
        for option in proposal.options
        if option.option_id != proposal.recommended_option_id
    ]
    book_number = proposal.book_number

    lines = [
        f"Series Focus: Book {book_number}",
        "",
        "Decision",
        proposal.question,
        "",
        "Recommendation",
        f"{recommended.label}: {recommended.summary}",
        "",
        "Why this is preferred",
        proposal.rationale,
        "",
        "Principal tradeoff",
        recommended.tradeoff,
        "",
        f"This is a planning choice, not Book {book_number} canon.",
        "Choosing an option records what you want to explore next. You can "
        f"change or develop it before accepting a Book {book_number} direction.",
        "",
        "Your choices",
        f"- Choose recommended: {recommended.label}",
        "- Choose another option:",
    ]
    for option in alternatives:
        lines.extend(
            [
                f"  - {option.label}: {option.summary}",
                f"    Tradeoff: {option.tradeoff}",
            ]
        )
    lines.append("- Defer")

    if detail:
        lines.extend(["", f"Proposal ID: {proposal.proposal_id}"])
        lines.append("Accepted input sources")
        lines.extend(
            f"- {_format_source_ref(source_ref)}"
            for source_ref in proposal.accepted_input_refs
        )
        lines.append("Option IDs")
        lines.extend(
            f"- {option.label}: {option.option_id}"
            for option in proposal.options
        )

    return "\n".join(lines)


def format_series_journey_map(
    context: BookPlanningContext,
    decision: NextDecisionProposal,
    *,
    detail: bool = False,
) -> str:
    lines = [
        f"Series Map: Book {context.book_number}",
        "",
        "Established context",
    ]
    for item in context.items:
        lines.extend(
            [
                f"- {item.summary}",
                f"  Why it matters now: {item.why_matters_now}",
            ]
        )
        if detail:
            lines.append("  Source references:")
            lines.extend(
                f"    - {_format_source_ref(source_ref)}"
                for source_ref in item.source_refs
            )

    lines.extend(
        [
            "",
            "Next available decision",
            decision.question,
            "Open Focus to see Auteur's recommendation and your choices.",
        ]
    )

    if detail:
        lines.extend(["", f"Proposal ID: {decision.proposal_id}"])

    return "\n".join(lines)


def format_series_journey_focus(
    decision: NextDecisionProposal,
    *,
    detail: bool = False,
) -> str:
    options_by_id = {option.option_id: option for option in decision.options}
    recommended = options_by_id[decision.recommended_option_id]
    alternatives = [
        option
        for option in decision.options
        if option.option_id != decision.recommended_option_id
    ]

    lines = [
        f"Series Focus: Book {decision.book_number}",
        "",
        "Decision",
        decision.question,
        "",
        "Recommendation",
        f"{recommended.label}: {recommended.summary}",
        "",
        "Why this is preferred",
        decision.rationale,
        "",
        "Principal tradeoff",
        recommended.tradeoff,
        "",
        "This is a planning choice, not Book 2 canon.",
        "Choosing an option records what you want to explore next. You can "
        "change or develop it before accepting a Book 2 direction.",
        "",
        "Your choices",
        f"- Choose recommended: {recommended.label}",
        "- Choose another option:",
    ]
    lines.extend(f"  - {option.label}" for option in alternatives)
    lines.append("- Defer")

    if detail:
        lines.extend(["", f"Proposal ID: {decision.proposal_id}"])
        lines.append("Accepted input sources")
        lines.extend(
            f"- {_format_source_ref(source_ref)}"
            for source_ref in decision.accepted_input_refs
        )
        lines.append("Option IDs")
        lines.extend(
            f"- {option.label}: {option.option_id}"
            for option in decision.options
        )

    return "\n".join(lines)
