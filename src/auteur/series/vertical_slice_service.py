from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from auteur.provenance import ArtifactMetadata
from auteur.series.vertical_slice_models import (
    AcceptedSeriesDirection,
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
