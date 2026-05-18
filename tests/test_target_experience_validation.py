from auteur.blueprint import TargetExperience, StoryBlueprint
from auteur.structure import analyze_structure, DiagnosticSeverity, DiagnosticLayer


def _blueprint_base_data() -> dict[str, object]:
    return {
        "identity": {
            "title": "Test Story",
            "author_intent": "A test premise.",
            "length_class": "novel",
            "genre": "literary",
            "medium": "novel",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "quiet pressure",
        },
        "theme": {
            "central_question": "What does truth cost?",
            "thesis": "Truth costs belonging.",
            "motifs": [],
        },
        "story_engine": {
            "main_thread": {
                "want": {"author_text": "The protagonist wants truth.", "checkable_claims": []},
                "resistance": {"author_text": "The town lies.", "checkable_claims": []},
                "conflict": {"author_text": "Truth is painful.", "checkable_claims": []},
                "stakes": {"author_text": "Losing home.", "checkable_claims": []},
                "change": {"author_text": "Protagonist accepts exile.", "checkable_claims": []},
                "thematic_function": "Tests that truth costs belonging.",
            },
            "threads": [],
        },
        "characters": [
            {
                "name": "Protagonist",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
                "current_arc_percentage": 0,
                "key_milestones": [],
                "current_state": {},
            }
        ]
    }


def test_simplified_target_experience_validation():
    data = {
        "primary": "dread",
        "progression": "wonder -> unease -> dread -> tragic catharsis",
        "secondary": ["longing", "moral discomfort"],
        "avoid": ["cozy safety", "clean triumph"],
    }
    te = TargetExperience.model_validate(data)

    assert te.primary == "dread"
    assert te.primary_emotional_promise == "dread"
    assert te.progression == "wonder -> unease -> dread -> tragic catharsis"
    assert te.secondary == ["longing", "moral discomfort"]
    assert te.secondary_palette == ["longing", "moral discomfort"]
    assert te.avoid == ["cozy safety", "clean triumph"]
    assert te.avoided_experiences == ["cozy safety", "clean triumph"]


def test_rich_target_experience_validation():
    data = {
        "primary_emotional_promise": "dread",
        "secondary_palette": ["wonder", "longing", "moral discomfort", "grief"],
        "avoided_experiences": ["cozy safety", "clean heroic triumph"],
        "emotional_trajectory": {
            "pattern": "wonder -> unease -> dread -> tragic catharsis",
            "start": "wonder",
            "midpoint": "dread",
            "ending": "tragic catharsis",
        },
        "genre_emotion_stack": {
            "primary": {
                "genre": "grimdark_fantasy",
                "emotion": "dread",
                "role": "dominant audience product",
            },
            "secondary": {
                "genre": "romance",
                "emotion": "longing",
                "role": "makes the fall emotionally costly",
            }
        },
        "pov_experience_contracts": {
            "protagonist": {
                "dominant_feeling": "moral pressure",
                "function": "audience experiences compromise from inside",
            },
            "antagonist": {
                "dominant_feeling": "fascination",
                "function": "audience understands why corruption is tempting",
            }
        }
    }
    te = TargetExperience.model_validate(data)

    assert te.primary == "dread"
    assert te.primary_emotional_promise == "dread"
    assert te.progression == "wonder -> unease -> dread -> tragic catharsis"
    assert te.secondary == ["wonder", "longing", "moral discomfort", "grief"]
    assert te.secondary_palette == ["wonder", "longing", "moral discomfort", "grief"]
    assert te.avoid == ["cozy safety", "clean heroic triumph"]
    assert te.avoided_experiences == ["cozy safety", "clean heroic triumph"]
    assert te.emotional_trajectory is not None
    assert te.emotional_trajectory.pattern == "wonder -> unease -> dread -> tragic catharsis"
    assert te.emotional_trajectory.start == "wonder"
    assert te.emotional_trajectory.midpoint == "dread"
    assert te.emotional_trajectory.ending == "tragic catharsis"
    assert te.genre_emotion_stack is not None
    assert te.genre_emotion_stack["primary"].genre == "grimdark_fantasy"
    assert te.genre_emotion_stack["primary"].emotion == "dread"
    assert te.pov_experience_contracts is not None
    assert te.pov_experience_contracts["protagonist"].dominant_feeling == "moral pressure"


def test_analyzer_reports_genre_emotion_stack_primary_mismatch():
    blueprint_data = _blueprint_base_data()
    blueprint_data["identity"]["target_experience"] = {
        "primary_emotional_promise": "dread",
        "genre_emotion_stack": {
            "primary": {
                "genre": "grimdark_fantasy",
                "emotion": "wonder",
                "role": "mismatched",
            }
        }
    }
    blueprint = StoryBlueprint.model_validate(blueprint_data)
    diagnostics = analyze_structure(blueprint)

    by_rule = {d.rule: d for d in diagnostics}
    assert "target_experience.genre_emotion_stack.primary_mismatch" in by_rule
    diagnostic = by_rule["target_experience.genre_emotion_stack.primary_mismatch"]
    assert diagnostic.severity == DiagnosticSeverity.ERROR
    assert diagnostic.layer == DiagnosticLayer.TARGET_EXPERIENCE
    assert "identity.target_experience.primary_emotional_promise = dread" in diagnostic.evidence
    assert "genre_emotion_stack.primary.emotion = wonder" in diagnostic.evidence


def test_analyzer_reports_pov_contract_unknown_character():
    blueprint_data = _blueprint_base_data()
    blueprint_data["identity"]["target_experience"] = {
        "primary_emotional_promise": "dread",
        "pov_experience_contracts": {
            "antagonist": {
                "dominant_feeling": "fear",
                "function": "threat",
            }
        }
    }
    # Declared characters list in _blueprint_base_data only has "Protagonist" with role "protagonist"
    blueprint = StoryBlueprint.model_validate(blueprint_data)
    diagnostics = analyze_structure(blueprint)

    by_rule = {d.rule: d for d in diagnostics}
    assert "target_experience.pov_contract.unknown_character" in by_rule
    diagnostic = by_rule["target_experience.pov_contract.unknown_character"]
    assert diagnostic.severity == DiagnosticSeverity.WARNING
    assert diagnostic.layer == DiagnosticLayer.TARGET_EXPERIENCE
    assert "pov_experience_contracts key = antagonist" in diagnostic.evidence
