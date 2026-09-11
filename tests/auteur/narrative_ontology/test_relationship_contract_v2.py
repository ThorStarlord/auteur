"""Contract tests for relationship-domain reconciliation."""

from auteur.narrative_ontology import OntologyRegistry


def _cardinality(source, target: str) -> str:
    matches = [
        relation.cardinality
        for relation in source.relationships
        if relation.target_concept == target
    ]
    assert len(matches) == 1
    return matches[0]


def test_canonical_setup_payoff_is_many_to_many_in_both_directions() -> None:
    registry = OntologyRegistry()
    setup = registry.get_concept("Setup", "literary")
    payoff = registry.get_concept("Payoff", "literary")
    assert setup is not None
    assert payoff is not None
    assert _cardinality(setup, "Payoff") == "many-to-many"
    assert _cardinality(payoff, "Setup") == "many-to-many"


def test_relationship_domains_are_not_collapsed_into_one_runtime_type() -> None:
    registry = OntologyRegistry()
    legacy = registry.get_concept("Relationship", "literary")
    character_relationship = registry.get_concept("CharacterRelationship", "literary")
    relation_type = registry.get_relation_type("depends_on")

    assert legacy is not None
    assert character_relationship is not None
    assert relation_type is not None
    assert character_relationship.name != relation_type.id
    assert "Relationship" in character_relationship.parent_concepts


def test_structural_beat_and_realization_event_are_distinct_concepts() -> None:
    registry = OntologyRegistry()
    structural_beat = registry.get_concept("StructuralBeat", "literary")
    event = registry.get_concept("Event", "literary")
    transition = registry.get_concept("StateTransition", "literary")

    assert structural_beat is not None
    assert event is not None
    assert transition is not None
    assert structural_beat.name != event.name
    assert event.name != transition.name
    assert any(
        relation.target_concept == "Event"
        and relation.relation_type == "may_be_realized_as"
        for relation in structural_beat.relationships
    )
    assert any(
        relation.target_concept == "StateTransition"
        and relation.relation_type == "may_produce"
        for relation in event.relationships
    )
