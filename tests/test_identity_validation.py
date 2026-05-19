import pytest
from pydantic import ValidationError
from auteur.identity import StoryIdentity

def test_story_identity_valid_minimal():
    data = {
        "title": "The Fallen Angel",
        "core_answer": "A tragic story about an angel who falls in love with a mortal and loses their wings.",
        "central_engine": {
            "want": "The angel wants to save the mortal from a terminal curse.",
            "resistance": "The curse is woven into the mortal's soul by the gods.",
            "conflict": "Saving them requires absorbing the curse, losing divinity, and becoming mortal.",
            "stakes": "The angel will die a human death if they fail, or live a mortal life if they succeed.",
            "change": "The angel changes from an aloof divine observer to a deeply feeling mortal.",
        }
    }
    
    identity = StoryIdentity.model_validate(data)
    assert identity.title == "The Fallen Angel"
    assert identity.core_answer.startswith("A tragic story")
    assert identity.central_engine.want.startswith("The angel wants")
    assert identity.story_type.genre.value == "grimdark_fantasy" # default
    assert identity.story_type.medium.value == "novel" # default
    assert identity.story_type.mode.value == "tragic" # default
    assert identity.recommendation_mode.value == "opinionated"
    assert identity.best_basis.value == "genre_aligned"


def test_story_identity_accepts_opinionated_recommendation_metadata(tmp_path):
    data = {
        "title": "The Fallen Angel",
        "core_answer": "A tragic romantasy about an angel who becomes mortal to save a cursed beloved.",
        "central_engine": {
            "want": "The angel wants to save the mortal from a terminal curse.",
            "resistance": "The curse is protected by divine law and enforced by the angel's former kin.",
            "conflict": "Saving the beloved requires breaking heaven's order and becoming the thing heaven condemns.",
            "stakes": "The mortal dies if the angel obeys, but heaven fractures if the angel rebels.",
            "change": "The angel changes from obedient guardian to exiled mortal lover.",
        },
        "recommendation_mode": "opinionated",
        "best_basis": "genre_aligned",
        "why_this_is_best": "The romantasy premise is strongest when genre promise, forbidden intimacy, and sacrificial transformation pressure the same ending.",
        "rejected_directions": [
            "A neutral portal fantasy would weaken the romantic genre promise.",
            "A detached theological parable would underuse the author-provided love story.",
        ],
        "author_overrides": [
            "Keep the ending tragic rather than redemptive.",
        ],
    }

    identity = StoryIdentity.model_validate(data)
    assert identity.why_this_is_best.startswith("The romantasy premise")
    assert identity.rejected_directions == [
        "A neutral portal fantasy would weaken the romantic genre promise.",
        "A detached theological parable would underuse the author-provided love story.",
    ]
    assert identity.author_overrides == ["Keep the ending tragic rather than redemptive."]

    identity_path = tmp_path / "story_identity.yaml"
    identity.to_yaml(identity_path)
    round_tripped = StoryIdentity.from_yaml(identity_path)

    assert round_tripped.recommendation_mode.value == "opinionated"
    assert round_tripped.best_basis.value == "genre_aligned"
    assert round_tripped.why_this_is_best == identity.why_this_is_best
    assert round_tripped.rejected_directions == identity.rejected_directions


def test_story_identity_invalid_missing_fields():
    # Missing central_engine
    with pytest.raises(ValidationError):
        StoryIdentity.model_validate({
            "title": "Title",
            "core_answer": "Answer",
        })

    # Missing title
    with pytest.raises(ValidationError):
        StoryIdentity.model_validate({
            "core_answer": "Answer",
            "central_engine": {
                "want": "want",
                "resistance": "resistance",
                "conflict": "conflict",
                "stakes": "stakes",
                "change": "change",
            }
        })

    # Empty want
    with pytest.raises(ValidationError):
        StoryIdentity.model_validate({
            "title": "Title",
            "core_answer": "Answer",
            "central_engine": {
                "want": "",
                "resistance": "resistance",
                "conflict": "conflict",
                "stakes": "stakes",
                "change": "change",
            }
        })


def test_story_identity_includes_genre_contract_snapshot(tmp_path):
    data = {
        "title": "Grimdark Journey",
        "core_answer": "A grim story about survival.",
        "central_engine": {
            "want": "Survive the plague.",
            "resistance": "The city is quarantined.",
            "conflict": "Supplies are running out.",
            "stakes": "Death by starvation or plague.",
            "change": "Learns to rely on others.",
        },
        "story_type": {
            "genre": "grimdark_fantasy",
        }
    }
    
    identity = StoryIdentity.model_validate(data)
    assert identity.genre_contract_snapshot is not None
    assert identity.genre_contract_snapshot.genre_id.value == "grimdark_fantasy"
    assert "hopeful ending" in identity.genre_contract_snapshot.forbidden_mismatches

    data["story_type"]["genre"] = "romance"
    identity_romance = StoryIdentity.model_validate(data)
    assert identity_romance.genre_contract_snapshot.genre_id.value == "romance"
    assert "tragic ending" in identity_romance.genre_contract_snapshot.forbidden_mismatches

    identity_path = tmp_path / "story_identity.yaml"
    identity_romance.to_yaml(identity_path)
    
    round_tripped = StoryIdentity.from_yaml(identity_path)
    assert round_tripped.genre_contract_snapshot is not None
    assert round_tripped.genre_contract_snapshot.genre_id.value == "romance"
    assert "tragic ending" in round_tripped.genre_contract_snapshot.forbidden_mismatches


def test_story_identity_want_change_duplicate_fails():
    data = {
        "title": "Duplicate Want Change",
        "core_answer": "A tragic story.",
        "central_engine": {
            "want": "The hero wants to find the cure.",
            "resistance": "The dragon blocks the path.",
            "conflict": "Fighting the dragon.",
            "stakes": "Death or cure.",
            "change": "The hero wants to find the cure.",  # Duplicate!
        }
    }
    identity = StoryIdentity.model_validate(data)
    diagnostics = identity.validate_identity()
    
    assert len(diagnostics) == 1
    assert diagnostics[0].severity.value == "error"
    assert diagnostics[0].rule == "identity.central_engine.change_duplicates_want"


def test_story_identity_forbidden_ending_tone_fails():
    # Romance forbids tragic endings
    data = {
        "title": "Tragic Romance",
        "core_answer": "A sad story.",
        "central_engine": {
            "want": "The lover wants to be with their partner.",
            "resistance": "Distance.",
            "conflict": "Relational differences.",
            "stakes": "Loneliness.",
            "change": "They learn to accept love.",
        },
        "story_type": {
            "genre": "romance",
            "mode": "tragic",  # Implies tragic ending
        }
    }
    identity = StoryIdentity.model_validate(data)
    diagnostics = identity.validate_identity()
    
    errors = [d for d in diagnostics if d.severity.value == "error"]
    assert len(errors) == 1
    assert errors[0].rule == "identity.genre.forbidden_mismatch.ending_tone"


def test_story_identity_forbidden_ending_tone_with_override_warns():
    data = {
        "title": "Tragic Romance Override",
        "core_answer": "A sad story.",
        "central_engine": {
            "want": "The lover wants to be with their partner.",
            "resistance": "Distance.",
            "conflict": "Relational differences.",
            "stakes": "Loneliness.",
            "change": "They learn to accept love.",
        },
        "story_type": {
            "genre": "romance",
            "mode": "tragic",
        },
        "author_overrides": ["ending_tone"]
    }
    identity = StoryIdentity.model_validate(data)
    diagnostics = identity.validate_identity()
    
    errors = [d for d in diagnostics if d.severity.value == "error"]
    warnings = [d for d in diagnostics if d.severity.value == "warning"]
    
    assert len(errors) == 0
    assert len(warnings) == 1
    assert warnings[0].rule == "identity.genre.forbidden_mismatch.ending_tone.override"


def test_story_identity_avoided_experience_clash_fails():
    data = {
        "title": "Clashing Experiences",
        "core_answer": "A story about hope.",
        "central_engine": {
            "want": "Find hope.",
            "resistance": "Despair.",
            "conflict": "Struggle.",
            "stakes": "Life.",
            "change": "Transformed.",
        },
        "target_experience": {
            "primary": "hope",
            "progression": "rising -> climax -> peace",
            "avoid": ["hope", "peace"]
        }
    }
    identity = StoryIdentity.model_validate(data)
    diagnostics = identity.validate_identity()
    
    errors = [d for d in diagnostics if d.severity.value == "error"]
    rules = [d.rule for d in errors]
    assert "identity.target_experience.avoid_clashes_with_primary" in rules
    assert "identity.target_experience.avoid_clashes_with_progression" in rules


def test_cli_identity_validation_and_compile_failures(tmp_path):
    identity_yaml_path = tmp_path / "story_identity_invalid.yaml"
    blueprint_yaml_path = tmp_path / "blueprint.yaml"
    
    # Create invalid identity data (duplicate want/change)
    identity_data = {
        "title": "Invalid Story",
        "core_answer": "A tragic political drama.",
        "central_engine": {
            "want": "The king wants to preserve the trade routes.",
            "resistance": "The Sea Peoples disrupt the shipping lanes.",
            "conflict": "Fighting them.",
            "stakes": "Collapse.",
            "change": "The king wants to preserve the trade routes.",  # Duplicate!
        }
    }
    
    import yaml
    identity_yaml_path.write_text(yaml.safe_dump(identity_data), encoding="utf-8")
    
    # 1. Test validate command returns error code 1
    from auteur.cli import main
    exit_code_validate = main(["identity", "validate", str(identity_yaml_path)])
    assert exit_code_validate == 1
    
    # 2. Test compile command aborts and returns error code 1
    exit_code_compile = main(["identity", "compile", str(identity_yaml_path), "--output", str(blueprint_yaml_path)])
    assert exit_code_compile == 1
    assert not blueprint_yaml_path.exists()


def test_story_identity_runway_validation_and_overrides():
    data = {
        "title": "Short Netorare Story",
        "core_answer": "A brief netorare tale.",
        "central_engine": {
            "want": "The protagonist wants to keep trust.",
            "resistance": "The intruder.",
            "conflict": "Trust is eroded.",
            "stakes": "Loss of relationship.",
            "change": "Protagonist accepts the loss.",
        },
        "story_type": {
            "genre": "netorare",
            "medium": "short_story",  # short_story resolves to length_class: short_story
        }
    }
    
    identity = StoryIdentity.model_validate(data)
    # netorare minimum viable length is novella.
    # Since length class resolved is short_story, it should fail.
    diagnostics = identity.validate_identity()
    errors = [d for d in diagnostics if d.severity.value == "error"]
    assert len(errors) == 1
    assert errors[0].rule == "identity.genre.scope.runway_mismatch"
    
    # Now let's try with override
    data["author_overrides"] = ["runway_compression"]
    identity_overridden = StoryIdentity.model_validate(data)
    diagnostics_overridden = identity_overridden.validate_identity()
    errors_overridden = [d for d in diagnostics_overridden if d.severity.value == "error"]
    warnings_overridden = [d for d in diagnostics_overridden if d.severity.value == "warning"]
    
    assert len(errors_overridden) == 0
    assert len(warnings_overridden) == 1
    assert warnings_overridden[0].rule == "identity.genre.scope.runway_mismatch.override"

