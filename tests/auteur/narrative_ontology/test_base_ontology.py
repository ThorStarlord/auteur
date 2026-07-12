"""Tests for base narrative concepts (Task 2).

Tests that all 11+ core narrative concepts are properly defined with:
- Correct definitions
- Relationships to other concepts
- Validation rules
- Cardinality constraints
"""

import pytest
from auteur.narrative_ontology.core.narrative_concepts import (
    CHARACTER,
    ARC,
    THEME,
    GOAL,
    CONFLICT,
    PAYOFF,
    SYMBOL,
    RELATIONSHIP_CONCEPT,
    BEAT,
    SETUP,
    REVELATION,
    REVERSAL,
    ALL_CONCEPTS,
    get_concept,
)
from auteur.narrative_ontology.schema.ontology_types import Concept


class TestCharacterConcept:
    """Test the Character concept definition."""

    def test_character_exists(self):
        """Test that Character concept is defined."""
        assert CHARACTER is not None
        assert isinstance(CHARACTER, Concept)

    def test_character_name(self):
        """Test Character concept has correct name."""
        assert CHARACTER.name == "Character"

    def test_character_definition(self):
        """Test Character concept has non-empty definition."""
        assert CHARACTER.definition
        assert len(CHARACTER.definition) > 0
        assert "entity" in CHARACTER.definition.lower() or "agency" in CHARACTER.definition.lower()

    def test_character_has_relationships(self):
        """Test Character has relationships defined."""
        assert len(CHARACTER.relationships) > 0

    def test_character_has_validation_rules(self):
        """Test Character has validation rules."""
        assert len(CHARACTER.validation_rules) > 0

    def test_character_goal_relationship(self):
        """Test Character has relationship to Goal."""
        goal_rels = [r for r in CHARACTER.relationships if r.target_concept == "Goal"]
        assert len(goal_rels) > 0

    def test_character_arc_relationship(self):
        """Test Character has relationship to Arc."""
        arc_rels = [r for r in CHARACTER.relationships if r.target_concept == "Arc"]
        assert len(arc_rels) > 0

    def test_character_validation_rule_ids(self):
        """Test Character validation rules have correct rule IDs."""
        rule_ids = [r.rule_id for r in CHARACTER.validation_rules]
        assert "character_must_have_identity" in rule_ids
        assert "character_may_appear_in_multiple_arcs" in rule_ids


class TestArcConcept:
    """Test the Arc concept definition."""

    def test_arc_exists(self):
        """Test that Arc concept is defined."""
        assert ARC is not None
        assert isinstance(ARC, Concept)

    def test_arc_name(self):
        """Test Arc concept has correct name."""
        assert ARC.name == "Arc"

    def test_arc_definition(self):
        """Test Arc concept has non-empty definition."""
        assert ARC.definition
        assert "progression" in ARC.definition.lower()

    def test_arc_must_contain_beats(self):
        """Test Arc has required relationship to Beat."""
        beat_rels = [r for r in ARC.relationships if r.target_concept == "Beat"]
        assert len(beat_rels) > 0
        assert beat_rels[0].required is True

    def test_arc_has_validation_rules(self):
        """Test Arc has validation rules."""
        assert len(ARC.validation_rules) > 0
        rule_ids = [r.rule_id for r in ARC.validation_rules]
        assert "arc_must_have_start" in rule_ids
        assert "arc_must_have_end" in rule_ids

    def test_arc_character_relationship(self):
        """Test Arc has relationship to Character."""
        char_rels = [r for r in ARC.relationships if r.target_concept == "Character"]
        assert len(char_rels) > 0


class TestThemeConcept:
    """Test the Theme concept definition."""

    def test_theme_exists(self):
        """Test that Theme concept is defined."""
        assert THEME is not None
        assert isinstance(THEME, Concept)

    def test_theme_definition(self):
        """Test Theme has appropriate definition."""
        assert THEME.definition
        assert "abstract" in THEME.definition.lower()

    def test_theme_not_require_resolution_rule(self):
        """Test Theme has rule about not requiring resolution."""
        rule_ids = [r.rule_id for r in THEME.validation_rules]
        assert any("not_require" in rid or "may_not" in rid for rid in rule_ids)

    def test_theme_influences_arcs(self):
        """Test Theme has influence relationship to Arc."""
        arc_rels = [r for r in THEME.relationships if r.target_concept == "Arc"]
        assert len(arc_rels) > 0


class TestGoalConcept:
    """Test the Goal concept definition."""

    def test_goal_exists(self):
        """Test that Goal concept is defined."""
        assert GOAL is not None

    def test_goal_must_have_owner(self):
        """Test Goal has required relationship to Character."""
        char_rels = [r for r in GOAL.relationships if r.target_concept == "Character"]
        assert len(char_rels) > 0
        assert char_rels[0].required is True

    def test_goal_validation_rules(self):
        """Test Goal has validation rules."""
        rule_ids = [r.rule_id for r in GOAL.validation_rules]
        assert "goal_must_have_owner" in rule_ids


class TestConflictConcept:
    """Test the Conflict concept definition."""

    def test_conflict_exists(self):
        """Test that Conflict concept is defined."""
        assert CONFLICT is not None

    def test_conflict_definition(self):
        """Test Conflict has appropriate definition."""
        assert "opposition" in CONFLICT.definition.lower() or "tension" in CONFLICT.definition.lower()

    def test_conflict_has_stakes_rule(self):
        """Test Conflict has rule about having stakes."""
        rule_ids = [r.rule_id for r in CONFLICT.validation_rules]
        assert "conflict_must_have_stakes" in rule_ids


class TestPayoffConcept:
    """Test the Payoff concept definition."""

    def test_payoff_exists(self):
        """Test that Payoff concept is defined."""
        assert PAYOFF is not None

    def test_payoff_resolves_setup(self):
        """Test Payoff has required relationship to Setup."""
        setup_rels = [r for r in PAYOFF.relationships if r.target_concept == "Setup"]
        assert len(setup_rels) > 0
        assert setup_rels[0].required is True


class TestSymbolConcept:
    """Test the Symbol concept definition."""

    def test_symbol_exists(self):
        """Test that Symbol concept is defined."""
        assert SYMBOL is not None

    def test_symbol_definition(self):
        """Test Symbol has appropriate definition."""
        assert "meaning" in SYMBOL.definition.lower()

    def test_symbol_represents_themes(self):
        """Test Symbol has relationship to Theme."""
        theme_rels = [r for r in SYMBOL.relationships if r.target_concept == "Theme"]
        assert len(theme_rels) > 0


class TestRelationshipConcept:
    """Test the Relationship concept definition."""

    def test_relationship_exists(self):
        """Test that Relationship concept is defined."""
        assert RELATIONSHIP_CONCEPT is not None

    def test_relationship_connects_characters(self):
        """Test Relationship connects characters."""
        char_rels = [r for r in RELATIONSHIP_CONCEPT.relationships if r.target_concept == "Character"]
        assert len(char_rels) > 0
        assert char_rels[0].required is True


class TestBeatConcept:
    """Test the Beat concept definition."""

    def test_beat_exists(self):
        """Test that Beat concept is defined."""
        assert BEAT is not None

    def test_beat_definition(self):
        """Test Beat has appropriate definition."""
        assert "moment" in BEAT.definition.lower() or "atomic" in BEAT.definition.lower()

    def test_beat_belongs_to_arc(self):
        """Test Beat has required relationship to Arc."""
        arc_rels = [r for r in BEAT.relationships if r.target_concept == "Arc"]
        assert len(arc_rels) > 0
        assert arc_rels[0].required is True


class TestSetupConcept:
    """Test the Setup concept definition."""

    def test_setup_exists(self):
        """Test that Setup concept is defined."""
        assert SETUP is not None

    def test_setup_requires_payoff(self):
        """Test Setup has required relationship to Payoff."""
        payoff_rels = [r for r in SETUP.relationships if r.target_concept == "Payoff"]
        assert len(payoff_rels) > 0
        assert payoff_rels[0].required is True


class TestRevelationConcept:
    """Test the Revelation concept definition."""

    def test_revelation_exists(self):
        """Test that Revelation concept is defined."""
        assert REVELATION is not None

    def test_revelation_definition(self):
        """Test Revelation has appropriate definition."""
        assert "disclosure" in REVELATION.definition.lower() or "information" in REVELATION.definition.lower()

    def test_revelation_validation_rules(self):
        """Test Revelation has validation rules."""
        rule_ids = [r.rule_id for r in REVELATION.validation_rules]
        assert "revelation_discloses_hidden_info" in rule_ids


class TestReversalConcept:
    """Test the Reversal concept definition."""

    def test_reversal_exists(self):
        """Test that Reversal concept is defined."""
        assert REVERSAL is not None

    def test_reversal_definition(self):
        """Test Reversal has appropriate definition."""
        assert "invert" in REVERSAL.definition.lower() or "unexpected" in REVERSAL.definition.lower()

    def test_reversal_affects_arc(self):
        """Test Reversal affects Arc."""
        arc_rels = [r for r in REVERSAL.relationships if r.target_concept == "Arc"]
        assert len(arc_rels) > 0


class TestConceptCardinality:
    """Test cardinality constraints across concepts."""

    def test_character_goal_cardinality_one_to_many(self):
        """Test Character-Goal relationship is one-to-many."""
        rels = [r for r in CHARACTER.relationships if r.target_concept == "Goal"]
        assert len(rels) > 0
        assert rels[0].cardinality == "one-to-many"

    def test_character_arc_cardinality_many_to_many(self):
        """Test Character-Arc relationship is many-to-many."""
        rels = [r for r in CHARACTER.relationships if r.target_concept == "Arc"]
        assert len(rels) > 0
        assert rels[0].cardinality == "many-to-many"

    def test_arc_beat_cardinality_one_to_many(self):
        """Test Arc-Beat relationship is one-to-many."""
        rels = [r for r in ARC.relationships if r.target_concept == "Beat"]
        assert len(rels) > 0
        assert rels[0].cardinality == "one-to-many"

    def test_setup_payoff_cardinality_one_to_one(self):
        """Test Setup-Payoff relationship is one-to-one."""
        rels = [r for r in SETUP.relationships if r.target_concept == "Payoff"]
        assert len(rels) > 0
        assert rels[0].cardinality == "one-to-one"


class TestConceptRegistry:
    """Test the concept registry and access functions."""

    def test_all_concepts_accessible(self):
        """Test all 12 concepts are in registry."""
        assert len(ALL_CONCEPTS) == 12
        expected_names = [
            "Character", "Arc", "Theme", "Goal", "Conflict", "Payoff",
            "Symbol", "Relationship", "Beat", "Setup", "Revelation", "Reversal"
        ]
        for name in expected_names:
            assert name in ALL_CONCEPTS

    def test_get_concept_retrieves_concepts(self):
        """Test get_concept function retrieves concepts by name."""
        char = get_concept("Character")
        assert char.name == "Character"

        arc = get_concept("Arc")
        assert arc.name == "Arc"

    def test_get_concept_raises_on_unknown(self):
        """Test get_concept raises ValueError for unknown concepts."""
        with pytest.raises(ValueError):
            get_concept("UnknownConcept")

    def test_all_concepts_have_definitions(self):
        """Test all concepts have non-empty definitions."""
        for name, concept in ALL_CONCEPTS.items():
            assert concept.definition
            assert len(concept.definition) > 0

    def test_all_concepts_have_validation_rules(self):
        """Test all concepts have at least one validation rule."""
        for name, concept in ALL_CONCEPTS.items():
            assert len(concept.validation_rules) > 0


class TestValidationRuleGenreApplicability:
    """Test that validation rules correctly specify genre applicability."""

    def test_character_rules_apply_to_all_genres(self):
        """Test Character validation rules apply to all three genres."""
        for rule in CHARACTER.validation_rules:
            assert "netorare" in rule.applies_to
            assert "mystery" in rule.applies_to
            assert "gentlefemdom" in rule.applies_to

    def test_arc_rules_apply_to_all_genres(self):
        """Test Arc validation rules apply to all three genres."""
        for rule in ARC.validation_rules:
            assert len(rule.applies_to) == 3

    def test_all_concept_rules_have_genre_applicability(self):
        """Test all concepts' validation rules specify genre applicability."""
        for concept in ALL_CONCEPTS.values():
            for rule in concept.validation_rules:
                assert len(rule.applies_to) > 0
                for genre in rule.applies_to:
                    assert genre in ["netorare", "mystery", "gentlefemdom"]


class TestConceptIntegration:
    """Integration tests for concepts and their relationships."""

    def test_character_and_goal_relationship_consistency(self):
        """Test Character-Goal relationship is consistent."""
        # Character should have Goal relationship
        char_to_goal = [r for r in CHARACTER.relationships if r.target_concept == "Goal"]
        assert len(char_to_goal) > 0

        # Goal should have Character relationship
        goal_to_char = [r for r in GOAL.relationships if r.target_concept == "Character"]
        assert len(goal_to_char) > 0

    def test_arc_and_beat_relationship_consistency(self):
        """Test Arc-Beat relationship is required and consistent."""
        # Arc must contain Beat
        arc_to_beat = [r for r in ARC.relationships if r.target_concept == "Beat"]
        assert len(arc_to_beat) > 0
        assert arc_to_beat[0].required is True

        # Beat must belong to Arc
        beat_to_arc = [r for r in BEAT.relationships if r.target_concept == "Arc"]
        assert len(beat_to_arc) > 0
        assert beat_to_arc[0].required is True

    def test_setup_payoff_relationship_consistency(self):
        """Test Setup-Payoff relationship is bidirectional and required."""
        # Setup requires Payoff
        setup_to_payoff = [r for r in SETUP.relationships if r.target_concept == "Payoff"]
        assert len(setup_to_payoff) > 0
        assert setup_to_payoff[0].required is True

        # Payoff resolves Setup
        payoff_to_setup = [r for r in PAYOFF.relationships if r.target_concept == "Setup"]
        assert len(payoff_to_setup) > 0
        assert payoff_to_setup[0].required is True

    def test_theme_arc_relationship(self):
        """Test Theme-Arc relationship is many-to-many."""
        theme_to_arc = [r for r in THEME.relationships if r.target_concept == "Arc"]
        assert len(theme_to_arc) > 0
        assert theme_to_arc[0].cardinality == "many-to-many"

    def test_all_relationship_targets_exist(self):
        """Test all relationship targets refer to defined concepts."""
        all_target_names = set()
        for concept in ALL_CONCEPTS.values():
            for rel in concept.relationships:
                all_target_names.add(rel.target_concept)

        # All targets should exist in ALL_CONCEPTS
        for target in all_target_names:
            assert target in ALL_CONCEPTS, f"Relationship targets undefined concept: {target}"


class TestConceptCompleteness:
    """Test that all expected concepts are fully implemented."""

    def test_12_concepts_defined(self):
        """Test that all 12 required concepts are defined."""
        expected = 12
        actual = len(ALL_CONCEPTS)
        assert actual == expected, f"Expected {expected} concepts, found {actual}"

    def test_all_required_concepts_present(self):
        """Test all required concepts are present."""
        required = {
            "Character", "Arc", "Theme", "Goal", "Conflict", "Payoff",
            "Symbol", "Relationship", "Beat", "Setup", "Revelation", "Reversal"
        }
        for concept_name in required:
            assert concept_name in ALL_CONCEPTS
            assert ALL_CONCEPTS[concept_name] is not None
