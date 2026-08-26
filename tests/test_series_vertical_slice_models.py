from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from auteur.series.models import SeriesIdentity
from auteur.series import vertical_slice_models
from auteur.series.vertical_slice_models import (
    AcceptedRealizationBundle,
    RealizationCandidate,
    SeriesDirection,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "archive_of_lies_vertical_slice"
    / "series_direction.yaml"
)


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
