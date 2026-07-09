from __future__ import annotations

import pytest
from pydantic import ValidationError

from series_fixtures import valid_trilogy_data


def test_valid_trilogy_parses():
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())

    assert series.title == "The Ash Empire Trilogy"
    assert series.series_type == "trilogy"
    assert len(series.book_plans) == 3


@pytest.mark.parametrize(
    ("series_type", "count", "book_count", "valid"),
    [
        ("duology", 2, None, True),
        ("duology", 3, None, False),
        ("trilogy", 3, None, True),
        ("trilogy", 2, None, False),
        ("quartet", 4, None, True),
        ("quartet", 3, None, False),
        ("limited_series", 3, 3, True),
        ("limited_series", 3, 4, False),
        ("ongoing", 2, None, True),
        ("ongoing", 1, None, False),
    ],
)
def test_series_type_book_count_rules(series_type, count, book_count, valid):
    from auteur.series.models import SeriesIdentity

    data = valid_trilogy_data()
    data["series_type"] = series_type
    data["book_plans"] = data["book_plans"][:count]
    data["dependency_edges"] = []
    if count == 4:
        extra = dict(data["book_plans"][-1])
        extra["book_number"] = 4
        extra["title"] = "After Ash"
        data["book_plans"].append(extra)
    data["book_count"] = book_count

    if valid:
        assert SeriesIdentity.model_validate(data).series_type == series_type
    else:
        with pytest.raises(ValidationError):
            SeriesIdentity.model_validate(data)


@pytest.mark.parametrize("field", ["continuity_facts", "impact_metadata", "diagnostic_findings", "compiled_timeline"])
def test_series_identity_rejects_generated_fields(field):
    from auteur.series.models import SeriesIdentity

    data = valid_trilogy_data()
    data[field] = {}

    with pytest.raises(ValidationError):
        SeriesIdentity.model_validate(data)


def test_dependency_edges_reject_unknown_nodes():
    from auteur.series.models import SeriesIdentity

    data = valid_trilogy_data()
    data["dependency_edges"].append(
        {"source": "missing_reveal", "target": "book_2", "type": "depends_on"}
    )

    with pytest.raises(ValidationError):
        SeriesIdentity.model_validate(data)
