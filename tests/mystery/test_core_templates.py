"""Tests for Mystery genre core templates."""

import pytest
from auteur.mystery.core_templates import (
    HowdunitTemplate, ParanoiaTemplate, CozyTemplate,
    get_template, TemplateOption
)


class TestHowdunitTemplate:
    """Test Howdunit (classic detective) template."""

    def test_howdunit_instantiation(self):
        """Test that HowdunitTemplate can be instantiated."""
        template = HowdunitTemplate()
        assert template.core_id == "howdunit"
        assert template.primary_emotion == "puzzle-solving"

    def test_howdunit_phases(self):
        """Test that HowdunitTemplate has all 9 phases."""
        template = HowdunitTemplate()
        assert len(template.phases) == 9
        assert template.phases[1] == "emotional_core"
        assert template.phases[2] == "genre_contract"
        assert template.phases[3] == "scope"
        assert template.phases[4] == "structural_forces"

    def test_howdunit_get_options_layer1(self):
        """Test get_options(1) returns howdunit as only option."""
        template = HowdunitTemplate()
        options = template.get_options(1)
        assert len(options) > 0
        assert any(opt.id == "howdunit" for opt in options)

    def test_howdunit_get_options_layer2_genre_contracts(self):
        """Test get_options(2) returns multiple genre contract options."""
        template = HowdunitTemplate()
        options = template.get_options(2)
        assert len(options) >= 4  # At least 4 genre options
        option_ids = [opt.id for opt in options]
        assert "detective" in option_ids
        assert "procedural" in option_ids
        assert "locked-room" in option_ids
        assert "puzzle-box" in option_ids

    def test_howdunit_get_options_layer4_want(self):
        """Test get_options(4, 'want') returns want options for Howdunit."""
        template = HowdunitTemplate()
        options = template.get_options(4)
        # Filter options that start with "want-"
        wants = [opt for opt in options if opt.id.startswith("want-")]
        assert len(wants) >= 3
        want_ids = [opt.id for opt in wants]
        assert "want-solve-puzzle" in want_ids
        assert "want-identify-culprit" in want_ids

    def test_howdunit_validate_choices_valid(self):
        """Test validate_choices with valid howdunit choices."""
        template = HowdunitTemplate()
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "detective"},
            3: {"scope": "standard"},
            4: {
                "want": "want-solve-puzzle",
                "resistance": "resistance-misleading-clues",
                "conflict": "conflict-deduction-misdirection",
                "stakes": "stakes-justice",
                "change": "change-clarity"
            },
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is True
        assert len(errors) == 0

    def test_howdunit_validate_choices_invalid_phase(self):
        """Test validate_choices with invalid phase number."""
        template = HowdunitTemplate()
        choices = {
            99: {"invalid": "phase"}
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is False
        assert any("phase" in err.lower() for err in errors)

    def test_howdunit_validate_choices_invalid_option_id(self):
        """Test validate_choices with invalid option ID."""
        template = HowdunitTemplate()
        choices = {
            2: {"genre_contract": "invalid-genre-id"}
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is False
        assert any("invalid-genre-id" in err for err in errors)

    def test_howdunit_get_constraints_layer4(self):
        """Test get_constraints returns validation hints for layer 4."""
        template = HowdunitTemplate()
        constraints = template.get_constraints(4)
        assert constraints is not None
        # Constraints should mention that want ≠ change
        assert isinstance(constraints, (str, dict, list))


class TestParanoiaTemplate:
    """Test Paranoia (psychological thriller) template."""

    def test_paranoia_instantiation(self):
        """Test that ParanoiaTemplate can be instantiated."""
        template = ParanoiaTemplate()
        assert template.core_id == "paranoia"
        assert template.primary_emotion == "dread"

    def test_paranoia_phases(self):
        """Test that ParanoiaTemplate has all 9 phases."""
        template = ParanoiaTemplate()
        assert len(template.phases) == 9
        assert template.phases[1] == "emotional_core"
        assert template.phases[4] == "structural_forces"

    def test_paranoia_get_options_layer1(self):
        """Test get_options(1) returns paranoia as only option."""
        template = ParanoiaTemplate()
        options = template.get_options(1)
        assert any(opt.id == "paranoia" for opt in options)

    def test_paranoia_validate_choices_valid(self):
        """Test validate_choices with valid paranoia choices."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            2: {"genre_contract": "gaslight"},
            4: {
                "want": "want-understand-reality",
                "resistance": "resistance-unreliable-narrator",
                "conflict": "conflict-reality-perception",
                "stakes": "stakes-mental-stability",
                "change": "change-paranoia-peak"
            }
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is True


class TestCozyTemplate:
    """Test Cozy (low-stakes) template."""

    def test_cozy_instantiation(self):
        """Test that CozyTemplate can be instantiated."""
        template = CozyTemplate()
        assert template.core_id == "cozy"
        assert template.primary_emotion == "comfort"

    def test_cozy_phases(self):
        """Test that CozyTemplate has all 9 phases."""
        template = CozyTemplate()
        assert len(template.phases) == 9

    def test_cozy_validate_choices_valid(self):
        """Test validate_choices with valid cozy choices."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            2: {"genre_contract": "village"},
            4: {
                "want": "want-solve-community",
                "resistance": "resistance-scattered-clues",
                "conflict": "conflict-investigation-daily-life",
                "stakes": "stakes-community-bonds",
                "change": "change-community-shift"
            }
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is True


class TestGetTemplate:
    """Test template factory function."""

    def test_get_template_howdunit(self):
        """Test get_template returns HowdunitTemplate for 'howdunit'."""
        template = get_template("howdunit")
        assert isinstance(template, HowdunitTemplate)
        assert template.core_id == "howdunit"

    def test_get_template_paranoia(self):
        """Test get_template returns ParanoiaTemplate for 'paranoia'."""
        template = get_template("paranoia")
        assert isinstance(template, ParanoiaTemplate)
        assert template.core_id == "paranoia"

    def test_get_template_cozy(self):
        """Test get_template returns CozyTemplate for 'cozy'."""
        template = get_template("cozy")
        assert isinstance(template, CozyTemplate)
        assert template.core_id == "cozy"

    def test_get_template_invalid_core_id(self):
        """Test get_template raises ValueError for unknown core."""
        with pytest.raises(ValueError):
            get_template("invalid-core")
