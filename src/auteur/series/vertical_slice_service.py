from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from auteur.provenance import ArtifactMetadata
from auteur.series.vertical_slice_models import (
    AcceptedBookDirection,
    AcceptedRealizationBundle,
    AcceptedSeriesDirection,
    ArtifactRef,
    BookDirection,
    BookDirectionProposal,
    CanonicalState,
    RealizationCandidate,
    SeriesDirection,
    SeriesDirectionProposal,
)
from auteur.series.vertical_slice_store import VerticalSliceStore


class SeriesVerticalSliceService:
    def __init__(self, project_root: Path) -> None:
        self.store = VerticalSliceStore(project_root)

    def propose_series_direction(
        self, direction: SeriesDirection
    ) -> SeriesDirectionProposal:
        proposal = SeriesDirectionProposal(
            proposal_id=f"series-direction-{uuid4().hex}",
            revision=1,
            direction=direction,
        )
        self.store.save_series_direction_proposal(proposal)
        return proposal

    def load_series_direction_proposal(
        self, proposal_id: str
    ) -> SeriesDirectionProposal:
        return self.store.load_series_direction_proposal(proposal_id)

    def accept_series_direction(
        self,
        proposal_id: str,
        *,
        accepted_by: str,
        rationale: str | None = None,
    ) -> AcceptedSeriesDirection:
        proposal = self.load_series_direction_proposal(proposal_id)
        accepted = AcceptedSeriesDirection(
            artifact_id="series-direction",
            proposal_id=proposal.proposal_id,
            direction=proposal.direction,
        )
        self.store.save_accepted_series_direction(
            accepted,
            accepted_by=accepted_by,
            rationale=rationale,
        )
        return accepted

    def load_accepted_series_direction(
        self,
    ) -> AcceptedSeriesDirection | None:
        return self.store.load_accepted_series_direction()

    def load_series_direction_metadata(self) -> ArtifactMetadata | None:
        return self.store.load_series_direction_metadata()

    def _accepted_series_source(
        self,
    ) -> tuple[AcceptedSeriesDirection, ArtifactMetadata]:
        accepted = self.load_accepted_series_direction()
        metadata = self.load_series_direction_metadata()
        if accepted is None or metadata is None:
            raise ValueError(
                "An accepted Series Direction is required for a Book Direction"
            )
        return accepted, metadata

    @staticmethod
    def _validate_series_commitments(
        book_direction: BookDirection,
        accepted_series: AcceptedSeriesDirection,
    ) -> None:
        known_ids = {
            commitment.commitment_id
            for commitment in accepted_series.direction.commitments
        }
        unknown_ids = sorted(
            set(book_direction.series_commitment_ids) - known_ids
        )
        if unknown_ids:
            raise ValueError(
                "Unknown accepted Series commitment reference(s): "
                + ", ".join(unknown_ids)
            )

    def propose_book_direction(
        self, book_direction: BookDirection
    ) -> BookDirectionProposal:
        accepted_series, series_metadata = self._accepted_series_source()
        self._validate_series_commitments(book_direction, accepted_series)
        proposal = BookDirectionProposal(
            proposal_id=f"book-direction-{uuid4().hex}",
            revision=1,
            direction=book_direction,
            source_refs=[
                ArtifactRef(
                    artifact_id=accepted_series.artifact_id,
                    revision=series_metadata.revision,
                )
            ],
        )
        self.store.save_book_direction_proposal(proposal)
        return proposal

    def load_book_direction_proposal(
        self, proposal_id: str
    ) -> BookDirectionProposal:
        return self.store.load_book_direction_proposal(proposal_id)

    def accept_book_direction(
        self,
        proposal_id: str,
        *,
        accepted_by: str,
        rationale: str | None = None,
    ) -> AcceptedBookDirection:
        proposal = self.load_book_direction_proposal(proposal_id)
        accepted_series, series_metadata = self._accepted_series_source()
        self._validate_series_commitments(proposal.direction, accepted_series)
        current_source = ArtifactRef(
            artifact_id=accepted_series.artifact_id,
            revision=series_metadata.revision,
        )
        if proposal.source_refs != [current_source]:
            raise ValueError(
                "Book Direction proposal does not reference the current accepted "
                "Series Direction revision"
            )
        accepted = AcceptedBookDirection(
            artifact_id=f"book-{proposal.direction.book_number}-direction",
            proposal_id=proposal.proposal_id,
            direction=proposal.direction,
        )
        self.store.save_accepted_book_direction(
            accepted,
            series_source=proposal.source_refs[0],
            accepted_by=accepted_by,
            rationale=rationale,
        )
        return accepted

    def load_accepted_book_direction(
        self, book_number: int
    ) -> AcceptedBookDirection | None:
        return self.store.load_accepted_book_direction(book_number)

    def load_book_direction_metadata(
        self, book_number: int
    ) -> ArtifactMetadata | None:
        return self.store.load_book_direction_metadata(book_number)

    def _accepted_book_source(
        self, book_number: int
    ) -> tuple[AcceptedBookDirection, ArtifactMetadata]:
        accepted = self.load_accepted_book_direction(book_number)
        metadata = self.load_book_direction_metadata(book_number)
        if accepted is None or metadata is None:
            raise ValueError(
                "An accepted Book Direction is required for a Realization"
            )
        return accepted, metadata

    def _current_book_source_ref(self, book_number: int) -> ArtifactRef:
        accepted, metadata = self._accepted_book_source(book_number)
        return ArtifactRef(
            artifact_id=accepted.artifact_id,
            revision=metadata.revision,
        )

    def propose_realization(
        self, candidate: RealizationCandidate
    ) -> RealizationCandidate:
        current_source = self._current_book_source_ref(candidate.book_number)
        if candidate.source_refs != [current_source]:
            raise ValueError(
                "Realization candidate does not reference the current accepted "
                "Book Direction revision"
            )
        self.store.validate_current_book_dependency(
            candidate.book_number, current_source
        )
        self.store.save_realization_candidate(candidate)
        return candidate

    def accept_realization(
        self,
        candidate_id: str,
        *,
        accepted_by: str,
        rationale: str | None = None,
    ) -> AcceptedRealizationBundle:
        candidate = self.store.load_realization_candidate(candidate_id)
        current_source = self._current_book_source_ref(candidate.book_number)
        if candidate.source_refs != [current_source]:
            raise ValueError(
                "Realization candidate does not reference the current accepted "
                "Book Direction revision"
            )
        accepted = AcceptedRealizationBundle(
            artifact_id="realization-bundles",
            bundle_id=f"bundle-{candidate.candidate_id}",
            candidate_id=candidate.candidate_id,
            book_number=candidate.book_number,
            transitions=candidate.transitions,
        )
        previous_state = self.store.snapshot_canonical_state()
        metadata = self.store.save_accepted_realization_bundle(
            accepted,
            book_source=current_source,
            accepted_by=accepted_by,
            rationale=rationale,
        )
        try:
            self.rebuild_canonical_state()
        except Exception:
            self.store.rollback_accepted_realization_bundle(
                accepted.bundle_id, metadata.revision
            )
            self.store.restore_canonical_state(previous_state)
            raise
        return accepted

    def rebuild_canonical_state(self) -> CanonicalState:
        values: dict[str, str] = {}
        applied_bundle_ids: list[str] = []
        state_version = 0
        for bundle, metadata in self.store.load_accepted_realization_bundles():
            for transition in bundle.transitions:
                values[f"{transition.subject}.{transition.attribute}"] = (
                    transition.after
                )
            applied_bundle_ids.append(bundle.bundle_id)
            state_version = metadata.revision
        state = CanonicalState(
            state_version=state_version,
            values=values,
            applied_bundle_ids=applied_bundle_ids,
        )
        self.store.save_canonical_state(state)
        return state

    def load_canonical_state(self) -> CanonicalState:
        return self.store.load_canonical_state()
