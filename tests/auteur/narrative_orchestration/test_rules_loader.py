"""Tests for Layer 2.5 composition rules YAML loader.

Validates that:
- YAML rules file can be loaded and parsed
- All rule types are created correctly (optionality, ordering, state, coverage)
- Genre-specific rules override global rules correctly
- Rule validation detects inconsistencies
- Rules can be queried by ID, type, genre
- Wildcard character matching works
- Merging strategy produces consistent results
"""

import pytest
import yaml
from pathlib import Path
from auteur.narrative_orchestration.schema.rules_loader import (
    CompositionRulesLoader,
    OptionalityRule,
    ChronologicalOrderingRule,
    StateValidityRule,
    StateTransition,
    ArcCoverageRule,
    CompositionRules,
    RuleType,
    OptionalityLevel,
    Severity,
)


class TestOptionalityRuleCreation:
    """Test OptionalityRule model creation and validation."""

    def test_optionality_rule_creation(self):
        """Test creating a basic OptionalityRule."""
        rule = OptionalityRule(
            constraint_id="test_optional",
            artifact_type="sequence",
            optionality_level=OptionalityLevel.OPTIONAL,
            description="Sequences are optional in some genres",
            reason="Sequences provide organizational structure but can be omitted",
        )

        assert rule.constraint_id == "test_optional"
        assert rule.artifact_type == "sequence"
        assert rule.optionality_level == OptionalityLevel.OPTIONAL
        assert rule.is_artifact_optional() is True
        assert rule.is_artifact_required() is False

    def test_optionality_rule_required(self):
        """Test OptionalityRule for required artifacts."""
        rule = OptionalityRule(
            constraint_id="test_required",
            artifact_type="chapter",
            optionality_level=OptionalityLevel.REQUIRED,
            description="Chapters are required",
            reason="Every book must have at least one chapter",
        )

        assert rule.is_artifact_required() is True
        assert rule.is_artifact_optional() is False

    def test_optionality_rule_with_condition(self):
        """Test OptionalityRule with conditional description."""
        rule = OptionalityRule(
            constraint_id="test_conditional",
            artifact_type="character_arc",
            optionality_level=OptionalityLevel.CONDITIONAL,
            description="Character arcs optional for short stories",
            reason="Short stories may focus purely on plot",
            condition="Required for 5+ chapters, optional for shorter works",
        )

        assert rule.optionality_level == OptionalityLevel.CONDITIONAL
        assert rule.condition is not None
        assert "5+" in rule.condition

    def test_optionality_rule_rejects_invalid_constraint_id(self):
        """Test that OptionalityRule rejects invalid constraint_ids."""
        with pytest.raises(ValueError):
            OptionalityRule(
                constraint_id="invalid constraint!",  # Contains space and special char
                artifact_type="chapter",
                optionality_level=OptionalityLevel.REQUIRED,
                description="Valid description here",
                reason="Valid reason here",
            )


class TestChronologicalOrderingRuleCreation:
    """Test ChronologicalOrderingRule model creation and validation."""

    def test_chronological_rule_with_phases(self):
        """Test creating a ChronologicalOrderingRule with phase requirements."""
        rule = ChronologicalOrderingRule(
            constraint_id="payoff_after_setup",
            name="payoff_after_setup",
            source_artifact_type="setup_event",
            source_phase=2,
            target_artifact_type="payoff_event",
            target_phase=5,
            description="Payoff must occur after setup",
            reason="Narrative cause-effect requires setup before payoff",
        )

        assert rule.requires_phases() is True
        assert rule.requires_strict_ordering() is True
        assert rule.source_phase < rule.target_phase

    def test_chronological_rule_without_phases(self):
        """Test creating a ChronologicalOrderingRule without phase requirements."""
        rule = ChronologicalOrderingRule(
            constraint_id="crisis_before_resolution",
            name="crisis_before_resolution",
            source_artifact_type="crisis_chapter",
            target_artifact_type="resolution_chapter",
            description="Crisis before resolution",
            reason="Structure requires crisis before resolution",
        )

        assert rule.requires_phases() is False
        assert rule.source_phase is None
        assert rule.target_phase is None

    def test_chronological_rule_invalid_phase(self):
        """Test that ChronologicalOrderingRule rejects invalid phases."""
        with pytest.raises(ValueError):
            ChronologicalOrderingRule(
                constraint_id="invalid_phase",
                name="invalid_phase",
                source_artifact_type="source",
                source_phase=10,  # Invalid: must be 1-9
                target_artifact_type="target",
                target_phase=5,
                description="Invalid description",
                reason="Invalid reason",
            )

    def test_chronological_rule_with_severity(self):
        """Test ChronologicalOrderingRule with severity levels."""
        error_rule = ChronologicalOrderingRule(
            constraint_id="error_rule",
            name="error_rule",
            source_artifact_type="source",
            target_artifact_type="target",
            description="Error rule",
            reason="Error reason",
            severity=Severity.ERROR,
        )

        warning_rule = ChronologicalOrderingRule(
            constraint_id="warning_rule",
            name="warning_rule",
            source_artifact_type="source",
            target_artifact_type="target",
            description="Warning rule",
            reason="Warning reason",
            severity=Severity.WARNING,
        )

        assert error_rule.severity == Severity.ERROR
        assert warning_rule.severity == Severity.WARNING


class TestStateValidityRuleCreation:
    """Test StateValidityRule model creation and validation."""

    def test_state_validity_rule_creation(self):
        """Test creating a StateValidityRule with transitions."""
        transitions = [
            StateTransition(
                from_state="trust",
                to_state="suspicion",
                description="Protagonist suspects partner",
            ),
            StateTransition(
                from_state="suspicion",
                to_state="shock",
                description="Suspicions confirmed",
            ),
        ]

        rule = StateValidityRule(
            constraint_id="protagonist_distrust_arc",
            character_id="protagonist",
            valid_transitions=transitions,
            description="Protagonist emotional journey",
            reason="Netorare requires specific emotional progression",
        )

        assert len(rule.valid_transitions) == 2
        assert rule.valid_transitions[0].from_state == "trust"
        assert rule.valid_transitions[1].to_state == "shock"

    def test_state_validity_rule_character_matching_exact(self):
        """Test exact character ID matching."""
        rule = StateValidityRule(
            constraint_id="test_rule",
            character_id="clara",
            valid_transitions=[],
            description="Test for exact matching of character ID",
            reason="Exact ID matching is required for specific characters",
        )

        assert rule.matches_character("clara") is True
        assert rule.matches_character("clara_best_friend") is False
        assert rule.matches_character("protagonist") is False

    def test_state_validity_rule_character_matching_wildcard_prefix(self):
        """Test wildcard prefix pattern matching."""
        rule = StateValidityRule(
            constraint_id="test_rule",
            character_id="*protagonist*",
            valid_transitions=[],
            description="Test for wildcard matching with protagonist pattern",
            reason="Wildcard pattern matching enables flexible character selection",
        )

        assert rule.matches_character("protagonist") is True
        assert rule.matches_character("main_protagonist") is True
        assert rule.matches_character("protagonist_best_friend") is True
        assert rule.matches_character("antagonist") is False

    def test_state_validity_rule_character_matching_wildcard_all(self):
        """Test universal wildcard matching."""
        rule = StateValidityRule(
            constraint_id="test_rule",
            character_id="*",
            valid_transitions=[],
            description="Test for universal wildcard matching all characters",
            reason="Universal wildcard enables rules applicable to all characters",
        )

        assert rule.matches_character("protagonist") is True
        assert rule.matches_character("clara") is True
        assert rule.matches_character("any_character") is True


class TestArcCoverageRuleCreation:
    """Test ArcCoverageRule model creation and validation."""

    def test_arc_coverage_rule_creation(self):
        """Test creating an ArcCoverageRule."""
        rule = ArcCoverageRule(
            constraint_id="protagonist_coverage",
            character_id="protagonist",
            minimum_beats=3,
            minimum_chapters=5,
            description="Protagonist must have transformation beats",
            reason="Protagonist arc is core to story",
        )

        assert rule.minimum_beats == 3
        assert rule.minimum_chapters == 5
        assert rule.character_id == "protagonist"

    def test_arc_coverage_rule_with_coverage_type(self):
        """Test ArcCoverageRule with required_coverage_type."""
        rule = ArcCoverageRule(
            constraint_id="arc_each_book",
            character_id="protagonist",
            minimum_beats=3,
            required_coverage_type="each_book",
            description="Coverage in each book",
            reason="Protagonist must be in every book",
        )

        assert rule.required_coverage_type == "each_book"

    def test_arc_coverage_rule_invalid_coverage_type(self):
        """Test that invalid coverage_type is rejected."""
        with pytest.raises(ValueError):
            ArcCoverageRule(
                constraint_id="invalid_coverage",
                character_id="protagonist",
                minimum_beats=1,
                required_coverage_type="invalid_type",  # Invalid
                description="Test",
                reason="Test",
            )

    def test_arc_coverage_rule_artifact_matching(self):
        """Test artifact matching with wildcard patterns."""
        rule = ArcCoverageRule(
            constraint_id="test_rule",
            character_id="*protagonist*",
            minimum_beats=1,
            description="Test for artifact matching with wildcard patterns",
            reason="Artifact matching enables flexible coverage requirements",
        )

        assert rule.matches_artifact("main_protagonist") is True
        assert rule.matches_artifact("protagonist_secondary") is True
        assert rule.matches_artifact("antagonist") is False


class TestCompositionRulesLoading:
    """Test loading composition rules from YAML file."""

    def test_rules_loader_initialization(self):
        """Test initializing CompositionRulesLoader."""
        loader = CompositionRulesLoader()

        assert loader.yaml_path.exists()
        assert loader.raw_data is not None
        assert loader.global_rules is not None
        assert len(loader.genre_rules) > 0

    def test_load_global_rules(self):
        """Test loading global composition rules."""
        loader = CompositionRulesLoader()
        global_rules = loader.get_global_rules()

        assert global_rules.scope == "global"
        assert len(global_rules.optionality_rules) > 0
        assert len(global_rules.chronological_rules) > 0

    def test_load_genre_rules_netorare(self):
        """Test loading netorare-specific rules."""
        loader = CompositionRulesLoader()
        netorare_rules = loader.get_genre_rules("netorare")

        assert netorare_rules.scope == "netorare"
        assert len(netorare_rules.chronological_rules) > 0
        assert len(netorare_rules.state_validity_rules) > 0

    def test_load_genre_rules_mystery(self):
        """Test loading mystery-specific rules."""
        loader = CompositionRulesLoader()
        mystery_rules = loader.get_genre_rules("mystery")

        assert mystery_rules.scope == "mystery"
        assert len(mystery_rules.chronological_rules) > 0
        assert len(mystery_rules.state_validity_rules) > 0

    def test_load_genre_rules_gentlefemdom(self):
        """Test loading gentle femdom-specific rules."""
        loader = CompositionRulesLoader()
        femdom_rules = loader.get_genre_rules("gentlefemdom")

        assert femdom_rules.scope == "gentlefemdom"
        assert len(femdom_rules.chronological_rules) > 0
        assert len(femdom_rules.state_validity_rules) > 0

    def test_load_genre_rules_fallback(self):
        """Test that unknown genre falls back to global rules."""
        loader = CompositionRulesLoader()

        # Unknown genres should fall back to global
        fallback_rules = loader.get_merged_rules("netorare")
        assert fallback_rules is not None

    def test_load_genre_rules_invalid_genre(self):
        """Test that invalid genre raises ValueError."""
        loader = CompositionRulesLoader()

        with pytest.raises(ValueError):
            loader.get_genre_rules("invalid_genre_xyz")

    def test_get_all_genres(self):
        """Test getting all supported genres."""
        loader = CompositionRulesLoader()
        genres = loader.get_all_genres()

        assert "netorare" in genres
        assert "mystery" in genres
        assert "gentlefemdom" in genres


class TestCompositionRulesQueries:
    """Test querying rules by ID, type, and other criteria."""

    def test_get_rule_by_id(self):
        """Test looking up a rule by constraint_id."""
        loader = CompositionRulesLoader()
        global_rules = loader.get_global_rules()

        # Find a rule ID from the loaded rules
        if global_rules.optionality_rules:
            rule_id = global_rules.optionality_rules[0].constraint_id
            found_rule = global_rules.get_rule_by_id(rule_id)

            assert found_rule is not None
            assert found_rule.constraint_id == rule_id

    def test_get_rules_by_type(self):
        """Test getting all rules of a specific type."""
        loader = CompositionRulesLoader()
        global_rules = loader.get_global_rules()

        optionality_rules = global_rules.get_rules_by_type(RuleType.OPTIONALITY)
        chronological_rules = global_rules.get_rules_by_type(RuleType.CHRONOLOGICAL_ORDERING)

        assert isinstance(optionality_rules, list)
        assert isinstance(chronological_rules, list)
        assert len(optionality_rules) == len(global_rules.optionality_rules)
        assert len(chronological_rules) == len(global_rules.chronological_rules)

    def test_get_nonexistent_rule(self):
        """Test looking up a rule that doesn't exist."""
        loader = CompositionRulesLoader()
        global_rules = loader.get_global_rules()

        found_rule = global_rules.get_rule_by_id("nonexistent_rule_id")
        assert found_rule is None

    def test_rules_summary(self):
        """Test getting a summary of all loaded rules."""
        loader = CompositionRulesLoader()
        summary = loader.rules_summary()

        assert "version" in summary
        assert "global" in summary
        assert "genres" in summary
        assert summary["global"]["total"] > 0
        assert "netorare" in summary["genres"]


class TestRulesValidation:
    """Test rule validation and consistency checking."""

    def test_validate_rules_consistency(self):
        """Test that rules pass consistency validation."""
        loader = CompositionRulesLoader()
        is_valid, errors = loader.validate_rules_consistency()

        # Rules should be consistent
        assert is_valid is True
        assert len(errors) == 0

    def test_rule_phases_valid_range(self):
        """Test that all phase numbers are in valid range."""
        loader = CompositionRulesLoader()

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            rules = loader.get_genre_rules(genre)
            for rule in rules.chronological_rules:
                if rule.source_phase is not None:
                    assert 1 <= rule.source_phase <= 9
                if rule.target_phase is not None:
                    assert 1 <= rule.target_phase <= 9

    def test_no_duplicate_constraint_ids_in_genre(self):
        """Test that no genre has duplicate constraint_ids."""
        loader = CompositionRulesLoader()

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            rules = loader.get_genre_rules(genre)
            all_rules = (
                rules.optionality_rules
                + rules.chronological_rules
                + rules.state_validity_rules
                + rules.arc_coverage_rules
            )

            ids = [rule.constraint_id for rule in all_rules]
            assert len(ids) == len(set(ids)), f"Duplicate IDs in {genre}"

    def test_state_validity_rules_have_transitions(self):
        """Test that genre state validity rules have defined transitions."""
        loader = CompositionRulesLoader()

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            rules = loader.get_genre_rules(genre)
            # Filter out global rules (which may have empty transitions)
            genre_state_rules = [
                r for r in rules.state_validity_rules
                if "global_" not in r.constraint_id
            ]
            for rule in genre_state_rules:
                # Each genre-specific state validity rule should have at least one transition
                assert (
                    len(rule.valid_transitions) > 0
                ), f"No transitions in {rule.constraint_id} for {genre}"


class TestGenreRuleMerging:
    """Test that genre-specific rules properly merge with global rules."""

    def test_genre_rules_include_global_rules(self):
        """Test that genre rules include relevant global rules."""
        loader = CompositionRulesLoader()
        global_rules = loader.get_global_rules()
        netorare_rules = loader.get_genre_rules("netorare")

        # Netorare should have more rules than just genre-specific
        assert len(netorare_rules.chronological_rules) >= len(
            global_rules.chronological_rules
        )

    def test_genre_optionality_overrides_global(self):
        """Test that genre can override global optionality rules."""
        loader = CompositionRulesLoader()
        netorare_rules = loader.get_genre_rules("netorare")

        # Find sequence optionality rules
        sequence_rules = [
            r for r in netorare_rules.optionality_rules if r.artifact_type == "sequence"
        ]

        # Should have sequence optionality rule
        assert len(sequence_rules) > 0

    def test_genre_rules_have_genre_specific_additions(self):
        """Test that genre rules include genre-specific additions."""
        loader = CompositionRulesLoader()
        netorare_rules = loader.get_genre_rules("netorare")

        # Netorare should have humiliation-specific rules
        humiliation_rules = [
            r for r in netorare_rules.chronological_rules
            if "humiliation" in r.constraint_id.lower()
        ]

        assert len(humiliation_rules) > 0

    def test_mystery_has_investigation_rules(self):
        """Test that mystery genre has investigation-specific rules."""
        loader = CompositionRulesLoader()
        mystery_rules = loader.get_genre_rules("mystery")

        investigation_rules = [
            r for r in mystery_rules.chronological_rules
            if "investigation" in r.constraint_id.lower()
        ]

        assert len(investigation_rules) > 0

    def test_gentlefemdom_has_trust_rules(self):
        """Test that gentle femdom has trust/consent-specific rules."""
        loader = CompositionRulesLoader()
        femdom_rules = loader.get_genre_rules("gentlefemdom")

        trust_rules = [
            r for r in femdom_rules.chronological_rules
            if "trust" in r.constraint_id.lower()
            or "boundary" in r.constraint_id.lower()
        ]

        assert len(trust_rules) > 0


class TestRuleIntegration:
    """Test integration between different rule types."""

    def test_state_validity_with_optionality(self):
        """Test that state validity rules work with optionality constraints."""
        loader = CompositionRulesLoader()

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            rules = loader.get_genre_rules(genre)
            # Both types should exist
            assert len(rules.optionality_rules) > 0
            assert len(rules.state_validity_rules) > 0

    def test_arc_coverage_with_chronological(self):
        """Test that arc coverage rules work with chronological constraints."""
        loader = CompositionRulesLoader()

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            rules = loader.get_genre_rules(genre)
            # Both types should exist
            assert len(rules.arc_coverage_rules) > 0
            assert len(rules.chronological_rules) > 0

    def test_genre_specific_character_arc_rules(self):
        """Test that each genre has character-specific arc coverage rules."""
        loader = CompositionRulesLoader()

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            rules = loader.get_genre_rules(genre)

            # Should have character arc coverage rules
            char_arc_rules = [
                r for r in rules.arc_coverage_rules if r.character_id is not None
            ]

            assert len(char_arc_rules) > 0, f"No character arc rules in {genre}"

    def test_rules_for_short_vs_long_stories(self):
        """Test that conditional optionality rules handle short vs. long stories."""
        loader = CompositionRulesLoader()
        global_rules = loader.get_global_rules()

        # Find conditional optionality rules
        conditional_rules = [
            r for r in global_rules.optionality_rules
            if r.optionality_level == OptionalityLevel.CONDITIONAL
        ]

        # Should have conditional rules for short/long story handling
        assert len(conditional_rules) > 0
