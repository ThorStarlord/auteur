from __future__ import annotations

import pytest
import yaml
from pydantic import ValidationError

from auteur.relations.models import RelationChangeSet, RelationMap, RelationState


def test_valid_relation_map_round_trips_through_yaml() -> None:
    relation_map = RelationMap(
        relations=[
            RelationState(
                id="elena_marcus",
                from_character="Elena",
                to_character="Marcus",
                public_role="wife",
                private_truth="exhausted loyalty",
                trust=62,
                resentment=41,
                dependency=73,
                attraction=28,
                fear=12,
                obligation=85,
                last_changed_in="chapter_03",
            )
        ]
    )

    payload = yaml.safe_load(yaml.safe_dump(relation_map.model_dump(mode="json")))

    parsed = RelationMap.model_validate(payload)
    assert parsed.relations[0].id == "elena_marcus"
    assert parsed.relations[0].trust == 62


def test_relation_metric_bounds_are_enforced() -> None:
    with pytest.raises(ValidationError):
        RelationState(
            id="elena_marcus",
            from_character="Elena",
            to_character="Marcus",
            trust=101,
        )


def test_relation_map_rejects_duplicate_ids() -> None:
    relation = {
        "id": "elena_marcus",
        "from_character": "Elena",
        "to_character": "Marcus",
    }

    with pytest.raises(ValidationError):
        RelationMap.model_validate({"relations": [relation, relation]})


def test_relation_change_set_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        RelationChangeSet.model_validate(
            {
                "chapter": 3,
                "relation_changes": [
                    {
                        "relation": "elena_marcus",
                        "trust": 8,
                        "reason": "Marcus protects Elena publicly.",
                        "unexpected": True,
                    }
                ],
            }
        )

