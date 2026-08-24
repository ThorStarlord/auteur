from pathlib import Path
from typing import Any, TypeVar

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


def load_repeated_ledger_fixture() -> dict[str, Any]:
    return yaml.safe_load(
        (FIXTURE_ROOT / "r1-r3-history.yaml").read_text(encoding="utf-8")
    )


def build_repeated_ledger(
    tmp_path: Path,
    *,
    book_two_resolved_commitment_ids: list[str] | None = None,
    use_unrelated_book_two_outcome: bool = False,
    accepted_through_book: int = 3,
    duplicate_fact_id_across_books: bool = False,
) -> SeriesVerticalSliceService:
    ledger = load_repeated_ledger_fixture()
    service = SeriesVerticalSliceService(tmp_path)
    series = load_fixture(str(ledger["series_direction_fixture"]), SeriesDirection)
    series_proposal = service.propose_series_direction(series)
    service.accept_series_direction(
        series_proposal.proposal_id, accepted_by="archive-author"
    )

    for accepted_book in ledger["accepted_books"]:
        book_number = accepted_book["book_number"]
        if book_number > accepted_through_book:
            continue
        if "direction_fixture" in accepted_book:
            direction = load_fixture(
                accepted_book["direction_fixture"], BookDirection
            ).model_copy(
                update={
                    "book_number": book_number,
                    "series_commitment_ids": accepted_book[
                        "series_commitment_ids"
                    ],
                }
            )
        else:
            direction = BookDirection.model_validate(
                accepted_book["direction"]
            )
        book_proposal = service.propose_book_direction(direction)
        service.accept_book_direction(
            book_proposal.proposal_id, accepted_by="archive-author"
        )
        if book_number == 2 and use_unrelated_book_two_outcome:
            accept_unrelated_book_two_outcome(service)
            continue
        realization = RealizationCandidate.model_validate(
            accepted_book["realization"]
        )
        if book_number == 3 and duplicate_fact_id_across_books:
            duplicate = realization.transitions[0].model_copy(
                update={
                    "transition_id": "monastery-testimony",
                    "subject": "monastery_copy",
                    "attribute": "testimony",
                    "before": None,
                    "after": "copied",
                    "explanation": (
                        "A separate accepted Book 3 fact reuses the "
                        "bundle-local transition ID."
                    ),
                }
            )
            realization = realization.model_copy(
                update={"transitions": [*realization.transitions, duplicate]}
            )
        resolved_ids = accepted_book.get("resolved_commitment_ids", [])
        if book_number == 2 and book_two_resolved_commitment_ids is not None:
            resolved_ids = book_two_resolved_commitment_ids
        realization = realization.model_copy(
            update={"resolved_commitment_ids": resolved_ids}
        )
        service.propose_realization(realization)
        service.accept_realization(
            realization.candidate_id, accepted_by="archive-author"
        )

    for candidate_payload in ledger["unaccepted_realizations"]:
        if candidate_payload["book_number"] > accepted_through_book:
            continue
        service.propose_realization(
            RealizationCandidate.model_validate(candidate_payload)
        )

    return service


def build_repeated_scenario(
    tmp_path: Path, planning_book_number: int
) -> SeriesVerticalSliceService:
    service = build_repeated_ledger(
        tmp_path, accepted_through_book=planning_book_number - 1
    )
    enter_fixture_planning_intent(service, planning_book_number)
    return service


def enter_fixture_planning_intent(
    service: SeriesVerticalSliceService, book_number: int
) -> None:
    ledger = load_repeated_ledger_fixture()
    intent = next(
        item
        for item in ledger["planning_intents"]
        if item["book_number"] == book_number
    )
    service.enter_repeated_book_planning(
        book_number,
        entered_by="archive-author",
        intent=intent["intent"],
        relevance_refs=[
            vertical_slice_models.AcceptedFactRef.model_validate(ref)
            for ref in intent["relevance_refs"]
        ],
    )


def derive_repeated_context(
    service: SeriesVerticalSliceService, book_number: int
) -> repeated_map_focus.RepeatedBookPlanningContext:
    return service.derive_repeated_book_context(book_number)


def repeated_authority_snapshot(
    service: SeriesVerticalSliceService,
) -> dict[str, bytes]:
    roots = (
        service.store.root / "accepted",
        service.store.root / "workflow",
        service.store.artifact_store.root,
    )
    paths = [
        path
        for root in roots
        if root.exists()
        for path in root.rglob("*")
        if path.is_file()
    ]
    if service.store.canonical_state_path.is_file():
        paths.append(service.store.canonical_state_path)
    return {
        str(path.relative_to(service.store.project_root)): path.read_bytes()
        for path in paths
    }


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


def accepted_monastery_fact_ref() -> vertical_slice_models.AcceptedFactRef:
    return vertical_slice_models.AcceptedFactRef(
        artifact_id="realization-bundle-book-1-history",
        revision=1,
        fact_id="monastery-testimony",
    )


def write_unaccepted_book_direction_proposal(
    service: SeriesVerticalSliceService, *, book_number: int
) -> vertical_slice_models.BookDirectionProposal:
    direction = load_fixture("book_2_direction.yaml", BookDirection)
    unaccepted = direction.model_copy(
        update={"book_number": book_number}
    )
    return service.propose_book_direction(unaccepted)


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


def test_selector_keeps_active_series_pressure_and_current_consequence(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 2)
    current_proposal = write_unaccepted_book_direction_proposal(
        service, book_number=2
    )

    assert (
        service.load_book_direction_proposal(current_proposal.proposal_id)
        == current_proposal
    )
    assert service.load_accepted_book_direction(2) is None
    assert all(
        bundle.book_number != 2
        for bundle, _metadata in service.store.load_accepted_realization_bundles()
    )
    context = derive_repeated_context(service, 2)

    assert "contested-history" in context.active_ids
    assert "founding-record" in context.active_fact_ids
    context_source_ids = {
        ref.artifact_id
        for item in context.items
        for ref in item.source_refs
    }
    assert current_proposal.proposal_id not in context.dispositions
    assert current_proposal.proposal_id not in context_source_ids
    assert "book-2-direction" not in context_source_ids
    founding_record = next(
        item for item in context.items if item.item_id == "founding-record"
    )
    assert founding_record.source_refs == (
        vertical_slice_models.AcceptedFactRef(
            artifact_id="realization-bundle-book-1-history",
            revision=1,
            fact_id="founding-record",
        ),
    )


def test_selector_keeps_unreferenced_book_one_facts_dormant_at_book_two(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 2)

    context = derive_repeated_context(service, 2)

    assert context.dispositions["broken-lantern"] == "dormant"
    assert context.dispositions["monastery-testimony"] == "dormant"
    assert "broken-lantern" not in context.active_fact_ids
    assert "monastery-testimony" not in context.active_fact_ids


def test_selector_omits_resolved_commitment_from_book_three_active_items(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 3)

    assert service.load_accepted_book_direction(3) is None
    assert all(
        bundle.book_number != 3
        for bundle, _metadata in service.store.load_accepted_realization_bundles()
    )
    context = derive_repeated_context(service, 3)

    assert "commitment-falsifier" not in context.active_ids
    assert "commitment-falsifier" in context.resolved_history_ids
    assert context.dispositions["commitment-falsifier"] == "resolved"


def test_selector_reactivates_old_fact_from_current_book_four_intent(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)

    assert service.load_accepted_book_direction(4) is None
    assert all(
        bundle.book_number != 4
        for bundle, _metadata in service.store.load_accepted_realization_bundles()
    )
    context = derive_repeated_context(service, 4)

    assert "monastery-testimony" in context.active_fact_ids
    assert context.dispositions["monastery-testimony"] == "reactivated"
    assert set(context.dispositions.values()) == {
        "active",
        "resolved",
        "dormant",
        "reactivated",
        "superseded",
        "irrelevant",
    }


def test_selector_omits_superseded_and_recent_irrelevant_material(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)

    assert service.load_accepted_book_direction(4) is None
    assert all(
        bundle.book_number != 4
        for bundle, _metadata in service.store.load_accepted_realization_bundles()
    )
    context = derive_repeated_context(service, 4)

    assert "public-admission" not in context.active_fact_ids
    assert context.dispositions["public-admission"] == "superseded"
    assert "repaired-lantern" not in context.active_fact_ids
    assert context.dispositions["repaired-lantern"] == "irrelevant"


def test_selector_excludes_unaccepted_proposals_even_when_recent(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)

    context = derive_repeated_context(service, 4)

    assert "burn-archive" not in context.active_fact_ids
    assert "burn-archive" not in context.dispositions
    assert "ally-militia" not in context.active_fact_ids
    assert "ally-militia" not in context.dispositions


def test_selector_requires_explicit_current_book_planning_intent(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(tmp_path)

    with pytest.raises(ValueError, match="planning intent"):
        derive_repeated_context(service, 4)


def test_repeated_context_round_trip_through_derived_storage(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)

    derived = derive_repeated_context(service, 4)

    path = service.store.repeated_book_context_path(4)
    assert path == (
        tmp_path
        / ".auteur"
        / "series"
        / "vertical-slice"
        / "derived"
        / "repeated-book-4-context.yaml"
    )
    assert path.is_file()
    assert yaml.safe_load(path.read_text(encoding="utf-8"))[
        "derivation_version"
    ] == "repeated-map-focus-v2-r1"
    reloaded = SeriesVerticalSliceService(
        tmp_path
    ).store.load_repeated_book_context(4)
    assert reloaded == derived
    assert reloaded.model_dump(mode="json") == derived.model_dump(mode="json")


def test_repeated_context_delete_and_rebuild_are_equivalent(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)
    original = derive_repeated_context(service, 4)

    service.store.delete_repeated_book_context(4)

    assert not service.store.repeated_book_context_path(4).exists()
    assert service.store.load_repeated_book_context(4) is None
    rebuilt_service = SeriesVerticalSliceService(tmp_path)
    rebuilt = derive_repeated_context(rebuilt_service, 4)
    assert rebuilt.model_dump(mode="json") == original.model_dump(mode="json")
    assert rebuilt_service.store.load_repeated_book_context(4) == rebuilt


def test_repeated_context_rebuild_preserves_authority_snapshot(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)
    authority_before = repeated_authority_snapshot(service)

    derive_repeated_context(service, 4)
    assert repeated_authority_snapshot(service) == authority_before

    service.store.delete_repeated_book_context(4)
    assert repeated_authority_snapshot(service) == authority_before

    derive_repeated_context(SeriesVerticalSliceService(tmp_path), 4)
    assert repeated_authority_snapshot(service) == authority_before
    assert service.load_accepted_book_direction(4) is None


def test_grouping_keeps_one_group_for_multiple_consequences_of_one_commitment(
    tmp_path: Path,
) -> None:
    context = derive_repeated_context(build_repeated_scenario(tmp_path, 4), 4)

    assert context.group_ids == ("contested-history",)
    assert context.group("contested-history").entry_ids == [
        "realization-bundle-book-1-history@1/monastery-testimony",
        "realization-bundle-book-3-history@1/archive-protected",
    ]
    assert context.group_source_fact_ids("contested-history") == {
        "monastery-testimony",
        "archive-protected",
    }


def test_grouping_preserves_exact_book_one_and_three_supporting_sources(
    tmp_path: Path,
) -> None:
    context = derive_repeated_context(build_repeated_scenario(tmp_path, 4), 4)

    assert context.group("contested-history").source_refs == [
        vertical_slice_models.ArtifactRef(
            artifact_id="series-direction",
            revision=1,
        ),
        vertical_slice_models.ArtifactRef(
            artifact_id="book-1-direction",
            revision=1,
        ),
        vertical_slice_models.ArtifactRef(
            artifact_id="book-3-direction",
            revision=1,
        ),
        vertical_slice_models.AcceptedFactRef(
            artifact_id="realization-bundle-book-1-history",
            revision=1,
            fact_id="monastery-testimony",
        ),
        vertical_slice_models.AcceptedFactRef(
            artifact_id="realization-bundle-book-3-history",
            revision=1,
            fact_id="archive-protected",
        ),
    ]
    assert context.model_dump(mode="json")["groups"][0]["source_refs"] == [
        {
            "artifact_id": "series-direction",
            "revision": 1,
        },
        {
            "artifact_id": "book-1-direction",
            "revision": 1,
        },
        {
            "artifact_id": "book-3-direction",
            "revision": 1,
        },
        {
            "artifact_id": "realization-bundle-book-1-history",
            "revision": 1,
            "fact_id": "monastery-testimony",
        },
        {
            "artifact_id": "realization-bundle-book-3-history",
            "revision": 1,
            "fact_id": "archive-protected",
        },
    ]


def test_grouped_item_has_specific_book_four_monastery_why_now(
    tmp_path: Path,
) -> None:
    context = derive_repeated_context(build_repeated_scenario(tmp_path, 4), 4)

    testimony = context.item("monastery-testimony")
    assert "Book 4" in testimony.why_matters_now
    assert "monastery-testimony" in testimony.why_matters_now
    assert testimony.is_current_constraint
    assert testimony.source_refs == (accepted_monastery_fact_ref(),)
    assert all(entry.source_refs for entry in context.entries)
    assert all(group.source_refs for group in context.groups)


def test_fact_identity_distinguishes_duplicate_ids_across_accepted_bundles(
    tmp_path: Path,
) -> None:
    service = build_repeated_ledger(
        tmp_path,
        duplicate_fact_id_across_books=True,
    )
    book_one_ref = accepted_monastery_fact_ref()
    book_three_ref = vertical_slice_models.AcceptedFactRef(
        artifact_id="realization-bundle-book-3-history",
        revision=1,
        fact_id="monastery-testimony",
    )
    service.enter_repeated_book_planning(
        4,
        entered_by="archive-author",
        intent="Use both accepted testimony facts.",
        relevance_refs=[book_one_ref, book_three_ref],
    )

    context = derive_repeated_context(service, 4)
    book_one_entry_id = (
        "realization-bundle-book-1-history@1/monastery-testimony"
    )
    book_three_entry_id = (
        "realization-bundle-book-3-history@1/monastery-testimony"
    )

    assert context.item(book_one_entry_id).source_refs == (book_one_ref,)
    assert context.item(book_three_entry_id).source_refs == (book_three_ref,)
    with pytest.raises(ValueError, match="ambiguous"):
        context.item("monastery-testimony")
    assert context.dispositions[book_one_entry_id] == "reactivated"
    assert context.dispositions[book_three_entry_id] == "active"
    assert "monastery-testimony" not in context.dispositions
    assert set(context.group("contested-history").entry_ids) == {
        book_one_entry_id,
        book_three_entry_id,
    }
    assert "monastery-testimony" in context.active_fact_ids
