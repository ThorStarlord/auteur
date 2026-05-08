from pathlib import Path

import pytest
from pydantic import ValidationError

from auteur.blueprint import (
    StoryBlueprint,
    StoryEngine,
    StoryMedium,
    StoryMode,
    SupportFunction,
    ThreadType,
)


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _claim(text: str) -> dict[str, object]:
    return {"author_text": text, "checkable_claims": []}


def test_sample_blueprint_loads_whole_story_engine_fields():
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)

    assert blueprint.identity.target_experience.primary == "dread"
    assert blueprint.identity.target_experience.progression == "unease -> dread -> catharsis"
    assert blueprint.identity.target_experience.avoid == [
        "triumphant power fantasy",
        "cozy safety",
    ]
    assert blueprint.identity.subgenre == "grimdark"
    assert blueprint.identity.subgenres == ["grimdark", "corruption_tragedy"]
    assert blueprint.identity.mode == StoryMode.TRAGIC
    assert blueprint.identity.medium == StoryMedium.NOVEL
    assert blueprint.structure.subplot_budget == 3

    assert blueprint.story_engine is not None
    assert blueprint.story_engine.main_thread.type == ThreadType.MAIN_PLOT
    assert blueprint.story_engine.main_thread.want.author_text.startswith("Kael wants")
    assert blueprint.story_engine.main_thread.thematic_function.startswith("Tests whether")

    thread = blueprint.story_engine.threads[0]
    assert thread.type == ThreadType.CHARACTER_ARC
    assert thread.supports_main_by == [
        SupportFunction.CONTRASTS,
        SupportFunction.PRESSURES_CHANGE,
    ]
    assert "restraint" in thread.thematic_function


def test_legacy_subgenre_is_preserved_when_subgenres_are_absent():
    data = {
        "identity": {
            "title": "Legacy Story",
            "author_intent": "A compact test premise.",
            "length_class": "short_story",
            "genre": "literary",
            "subgenre": "chamber_piece",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "quiet unease",
        },
        "theme": {
            "central_question": "What remains unsaid?",
            "thesis": "Silence can be a form of action.",
            "motifs": [],
        },
    }

    blueprint = StoryBlueprint.model_validate(data)

    assert blueprint.identity.subgenre == "chamber_piece"
    assert blueprint.identity.subgenres == []
    assert blueprint.identity.target_experience is None
    assert blueprint.identity.mode is None
    assert blueprint.identity.medium is None
    assert blueprint.story_engine is None


def test_subordinate_threads_cannot_use_main_plot_type():
    with pytest.raises(ValidationError, match="main_plot"):
        StoryEngine.model_validate(
            {
                "main_thread": {
                    "want": _claim("The protagonist wants to expose the false king."),
                    "resistance": _claim("The court profits from the lie."),
                    "conflict": _claim("Truth would save the realm and destroy the protagonist's family."),
                    "stakes": _claim("Every choice deepens either public ruin or private betrayal."),
                    "change": _claim("The protagonist becomes willing to lose status for truth."),
                    "thematic_function": "Tests whether truth matters when everyone benefits from a lie.",
                },
                "threads": [
                    {
                        "name": "Court succession",
                        "type": "main_plot",
                        "want": _claim("A faction wants the throne."),
                        "resistance": _claim("The old guard blocks succession."),
                        "conflict": _claim("Competing claims fracture the court."),
                        "stakes": _claim("Civil war becomes more likely."),
                        "change": _claim("The succession claim curdles into open revolt."),
                        "supports_main_by": ["escalates"],
                        "thematic_function": "Shows how institutions preserve useful lies.",
                    }
                ],
            }
        )
