"""Promotion previews for the Beginner Workspace.

This module prepares a deterministic, noncanonical comparison.  The existing
authority service remains responsible for validating and applying any accepted
canonical change.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from auteur.identity import StoryIdentity

from .composition import CompositionResolution
from .contracts import MappingRecord, SemanticChange


class PromotionPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_identity: StoryIdentity
    candidate_identity: StoryIdentity
    semantic_changes: tuple[SemanticChange, ...] = ()
    mapping_records: tuple[MappingRecord, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    blocking_items: tuple[str, ...] = ()
    downstream_impact: tuple[str, ...] = ()
    ready_to_accept: bool


def _semantic_changes(
    current: StoryIdentity,
    candidate: StoryIdentity,
    mappings: tuple[MappingRecord, ...],
) -> tuple[SemanticChange, ...]:
    fields = (
        ("story_type.genre", current.story_type.genre.value, candidate.story_type.genre.value),
        ("story_type.subgenres", tuple(current.story_type.subgenres), tuple(candidate.story_type.subgenres)),
        ("target_experience.primary", current.target_experience.primary, candidate.target_experience.primary),
        ("central_engine.conflict", current.central_engine.conflict, candidate.central_engine.conflict),
    )
    changes: list[SemanticChange] = []
    for field, before, after in fields:
        if before == after:
            continue
        changes.append(
            SemanticChange(
                destination_field=field,
                before=str(before),
                after=str(after),
                mapping_ids=tuple(
                    mapping.mapping_id
                    for mapping in mappings
                    if mapping.destination_field == field
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
        unresolved_items=unresolved,
        blocking_items=resolution.blocking_items,
        downstream_impact=impact,
        ready_to_accept=not resolution.blocking_items,
    )
