"""Tests for gentle femdom core templates."""

import pytest
from auteur.gentlefemdom.core_templates import (
    SensualDominanceTemplate,
    TenderSurrenderTemplate,
    RomanticAuthorityTemplate,
    get_template,
)


class TestSensualDominanceTemplate:
    """Tests for SensualDominanceTemplate."""

    def test_sensual_dominance_instantiation(self):
        """Test that SensualDominanceTemplate can be instantiated."""
        t = SensualDominanceTemplate()
        assert t.core_id == "sensual_dominance"
        assert t.primary_emotion == "playful_control"

    def test_sensual_dominance_has_all_phases(self):
        """Test that SensualDominanceTemplate has all 9 phases."""
        t = SensualDominanceTemplate()
        assert t.phases == {
            1: "emotional_core",
            2: "genre_contract",
            3: "scope",
            4: "structural_forces",
            5: "boundary_clarity",
            6: "tone_playfulness",
            7: "care_expression",
            8: "power_balance",
            9: "connection_confidence"
        }

    def test_sensual_dominance_layer_4_has_required_fields(self):
        """Test that Layer 4 has all required fields."""
        t = SensualDominanceTemplate()
        options = t.get_options(4)
        required_fields = {"want", "resistance", "conflict", "stakes", "change"}
        assert set(options.keys()) == required_fields

    def test_sensual_dominance_layer_4_want_options(self):
        """Test that Layer 4 want field has options."""
        t = SensualDominanceTemplate()
        options = t.get_options(4)
        assert "want" in options
        assert len(options["want"]) >= 2
        assert all(isinstance(opt, dict) for opt in options["want"])
        assert all("id" in opt and "label" in opt for opt in options["want"])

    def test_sensual_dominance_has_constraints(self):
        """Test that template has constraints for appropriate layers."""
        t = SensualDominanceTemplate()
        constraints = t.get_constraints(4)
        assert isinstance(constraints, list)
        assert len(constraints) > 0

    def test_sensual_dominance_validate_valid_choices(self):
        """Test validation of valid choices."""
        t = SensualDominanceTemplate()
        options = t.get_options(4)
        # Pick first option from each field
        choices = {
            4: {
                "want": options["want"][0]["id"],
                "resistance": options["resistance"][0]["id"],
                "conflict": options["conflict"][0]["id"],
                "stakes": options["stakes"][0]["id"],
                "change": options["change"][0]["id"],
            }
        }
        is_valid, errors, warnings = t.validate_choices(choices)
        assert is_valid
        assert len(errors) == 0


class TestTenderSurrenderTemplate:
    """Tests for TenderSurrenderTemplate."""

    def test_tender_surrender_instantiation(self):
        """Test that TenderSurrenderTemplate can be instantiated."""
        t = TenderSurrenderTemplate()
        assert t.core_id == "tender_surrender"
        assert t.primary_emotion == "safe_vulnerability"

    def test_tender_surrender_has_all_phases(self):
        """Test that TenderSurrenderTemplate has all 9 phases."""
        t = TenderSurrenderTemplate()
        assert t.phases == {
            1: "emotional_core",
            2: "genre_contract",
            3: "scope",
            4: "structural_forces",
            5: "vulnerability_journey",
            6: "trust_building",
            7: "release_rhythm",
            8: "emotional_tone",
            9: "transformation_culmination"
        }

    def test_tender_surrender_layer_4_has_required_fields(self):
        """Test that Layer 4 has all required fields."""
        t = TenderSurrenderTemplate()
        options = t.get_options(4)
        required_fields = {"want", "resistance", "conflict", "stakes", "change"}
        assert set(options.keys()) == required_fields

    def test_tender_surrender_layer_4_resistance_options(self):
        """Test that Layer 4 resistance field has options."""
        t = TenderSurrenderTemplate()
        options = t.get_options(4)
        assert "resistance" in options
        assert len(options["resistance"]) >= 2
        assert all(isinstance(opt, dict) for opt in options["resistance"])

    def test_tender_surrender_validate_valid_choices(self):
        """Test validation of valid choices."""
        t = TenderSurrenderTemplate()
        options = t.get_options(4)
        choices = {
            4: {
                "want": options["want"][0]["id"],
                "resistance": options["resistance"][0]["id"],
                "conflict": options["conflict"][0]["id"],
                "stakes": options["stakes"][0]["id"],
                "change": options["change"][0]["id"],
            }
        }
        is_valid, errors, warnings = t.validate_choices(choices)
        assert is_valid
        assert len(errors) == 0


class TestRomanticAuthorityTemplate:
    """Tests for RomanticAuthorityTemplate."""

    def test_romantic_authority_instantiation(self):
        """Test that RomanticAuthorityTemplate can be instantiated."""
        t = RomanticAuthorityTemplate()
        assert t.core_id == "romantic_authority"
        assert t.primary_emotion == "cherished_leadership"

    def test_romantic_authority_has_all_phases(self):
        """Test that RomanticAuthorityTemplate has all 9 phases."""
        t = RomanticAuthorityTemplate()
        assert t.phases == {
            1: "emotional_core",
            2: "genre_contract",
            3: "scope",
            4: "structural_forces",
            5: "leadership_style",
            6: "care_expression",
            7: "partnership_rhythm",
            8: "respect_dynamic",
            9: "interdependence_deepening"
        }

    def test_romantic_authority_layer_4_has_required_fields(self):
        """Test that Layer 4 has all required fields."""
        t = RomanticAuthorityTemplate()
        options = t.get_options(4)
        required_fields = {"want", "resistance", "conflict", "stakes", "change"}
        assert set(options.keys()) == required_fields

    def test_romantic_authority_layer_4_stakes_options(self):
        """Test that Layer 4 stakes field has options."""
        t = RomanticAuthorityTemplate()
        options = t.get_options(4)
        assert "stakes" in options
        assert len(options["stakes"]) >= 2
        assert all(isinstance(opt, dict) for opt in options["stakes"])

    def test_romantic_authority_validate_valid_choices(self):
        """Test validation of valid choices."""
        t = RomanticAuthorityTemplate()
        options = t.get_options(4)
        choices = {
            4: {
                "want": options["want"][0]["id"],
                "resistance": options["resistance"][0]["id"],
                "conflict": options["conflict"][0]["id"],
                "stakes": options["stakes"][0]["id"],
                "change": options["change"][0]["id"],
            }
        }
        is_valid, errors, warnings = t.validate_choices(choices)
        assert is_valid
        assert len(errors) == 0


class TestFactoryFunction:
    """Tests for get_template factory function."""

    def test_get_template_sensual_dominance(self):
        """Test factory returns correct template for sensual_dominance."""
        t = get_template("sensual_dominance")
        assert isinstance(t, SensualDominanceTemplate)
        assert t.core_id == "sensual_dominance"

    def test_get_template_tender_surrender(self):
        """Test factory returns correct template for tender_surrender."""
        t = get_template("tender_surrender")
        assert isinstance(t, TenderSurrenderTemplate)
        assert t.core_id == "tender_surrender"

    def test_get_template_romantic_authority(self):
        """Test factory returns correct template for romantic_authority."""
        t = get_template("romantic_authority")
        assert isinstance(t, RomanticAuthorityTemplate)
        assert t.core_id == "romantic_authority"

    def test_get_template_unknown_raises_error(self):
        """Test factory raises ValueError for unknown core."""
        with pytest.raises(ValueError, match="Unknown core"):
            get_template("unknown_core")


class TestCrossTemplateConsistency:
    """Tests for consistency across all templates."""

    def test_all_templates_have_9_phases(self):
        """Test that all templates have 9 phases."""
        for template_class in [SensualDominanceTemplate, TenderSurrenderTemplate, RomanticAuthorityTemplate]:
            t = template_class()
            assert len(t.phases) == 9
            assert all(isinstance(k, int) for k in t.phases.keys())
            assert set(t.phases.keys()) == {1, 2, 3, 4, 5, 6, 7, 8, 9}

    def test_all_templates_have_api_methods(self):
        """Test that all templates have required API methods."""
        for template_class in [SensualDominanceTemplate, TenderSurrenderTemplate, RomanticAuthorityTemplate]:
            t = template_class()
            assert hasattr(t, "get_options")
            assert hasattr(t, "get_constraints")
            assert hasattr(t, "validate_choices")
            assert callable(t.get_options)
            assert callable(t.get_constraints)
            assert callable(t.validate_choices)

    def test_validate_choices_returns_triple(self):
        """Test that validate_choices returns (bool, list, list)."""
        for template_class in [SensualDominanceTemplate, TenderSurrenderTemplate, RomanticAuthorityTemplate]:
            t = template_class()
            is_valid, errors, warnings = t.validate_choices({})
            assert isinstance(is_valid, bool)
            assert isinstance(errors, list)
            assert isinstance(warnings, list)
