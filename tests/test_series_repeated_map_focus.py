from pathlib import Path
from typing import TypeVar

import pytest
import yaml
from pydantic import BaseModel

from auteur.series import repeated_map_focus, vertical_slice_models
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


def build_repeated_ledger(
    tmp_path: Path,
    *,
    book_two_resolved_commitment_ids: list[str] | None = None,
    use_unrelated_book_two_outcome: bool = False,
) -> SeriesVerticalSliceService:
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
        if book_number == 2 and use_unrelated_book_two_outcome:
            accept_unrelated_book_two_outcome(service)
            continue
        realization = load_fixture(
            f"book_{book_number}_realization.yaml", RealizationCandidate
        )
        if book_number == 2 and book_two_resolved_commitment_ids is not None:
            payload = realization.model_dump(mode="json")
            payload["resolved_commitment_ids"] = (
                book_two_resolved_commitment_ids
            )
            realization = RealizationCandidate.model_validate(payload)
        service.propose_realization(realization)
        service.accept_realization(
            realization.candidate_id, accepted_by="archive-author"
        )

    return service


def accept_unrelated_book_two_outcome(
    service: SeriesVerticalSliceService,
) -> None:
    realization = load_fixture(
        "book_2_unrelated_realization.yaml", RealizationCandidate
    )
    assert realization.resolved_commitment_ids == []
    service.propose_realization(realization)
    service.accept_realization(
        realization.candidate_id, accepted_by="archive-author"
    )


def accept_book_three_direction(service: SeriesVerticalSliceService) -> None:
    direction = load_fixture("book_2_direction.yaml", BookDirection)
    book_three = direction.model_copy(update={"book_number": 3})
    proposal = service.propose_book_direction(book_three)
    service.accept_book_direction(
        proposal.proposal_id, accepted_by="archive-author"
    )


def accepted_monastery_fact_ref() -> BaseModel:
    return vertical_slice_models.AcceptedFactRef(
        artifact_id="realization-bundle-book-1-history",
        revision=1,
        fact_id="monastery-testimony",
    )


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


def test_current_state_evidence_keeps_latest_transition_current(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(tmp_path)

    evidence = service.derive_current_state_evidence(3)

    assert evidence["council.archive_position"] == (
        repeated_map_focus.CurrentStateEvidence(
            key="council.archive_position",
            current_value="retracted admission",
            current_fact_id="admission-retracted",
            current_source_ref=vertical_slice_models.AcceptedFactRef(
                artifact_id="realization-bundle-book-2-history",
                revision=1,
                fact_id="admission-retracted",
            ),
            superseded_fact_ids=("public-admission",),
        )
    )


def test_superseded_state_is_not_selected_as_current_map_evidence(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(tmp_path)

    evidence = service.derive_current_state_evidence(3)

    current = evidence["council.archive_position"]
    assert current.current_fact_id != "public-admission"
    assert "public-admission" in current.superseded_fact_ids


def test_current_state_evidence_does_not_mutate_canonical_state(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(tmp_path)
    accept_book_three_direction(service)
    before = service.load_canonical_state()
    stored_before = service.store.canonical_state_path.read_bytes()

    service.derive_current_state_evidence(4)

    assert service.load_canonical_state() == before
    assert service.store.canonical_state_path.read_bytes() == stored_before


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


def test_accepted_outcome_can_explicitly_resolve_a_series_commitment(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(
        tmp_path,
        book_two_resolved_commitment_ids=["commitment-falsifier"],
    )

    bundle = service.store.load_accepted_realization_bundles()[1][0]
    snapshot = service.load_repeated_history_for_book(3)

    assert "commitment-falsifier" in bundle.resolved_commitment_ids
    assert (
        "commitment-falsifier"
        in snapshot.explicitly_resolved_commitment_ids
    )


def test_resolution_is_not_inferred_from_similar_text(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(
        tmp_path, use_unrelated_book_two_outcome=True
    )

    bundle = service.store.load_accepted_realization_bundles()[1][0]
    snapshot = service.load_repeated_history_for_book(3)

    assert bundle.candidate_id == "book-2-unrelated-history"
    assert bundle.resolved_commitment_ids == []
    assert (
        "commitment-falsifier"
        not in snapshot.explicitly_resolved_commitment_ids
    )


def test_realization_acceptance_rejects_unknown_resolved_commitment_id(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError, match="Unknown accepted Series commitment resolution"
    ):
        build_repeated_ledger(
            tmp_path,
            book_two_resolved_commitment_ids=["unknown-commitment"],
        )


def test_book_n_planning_intent_references_accepted_fact_without_authority(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(tmp_path)
    accept_book_three_direction(service)
    monastery_ref = accepted_monastery_fact_ref()

    intent = service.enter_repeated_book_planning(
        4,
        entered_by="archive-author",
        intent="Return to the monastery testimony.",
        relevance_refs=[monastery_ref],
    )

    reloaded = SeriesVerticalSliceService(
        tmp_path
    ).store.load_book_planning_intent(4)
    assert intent.book_number == 4
    assert intent.relevance_refs == [monastery_ref]
    assert reloaded == intent
    assert service.load_accepted_book_direction(4) is None
    assert service.load_accepted_book_direction(3) is not None


def test_planning_intent_rejects_fact_outside_accepted_history(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(tmp_path)
    accept_book_three_direction(service)
    stale_ref = accepted_monastery_fact_ref().model_copy(
        update={"revision": 999}
    )

    with pytest.raises(ValueError, match="accepted history"):
        service.enter_repeated_book_planning(
            4,
            entered_by="archive-author",
            intent="Return to the monastery testimony.",
            relevance_refs=[stale_ref],
        )
