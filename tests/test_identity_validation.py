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
