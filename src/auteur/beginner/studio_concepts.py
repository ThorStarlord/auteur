"""Provisional, project-scoped narrative concepts as noncanonical working notes.

A provisional concept is useful within one working story and remains reviewable
across sessions. It never becomes a shared ontology definition until a separate
author-reviewed ontology change accepts it.
"""
from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .studio_store import CanvasStore, WorkingCanvas

_CONCEPT_GROUP = "provisional-concepts"


class ProvisionalNarrativeConcept(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=120)
    definition: str = Field(min_length=1, max_length=1200)
    motivating_story_use: str = Field(min_length=1, max_length=1200)
    why_existing_concepts_insufficient: str = Field(min_length=1, max_length=1200)
    related_concepts: list[str] = Field(default_factory=list, max_length=16)
    proposed_relations: list[str] = Field(default_factory=list, max_length=16)
    compatibility_concerns: list[str] = Field(default_factory=list, max_length=16)
    status: Literal["provisional"] = "provisional"


def _concept_item(concept: ProvisionalNarrativeConcept) -> tuple[dict, dict]:
    content = json.dumps(
        concept.model_dump(mode="json"), sort_keys=True, ensure_ascii=False,
    )
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    item = {
        "id": f"concept-{digest[:16]}",
        "kind": "note",
        "title": concept.name,
        "group": _CONCEPT_GROUP,
        "content": content,
    }
    position = {
        "x": 40 + int(digest[:4], 16) % 1200,
        "y": 40 + int(digest[4:8], 16) % 900,
    }
    return item, position


def record_provisional_concept(
    store: CanvasStore,
    concept: ProvisionalNarrativeConcept,
    *,
    expected_revision: int,
    command_id: str,
) -> WorkingCanvas:
    """Persist one provisional concept through the existing working-note store."""
    if not isinstance(concept, ProvisionalNarrativeConcept):
        concept = ProvisionalNarrativeConcept.model_validate(concept)
    item, position = _concept_item(concept)
    return store.apply(
        "create-item",
        expected_revision=expected_revision,
        command_id=command_id,
        payload={"item": item, "position": position},
    )


def list_provisional_concepts(store: CanvasStore) -> list[ProvisionalNarrativeConcept]:
    """Read project-level provisional concepts; never shared ontology."""
    concepts = [
        ProvisionalNarrativeConcept.model_validate_json(item.content)
        for item in store.load().items
        if item.group == _CONCEPT_GROUP
    ]
    return sorted(concepts, key=lambda concept: concept.name)
