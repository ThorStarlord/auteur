"""Capability-level tests for the bounded Episode 1 Direction slice.

Covers acceptance invariants 4, 8, and 9 of the ratified capability contract:
structural reference validation at propose/accept, episodic-only availability,
and entry-form eligibility. Does not yet cover persistence, CLI, or inspection
(those land in later bounded responsibilities).
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from auteur.series.episode_one_direction import (
    AcceptedEpisodeDirection,
    EpisodeDirection,
    EpisodeDirectionProposal,
    EpisodicEntryFormDeclaration,
    require_entry_form_eligibility,
    require_episodic_for_episode_direction,
    validate_episode_references,
)
from auteur.series.vertical_slice_models import (
    AcceptedSeriesDirection,
    ArtifactRef,
    SeriesDirection,
)

FIXTURES = Path(__file__).parent / "fixtures" / "archive_of_lies_vertical_slice"


def _identity() -> dict:
    raw = yaml.safe_load(
        (FIXTURES / "book_1_direction.yaml").read_text(encoding="utf-8")
    )
    return raw["identity"]


def _accepted_series() -> AcceptedSeriesDirection:
    raw = yaml.safe_load(
        (FIXTURES / "series_direction.yaml").read_text(encoding="utf-8")
    )
    return AcceptedSeriesDirection(
        artifact_id="series-direction",
        proposal_id="series-direction-seed",
        direction=SeriesDirection.model_validate(raw),
    )


def _episode_direction(**overrides) -> EpisodeDirection:
    series = _accepted_series()
    payload = {
        "episode_number": 1,
        "identity": _identity(),
        "series_commitment_ids": [
            series.direction.commitments[0].commitment_id
        ],
    }
    payload.update(overrides)
    return EpisodeDirection.model_validate(payload)


def test_episode_direction_requires_at_least_one_reference() -> None:
    with pytest.raises(ValidationError, match="series_commitment_ids"):
        _episode_direction(series_commitment_ids=[])


def test_episode_direction_rejects_duplicate_references() -> None:
    series = _accepted_series()
    first = series.direction.commitments[0].commitment_id
    with pytest.raises(ValidationError, match="Duplicate"):
        _episode_direction(series_commitment_ids=[first, first])


def test_episode_direction_reloads_identically() -> None:
    direction = _episode_direction()
    reloaded = EpisodeDirection.model_validate(direction.model_dump(mode="json"))
    assert reloaded == direction


def test_valid_reference_to_current_commitment_passes() -> None:
    validate_episode_references(_episode_direction(), _accepted_series())


def test_unknown_or_superseded_reference_is_rejected() -> None:
    direction = _episode_direction(
        series_commitment_ids=["commitment-from-superseded-revision"]
    )
    with pytest.raises(ValueError, match="Unknown accepted Series commitment"):
        validate_episode_references(direction, _accepted_series())


def test_entry_form_requires_an_accepted_series_direction() -> None:
    with pytest.raises(ValueError, match="accepted Series Direction is required"):
        require_entry_form_eligibility(
            None,
            has_book_direction_proposal=False,
            has_accepted_book_direction=False,
        )


def test_entry_form_rejected_after_book_direction_proposal() -> None:
    with pytest.raises(ValueError, match="Book Direction work has begun"):
        require_entry_form_eligibility(
            _accepted_series(),
            has_book_direction_proposal=True,
            has_accepted_book_direction=False,
        )


def test_entry_form_rejected_after_accepted_book_direction() -> None:
    with pytest.raises(ValueError, match="Book Direction has been accepted"):
        require_entry_form_eligibility(
            _accepted_series(),
            has_book_direction_proposal=False,
            has_accepted_book_direction=True,
        )


def test_entry_form_eligible_with_accepted_series_and_no_book_work() -> None:
    require_entry_form_eligibility(
        _accepted_series(),
        has_book_direction_proposal=False,
        has_accepted_book_direction=False,
    )


def test_episode_direction_requires_episodic_entry_form() -> None:
    with pytest.raises(ValueError, match="explicitly episodic"):
        require_episodic_for_episode_direction(None)


def test_entry_form_declaration_requires_utc_timestamp() -> None:
    with pytest.raises(ValidationError, match="UTC"):
        EpisodicEntryFormDeclaration(
            declaration_id="series-episodic-entry-form",
            declaring_author="author",
            declared_at=datetime(2026, 9, 26, 12, 0, 0),
            series_direction=ArtifactRef(
                artifact_id="series-direction", revision=1
            ),
        )

    with pytest.raises(ValidationError, match="UTC"):
        EpisodicEntryFormDeclaration(
            declaration_id="series-episodic-entry-form",
            declaring_author="author",
            declared_at=datetime(
                2026, 9, 26, 12, 0, 0, tzinfo=timezone(timedelta(hours=-5))
            ),
            series_direction=ArtifactRef(
                artifact_id="series-direction", revision=1
            ),
        )


def test_accepted_episode_direction_reloads_identically() -> None:
    direction = _episode_direction()
    proposal = EpisodeDirectionProposal(
        proposal_id="episode-1-direction-abc",
        revision=1,
        direction=direction,
        source_refs=[ArtifactRef(artifact_id="series-direction", revision=1)],
    )
    accepted = AcceptedEpisodeDirection(
        artifact_id="episode-1-direction",
        proposal_id=proposal.proposal_id,
        direction=proposal.direction,
    )
    reloaded = AcceptedEpisodeDirection.model_validate(
        accepted.model_dump(mode="json")
    )
    assert reloaded == accepted
    assert reloaded.direction.series_commitment_ids == [
        _accepted_series().direction.commitments[0].commitment_id
    ]
