from __future__ import annotations

from series_fixtures import valid_trilogy_data


def test_series_bible_contains_compiled_sections():
    from auteur.series.bible import compile_series_bible
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())
    bible = compile_series_bible(series)

    assert bible["characters"][0]["name"] == "Elena"
    assert bible["relationships"]
    assert bible["factions"][0]["name"] == "Empire"
    assert bible["mysteries"][0]["id"] == "emperor_identity"
    assert bible["timeline"][0]["book"] == 1
    assert bible["recurring_symbols"] == ["ash crown", "broken gates"]
    assert "emperor_identity" in bible["dependency_index"]
    assert bible["character_state_matrix"]["Elena"]["2"] == "exhausted commander"
    assert bible["relationship_state_matrix"]["elena_marcus"]["2"] == "fracture"
    assert bible["faction_state_matrix"]["Empire"]["2"] == "civil_war"
    assert bible["mystery_status_by_book"]["3"][0]["status"] == "paid_off"
    assert bible["payoff_schedule"]["3"] == ["emperor_identity"]
    assert bible["unresolved_threads"] == []
    assert bible["book_context_packets"]["2"]["series_function"] == "complication"


def test_series_bible_is_deterministic():
    from auteur.series.bible import compile_series_bible
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())

    assert compile_series_bible(series) == compile_series_bible(series)
