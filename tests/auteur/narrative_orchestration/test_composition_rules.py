"""Comprehensive tests for composition constraints (Layer 2.5 Task 3).

Tests cover all constraint types:
- Optionality constraints
- Chronological ordering constraints
- State validity constraints
- Arc coverage constraints
- Genre-specific constraint sets
"""

import pytest

from auteur.narrative_orchestration.schema.composition_rules import (
    ArcCoverageConstraint,
    ArtifactType,
    ChronologicalOrderingConstraint,
    CompositionConstraintSet,
    ConstraintViolation,
    OptionalityConstraint,
    OptionalityLevel,
    StateTransition,
    StateValidityConstraint,
    create_gentlefemdom_constraints,
    create_mystery_constraints,
    create_netorare_constraints,
    get_constraints_for_genre,
)


class TestOptionalityConstraint:
    """Test optionality constraints."""

    def test_required_artifact_present_passes(self):
        """Required artifact present should pass evaluation."""
        constraint = OptionalityConstraint(
            constraint_id="test_required",
            artifact_type=ArtifactType.CHAPTER,
            optionality_level=OptionalityLevel.REQUIRED,
        )

        artifacts = [
            {"type": "chapter", "id": "ch_1"},
            {"type": "chapter", "id": "ch_2"},
        ]

        evaluation = constraint.evaluate(artifacts)

        assert evaluation.is_satisfied is True
        assert len(evaluation.violations) == 0

    def test_required_artifact_missing_fails(self):
        """Missing required artifact should fail evaluation."""
        constraint = OptionalityConstraint(
            constraint_id="test_required",
            artifact_type=ArtifactType.CHAPTER,
            optionality_level=OptionalityLevel.REQUIRED,
        )

        artifacts = [
            {"type": "sequence", "id": "seq_1"},
        ]

        evaluation = constraint.evaluate(artifacts)

        assert evaluation.is_satisfied is False
        assert len(evaluation.violations) == 1
        assert "missing" in evaluation.violations[0].message.lower()

    def test_optional_artifact_missing_passes(self):
        """Missing optional artifact should pass evaluation."""
        constraint = OptionalityConstraint(
            constraint_id="test_optional",
            artifact_type=ArtifactType.SEQUENCE,
            optionality_level=OptionalityLevel.OPTIONAL,
        )

        artifacts = [
            {"type": "chapter", "id": "ch_1"},
        ]

        evaluation = constraint.evaluate(artifacts)

        assert evaluation.is_satisfied is True
        assert len(evaluation.violations) == 0

    def test_optional_artifact_present_passes(self):
        """Optional artifact present should pass evaluation."""
        constraint = OptionalityConstraint(
            constraint_id="test_optional",
            artifact_type=ArtifactType.SEQUENCE,
            optionality_level=OptionalityLevel.OPTIONAL,
        )

        artifacts = [
            {"type": "sequence", "id": "seq_1"},
            {"type": "chapter", "id": "ch_1"},
        ]

        evaluation = constraint.evaluate(artifacts)

        assert evaluation.is_satisfied is True
        assert len(evaluation.violations) == 0

    def test_conditional_artifact_optionality(self):
        """Conditional optionality can be specified."""
        constraint = OptionalityConstraint(
            constraint_id="test_conditional",
            artifact_type=ArtifactType.SEQUENCE,
            optionality_level=OptionalityLevel.CONDITIONAL,
            condition="Optional if book has fewer than 8 chapters",
        )

        assert constraint.optionality_level == OptionalityLevel.CONDITIONAL
        assert "fewer than 8" in constraint.condition


class TestChronologicalOrderingConstraint:
    """Test chronological ordering constraints."""

    def test_valid_phase_ordering(self):
        """Valid phase ordering should pass evaluation."""
        constraint = ChronologicalOrderingConstraint(
            constraint_id="test_ordering",
            name="setup_before_payoff",
            source_artifact="setup_ch_1",
            source_phase=2,
            target_artifact="payoff_ch_5",
            target_phase=6,
            description="Setup must occur before payoff",
        )

        artifacts = {
            "setup_ch_1": {"id": "setup_ch_1", "phase": 2},
            "payoff_ch_5": {"id": "payoff_ch_5", "phase": 6},
        }
        ordering = {"setup_ch_1": 1, "payoff_ch_5": 2}

        evaluation = constraint.evaluate(artifacts, ordering)

        assert evaluation.is_satisfied is True
        assert len(evaluation.violations) == 0

    def test_invalid_phase_ordering(self):
        """Invalid phase ordering should fail evaluation."""
        constraint = ChronologicalOrderingConstraint(
            constraint_id="test_ordering",
            name="setup_before_payoff",
            source_artifact="payoff_ch_5",
            source_phase=6,
            target_artifact="setup_ch_1",
            target_phase=2,
            description="Setup must occur before payoff",
        )

        artifacts = {
            "payoff_ch_5": {"id": "payoff_ch_5", "phase": 6},
            "setup_ch_1": {"id": "setup_ch_1", "phase": 2},
        }
        ordering = {"payoff_ch_5": 2, "setup_ch_1": 1}

        evaluation = constraint.evaluate(artifacts, ordering)

        assert evaluation.is_satisfied is False
        assert len(evaluation.violations) == 1
        assert "violation" in evaluation.violations[0].message.lower()

    def test_missing_source_artifact(self):
        """Missing source artifact should fail with error."""
        constraint = ChronologicalOrderingConstraint(
            constraint_id="test_ordering",
            name="missing_source",
            source_artifact="missing_setup",
            target_artifact="payoff_ch_5",
            description="Test missing source",
        )

        artifacts = {
            "payoff_ch_5": {"id": "payoff_ch_5"},
        }
        ordering = {}

        evaluation = constraint.evaluate(artifacts, ordering)

        assert evaluation.is_satisfied is False
        assert "source" in evaluation.violations[0].message.lower()
        assert "not found" in evaluation.violations[0].message.lower()

    def test_missing_target_artifact(self):
        """Missing target artifact should fail with error."""
        constraint = ChronologicalOrderingConstraint(
            constraint_id="test_ordering",
            name="missing_target",
            source_artifact="setup_ch_1",
            target_artifact="missing_payoff",
            description="Test missing target",
        )

        artifacts = {
            "setup_ch_1": {"id": "setup_ch_1"},
        }
        ordering = {}

        evaluation = constraint.evaluate(artifacts, ordering)

        assert evaluation.is_satisfied is False
        assert "target" in evaluation.violations[0].message.lower()

    def test_phase_validation(self):
        """Phase must be in range 1-9."""
        with pytest.raises(ValueError, match="phase must be between 1 and 9"):
            ChronologicalOrderingConstraint(
                constraint_id="test",
                name="test",
                source_artifact="s",
                source_phase=0,
                target_artifact="t",
                description="test",
            )

        with pytest.raises(ValueError, match="phase must be between 1 and 9"):
            ChronologicalOrderingConstraint(
                constraint_id="test",
                name="test",
                source_artifact="s",
                target_artifact="t",
                target_phase=10,
                description="test",
            )

    def test_same_phase_ordering_fails(self):
        """Same phase for setup and payoff should fail."""
        constraint = ChronologicalOrderingConstraint(
            constraint_id="test_ordering",
            name="same_phase",
            source_artifact="setup_ch_1",
            source_phase=5,
            target_artifact="payoff_ch_2",
            target_phase=5,
            description="Must be different phases",
        )

        artifacts = {
            "setup_ch_1": {"id": "setup_ch_1", "phase": 5},
            "payoff_ch_2": {"id": "payoff_ch_2", "phase": 5},
        }
        ordering = {"setup_ch_1": 1, "payoff_ch_2": 2}

        evaluation = constraint.evaluate(artifacts, ordering)

        assert evaluation.is_satisfied is False


class TestStateValidityConstraint:
    """Test state validity constraints."""

    def test_valid_state_transition(self):
        """Valid state transitions should pass evaluation."""
        constraint = StateValidityConstraint(
            constraint_id="test_state",
            character_id="protagonist",
            valid_transitions=[
                StateTransition(
                    from_state="trust",
                    to_state="doubt",
                    description="Can shift from trust to doubt",
                ),
                StateTransition(
                    from_state="doubt",
                    to_state="acceptance",
                    description="Can shift from doubt to acceptance",
                ),
            ],
            description="Valid protagonist state transitions",
        )

        character_states = {
            "protagonist": ["trust", "doubt", "acceptance"],
        }

        evaluation = constraint.evaluate(character_states)

        assert evaluation.is_satisfied is True
        assert len(evaluation.violations) == 0

    def test_invalid_state_transition(self):
        """Invalid state transitions should fail evaluation."""
        constraint = StateValidityConstraint(
            constraint_id="test_state",
            character_id="protagonist",
            valid_transitions=[
                StateTransition(
                    from_state="trust",
                    to_state="doubt",
                    description="Can shift from trust to doubt",
                ),
            ],
            description="Valid protagonist state transitions",
        )

        character_states = {
            "protagonist": ["trust", "acceptance"],  # Invalid: trust -> acceptance not allowed
        }

        evaluation = constraint.evaluate(character_states)

        assert evaluation.is_satisfied is False
        assert len(evaluation.violations) == 1
        assert "invalid" in evaluation.violations[0].message.lower()

    def test_single_state_is_valid(self):
        """Single state (no transitions) should be valid."""
        constraint = StateValidityConstraint(
            constraint_id="test_state",
            character_id="character",
            valid_transitions=[],
            description="Test single state",
        )

        character_states = {
            "character": ["initial_state"],
        }

        evaluation = constraint.evaluate(character_states)

        assert evaluation.is_satisfied is True

    def test_missing_character_is_valid(self):
        """Missing character should be treated as valid."""
        constraint = StateValidityConstraint(
            constraint_id="test_state",
            character_id="missing_char",
            valid_transitions=[],
            description="Test missing character",
        )

        character_states = {}

        evaluation = constraint.evaluate(character_states)

        assert evaluation.is_satisfied is True

    def test_empty_state_list_is_valid(self):
        """Empty state list should be valid."""
        constraint = StateValidityConstraint(
            constraint_id="test_state",
            character_id="character",
            valid_transitions=[],
            description="Test empty state",
        )

        character_states = {
            "character": [],
        }

        evaluation = constraint.evaluate(character_states)

        assert evaluation.is_satisfied is True


class TestArcCoverageConstraint:
    """Test arc coverage constraints."""

    def test_sufficient_arc_beats(self):
        """Arc with sufficient beats should pass evaluation."""
        constraint = ArcCoverageConstraint(
            constraint_id="test_arc",
            character_id="protagonist",
            minimum_beats=3,
            description="Protagonist needs 3+ turning points",
        )

        character_arcs = {
            "protagonist": {
                "beats": ["beat_1", "beat_2", "beat_3"],
                "chapters": ["ch_1", "ch_5", "ch_9"],
            },
        }

        evaluation = constraint.evaluate(character_arcs)

        assert evaluation.is_satisfied is True
        assert len(evaluation.violations) == 0

    def test_insufficient_arc_beats(self):
        """Arc with insufficient beats should fail evaluation."""
        constraint = ArcCoverageConstraint(
            constraint_id="test_arc",
            character_id="protagonist",
            minimum_beats=3,
            description="Protagonist needs 3+ turning points",
        )

        character_arcs = {
            "protagonist": {
                "beats": ["beat_1"],
                "chapters": ["ch_1"],
            },
        }

        evaluation = constraint.evaluate(character_arcs)

        assert evaluation.is_satisfied is False
        assert len(evaluation.violations) == 1
        assert "only 1 beats" in evaluation.violations[0].message

    def test_required_chapter_coverage(self):
        """Arc must have beats in required chapters."""
        constraint = ArcCoverageConstraint(
            constraint_id="test_arc",
            character_id="protagonist",
            required_coverage={"ch_1", "ch_5", "ch_9"},
            minimum_beats=3,
            description="Protagonist needs beats in chapters 1, 5, 9",
        )

        character_arcs = {
            "protagonist": {
                "beats": ["beat_1", "beat_2", "beat_3"],
                "chapters": ["ch_1", "ch_2", "ch_3"],  # Missing ch_5 and ch_9
            },
        }

        evaluation = constraint.evaluate(character_arcs)

        assert evaluation.is_satisfied is False
        assert len(evaluation.violations) == 1
        assert "ch_5" in evaluation.violations[0].message
        assert "ch_9" in evaluation.violations[0].message

    def test_missing_character_arc(self):
        """Missing character arc should fail evaluation."""
        constraint = ArcCoverageConstraint(
            constraint_id="test_arc",
            character_id="protagonist",
            minimum_beats=3,
            description="Protagonist needs 3+ turning points",
        )

        character_arcs = {}

        evaluation = constraint.evaluate(character_arcs)

        assert evaluation.is_satisfied is False
        assert len(evaluation.violations) == 1
        assert "not found" in evaluation.violations[0].message


class TestCompositionConstraintSet:
    """Test composition constraint sets."""

    def test_create_empty_constraint_set(self):
        """Create empty constraint set for a genre."""
        constraint_set = CompositionConstraintSet(genre="mystery")

        assert constraint_set.genre == "mystery"
        assert len(constraint_set.optionality_constraints) == 0
        assert len(constraint_set.chronological_constraints) == 0
        assert len(constraint_set.state_validity_constraints) == 0
        assert len(constraint_set.arc_coverage_constraints) == 0

    def test_add_optionality_constraint(self):
        """Add optionality constraint to set."""
        constraint_set = CompositionConstraintSet(genre="mystery")
        constraint = OptionalityConstraint(
            constraint_id="test",
            artifact_type=ArtifactType.CHAPTER,
            optionality_level=OptionalityLevel.REQUIRED,
        )

        constraint_set.add_optionality_constraint(constraint)

        assert len(constraint_set.optionality_constraints) == 1
        assert constraint_set.optionality_constraints[0].constraint_id == "test"

    def test_add_chronological_constraint(self):
        """Add chronological constraint to set."""
        constraint_set = CompositionConstraintSet(genre="mystery")
        constraint = ChronologicalOrderingConstraint(
            constraint_id="test",
            name="test",
            source_artifact="a",
            target_artifact="b",
            description="test",
        )

        constraint_set.add_chronological_constraint(constraint)

        assert len(constraint_set.chronological_constraints) == 1

    def test_add_state_validity_constraint(self):
        """Add state validity constraint to set."""
        constraint_set = CompositionConstraintSet(genre="mystery")
        constraint = StateValidityConstraint(
            constraint_id="test",
            character_id="char",
            description="test",
        )

        constraint_set.add_state_validity_constraint(constraint)

        assert len(constraint_set.state_validity_constraints) == 1

    def test_add_arc_coverage_constraint(self):
        """Add arc coverage constraint to set."""
        constraint_set = CompositionConstraintSet(genre="mystery")
        constraint = ArcCoverageConstraint(
            constraint_id="test",
            character_id="char",
            description="test",
        )

        constraint_set.add_arc_coverage_constraint(constraint)

        assert len(constraint_set.arc_coverage_constraints) == 1

    def test_evaluate_all_constraints(self):
        """Evaluate all constraints in a set."""
        constraint_set = CompositionConstraintSet(genre="mystery")
        constraint_set.add_optionality_constraint(
            OptionalityConstraint(
                constraint_id="opt_1",
                artifact_type=ArtifactType.CHAPTER,
                optionality_level=OptionalityLevel.REQUIRED,
            )
        )

        artifacts = [{"type": "chapter", "id": "ch_1"}]
        all_satisfied, evaluations = constraint_set.evaluate_all(
            artifacts=artifacts,
            artifact_ordering={"ch_1": 0},
            character_states={},
            character_arcs={},
        )

        assert all_satisfied is True
        assert len(evaluations) == 1
        assert evaluations[0].is_satisfied is True


class TestGenreSpecificConstraints:
    """Test genre-specific constraint sets."""

    def test_create_netorare_constraints(self):
        """Create netorare genre constraint set."""
        constraint_set = create_netorare_constraints()

        assert constraint_set.genre == "netorare"
        assert len(constraint_set.optionality_constraints) > 0
        assert len(constraint_set.chronological_constraints) > 0
        assert len(constraint_set.arc_coverage_constraints) > 0

    def test_create_mystery_constraints(self):
        """Create mystery genre constraint set."""
        constraint_set = create_mystery_constraints()

        assert constraint_set.genre == "mystery"
        assert len(constraint_set.optionality_constraints) > 0
        assert len(constraint_set.chronological_constraints) > 0
        assert len(constraint_set.arc_coverage_constraints) > 0

    def test_create_gentlefemdom_constraints(self):
        """Create gentle femdom genre constraint set."""
        constraint_set = create_gentlefemdom_constraints()

        assert constraint_set.genre == "gentlefemdom"
        assert len(constraint_set.optionality_constraints) > 0
        assert len(constraint_set.chronological_constraints) > 0
        assert len(constraint_set.arc_coverage_constraints) > 0

    def test_get_constraints_for_genre_netorare(self):
        """Get netorare constraints via factory function."""
        constraint_set = get_constraints_for_genre("netorare")

        assert constraint_set.genre == "netorare"
        assert len(constraint_set.optionality_constraints) > 0

    def test_get_constraints_for_genre_mystery(self):
        """Get mystery constraints via factory function."""
        constraint_set = get_constraints_for_genre("mystery")

        assert constraint_set.genre == "mystery"

    def test_get_constraints_for_genre_gentlefemdom(self):
        """Get gentle femdom constraints via factory function."""
        constraint_set = get_constraints_for_genre("gentlefemdom")

        assert constraint_set.genre == "gentlefemdom"

    def test_get_constraints_for_unknown_genre(self):
        """Getting constraints for unknown genre should raise error."""
        with pytest.raises(ValueError, match="Unknown genre"):
            get_constraints_for_genre("unknown_genre")

    def test_netorare_sequence_optionality(self):
        """Netorare allows optional sequences."""
        constraint_set = create_netorare_constraints()

        # Find sequence constraint
        seq_constraint = next(
            (c for c in constraint_set.optionality_constraints
             if c.artifact_type == ArtifactType.SEQUENCE),
            None,
        )

        assert seq_constraint is not None
        assert seq_constraint.optionality_level == OptionalityLevel.OPTIONAL

    def test_netorare_chapter_required(self):
        """Netorare requires chapters."""
        constraint_set = create_netorare_constraints()

        # Find chapter constraint
        ch_constraint = next(
            (c for c in constraint_set.optionality_constraints
             if c.artifact_type == ArtifactType.CHAPTER),
            None,
        )

        assert ch_constraint is not None
        assert ch_constraint.optionality_level == OptionalityLevel.REQUIRED

    def test_mystery_has_investigation_ordering(self):
        """Mystery genre has investigation ordering constraints."""
        constraint_set = create_mystery_constraints()

        # Find investigation constraint
        inv_constraint = next(
            (c for c in constraint_set.chronological_constraints
             if "investigation" in c.name.lower()),
            None,
        )

        assert inv_constraint is not None
        assert "before" in inv_constraint.description.lower()

    def test_gentlefemdom_trust_before_surrender(self):
        """Gentle femdom has trust-before-surrender ordering."""
        constraint_set = create_gentlefemdom_constraints()

        # Find trust constraint
        trust_constraint = next(
            (c for c in constraint_set.chronological_constraints
             if "trust" in c.name.lower()),
            None,
        )

        assert trust_constraint is not None
        assert "surrender" in trust_constraint.description.lower()


class TestConstraintViolation:
    """Test constraint violation reporting."""

    def test_create_constraint_violation(self):
        """Create constraint violation with severity."""
        violation = ConstraintViolation(
            constraint_id="test",
            constraint_type="chronological_ordering",
            artifact_id="ch_1",
            message="Setup must occur before payoff",
            severity="error",
        )

        assert violation.constraint_id == "test"
        assert violation.severity == "error"

    def test_constraint_violation_warning_severity(self):
        """Constraint violation can have warning severity."""
        violation = ConstraintViolation(
            constraint_id="test",
            constraint_type="state_validity",
            artifact_id="char",
            message="Consider this state transition",
            severity="warning",
        )

        assert violation.severity == "warning"

    def test_constraint_violation_invalid_severity(self):
        """Invalid severity should raise validation error."""
        with pytest.raises(ValueError):
            ConstraintViolation(
                constraint_id="test",
                constraint_type="test",
                artifact_id="a",
                message="test",
                severity="invalid",
            )


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_constraint_with_empty_artifact_list(self):
        """Evaluate constraint with empty artifact list."""
        constraint = OptionalityConstraint(
            constraint_id="test",
            artifact_type=ArtifactType.CHAPTER,
            optionality_level=OptionalityLevel.REQUIRED,
        )

        evaluation = constraint.evaluate([])

        assert evaluation.is_satisfied is False

    def test_multiple_violations_in_arc_coverage(self):
        """Arc coverage can have multiple violations."""
        constraint = ArcCoverageConstraint(
            constraint_id="test_arc",
            character_id="protagonist",
            required_coverage={"ch_1", "ch_5", "ch_9"},
            minimum_beats=5,
            description="Protagonist needs 5+ turning points in specific chapters",
        )

        character_arcs = {
            "protagonist": {
                "beats": ["beat_1"],  # Only 1 beat, needs 5
                "chapters": ["ch_2"],  # Wrong chapters
            },
        }

        evaluation = constraint.evaluate(character_arcs)

        assert evaluation.is_satisfied is False
        assert len(evaluation.violations) == 2  # Two violations: beats and coverage

    def test_state_transition_with_multiple_invalid_transitions(self):
        """Multiple invalid transitions should generate multiple violations."""
        constraint = StateValidityConstraint(
            constraint_id="test_state",
            character_id="character",
            valid_transitions=[
                StateTransition(
                    from_state="A",
                    to_state="B",
                    description="A to B",
                ),
            ],
            description="Test",
        )

        character_states = {
            "character": ["A", "C", "D", "E"],  # A->C invalid, C->D invalid, D->E invalid
        }

        evaluation = constraint.evaluate(character_states)

        assert evaluation.is_satisfied is False
        assert len(evaluation.violations) >= 2  # At least 2 violations
