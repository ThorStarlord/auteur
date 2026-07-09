from __future__ import annotations

from series_fixtures import valid_trilogy_data


def _rules(series) -> set[str]:
    from auteur.series.diagnostics import diagnose_series

    return {d.rule for d in diagnose_series(series)}


def test_valid_escalation_has_no_flat_stakes_warning():
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())

    assert "series.scope.flat_stakes" not in _rules(series)


def test_character_regression_without_transition_warns():
    from auteur.series.models import SeriesIdentity

    data = valid_trilogy_data()
    data["character_arcs"][0]["book_states"]["2"] = "revenge obsessed"
    data["character_arcs"][0]["transitions"].pop("1->2")
    series = SeriesIdentity.model_validate(data)

    assert "series.character.regression_without_transition" in _rules(series)


def test_flat_stakes_warns():
    from auteur.series.models import SeriesIdentity

    data = valid_trilogy_data()
    for book in data["book_plans"]:
        book["scope"] = "city"
        book["central_engine"]["stakes"] = "The same village is threatened."
    series = SeriesIdentity.model_validate(data)

    assert "series.scope.flat_stakes" in _rules(series)


def test_premature_mystery_payoff_warns():
    from auteur.series.models import SeriesIdentity

    data = valid_trilogy_data()
    data["mysteries"][0]["actual_payoff_book"] = 1
    series = SeriesIdentity.model_validate(data)

    assert "series.mystery.premature_payoff" in _rules(series)


def test_transformation_completed_too_early_warns():
    from auteur.series.models import SeriesIdentity

    data = valid_trilogy_data()
    data["character_arcs"][0]["book_states"]["1"] = "reluctant ruler"
    series = SeriesIdentity.model_validate(data)

    assert "series.character.completed_too_early" in _rules(series)
