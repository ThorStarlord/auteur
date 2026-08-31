from __future__ import annotations

import hashlib
from dataclasses import dataclass

from auteur.series.vertical_slice_models import (
    AcceptedBookDirection,
    AcceptedContinuitySourceRef,
    AcceptedFactRef,
    AcceptedRealizationBundle,
    AcceptedSeriesDirection,
    ArtifactRef,
    BookPlanningIntent,
    CanonicalState,
    GlobalMapSnapshot,
    ContinuityDisposition,
    ContinuityEntry,
    ContinuityGroup,
    DecisionOption,
    NextDecisionProposal,
    RepeatedBookPlanningContext,
    StateTransition,
)


_ACTIVE_DISPOSITIONS = frozenset({"active", "reactivated"})
_DERIVATION_VERSION = "repeated-map-focus-v2-r1"


def selection_token_for(source_ref: AcceptedFactRef) -> str:
    """Derive a deterministic, non-authoritative selection-token fingerprint.

    ``selection_token`` is a presentation locator, never an identity. The
    fingerprint is computed from the exact revisioned ``AcceptedFactRef`` and
    is never persisted as narrative identity or authority. The internal
    artifact id, revision, and fact id remain visible only under ``--detail``.

    Fail-closed guarantees (see ``resolve_accepted_fact_selection_token``):
    the fingerprint is bound to the exact accepted source, so a changed
    revision or artifact id stops an old token resolving. It is not an alias
    system and uses no fuzzy matching.
    """
    digest = hashlib.sha256(
        f"{source_ref.artifact_id}\0{source_ref.revision}\0{source_ref.fact_id}".encode()
    ).hexdigest()
    return digest[:6].upper()


def selection_token_display(
    source_book_number: int, position: int, source_ref: AcceptedFactRef
) -> str:
    """Compose the user-facing selection token for one listed accepted fact.

    ``B{book}-{position:02d}~{fingerprint}`` gives a human-readable display
    position (Book and per-Book 1-based index in the deterministic accepted
    listing order) plus a fingerprint bound to the exact revisioned ref. The
    full token is the selection handle passed to ``--relevance``.
    """
    return (
        f"B{source_book_number}-{position:02d}~{selection_token_for(source_ref)}"
    )


@dataclass(frozen=True)
class CurrentStateEvidence:
    key: str
    current_value: str
    current_fact_id: str
    current_source_ref: AcceptedFactRef
    superseded_fact_ids: tuple[str, ...]


@dataclass(frozen=True)
class RepeatedDecisionSeed:
    question: str
    recommended_option_id: str
    options: tuple[DecisionOption, ...]
    rationale: str


def validate_repeated_decision_proposal(
    proposal: NextDecisionProposal,
    context: RepeatedBookPlanningContext,
) -> None:
    """Reject stale or state-incompatible repeated proposals."""
    if proposal.accepted_input_refs != context.generated_from:
        raise ValueError(
            "Repeated Next Decision proposal is stale against the current "
            "accepted state; recompute it before recording an action"
        )

    recommended_option = next(
        option
        for option in proposal.options
        if option.option_id == proposal.recommended_option_id
    )
    if (
        recommended_option.incompatible_with_state_refs
        or recommended_option.incompatibility_reason is not None
    ):
        message = (
            "Recommended option is incompatible with current accepted state"
        )
        if recommended_option.incompatibility_reason:
            message = (
                f"{message}: {recommended_option.incompatibility_reason}"
            )
        raise ValueError(message)


@dataclass(frozen=True)
class AcceptedHistorySnapshot:
    planning_book_number: int
    series: AcceptedSeriesDirection
    series_ref: ArtifactRef
    books: tuple[AcceptedBookDirection, ...]
    book_refs: tuple[ArtifactRef, ...]
    realizations: tuple[AcceptedRealizationBundle, ...]
    realization_refs: tuple[ArtifactRef, ...]
    explicitly_resolved_commitment_ids: tuple[str, ...]
    accepted_fact_refs: tuple[AcceptedFactRef, ...]
    canonical_state: CanonicalState


def _fact_entry_id(source_ref: AcceptedFactRef) -> str:
    return (
        f"{source_ref.artifact_id}@{source_ref.revision}/"
        f"{source_ref.fact_id}"
    )


def _unique_source_refs(
    refs: list[AcceptedContinuitySourceRef],
) -> list[AcceptedContinuitySourceRef]:
    unique_refs: list[AcceptedContinuitySourceRef] = []
    seen: set[tuple[str, int, str | None]] = set()
    for ref in refs:
        key = (ref.artifact_id, ref.revision, getattr(ref, "fact_id", None))
        if key in seen:
            continue
        seen.add(key)
        unique_refs.append(ref)
    return unique_refs


def _commitment_why_now(
    commitment_id: str,
    disposition: ContinuityDisposition,
    carried_book_numbers: list[int],
    planning_book_number: int,
) -> str:
    if disposition == "resolved":
        return (
            f"Accepted Series commitment {commitment_id} was explicitly "
            f"resolved before Book {planning_book_number}, so it remains "
            "history support only."
        )
    carried_books = ", ".join(
        f"Book {book_number}" for book_number in carried_book_numbers
    )
    return (
        f"Accepted Series commitment {commitment_id} is carried by accepted "
        f"{carried_books} direction history, so it remains a constraint on "
        f"Book {planning_book_number} planning."
    )


def _fact_why_now(
    transition: StateTransition,
    source_ref: AcceptedFactRef,
    source_book_number: int,
    disposition: ContinuityDisposition,
    planning_intent: BookPlanningIntent,
    current_evidence: CurrentStateEvidence | None,
    superseding_evidence: CurrentStateEvidence | None,
) -> str:
    planning_book_number = planning_intent.book_number
    if (
        disposition in _ACTIVE_DISPOSITIONS
        and source_ref in planning_intent.relevance_refs
    ):
        if current_evidence is not None:
            if disposition == "reactivated":
                relevance = "this older fact is relevant again now"
            else:
                relevance = f"this current fact constrains Book {planning_book_number}"
            return (
                f"Book {planning_book_number} planning explicitly references "
                f"accepted fact {transition.transition_id}; its current "
                f"{current_evidence.key} state is "
                f"{current_evidence.current_value}, so {relevance}."
            )
        return (
            f"Book {planning_book_number} planning explicitly references "
            f"accepted fact {transition.transition_id} from Book "
            f"{source_book_number}, so it matters now."
        )
    if disposition == "superseded" and superseding_evidence is not None:
        return (
            f"Accepted fact {transition.transition_id} is superseded for Book "
            f"{planning_book_number} by current fact "
            f"{superseding_evidence.current_fact_id}, which sets "
            f"{superseding_evidence.key} to "
            f"{superseding_evidence.current_value}."
        )
    if current_evidence is not None:
        return (
            f"Accepted fact {transition.transition_id} sets current "
            f"{current_evidence.key} to {current_evidence.current_value}, but "
            f"Book {planning_book_number} planning does not reference it, so "
            "it remains derived support only."
        )
    return (
        f"Accepted fact {transition.transition_id} remains Book "
        f"{source_book_number} history for Book {planning_book_number}, but it "
        "is not a current constraint or explicit planning reference."
    )


def _group_active_consequences(
    entries: list[ContinuityEntry],
    history: AcceptedHistorySnapshot,
) -> tuple[list[ContinuityEntry], list[ContinuityGroup]]:
    active_commitment_ids = {
        entry.entry_id
        for entry in entries
        if entry.kind == "commitment" and entry.disposition == "active"
    }
    fact_book_numbers = {
        _fact_entry_id(
            AcceptedFactRef(
                artifact_id=realization.artifact_id,
                revision=realization_ref.revision,
                fact_id=transition.transition_id,
            )
        ): realization.book_number
        for realization, realization_ref in zip(
            history.realizations, history.realization_refs, strict=True
        )
        for transition in realization.transitions
    }
    commitments_by_id = {
        commitment.commitment_id: commitment
        for commitment in history.series.direction.commitments
    }
    book_directions = {
        book.direction.book_number: book.direction for book in history.books
    }
    book_direction_refs = {
        book.direction.book_number: book_ref
        for book, book_ref in zip(
            history.books, history.book_refs, strict=True
        )
    }

    candidate_members: dict[str, list[str]] = {}
    for commitment in history.series.direction.commitments:
        commitment_id = commitment.commitment_id
        if commitment_id not in active_commitment_ids:
            continue
        members = [
            entry.entry_id
            for entry in entries
            if entry.kind == "fact"
            and entry.disposition in _ACTIVE_DISPOSITIONS
            and commitment_id
            in book_directions[
                fact_book_numbers[entry.entry_id]
            ].series_commitment_ids
        ]
        if len(members) > 1:
            candidate_members[commitment_id] = members

    candidate_ids_by_entry: dict[str, list[str]] = {}
    for commitment_id, member_ids in candidate_members.items():
        for member_id in member_ids:
            candidate_ids_by_entry.setdefault(member_id, []).append(
                commitment_id
            )
    assigned_group_ids = {
        entry_id: group_ids[0]
        for entry_id, group_ids in candidate_ids_by_entry.items()
        if len(group_ids) == 1
    }
    grouped_entries = [
        entry.model_copy(
            update={"group_id": assigned_group_ids.get(entry.entry_id)}
        )
        for entry in entries
    ]

    groups: list[ContinuityGroup] = []
    entries_by_id = {entry.entry_id: entry for entry in grouped_entries}
    for commitment_id in candidate_members:
        member_ids = [
            entry_id
            for entry_id, group_id in assigned_group_ids.items()
            if group_id == commitment_id
        ]
        if len(member_ids) < 2:
            continue
        member_entries = [entries_by_id[entry_id] for entry_id in member_ids]
        supporting_book_numbers = sorted(
            {fact_book_numbers[entry_id] for entry_id in member_ids}
        )
        carried_books = " and ".join(
            f"Book {book_number}" for book_number in supporting_book_numbers
        )
        groups.append(
            ContinuityGroup(
                group_id=commitment_id,
                summary=commitments_by_id[commitment_id].statement,
                why_matters_now=(
                    f"Accepted Series commitment {commitment_id} is carried "
                    f"by accepted {carried_books} directions, so these "
                    f"consequences stay grouped for Book "
                    f"{history.planning_book_number} planning."
                ),
                source_refs=_unique_source_refs(
                    [
                        history.series_ref,
                        *(
                            book_direction_refs[book_number]
                            for book_number in supporting_book_numbers
                        ),
                        *(
                        source_ref
                        for entry in member_entries
                        for source_ref in entry.source_refs
                        ),
                    ]
                ),
                entry_ids=member_ids,
            )
        )
    return grouped_entries, groups


def select_repeated_continuity(
    history: AcceptedHistorySnapshot,
    planning_intent: BookPlanningIntent,
    current_state: dict[str, CurrentStateEvidence],
) -> RepeatedBookPlanningContext:
    """Select local continuity for one opening Book planning projection."""
    all_entries: list[ContinuityEntry] = []
    resolved_ids = set(history.explicitly_resolved_commitment_ids)

    for commitment in history.series.direction.commitments:
        carried = [
            (book.direction.book_number, book_ref)
            for book, book_ref in zip(
                history.books, history.book_refs, strict=True
            )
            if commitment.commitment_id
            in book.direction.series_commitment_ids
        ]
        if not carried:
            continue
        resolution_refs = [
            realization_ref
            for realization, realization_ref in zip(
                history.realizations,
                history.realization_refs,
                strict=True,
            )
            if commitment.commitment_id
            in realization.resolved_commitment_ids
        ]
        disposition: ContinuityDisposition = (
            "resolved"
            if commitment.commitment_id in resolved_ids
            else "active"
        )
        all_entries.append(
            ContinuityEntry(
                entry_id=commitment.commitment_id,
                kind="commitment",
                summary=commitment.statement,
                why_matters_now=_commitment_why_now(
                    commitment.commitment_id,
                    disposition,
                    [book_number for book_number, _book_ref in carried],
                    history.planning_book_number,
                ),
                disposition=disposition,
                source_refs=[
                    history.series_ref,
                    *(book_ref for _book_number, book_ref in carried),
                    *resolution_refs,
                ],
                group_id=None,
                is_current_constraint=False,
            )
        )

    latest_history_book = history.planning_book_number - 1
    has_older_realization_history = any(
        realization.book_number < latest_history_book
        for realization in history.realizations
    )

    for realization, realization_ref in zip(
        history.realizations, history.realization_refs, strict=True
    ):
        for transition in realization.transitions:
            source_ref = AcceptedFactRef(
                artifact_id=realization.artifact_id,
                revision=realization_ref.revision,
                fact_id=transition.transition_id,
            )
            state_key = f"{transition.subject}.{transition.attribute}"
            state_evidence = current_state.get(state_key)
            is_current = (
                state_evidence is not None
                and state_evidence.current_source_ref == source_ref
            )
            is_superseded = state_evidence is not None and not is_current
            if is_superseded:
                disposition = "superseded"
            elif source_ref in planning_intent.relevance_refs:
                disposition = (
                    "active"
                    if realization.book_number == latest_history_book
                    else "reactivated"
                )
            elif (
                realization.book_number == latest_history_book
                and has_older_realization_history
            ):
                disposition = "irrelevant"
            else:
                disposition = "dormant"
            all_entries.append(
                ContinuityEntry(
                    entry_id=_fact_entry_id(source_ref),
                    kind="fact",
                    summary=(
                        f"{transition.subject}.{transition.attribute} is "
                        f"{transition.after}."
                    ),
                    why_matters_now=_fact_why_now(
                        transition,
                        source_ref,
                        realization.book_number,
                        disposition,
                        planning_intent,
                        state_evidence if is_current else None,
                        state_evidence if is_superseded else None,
                    ),
                    disposition=disposition,
                    source_refs=[source_ref],
                    group_id=None,
                    is_current_constraint=is_current,
                )
            )

    grouped_entries, groups = _group_active_consequences(all_entries, history)
    return RepeatedBookPlanningContext(
        book_number=history.planning_book_number,
        generated_from=[
            history.series_ref,
            *history.book_refs,
            *history.realization_refs,
        ],
        groups=groups,
        entries=[
            entry
            for entry in grouped_entries
            if entry.disposition in _ACTIVE_DISPOSITIONS
        ],
        history_entries=[
            entry
            for entry in grouped_entries
            if entry.disposition not in _ACTIVE_DISPOSITIONS
        ],
        trigger_refs=list(planning_intent.relevance_refs),
        derivation_version=_DERIVATION_VERSION,
    )


def select_focus_from_global_map(
    snapshot: GlobalMapSnapshot,
    planning_intent: BookPlanningIntent,
) -> RepeatedBookPlanningContext:
    """Select Focus solely from a neutral Global Map projection."""
    if snapshot.freshness != "fresh":
        raise ValueError("Global Map is stale; rebuild it before Focus")
    if snapshot.planning_book_number != planning_intent.book_number:
        raise ValueError("Global Map and planning intent book numbers differ")

    group_by_fact_ref: dict[tuple[str, int, str], tuple[str, str]] = {}
    groups: list[ContinuityGroup] = []
    for relation in snapshot.pressure_groups:
        member_keys = {
            (
                member.fact_ref.artifact_id,
                member.fact_ref.revision,
                member.fact_ref.fact_id,
            )
            for member in relation.members
        }
        for member in relation.members:
            key = (
                member.fact_ref.artifact_id,
                member.fact_ref.revision,
                member.fact_ref.fact_id,
            )
            group_by_fact_ref[key] = (relation.relation_id, member.role)
        groups.append(
            ContinuityGroup(
                group_id=relation.relation_id,
                summary=relation.relation_id,
                why_matters_now=(
                    "This accepted pressure group remains relevant through "
                    "its derived evidence."
                ),
                source_refs=relation.evidence_refs,
                entry_ids=[
                    entry.entry_id
                    for entry in snapshot.entries
                    if entry.fact_ref is not None
                    and (
                        entry.fact_ref.artifact_id,
                        entry.fact_ref.revision,
                        entry.fact_ref.fact_id,
                    ) in member_keys
                ],
                relation_id=relation.relation_id,
                member_roles={
                    member.fact_ref.fact_id: member.role
                    for member in relation.members
                },
            )
        )

    entries: list[ContinuityEntry] = []
    for mapped in snapshot.entries:
        fact_ref = mapped.fact_ref
        group_id = None
        if fact_ref is not None:
            group_id = group_by_fact_ref.get(
                (fact_ref.artifact_id, fact_ref.revision, fact_ref.fact_id),
                (None, ""),
            )[0]
        disposition = mapped.disposition
        if (
            fact_ref is not None
            and fact_ref in planning_intent.relevance_refs
            and disposition not in {"active", "superseded"}
        ):
            disposition = "reactivated"
        entries.append(
            ContinuityEntry(
                entry_id=mapped.entry_id,
                kind=mapped.kind,
                summary=mapped.summary,
                why_matters_now=(
                    f"Book {planning_intent.book_number} planning explicitly "
                    f"references accepted fact {fact_ref.fact_id}; it matters "
                    "now."
                    if fact_ref is not None
                    and fact_ref in planning_intent.relevance_refs
                    else mapped.summary
                ),
                source_refs=tuple(mapped.source_refs),
                disposition=disposition,
                group_id=group_id,
                is_current_constraint=mapped.is_current_constraint,
            )
        )

    active = [entry for entry in entries if entry.disposition in _ACTIVE_DISPOSITIONS]
    return RepeatedBookPlanningContext(
        book_number=planning_intent.book_number,
        generated_from=list(snapshot.source_revisions),
        groups=groups,
        entries=active,
        history_entries=[entry for entry in entries if entry not in active],
        trigger_refs=list(planning_intent.relevance_refs),
        derivation_version=f"{_DERIVATION_VERSION}+global-map",
    )
