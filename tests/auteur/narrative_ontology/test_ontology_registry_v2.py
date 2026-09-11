"""Qualification tests for the Narrative Ontology V2 reconciliation."""

from __future__ import annotations

from auteur.narrative_ontology import (
    EntryKind,
    OntologyRegistry,
    SegmentKind,
    semantic_scope_name,
)
from auteur.narrative_ontology.core.narrative_concepts import ALL_CONCEPTS
from auteur.narrative_ontology.schema.ontology_types import (
    Relationship,
    ValidationRuleKind,
)
from auteur.narrative_ontology.validator import OntologyValidator


def test_registry_integrity_passes_for_packaged_specs() -> None:
    registry = OntologyRegistry()
    registry.assert_valid()


def test_historical_core_facade_remains_exactly_twelve_concepts() -> None:
    assert len(ALL_CONCEPTS) == 12
    assert "Character" in ALL_CONCEPTS
    assert "Beat" in ALL_CONCEPTS
    assert "StateTransition" not in ALL_CONCEPTS


def test_modern_semantic_vocabulary_is_available_through_registry() -> None:
    registry = OntologyRegistry()
    for concept_name in (
        "StructuralBeat",
        "NarrativeThread",
        "Event",
        "Fact",
        "State",
        "StateTransition",
        "CharacterRelationship",
    ):
        assert registry.get_concept(concept_name, "literary") is not None


def test_genre_without_extension_inherits_core_ontology() -> None:
    validator = OntologyValidator()
    assert validator.is_valid_genre("literary") is True
    assert validator.validate_concept("Character", "literary") is True
    assert validator.validate_concept("Event", "literary") is True
    assert validator.get_genre_specific_concepts("literary") == []
    assert validator.get_genre_themes("literary") == set()


def test_invalid_genre_still_fails_closed() -> None:
    validator = OntologyValidator()
    assert validator.is_valid_genre("not_a_real_auteur_genre") is False
    assert validator.validate_concept("Character", "not_a_real_auteur_genre") is False


def test_legacy_genre_names_resolve_without_python_registry() -> None:
    validator = OntologyValidator()
    assert validator.validate_concept("Cuckoldry Arc", "netorare") is True
    assert validator.validate_concept("Investigation Arc", "mystery") is True
    assert validator.validate_concept("Authority Arc", "gentlefemdom") is True
    assert validator.validate_concept("Surrender Beat", "gentlefemdom") is True
    assert validator.validate_concept("Trust Checkpoint", "gentlefemdom") is True


def test_many_to_one_cardinality_is_part_of_typed_schema() -> None:
    relation = Relationship(
        source_concept="Clue",
        target_concept="MysteryProblem",
        cardinality="many-to-one",
        description="Many clues may point to one mystery problem.",
    )
    assert relation.cardinality == "many-to-one"


def test_relation_type_is_vocabulary_not_story_assertion() -> None:
    registry = OntologyRegistry()
    relation_type = registry.get_relation_type("depends_on")
    assert relation_type is not None
    assert relation_type.id == "depends_on"
    assert not hasattr(relation_type, "authority")
    assert not hasattr(relation_type, "accepted_at")


def test_deterministic_semantic_rule_executes_by_named_executor() -> None:
    validator = OntologyValidator()
    ok, errors = validator.enforce_validation_rules(
        "StateTransition", {}, "literary"
    )
    assert ok is False
    assert errors

    ok, errors = validator.enforce_validation_rules(
        "StateTransition",
        {"from_state": "closed", "to_state": "open"},
        "literary",
    )
    assert ok is True
    assert errors == []


def test_legacy_free_text_rules_are_non_executable_by_default() -> None:
    validator = OntologyValidator()
    character = validator.get_concept("Character", "literary")
    assert character is not None
    assert character.validation_rules
    assert all(
        rule.kind == ValidationRuleKind.INTERPRETIVE_CRITERION
        for rule in character.validation_rules
    )
    ok, errors = validator.enforce_validation_rules("Character", {}, "literary")
    assert ok is True
    assert errors == []


def test_ontology_runtime_has_no_authority_mutation_surface() -> None:
    registry = OntologyRegistry()
    validator = OntologyValidator(registry)
    forbidden = {
        "accept",
        "accept_identity",
        "accept_structure",
        "accept_realization",
        "promote",
        "publish",
        "write_global_map",
    }
    assert forbidden.isdisjoint(set(dir(registry)))
    assert forbidden.isdisjoint(set(dir(validator)))


def test_medium_neutral_scope_vocabulary_is_compatibility_only() -> None:
    assert EntryKind.BOOK.value == "book"
    assert EntryKind.EPISODE.value == "episode"
    assert SegmentKind.CHAPTER.value == "chapter"
    assert semantic_scope_name("Book") == "entry"
    assert semantic_scope_name("chapter") == "segment"
    assert semantic_scope_name("scene") == "scene"
