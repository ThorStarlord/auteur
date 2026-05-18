from pathlib import Path

import pytest
from pydantic import ValidationError

from auteur.blueprint import (
    ConsequenceScale,
    InteractionModel,
    MechanicalLoad,
    MediumFormat,
    ReleaseModel,
    NarrativeRunway,
    ScopeComplexity,
    StoryBlueprint,
    StoryEngine,
    StoryMedium,
    StoryMode,
    UnitOfDelivery,
    SupportFunction,
    ThreadType,
)
from auteur.structure.analyzer import analyze_structure


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
    assert blueprint.identity.medium_contract is not None
    assert blueprint.identity.medium_contract.medium == StoryMedium.NOVEL
    assert blueprint.identity.medium_contract.format == MediumFormat.STANDALONE_BOOK
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
    assert blueprint.identity.medium_contract is None
    assert blueprint.story_engine is None


def test_legacy_medium_populates_medium_contract_from_registry():
    data = {
        "identity": {
            "title": "Legacy Medium",
            "author_intent": "A compact test premise.",
            "length_class": "novella",
            "genre": "horror",
            "medium": "visual_novel",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "unease -> dread",
        },
        "theme": {
            "central_question": "What waits in the dark?",
            "thesis": "Curiosity has a cost.",
            "motifs": [],
        },
    }

    blueprint = StoryBlueprint.model_validate(data)

    assert blueprint.identity.medium == StoryMedium.VISUAL_NOVEL
    assert blueprint.identity.medium_contract is not None
    assert blueprint.identity.medium_contract.medium == StoryMedium.VISUAL_NOVEL
    assert blueprint.identity.medium_contract.format == MediumFormat.ROUTE_BASED


def test_blueprint_accepts_nested_medium_contract():
    data = {
        "identity": {
            "title": "Serial Horror",
            "author_intent": "A daily horror serial built around escalating room discoveries.",
            "length_class": "novel",
            "genre": "horror",
            "medium": "novel",
            "medium_contract": {
                "medium": "novel",
                "format": "webnovel",
                "release_model": "episodic_serial",
                "interaction_model": "serial_reader",
                "unit_of_delivery": "episode",
                "representation_units": ["short chapters", "cliffhangers"],
                "modulation_biases": ["fast re-entry"],
                "medium_failure_modes": ["episodes end without propulsion"],
            },
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "hook -> dread -> hook",
        },
        "theme": {
            "central_question": "What does curiosity cost?",
            "thesis": "Attention can become appetite.",
            "motifs": [],
        },
    }

    blueprint = StoryBlueprint.model_validate(data)

    assert blueprint.identity.medium_contract is not None
    assert blueprint.identity.medium_contract.format == MediumFormat.WEBNOVEL
    assert blueprint.identity.medium_contract.release_model == ReleaseModel.EPISODIC_SERIAL
    assert blueprint.identity.medium_contract.interaction_model == InteractionModel.SERIAL_READER
    assert blueprint.identity.medium_contract.unit_of_delivery == UnitOfDelivery.EPISODE
    assert "cliffhangers" in blueprint.identity.medium_contract.representation_units


def test_medium_contract_rejects_invalid_enum_values():
    data = {
        "identity": {
            "title": "Invalid Medium Contract",
            "author_intent": "A test premise.",
            "length_class": "novella",
            "genre": "horror",
            "medium_contract": {
                "medium": "novel",
                "format": "scrolling_dream",
                "release_model": "complete_release",
                "interaction_model": "passive_reader",
                "unit_of_delivery": "chapter",
            },
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "unease -> dread",
        },
        "theme": {
            "central_question": "What waits in the dark?",
            "thesis": "Curiosity has a cost.",
            "motifs": [],
        },
    }

    with pytest.raises(ValidationError, match="format"):
        StoryBlueprint.model_validate(data)


def test_medium_contract_mismatch_produces_structure_diagnostic():
    data = {
        "identity": {
            "title": "Mismatch",
            "author_intent": "A test premise.",
            "length_class": "novella",
            "genre": "horror",
            "medium": "novel",
            "medium_contract": {
                "medium": "game",
                "format": "action_game",
                "release_model": "complete_release",
                "interaction_model": "player_agency",
                "unit_of_delivery": "mission",
            },
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "unease -> dread",
        },
        "theme": {
            "central_question": "What waits in the dark?",
            "thesis": "Curiosity has a cost.",
            "motifs": [],
        },
    }

    blueprint = StoryBlueprint.model_validate(data)

    diagnostics = analyze_structure(blueprint)

    assert any(
        diagnostic.rule == "medium_contract.medium_mismatch"
        for diagnostic in diagnostics
    )


def test_missing_medium_contract_produces_structure_diagnostic():
    data = {
        "identity": {
            "title": "No Medium",
            "author_intent": "A test premise.",
            "length_class": "novella",
            "genre": "horror",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "unease -> dread",
        },
        "theme": {
            "central_question": "What waits in the dark?",
            "thesis": "Curiosity has a cost.",
            "motifs": [],
        },
    }

    blueprint = StoryBlueprint.model_validate(data)

    diagnostics = analyze_structure(blueprint)

    assert any(
        diagnostic.rule == "medium_contract.missing"
        for diagnostic in diagnostics
    )


def test_blueprint_accepts_nested_scope_contract():
    data = {
        "identity": {
            "title": "Fortress Betrayal",
            "author_intent": "A focused grimdark fantasy about one siege and one moral collapse.",
            "length_class": "novel",
            "genre": "grimdark_fantasy",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "structure": {
            "scope_contract": {
                "recommended_complexity": "focused",
                "narrative_runway": "medium",
                "mechanical_load": "medium",
                "setting_footprint": "local",
                "timeframe": "compressed",
                "worldbuilding_load": "medium",
                "cast_load": "medium",
                "trope_load": "selective",
                "scope_notes": [
                    "Keep the war off-page and make the fortress the arena."
                ],
                "scope_warnings": [
                    "Do not add a full faction war unless length expands."
                ],
            }
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "bittersweet",
        },
        "emotional_design": {
            "overall_emotional_arc": "pressure -> compromise -> cost",
        },
        "theme": {
            "central_question": "What does survival cost?",
            "thesis": "Power preserves the body while corroding the self.",
            "motifs": [],
        },
    }

    blueprint = StoryBlueprint.model_validate(data)

    assert blueprint.structure.scope_contract is not None
    assert blueprint.structure.scope_contract.recommended_complexity == ScopeComplexity.FOCUSED
    assert blueprint.structure.scope_contract.narrative_runway == NarrativeRunway.MEDIUM
    assert blueprint.structure.scope_contract.mechanical_load == MechanicalLoad.MEDIUM
    assert blueprint.structure.scope_contract.scope_warnings == [
        "Do not add a full faction war unless length expands."
    ]


def test_scope_contract_rejects_invalid_load_values():
    data = {
        "identity": {
            "title": "Bad Scope",
            "author_intent": "A test premise.",
            "length_class": "novella",
            "genre": "horror",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "structure": {
            "scope_contract": {
                "recommended_complexity": "focused",
                "narrative_runway": "medium",
                "mechanical_load": "enormous",
            }
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "unease -> dread",
        },
        "theme": {
            "central_question": "What waits in the dark?",
            "thesis": "Curiosity has a cost.",
            "motifs": [],
        },
    }

    with pytest.raises(ValidationError, match="mechanical_load"):
        StoryBlueprint.model_validate(data)


def test_stakes_accept_consequence_scale_metadata():
    engine = StoryEngine.model_validate(
        {
            "main_thread": {
                "want": _claim("The protagonist wants to expose the false king."),
                "resistance": _claim("The court profits from the lie."),
                "conflict": _claim("Truth would save the realm and destroy the protagonist's family."),
                "stakes": {
                    "author_text": "If she fails, the city falls into civil war.",
                    "checkable_claims": [],
                    "consequence_scale": "city",
                    "escalation_ceiling": "national",
                },
                "change": _claim("The protagonist becomes willing to lose status for truth."),
                "thematic_function": "Tests whether truth matters when everyone benefits from a lie.",
            },
            "threads": [],
        }
    )

    assert engine.main_thread.stakes.consequence_scale == ConsequenceScale.CITY
    assert engine.main_thread.stakes.escalation_ceiling == ConsequenceScale.NATIONAL


def test_stakes_consequence_scale_is_optional_for_existing_yaml_shape():
    engine = StoryEngine.model_validate(
        {
            "main_thread": {
                "want": _claim("The protagonist wants to expose the false king."),
                "resistance": _claim("The court profits from the lie."),
                "conflict": _claim("Truth would save the realm and destroy the protagonist's family."),
                "stakes": _claim("Every choice deepens either public ruin or private betrayal."),
                "change": _claim("The protagonist becomes willing to lose status for truth."),
                "thematic_function": "Tests whether truth matters when everyone benefits from a lie.",
            },
            "threads": [],
        }
    )

    assert engine.main_thread.stakes.consequence_scale is None
    assert engine.main_thread.stakes.escalation_ceiling is None


def test_stakes_reject_invalid_consequence_scale():
    with pytest.raises(ValidationError, match="consequence_scale"):
        StoryEngine.model_validate(
            {
                "main_thread": {
                    "want": _claim("The protagonist wants to expose the false king."),
                    "resistance": _claim("The court profits from the lie."),
                    "conflict": _claim("Truth would save the realm and destroy the protagonist's family."),
                    "stakes": {
                        "author_text": "If she fails, the city falls into civil war.",
                        "checkable_claims": [],
                        "consequence_scale": "galactic",
                    },
                    "change": _claim("The protagonist becomes willing to lose status for truth."),
                    "thematic_function": "Tests whether truth matters when everyone benefits from a lie.",
                },
                "threads": [],
            }
        )


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
