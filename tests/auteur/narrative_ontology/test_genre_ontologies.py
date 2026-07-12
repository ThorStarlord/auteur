"""Tests for genre-specific narrative ontologies.

Tests cover netorare, mystery, and gentle femdom genre ontologies,
including concept definitions, relationships, validation rules, and theme sets.
"""

import pytest
from auteur.narrative_ontology.genre.netorara_ontology import (
    NetorareOntology,
    CuckoldryArc,
    HumiliationProgression,
    ConsentBoundary,
)
from auteur.narrative_ontology.genre.mystery_ontology import (
    MysteryOntology,
    InvestigationArc,
    Clue,
    RedHerring,
)
from auteur.narrative_ontology.genre.gentlefemdom_ontology import (
    GentleFemdomOntology,
    AuthorityArc,
    SurrenderBeat,
    TrustCheckpoint,
)
from auteur.narrative_ontology.base_concept import BaseConcept, Relationship, ValidationRule


class TestNetorareOntology:
    """Tests for netorare genre ontology."""

    def test_netorare_ontology_instantiation(self):
        """Test that netorare ontology instantiates correctly."""
        ontology = NetorareOntology()
        assert ontology.genre == "netorare"
        assert len(ontology.concepts) == 3

    def test_netorare_theme_set(self):
        """Test netorare theme set contains correct themes."""
        ontology = NetorareOntology()
        themes = ontology.get_theme_set()
        assert "humiliation" in themes
        assert "degradation" in themes
        assert "cuckoldry" in themes
        assert "shame" in themes
        assert "exposure" in themes
        assert len(themes) == 5

    def test_cuckoldry_arc_definition(self):
        """Test cuckoldry arc concept definition."""
        arc = CuckoldryArc()
        assert arc.name == "Cuckoldry Arc"
        assert "cuckoldry" in arc.definition.lower()
        assert arc.category == "genre-specific"
        assert "Arc" in arc.parent_concepts

    def test_cuckoldry_arc_relationships(self):
        """Test cuckoldry arc relationships to other concepts."""
        arc = CuckoldryArc()
        related_concepts = arc.get_related_concepts()
        assert "Character" in related_concepts
        assert "Humiliation Progression" in related_concepts
        assert "Consent Boundary" in related_concepts

    def test_cuckoldry_arc_validation_rules(self):
        """Test cuckoldry arc validation rules."""
        arc = CuckoldryArc()
        rules = arc.validation_rules
        rule_ids = [rule.rule_id for rule in rules]
        assert "netorara_cuckoldry_stages" in rule_ids
        assert "netorara_cuckoldry_characters" in rule_ids
        assert "netorara_cuckoldry_consent" in rule_ids

    def test_humiliation_progression_definition(self):
        """Test humiliation progression concept definition."""
        progression = HumiliationProgression()
        assert progression.name == "Humiliation Progression"
        assert "escalat" in progression.definition.lower()
        assert progression.category == "genre-specific"

    def test_humiliation_progression_metadata(self):
        """Test humiliation progression metadata."""
        progression = HumiliationProgression(intensity_levels=7, progression_type="cyclical")
        assert progression.metadata["intensity_levels"] == 7
        assert progression.metadata["progression_type"] == "cyclical"
        assert len(progression.metadata["intensity_scale"]) == 7

    def test_humiliation_progression_validation_rules(self):
        """Test humiliation progression validation rules."""
        progression = HumiliationProgression()
        rules = progression.validation_rules
        rule_ids = [rule.rule_id for rule in rules]
        assert "netorara_humiliation_levels" in rule_ids
        assert "netorara_humiliation_consistency" in rule_ids
        assert "netorara_humiliation_theme_alignment" in rule_ids

    def test_consent_boundary_definition(self):
        """Test consent boundary concept definition."""
        boundary = ConsentBoundary()
        assert boundary.name == "Consent Boundary"
        assert "safety" in boundary.definition.lower()
        assert "constraints" in boundary.definition.lower()
        assert boundary.category == "genre-specific"

    def test_consent_boundary_types(self):
        """Test consent boundary types."""
        boundary = ConsentBoundary(boundary_type="hard_stop")
        assert boundary.metadata["boundary_type"] == "hard_stop"
        assert "hard_stop" in boundary.metadata["boundary_types"]
        assert "warning_zone" in boundary.metadata["boundary_types"]
        assert "safe_zone" in boundary.metadata["boundary_types"]

    def test_consent_boundary_validation_rules(self):
        """Test consent boundary validation rules."""
        boundary = ConsentBoundary()
        rules = boundary.validation_rules
        rule_ids = [rule.rule_id for rule in rules]
        assert "netorara_consent_required" in rule_ids
        assert "netorara_consent_type_valid" in rule_ids
        assert "netorara_consent_coverage" in rule_ids

    def test_netorare_ontology_get_concept(self):
        """Test getting concept from netorare ontology."""
        ontology = NetorareOntology()
        arc = ontology.get_concept("Cuckoldry Arc")
        assert arc.name == "Cuckoldry Arc"
        assert isinstance(arc, BaseConcept)

    def test_netorare_ontology_get_all_concepts(self):
        """Test getting all concepts from netorare ontology."""
        ontology = NetorareOntology()
        concepts = ontology.get_all_concepts()
        assert len(concepts) == 3
        assert "Cuckoldry Arc" in concepts
        assert "Humiliation Progression" in concepts
        assert "Consent Boundary" in concepts

    def test_netorare_ontology_validate_concept(self):
        """Test concept validation in netorare ontology."""
        ontology = NetorareOntology()
        assert ontology.validate_concept("Cuckoldry Arc") is True
        assert ontology.validate_concept("Invalid Concept") is False

    def test_netorare_ontology_to_dict(self):
        """Test converting netorare ontology to dictionary."""
        ontology = NetorareOntology()
        data = ontology.to_dict()
        assert data["genre"] == "netorare"
        assert "Cuckoldry Arc" in data["concepts"]
        assert len(data["concepts"]) == 3


class TestMysteryOntology:
    """Tests for mystery genre ontology."""

    def test_mystery_ontology_instantiation(self):
        """Test that mystery ontology instantiates correctly."""
        ontology = MysteryOntology()
        assert ontology.genre == "mystery"
        assert len(ontology.concepts) == 3

    def test_mystery_theme_set(self):
        """Test mystery theme set contains correct themes."""
        ontology = MysteryOntology()
        themes = ontology.get_theme_set()
        assert "investigation" in themes
        assert "deception" in themes
        assert "revelation" in themes
        assert "conspiracy" in themes
        assert "doubt" in themes

    def test_investigation_arc_definition(self):
        """Test investigation arc concept definition."""
        arc = InvestigationArc()
        assert arc.name == "Investigation Arc"
        assert "evidence" in arc.definition.lower()
        assert "arc" in arc.definition.lower()
        assert arc.category == "genre-specific"
        assert "Arc" in arc.parent_concepts

    def test_investigation_arc_relationships(self):
        """Test investigation arc relationships."""
        arc = InvestigationArc()
        related = arc.get_related_concepts()
        assert "Character" in related
        assert "Clue" in related
        assert "Red Herring" in related

    def test_investigation_arc_types(self):
        """Test investigation arc types."""
        arc = InvestigationArc(investigation_type="forensic", complexity_level=4)
        assert arc.metadata["investigation_type"] == "forensic"
        assert arc.metadata["complexity_level"] == 4
        assert "forensic" in arc.metadata["valid_types"]
        assert "police" in arc.metadata["valid_types"]

    def test_clue_definition(self):
        """Test clue concept definition."""
        clue = Clue()
        assert clue.name == "Clue"
        assert "information" in clue.definition.lower()
        assert clue.category == "genre-specific"
        assert "Information" in clue.parent_concepts

    def test_clue_types(self):
        """Test clue types."""
        clue = Clue(clue_type="testimony", significance="major")
        assert clue.metadata["clue_type"] == "testimony"
        assert clue.metadata["significance"] == "major"
        assert "testimony" in clue.metadata["valid_types"]
        assert "major" in clue.metadata["valid_significance"]

    def test_clue_validation_rules(self):
        """Test clue validation rules."""
        clue = Clue()
        rules = clue.validation_rules
        rule_ids = [rule.rule_id for rule in rules]
        assert "mystery_clue_type_valid" in rule_ids
        assert "mystery_clue_significance_valid" in rule_ids
        assert "mystery_clue_context" in rule_ids

    def test_red_herring_definition(self):
        """Test red herring concept definition."""
        herring = RedHerring()
        assert herring.name == "Red Herring"
        assert "misdirection" in herring.definition.lower()
        assert herring.category == "genre-specific"
        assert "Misdirection" in herring.parent_concepts

    def test_red_herring_deception_levels(self):
        """Test red herring deception levels."""
        herring = RedHerring(deception_level="subtle", resolution_point="final")
        assert herring.metadata["deception_level"] == "subtle"
        assert herring.metadata["resolution_point"] == "final"
        assert "subtle" in herring.metadata["valid_deception_levels"]
        assert "final" in herring.metadata["valid_resolution_points"]

    def test_red_herring_validation_rules(self):
        """Test red herring validation rules."""
        herring = RedHerring()
        rules = herring.validation_rules
        rule_ids = [rule.rule_id for rule in rules]
        assert "mystery_red_herring_deception" in rule_ids
        assert "mystery_red_herring_resolution" in rule_ids
        assert "mystery_red_herring_plausibility" in rule_ids
        assert "mystery_red_herring_purpose" in rule_ids

    def test_mystery_ontology_validate_concept(self):
        """Test concept validation in mystery ontology."""
        ontology = MysteryOntology()
        assert ontology.validate_concept("Clue") is True
        assert ontology.validate_concept("Red Herring") is True
        assert ontology.validate_concept("Invalid") is False

    def test_mystery_ontology_to_dict(self):
        """Test converting mystery ontology to dictionary."""
        ontology = MysteryOntology()
        data = ontology.to_dict()
        assert data["genre"] == "mystery"
        assert len(data["concepts"]) == 3


class TestGentleFemdomOntology:
    """Tests for gentle femdom genre ontology."""

    def test_femdom_ontology_instantiation(self):
        """Test that gentle femdom ontology instantiates correctly."""
        ontology = GentleFemdomOntology()
        assert ontology.genre == "gentlefemdom"
        assert len(ontology.concepts) == 3

    def test_femdom_theme_set(self):
        """Test gentle femdom theme set contains correct themes."""
        ontology = GentleFemdomOntology()
        themes = ontology.get_theme_set()
        assert "authority" in themes
        assert "surrender" in themes
        assert "dominance" in themes
        assert "trust" in themes
        assert "control" in themes

    def test_authority_arc_definition(self):
        """Test authority arc concept definition."""
        arc = AuthorityArc()
        assert arc.name == "Authority Arc"
        assert "power" in arc.definition.lower()
        assert "consensual" in arc.definition.lower()
        assert arc.category == "genre-specific"
        assert "Arc" in arc.parent_concepts

    def test_authority_arc_types(self):
        """Test authority arc types."""
        arc = AuthorityArc(authority_type="romantic", dynamic_type="negotiated")
        assert arc.metadata["authority_type"] == "romantic"
        assert arc.metadata["dynamic_type"] == "negotiated"
        assert "romantic" in arc.metadata["valid_types"]
        assert "negotiated" in arc.metadata["valid_dynamics"]

    def test_authority_arc_relationships(self):
        """Test authority arc relationships."""
        arc = AuthorityArc()
        related = arc.get_related_concepts()
        assert "Character" in related
        assert "Surrender Beat" in related
        assert "Trust Checkpoint" in related

    def test_surrender_beat_definition(self):
        """Test surrender beat concept definition."""
        beat = SurrenderBeat()
        assert beat.name == "Surrender Beat"
        assert "embraces" in beat.definition.lower()
        assert "vulnerability" in beat.definition.lower()
        assert beat.category == "genre-specific"
        assert "Beat" in beat.parent_concepts

    def test_surrender_beat_types(self):
        """Test surrender beat types."""
        beat = SurrenderBeat(beat_type="psychological", intensity_level="profound")
        assert beat.metadata["beat_type"] == "psychological"
        assert beat.metadata["intensity_level"] == "profound"
        assert "psychological" in beat.metadata["valid_types"]
        assert "profound" in beat.metadata["valid_intensity"]

    def test_surrender_beat_validation_rules(self):
        """Test surrender beat validation rules."""
        beat = SurrenderBeat()
        rules = beat.validation_rules
        rule_ids = [rule.rule_id for rule in rules]
        assert "femdom_surrender_consensual" in rule_ids
        assert "femdom_surrender_character_agency" in rule_ids

    def test_trust_checkpoint_definition(self):
        """Test trust checkpoint concept definition."""
        checkpoint = TrustCheckpoint()
        assert checkpoint.name == "Trust Checkpoint"
        assert "trust" in checkpoint.definition.lower()
        assert "consent" in checkpoint.definition.lower()
        assert checkpoint.category == "genre-specific"
        assert "Checkpoint" in checkpoint.parent_concepts

    def test_trust_checkpoint_types(self):
        """Test trust checkpoint types."""
        checkpoint = TrustCheckpoint(checkpoint_type="crisis", validation_outcome="renegotiated")
        assert checkpoint.metadata["checkpoint_type"] == "crisis"
        assert checkpoint.metadata["validation_outcome"] == "renegotiated"
        assert "crisis" in checkpoint.metadata["valid_types"]
        assert "renegotiated" in checkpoint.metadata["valid_outcomes"]

    def test_trust_checkpoint_validation_rules(self):
        """Test trust checkpoint validation rules."""
        checkpoint = TrustCheckpoint()
        rules = checkpoint.validation_rules
        rule_ids = [rule.rule_id for rule in rules]
        assert "femdom_checkpoint_consent_explicit" in rule_ids
        assert "femdom_checkpoint_honesty" in rule_ids
        assert "femdom_checkpoint_agency" in rule_ids

    def test_femdom_ontology_get_concept(self):
        """Test getting concept from gentle femdom ontology."""
        ontology = GentleFemdomOntology()
        beat = ontology.get_concept("Surrender Beat")
        assert beat.name == "Surrender Beat"
        assert isinstance(beat, BaseConcept)

    def test_femdom_ontology_validate_concept(self):
        """Test concept validation in gentle femdom ontology."""
        ontology = GentleFemdomOntology()
        assert ontology.validate_concept("Authority Arc") is True
        assert ontology.validate_concept("Trust Checkpoint") is True
        assert ontology.validate_concept("Invalid") is False

    def test_femdom_ontology_to_dict(self):
        """Test converting gentle femdom ontology to dictionary."""
        ontology = GentleFemdomOntology()
        data = ontology.to_dict()
        assert data["genre"] == "gentlefemdom"
        assert len(data["concepts"]) == 3
        assert "Authority Arc" in data["concepts"]


class TestGenreOntologyStructure:
    """Tests for genre ontology structure and relationships."""

    def test_all_genres_have_theme_sets(self):
        """Test that all genres have defined theme sets."""
        genres = [
            (NetorareOntology(), ["humiliation", "degradation"]),
            (MysteryOntology(), ["investigation", "revelation"]),
            (GentleFemdomOntology(), ["authority", "trust"]),
        ]
        for ontology, expected_themes in genres:
            themes = ontology.get_theme_set()
            for theme in expected_themes:
                assert theme in themes

    def test_all_concepts_are_genre_specific(self):
        """Test that all concepts are marked as genre-specific."""
        ontologies = [
            NetorareOntology(),
            MysteryOntology(),
            GentleFemdomOntology(),
        ]
        for ontology in ontologies:
            for concept in ontology.get_all_concepts().values():
                assert concept.category == "genre-specific"

    def test_all_concepts_have_parent_concepts(self):
        """Test that all concepts inherit from base concepts."""
        ontologies = [
            NetorareOntology(),
            MysteryOntology(),
            GentleFemdomOntology(),
        ]
        for ontology in ontologies:
            for concept in ontology.get_all_concepts().values():
                assert len(concept.parent_concepts) > 0

    def test_all_concepts_have_validation_rules(self):
        """Test that all concepts have validation rules."""
        ontologies = [
            NetorareOntology(),
            MysteryOntology(),
            GentleFemdomOntology(),
        ]
        for ontology in ontologies:
            for concept in ontology.get_all_concepts().values():
                assert len(concept.validation_rules) > 0

    def test_concept_relationships_are_bidirectional(self):
        """Test that concept relationships reference both directions."""
        ontologies = [
            NetorareOntology(),
            MysteryOntology(),
            GentleFemdomOntology(),
        ]
        for ontology in ontologies:
            for concept in ontology.get_all_concepts().values():
                for relationship in concept.relationships:
                    assert relationship.source == concept.name
                    assert relationship.target is not None

    def test_genre_distinction(self):
        """Test that genres are properly distinguished."""
        netorare = NetorareOntology()
        mystery = MysteryOntology()
        femdom = GentleFemdomOntology()

        assert netorare.genre != mystery.genre
        assert mystery.genre != femdom.genre
        assert femdom.genre != netorare.genre

    def test_no_concept_overlap_between_genres(self):
        """Test that genres don't have overlapping core concepts."""
        netorare_concepts = set(NetorareOntology().get_all_concepts().keys())
        mystery_concepts = set(MysteryOntology().get_all_concepts().keys())
        femdom_concepts = set(GentleFemdomOntology().get_all_concepts().keys())

        # Genres should have distinct concepts
        assert len(netorare_concepts & mystery_concepts) == 0
        assert len(mystery_concepts & femdom_concepts) == 0
        assert len(femdom_concepts & netorare_concepts) == 0


class TestBaseConcept:
    """Tests for base concept functionality."""

    def test_concept_to_dict(self):
        """Test converting concept to dictionary."""
        arc = CuckoldryArc()
        data = arc.to_dict()
        assert data["name"] == "Cuckoldry Arc"
        assert data["definition"] is not None
        assert data["category"] == "genre-specific"
        assert len(data["relationships"]) > 0

    def test_get_related_concepts(self):
        """Test getting related concepts."""
        arc = CuckoldryArc()
        related = arc.get_related_concepts()
        assert isinstance(related, list)
        assert len(related) > 0

    def test_validation_rule_application(self):
        """Test getting validation rules for concept."""
        arc = CuckoldryArc()
        rules = arc.get_validation_rules_for_concept("Cuckoldry Arc")
        assert len(rules) > 0

    def test_subtype_checking(self):
        """Test checking if concept is subtype of parent."""
        arc = CuckoldryArc()
        assert arc.is_subtype_of("Arc") is True
        assert arc.is_subtype_of("Invalid") is False
