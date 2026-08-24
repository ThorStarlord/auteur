from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from auteur.series.vertical_slice_models import (
    AcceptedFactRef,
    AcceptedBookDirection,
    AcceptedRealizationBundle,
    AcceptedSeriesDirection,
    ArtifactRef,
    BookPlanningIntent,
    CanonicalState,
)


ContinuityDisposition = Literal[
    "active",
    "resolved",
    "dormant",
    "reactivated",
    "superseded",
    "irrelevant",
]

_ACTIVE_DISPOSITIONS = frozenset({"active", "reactivated"})


@dataclass(frozen=True)
class CurrentStateEvidence:
    key: str
    current_value: str
    current_fact_id: str
    current_source_ref: AcceptedFactRef
    superseded_fact_ids: tuple[str, ...]


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


@dataclass(frozen=True)
class _SelectedContinuityItem:
    item_id: str
    kind: Literal["commitment", "fact"]
    disposition: ContinuityDisposition
    source_refs: tuple[ArtifactRef | AcceptedFactRef, ...]


@dataclass(frozen=True)
class RepeatedBookPlanningContext:
    book_number: int
    items: tuple[_SelectedContinuityItem, ...]
    trigger_refs: tuple[AcceptedFactRef, ...]

    @property
    def active_ids(self) -> tuple[str, ...]:
        return tuple(
            item.item_id
            for item in self.items
            if item.kind == "commitment"
            and item.disposition in _ACTIVE_DISPOSITIONS
        )

    @property
    def active_fact_ids(self) -> tuple[str, ...]:
        return tuple(
            item.item_id
            for item in self.items
            if item.kind == "fact"
            and item.disposition in _ACTIVE_DISPOSITIONS
        )

    @property
    def resolved_history_ids(self) -> tuple[str, ...]:
        return tuple(
            item.item_id
            for item in self.items
            if item.disposition == "resolved"
        )

    @property
    def dispositions(self) -> dict[str, ContinuityDisposition]:
        return {item.item_id: item.disposition for item in self.items}


def select_repeated_continuity(
    history: AcceptedHistorySnapshot,
    planning_intent: BookPlanningIntent,
    current_state: dict[str, CurrentStateEvidence],
) -> RepeatedBookPlanningContext:
    """Select local continuity for one opening Book planning projection."""
    items: list[_SelectedContinuityItem] = []
    resolved_ids = set(history.explicitly_resolved_commitment_ids)

    for commitment in history.series.direction.commitments:
        carried_refs = tuple(
            book_ref
            for book, book_ref in zip(
                history.books, history.book_refs, strict=True
            )
            if commitment.commitment_id
            in book.direction.series_commitment_ids
        )
        if not carried_refs:
            continue
        resolution_refs = tuple(
            realization_ref
            for realization, realization_ref in zip(
                history.realizations,
                history.realization_refs,
                strict=True,
            )
            if commitment.commitment_id
            in realization.resolved_commitment_ids
        )
        disposition: ContinuityDisposition = (
            "resolved"
            if commitment.commitment_id in resolved_ids
            else "active"
        )
        items.append(
            _SelectedContinuityItem(
                item_id=commitment.commitment_id,
                kind="commitment",
                disposition=disposition,
                source_refs=(
                    history.series_ref,
                    *carried_refs,
                    *resolution_refs,
                ),
            )
        )

    superseded_fact_ids = {
        fact_id
        for evidence in current_state.values()
        for fact_id in evidence.superseded_fact_ids
    }
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
            if transition.transition_id in superseded_fact_ids:
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
            items.append(
                _SelectedContinuityItem(
                    item_id=transition.transition_id,
                    kind="fact",
                    disposition=disposition,
                    source_refs=(source_ref,),
                )
            )

    return RepeatedBookPlanningContext(
        book_number=history.planning_book_number,
        items=tuple(items),
        trigger_refs=tuple(planning_intent.relevance_refs),
    )
