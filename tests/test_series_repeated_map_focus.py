from pathlib import Path
from typing import Any, TypeVar

import pytest
import yaml
from pydantic import BaseModel

from auteur.cli import main
from auteur.series import (
    repeated_map_focus,
    vertical_slice_formatters,
    vertical_slice_models,
)
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


def book_three_decision_seed() -> "repeated_map_focus.RepeatedDecisionSeed":
    return repeated_map_focus.RepeatedDecisionSeed(
        question=(
            "How should Book 3 respond to the council's retraction while "
            "preserving the witness's authority?"
        ),
        recommended_option_id="publish-witness-account",
        options=(
            vertical_slice_models.DecisionOption(
                option_id="publish-witness-account",
                label="Publish the witness account",
                summary=(
                    "Give the witness an independent public record that the "
                    "council cannot retract."
                ),
                tradeoff=(
                    "This protects the witness's authority but exposes the "
                    "witness to direct institutional retaliation."
                ),
            ),
            vertical_slice_models.DecisionOption(
                option_id="force-council-hearing",
                label="Force another council hearing",
                summary=(
                    "Use the named falsifier to compel the council to answer "
                    "the witness in public."
                ),
                tradeoff=(
                    "This keeps institutional accountability central but "
                    "lets the council control the forum and timing."
                ),
            ),
        ),
        rationale=(
            "The accepted retraction makes the council unreliable, while the "
            "resolved falsifier question gives the witness a concrete basis "
            "for an independent account."
        ),
    )


def book_four_decision_seed() -> "repeated_map_focus.RepeatedDecisionSeed":
    return repeated_map_focus.RepeatedDecisionSeed(
        question=(
            "How should Book 4 bring the monastery testimony back into "
            "public memory without destroying the archive's evidentiary "
            "chain?"
        ),
        recommended_option_id="publish-verified-testimony",
        options=(
            vertical_slice_models.DecisionOption(
                option_id="publish-verified-testimony",
                label="Publish verified testimony",
                summary=(
                    "Authenticate and publish the testimony while the "
                    "protected archive keeps the original evidence secure."
                ),
                tradeoff=(
                    "This preserves the evidentiary chain but delays public "
                    "release until verification is complete."
                ),
            ),
            vertical_slice_models.DecisionOption(
                option_id="stage-protected-hearing",
                label="Stage a protected hearing",
                summary=(
                    "Present the testimony beside selected archive evidence "
                    "under the treaty's protections."
                ),
                tradeoff=(
                    "This creates immediate public pressure but reveals which "
                    "archive records carry the strongest evidence."
                ),
            ),
        ),
        rationale=(
            "The monastery testimony matters again because Book 4 planning "
            "references it, while the accepted treaty requires the archive's "
            "evidentiary chain to remain intact."
        ),
    )


def write_repeated_decision_seed(
    path: Path,
    seed: "repeated_map_focus.RepeatedDecisionSeed",
) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "question": seed.question,
                "recommended_option_id": seed.recommended_option_id,
                "options": [
                    option.model_dump(mode="json")
                    for option in seed.options
                ],
                "rationale": seed.rationale,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def book_four_burn_archive_recommendation_seed(
) -> "repeated_map_focus.RepeatedDecisionSeed":
    return repeated_map_focus.RepeatedDecisionSeed(
        question=(
            "How should Book 4 bring the monastery testimony back into "
            "public memory without losing the archive's evidentiary chain?"
        ),
        recommended_option_id="burn-archive",
        options=(
            vertical_slice_models.DecisionOption(
                option_id="burn-archive",
                label="Burn the archive",
                summary=(
                    "Destroy the archive so the monastery testimony becomes "
                    "the only surviving public account."
                ),
                tradeoff=(
                    "This makes the testimony unavoidable but destroys the "
                    "accepted evidentiary chain that can authenticate it."
                ),
                incompatible_with_state_refs=[
                    vertical_slice_models.ArtifactRef(
                        artifact_id="realization-bundle-book-3-history",
                        revision=1,
                    )
                ],
                incompatibility_reason=(
                    "Burning the archive contradicts the current accepted "
                    "archive.protection state of treaty protected."
                ),
            ),
            vertical_slice_models.DecisionOption(
                option_id="publish-verified-testimony",
                label="Publish verified testimony",
                summary=(
                    "Authenticate and publish the testimony while preserving "
                    "the protected archive."
                ),
                tradeoff=(
                    "This preserves the evidentiary chain but delays public "
                    "release until verification is complete."
                ),
            ),
        ),
        rationale=(
            "The monastery testimony matters again, but this recommendation "
            "conflicts with the accepted treaty protection."
        ),
    )


def accept_additional_book_three_state(
    service: SeriesVerticalSliceService,
) -> None:
    candidate = RealizationCandidate(
        candidate_id="book-3-archive-access-tightened",
        book_number=3,
        summary="The treaty adds a controlled-access rule for the archive.",
        transitions=[
            vertical_slice_models.StateTransition(
                transition_id="archive-access-tightened",
                subject="archive",
                attribute="public_access",
                before=None,
                after="treaty controlled",
                explanation=(
                    "The accepted treaty limits public access while keeping "
                    "the archive available for verification."
                ),
            )
        ],
        source_refs=[
            vertical_slice_models.ArtifactRef(
                artifact_id="book-3-direction",
                revision=1,
            )
        ],
    )
    service.propose_realization(candidate)
    service.accept_realization(
        candidate.candidate_id,
        accepted_by="archive-author",
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


def test_format_repeated_map_groups_current_book_why_now_and_hides_history(
    tmp_path: Path,
) -> None:
    context = derive_repeated_context(
        build_repeated_scenario(tmp_path, 4), 4
    )
    group = context.group("contested-history")
    testimony = context.item("monastery-testimony")

    output = vertical_slice_formatters.format_repeated_series_map(context)

    assert output.startswith("Series Map: Book 4\n")
    assert "Active continuity" in output
    assert group.summary in output
    assert f"Why it matters now: {group.why_matters_now}" in output
    assert "Current constraints" in output
    assert testimony.summary in output
    assert f"Why it matters now: {testimony.why_matters_now}" in output
    assert "Source references" not in output
    assert "Entry ID:" not in output
    assert "Disposition:" not in output
    assert all(
        entry.summary not in output for entry in context.history_entries
    )
    assert all(
        ref.artifact_id not in output for ref in context.generated_from
    )


def test_format_repeated_map_detail_preserves_provenance_and_history(
    tmp_path: Path,
) -> None:
    context = derive_repeated_context(
        build_repeated_scenario(tmp_path, 4), 4
    )

    output = vertical_slice_formatters.format_repeated_series_map(
        context, detail=True
    )

    assert "Source references:" in output
    assert "Group ID: contested-history" in output
    assert (
        "Entry ID: realization-bundle-book-1-history@1/"
        "monastery-testimony"
    ) in output
    assert "book-1-direction (revision 1)" in output
    assert "book-3-direction (revision 1)" in output
    assert (
        "realization-bundle-book-1-history "
        "(revision 1, fact monastery-testimony)"
    ) in output
    assert (
        "realization-bundle-book-3-history "
        "(revision 1, fact archive-protected)"
    ) in output
    assert "Historical continuity" in output
    assert "Entry ID: commitment-falsifier" in output
    assert "Disposition: resolved" in output


def test_format_repeated_focus_uses_current_book_noncanonical_language(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)
    proposal = service.propose_repeated_next_decision(
        4, decision_seed=book_four_decision_seed()
    )

    output = vertical_slice_formatters.format_repeated_series_focus(proposal)

    assert output.startswith("Series Focus: Book 4\n")
    assert proposal.question in output
    assert proposal.rationale in output
    for option in proposal.options:
        assert option.label in output
        assert option.summary in output
        assert option.tradeoff in output
    assert "This is a planning choice, not Book 4 canon." in output
    assert (
        "Choosing an option records what you want to explore next. You can "
        "change or develop it before accepting a Book 4 direction."
    ) in output
    assert "Book 2 canon" not in output
    assert "Proposal ID:" not in output
    assert "Accepted input sources" not in output
    assert "Option IDs" not in output


def test_format_repeated_focus_detail_preserves_ids_and_accepted_refs(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 3)
    proposal = service.propose_repeated_next_decision(
        3, decision_seed=book_three_decision_seed()
    )

    output = vertical_slice_formatters.format_repeated_series_focus(
        proposal, detail=True
    )

    assert f"Proposal ID: {proposal.proposal_id}" in output
    assert "Accepted input sources" in output
    assert "series-direction (revision 1)" in output
    assert "book-2-direction (revision 1)" in output
    assert "Option IDs" in output
    assert all(option.option_id in output for option in proposal.options)


def test_cli_repeated_map_uses_real_service_context(
    tmp_path: Path,
    capsys,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)

    assert (
        main(
            [
                "series",
                "journey",
                "map",
                str(tmp_path),
                "--book",
                "4",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "Series Map: Book 4" in output
    assert "Active continuity" in output
    assert "monastery.testimony is preserved." in output
    assert "The person who falsified" not in output
    assert service.load_accepted_book_direction(4) is None


def test_cli_repeated_focus_uses_real_service_and_explicit_seed(
    tmp_path: Path,
    capsys,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)
    seed_path = tmp_path / "book-4-focus-seed.yaml"
    seed = book_four_decision_seed()
    write_repeated_decision_seed(seed_path, seed)

    assert (
        main(
            [
                "series",
                "journey",
                "focus",
                str(tmp_path),
                "--book",
                "4",
                "--input",
                str(seed_path),
                "--detail",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "Series Focus: Book 4" in output
    assert "This is a planning choice, not Book 4 canon." in output
    assert "Publish verified testimony" in output
    assert "Book 2 canon" not in output
    proposal_id = next(
        line.removeprefix("Proposal ID: ")
        for line in output.splitlines()
        if line.startswith("Proposal ID: ")
    )
    proposal = service.store.load_next_decision_proposal(proposal_id)
    assert proposal.book_number == 4
    assert proposal.question == seed.question
    assert proposal.options == list(seed.options)
    assert service.load_accepted_book_direction(4) is None


def test_cli_repeated_focus_requires_explicit_seed_input(
    tmp_path: Path,
    capsys,
) -> None:
    build_repeated_scenario(tmp_path, 4)

    assert (
        main(
            [
                "series",
                "journey",
                "focus",
                str(tmp_path),
                "--book",
                "4",
            ]
        )
        == 1
    )
    assert "Book 4 Focus requires --input" in capsys.readouterr().out


def test_book_three_focus_proposal_uses_current_book_and_context(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 3)
    context = service.derive_repeated_book_context(3)
    seed = book_three_decision_seed()

    proposal = service.propose_repeated_next_decision(
        3, decision_seed=seed
    )

    assert proposal.book_number == 3
    assert proposal.question == seed.question
    assert proposal.recommended_option_id == seed.recommended_option_id
    assert proposal.options == list(seed.options)
    assert proposal.rationale == seed.rationale
    assert proposal.accepted_input_refs == context.generated_from
    assert len(proposal.options) >= 2
    assert len({option.tradeoff for option in proposal.options}) == len(
        proposal.options
    )


def test_repeated_focus_rejects_legacy_book_two_route(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)

    with pytest.raises(ValueError, match="Book 3 or later"):
        service.propose_repeated_next_decision(
            2, decision_seed=book_three_decision_seed()
        )

    proposal_root = service.store.root / "proposals" / "next-decision"
    assert not proposal_root.exists()


def test_repeated_focus_copies_mutable_seed_options(tmp_path: Path) -> None:
    service = build_repeated_scenario(tmp_path, 3)
    seed = book_three_decision_seed()
    original_option = seed.options[0].model_copy(deep=True)
    proposal = service.propose_repeated_next_decision(
        3, decision_seed=seed
    )

    seed.options[0].tradeoff = "Mutated after proposal persistence."

    assert proposal.options[0] == original_option
    action = service.record_decision_action(
        proposal.proposal_id,
        action="choose_recommended",
    )
    assert action.selected_option_id == proposal.recommended_option_id
    persisted = service.store.load_next_decision_proposal(
        proposal.proposal_id
    )
    assert persisted.options[0] == original_option


@pytest.mark.parametrize(
    ("action", "selected_option_index", "expected_status"),
    [
        ("choose_recommended", None, "resolved"),
        ("choose_other", 1, "resolved"),
        ("defer", None, "deferred"),
    ],
)
def test_repeated_focus_action_does_not_create_current_book_authority(
    tmp_path: Path,
    action: str,
    selected_option_index: int | None,
    expected_status: str,
) -> None:
    service = build_repeated_scenario(tmp_path / action, 3)
    proposal = service.propose_repeated_next_decision(
        3, decision_seed=book_three_decision_seed()
    )
    canonical_before = service.load_canonical_state()
    realizations_before = service.store.load_accepted_realization_bundles()
    selected_option_id = (
        None
        if selected_option_index is None
        else proposal.options[selected_option_index].option_id
    )

    recorded = service.record_decision_action(
        proposal.proposal_id,
        action=action,
        selected_option_id=selected_option_id,
    )

    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ).status == expected_status
    assert service.store.load_decision_actions(proposal.proposal_id) == [
        recorded
    ]
    assert service.load_accepted_book_direction(3) is None
    assert service.load_canonical_state() == canonical_before
    assert service.store.load_accepted_realization_bundles() == (
        realizations_before
    )


def test_book_four_focus_proposal_shape_uses_current_book(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)
    seed = book_four_decision_seed()

    proposal = service.propose_repeated_next_decision(
        4, decision_seed=seed
    )

    assert proposal.book_number == 4
    assert proposal.question == seed.question
    assert "Book 4" in proposal.question
    assert "Book 2" not in proposal.question
    assert proposal.recommended_option_id == seed.recommended_option_id
    assert proposal.options == list(seed.options)
    assert proposal.rationale == seed.rationale
    assert len({option.tradeoff for option in proposal.options}) == len(
        proposal.options
    )


def test_contradictory_recommended_option_is_rejected(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)
    context = service.derive_repeated_book_context(4)
    proposal = service.propose_repeated_next_decision(
        4,
        decision_seed=book_four_burn_archive_recommendation_seed(),
    )
    authority_before = repeated_authority_snapshot(service)
    canonical_before = service.load_canonical_state()

    with pytest.raises(
        ValueError,
        match="incompatible.*current accepted state",
    ):
        repeated_map_focus.validate_repeated_decision_proposal(
            proposal,
            context,
        )
    with pytest.raises(
        ValueError,
        match="incompatible.*current accepted state",
    ):
        service.validate_repeated_decision_proposal(proposal)
    with pytest.raises(
        ValueError,
        match="incompatible.*current accepted state",
    ):
        service.record_decision_action(
            proposal.proposal_id,
            action="choose_recommended",
        )

    assert repeated_authority_snapshot(service) == authority_before
    assert service.load_canonical_state() == canonical_before
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ) == proposal
    assert service.store.load_decision_actions(proposal.proposal_id) == []


def test_stale_repeated_focus_proposal_cannot_be_exercised(
    tmp_path: Path,
) -> None:
    service = build_repeated_scenario(tmp_path, 4)
    proposal = service.propose_repeated_next_decision(
        4,
        decision_seed=book_four_decision_seed(),
    )
    accept_additional_book_three_state(service)
    current_context = service.derive_repeated_book_context(4)
    authority_before = repeated_authority_snapshot(service)
    canonical_before = service.load_canonical_state()

    with pytest.raises(ValueError, match="stale"):
        repeated_map_focus.validate_repeated_decision_proposal(
            proposal,
            current_context,
        )
    with pytest.raises(ValueError, match="stale"):
        service.validate_repeated_decision_proposal(proposal)
    with pytest.raises(ValueError, match="stale"):
        service.record_decision_action(
            proposal.proposal_id,
            action="choose_recommended",
        )

    assert repeated_authority_snapshot(service) == authority_before
    assert service.load_canonical_state() == canonical_before
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ) == proposal
    assert service.store.load_decision_actions(proposal.proposal_id) == []


@pytest.mark.parametrize("book_number", [3, 10])
def test_current_book_proposal_store_round_trips_matching_book_identity(
    tmp_path: Path,
    book_number: int,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = vertical_slice_models.NextDecisionProposal(
        proposal_id=f"book-{book_number}-next-decision-{'a' * 32}",
        book_number=book_number,
        question=(
            f"Which bounded Book {book_number} direction should planning "
            "examine?"
        ),
        recommended_option_id="first-option",
        options=(
            vertical_slice_models.DecisionOption(
                option_id="first-option",
                label="First option",
                summary="Examine the first bounded option.",
                tradeoff="This prioritizes the first pressure.",
            ),
            vertical_slice_models.DecisionOption(
                option_id="second-option",
                label="Second option",
                summary="Examine the second bounded option.",
                tradeoff="This prioritizes the second pressure.",
            ),
        ),
        rationale="The current accepted inputs support this bounded choice.",
        accepted_input_refs=[
            vertical_slice_models.ArtifactRef(
                artifact_id="series-direction", revision=1
            )
        ],
    )

    service.store.save_next_decision_proposal(proposal)

    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ) == proposal


@pytest.mark.parametrize(
    ("encoded_book_number", "book_number"),
    [("02", 2), ("010", 10)],
)
def test_current_book_proposal_store_rejects_leading_zero_identity_alias(
    tmp_path: Path,
    encoded_book_number: str,
    book_number: int,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    seed = book_three_decision_seed()
    proposal = vertical_slice_models.NextDecisionProposal(
        proposal_id=(
            f"book-{encoded_book_number}-next-decision-{'a' * 32}"
        ),
        book_number=book_number,
        question=seed.question,
        recommended_option_id=seed.recommended_option_id,
        options=seed.options,
        rationale=seed.rationale,
        accepted_input_refs=[
            vertical_slice_models.ArtifactRef(
                artifact_id="series-direction", revision=1
            )
        ],
    )

    with pytest.raises(ValueError, match="ID does not match Book"):
        service.store.save_next_decision_proposal(proposal)

    assert not service.store.next_decision_proposal_path(
        proposal.proposal_id
    ).exists()
