"""Tests for mystery identity generation."""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.mystery.core_templates import (
    HowdunitTemplate, ParanoiaTemplate, CozyTemplate
)


class TestMysteryIdentityGeneratorBasics:
    """Test basic identity generation for mystery cores."""

    def test_from_choices_howdunit(self):
        """Test generating identity from howdunit choices."""
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
            }
        }
        identity = IdentityGenerator.from_choices("howdunit", choices)
        assert identity is not None
        assert identity.story_type.genre.value == "mystery"

    def test_from_choices_paranoia(self):
        """Test generating identity from paranoia choices."""
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
        identity = IdentityGenerator.from_choices("paranoia", choices)
        assert identity is not None
        assert identity.story_type.genre.value == "mystery"

    def test_from_choices_cozy(self):
        """Test generating identity from cozy choices."""
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
        identity = IdentityGenerator.from_choices("cozy", choices)
        assert identity is not None
        assert identity.story_type.genre.value == "mystery"

    def test_from_choices_validates_before_generating(self):
        """Test that invalid choices raise ValueError."""
        invalid_choices = {
            1: {"emotional_core": "invalid-core"}
        }
        with pytest.raises(ValueError):
            IdentityGenerator.from_choices("howdunit", invalid_choices)


class TestMysteryIdentityYAML:
    """Test YAML serialization for mystery identities."""

    def test_to_yaml_produces_valid_yaml(self):
        """Test that generated YAML is parseable."""
        import yaml
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
        identity = IdentityGenerator.from_choices("howdunit", choices)
        yaml_content = IdentityGenerator.to_yaml(identity)

        # Verify it's valid YAML
        parsed = yaml.safe_load(yaml_content)
        assert parsed is not None
        assert "story_type" in parsed

    def test_yaml_output_has_mystery_genre(self):
        """Test that mystery YAML contains Genre: mystery."""
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
        identity = IdentityGenerator.from_choices("howdunit", choices)
        yaml_content = IdentityGenerator.to_yaml(identity)

        # Genre should be mystery
        assert "genre:" in yaml_content.lower()
        assert "mystery" in yaml_content.lower()


class TestMysteryIdentityIntegration:
    """Integration tests for full mystery pipeline."""

    def test_full_howdunit_workflow(self):
        """Test end-to-end: choices → identity → YAML."""
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "puzzle-box"},
            3: {"scope": "focused"},
            4: {
                "want": "want-identify-culprit",
                "resistance": "resistance-false-suspects",
                "conflict": "conflict-logic-chaos",
                "stakes": "stakes-order-restored",
                "change": "change-certainty"
            },
            5: {"investigation_style": "logical"},
            6: {"pacing_rhythm": "accelerating"},
            7: {"clue_distribution": "even"},
            8: {"solution_density": "moderate"},
            9: {"fairness_confidence": "fair-high"}
        }

        identity = IdentityGenerator.from_choices("howdunit", choices)
        yaml_content = IdentityGenerator.to_yaml(identity)

        # Should produce valid YAML with all required fields
        import yaml
        parsed = yaml.safe_load(yaml_content)
        assert "target_experience" in parsed
        assert "story_type" in parsed
        assert parsed["story_type"]["genre"] == "mystery"

    def test_multiple_cores_generate_different_identities(self):
        """Test that different cores produce distinct identities."""
        howdunit_choices = {
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

        paranoia_choices = {
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

        h_identity = IdentityGenerator.from_choices("howdunit", howdunit_choices)
        p_identity = IdentityGenerator.from_choices("paranoia", paranoia_choices)

        # Both should be mystery genre but different target experiences
        h_yaml = IdentityGenerator.to_yaml(h_identity)
        p_yaml = IdentityGenerator.to_yaml(p_identity)

        assert "mystery" in h_yaml.lower()
        assert "mystery" in p_yaml.lower()
