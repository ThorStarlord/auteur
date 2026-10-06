from auteur.beginner.creative_divergence import infer_creative_discoveries


def values(text: str) -> set[str]:
    return {item["value"] for item in infer_creative_discoveries(text)}


def test_keeps_clear_new_place_and_named_character() -> None:
    discovered = values(
        "At the abandoned seaside convent, Sister Beatrice tells Detective Miller the truth."
    )
    assert "Sister Beatrice" in discovered
    assert "abandoned seaside convent" in discovered


def test_filters_real_generated_non_place_prepositional_phrases() -> None:
    discovered = values(
        "Miller saw doubt in Miller's face, blood on his hand, a man in a gray jacket, "
        "and rain on Vance's shoulders before driving to the abandoned seaside convent."
    )
    assert "abandoned seaside convent" in discovered
    assert "Miller's face" not in discovered
    assert "a gray jacket" not in discovered
    assert "Vance's shoulders" not in discovered


def test_keeps_common_location_heads_without_general_noun_extraction() -> None:
    discovered = values(
        "She waited in the restaurant, crossed to the police precinct, and slept in an apartment."
    )
    assert "restaurant" in discovered
    assert "police precinct" in discovered
    assert "an apartment" in discovered
