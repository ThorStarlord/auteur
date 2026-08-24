from __future__ import annotations

from dataclasses import dataclass

from auteur.series.vertical_slice_models import (
    AcceptedBookDirection,
    AcceptedRealizationBundle,
    AcceptedSeriesDirection,
    ArtifactRef,
    CanonicalState,
)


@dataclass(frozen=True)
class AcceptedHistorySnapshot:
    planning_book_number: int
    series: AcceptedSeriesDirection
    series_ref: ArtifactRef
    books: tuple[AcceptedBookDirection, ...]
    book_refs: tuple[ArtifactRef, ...]
    realizations: tuple[AcceptedRealizationBundle, ...]
    realization_refs: tuple[ArtifactRef, ...]
    canonical_state: CanonicalState
