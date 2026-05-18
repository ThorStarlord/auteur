from auteur.blueprint import MediumFormat, StoryMedium
from auteur.mediums.registry import load_medium_contract


def test_every_story_medium_has_loadable_contract():
    for medium in StoryMedium:
        contract = load_medium_contract(medium)

        assert contract.medium == medium
        assert contract.representation_units
        assert contract.modulation_biases
        assert contract.medium_failure_modes


def test_invalid_string_medium_falls_back_to_other():
    contract = load_medium_contract("not_a_real_medium")

    assert contract.medium == StoryMedium.OTHER
    assert contract.format == MediumFormat.OTHER


def test_seeded_contracts_capture_delivery_grammar():
    novel = load_medium_contract(StoryMedium.NOVEL)
    visual_novel = load_medium_contract(StoryMedium.VISUAL_NOVEL)
    game = load_medium_contract(StoryMedium.GAME)

    assert "prose narration" in novel.representation_units
    assert "routes" in visual_novel.representation_units
    assert "choices" in visual_novel.representation_units
    assert game.format == MediumFormat.ACTION_GAME
    assert "gameplay encounters" in game.representation_units
