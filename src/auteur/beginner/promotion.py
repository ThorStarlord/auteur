"""Promotion previews for the Beginner Workspace.

This module prepares a deterministic, noncanonical comparison.  The existing
authority service remains responsible for validating and applying any accepted
canonical change.
"""

from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict

from auteur.identity import StoryIdentity

from .composition import CompositionResolution
from .contracts import CompositionTension, MappingRecord, SemanticChange


class PromotionPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_identity: StoryIdentity
    candidate_identity: StoryIdentity
    semantic_changes: tuple[SemanticChange, ...] = ()
    mapping_records: tuple[MappingRecord, ...] = ()
    tensions: tuple[CompositionTension, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    blocking_items: tuple[str, ...] = ()
    downstream_impact: tuple[str, ...] = ()
    ready_to_accept: bool
    becomes_canonical: tuple[str, ...] = ()
    remains_downstream_guidance: tuple[str, ...] = ()
    preserved_as_provenance: tuple[str, ...] = ()
    unresolved_not_representable: tuple[str, ...] = ()


_SEMANTIC_IDENTITY_FIELDS = (
    "core_answer",
    "target_experience",
    "story_type",
    "central_engine",
    "architecture_preferences",
    "hard_constraints",
    "not_this",
    "open_questions",
    "characters",
    "genre_profile",
)


def identity_semantic_projection(identity: StoryIdentity) -> dict[str, object]:
    dumped = identity.model_dump(mode="json")
    return {field: dumped.get(field) for field in _SEMANTIC_IDENTITY_FIELDS}


def _semantic_changes(
    current: StoryIdentity,
    candidate: StoryIdentity,
    mappings: tuple[MappingRecord, ...],
) -> tuple[SemanticChange, ...]:
    current_projection = identity_semantic_projection(current)
    candidate_projection = identity_semantic_projection(candidate)
    changes: list[SemanticChange] = []
    for field in _SEMANTIC_IDENTITY_FIELDS:
        before = current_projection[field]
        after = candidate_projection[field]
        if before == after:
            continue
        changes.append(
            SemanticChange(
                destination_field=field,
                before=json.dumps(before, sort_keys=True, ensure_ascii=False),
                after=json.dumps(after, sort_keys=True, ensure_ascii=False),
                mapping_ids=tuple(
                    mapping.mapping_id
                    for mapping in mappings
                    if mapping.destination_field == field
                    or (
                        mapping.destination_field is not None
                        and mapping.destination_field.startswith(field + ".")
                    )
                ),
            )
        )
    return tuple(changes)


def build_promotion_preview(
    current_identity: StoryIdentity,
    resolution: CompositionResolution,
    existing_mapping_provenance: tuple[MappingRecord, ...],
) -> PromotionPreview:
    """Build a reviewable candidate without mutating canonical identity state."""
    changes = _semantic_changes(
        current_identity,
        resolution.candidate_identity,
        resolution.mappings,
    )
    unresolved = tuple(
        dict.fromkeys(
            [
                *(collision.destination_field for collision in resolution.collisions),
                *(item.remainder_id for item in resolution.unmapped_remainder),
                *(item.tension_id for item in resolution.tensions if not item.acknowledged),
            ]
        )
    )
    impact = (
        "Downstream guidance and artifacts may require reassessment if these semantic identity changes are accepted.",
    ) if changes else ()
    mapping_records: list[MappingRecord] = []
    seen_mapping_ids: set[str] = set()
    for mapping in (*existing_mapping_provenance, *resolution.mappings):
        if mapping.mapping_id not in seen_mapping_ids:
            seen_mapping_ids.add(mapping.mapping_id)
            mapping_records.append(mapping)
    return PromotionPreview(
        current_identity=current_identity,
        candidate_identity=resolution.candidate_identity,
        semantic_changes=changes,
        mapping_records=tuple(mapping_records),
        tensions=resolution.tensions,
        unresolved_items=unresolved,
        blocking_items=resolution.blocking_items,
        downstream_impact=impact,
        ready_to_accept=not resolution.blocking_items,
        becomes_canonical=tuple(change.destination_field for change in changes),
        remains_downstream_guidance=tuple(
            mapping.mapping_id
            for mapping in mapping_records
            if mapping.destination_field is None
        ),
        preserved_as_provenance=tuple(mapping.mapping_id for mapping in mapping_records),
        unresolved_not_representable=unresolved,
    )
