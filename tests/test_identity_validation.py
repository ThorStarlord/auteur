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
