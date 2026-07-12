"""Tests for Layer 2.5 ownership rules schema and loading.

Validates that:
- OwnershipRule and OwnershipMapping Pydantic models work correctly
- Ownership rules can be loaded from YAML
- Ownership model enforces required facts and prevents duplicates
- Ownership queries (get_owner, get_rules_by_owner, etc.) work correctly
- Derived vs. authored facts are properly distinguished
"""

import pytest
import yaml
from pathlib import Path
from auteur.narrative_orchestration.schema.ownership import (
    OwnershipRule,
    OwnershipMapping,
    ArtifactType,
    StructuralFact,
)


class TestOwnershipRuleCreation:
    """Test OwnershipRule model creation and validation."""

    def test_ownership_rule_creation_basic(self):
        """Test creating a basic OwnershipRule with required fields."""
        rule = OwnershipRule(
            fact=StructuralFact.BOOKS_IN_SERIES,
            owner=ArtifactType.SERIES_OUTLINE,
            description="Series Outline owns the list of books in a series.",
        )

        assert rule.fact == StructuralFact.BOOKS_IN_SERIES
        assert rule.owner == ArtifactType.SERIES_OUTLINE
        assert rule.description == "Series Outline owns the list of books in a series."
        assert rule.is_derived is False

    def test_ownership_rule_with_is_derived_true(self):
        """Test creating an OwnershipRule marked as derived."""
        rule = OwnershipRule(
            fact=StructuralFact.CHAPTER_COUNT,
            owner=ArtifactType.CHAPTER_OUTLINE,
            description="Chapter count is computed from individual chapters.",
            is_derived=True,
        )

        assert rule.is_derived is True
        assert rule.fact == StructuralFact.CHAPTER_COUNT

    def test_ownership_rule_rejects_empty_description(self):
        """Test that OwnershipRule rejects empty descriptions."""
        with pytest.raises(ValueError):
            OwnershipRule(
                fact=StructuralFact.BOOKS_IN_SERIES,
                owner=ArtifactType.SERIES_OUTLINE,
                description="",
            )

    def test_ownership_rule_rejects_whitespace_only_description(self):
        """Test that OwnershipRule rejects whitespace-only descriptions."""
        with pytest.raises(ValueError):
            OwnershipRule(
                fact=StructuralFact.BOOKS_IN_SERIES,
                owner=ArtifactType.SERIES_OUTLINE,
                description="   ",
            )

    def test_ownership_rule_trims_description_whitespace(self):
        """Test that OwnershipRule trims leading/trailing whitespace."""
        rule = OwnershipRule(
            fact=StructuralFact.BOOKS_IN_SERIES,
            owner=ArtifactType.SERIES_OUTLINE,
            description="  Valid description with spaces  ",
        )

        assert rule.description == "Valid description with spaces"


class TestOwnershipMappingCreation:
    """Test OwnershipMapping model creation and validation."""

    @staticmethod
    def create_minimal_rules():
        """Create minimal set of 8 core ownership rules."""
        return [
            OwnershipRule(
                fact=StructuralFact.BOOKS_IN_SERIES,
                owner=ArtifactType.SERIES_OUTLINE,
                description="Series Outline owns books in series.",
            ),
            OwnershipRule(
                fact=StructuralFact.SEQUENCES_IN_BOOK,
                owner=ArtifactType.BOOK_OUTLINE,
                description="Book Outline owns sequences in book.",
            ),
            OwnershipRule(
                fact=StructuralFact.CHAPTERS_IN_SEQUENCE,
                owner=ArtifactType.SEQUENCE_OUTLINE,
                description="Sequence Outline owns chapters in sequence.",
            ),
            OwnershipRule(
                fact=StructuralFact.CHAPTER_PURPOSE,
                owner=ArtifactType.CHAPTER_OUTLINE,
                description="Chapter Outline owns chapter purpose.",
            ),
            OwnershipRule(
                fact=StructuralFact.CHARACTER_TRANSFORMATION,
                owner=ArtifactType.CHARACTER_ARC,
                description="Character Arc owns character transformation.",
            ),
            OwnershipRule(
                fact=StructuralFact.PLOT_PROGRESSION,
                owner=ArtifactType.STORY_ARC,
                description="Story Arc owns plot progression.",
            ),
            OwnershipRule(
                fact=StructuralFact.ARC_BEAT_LOCATIONS,
                owner=ArtifactType.STORY_ARC,
                description="Story Arc owns arc beat locations.",
            ),
            OwnershipRule(
                fact=StructuralFact.ARC_SPAN_CHAPTERS,
                owner=ArtifactType.STORY_ARC,
                description="Story Arc owns arc span chapters.",
                is_derived=True,
            ),
        ]

    def test_ownership_mapping_creation_with_minimal_rules(self):
        """Test creating OwnershipMapping with minimum required 8 rules."""
        rules = self.create_minimal_rules()
        mapping = OwnershipMapping(rules=rules)

        assert len(mapping.rules) == 8
        assert mapping.version == "1.0.0"
        assert "canonical ownership" in mapping.description.lower()

    def test_ownership_mapping_requires_minimum_8_rules(self):
        """Test that OwnershipMapping requires at least 8 rules."""
        with pytest.raises(ValueError):
            # Create only 7 rules
            rules = self.create_minimal_rules()[:-1]
            OwnershipMapping(rules=rules)

    def test_ownership_mapping_rejects_duplicate_facts(self):
        """Test that OwnershipMapping rejects duplicate ownership for same fact."""
        rules = self.create_minimal_rules()
        # Add a duplicate rule for BOOKS_IN_SERIES
        rules.append(
            OwnershipRule(
                fact=StructuralFact.BOOKS_IN_SERIES,
                owner=ArtifactType.BOOK_OUTLINE,
                description="Duplicate ownership for testing.",
            )
        )

        with pytest.raises(ValueError, match="Duplicate ownership rules"):
            OwnershipMapping(rules=rules)

    def test_ownership_mapping_custom_version(self):
        """Test creating OwnershipMapping with custom version."""
        rules = self.create_minimal_rules()
        mapping = OwnershipMapping(
            version="2.0.0",
            rules=rules,
            description="Custom test mapping",
            last_updated="2026-08-01",
        )

        assert mapping.version == "2.0.0"
        assert mapping.description == "Custom test mapping"
        assert mapping.last_updated == "2026-08-01"


class TestOwnershipMappingQueries:
    """Test OwnershipMapping query methods."""

    @staticmethod
    def create_full_mapping():
        """Create complete ownership mapping with all core facts."""
        rules = [
            OwnershipRule(
                fact=StructuralFact.BOOKS_IN_SERIES,
                owner=ArtifactType.SERIES_OUTLINE,
                description="Series Outline owns books in series.",
            ),
            OwnershipRule(
                fact=StructuralFact.SEQUENCES_IN_BOOK,
                owner=ArtifactType.BOOK_OUTLINE,
                description="Book Outline owns sequences in book.",
            ),
            OwnershipRule(
                fact=StructuralFact.CHAPTERS_IN_SEQUENCE,
                owner=ArtifactType.SEQUENCE_OUTLINE,
                description="Sequence Outline owns chapters in sequence.",
            ),
            OwnershipRule(
                fact=StructuralFact.CHAPTER_PURPOSE,
                owner=ArtifactType.CHAPTER_OUTLINE,
                description="Chapter Outline owns chapter purpose.",
            ),
            OwnershipRule(
                fact=StructuralFact.CHARACTER_TRANSFORMATION,
                owner=ArtifactType.CHARACTER_ARC,
                description="Character Arc owns character transformation.",
            ),
            OwnershipRule(
                fact=StructuralFact.PLOT_PROGRESSION,
                owner=ArtifactType.STORY_ARC,
                description="Story Arc owns plot progression.",
            ),
            OwnershipRule(
                fact=StructuralFact.ARC_BEAT_LOCATIONS,
                owner=ArtifactType.STORY_ARC,
                description="Story Arc owns arc beat locations.",
            ),
            OwnershipRule(
                fact=StructuralFact.ARC_SPAN_CHAPTERS,
                owner=ArtifactType.STORY_ARC,
                description="Story Arc owns arc span chapters.",
                is_derived=True,
            ),
        ]
        return OwnershipMapping(rules=rules)

    def test_get_rule_returns_correct_rule(self):
        """Test get_rule() returns the correct OwnershipRule."""
        mapping = self.create_full_mapping()
        rule = mapping.get_rule(StructuralFact.CHAPTER_PURPOSE)

        assert rule is not None
        assert rule.fact == StructuralFact.CHAPTER_PURPOSE
        assert rule.owner == ArtifactType.CHAPTER_OUTLINE

    def test_get_rule_returns_none_for_undefined_fact(self):
        """Test get_rule() returns None for facts not in mapping."""
        mapping = self.create_full_mapping()
        rule = mapping.get_rule(StructuralFact.CHAPTER_SUMMARY)

        assert rule is None

    def test_get_owner_returns_correct_artifact_type(self):
        """Test get_owner() returns the owning artifact type."""
        mapping = self.create_full_mapping()
        owner = mapping.get_owner(StructuralFact.BOOKS_IN_SERIES)

        assert owner == ArtifactType.SERIES_OUTLINE

    def test_get_owner_returns_none_for_undefined_fact(self):
        """Test get_owner() returns None for undefined facts."""
        mapping = self.create_full_mapping()
        owner = mapping.get_owner(StructuralFact.CHAPTER_SUMMARY)

        assert owner is None

    def test_get_rules_by_owner_returns_all_owned_facts(self):
        """Test get_rules_by_owner() returns all rules for an artifact."""
        mapping = self.create_full_mapping()
        story_arc_rules = mapping.get_rules_by_owner(ArtifactType.STORY_ARC)

        # Story Arc should own 3 facts
        assert len(story_arc_rules) == 3
        facts = {rule.fact for rule in story_arc_rules}
        assert StructuralFact.PLOT_PROGRESSION in facts
        assert StructuralFact.ARC_BEAT_LOCATIONS in facts
        assert StructuralFact.ARC_SPAN_CHAPTERS in facts

    def test_get_rules_by_owner_returns_empty_for_unrelated_artifact(self):
        """Test get_rules_by_owner() returns empty list for unrelated artifact."""
        mapping = self.create_full_mapping()
        theme_arc_rules = mapping.get_rules_by_owner(ArtifactType.THEME_ARC)

        assert len(theme_arc_rules) == 0

    def test_get_derived_facts_returns_only_derived(self):
        """Test get_derived_facts() returns only facts marked as derived."""
        mapping = self.create_full_mapping()
        derived = mapping.get_derived_facts()

        # Only ARC_SPAN_CHAPTERS is marked as derived in test data
        assert len(derived) == 1
        assert StructuralFact.ARC_SPAN_CHAPTERS in derived

    def test_get_authored_facts_returns_only_authored(self):
        """Test get_authored_facts() returns only non-derived facts."""
        mapping = self.create_full_mapping()
        authored = mapping.get_authored_facts()

        # Should have 7 authored facts (8 total - 1 derived)
        assert len(authored) == 7
        assert StructuralFact.ARC_SPAN_CHAPTERS not in authored


class TestOwnershipRulesYAMLLoading:
    """Test loading ownership rules from YAML file."""

    def test_load_ownership_rules_from_yaml(self):
        """Test loading canonical ownership rules from YAML data file."""
        yaml_path = Path(
            "H:/GithubRepositories/auteur/data/composition/ownership_rules.yaml"
        )

        # Verify file exists
        assert yaml_path.exists(), f"YAML file not found at {yaml_path}"

        # Load YAML
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        # Parse into OwnershipMapping
        mapping = OwnershipMapping(**data)

        # Verify core properties
        assert mapping.version is not None
        assert mapping.rules is not None
        assert len(mapping.rules) >= 8

    def test_yaml_rules_cover_all_8_core_facts(self):
        """Test that YAML contains all 8 core ownership facts."""
        yaml_path = Path(
            "H:/GithubRepositories/auteur/data/composition/ownership_rules.yaml"
        )

        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        mapping = OwnershipMapping(**data)

        # Verify all 8 core facts are defined
        core_facts = {
            StructuralFact.BOOKS_IN_SERIES,
            StructuralFact.SEQUENCES_IN_BOOK,
            StructuralFact.CHAPTERS_IN_SEQUENCE,
            StructuralFact.CHAPTER_PURPOSE,
            StructuralFact.CHARACTER_TRANSFORMATION,
            StructuralFact.PLOT_PROGRESSION,
            StructuralFact.ARC_BEAT_LOCATIONS,
            StructuralFact.ARC_SPAN_CHAPTERS,
        }

        defined_facts = {rule.fact for rule in mapping.rules}
        missing = core_facts - defined_facts
        assert len(missing) == 0, f"Missing core facts in YAML: {missing}"

    def test_yaml_rules_have_meaningful_descriptions(self):
        """Test that all YAML rules have substantive descriptions."""
        yaml_path = Path(
            "H:/GithubRepositories/auteur/data/composition/ownership_rules.yaml"
        )

        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        mapping = OwnershipMapping(**data)

        for rule in mapping.rules:
            assert len(rule.description) > 20, (
                f"Rule {rule.fact.value} has too-short description: {rule.description}"
            )


class TestOwnershipSchemaConsistency:
    """Test consistency of ownership schema across all artifacts."""

    def test_each_artifact_type_owns_at_least_one_fact(self):
        """Test that most artifact types own at least one fact."""
        yaml_path = Path(
            "H:/GithubRepositories/auteur/data/composition/ownership_rules.yaml"
        )

        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        mapping = OwnershipMapping(**data)

        # Get all artifact types mentioned in rules
        owned_artifacts = {rule.owner for rule in mapping.rules}

        # Each mentioned artifact should own at least one fact
        for artifact_type in owned_artifacts:
            rules = mapping.get_rules_by_owner(artifact_type)
            assert len(rules) > 0, f"Artifact {artifact_type} owns no facts"

    def test_derived_facts_are_subset_of_all_facts(self):
        """Test that derived facts are a subset of all facts."""
        yaml_path = Path(
            "H:/GithubRepositories/auteur/data/composition/ownership_rules.yaml"
        )

        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        mapping = OwnershipMapping(**data)

        derived = set(mapping.get_derived_facts())
        authored = set(mapping.get_authored_facts())

        # Derived and authored should be disjoint
        assert len(derived & authored) == 0
        # Together they should equal all facts
        assert len(derived | authored) == len(mapping.rules)

    def test_fact_ownership_is_mutually_exclusive(self):
        """Test that each fact has exactly one owner."""
        yaml_path = Path(
            "H:/GithubRepositories/auteur/data/composition/ownership_rules.yaml"
        )

        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        mapping = OwnershipMapping(**data)

        # Count how many rules define each fact
        fact_counts = {}
        for rule in mapping.rules:
            fact_counts[rule.fact] = fact_counts.get(rule.fact, 0) + 1

        # Each fact should have exactly one owner
        for fact, count in fact_counts.items():
            assert count == 1, f"Fact {fact.value} has {count} owners"
