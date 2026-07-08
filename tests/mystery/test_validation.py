"""Tests for Mystery genre validation rules."""

import pytest
from auteur.mystery.core_templates import (
    HowdunitTemplate, ParanoiaTemplate, CozyTemplate
)
from auteur.mystery.validation import validate_choices, RuleSet, ValidationRule


class TestHowdunitValidationRules:
    """Test validation rules specific to Howdunit."""

    def test_howdunit_want_not_equal_change(self):
        """Howdunit: Want and Change must differ."""
        template = HowdunitTemplate()
        # Valid: want ≠ change
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "detective"},
            4: {
                "want": "want-solve-puzzle",
                "resistance": "resistance-misleading-clues",
                "conflict": "conflict-deduction-misdirection",
                "stakes": "stakes-justice",
                "change": "change-clarity"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True, f"Valid howdunit choices failed: {errors}"

    def test_howdunit_want_equal_change_fails(self):
        """Howdunit: Want and Change cannot be identical (validation error)."""
        template = HowdunitTemplate()
        choices = {
            1: {"emotional_core": "howdunit"},
            4: {
                "want": "want-solve-puzzle",
                "resistance": "resistance-misleading-clues",
                "conflict": "conflict-deduction-misdirection",
                "stakes": "stakes-justice",
                "change": "want-solve-puzzle"  # Same as want - should fail
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is False
        assert any("cannot be the same" in err.lower() for err in errors)

    def test_howdunit_red_herring_coherence(self):
        """Howdunit: Red herrings must not contradict solution."""
        template = HowdunitTemplate()
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "puzzle-box"},
            7: {"clue_distribution": "early-heavy"},
        }
        # This should pass; red herring coherence is checked by rule
        is_valid, errors, warnings = validate_choices(template, choices)
        # Should not error on missing layer 4 (optional layers)
        assert is_valid is True

    def test_howdunit_puzzle_box_late_clues_fails(self):
        """Howdunit: Puzzle-box with late-heavy clues fails coherence check."""
        template = HowdunitTemplate()
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "puzzle-box"},
            7: {"clue_distribution": "late-heavy"},
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is False
        assert any("clue" in err.lower() for err in errors)

    def test_howdunit_solution_derivable(self):
        """Howdunit: Solution must be theoretically discoverable."""
        template = HowdunitTemplate()
        choices = {
            1: {"emotional_core": "howdunit"},
            8: {"solution_density": "tight"},  # Reader can barely derive solution
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        # Tight solution density is valid (by itself)
        assert is_valid is True

    def test_howdunit_tight_solution_late_clues_fails(self):
        """Howdunit: Tight solution with late clue distribution fails."""
        template = HowdunitTemplate()
        choices = {
            1: {"emotional_core": "howdunit"},
            7: {"clue_distribution": "late-heavy"},
            8: {"solution_density": "tight"},
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is False
        assert any("distribution" in err.lower() for err in errors)


class TestParanoiaValidationRules:
    """Test validation rules specific to Paranoia."""

    def test_paranoia_want_not_equal_change(self):
        """Paranoia: Want and Change must differ."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            2: {"genre_contract": "gaslight"},
            4: {
                "want": "want-understand-reality",
                "resistance": "resistance-gaslighting",
                "conflict": "conflict-reality-perception",
                "stakes": "stakes-mental-stability",
                "change": "change-revelation"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_paranoia_want_equal_change_fails(self):
        """Paranoia: Want and Change cannot be identical."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            4: {
                "want": "want-escape-situation",
                "resistance": "resistance-gaslighting",
                "conflict": "conflict-reality-perception",
                "stakes": "stakes-mental-stability",
                "change": "want-escape-situation"  # Same as want - should fail
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is False
        assert any("cannot be the same" in err.lower() for err in errors)

    def test_paranoia_narrator_inconsistency_deliberate(self):
        """Paranoia: Narrator inconsistencies must be intentional."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            5: {"narrator_reliability": "highly-unreliable"},  # Intentional unreliability
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_paranoia_unreliable_narrator_with_fully_revealed_fails(self):
        """Paranoia: Unreliable narrator cannot have fully revealed truth."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            5: {"narrator_reliability": "highly-unreliable"},
            8: {"truth_ambiguity": "fully-revealed"},  # Contradicts unreliable narrator
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is False
        assert any("unreliable" in err.lower() or "fully revealed" in err.lower() for err in errors)

    def test_paranoia_paranoia_escalates(self):
        """Paranoia: Dread/paranoia must escalate logically."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            7: {"paranoia_escalation": "rapid-spiral"},  # Escalates logically
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_paranoia_institutional_gaslighting_slow_build_fails(self):
        """Paranoia: Institutional gaslighting should not have slow build."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            6: {"gaslighting_intensity": "institutional"},
            7: {"paranoia_escalation": "slow-build"},  # Contradicts institutional
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is False
        assert any("escalat" in err.lower() or "institutional" in err.lower() for err in errors)


class TestCozyValidationRules:
    """Test validation rules specific to Cozy."""

    def test_cozy_violence_budget_respected(self):
        """Cozy: Violence must stay within declared budget."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            2: {"genre_contract": "village"},
            7: {"violence_budget": "off-page"},  # Off-page is acceptable
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_cozy_violence_budget_none(self):
        """Cozy: Violence can be none (no violence)."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            7: {"violence_budget": "none"},  # None is acceptable
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_cozy_violence_budget_minimal(self):
        """Cozy: Violence can be minimal (non-graphic)."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            7: {"violence_budget": "minimal"},  # Minimal is acceptable
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_cozy_tone_consistency(self):
        """Cozy: Warm tone must be maintained."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            5: {"humor_level": "light-humor"},  # Maintains warmth
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_cozy_dark_humor_very_cozy_fails(self):
        """Cozy: Dark humor contradicts 'very cozy' tone."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            5: {"humor_level": "dark-undertone"},
            9: {"warmth_confidence": "very-cozy"},
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is False
        assert any("dark" in err.lower() or "tone" in err.lower() for err in errors)

    def test_cozy_dark_humor_restored_coziness(self):
        """Cozy: Dark humor with restored coziness works."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            5: {"humor_level": "dark-undertone"},
            9: {"warmth_confidence": "restored-coziness"},
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_cozy_community_relationships_nuanced(self):
        """Cozy: Community relationships must be complex, not binary."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            6: {"relationship_focus": "community-web"},  # Complex relationships
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_cozy_community_web_protagonist_solves_fails(self):
        """Cozy: Community-web relationships should involve community in solution."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            6: {"relationship_focus": "community-web"},
            8: {"community_role": "protagonist-solves"},  # Contradicts community-web
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is False
        assert any("community" in err.lower() for err in errors)

    def test_cozy_community_web_community_involved(self):
        """Cozy: Community-web with community involvement works."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            6: {"relationship_focus": "community-web"},
            8: {"community_role": "community-involved"},
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True


class TestValidationIntegration:
    """Integration tests for validation across all three cores."""

    def test_validate_choices_function_exists(self):
        """Test that validate_choices function is callable."""
        template = HowdunitTemplate()
        choices = {1: {"emotional_core": "howdunit"}}
        result = validate_choices(template, choices)
        assert isinstance(result, tuple)
        assert len(result) == 3
        is_valid, errors, warnings = result
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
        assert isinstance(warnings, list)

    def test_ruleset_for_howdunit(self):
        """Test RuleSet instantiation for Howdunit."""
        ruleset = RuleSet("howdunit")
        assert len(ruleset.rules) > 0

    def test_ruleset_for_paranoia(self):
        """Test RuleSet instantiation for Paranoia."""
        ruleset = RuleSet("paranoia")
        assert len(ruleset.rules) > 0

    def test_ruleset_for_cozy(self):
        """Test RuleSet instantiation for Cozy."""
        ruleset = RuleSet("cozy")
        assert len(ruleset.rules) > 0

    def test_all_cores_produce_errors_list_on_validation(self):
        """Test that validation always returns (bool, list, list)."""
        for core_id, TemplateClass in [
            ("howdunit", HowdunitTemplate),
            ("paranoia", ParanoiaTemplate),
            ("cozy", CozyTemplate)
        ]:
            template = TemplateClass()
            choices = {1: {"emotional_core": core_id}}
            is_valid, errors, warnings = validate_choices(template, choices)
            assert isinstance(errors, list)
            assert isinstance(warnings, list)
