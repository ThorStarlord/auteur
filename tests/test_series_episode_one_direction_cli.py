"""CLI and inspection tests for bounded Episode 1 Direction.

Covers acceptance invariants 12-13 of the ratified capability contract: the
inspection view distinguishes Series-level and Episode-level content, lists
the referenced commitments, never labels the Episode as Book, and reports a
clean absence; an existing Book-oriented project is untouched.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from auteur.cli import main
from auteur.series.episode_one_direction import EpisodeDirection
from auteur.series.vertical_slice_models import SeriesDirection
from auteur.series.vertical_slice_service import SeriesVerticalSliceService

FIXTURES = Path(__file__).parent / "fixtures" / "archive_of_lies_vertical_slice"
SERIES_INPUT = FIXTURES / "series_direction.yaml"
EPISODE_INPUT = FIXTURES / "episode_1_direction.yaml"


def accept_series(project: Path) -> SeriesVerticalSliceService:
    service = SeriesVerticalSliceService(project)
    series = SeriesDirection.model_validate(
        yaml.safe_load(SERIES_INPUT.read_text(encoding="utf-8"))
    )
    proposal = service.propose_series_direction(series)
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    return service


def _proposal_id(output: str) -> str:
    line = next(
        line for line in output.splitlines() if line.startswith("Proposal ID: ")
    )
    return line.removeprefix("Proposal ID: ")


def test_declare_propose_accept_inspect_episode(
    tmp_path: Path, capsys
) -> None:
    accept_series(tmp_path)

    assert (
        main(["series", "journey", "declare-episodic", str(tmp_path)]) == 0
    )
    assert "episodic" in capsys.readouterr().out

    assert (
        main(["series", "journey", "declare-episodic", str(tmp_path)]) == 0
    )
    assert "no change" in capsys.readouterr().out

    assert (
        main(
            [
                "series",
                "journey",
                "propose-episode",
                str(tmp_path),
                "--input",
                str(EPISODE_INPUT),
            ]
        )
        == 0
    )
    proposal_id = _proposal_id(capsys.readouterr().out)

    assert (
        main(["series", "journey", "accept-episode", str(tmp_path), proposal_id])
        == 0
    )
    assert "Accepted Episode 1 Direction" in capsys.readouterr().out

    assert (
        main(["series", "journey", "inspect-episode", str(tmp_path)]) == 0
    )
    output = capsys.readouterr().out
    assert "SERIES DIRECTION" in output
    assert "EPISODE 1 DIRECTION" in output
    assert "contested-history" in output
    assert "Book 1" not in output
    assert "Book Direction" not in output


def test_inspect_episode_reports_absence(
    tmp_path: Path, capsys
) -> None:
    accept_series(tmp_path)

    assert (
        main(["series", "journey", "inspect-episode", str(tmp_path)]) == 0
    )
    output = capsys.readouterr().out
    assert "Book-oriented" in output
    assert "Unavailable" in output

    service = SeriesVerticalSliceService(tmp_path)
    service.declare_series_episodic(declaring_author="author")
    assert (
        main(["series", "journey", "inspect-episode", str(tmp_path)]) == 0
    )
    output = capsys.readouterr().out
    assert "none accepted yet" in output


def test_accept_episode_idempotent_no_change(
    tmp_path: Path, capsys
) -> None:
    accept_series(tmp_path)
    service = SeriesVerticalSliceService(tmp_path)
    service.declare_series_episodic(declaring_author="author")
    direction = EpisodeDirection.model_validate(
        yaml.safe_load(EPISODE_INPUT.read_text(encoding="utf-8"))
    )
    proposal = service.propose_episode_direction(direction)

    assert (
        main(
            ["series", "journey", "accept-episode", str(tmp_path), proposal.proposal_id]
        )
        == 0
    )
    capsys.readouterr()
    assert (
        main(
            ["series", "journey", "accept-episode", str(tmp_path), proposal.proposal_id]
        )
        == 0
    )
    assert "no change" in capsys.readouterr().out
