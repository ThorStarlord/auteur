from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.cli import main
from auteur.series.vertical_slice_models import (
    BookDirection,
    RealizationCandidate,
    SeriesDirection,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


FIXTURE_ROOT = (
    Path(__file__).parent / "fixtures" / "archive_of_lies_vertical_slice"
)
SERIES_INPUT = FIXTURE_ROOT / "series_direction.yaml"
BOOK_INPUT = FIXTURE_ROOT / "book_1_direction.yaml"
OUTCOME_INPUT = FIXTURE_ROOT / "book_1_outcome.yaml"


def _load_model(path: Path, model_type):
    return model_type.model_validate(
        yaml.safe_load(path.read_text(encoding="utf-8"))
    )


def _prepare_book_2(project: Path) -> SeriesVerticalSliceService:
    service, candidate = _prepare_outcome_candidate(project)
    service.accept_realization(
        candidate.candidate_id, accepted_by="archive-author"
    )
    service.enter_book_planning(2, entered_by="archive-author")
    return service


def _prepare_outcome_candidate(
    project: Path,
) -> tuple[SeriesVerticalSliceService, RealizationCandidate]:
    service = SeriesVerticalSliceService(project)
    series_proposal = service.propose_series_direction(
        _load_model(SERIES_INPUT, SeriesDirection)
    )
    service.accept_series_direction(
        series_proposal.proposal_id, accepted_by="archive-author"
    )
    book_proposal = service.propose_book_direction(
        _load_model(BOOK_INPUT, BookDirection)
    )
    service.accept_book_direction(
        book_proposal.proposal_id, accepted_by="archive-author"
    )
    candidate = service.propose_realization(
        _load_model(OUTCOME_INPUT, RealizationCandidate)
    )
    return service, candidate


def _proposal_id(output: str) -> str:
    line = next(
        line for line in output.splitlines() if line.startswith("Proposal ID: ")
    )
    return line.removeprefix("Proposal ID: ")


def test_map_shows_established_context_and_next_available_decision(
    tmp_path: Path,
    capsys,
) -> None:
    _prepare_book_2(tmp_path)

    assert (
        main(
            [
                "series",
                "journey",
                "map",
                str(tmp_path),
                "--book",
                "2",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "Established context" in output
    assert "Every Book must expose a consequential conflict" in output
    assert "Why it matters now" in output
    assert "exposed founding fraud" in output
    assert "Next available decision" in output
    assert "How should Book 2 turn the exposed founding fraud" in output


def test_focus_shows_recommendation_rationale_tradeoff_and_choices(
    tmp_path: Path,
    capsys,
) -> None:
    _prepare_book_2(tmp_path)

    assert (
        main(
            [
                "series",
                "journey",
                "focus",
                str(tmp_path),
                "--book",
                "2",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "Recommendation" in output
    assert "Center a living witness" in output
    assert "Why this is preferred" in output
    assert "accepted Series commitment" in output
    assert "Principal tradeoff" in output
    assert "testimony and personal credibility central" in output
    assert "Choose recommended" in output
    assert "Choose another option" in output
    assert "Defer" in output


def test_default_surface_hides_revision_ids_but_deep_output_can_show_sources(
    tmp_path: Path,
    capsys,
) -> None:
    _prepare_book_2(tmp_path)

    base_command = [
        "series",
        "journey",
        "map",
        str(tmp_path),
        "--book",
        "2",
    ]
    assert main(base_command) == 0
    default_output = capsys.readouterr().out

    assert "series-direction" not in default_output
    assert "revision 1" not in default_output
    assert "Proposal ID:" not in default_output

    assert main([*base_command, "--detail"]) == 0
    detail_output = capsys.readouterr().out

    assert "series-direction (revision 1)" in detail_output
    assert "book-1-direction (revision 1)" in detail_output
    assert "Proposal ID:" in detail_output


def test_detail_map_keeps_each_item_adjacent_to_its_source_refs(
    tmp_path: Path,
    capsys,
) -> None:
    _prepare_book_2(tmp_path)

    assert (
        main(
            [
                "series",
                "journey",
                "map",
                str(tmp_path),
                "--book",
                "2",
                "--detail",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out

    commitment_start = output.index(
        "Every Book must expose a consequential conflict"
    )
    state_change_start = output.index(
        "archive.founding_record changed to confirmed fraudulent"
    )
    decision_start = output.index("Next available decision")
    commitment_block = output[commitment_start:state_change_start]
    state_change_block = output[state_change_start:decision_start]

    assert "Source references:" in commitment_block
    assert "series-direction (revision 1)" in commitment_block
    assert "book-1-direction (revision 1)" in commitment_block
    assert "realization-bundle" not in commitment_block
    assert "Source references:" in state_change_block
    assert (
        "realization-bundle-recovered-founding-ledger (revision 1)"
        in state_change_block
    )
    assert "series-direction" not in state_change_block


@pytest.mark.parametrize("command", ["map", "focus"])
def test_detail_help_explains_progressive_source_disclosure(
    command: str,
    capsys,
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["series", "journey", command, "--help"])

    assert exc_info.value.code == 0
    assert "Show artifact and revision IDs hidden by default." in (
        capsys.readouterr().out
    )


def test_choice_help_explains_bounded_values(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["series", "journey", "decide", "--help"])

    assert exc_info.value.code == 0
    assert "recommended|<presented-option-id>|defer" in (
        capsys.readouterr().out
    )


def test_cli_proposal_commands_do_not_accept_on_generation(
    tmp_path: Path,
    capsys,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)

    assert (
        main(
            [
                "series",
                "journey",
                "propose-series",
                str(tmp_path),
                "--input",
                str(SERIES_INPUT),
            ]
        )
        == 0
    )
    series_proposal_id = _proposal_id(capsys.readouterr().out)
    assert service.load_accepted_series_direction() is None

    assert (
        main(
            [
                "series",
                "journey",
                "accept-series",
                str(tmp_path),
                series_proposal_id,
            ]
        )
        == 0
    )
    capsys.readouterr()

    assert (
        main(
            [
                "series",
                "journey",
                "propose-book",
                str(tmp_path),
                "--input",
                str(BOOK_INPUT),
            ]
        )
        == 0
    )
    book_proposal_id = _proposal_id(capsys.readouterr().out)
    assert service.load_accepted_book_direction(1) is None

    assert (
        main(
            [
                "series",
                "journey",
                "accept-book",
                str(tmp_path),
                book_proposal_id,
            ]
        )
        == 0
    )
    capsys.readouterr()
    state_before = service.load_canonical_state()

    assert (
        main(
            [
                "series",
                "journey",
                "propose-outcome",
                str(tmp_path),
                "--input",
                str(OUTCOME_INPUT),
            ]
        )
        == 0
    )
    capsys.readouterr()

    assert service.store.load_accepted_realization_bundles() == []
    assert service.load_canonical_state() == state_before


def test_accept_outcome_and_plan_next_book_dispatch(
    tmp_path: Path,
    capsys,
) -> None:
    service, candidate = _prepare_outcome_candidate(tmp_path)

    assert (
        main(
            [
                "series",
                "journey",
                "accept-outcome",
                str(tmp_path),
                candidate.candidate_id,
            ]
        )
        == 0
    )
    assert "Accepted Book 1 outcome." in capsys.readouterr().out
    assert service.load_canonical_state().values[
        "archive.founding_record"
    ] == "confirmed fraudulent"

    assert (
        main(
            [
                "series",
                "journey",
                "plan-next-book",
                str(tmp_path),
                "--book",
                "2",
            ]
        )
        == 0
    )
    assert "Entered exploratory planning for Book 2." in capsys.readouterr().out
    entry = service.store.load_planning_entry(2)
    assert entry is not None
    assert entry.entered_by == "author"


@pytest.mark.parametrize(
    ("choice", "expected_action", "expected_option_id"),
    [
        (
            "trace-institutional-cover-up",
            "choose_other",
            "trace-institutional-cover-up",
        ),
        ("defer", "defer", None),
    ],
)
def test_decide_dispatches_choose_other_and_defer(
    tmp_path: Path,
    capsys,
    choice: str,
    expected_action: str,
    expected_option_id: str | None,
) -> None:
    service = _prepare_book_2(tmp_path)
    proposal = service.propose_next_decision(2)
    state_before = service.load_canonical_state()

    assert (
        main(
            [
                "series",
                "journey",
                "decide",
                str(tmp_path),
                proposal.proposal_id,
                "--choice",
                choice,
            ]
        )
        == 0
    )
    assert f"Recorded decision action: {expected_action}" in (
        capsys.readouterr().out
    )
    actions = service.store.load_decision_actions(proposal.proposal_id)
    assert len(actions) == 1
    assert actions[0].action == expected_action
    assert actions[0].selected_option_id == expected_option_id
    assert service.load_accepted_book_direction(2) is None
    assert service.load_canonical_state() == state_before


def test_missing_journey_input_returns_nonzero(
    tmp_path: Path,
    capsys,
) -> None:
    missing_input = tmp_path / "missing-series-direction.yaml"

    assert (
        main(
            [
                "series",
                "journey",
                "propose-series",
                str(tmp_path),
                "--input",
                str(missing_input),
            ]
        )
        == 1
    )
    assert "Error:" in capsys.readouterr().out
    assert SeriesVerticalSliceService(
        tmp_path
    ).load_accepted_series_direction() is None


def test_decide_records_only_the_workflow_action(
    tmp_path: Path,
    capsys,
) -> None:
    service = _prepare_book_2(tmp_path)
    accepted_before = (
        service.load_accepted_series_direction(),
        service.load_accepted_book_direction(1),
        service.load_accepted_book_direction(2),
        service.load_canonical_state(),
    )

    assert (
        main(
            [
                "series",
                "journey",
                "focus",
                str(tmp_path),
                "--book",
                "2",
                "--detail",
            ]
        )
        == 0
    )
    proposal_id = _proposal_id(capsys.readouterr().out)

    assert (
        main(
            [
                "series",
                "journey",
                "decide",
                str(tmp_path),
                proposal_id,
                "--choice",
                "recommended",
            ]
        )
        == 0
    )

    actions = service.store.load_decision_actions(proposal_id)
    assert len(actions) == 1
    assert actions[0].action == "choose_recommended"
    assert (
        service.load_accepted_series_direction(),
        service.load_accepted_book_direction(1),
        service.load_accepted_book_direction(2),
        service.load_canonical_state(),
    ) == accepted_before
