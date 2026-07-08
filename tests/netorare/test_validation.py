"""Tests for deterministic validation rules engine."""

import pytest
from auteur.netorare.validation import validate_choices, ValidationError
from auteur.netorare.core_templates import HumiliationTemplate, HorrorTemplate, MysteryTemplate


class TestHumiliationValidation:
    """Tests for humiliation-specific validation rules."""

    def test_want_not_equal_change_rule(self):
        """Layer 4: Want cannot equal Change."""
        template = HumiliationTemplate()
        choices = {
            4: {"want": "want-dignity", "change": "want-dignity"}  # INVALID: same
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert any("want" in e.lower() and "change" in e.lower() for e in errors)

    def test_valid_want_change_passes(self):
        """Valid want/change combination passes."""
        template = HumiliationTemplate()
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-inadequacy",
                "change": "change-accept"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid
        assert len(errors) == 0

    def test_incompatible_want_resistance_warns(self):
        """Uncommon want/resistance pairing generates warning."""
        template = HumiliationTemplate()
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-no-one-believes",  # Uncommon for this want
                "change": "change-accept"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid  # Still valid, but warns
        assert len(warnings) > 0

    def test_resistance_blocks_want_invalid(self):
        """Resistance must create genuine obstacle to want."""
        template = HumiliationTemplate()
        choices = {
            4: {
                "want": "want-prove-love",
                "resistance": "resistance-inadequacy",  # Doesn't block prove-love
                "change": "change-accept"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert any("resistance" in e.lower() for e in errors)

    def test_forbidden_pacing_mc_wins(self):
        """Humiliation cannot end with MC winning."""
        template = HumiliationTemplate()
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-inadequacy",
                "change": "change-accept"
            },
            7: {
                "pacing": "pacing-mc-wins"  # Forbidden
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert any("forbidden" in e.lower() or "mc" in e.lower() for e in errors)


class TestHorrorValidation:
    """Tests for horror-specific validation rules."""

    def test_horror_want_not_equal_change(self):
        """Horror: Want cannot equal Change."""
        template = HorrorTemplate()
        choices = {
            4: {"want": "want-escape", "change": "want-escape"}  # INVALID
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert any("want" in e.lower() and "change" in e.lower() for e in errors)

    def test_horror_resistance_inescapable_required(self):
        """Horror: Resistance must be inescapable."""
        template = HorrorTemplate()
        choices = {
            4: {
                "want": "want-escape",
                "change": "change-transform"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        # Should fail: resistance is required and must be inescapable
        assert not is_valid

    def test_horror_inescapable_resistance_passes(self):
        """Horror with proper inescapable resistance passes."""
        template = HorrorTemplate()
        choices = {
            4: {
                "want": "want-prevent",
                "resistance": "resistance-inescapable",
                "change": "change-transform"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid
        assert len(errors) == 0

    def test_horror_forbidden_return_to_normal(self):
        """Horror cannot end with return to normal."""
        template = HorrorTemplate()
        choices = {
            4: {
                "want": "want-escape",
                "resistance": "resistance-inescapable",
                "change": "change-transform"
            },
            7: {
                "pacing": "pacing-return-to-normal"  # Forbidden
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert any("return" in e.lower() or "normal" in e.lower() for e in errors)


class TestMysteryValidation:
    """Tests for mystery-specific validation rules."""

    def test_mystery_want_not_equal_change(self):
        """Mystery: Want cannot equal Change."""
        template = MysteryTemplate()
        choices = {
            4: {"want": "want-truth", "change": "want-truth"}  # INVALID
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert any("want" in e.lower() and "change" in e.lower() for e in errors)

    def test_mystery_no_innocent_observer_endings(self):
        """Mystery: MC cannot remain innocent observer."""
        template = MysteryTemplate()
        choices = {
            4: {
                "want": "want-truth",
                "change": "change-witness"  # OK: unwilling witness
            }
        }
        is_valid, _, _ = validate_choices(template, choices)
        assert is_valid  # Witness is OK (unwilling complicity)

    def test_mystery_forbidden_innocent_change(self):
        """Mystery cannot end with MC remaining innocent."""
        template = MysteryTemplate()
        choices = {
            4: {
                "want": "want-truth",
                "change": "change-innocent"  # Forbidden
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert any("innocent" in e.lower() for e in errors)

    def test_mystery_participant_ending_passes(self):
        """Mystery with active participant ending is valid."""
        template = MysteryTemplate()
        choices = {
            4: {
                "want": "want-confirm",
                "change": "change-participant"  # OK: active complicity
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid
        assert len(errors) == 0


class TestValidationErrorHandling:
    """Tests for error handling in validation."""

    def test_partial_layer_4_choices_pass(self):
        """Partial layer 4 choices without all fields should still validate."""
        template = HumiliationTemplate()
        choices = {
            4: {
                "want": "want-dignity",
                "change": "change-accept"
                # resistance is optional
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        # Should not fail just because resistance is missing
        assert is_valid or not any("want" in e.lower() and "change" in e.lower() for e in errors)

    def test_empty_choices_passes(self):
        """Empty choices dict should not cause errors."""
        template = HumiliationTemplate()
        choices = {}
        is_valid, errors, warnings = validate_choices(template, choices)
        # Should be valid (no invalid choices)
        assert is_valid

    def test_multiple_phases_all_validated(self):
        """Multiple phase choices all get validated."""
        template = HumiliationTemplate()
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-inadequacy",
                "change": "change-accept"
            },
            6: {
                "pov_structure": "pov-limited-mc"
            },
            7: {
                "pacing": "pacing-accelerating"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid
        assert len(errors) == 0
