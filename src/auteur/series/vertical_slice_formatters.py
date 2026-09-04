from __future__ import annotations

from auteur.series.repeated_map_focus import AcceptedHistorySnapshot, selection_token_display
from auteur.series.productization import (
    AuthorFocusReport,
    RevisionImpactReport,
    SeriesContinuityReviewReport,
)
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


def format_accepted_facts(
    snapshot: AcceptedHistorySnapshot,
    *,
    detail: bool = False,
) -> str:
    """Render accepted historical facts for read-only discovery.

    Default output shows a deterministic selection token (``B{book}-{position}~
    {fingerprint}``), a plain-language fact summary, and the accepted source
    Book. Internal artifact id, revision, and fact id are shown only when
    ``detail=True`` (opt-in), mirroring the progressive disclosure of Map/Focus.
    The selection token is user-facing and is never hidden behind ``--detail``.

    Only accepted facts are rendered; proposed or unaccepted candidates never
    appear.
    """
    lines: list[str] = [f"Accepted facts through Book {snapshot.planning_book_number - 1}"]
    counters: dict[int, int] = {}
    for bundle, realization_ref in zip(
        snapshot.realizations, snapshot.realization_refs, strict=True
    ):
        position = counters.get(bundle.book_number, 0)
        for transition in bundle.transitions:
            position += 1
            counters[bundle.book_number] = position
            source_ref = AcceptedFactRef(
                artifact_id=bundle.artifact_id,
                revision=realization_ref.revision,
                fact_id=transition.transition_id,
            )
            token = selection_token_display(
                bundle.book_number, position, source_ref
            )
            lines.append(
                f"[{token}] {transition.subject}.{transition.attribute} "
                f"is {transition.after}."
            )
            lines.append(f"  Accepted in Book {bundle.book_number}")
            if detail:
                lines.append(
                    "  Accepted source: artifact "
                    f"{source_ref.artifact_id}, revision {source_ref.revision}, "
                    f"fact {source_ref.fact_id}"
                )
    return "\n".join(lines)


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


def format_author_focus(report: AuthorFocusReport, *, detail: bool = False) -> str:
    """Render the productized Focus with progressive provenance disclosure."""
    lines = [f"Series Focus: Book {report.book_number}", "", "DECISION", report.decision]
    lines.extend(["", "ACTIVE CONSTRAINTS"])
    if report.active_constraints:
        for entry in report.active_constraints:
            _append_repeated_entry(lines, entry, indent=0, detail=detail)
    else:
        lines.append("- None surfaced.")
    lines.extend(["", "RELEVANT HISTORY"])
    if report.relevant_history:
        for entry in report.relevant_history:
            _append_repeated_entry(lines, entry, indent=0, detail=detail)
    else:
        lines.append("- None surfaced.")
    lines.extend(["", "PERSISTENT PRESSURES"])
    if report.persistent_pressures:
        for group in report.persistent_pressures:
            lines.extend([f"- {group.summary}", f"  Why it matters now: {group.why_matters_now}"])
    else:
        lines.append("- None surfaced.")
    lines.extend(["", "LONG-RANGE CONNECTIONS"])
    if report.long_range_connections:
        for connection in report.long_range_connections:
            lines.append(f"- {connection.summary}")
            if detail:
                lines.append(f"  Relation: {connection.relation_id}")
    else:
        lines.append("- None surfaced.")
    lines.extend(["", "RISKS / CONFLICTS"])
    lines.extend(f"- {risk}" for risk in report.risks_or_conflicts or ["None detected."])
    lines.extend(["", "PROVENANCE"])
    lines.extend(
        f"- {_format_source_ref(source_ref)}" for source_ref in report.provenance
    )
    if detail:
        lines.extend(
            [
                "",
                f"Map snapshot: {report.map_snapshot_id}",
                f"Map freshness: {report.map_freshness}",
                f"Semantic impact: {report.semantic_impact}",
            ]
        )
    return "\n".join(lines)


def format_revision_impact(report: RevisionImpactReport) -> str:
    lines = ["Revision impact", "", report.reconciliation_boundary, "", "REVIEW ORDER"]
    lines.extend(f"- {artifact_id}" for artifact_id in report.review_order or ["None required."])
    lines.extend(["", "AFFECTED ACCEPTED ARTIFACTS"])
    lines.extend(
        f"- Book {item.book_number}: {item.artifact_id} ({item.freshness}, {item.semantic_impact})"
        for item in report.affected_artifacts
    )
    if not report.affected_artifacts:
        lines.append("- None detected.")
    return "\n".join(lines)


def format_series_continuity_review(
    report: SeriesContinuityReviewReport, *, detail: bool = False
) -> str:
    lines = [
        f"Series Continuity Review: Book {report.book_number}",
        "",
        "CURRENT PLANNING DECISION",
        report.planning_intent,
        "",
        "SERIES DIRECTION",
        f"Promise: {report.promise}",
        f"Pressure: {report.pressure}",
        f"Series open question: {report.open_question}",
        "",
        "ACTIVE COMMITMENTS",
    ]
    if report.active_commitments:
        for item in report.active_commitments:
            lines.append(f"- {item.statement}")
            if detail:
                lines.append(f"  Commitment ID: {item.commitment_id} ({item.scope})")
    else:
        lines.append("- None recorded.")
    lines.extend(["", "RESOLVED COMMITMENTS (HISTORY)"])
    if report.resolved_commitments:
        for item in report.resolved_commitments:
            lines.append(f"- {item.statement}")
            if detail:
                lines.append(f"  Commitment ID: {item.commitment_id} ({item.scope})")
    else:
        lines.append("- None recorded.")
    lines.extend(["", "WHAT THE ACCEPTED STORY CURRENTLY SAYS"])
    if report.current_context:
        for entry in report.current_context:
            lines.append(f"- {entry.summary}")
            if detail:
                lines.append(f"  Entry ID: {entry.entry_id}; disposition: {entry.disposition}")
    else:
        lines.append("- No current context surfaced.")
    lines.extend(["", "RELEVANT ACCEPTED HISTORY"])
    if report.relevant_history:
        for entry in report.relevant_history:
            lines.append(f"- {entry.summary}")
            if detail:
                lines.append(f"  Entry ID: {entry.entry_id}; disposition: {entry.disposition}")
    else:
        lines.append("- None surfaced.")
    lines.extend(["", "REVISION / CONTINUITY WARNINGS"])
    lines.extend(f"- {warning}" for warning in report.warnings or ["None detected."])
    lines.extend(["", "LONG-RANGE SUPPORTING CONTEXT"])
    if report.supporting_connections:
        for connection in report.supporting_connections:
            lines.append(f"- {connection.summary}")
            if detail:
                lines.append(f"  Relation: {connection.relation_id}")
                lines.append("  Source evidence:")
                lines.extend(
                    f"    - {_format_continuity_source_ref(ref)}"
                    for ref in connection.source_refs
                )
                lines.append("  Target evidence:")
                lines.extend(
                    f"    - {_format_continuity_source_ref(ref)}"
                    for ref in connection.target_refs
                )
                lines.append(f"  Origin: {connection.origin}; disposition: {connection.disposition}")
                lines.append(f"  Rule version: {connection.rule_version or 'none'}")
                lines.append("  Relation evidence:")
                lines.extend(
                    f"    - {_format_continuity_source_ref(ref)}"
                    for ref in connection.evidence_refs
                )
                lines.append("  Source revisions:")
                lines.extend(
                    f"    - {_format_source_ref(ref)}"
                    for ref in connection.source_revision_refs
                )
    else:
        lines.append("- None surfaced.")
    lines.extend(
        [
            "",
            "REVISION IMPACT",
            report.revision_impact.reconciliation_boundary,
            "Affected accepted artifacts are not automatically rewrite instructions.",
            "AFFECTED ACCEPTED ARTIFACTS",
            *(
                (
                    f"- Book {item.book_number}: {item.artifact_id} "
                    f"({item.freshness}, {item.semantic_impact})"
                    if detail
                    else f"- Book {item.book_number} ({item.freshness}, {item.semantic_impact})"
                )
                for item in report.revision_impact.affected_artifacts
            ),
            *( ["- None detected."] if not report.revision_impact.affected_artifacts else [] ),
            "SERIES DIRECTION IMPACT",
            *(
                (
                    f"- Book {item['book_number']}: {item['artifact_id']} "
                    f"({item['freshness']}, {item['lifecycle']})"
                    if detail
                    else f"- Book {item['book_number']} ({item['freshness']}, {item['lifecycle']})"
                )
                for item in report.revision_impact.series_direction_impact
            ),
            *(
                ["- None detected."]
                if not report.revision_impact.series_direction_impact
                else []
            ),
            "",
            "WHAT REMAINS UNCHANGED",
            "Accepted downstream material remains accepted. This review does not rewrite it.",
            "No narrative authority has changed.",
        ]
    )
    if detail:
        lines.extend(["", "DETAIL", f"Freshness: {report.freshness}", f"Semantic impact: {report.semantic_impact}"])
        lines.append("Provenance:")
        lines.extend(f"- {_format_source_ref(ref)}" for ref in report.provenance)
        lines.append("Current state evidence:")
        lines.extend(
            f"- {key}: {value.current_value} ({_format_continuity_source_ref(value.current_fact_ref)})"
            for key, value in report.current_state_evidence.items()
        )
        lines.append(f"Map snapshot: {report.map_snapshot_id}")
    return "\n".join(lines)
