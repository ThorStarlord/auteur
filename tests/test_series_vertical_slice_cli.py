from __future__ import annotations

from pathlib import Path

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
    service.accept_realization(
        candidate.candidate_id, accepted_by="archive-author"
    )
    service.enter_book_planning(2, entered_by="archive-author")
    return service


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
