from __future__ import annotations

from auteur.series.vertical_slice_models import (
    ArtifactRef,
    BookPlanningContext,
    NextDecisionProposal,
)


def _format_source_ref(source_ref: ArtifactRef) -> str:
    return f"{source_ref.artifact_id} (revision {source_ref.revision})"


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
