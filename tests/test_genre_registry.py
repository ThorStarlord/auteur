import pytest
from auteur.blueprint import Genre
from auteur.genres.models import GenreContract, PsychologyLevel, RequirementLevel
from auteur.genres.registry import load_genre_contract

def test_load_grimdark_fantasy():
    contract = load_genre_contract(Genre.GRIMDARK_FANTASY)
    assert contract.genre_id == Genre.GRIMDARK_FANTASY
    assert contract.display_name == "Grimdark Fantasy"
    assert "moral pressure" in contract.audience_product.lower()
    assert contract.psychology_budget.level == PsychologyLevel.CONFLICT_BEARING
    assert contract.psychology_budget.motivation_clarity == RequirementLevel.REQUIRED
    assert "hopeful ending" in contract.forbidden_mismatches

def test_load_romance():
    contract = load_genre_contract(Genre.ROMANCE)
    assert contract.genre_id == Genre.ROMANCE
    assert contract.display_name == "Romance"
    assert contract.psychology_budget.level == PsychologyLevel.CONFLICT_BEARING
    assert "tragic ending" in contract.forbidden_mismatches
    assert "happily ever after or happy for now" in contract.required_tropes

def test_load_horror():
    contract = load_genre_contract(Genre.HORROR)
    assert contract.genre_id == Genre.HORROR
    assert contract.display_name == "Horror"
    assert contract.psychology_budget.level == PsychologyLevel.FUNCTIONAL
    assert "therapeutic explanation of the monster" in contract.forbidden_mismatches
    assert contract.scope_profile.default_length.value == "short_story"
    assert contract.scope_profile.narrative_runway.value == "short"
    assert contract.scope_profile.mechanical_load.value == "medium"
    assert "Use one central threat." in contract.scope_profile.compression_strategies

def test_load_mystery():
    contract = load_genre_contract(Genre.MYSTERY)
    assert contract.genre_id == Genre.MYSTERY
    assert contract.display_name == "Mystery"
    assert contract.psychology_budget.level == PsychologyLevel.FUNCTIONAL
    assert "clue logic" in contract.required_tropes
    assert contract.scope_profile.minimum_viable_length.value == "short_story"
    assert contract.scope_profile.default_length.value == "novel"
    assert contract.scope_profile.narrative_runway.value == "medium"
    assert any("suspect" in mode for mode in contract.scope_profile.scope_failure_modes)

def test_load_thriller():
    contract = load_genre_contract(Genre.THRILLER)
    assert contract.genre_id == Genre.THRILLER
    assert contract.display_name == "Thriller"
    assert contract.psychology_budget.level == PsychologyLevel.FUNCTIONAL
    assert any("passive protagonist" in m for m in contract.forbidden_mismatches)

def test_unregistered_genre_fallback():
    # Cozy Mystery is in the Genre enum, but does not have a YAML file
    contract = load_genre_contract(Genre.COZY_MYSTERY)
    assert contract.genre_id == Genre.COZY_MYSTERY
    assert contract.display_name == "Cozy Mystery"
    # Fallback default uses functional level
    assert contract.psychology_budget.level == PsychologyLevel.FUNCTIONAL
    assert contract.psychology_budget.motivation_clarity == RequirementLevel.REQUIRED
    assert contract.scope_profile.default_length.value == "novel"
    assert contract.scope_profile.recommended_complexity.value == "standard"
    assert contract.scope_profile.mechanical_load.value == "medium"

def test_invalid_string_genre_fallback():
    # An entirely custom/invalid genre string falls back to Genre.OTHER
    contract = load_genre_contract("non_existent_genre_string")
    assert contract.genre_id == Genre.OTHER
    assert contract.display_name == "Other"
    assert contract.psychology_budget.level == PsychologyLevel.FUNCTIONAL

def test_registry_caching():
    contract1 = load_genre_contract(Genre.THRILLER)
    contract2 = load_genre_contract(Genre.THRILLER)
    assert contract1 is contract2  # Should be the exact same object in memory


def test_load_grimdark_fantasy_scope_profile():
    contract = load_genre_contract(Genre.GRIMDARK_FANTASY)

    assert contract.scope_profile.default_length.value == "novel"
    assert contract.scope_profile.narrative_runway.value == "long"
    assert contract.scope_profile.worldbuilding_load.value == "high"
    assert contract.scope_profile.cast_load.value == "high"
    assert any("faction" in mode.casefold() for mode in contract.scope_profile.scope_failure_modes)
