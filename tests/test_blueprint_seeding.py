import pytest
from pathlib import Path
import yaml
from auteur.identity import StoryIdentity, compile_to_blueprint
from auteur.blueprint import StoryBlueprint, EndingTone, Genre, StoryMode

def test_compile_to_blueprint_valid():
    identity_data = {
        "title": "A Song of Bronze",
        "core_answer": "A tragic political drama about the bronze age collapse.",
        "target_experience": {
            "primary": "inevitability",
            "progression": "confidence -> unease -> collapse",
            "avoid": ["modern sensibilities", "deus ex machina"]
        },
        "story_type": {
            "medium": "novel",
            "mode": "tragic",
            "genre": "grimdark_fantasy",
            "subgenres": ["bronze_punk", "political_tragedy"],
            "target_audience": "adult"
        },
        "central_engine": {
            "want": "The king wants to preserve the trade routes at any cost.",
            "resistance": "The Sea Peoples disrupt the shipping lanes and burn the ports.",
            "conflict": "Sacrificing minor cities protects the capital but destroys the empire's legitimacy.",
            "stakes": "The complete collapse of late bronze age civilization.",
            "change": "The king changes from a proud god-ruler to an exhausted survivor sitting in ashes.",
        },
        "not_this": ["a triumph story", "magic-heavy fantasy"],
        "open_questions": ["Will any of the royal archive survive the fire?", "Does the crown prince betray the king?"],
        "recommendation_mode": "opinionated",
        "best_basis": "genre_aligned",
        "why_this_is_best": "The bronze age collapse premise is most genre-aligned as political tragedy, because the expected promise is escalating institutional failure rather than personal victory.",
        "rejected_directions": [
            "A heroic war epic would fight the collapse promise.",
            "A cozy court intrigue would undercut the scale of civilization failure.",
        ],
        "author_overrides": [
            "Do not soften the ending into a restoration of the old empire.",
        ],
    }
    
    identity = StoryIdentity.model_validate(identity_data)
    blueprint = compile_to_blueprint(identity)
    
    # Verify Project Identity
    assert blueprint.identity.title == "A Song of Bronze"
    assert blueprint.identity.author_intent == "A tragic political drama about the bronze age collapse."
    assert blueprint.identity.target_experience.primary == "inevitability"
    assert blueprint.identity.target_experience.progression == "confidence -> unease -> collapse"
    assert blueprint.identity.target_experience.avoid == ["modern sensibilities", "deus ex machina"]
    assert blueprint.identity.genre == Genre.GRIMDARK_FANTASY
    assert blueprint.identity.subgenres == ["bronze_punk", "political_tragedy"]
    assert blueprint.identity.mode == StoryMode.TRAGIC
    assert blueprint.identity.target_audience.value == "adult"
    assert blueprint.identity.author_intent == identity.core_answer
    
    # Verify Story Engine
    assert blueprint.story_engine is not None
    assert blueprint.story_engine.main_thread.want.author_text == "The king wants to preserve the trade routes at any cost."
    assert blueprint.story_engine.main_thread.resistance.author_text == "The Sea Peoples disrupt the shipping lanes and burn the ports."
    assert blueprint.story_engine.main_thread.conflict.author_text == "Sacrificing minor cities protects the capital but destroys the empire's legitimacy."
    assert blueprint.story_engine.main_thread.stakes.author_text == "The complete collapse of late bronze age civilization."
    assert blueprint.story_engine.main_thread.change.author_text == "The king changes from a proud god-ruler to an exhausted survivor sitting in ashes."
    assert "Will any of the royal archive survive" in blueprint.story_engine.main_thread.thematic_function
    
    # Verify Contract
    assert blueprint.contract.mandatory_ending_tone == EndingTone.TRAGIC
    assert blueprint.contract.content_rating.value == "R"
    
    # Verify Characters
    assert len(blueprint.characters) == 2
    assert blueprint.characters[0].name == "Protagonist"
    assert blueprint.characters[0].role.value == "protagonist"
    assert blueprint.characters[0].arc_type.value == "corruption"
    assert blueprint.characters[1].name == "Antagonist"
    assert blueprint.characters[1].role.value == "antagonist"
    
    # Verify we can serialize and deserialize back to a valid StoryBlueprint
    serialized = yaml.safe_dump(blueprint.model_dump(mode="json"))
    loaded_data = yaml.safe_load(serialized)
    parsed_blueprint = StoryBlueprint.model_validate(loaded_data)
    assert parsed_blueprint.identity.title == "A Song of Bronze"
    assert not hasattr(parsed_blueprint.identity, "why_this_is_best")
