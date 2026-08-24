from pathlib import Path
from typing import TypeVar

import pytest
import yaml
from pydantic import BaseModel

from auteur.series.vertical_slice_models import (
    BookDirection,
    RealizationCandidate,
    SeriesDirection,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "repeated_map_focus_v2"
ModelT = TypeVar("ModelT", bound=BaseModel)


def load_fixture(name: str, model_type: type[ModelT]) -> ModelT:
    payload = yaml.safe_load(
        (FIXTURE_ROOT / name).read_text(encoding="utf-8")
    )
    return model_type.model_validate(payload)


def build_repeated_ledger(tmp_path: Path) -> SeriesVerticalSliceService:
    service = SeriesVerticalSliceService(tmp_path)
    series = load_fixture("series_direction.yaml", SeriesDirection)
    series_proposal = service.propose_series_direction(series)
    service.accept_series_direction(
        series_proposal.proposal_id, accepted_by="archive-author"
    )

    for book_number in (1, 2):
        direction = load_fixture(
            f"book_{book_number}_direction.yaml", BookDirection
        )
        book_proposal = service.propose_book_direction(direction)
        service.accept_book_direction(
            book_proposal.proposal_id, accepted_by="archive-author"
        )
        realization = load_fixture(
            f"book_{book_number}_realization.yaml", RealizationCandidate
        )
        service.propose_realization(realization)
        service.accept_realization(
            realization.candidate_id, accepted_by="archive-author"
        )

    return service


def write_unaccepted_book_direction_proposal(
    service: SeriesVerticalSliceService, *, book_number: int
) -> None:
    direction = load_fixture("book_2_direction.yaml", BookDirection)
    unaccepted = direction.model_copy(
        update={"book_number": book_number}
    )
    service.propose_book_direction(unaccepted)


def corrupt_book_two_metadata(service: SeriesVerticalSliceService) -> None:
    metadata = service.load_book_direction_metadata(2)
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["revision"] = 999
    sidecar.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )


def test_book_n_history_includes_only_accepted_sources_through_previous_book(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(tmp_path)

    snapshot = service.load_repeated_history_for_book(3)

    assert [book.direction.book_number for book in snapshot.books] == [1, 2]
    assert all(bundle.book_number <= 2 for bundle in snapshot.realizations)
    assert snapshot.planning_book_number == 3


def test_book_n_history_rejects_unaccepted_sources(tmp_path: Path) -> None:
    service = build_repeated_ledger(tmp_path)
    write_unaccepted_book_direction_proposal(service, book_number=3)

    snapshot = service.load_repeated_history_for_book(3)

    assert all(book.direction.book_number <= 2 for book in snapshot.books)
    assert snapshot.planning_book_number == 3


def test_book_n_history_validates_current_source_revisions(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(tmp_path)
    corrupt_book_two_metadata(service)

    with pytest.raises(
        ValueError, match="accepted.*revision|source metadata"
    ):
        service.load_repeated_history_for_book(3)
