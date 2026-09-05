from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from auteur.series.models import SeriesIdentity
from auteur.series import vertical_slice_models
from auteur.series.vertical_slice_models import (
    AcceptedEpisodeDirection,
    AcceptedRealizationBundle,
    AcceptedSeriesEntryForm,
    ArtifactRef,
    EpisodeDirection,
    EpisodeDirectionProposal,
    RealizationCandidate,
    SeriesDirection,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "archive_of_lies_vertical_slice"
    / "series_direction.yaml"
)
BOOK_FIXTURE = FIXTURE.with_name("book_1_direction.yaml")


def _episode_direction_payload() -> dict:
    raw = yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    return {
        "identity": raw["identity"],
        "series_commitment_ids": raw["series_commitment_ids"],
    }


def test_ongoing_series_direction_requires_no_future_books() -> None:
    raw = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))

    direction = SeriesDirection.model_validate(raw)
    reloaded = SeriesDirection.model_validate(
        yaml.safe_load(yaml.safe_dump(direction.model_dump(mode="json"), sort_keys=False))
    )

    assert "book_plans" not in raw
    assert "book_plans" not in direction.model_dump(mode="json")
    assert not isinstance(direction, SeriesIdentity)
    assert reloaded == direction


def test_series_direction_requires_at_least_one_commitment() -> None:
    raw = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    raw["commitments"] = []

    with pytest.raises(ValidationError, match="commitments"):
        SeriesDirection.model_validate(raw)


def test_v1_realization_payloads_default_to_no_resolved_commitments() -> None:
    path = (
        Path(__file__).parent
        / "fixtures"
        / "repeated_map_focus_v2"
        / "book_1_realization.yaml"
    )
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))

    candidate = RealizationCandidate.model_validate(raw)
    accepted = AcceptedRealizationBundle(
        artifact_id="realization-bundle-book-1-history",
        bundle_id="realization-bundle-book-1-history",
        candidate_id=candidate.candidate_id,
        book_number=candidate.book_number,
        transitions=candidate.transitions,
    )

    assert candidate.resolved_commitment_ids == []
    assert accepted.resolved_commitment_ids == []
    assert RealizationCandidate.model_validate(
        candidate.model_dump(mode="json")
    ) == candidate
    assert AcceptedRealizationBundle.model_validate(
        accepted.model_dump(mode="json")
    ) == accepted


def test_planning_intent_defaults_to_no_relevance_refs_and_is_strict() -> None:
    intent_type = vertical_slice_models.BookPlanningIntent

    intent = intent_type(book_number=4, intent="Return to the testimony.")

    assert intent.relevance_refs == []
    with pytest.raises(ValidationError, match="extra"):
        intent_type(
            book_number=4,
            intent="Return to the testimony.",
            accepted=True,
        )


def test_episode_direction_round_trips() -> None:
    payload = _episode_direction_payload()

    direction = EpisodeDirection.model_validate(payload)
    reloaded = EpisodeDirection.model_validate(
        yaml.safe_load(
            yaml.safe_dump(direction.model_dump(mode="json"), sort_keys=False)
        )
    )

    assert direction.episode_number == 1
    assert reloaded == direction


@pytest.mark.parametrize("episode_number", [0, 2])
def test_episode_direction_rejects_non_one_episode_number(
    episode_number: int,
) -> None:
    payload = {**_episode_direction_payload(), "episode_number": episode_number}

    with pytest.raises(ValidationError):
        EpisodeDirection.model_validate(payload)


def test_episode_direction_rejects_zero_commitment_refs() -> None:
    payload = {**_episode_direction_payload(), "series_commitment_ids": []}

    with pytest.raises(ValidationError, match="series_commitment_ids"):
        EpisodeDirection.model_validate(payload)


def test_episode_direction_rejects_duplicate_commitment_refs_without_dedup() -> None:
    payload = {
        **_episode_direction_payload(),
        "series_commitment_ids": ["contested-history", "contested-history"],
    }

    with pytest.raises(ValueError, match="duplicate"):
        EpisodeDirection.model_validate(payload)


def test_episode_direction_accepts_unique_refs_without_silent_dedup() -> None:
    payload = {
        **_episode_direction_payload(),
        "series_commitment_ids": ["contested-history", "other-commitment"],
    }

    direction = EpisodeDirection.model_validate(payload)

    assert direction.series_commitment_ids == [
        "contested-history",
        "other-commitment",
    ]


def test_episode_direction_rejects_whitespace_only_title() -> None:
    payload = _episode_direction_payload()
    payload["identity"] = {**payload["identity"], "title": "   "}

    with pytest.raises(ValueError, match="title"):
        EpisodeDirection.model_validate(payload)


def test_episode_direction_rejects_whitespace_only_core_answer() -> None:
    payload = _episode_direction_payload()
    payload["identity"] = {**payload["identity"], "core_answer": "   "}

    with pytest.raises(ValueError, match="core_answer"):
        EpisodeDirection.model_validate(payload)


def test_episode_direction_rejects_extra_keys() -> None:
    payload = {**_episode_direction_payload(), "unexpected": True}

    with pytest.raises(ValidationError, match="extra"):
        EpisodeDirection.model_validate(payload)


def test_episode_direction_proposal_requires_at_least_one_source_ref() -> None:
    direction = EpisodeDirection.model_validate(_episode_direction_payload())

    with pytest.raises(ValidationError, match="source_refs"):
        EpisodeDirectionProposal(
            proposal_id="episode-direction-1",
            revision=1,
            direction=direction,
            source_refs=[],
        )


def test_episode_direction_proposal_requires_revision_at_least_one() -> None:
    direction = EpisodeDirection.model_validate(_episode_direction_payload())

    with pytest.raises(ValidationError, match="revision"):
        EpisodeDirectionProposal(
            proposal_id="episode-direction-1",
            revision=0,
            direction=direction,
            source_refs=[ArtifactRef(artifact_id="series-direction", revision=1)],
        )


def test_episode_direction_proposal_rejects_extra_keys() -> None:
    direction = EpisodeDirection.model_validate(_episode_direction_payload())

    with pytest.raises(ValidationError, match="extra"):
        EpisodeDirectionProposal(
            proposal_id="episode-direction-1",
            revision=1,
            direction=direction,
            source_refs=[ArtifactRef(artifact_id="series-direction", revision=1)],
            unexpected=True,
        )


def test_accepted_episode_direction_round_trips_with_fixed_artifact_id() -> None:
    direction = EpisodeDirection.model_validate(_episode_direction_payload())

    accepted = AcceptedEpisodeDirection(
        proposal_id="episode-direction-1", direction=direction
    )
    reloaded = AcceptedEpisodeDirection.model_validate(
        yaml.safe_load(
            yaml.safe_dump(accepted.model_dump(mode="json"), sort_keys=False)
        )
    )

    assert accepted.artifact_id == "episode-1-direction"
    assert reloaded == accepted


def test_accepted_episode_direction_rejects_extra_keys() -> None:
    direction = EpisodeDirection.model_validate(_episode_direction_payload())

    with pytest.raises(ValidationError, match="extra"):
        AcceptedEpisodeDirection(
            proposal_id="episode-direction-1",
            direction=direction,
            unexpected=True,
        )


def test_accepted_series_entry_form_accepts_episodic() -> None:
    record = AcceptedSeriesEntryForm(entry_form="episodic", declared_by="author")

    assert record.artifact_id == "series-entry-form"
    assert record.entry_form == "episodic"


def test_accepted_series_entry_form_rejects_other_entry_form_values() -> None:
    with pytest.raises(ValidationError):
        AcceptedSeriesEntryForm(entry_form="book", declared_by="author")


def test_accepted_series_entry_form_rejects_empty_declared_by() -> None:
    with pytest.raises(ValidationError, match="declared_by"):
        AcceptedSeriesEntryForm(entry_form="episodic", declared_by="")


def test_accepted_series_entry_form_rejects_extra_keys() -> None:
    with pytest.raises(ValidationError, match="extra"):
        AcceptedSeriesEntryForm(
            entry_form="episodic", declared_by="author", unexpected=True
        )
