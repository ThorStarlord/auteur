from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from auteur.series.models import SeriesIdentity
from auteur.series.vertical_slice_models import SeriesDirection


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
