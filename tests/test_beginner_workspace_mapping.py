from auteur.blueprint import Genre, StoryMedium, StoryMode, TargetAudience, TargetExperience
from auteur.beginner.contracts import (
    DimensionCategory,
    DimensionOrigin,
    DimensionStatus,
    MappingDisposition,
    MappingReviewStatus,
    MappingStrength,
    MappingDomainContext,
    WorkingDimension,
)
from auteur.beginner.mapping import map_dimension, validate_author_override
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
