"""Deterministic composition and durable review-state reconciliation."""

from __future__ import annotations

import hashlib
from collections import defaultdict

from pydantic import BaseModel, ConfigDict

from auteur.blueprint import Genre
from auteur.identity import StoryIdentity

from .contracts import (
    CompositionTension,
    DimensionCategory,
    MappingCollision,
    MappingDisposition,
    MappingRecord,
    MappingReviewStatus,
    UnmappedRemainder,
    WorkingComposition,
)


class CompositionResolution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_identity: StoryIdentity
    mappings: tuple[MappingRecord, ...]
    collisions: tuple[MappingCollision, ...] = ()
    unmapped_remainder: tuple[UnmappedRemainder, ...] = ()
    tensions: tuple[CompositionTension, ...] = ()
    blocking_items: tuple[str, ...] = ()


def _stable_remainder_id(mapping_id: str, text: str) -> str:
    digest = hashlib.sha256(f"{mapping_id}|{text.strip()}".encode("utf-8")).hexdigest()[:16]
    return f"remainder:{digest}"


def _apply_mapping(identity: StoryIdentity, mapping: MappingRecord) -> StoryIdentity:
    if mapping.destination_field is None or mapping.proposed_value is None:
        return identity
    if mapping.destination_field == "story_type.genre":
        return identity.model_copy(
            update={"story_type": identity.story_type.model_copy(update={"genre": Genre(mapping.proposed_value)})}
        )
    if mapping.destination_field == "story_type.subgenres":
        values = list(identity.story_type.subgenres)
        if mapping.proposed_value not in values:
            values.append(mapping.proposed_value)
        return identity.model_copy(
            update={"story_type": identity.story_type.model_copy(update={"subgenres": values})}
        )
    if mapping.destination_field == "target_experience.primary":
        return identity.model_copy(
            update={
                "target_experience": identity.target_experience.model_copy(
                    update={"primary": mapping.proposed_value}
                )
            }
        )
    return identity


def _raw_blocking_items(
    mappings: tuple[MappingRecord, ...],
    collisions: tuple[MappingCollision, ...],
    remainders: tuple[UnmappedRemainder, ...],
) -> tuple[str, ...]:
    blocking: list[str] = []
    blocking.extend(
        f"collision:{collision.destination_field}"
        for collision in collisions
        if collision.requires_author_decision
    )
    if any(
        mapping.source_category.value == "PRIMARY_ENGINE"
        and mapping.destination_field is None
        for mapping in mappings
        if mapping.disposition in {
            MappingDisposition.REQUIRES_AUTHOR_DECISION,
            MappingDisposition.NOT_REPRESENTABLE_BY_CURRENT_DOMAIN,
        }
    ):
        blocking.append("primary_engine_mapping_required")
    blocking.extend(
        "unmapped_remainder_requires_acknowledgement"
        for remainder in remainders
        if remainder.blocks_acceptance and not remainder.acknowledged
    )
    return tuple(dict.fromkeys(blocking))


def compose_mappings(
    mappings: tuple[MappingRecord, ...],
    canonical_identity: StoryIdentity,
) -> CompositionResolution:
    """Compose proposals without consulting or mutating durable review state."""
    active = tuple(
        mapping
        for mapping in mappings
        if mapping.review_status not in {MappingReviewStatus.REJECTED, MappingReviewStatus.DEFERRED}
    )
    grouped: dict[str, list[MappingRecord]] = defaultdict(list)
    for mapping in active:
        if mapping.destination_field is not None and mapping.proposed_value is not None:
            grouped[mapping.destination_field].append(mapping)

    collisions: list[MappingCollision] = []
    candidate = canonical_identity
    for destination, group in grouped.items():
        values = {mapping.proposed_value for mapping in group}
        if len(values) > 1:
            collisions.append(
                MappingCollision(
                    destination_field=destination,
                    mapping_ids=tuple(mapping.mapping_id for mapping in group),
                    explanation="Multiple active mappings propose different values for one canonical field.",
                    requires_author_decision=True,
                )
            )
            continue
        candidate = _apply_mapping(candidate, group[0])

    remainders = tuple(
        UnmappedRemainder(
            remainder_id=_stable_remainder_id(mapping.mapping_id, text),
            dimension_id=mapping.source_dimension_id,
            text=text,
            blocks_acceptance=mapping.disposition
            in {
                MappingDisposition.NOT_REPRESENTABLE_BY_CURRENT_DOMAIN,
                MappingDisposition.REQUIRES_AUTHOR_DECISION,
            },
        )
        for mapping in active
        for text in mapping.unmapped_remainder
    )
    categories = {mapping.source_category for mapping in active}
    tensions: tuple[CompositionTension, ...] = ()
    relationship_engine_mappings = tuple(
        mapping
        for mapping in active
        if mapping.source_category
        in {DimensionCategory.PRIMARY_ENGINE, DimensionCategory.RELATIONSHIP_THEMATIC}
    )
    already_integrated = bool(relationship_engine_mappings) and all(
        (
            mapping.destination_field == "story_type.genre"
            and mapping.proposed_value == canonical_identity.story_type.genre.value
        )
        or (
            mapping.destination_field == "target_experience.primary"
            and mapping.proposed_value == canonical_identity.target_experience.primary
        )
        for mapping in relationship_engine_mappings
        if mapping.destination_field is not None and mapping.proposed_value is not None
    )
    if (
        {DimensionCategory.PRIMARY_ENGINE, DimensionCategory.RELATIONSHIP_THEMATIC} <= categories
        and not already_integrated
    ):
        tension_dimensions = tuple(
            mapping.source_dimension_id
            for mapping in active
            if mapping.source_category
            in {DimensionCategory.PRIMARY_ENGINE, DimensionCategory.RELATIONSHIP_THEMATIC}
        )
        tension_key = hashlib.sha256("|".join(tension_dimensions).encode("utf-8")).hexdigest()[:16]
        tensions = (
            CompositionTension(
                tension_id=f"tension:{tension_key}",
                dimension_ids=tension_dimensions,
                explanation="The mystery engine's fair inference contract may pull against relationship-driven uncertainty.",
                affected_decision_or_contract="story_identity.information-contract",
                blocks_acceptance=True,
            ),
        )
    return CompositionResolution(
        candidate_identity=candidate,
        mappings=mappings,
        collisions=tuple(collisions),
        unmapped_remainder=remainders,
        tensions=tensions,
        blocking_items=_raw_blocking_items(active, tuple(collisions), remainders),
    )


def reconcile_review_state(
    working_composition: WorkingComposition,
    resolution: CompositionResolution,
) -> CompositionResolution:
    """Reapply durable acknowledgements by stable remainder and tension IDs."""
    saved_remainders = {item.remainder_id: item for item in working_composition.unmapped_remainders}
    remainders = tuple(
        item.model_copy(
            update={
                "acknowledged": saved_remainders.get(item.remainder_id, item).acknowledged,
            }
        )
        for item in resolution.unmapped_remainder
    )
    saved_tensions = {item.tension_id: item for item in working_composition.tensions}
    tensions = tuple(
        item.model_copy(update={"acknowledged": saved_tensions.get(item.tension_id, item).acknowledged})
        for item in resolution.tensions
    )
    blocking = _raw_blocking_items(resolution.mappings, resolution.collisions, remainders)
    blocking = blocking + tuple(
        "tension_requires_acknowledgement"
        for tension in tensions
        if tension.blocks_acceptance and not tension.acknowledged
    )
    return resolution.model_copy(
        update={
            "unmapped_remainder": remainders,
            "tensions": tensions,
            "blocking_items": tuple(dict.fromkeys(blocking)),
        }
    )
