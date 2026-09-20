from auteur.blueprint import Genre, StoryMedium, StoryMode, TargetAudience, TargetExperience
from auteur.beginner import contracts
from auteur.beginner.contracts import (
    DimensionCategory,
    DimensionOrigin,
    DimensionStatus,
    MappingDisposition,
    MappingRecord,
    MappingStrength,
    MappingDomainContext,
    WorkingDimension,
    WorkingComposition,
    EvidenceClass,
)
from auteur.beginner.mapping import map_dimension, validate_author_override
from auteur.beginner.composition import compose_mappings, reconcile_review_state
from auteur.beginner.promotion import build_promotion_preview
from auteur.identity import HighLevelCentralEngine, StoryIdentity, StoryType


def empty_identity() -> StoryIdentity:
    return StoryIdentity(
        title="Mapping fixture",
        core_answer="A deterministic identity mapping fixture.",
        target_experience=TargetExperience(primary="dread", progression="rising", avoid=[]),
        story_type=StoryType(
            medium=StoryMedium.NOVEL,
            mode=StoryMode.OTHER,
            genre=Genre.OTHER,
            target_audience=TargetAudience.ADULT,
        ),
        central_engine=HighLevelCentralEngine(
            want="Solve the mystery.",
            resistance="Hidden truth.",
            conflict="Suspicion versus trust.",
            stakes="The relationship collapses.",
            change="The protagonist accepts uncertainty.",
        ),
    )


def mystery_dimension() -> WorkingDimension:
    return WorkingDimension(
        dimension_id="mystery-engine",
        category=DimensionCategory.PRIMARY_ENGINE,
        origin=DimensionOrigin.DETECTED_FROM_PACK,
        status=DimensionStatus.CONFIRMED,
        label="Mystery investigation",
        confirmed_by_author=True,
    )


def mystery_context() -> MappingDomainContext:
    return MappingDomainContext(
        vocabulary={
            "story_type.genre": ("mystery", "other"),
            "story_type.subgenres": ("superhero", "howdunit"),
            "target_experience.primary": ("dread", "jealous uncertainty"),
        }
    )


def test_direct_mystery_mapping_uses_existing_domain_vocabulary() -> None:
    mappings = map_dimension(mystery_dimension(), empty_identity(), mystery_context())

    assert len(mappings) == 1
    assert mappings[0].destination_field == "story_type.genre"
    assert mappings[0].proposed_value == "mystery"
    assert mappings[0].mapping_strength is MappingStrength.DIRECT_DOMAIN_MAPPING
    assert mappings[0].disposition is MappingDisposition.MAPS_TO_CANON
    assert mappings[0].source_dimension_id == "mystery-engine"


def test_supported_contribution_and_contextual_mapping_preserve_source_provenance() -> None:
    dimension = WorkingDimension(
        dimension_id="relationship-lens",
        category=DimensionCategory.RELATIONSHIP_THEMATIC,
        origin=DimensionOrigin.AUTHOR_DEFINED,
        status=DimensionStatus.CONFIRMED,
        label="Erotic betrayal tension",
        confirmed_by_author=True,
    )
    mappings = map_dimension(dimension, empty_identity(), mystery_context())

    assert mappings
    assert all(item.source_dimension_id == dimension.dimension_id for item in mappings)
    assert all(item.source_origin is DimensionOrigin.AUTHOR_DEFINED for item in mappings)
    assert any(item.destination_field == "target_experience.primary" for item in mappings)


def test_unsupported_override_is_not_in_candidate_mapping() -> None:
    mapping = map_dimension(mystery_dimension(), empty_identity(), mystery_context())[0]
    result = validate_author_override(mapping, "invented-canonical-value", mystery_context().vocabulary)

    assert result.valid is False
    assert result.diagnostic == "INVALID_FOR_CURRENT_VOCABULARY"
    assert result.preflight_result == "rejected"
    assert result.final_result is None


def nonrepresentable_mapping() -> MappingRecord:
    dimension = WorkingDimension(
        dimension_id="unsupported-lens",
        category=DimensionCategory.EMOTIONAL_AESTHETIC,
        origin=DimensionOrigin.AUTHOR_DEFINED,
        status=DimensionStatus.CONFIRMED,
        label="Unrepresented aesthetic",
        confirmed_by_author=True,
    )
    return MappingRecord(
        mapping_id="mapping:unsupported-lens:context",
        source_dimension_id=dimension.dimension_id,
        source_category=dimension.category,
        source_origin=dimension.origin,
        mapping_strength=MappingStrength.CONTEXTUAL_INFLUENCE,
        evidence_class=contracts.EvidenceClass.AUTHOR_CONFIRMED_DECISION,
        disposition=MappingDisposition.NOT_REPRESENTABLE_BY_CURRENT_DOMAIN,
        rationale="No current canonical field represents this lens.",
        unmapped_remainder=(dimension.label,),
    )


def composition_with_remainder(remainder_id: str, acknowledged: bool) -> WorkingComposition:
    from auteur.beginner.contracts import UnmappedRemainder

    return WorkingComposition(
        workspace_id="w1",
        composition_id="c1",
        schema_version=1,
        dimensions=(),
        unmapped_remainders=(
            UnmappedRemainder(
                remainder_id=remainder_id,
                dimension_id="unsupported-lens",
                text="Unrepresented aesthetic",
                acknowledged=acknowledged,
                blocks_acceptance=True,
            ),
        ),
    )


def test_acknowledged_nonrepresentable_remainder_does_not_block() -> None:
    raw = compose_mappings((nonrepresentable_mapping(),), empty_identity())
    composition = composition_with_remainder(raw.unmapped_remainder[0].remainder_id, acknowledged=True)
    result = reconcile_review_state(composition, raw)

    assert result.blocking_items == ()
    assert result.unmapped_remainder[0].acknowledged is True


def test_unresolved_primary_engine_blocks_identity_acceptance() -> None:
    mapping = nonrepresentable_mapping().model_copy(
        update={
            "source_dimension_id": "primary-engine",
            "source_category": DimensionCategory.PRIMARY_ENGINE,
            "disposition": MappingDisposition.REQUIRES_AUTHOR_DECISION,
        }
    )
    result = compose_mappings((mapping,), empty_identity())

    assert "primary_engine_mapping_required" in result.blocking_items


def test_conflicting_values_preserve_all_mappings_and_report_collision() -> None:
    first = map_dimension(mystery_dimension(), empty_identity(), mystery_context())[0]
    second = first.model_copy(update={"mapping_id": "mapping:alternative", "proposed_value": "other"})
    result = compose_mappings((first, second), empty_identity())

    assert result.mappings == (first, second)
    assert result.collisions[0].mapping_ids == (first.mapping_id, second.mapping_id)
    assert result.blocking_items


def relationship_dimension() -> WorkingDimension:
    return WorkingDimension(
        dimension_id="relationship-lens",
        category=DimensionCategory.RELATIONSHIP_THEMATIC,
        origin=DimensionOrigin.AUTHOR_DEFINED,
        status=DimensionStatus.CONFIRMED,
        label="Relationship betrayal tension",
        confirmed_by_author=True,
    )


def test_preview_blocks_only_materially_unresolved_identity_mapping() -> None:
    preview = build_promotion_preview(empty_identity(), compose_mappings((nonrepresentable_mapping(),), empty_identity()), ())

    assert preview.ready_to_accept is False
    assert "unmapped_remainder_requires_acknowledgement" in preview.blocking_items


def test_preview_links_semantic_change_to_mapping_and_reports_impact() -> None:
    mapping = map_dimension(mystery_dimension(), empty_identity(), mystery_context())[0]
    resolution = compose_mappings((mapping,), empty_identity())

    preview = build_promotion_preview(empty_identity(), resolution, ())

    assert preview.semantic_changes[0].destination_field == "story_type.genre"
    assert preview.semantic_changes[0].after == "mystery"
    assert preview.semantic_changes[0].mapping_ids == (mapping.mapping_id,)
    assert preview.downstream_impact


def test_pack_and_provenance_context_alone_has_no_semantic_diff() -> None:
    mapping = MappingRecord(
        mapping_id="mapping:context-only",
        source_dimension_id="context-lens",
        source_category=DimensionCategory.EMOTIONAL_AESTHETIC,
        source_origin=DimensionOrigin.DETECTED_FROM_PACK,
        mapping_strength=MappingStrength.CONTEXTUAL_INFLUENCE,
        evidence_class=EvidenceClass.PACK_METADATA,
        disposition=MappingDisposition.GUIDANCE_CONTEXT,
        rationale="This pack contributes explanatory context only.",
    )
    resolution = compose_mappings((mapping,), empty_identity())

    preview = build_promotion_preview(empty_identity(), resolution, (mapping,))

    assert preview.semantic_changes == ()
    assert preview.downstream_impact == ()
    assert preview.ready_to_accept is True


def test_acknowledged_tension_is_nonblocking_after_recomputation() -> None:
    relationship_mapping = map_dimension(relationship_dimension(), empty_identity(), mystery_context())[0]
    raw = compose_mappings(
        tuple(map_dimension(mystery_dimension(), empty_identity(), mystery_context())) + (relationship_mapping,),
        empty_identity(),
    )
    composition = WorkingComposition(
        workspace_id="w1",
        composition_id="c1",
        schema_version=1,
        dimensions=(),
        tensions=(raw.tensions[0].model_copy(update={"acknowledged": True}),),
    )
    reconciled = reconcile_review_state(composition, raw)
    preview = build_promotion_preview(empty_identity(), reconciled, ())

    assert reconciled.tensions[0].acknowledged is True
    assert "tension_requires_acknowledgement" not in preview.blocking_items
