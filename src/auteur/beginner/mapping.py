"""Deterministic per-dimension mapping proposals over existing Identity vocabulary."""

from __future__ import annotations

from collections.abc import Mapping

from auteur.identity import StoryIdentity

from .contracts import (
    AuthorOverride,
    DimensionCategory,
    MappingDisposition,
    MappingDomainContext,
    MappingRecord,
    MappingReviewStatus,
    MappingStrength,
    EvidenceClass,
    OverrideValidationResult,
    WorkingDimension,
)


def _candidate_for(
    dimension: WorkingDimension,
    vocabulary: Mapping[str, tuple[str, ...]],
) -> tuple[str, str, MappingStrength, MappingDisposition] | None:
    candidates = {
        DimensionCategory.PRIMARY_ENGINE: ("story_type.genre", "mystery", MappingStrength.DIRECT_DOMAIN_MAPPING, MappingDisposition.MAPS_TO_CANON),
        DimensionCategory.SETTING_WORLD: ("story_type.subgenres", "superhero", MappingStrength.SUPPORTED_CONTRIBUTION, MappingDisposition.CONTRIBUTES_TO_CANON),
        DimensionCategory.RELATIONSHIP_THEMATIC: ("target_experience.primary", "jealous uncertainty", MappingStrength.SUPPORTED_CONTRIBUTION, MappingDisposition.CONTRIBUTES_TO_CANON),
        DimensionCategory.EMOTIONAL_AESTHETIC: ("target_experience.primary", "jealous uncertainty", MappingStrength.SUPPORTED_CONTRIBUTION, MappingDisposition.CONTRIBUTES_TO_CANON),
    }
    candidate = candidates.get(dimension.category)
    if candidate is None:
        return None
    destination, value, strength, disposition = candidate
    if destination not in vocabulary or value not in vocabulary[destination]:
        return None
    return candidate


def map_dimension(
    dimension: WorkingDimension,
    canonical_identity: StoryIdentity,
    domain_context: MappingDomainContext,
) -> tuple[MappingRecord, ...]:
    """Return only mappings whose field and value are in the supplied vocabulary."""
    del canonical_identity
    candidate = _candidate_for(dimension, domain_context.vocabulary)
    if candidate is None:
        return (
            MappingRecord(
                mapping_id=f"mapping:{dimension.dimension_id}:context",
                source_dimension_id=dimension.dimension_id,
                source_category=dimension.category,
                source_origin=dimension.origin,
                source_provenance=dimension.source_provenance,
                mapping_strength=MappingStrength.CONTEXTUAL_INFLUENCE,
                evidence_class=EvidenceClass.AUTHOR_CONFIRMED_DECISION,
                disposition=MappingDisposition.GUIDANCE_CONTEXT,
                review_status=MappingReviewStatus.PROPOSED,
                rationale="The current canonical vocabulary has no legal destination for this dimension.",
                unmapped_remainder=(dimension.label,),
            ),
        )

    destination, value, strength, disposition = candidate
    return (
        MappingRecord(
            mapping_id=f"mapping:{dimension.dimension_id}:{destination}",
            source_dimension_id=dimension.dimension_id,
            source_category=dimension.category,
            source_origin=dimension.origin,
            source_provenance=dimension.source_provenance,
            destination_field=destination,
            proposed_value=value,
            mapping_strength=strength,
            evidence_class=(
                EvidenceClass.AUTHOR_CONFIRMED_DECISION
                if dimension.origin.value.startswith("AUTHOR")
                else EvidenceClass.CURATED_COMPOSITION_RULE
            ),
            disposition=disposition,
            review_status=MappingReviewStatus.PROPOSED,
            rationale=f"The confirmed dimension contributes {value!r} to {destination}.",
        ),
    )


def validate_author_override(
    mapping: MappingRecord,
    override: str | AuthorOverride,
    canonical_vocabulary: Mapping[str, tuple[str, ...]],
) -> OverrideValidationResult:
    """Preflight an author override without deciding final canonical validity."""
    replacement = override if isinstance(override, str) else override.replacement_value
    allowed = (
        mapping.destination_field is not None
        and replacement in canonical_vocabulary.get(mapping.destination_field, ())
    )
    if not allowed:
        return OverrideValidationResult(
            preflight_result="rejected",
            final_result=None,
            valid=False,
            diagnostic="INVALID_FOR_CURRENT_VOCABULARY",
        )
    return OverrideValidationResult(
        preflight_result="accepted",
        final_result=None,
        valid=True,
        accepted_value=replacement,
    )
