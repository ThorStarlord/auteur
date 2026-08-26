from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from auteur.series import vertical_slice_models
from auteur.provenance import (
    ArtifactMetadata,
    DependencyKind,
    DependencySource,
    Lifecycle,
)
from auteur.series.vertical_slice_models import (
    AcceptedSeriesDirection,
    ArtifactRef,
    BookDirection,
    SeriesDirection,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "archive_of_lies_vertical_slice"
    / "series_direction.yaml"
)
BOOK_FIXTURE = FIXTURE.with_name("book_1_direction.yaml")
OUTCOME_FIXTURE = FIXTURE.with_name("book_1_outcome.yaml")
CONTEXT_FIXTURE = FIXTURE.with_name("book_2_context_expected.yaml")
DECISION_FIXTURE = FIXTURE.with_name("book_2_decision_expected.yaml")


def load_direction() -> SeriesDirection:
    return SeriesDirection.model_validate(
        yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    )


def load_book_direction() -> BookDirection:
    return BookDirection.model_validate(
        yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    )


def load_realization_candidate():
    return vertical_slice_models.RealizationCandidate.model_validate(
        yaml.safe_load(OUTCOME_FIXTURE.read_text(encoding="utf-8"))
    )


def accept_archive_series(
    service: SeriesVerticalSliceService,
) -> tuple[AcceptedSeriesDirection, ArtifactMetadata]:
    proposal = service.propose_series_direction(load_direction())
    accepted = service.accept_series_direction(
        proposal.proposal_id, accepted_by="archive-author"
    )
    metadata = service.load_series_direction_metadata()
    assert metadata is not None
    return accepted, metadata


def accept_archive_book(service: SeriesVerticalSliceService) -> ArtifactMetadata:
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(
        proposal.proposal_id, accepted_by="archive-author"
    )
    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    return metadata


def accept_archive_outcome(
    service: SeriesVerticalSliceService,
) -> tuple[
    vertical_slice_models.AcceptedRealizationBundle,
    ArtifactMetadata,
]:
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    accepted = service.accept_realization(
        candidate.candidate_id, accepted_by="archive-author"
    )
    bundles = service.store.load_accepted_realization_bundles()
    assert bundles[-1][0] == accepted
    return bundles[-1]


def accept_unrelated_newer_outcome(
    service: SeriesVerticalSliceService,
    *,
    transition_id: str = "mara-at-north-quay",
) -> tuple[
    vertical_slice_models.AcceptedRealizationBundle,
    ArtifactMetadata,
]:
    book_metadata = service.load_book_direction_metadata(1)
    assert book_metadata is not None
    candidate = vertical_slice_models.RealizationCandidate(
        candidate_id="mara-reaches-north-quay",
        book_number=1,
        summary="Mara reaches the north quay after the ledger is exposed.",
        transitions=[
            vertical_slice_models.StateTransition(
                transition_id=transition_id,
                subject="mara",
                attribute="location",
                before=None,
                after="north quay",
                explanation="Mara travels there after the archive hearing.",
            )
        ],
        source_refs=[
            ArtifactRef(
                artifact_id="book-1-direction",
                revision=book_metadata.revision,
            )
        ],
    )
    service.propose_realization(candidate)
    accepted = service.accept_realization(
        candidate.candidate_id, accepted_by="archive-author"
    )
    bundles = service.store.load_accepted_realization_bundles()
    assert bundles[-1][0] == accepted
    return bundles[-1]


def load_expected_book_2_context():
    return vertical_slice_models.BookPlanningContext.model_validate(
        yaml.safe_load(CONTEXT_FIXTURE.read_text(encoding="utf-8"))
    )


def load_expected_book_2_decision(proposal_id: str):
    expected = vertical_slice_models.NextDecisionProposal.model_validate(
        yaml.safe_load(DECISION_FIXTURE.read_text(encoding="utf-8"))
    )
    return expected.model_copy(update={"proposal_id": proposal_id})


def prepare_book_2_decision(
    service: SeriesVerticalSliceService,
):
    accept_archive_outcome(service)
    service.enter_book_planning(2, entered_by="archive-author")
    return service.propose_next_decision(2)


def advance_archive_series_and_book_provenance(
    service: SeriesVerticalSliceService,
) -> None:
    revised_series = load_direction().model_copy(
        update={
            "promise": "Every recovered account changes who controls history."
        }
    )
    series_proposal = service.propose_series_direction(revised_series)
    service.accept_series_direction(
        series_proposal.proposal_id,
        accepted_by="archive-author",
    )
    book_proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(
        book_proposal.proposal_id,
        accepted_by="archive-author",
    )
    assert service.load_series_direction_metadata().revision == 2
    assert service.load_book_direction_metadata(1).revision == 2


def decision_authority_snapshot(service: SeriesVerticalSliceService):
    return (
        service.load_accepted_series_direction(),
        service.load_series_direction_metadata(),
        service.load_accepted_book_direction(1),
        service.load_book_direction_metadata(1),
        service.load_accepted_book_direction(2),
        service.load_book_direction_metadata(2),
        service.store.load_accepted_realization_bundles(),
        service.load_canonical_state(),
    )


def assert_decision_action_is_non_canonical(
    service: SeriesVerticalSliceService,
    authority_before: object,
) -> None:
    assert decision_authority_snapshot(service) == authority_before
    assert not list(service.store.project_root.rglob("bible.json"))


def test_vertical_slice_acceptances_record_timestamps(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    _, series_metadata = accept_archive_series(service)
    book_proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(
        book_proposal.proposal_id,
        accepted_by="archive-author",
    )
    book_metadata = service.load_book_direction_metadata(1)
    assert book_metadata is not None
    realization = service.propose_realization(load_realization_candidate())
    service.accept_realization(
        realization.candidate_id,
        accepted_by="archive-author",
    )
    _, realization_metadata = service.store.load_accepted_realization_bundles()[-1]

    timestamps = (
        series_metadata.accepted_at,
        book_metadata.accepted_at,
        realization_metadata.accepted_at,
    )
    assert all(timestamp is not None for timestamp in timestamps)
    assert all(
        datetime.fromisoformat(timestamp).utcoffset()
        == timezone.utc.utcoffset(None)
        for timestamp in timestamps
        if timestamp is not None
    )


def test_next_decision_cites_context_inputs_and_tradeoff(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)

    with pytest.raises(ValueError, match="explicitly enter Book 2 planning"):
        service.propose_next_decision(2)

    service.enter_book_planning(2, entered_by="archive-author")
    service.derive_book_context(2)
    service.delete_derived_book_context(2)

    proposal = service.propose_next_decision(2)

    assert proposal == load_expected_book_2_decision(proposal.proposal_id)
    assert proposal.accepted_input_refs == [
        ArtifactRef(artifact_id="series-direction", revision=1),
        ArtifactRef(artifact_id="book-1-direction", revision=1),
        ArtifactRef(
            artifact_id="realization-bundle-recovered-founding-ledger",
            revision=1,
        ),
    ]
    assert proposal.recommended_option_id in {
        option.option_id for option in proposal.options
    }
    assert proposal.rationale.strip()
    assert all(option.tradeoff.strip() for option in proposal.options)
    assert all(
        option.incompatible_with_state_refs == []
        for option in proposal.options
    )
    assert all(
        option.incompatibility_reason is None for option in proposal.options
    )


def test_choose_recommended_does_not_accept_book_2_direction(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    authority_before = decision_authority_snapshot(service)

    action = service.record_decision_action(
        proposal.proposal_id,
        action="choose_recommended",
    )

    assert action.selected_option_id == proposal.recommended_option_id
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ).status == "resolved"
    assert service.store.load_decision_actions(proposal.proposal_id) == [action]
    assert_decision_action_is_non_canonical(service, authority_before)


def test_choose_another_presented_option_is_non_canonical(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    authority_before = decision_authority_snapshot(service)
    other_option = next(
        option
        for option in proposal.options
        if option.option_id != proposal.recommended_option_id
    )

    action = service.record_decision_action(
        proposal.proposal_id,
        action="choose_other",
        selected_option_id=other_option.option_id,
    )

    assert action.selected_option_id == other_option.option_id
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ).status == "resolved"
    assert service.store.load_decision_actions(proposal.proposal_id) == [action]
    assert_decision_action_is_non_canonical(service, authority_before)


def test_defer_preserves_open_decision_without_canonical_mutation(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    authority_before = decision_authority_snapshot(service)

    action = service.record_decision_action(
        proposal.proposal_id,
        action="defer",
    )

    assert action.selected_option_id is None
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ).status == "deferred"
    assert service.store.load_decision_actions(proposal.proposal_id) == [action]
    assert_decision_action_is_non_canonical(service, authority_before)


def test_unknown_decision_option_is_rejected(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    authority_before = decision_authority_snapshot(service)

    with pytest.raises(ValueError, match="Unknown decision option"):
        service.record_decision_action(
            proposal.proposal_id,
            action="choose_other",
            selected_option_id="invent-a-book-two-direction",
        )

    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ).status == "proposed"
    assert service.store.load_decision_actions(proposal.proposal_id) == []
    assert_decision_action_is_non_canonical(service, authority_before)


def test_next_decision_load_rejects_payload_with_different_proposal_id(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    payload = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    payload["proposal_id"] = "different-next-decision"
    proposal_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="does not match requested proposal"):
        service.store.load_next_decision_proposal(proposal.proposal_id)
    with pytest.raises(ValueError, match="does not match requested proposal"):
        service.record_decision_action(
            proposal.proposal_id,
            action="choose_recommended",
        )

    assert not service.store.decision_actions_path(proposal.proposal_id).exists()
    assert not service.store.decision_actions_path(
        "different-next-decision"
    ).exists()


def test_next_decision_rejects_unknown_recommended_option() -> None:
    payload = yaml.safe_load(DECISION_FIXTURE.read_text(encoding="utf-8"))
    payload["recommended_option_id"] = "not-a-presented-option"

    with pytest.raises(
        ValidationError,
        match="recommended_option_id must reference a presented option",
    ):
        vertical_slice_models.NextDecisionProposal.model_validate(payload)


def test_choose_recommended_rejects_reloaded_unknown_recommended_option(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    payload = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    payload["recommended_option_id"] = "not-a-presented-option"
    proposal_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(
        ValidationError,
        match="recommended_option_id must reference a presented option",
    ):
        service.record_decision_action(
            proposal.proposal_id,
            action="choose_recommended",
        )

    assert not service.store.decision_actions_path(proposal.proposal_id).exists()


def test_reloaded_decision_action_rejects_unknown_selected_option(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    other_option = next(
        option
        for option in proposal.options
        if option.option_id != proposal.recommended_option_id
    )
    service.record_decision_action(
        proposal.proposal_id,
        action="choose_other",
        selected_option_id=other_option.option_id,
    )
    actions_path = service.store.decision_actions_path(proposal.proposal_id)
    payload = yaml.safe_load(actions_path.read_text(encoding="utf-8"))
    payload[0]["selected_option_id"] = "not-a-presented-option"
    actions_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Unknown decision option"):
        service.store.load_decision_actions(proposal.proposal_id)


def test_decision_status_failure_restores_prior_proposal_and_action_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    actions_path = service.store.decision_actions_path(proposal.proposal_id)
    proposal_before = proposal_path.read_bytes()
    authority_before = decision_authority_snapshot(service)

    def fail_status_write(_proposal: object) -> None:
        raise OSError("decision status persistence failed")

    monkeypatch.setattr(
        service.store,
        "_write_next_decision_proposal",
        fail_status_write,
    )

    with pytest.raises(OSError, match="decision status persistence failed"):
        service.record_decision_action(
            proposal.proposal_id,
            action="choose_recommended",
        )

    assert proposal_path.read_bytes() == proposal_before
    assert not actions_path.exists()
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ).status == "proposed"
    assert service.store.load_decision_actions(proposal.proposal_id) == []
    assert_decision_action_is_non_canonical(service, authority_before)


def test_stale_next_decision_inputs_reject_action_without_workflow_mutation(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    proposal_before = proposal_path.read_bytes()

    advance_archive_series_and_book_provenance(service)
    authority_before = decision_authority_snapshot(service)

    with pytest.raises(ValueError, match="accepted inputs are stale"):
        service.record_decision_action(
            proposal.proposal_id,
            action="choose_recommended",
        )

    assert proposal_path.read_bytes() == proposal_before
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ).status == "proposed"
    assert service.store.load_decision_actions(proposal.proposal_id) == []
    assert_decision_action_is_non_canonical(service, authority_before)


def test_terminal_decision_exact_retry_is_idempotent_after_inputs_stale(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    first = service.record_decision_action(
        proposal.proposal_id,
        action="choose_recommended",
    )
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    actions_path = service.store.decision_actions_path(proposal.proposal_id)
    proposal_before = proposal_path.read_bytes()
    actions_before = actions_path.read_bytes()

    advance_archive_series_and_book_provenance(service)
    authority_before = decision_authority_snapshot(service)

    repeated = service.record_decision_action(
        proposal.proposal_id,
        action="choose_recommended",
    )

    assert repeated == first
    assert proposal_path.read_bytes() == proposal_before
    assert actions_path.read_bytes() == actions_before
    with pytest.raises(ValueError, match="already has a conflicting action"):
        service.record_decision_action(
            proposal.proposal_id,
            action="defer",
        )
    assert proposal_path.read_bytes() == proposal_before
    assert actions_path.read_bytes() == actions_before
    assert_decision_action_is_non_canonical(service, authority_before)


def test_direct_proposal_status_save_rejects_history_mismatch_without_write(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    actions_path = service.store.decision_actions_path(proposal.proposal_id)
    proposal_before = proposal_path.read_bytes()

    with pytest.raises(ValueError, match="status/history mismatch"):
        service.store.save_next_decision_proposal(
            proposal.model_copy(update={"status": "resolved"})
        )

    assert proposal_path.read_bytes() == proposal_before
    assert not actions_path.exists()
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ).status == "proposed"
    assert service.store.load_decision_actions(proposal.proposal_id) == []


def test_proposed_next_decision_proposal_is_immutable_after_creation(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    proposal_before = proposal_path.read_bytes()

    service.store.save_next_decision_proposal(proposal)
    assert proposal_path.read_bytes() == proposal_before

    with pytest.raises(ValueError, match="immutable once created"):
        service.store.save_next_decision_proposal(
            proposal.model_copy(
                update={"rationale": "Replace the persisted recommendation."}
            )
        )

    assert proposal_path.read_bytes() == proposal_before
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ) == proposal


def test_terminal_next_decision_proposal_is_immutable(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    action = service.record_decision_action(
        proposal.proposal_id,
        action="choose_recommended",
    )
    terminal = service.store.load_next_decision_proposal(
        proposal.proposal_id
    )
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    actions_path = service.store.decision_actions_path(proposal.proposal_id)
    proposal_before = proposal_path.read_bytes()
    actions_before = actions_path.read_bytes()

    with pytest.raises(ValueError, match="immutable once created"):
        service.store.save_next_decision_proposal(
            terminal.model_copy(
                update={"question": "Replace the persisted question?"}
            )
        )

    assert proposal_path.read_bytes() == proposal_before
    assert actions_path.read_bytes() == actions_before
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ) == terminal
    assert service.store.load_decision_actions(proposal.proposal_id) == [action]


def test_direct_decision_action_save_refuses_partial_history(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    actions_path = service.store.decision_actions_path(proposal.proposal_id)
    proposal_before = proposal_path.read_bytes()
    action = vertical_slice_models.DecisionAction(
        proposal_id=proposal.proposal_id,
        action="choose_recommended",
        selected_option_id=proposal.recommended_option_id,
        recorded_at=datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError, match="saved with proposal status"):
        service.store.save_decision_action(action)

    assert proposal_path.read_bytes() == proposal_before
    assert not actions_path.exists()
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ).status == "proposed"
    assert service.store.load_decision_actions(proposal.proposal_id) == []


def test_coordinated_decision_save_rejects_semantic_proposal_mutation(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    actions_path = service.store.decision_actions_path(proposal.proposal_id)
    proposal_before = proposal_path.read_bytes()
    action = vertical_slice_models.DecisionAction(
        proposal_id=proposal.proposal_id,
        action="choose_recommended",
        selected_option_id=proposal.recommended_option_id,
        recorded_at=datetime.now(timezone.utc),
    )
    mutated_terminal = proposal.model_copy(
        update={
            "rationale": "Replace the persisted recommendation.",
            "status": "resolved",
        }
    )

    with pytest.raises(ValueError, match="does not match persisted proposal"):
        service.store.save_decision_action_with_status(
            action,
            mutated_terminal,
        )

    assert proposal_path.read_bytes() == proposal_before
    assert not actions_path.exists()
    assert service.store.load_next_decision_proposal(
        proposal.proposal_id
    ) == proposal
    assert service.store.load_decision_actions(proposal.proposal_id) == []


@pytest.mark.parametrize(
    "tampering",
    ["proposed-with-action", "resolved-without-action", "deferred-with-choose"],
)
def test_decision_reload_rejects_status_history_mismatch(
    tmp_path: Path,
    tampering: str,
) -> None:
    service = SeriesVerticalSliceService(tmp_path / tampering)
    proposal = prepare_book_2_decision(service)
    actions_path = service.store.decision_actions_path(proposal.proposal_id)

    if tampering == "proposed-with-action":
        action = vertical_slice_models.DecisionAction(
            proposal_id=proposal.proposal_id,
            action="choose_recommended",
            selected_option_id=proposal.recommended_option_id,
            recorded_at=datetime.now(timezone.utc),
        )
        actions_path.parent.mkdir(parents=True, exist_ok=True)
        actions_path.write_text(
            yaml.safe_dump([action.model_dump(mode="json")], sort_keys=False),
            encoding="utf-8",
        )
    elif tampering == "resolved-without-action":
        service.record_decision_action(
            proposal.proposal_id,
            action="choose_recommended",
        )
        actions_path.unlink()
    else:
        service.record_decision_action(
            proposal.proposal_id,
            action="defer",
        )
        payload = yaml.safe_load(actions_path.read_text(encoding="utf-8"))
        payload[0]["action"] = "choose_recommended"
        payload[0]["selected_option_id"] = proposal.recommended_option_id
        actions_path.write_text(
            yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
        )

    with pytest.raises(ValueError, match="status/history mismatch"):
        service.store.load_next_decision_proposal(proposal.proposal_id)
    with pytest.raises(ValueError, match="status/history mismatch"):
        service.store.load_decision_actions(proposal.proposal_id)


@pytest.mark.parametrize(
    ("action", "selected_option"),
    [
        ("choose_recommended", None),
        ("choose_other", "trace-institutional-cover-up"),
        ("defer", None),
    ],
)
def test_repeated_identical_decision_action_is_idempotent(
    tmp_path: Path,
    action: str,
    selected_option: str | None,
) -> None:
    service = SeriesVerticalSliceService(tmp_path / action)
    proposal = prepare_book_2_decision(service)
    first = service.record_decision_action(
        proposal.proposal_id,
        action=action,
        selected_option_id=selected_option,
    )
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    actions_path = service.store.decision_actions_path(proposal.proposal_id)
    proposal_after_first = proposal_path.read_bytes()
    actions_after_first = actions_path.read_bytes()

    repeated = service.record_decision_action(
        proposal.proposal_id,
        action=action,
        selected_option_id=selected_option,
    )

    assert repeated == first
    assert proposal_path.read_bytes() == proposal_after_first
    assert actions_path.read_bytes() == actions_after_first
    assert service.store.load_decision_actions(proposal.proposal_id) == [first]


@pytest.mark.parametrize(
    ("first_action", "conflicting_action"),
    [
        ("choose_recommended", "defer"),
        ("defer", "choose_recommended"),
    ],
)
def test_conflicting_action_after_terminal_decision_is_rejected(
    tmp_path: Path,
    first_action: str,
    conflicting_action: str,
) -> None:
    service = SeriesVerticalSliceService(tmp_path / first_action)
    proposal = prepare_book_2_decision(service)
    first = service.record_decision_action(
        proposal.proposal_id,
        action=first_action,
    )
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    actions_path = service.store.decision_actions_path(proposal.proposal_id)
    proposal_before = proposal_path.read_bytes()
    actions_before = actions_path.read_bytes()

    with pytest.raises(ValueError, match="already has a conflicting action"):
        service.record_decision_action(
            proposal.proposal_id,
            action=conflicting_action,
        )

    assert proposal_path.read_bytes() == proposal_before
    assert actions_path.read_bytes() == actions_before
    assert service.store.load_decision_actions(proposal.proposal_id) == [first]


def test_next_decision_requires_unique_option_ids() -> None:
    payload = yaml.safe_load(DECISION_FIXTURE.read_text(encoding="utf-8"))
    payload["options"][1]["option_id"] = payload["options"][0]["option_id"]

    with pytest.raises(
        ValidationError,
        match="option_id values must be unique",
    ):
        vertical_slice_models.NextDecisionProposal.model_validate(payload)


def test_next_decision_book_number_must_be_greater_than_one() -> None:
    payload = yaml.safe_load(DECISION_FIXTURE.read_text(encoding="utf-8"))
    payload["book_number"] = 1

    with pytest.raises(ValidationError):
        vertical_slice_models.NextDecisionProposal.model_validate(payload)


def test_book_two_decision_rejects_mutated_book_number_on_reload_and_action(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    proposal_path = service.store.next_decision_proposal_path(
        proposal.proposal_id
    )
    payload = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    payload["book_number"] = 3
    proposal_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="must be for Book 2"):
        service.store.load_next_decision_proposal(proposal.proposal_id)
    with pytest.raises(ValueError, match="must be for Book 2"):
        service.record_decision_action(
            proposal.proposal_id,
            action="choose_recommended",
        )
    assert not service.store.decision_actions_path(proposal.proposal_id).exists()


def test_book_two_decision_rejects_invalid_proposal_id_convention(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = prepare_book_2_decision(service)
    invalid_id = "book-2-next-decision-not-a-uuid"
    payload = proposal.model_dump(mode="json")
    payload["proposal_id"] = invalid_id
    invalid_path = service.store.next_decision_proposal_path(invalid_id)
    invalid_path.parent.mkdir(parents=True, exist_ok=True)
    invalid_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="ID does not match Book 2 convention"):
        service.store.load_next_decision_proposal(invalid_id)


def test_book_planning_models_enforce_bounded_shape() -> None:
    with pytest.raises(ValidationError):
        vertical_slice_models.PlanningEntry(
            book_number=1,
            entered_by="archive-author",
            entered_at=datetime.now(timezone.utc),
        )
    with pytest.raises(ValidationError):
        vertical_slice_models.CarryForwardItem(
            item_id="invalid",
            kind="series_commitment",
            summary="Invalid because it has no source.",
            why_matters_now="It does not.",
            source_refs=[],
        )
    with pytest.raises(ValidationError):
        vertical_slice_models.BookPlanningContext(
            book_number=2,
            generated_from=[],
            items=[],
            derivation_version="archive-of-lies-book-2-v1",
        )


def test_book_2_planning_requires_explicit_author_entry(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)

    with pytest.raises(ValueError, match="explicitly enter Book 2 planning"):
        service.derive_book_context(2)


def test_mismatched_planning_entry_cannot_unlock_book_2_context(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)
    service.enter_book_planning(3, entered_by="archive-author")
    book_3_path = service.store.planning_entry_path(3)
    book_2_path = service.store.planning_entry_path(2)
    book_2_path.parent.mkdir(parents=True, exist_ok=True)
    book_2_path.write_bytes(book_3_path.read_bytes())

    with pytest.raises(ValueError, match="does not match requested Book 2"):
        service.store.load_planning_entry(2)
    with pytest.raises(ValueError, match="does not match requested Book 2"):
        service.derive_book_context(2)

    assert not service.store.book_planning_context_path(2).exists()


def test_book_2_entry_does_not_create_book_2_direction_or_canon(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)
    state_before = service.load_canonical_state()
    bundles_before = service.store.load_accepted_realization_bundles()

    entry = service.enter_book_planning(2, entered_by="archive-author")

    assert entry.book_number == 2
    assert entry.entered_by == "archive-author"
    assert entry.entered_at.utcoffset() == timezone.utc.utcoffset(entry.entered_at)
    assert service.store.load_planning_entry(2) == entry
    assert service.load_accepted_book_direction(2) is None
    assert service.load_book_direction_metadata(2) is None
    assert service.load_canonical_state() == state_before
    assert service.store.load_accepted_realization_bundles() == bundles_before


def test_repeated_book_planning_entry_preserves_original_workflow_record(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    first = service.enter_book_planning(2, entered_by="archive-author")
    path = service.store.planning_entry_path(2)
    original_bytes = path.read_bytes()

    repeated = service.enter_book_planning(2, entered_by="archive-author")

    assert repeated == first
    assert path.read_bytes() == original_bytes
    with pytest.raises(ValueError, match="already entered by archive-author"):
        service.enter_book_planning(2, entered_by="different-author")
    assert service.store.load_planning_entry(2) == first
    assert path.read_bytes() == original_bytes


def test_context_contains_only_explicitly_relevant_accepted_sources(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)
    unrelated, _unrelated_metadata = accept_unrelated_newer_outcome(service)
    service.enter_book_planning(2, entered_by="archive-author")

    context = service.derive_book_context(2)

    assert context == load_expected_book_2_context()
    assert [item.item_id for item in context.items] == [
        "series-commitment-contested-history",
        "state-change-founding-ledger-exposed",
    ]
    assert unrelated.artifact_id not in {
        ref.artifact_id
        for item in context.items
        for ref in item.source_refs
    }
    assert unrelated.artifact_id not in {
        ref.artifact_id for ref in context.generated_from
    }


def test_context_relevance_requires_exact_bundle_and_transition_source(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)
    unrelated, _unrelated_metadata = accept_unrelated_newer_outcome(
        service, transition_id="founding-ledger-exposed"
    )
    service.enter_book_planning(2, entered_by="archive-author")

    context = service.derive_book_context(2)

    assert context == load_expected_book_2_context()
    assert [item.item_id for item in context.items].count(
        "state-change-founding-ledger-exposed"
    ) == 1
    assert unrelated.artifact_id not in {
        ref.artifact_id
        for item in context.items
        for ref in item.source_refs
    }
    assert unrelated.artifact_id not in {
        ref.artifact_id for ref in context.generated_from
    }


def test_every_context_item_has_why_now_and_source_revisions(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)
    service.enter_book_planning(2, entered_by="archive-author")

    context = service.derive_book_context(2)

    assert all(item.why_matters_now.strip() for item in context.items)
    assert all(item.source_refs for item in context.items)
    for source_ref in {
        (ref.artifact_id, ref.revision)
        for item in context.items
        for ref in item.source_refs
    }:
        metadata = service.store.artifact_store.current(source_ref[0])
        assert metadata is not None
        assert metadata.lifecycle is Lifecycle.ACCEPTED
        assert metadata.revision == source_ref[1]


def test_context_rejects_current_metadata_without_revision_snapshot(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)
    service.enter_book_planning(2, entered_by="archive-author")
    sidecar = service.store.artifact_store.sidecar_path("series-direction")
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["revision"] = 999
    sidecar.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Book planning context source metadata"):
        service.derive_book_context(2)

    assert not service.store.book_planning_context_path(2).exists()


def test_deleted_context_rebuilds_semantically_equivalent_from_accepted_sources(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)
    service.enter_book_planning(2, entered_by="archive-author")
    original = service.derive_book_context(2)

    service.delete_derived_book_context(2)

    assert not service.store.book_planning_context_path(2).exists()
    rebuilt = service.derive_book_context(2)
    assert rebuilt.model_dump(mode="json") == original.model_dump(mode="json")
    assert [item.item_id for item in rebuilt.items] == [
        item.item_id for item in original.items
    ]
    assert [item.why_matters_now for item in rebuilt.items] == [
        item.why_matters_now for item in original.items
    ]
    assert [item.source_refs for item in rebuilt.items] == [
        item.source_refs for item in original.items
    ]


def test_rebuilding_context_does_not_change_authority_or_canonical_state(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_outcome(service)
    service.enter_book_planning(2, entered_by="archive-author")
    accepted_before = (
        service.load_accepted_series_direction(),
        service.load_series_direction_metadata(),
        service.load_accepted_book_direction(1),
        service.load_book_direction_metadata(1),
        service.store.load_accepted_realization_bundles(),
    )
    state_before = service.load_canonical_state()
    state_bytes_before = service.store.canonical_state_path.read_bytes()

    service.derive_book_context(2)
    service.delete_derived_book_context(2)
    service.derive_book_context(2)

    assert (
        service.load_accepted_series_direction(),
        service.load_series_direction_metadata(),
        service.load_accepted_book_direction(1),
        service.load_book_direction_metadata(1),
        service.store.load_accepted_realization_bundles(),
    ) == accepted_before
    assert service.load_accepted_book_direction(2) is None
    assert service.load_canonical_state() == state_before
    assert service.store.canonical_state_path.read_bytes() == state_bytes_before


def test_proposal_round_trips_without_becoming_accepted(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)

    proposal = service.propose_series_direction(load_direction())

    assert service.load_series_direction_proposal(proposal.proposal_id) == proposal
    assert service.load_accepted_series_direction() is None
    assert service.load_series_direction_metadata() is None
    assert (
        tmp_path
        / ".auteur"
        / "series"
        / "vertical-slice"
        / "proposals"
        / "series-direction"
        / f"{proposal.proposal_id}.yaml"
    ).is_file()
    assert not (tmp_path / ".auteur" / "series" / "vertical-slice" / "accepted").exists()
    assert not (
        tmp_path
        / ".auteur"
        / "series"
        / "vertical-slice"
        / "derived"
        / "canonical-state.yaml"
    ).exists()


def test_acceptance_round_trip_preserves_author_and_source_revision(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(load_direction())

    accepted = service.accept_series_direction(
        proposal.proposal_id,
        accepted_by="archive-author",
        rationale="This is the intended long-horizon promise.",
    )

    assert service.load_accepted_series_direction() == accepted
    assert accepted.proposal_id == proposal.proposal_id
    assert accepted.direction == proposal.direction
    assert service.load_series_direction_proposal(accepted.proposal_id).revision == 1

    metadata = service.load_series_direction_metadata()
    assert metadata is not None
    assert metadata.artifact_id == accepted.artifact_id
    assert metadata.lifecycle is Lifecycle.ACCEPTED
    assert metadata.accepted_by == "archive-author"
    assert metadata.rationale == "This is the intended long-horizon promise."
    assert metadata.revision == 1
    assert metadata.dependencies == []

    accepted_path = (
        tmp_path
        / ".auteur"
        / "series"
        / "vertical-slice"
        / "accepted"
        / "series-direction.yaml"
    )
    stored_payload = yaml.safe_load(accepted_path.read_text(encoding="utf-8"))
    assert stored_payload == accepted.model_dump(mode="json")
    assert {
        "accepted_by",
        "accepted_at",
        "revision",
        "content_hash",
        "dependencies",
        "freshness",
    }.isdisjoint(stored_payload)
    assert not accepted_path.with_suffix(".tmp").exists()
    assert not (accepted_path.parent / ".staging" / accepted_path.name).exists()


def test_unaccepted_outcome_does_not_change_canonical_state(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    state_before = service.load_canonical_state()

    candidate = service.propose_realization(load_realization_candidate())

    assert service.load_canonical_state() == state_before
    assert service.store.load_realization_candidate(candidate.candidate_id) == candidate
    assert service.store.load_accepted_realization_bundles() == []


def test_accepting_outcome_creates_bundle_and_state_transition(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())

    accepted = service.accept_realization(
        candidate.candidate_id,
        accepted_by="archive-author",
        rationale="The recovered ledger resolves the Book 1 archival dispute.",
    )

    state = service.load_canonical_state()
    assert accepted.candidate_id == candidate.candidate_id
    assert accepted.book_number == 1
    assert accepted.transitions == candidate.transitions
    assert state.values["archive.founding_record"] == "confirmed fraudulent"
    assert state.state_version == 1
    assert state.applied_bundle_ids == [accepted.bundle_id]
    stored = service.store.load_accepted_realization_bundles()
    assert [bundle for bundle, _metadata in stored] == [accepted]
    assert stored[0][1].accepted_by == "archive-author"
    assert stored[0][1].rationale == (
        "The recovered ledger resolves the Book 1 archival dispute."
    )


def test_reloading_rebuilds_same_state_from_accepted_bundles(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    service.accept_realization(candidate.candidate_id, accepted_by="archive-author")
    expected = service.load_canonical_state()

    service.store.canonical_state_path.unlink()
    reloaded = SeriesVerticalSliceService(tmp_path)
    rebuilt = reloaded.rebuild_canonical_state()

    assert rebuilt == expected
    assert reloaded.load_canonical_state() == expected


def test_state_rebuild_ignores_unaccepted_outcome_files(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    service.accept_realization(candidate.candidate_id, accepted_by="archive-author")
    expected = service.load_canonical_state()
    unrelated_transition = candidate.transitions[0].model_copy(
        update={
            "transition_id": "founding-ledger-hidden-again",
            "after": "suppressed",
        }
    )
    unaccepted = candidate.model_copy(
        update={
            "candidate_id": "unaccepted-suppression",
            "transitions": [unrelated_transition],
        }
    )
    service.propose_realization(unaccepted)

    rebuilt = service.rebuild_canonical_state()

    assert rebuilt == expected
    assert rebuilt.values["archive.founding_record"] == "confirmed fraudulent"


def test_accepted_outcome_preserves_source_revisions(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    book_metadata = accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    accepted = service.accept_realization(
        candidate.candidate_id, accepted_by="archive-author"
    )

    reloaded = SeriesVerticalSliceService(tmp_path)
    stored = reloaded.store.load_accepted_realization_bundles()

    assert len(stored) == 1
    bundle, metadata = stored[0]
    assert bundle == accepted
    assert len(metadata.dependencies) == 1
    dependency = metadata.dependencies[0]
    assert dependency.artifact_id == "book-1-direction"
    assert dependency.artifact_type == "book_direction"
    assert dependency.revision == book_metadata.revision
    assert dependency.full_content_hash == book_metadata.content_hash
    assert dependency.projected_hash == book_metadata.content_hash
    payload = yaml.safe_load(
        reloaded.store.accepted_realization_bundle_path(
            bundle.bundle_id
        ).read_text(encoding="utf-8")
    )
    assert "source_refs" not in payload


def test_deleting_derived_state_preserves_authority_and_rebuild_restores_it(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    accepted = service.accept_realization(
        candidate.candidate_id, accepted_by="archive-author"
    )
    expected_state = service.load_canonical_state()
    bundle_path = service.store.accepted_realization_bundle_path(
        accepted.bundle_id
    )
    bundle_bytes = bundle_path.read_bytes()
    stored = service.store.load_accepted_realization_bundles()
    metadata = stored[0][1]
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    sidecar_bytes = sidecar.read_bytes()
    revisions = service.store.artifact_store.list_revisions(metadata.artifact_id)

    service.store.canonical_state_path.unlink()

    assert bundle_path.read_bytes() == bundle_bytes
    assert sidecar.read_bytes() == sidecar_bytes
    assert service.store.artifact_store.list_revisions(metadata.artifact_id) == revisions
    assert service.rebuild_canonical_state() == expected_state
    assert service.load_canonical_state() == expected_state


def test_failed_realization_metadata_accept_leaves_no_partial_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    original_accept = service.store.artifact_store.accept

    def fail_accept(*args: object, **kwargs: object) -> None:
        original_accept(*args, **kwargs)
        raise OSError("realization metadata persistence failed")

    monkeypatch.setattr(service.store.artifact_store, "accept", fail_accept)

    with pytest.raises(OSError, match="realization metadata persistence failed"):
        service.accept_realization(candidate.candidate_id, accepted_by="author")

    assert service.store.load_accepted_realization_bundles() == []
    artifact_id = f"realization-bundle-{candidate.candidate_id}"
    assert service.store.artifact_store.current(artifact_id) is None
    assert service.store.artifact_store.list_revisions(artifact_id) == []
    assert service.load_canonical_state() == vertical_slice_models.CanonicalState(
        state_version=0
    )


def test_failed_canonical_state_write_rolls_back_accepted_realization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    original_save = service.store.save_canonical_state

    def fail_save(state: object) -> None:
        original_save(state)
        raise OSError("canonical state persistence failed")

    monkeypatch.setattr(service.store, "save_canonical_state", fail_save)

    with pytest.raises(OSError, match="canonical state persistence failed"):
        service.accept_realization(candidate.candidate_id, accepted_by="author")

    assert service.store.load_realization_candidate(candidate.candidate_id) == candidate
    assert service.store.load_accepted_realization_bundles() == []
    artifact_id = f"realization-bundle-{candidate.candidate_id}"
    assert service.store.artifact_store.current(artifact_id) is None
    assert service.store.artifact_store.list_revisions(artifact_id) == []
    assert service.load_canonical_state() == vertical_slice_models.CanonicalState(
        state_version=0
    )


def test_realization_candidate_id_must_be_path_safe(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = load_realization_candidate().model_copy(
        update={"candidate_id": "../outside"}
    )

    with pytest.raises(ValueError, match="path-safe"):
        service.propose_realization(candidate)


def test_realization_acceptance_validates_book_dependency_revision(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    revision_path = (
        service.store.artifact_store.root
        / "revisions"
        / "book-1-direction"
        / "000001.yaml"
    )
    payload = yaml.safe_load(revision_path.read_text(encoding="utf-8"))
    payload["content_hash"] = "sha256:mismatched"
    revision_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Book Direction dependency revision"):
        service.accept_realization(candidate.candidate_id, accepted_by="author")

    assert service.store.load_accepted_realization_bundles() == []
    artifact_id = f"realization-bundle-{candidate.candidate_id}"
    assert service.store.artifact_store.current(artifact_id) is None


def test_accepted_realization_requires_matching_current_metadata(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    service.accept_realization(candidate.candidate_id, accepted_by="author")
    metadata = service.store.load_accepted_realization_bundles()[0][1]
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["content_hash"] = "sha256:altered"
    sidecar.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="metadata history"):
        service.rebuild_canonical_state()


def test_rebuild_rejects_missing_realization_revision_and_preserves_state(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    service.accept_realization(candidate.candidate_id, accepted_by="author")
    expected_state = service.load_canonical_state()
    state_bytes = service.store.canonical_state_path.read_bytes()
    bundle, metadata = service.store.load_accepted_realization_bundles()[0]
    revision_path = (
        service.store.artifact_store.root
        / "revisions"
        / metadata.artifact_id
        / f"{metadata.revision:06d}.yaml"
    )
    revision_path.unlink()

    with pytest.raises(ValueError, match="metadata history"):
        service.rebuild_canonical_state()

    assert service.store.accepted_realization_bundle_path(
        bundle.bundle_id
    ).is_file()
    assert service.store.canonical_state_path.read_bytes() == state_bytes
    assert service.load_canonical_state() == expected_state


def test_second_acceptance_rejects_gapped_realization_metadata_history(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    first = service.propose_realization(load_realization_candidate())
    service.accept_realization(first.candidate_id, accepted_by="author")
    second_transition = first.transitions[0].model_copy(
        update={
            "transition_id": "public-record-corrected",
            "subject": "archive",
            "attribute": "public_record",
            "before": None,
            "after": "corrected",
        }
    )
    second = first.model_copy(
        update={
            "candidate_id": "public-record-correction",
            "transitions": [second_transition],
        }
    )
    service.propose_realization(second)
    payload_paths_before = set(
        (service.store.root / "accepted" / "realization").glob("*.yaml")
    )
    metadata_paths_before = set(
        service.store.artifact_store.root.glob("*.yaml")
    )
    revision_paths_before = set(
        (service.store.artifact_store.root / "revisions").rglob("*.yaml")
    )
    first_metadata = service.store.load_accepted_realization_bundles()[0][1]
    sidecar = service.store.artifact_store.sidecar_path(
        first_metadata.artifact_id
    )
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["revision"] = 3
    sidecar.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="metadata history"):
        service.accept_realization(second.candidate_id, accepted_by="author")

    assert set(
        (service.store.root / "accepted" / "realization").glob("*.yaml")
    ) == payload_paths_before
    assert set(service.store.artifact_store.root.glob("*.yaml")) == (
        metadata_paths_before
    )
    assert set(
        (service.store.artifact_store.root / "revisions").rglob("*.yaml")
    ) == revision_paths_before


def test_realization_metadata_tracks_bundle_path_and_book_freshness(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    book_metadata = accept_archive_book(service)
    candidate = service.propose_realization(load_realization_candidate())
    accepted = service.accept_realization(
        candidate.candidate_id, accepted_by="author"
    )
    bundle, metadata = service.store.load_accepted_realization_bundles()[0]
    bundle_path = service.store.accepted_realization_bundle_path(
        bundle.bundle_id
    )

    assert accepted == bundle
    assert bundle.artifact_id == bundle.bundle_id == bundle_path.stem
    assert metadata.artifact_id == bundle.artifact_id
    assert metadata.revision == 1
    assert metadata.dependencies[0].artifact_id == "book-1-direction"
    assert metadata.dependencies[0].revision == book_metadata.revision
    status = service.store.artifact_store.status(
        bundle_path, "accepted_realization_bundle"
    )
    assert status.lifecycle is Lifecycle.ACCEPTED
    assert status.health == "valid"
    assert status.freshness == "fresh"

    replacement_identity = load_book_direction().identity.model_copy(
        update={"title": "The Public Ledger"}
    )
    replacement = load_book_direction().model_copy(
        update={"identity": replacement_identity}
    )
    proposal = service.propose_book_direction(replacement)
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")

    stale_status = service.store.artifact_store.status(
        bundle_path, "accepted_realization_bundle"
    )
    assert stale_status.lifecycle is Lifecycle.ACCEPTED
    assert stale_status.health == "valid"
    assert stale_status.freshness == "stale"
    assert stale_status.stale_reasons[0].dependency_id == "book-1-direction"
    assert stale_status.stale_reasons[0].previous_revision == 1
    assert stale_status.stale_reasons[0].current_revision == 2


def test_repeated_state_transition_requires_matching_before_value(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    first = service.propose_realization(load_realization_candidate())
    service.accept_realization(first.candidate_id, accepted_by="author")
    expected_state = service.load_canonical_state()
    payload_paths_before = set(
        (service.store.root / "accepted" / "realization").glob("*.yaml")
    )
    metadata_paths_before = set(
        service.store.artifact_store.root.glob("realization-bundle-*.yaml")
    )
    impossible_transition = first.transitions[0].model_copy(
        update={
            "transition_id": "founding-ledger-publicly-corrected",
            "before": "still secret",
            "after": "publicly corrected",
        }
    )
    impossible = first.model_copy(
        update={
            "candidate_id": "impossible-public-correction",
            "transitions": [impossible_transition],
        }
    )
    service.propose_realization(impossible)

    with pytest.raises(ValueError, match="before value"):
        service.accept_realization(
            impossible.candidate_id, accepted_by="author"
        )

    assert service.load_canonical_state() == expected_state
    assert set(
        (service.store.root / "accepted" / "realization").glob("*.yaml")
    ) == payload_paths_before
    assert set(
        service.store.artifact_store.root.glob("realization-bundle-*.yaml")
    ) == metadata_paths_before


@pytest.mark.parametrize(
    ("field", "value"),
    [("book_number", 0), ("transitions", [])],
)
def test_accepted_realization_bundle_enforces_bounded_content(
    field: str,
    value: object,
) -> None:
    candidate = load_realization_candidate()
    raw = {
        "artifact_id": "realization-bundle-bounded",
        "bundle_id": "realization-bundle-bounded",
        "candidate_id": candidate.candidate_id,
        "book_number": candidate.book_number,
        "transitions": [
            transition.model_dump(mode="json")
            for transition in candidate.transitions
        ],
    }
    raw[field] = value

    with pytest.raises(ValidationError, match=field):
        vertical_slice_models.AcceptedRealizationBundle.model_validate(raw)


def test_duplicate_transition_ids_are_rejected_before_realization_acceptance(
    tmp_path: Path,
) -> None:
    candidate = load_realization_candidate()
    duplicate = candidate.transitions[0].model_copy(
        update={"subject": "duplicate-source"}
    )
    candidate_payload = candidate.model_dump(mode="json")
    candidate_payload["transitions"].append(duplicate.model_dump(mode="json"))

    with pytest.raises(ValidationError, match="transition_id values must be unique"):
        vertical_slice_models.RealizationCandidate.model_validate(
            candidate_payload
        )

    bundle_payload = {
        "artifact_id": "realization-bundle-duplicate-transitions",
        "bundle_id": "realization-bundle-duplicate-transitions",
        "candidate_id": candidate.candidate_id,
        "book_number": candidate.book_number,
        "transitions": candidate_payload["transitions"],
    }
    with pytest.raises(ValidationError, match="transition_id values must be unique"):
        vertical_slice_models.AcceptedRealizationBundle.model_validate(
            bundle_payload
        )

    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_book(service)
    service.propose_realization(candidate)
    candidate_path = service.store.realization_candidate_path(
        candidate.candidate_id
    )
    candidate_path.write_text(
        yaml.safe_dump(candidate_payload, sort_keys=False), encoding="utf-8"
    )
    state_before = service.load_canonical_state()

    with pytest.raises(ValidationError, match="transition_id values must be unique"):
        service.accept_realization(candidate.candidate_id, accepted_by="author")

    bundle_id = f"realization-bundle-{candidate.candidate_id}"
    assert not service.store.accepted_realization_bundle_path(bundle_id).exists()
    assert service.store.artifact_store.current(bundle_id) is None
    assert service.load_canonical_state() == state_before


def test_accepting_unknown_series_direction_proposal_is_rejected(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)

    with pytest.raises(FileNotFoundError, match="Unknown Series Direction proposal"):
        service.accept_series_direction("missing-proposal", accepted_by="author")

    assert service.load_accepted_series_direction() is None
    assert service.load_series_direction_metadata() is None


def test_new_proposal_does_not_modify_accepted_series_direction(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    first = service.propose_series_direction(load_direction())
    service.accept_series_direction(first.proposal_id, accepted_by="author")
    accepted_before = service.load_accepted_series_direction()
    metadata_before = service.load_series_direction_metadata()

    alternative = load_direction().model_copy(
        update={"open_question": "Will preserving every truth destroy the people it names?"}
    )
    service.propose_series_direction(alternative)

    assert service.load_accepted_series_direction() == accepted_before
    assert service.load_series_direction_metadata() == metadata_before


def test_accepted_series_direction_requires_metadata_sidecar(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(load_direction())
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_series_direction_metadata()
    assert metadata is not None

    service.store.artifact_store.sidecar_path(metadata.artifact_id).unlink()

    assert service.load_accepted_series_direction() is None


def test_accepted_series_direction_rejects_modified_payload(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(load_direction())
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    accepted_path = service.store.accepted_series_direction_path
    payload = yaml.safe_load(accepted_path.read_text(encoding="utf-8"))
    payload["direction"]["promise"] = "Tampered after acceptance."
    accepted_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    assert service.load_accepted_series_direction() is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_id", "other-artifact"),
        ("artifact_type", "blueprint"),
        ("lifecycle", "draft"),
    ],
)
def test_accepted_series_direction_requires_matching_accepted_metadata(
    tmp_path: Path,
    field: str,
    value: str,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(load_direction())
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_series_direction_metadata()
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload[field] = value
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_series_direction() is None


def test_failed_metadata_accept_preserves_previous_series_direction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal_a = service.propose_series_direction(load_direction())
    accepted_a = service.accept_series_direction(
        proposal_a.proposal_id, accepted_by="author"
    )
    metadata_a = service.load_series_direction_metadata()
    assert metadata_a is not None
    revisions_a = service.store.artifact_store.list_revisions(metadata_a.artifact_id)

    direction_b = load_direction().model_copy(
        update={"promise": "A replacement direction that must not be accepted."}
    )
    proposal_b = service.propose_series_direction(direction_b)
    original_accept = service.store.artifact_store.accept

    def fail_accept(*args: object, **kwargs: object) -> None:
        original_accept(*args, **kwargs)
        raise OSError("metadata persistence failed")

    monkeypatch.setattr(service.store.artifact_store, "accept", fail_accept)

    with pytest.raises(OSError, match="metadata persistence failed"):
        service.accept_series_direction(proposal_b.proposal_id, accepted_by="author")

    accepted_path = service.store.accepted_series_direction_path
    assert service.load_accepted_series_direction() == accepted_a
    assert service.load_series_direction_metadata() == metadata_a
    assert service.store.artifact_store.list_revisions(metadata_a.artifact_id) == revisions_a
    assert service.store.artifact_store.content_hash(accepted_path) == metadata_a.content_hash
    assert not (accepted_path.parent / ".staging" / "series-direction.yaml").exists()


@pytest.mark.parametrize(
    ("field", "value"),
    [("book_number", 0), ("series_commitment_ids", [])],
)
def test_book_direction_enforces_local_typed_boundary(
    field: str,
    value: object,
) -> None:
    raw = yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    raw[field] = value

    with pytest.raises(ValidationError, match=field):
        BookDirection.model_validate(raw)


def test_book_direction_rejects_undeclared_fields() -> None:
    raw = yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    raw["book_plans"] = []

    with pytest.raises(ValidationError, match="book_plans"):
        BookDirection.model_validate(raw)


def test_book_direction_requires_accepted_series_direction(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)

    with pytest.raises(ValueError, match="accepted Series Direction"):
        service.propose_book_direction(load_book_direction())

    assert service.load_accepted_book_direction(1) is None
    assert not (
        tmp_path
        / ".auteur"
        / "series"
        / "vertical-slice"
        / "proposals"
        / "book-direction"
    ).exists()


def test_accepting_book_direction_does_not_mutate_series_direction(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    series_before = service.load_accepted_series_direction()
    metadata_before = service.load_series_direction_metadata()
    series_path = service.store.accepted_series_direction_path
    series_bytes_before = series_path.read_bytes()

    proposal = service.propose_book_direction(load_book_direction())
    accepted = service.accept_book_direction(
        proposal.proposal_id,
        accepted_by="archive-author",
        rationale="This Book exposes the first consequential archival lie.",
    )

    assert service.load_accepted_book_direction(1) == accepted
    assert service.load_accepted_series_direction() == series_before
    assert service.load_series_direction_metadata() == metadata_before
    assert series_path.read_bytes() == series_bytes_before

    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    assert metadata.artifact_id == "book-1-direction"
    assert metadata.artifact_type == "book_direction"
    assert metadata.lifecycle is Lifecycle.ACCEPTED
    assert metadata.accepted_by == "archive-author"
    assert metadata.rationale == "This Book exposes the first consequential archival lie."
    assert len(metadata.dependencies) == 1
    dependency = metadata.dependencies[0]
    assert dependency.artifact_id == "series-direction"
    assert dependency.artifact_type == "series_direction"
    assert dependency.kind is DependencyKind.SEMANTIC
    assert dependency.source is DependencySource.DECLARED
    assert dependency.revision == metadata_before.revision
    assert dependency.fields == []
    assert dependency.projection.id == "full"
    assert Path(dependency.path) == Path(
        ".auteur/series/vertical-slice/accepted/series-direction.yaml"
    )

    accepted_path = service.store.accepted_book_direction_path(1)
    stored_payload = yaml.safe_load(accepted_path.read_text(encoding="utf-8"))
    assert stored_payload == accepted.model_dump(mode="json")
    assert {
        "accepted_by",
        "accepted_at",
        "revision",
        "content_hash",
        "dependencies",
        "freshness",
    }.isdisjoint(stored_payload)


def test_unaccepted_book_direction_has_no_authority(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accepted_series, series_metadata = accept_archive_series(service)

    proposal = service.propose_book_direction(load_book_direction())

    assert service.load_book_direction_proposal(proposal.proposal_id) == proposal
    assert proposal.source_refs == [
        ArtifactRef(
            artifact_id=accepted_series.artifact_id,
            revision=series_metadata.revision,
        )
    ]
    assert service.load_accepted_book_direction(1) is None
    assert service.load_book_direction_metadata(1) is None
    assert service.store.book_direction_proposal_path(
        1, proposal.proposal_id
    ).is_file()
    assert not service.store.accepted_book_direction_path(1).exists()


def test_book_direction_reload_preserves_book_number_commitment_refs_and_source(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accepted_series, series_metadata = accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    accepted = service.accept_book_direction(
        proposal.proposal_id, accepted_by="archive-author"
    )

    reloaded = SeriesVerticalSliceService(tmp_path)
    reloaded_proposal = reloaded.load_book_direction_proposal(proposal.proposal_id)
    reloaded_accepted = reloaded.load_accepted_book_direction(1)
    reloaded_metadata = reloaded.load_book_direction_metadata(1)

    assert reloaded_accepted == accepted
    assert reloaded_accepted.direction.book_number == 1
    assert reloaded_accepted.direction.series_commitment_ids == [
        "contested-history"
    ]
    assert reloaded_proposal.source_refs == [
        ArtifactRef(
            artifact_id=accepted_series.artifact_id,
            revision=series_metadata.revision,
        )
    ]
    assert reloaded_metadata is not None
    assert [dependency.revision for dependency in reloaded_metadata.dependencies] == [
        series_metadata.revision
    ]


def test_book_direction_rejects_unknown_series_commitment(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    invalid = load_book_direction().model_copy(
        update={"series_commitment_ids": ["invented-commitment"]}
    )

    with pytest.raises(ValueError, match="invented-commitment"):
        service.propose_book_direction(invalid)

    assert not (
        service.store.root / "proposals" / "book-direction"
    ).exists()


def test_accepting_unknown_book_direction_proposal_is_rejected(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)

    with pytest.raises(FileNotFoundError, match="Unknown Book Direction proposal"):
        service.accept_book_direction("missing-proposal", accepted_by="author")

    assert service.load_accepted_book_direction(1) is None
    assert service.load_book_direction_metadata(1) is None


def test_accepted_book_direction_rejects_modified_payload(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    accepted_path = service.store.accepted_book_direction_path(1)
    payload = yaml.safe_load(accepted_path.read_text(encoding="utf-8"))
    payload["direction"]["identity"]["title"] = "Tampered after acceptance"
    accepted_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    assert service.load_accepted_book_direction(1) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_id", "other-artifact"),
        ("artifact_type", "blueprint"),
        ("lifecycle", "draft"),
        ("dependencies", []),
    ],
)
def test_accepted_book_direction_requires_matching_accepted_metadata(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload[field] = value
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_book_direction(1) is None


def test_accepted_book_direction_rejects_invented_dependency_revision(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["dependencies"][0]["revision"] = 999
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_book_direction(1) is None


def test_accepted_book_direction_rejects_altered_projected_hash(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["dependencies"][0]["projected_hash"] = "sha256:altered"
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_book_direction(1) is None


def test_accepted_book_direction_rejects_altered_full_content_hash(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["dependencies"][0]["full_content_hash"] = "sha256:altered"
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_book_direction(1) is None


def test_book_acceptance_requires_valid_current_series_authority(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    series_sidecar = service.store.artifact_store.sidecar_path("series-direction")
    payload = yaml.safe_load(series_sidecar.read_text(encoding="utf-8"))
    payload["lifecycle"] = "draft"
    series_sidecar.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="accepted Series Direction"):
        service.accept_book_direction(proposal.proposal_id, accepted_by="author")

    assert not service.store.accepted_book_direction_path(1).exists()
    assert service.load_book_direction_metadata(1) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_id", "other-artifact"),
        ("artifact_type", "blueprint"),
        ("lifecycle", "draft"),
        ("content_hash", "sha256:altered"),
    ],
)
def test_accepted_book_direction_requires_valid_series_dependency_revision(
    tmp_path: Path,
    field: str,
    value: str,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    revision_path = (
        service.store.artifact_store.root
        / "revisions"
        / "series-direction"
        / "000001.yaml"
    )
    payload = yaml.safe_load(revision_path.read_text(encoding="utf-8"))
    payload[field] = value
    revision_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    assert service.load_accepted_book_direction(1) is None


@pytest.mark.parametrize(
    "tamper",
    ["missing", "invalid_lifecycle", "mismatched_hash"],
)
def test_book_acceptance_validates_series_revision_before_writing(
    tmp_path: Path,
    tamper: str,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    revision_path = (
        service.store.artifact_store.root
        / "revisions"
        / "series-direction"
        / "000001.yaml"
    )
    if tamper == "missing":
        revision_path.unlink()
    else:
        payload = yaml.safe_load(revision_path.read_text(encoding="utf-8"))
        if tamper == "invalid_lifecycle":
            payload["lifecycle"] = "draft"
        else:
            payload["content_hash"] = "sha256:mismatched"
        revision_path.write_text(
            yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
        )

    with pytest.raises(ValueError, match="Series Direction dependency revision"):
        service.accept_book_direction(proposal.proposal_id, accepted_by="author")

    accepted_path = service.store.accepted_book_direction_path(1)
    assert not accepted_path.exists()
    assert service.load_book_direction_metadata(1) is None
    assert service.store.artifact_store.list_revisions("book-1-direction") == []
    assert not (accepted_path.parent / ".staging" / accepted_path.name).exists()


def test_accepted_book_direction_remains_loadable_when_series_becomes_stale(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    book_proposal = service.propose_book_direction(load_book_direction())
    accepted_book = service.accept_book_direction(
        book_proposal.proposal_id, accepted_by="author"
    )
    book_metadata = service.load_book_direction_metadata(1)
    assert book_metadata is not None
    assert book_metadata.dependencies[0].revision == 1

    revised_series = load_direction().model_copy(
        update={"promise": "Every recovered account changes who controls history."}
    )
    series_proposal = service.propose_series_direction(revised_series)
    service.accept_series_direction(series_proposal.proposal_id, accepted_by="author")

    assert service.load_accepted_book_direction(1) == accepted_book
    preserved_metadata = service.load_book_direction_metadata(1)
    assert preserved_metadata is not None
    assert preserved_metadata.dependencies[0].revision == 1
    status = service.store.artifact_store.status(
        service.store.accepted_book_direction_path(1), "book_direction"
    )
    assert status.lifecycle is Lifecycle.ACCEPTED
    assert status.freshness == "stale"
    assert status.stale_reasons[0].previous_revision == 1
    assert status.stale_reasons[0].current_revision == 2


def test_failed_book_metadata_accept_preserves_previous_book_direction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal_a = service.propose_book_direction(load_book_direction())
    accepted_a = service.accept_book_direction(
        proposal_a.proposal_id, accepted_by="author"
    )
    metadata_a = service.load_book_direction_metadata(1)
    assert metadata_a is not None
    accepted_path = service.store.accepted_book_direction_path(1)
    accepted_bytes_a = accepted_path.read_bytes()
    revisions_a = service.store.artifact_store.list_revisions(
        metadata_a.artifact_id
    )

    replacement_identity = load_book_direction().identity.model_copy(
        update={"title": "The Counterfeit Ledger"}
    )
    replacement = load_book_direction().model_copy(
        update={"identity": replacement_identity}
    )
    proposal_b = service.propose_book_direction(replacement)
    original_accept = service.store.artifact_store.accept

    def fail_accept(*args: object, **kwargs: object) -> None:
        original_accept(*args, **kwargs)
        raise OSError("book metadata persistence failed")

    monkeypatch.setattr(service.store.artifact_store, "accept", fail_accept)

    with pytest.raises(OSError, match="book metadata persistence failed"):
        service.accept_book_direction(proposal_b.proposal_id, accepted_by="author")

    assert service.load_accepted_book_direction(1) == accepted_a
    assert service.load_book_direction_metadata(1) == metadata_a
    assert accepted_path.read_bytes() == accepted_bytes_a
    assert service.store.artifact_store.list_revisions(metadata_a.artifact_id) == (
        revisions_a
    )
    assert not (accepted_path.parent / ".staging" / accepted_path.name).exists()
