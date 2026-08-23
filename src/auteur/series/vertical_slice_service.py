from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from auteur.provenance import ArtifactMetadata
from auteur.series.vertical_slice_models import (
    AcceptedBookDirection,
    AcceptedSeriesDirection,
    ArtifactRef,
    BookDirection,
    BookDirectionProposal,
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
