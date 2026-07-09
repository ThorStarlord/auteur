"""Tests for identity_generator: converts choices to story_identity.yaml."""

import pytest
from pathlib import Path
import yaml

from auteur.netorare.identity_generator import IdentityGenerator
from auteur.netorare.core_templates import HumiliationTemplate, HorrorTemplate, MysteryTemplate
from auteur.identity import StoryIdentity


class TestIdentityGeneratorBasics:
    """Test basic IdentityGenerator functionality."""

    def test_from_choices_humiliation_minimal(self):
        """Generate minimal valid humiliation story identity from choices."""
        template = HumiliationTemplate()
        choices = {
            1: {"primary": "humiliation"},
            2: {"genre": "netorare"},
            3: {"scope_contract": "focused"},
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth and social standing"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )

        assert isinstance(identity, StoryIdentity)
        assert identity.title is not None
        assert len(identity.title) > 0
        assert identity.core_answer is not None
        # Central engine now uses template labels instead of raw IDs
        assert "dignity" in identity.central_engine.want.lower()

    def test_from_choices_validates_before_generating(self):
        """from_choices validates the choices before generating."""
        template = HumiliationTemplate()
        invalid_choices = {
            4: {
                "want": "want-dignity",
                "change": "want-dignity",  # Invalid: same as want
            }
        }

        with pytest.raises(ValueError) as exc_info:
            IdentityGenerator.from_choices(
                core_id="classic_humiliation",
                choices=invalid_choices
            )

        assert "validation" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()

    def test_from_choices_horror(self):
        """Generate horror story identity from choices."""
        template = HorrorTemplate()
        choices = {
            1: {"primary": "dread"},
            2: {"genre": "horror"},
            3: {"scope_contract": "focused"},
            4: {
                "want": "want-escape",
                "resistance": "resistance-inescapable",
                "change": "change-transform",
                "stakes": "sanity and reality"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="horror",
            choices=choices
        )

        assert isinstance(identity, StoryIdentity)
        # Central engine now uses template labels instead of raw IDs
        assert "inescapable" in identity.central_engine.resistance.lower()

    def test_from_choices_mystery(self):
        """Generate mystery (netorare core) story identity from choices."""
        template = MysteryTemplate()
        choices = {
            1: {"primary": "voyeurism"},
            2: {"genre": "netorare"},
            3: {"scope_contract": "focused"},
            4: {
                "want": "want-truth",
                "resistance": "resistance-hidden-truth",
                "change": "change-witness",
                "stakes": "innocence and truth"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="mystery",
            choices=choices
        )

        assert isinstance(identity, StoryIdentity)
        assert identity.story_type.genre.value == "netorare"


class TestIdentityGeneratorYAML:
    """Test YAML serialization and validation."""

    def test_to_yaml_produces_valid_yaml(self):
        """to_yaml produces valid YAML string."""
        template = HumiliationTemplate()
        choices = {
            1: {"primary": "humiliation"},
            2: {"genre": "netorare"},
            3: {"scope_contract": "focused"},
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )
        yaml_str = IdentityGenerator.to_yaml(identity)

        # Should be valid YAML
        parsed = yaml.safe_load(yaml_str)
        assert isinstance(parsed, dict)
        assert "title" in parsed
        assert "core_answer" in parsed
        assert "central_engine" in parsed

    def test_yaml_roundtrip(self):
        """YAML serialization can be deserialized back to StoryIdentity."""
        template = HumiliationTemplate()
        choices = {
            1: {"primary": "humiliation"},
            2: {"genre": "netorare"},
            3: {"scope_contract": "focused"},
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth"
            },
        }

        original = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )
        yaml_str = IdentityGenerator.to_yaml(original)

        # Parse back to dict and reconstruct
        parsed_dict = yaml.safe_load(yaml_str)
        reconstructed = StoryIdentity(**parsed_dict)

        assert reconstructed.title == original.title
        assert reconstructed.central_engine.want == original.central_engine.want
        assert reconstructed.story_type.genre == original.story_type.genre

    def test_yaml_output_structure(self):
        """Generated YAML has all required fields at top level."""
        template = HumiliationTemplate()
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )
        yaml_str = IdentityGenerator.to_yaml(identity)
        parsed = yaml.safe_load(yaml_str)

        # Verify required top-level fields
        required_fields = [
            "title",
            "core_answer",
            "target_experience",
            "story_type",
            "central_engine",
        ]
        for field in required_fields:
            assert field in parsed, f"Missing required field: {field}"

        # Verify central_engine has all required sub-fields
        assert "want" in parsed["central_engine"]
        assert "resistance" in parsed["central_engine"]
        assert "conflict" in parsed["central_engine"]
        assert "stakes" in parsed["central_engine"]
        assert "change" in parsed["central_engine"]


class TestIdentityGeneratorTransformation:
    """Test transformation logic from choices to StoryIdentity."""

    def test_choice_values_become_identity_fields(self):
        """Choice values are correctly mapped to StoryIdentity fields."""
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "my self-worth and honor"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )

        # Central engine now uses template labels instead of raw IDs (Phase 2)
        assert "dignity" in identity.central_engine.want.lower()
        assert "superior" in identity.central_engine.resistance.lower()
        assert "accept" in identity.central_engine.change.lower()
        # Stakes falls back to readable conversion (netorare doesn't have stakes in template)
        assert "worth" in identity.central_engine.stakes.lower()

    def test_generated_conflict_describes_tension(self):
        """Generated conflict field describes the dramatic tension."""
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )

        # Conflict should be non-empty and describe the tension
        assert len(identity.central_engine.conflict) > 0
        # Should reference the core dramatic problem
        conflict_lower = identity.central_engine.conflict.lower()
        assert any(word in conflict_lower for word in ["want", "resistance", "choice", "face", "between"])

    def test_layers_populate_story_type_correctly(self):
        """Story type fields are populated from layer 1-3 choices."""
        choices = {
            1: {"primary": "humiliation"},
            2: {"genre": "netorare"},
            3: {"scope_contract": "focused"},
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )

        # Story type should be populated
        assert identity.story_type is not None
        assert identity.story_type.genre.value == "netorare"
        assert identity.story_type.medium is not None
        assert identity.story_type.mode is not None
        assert identity.story_type.target_audience is not None

    def test_core_answer_generated_from_choices(self):
        """Core answer is generated as a coherent summary."""
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth and standing"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )

        # Core answer should exist and be substantive
        assert len(identity.core_answer) > 20
        # Should hint at the core transformation
        core_lower = identity.core_answer.lower()
        assert any(word in core_lower for word in ["humiliation", "lose", "accept", "dignity", "worth"])

    def test_title_generated_from_choices(self):
        """Title is generated from the central dramatic question."""
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )

        # Title should be substantive
        assert len(identity.title) > 5
        # Should not be a generic placeholder
        assert identity.title != "Story"
        assert "story" not in identity.title.lower()


class TestIdentityGeneratorValidation:
    """Test that generated identities pass auteur validation."""

    def test_generated_identity_passes_validate_identity(self):
        """Generated StoryIdentity passes its own validate_identity() method."""
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )

        # Should not raise and should return diagnostics
        diagnostics = identity.validate_identity()
        assert isinstance(diagnostics, list)

        # There should be no ERROR-level diagnostics
        errors = [d for d in diagnostics if hasattr(d, 'severity') and "error" in str(d.severity).lower()]
        assert len(errors) == 0, f"Generated identity has validation errors: {errors}"

    def test_generated_identity_coherent(self):
        """Generated identity has coherent central_engine."""
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "self-worth"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )

        engine = identity.central_engine
        # Want and change must differ
        assert engine.want != engine.change
        # All fields must be non-empty
        assert len(engine.want) > 0
        assert len(engine.resistance) > 0
        assert len(engine.change) > 0
        assert len(engine.stakes) > 0
        assert len(engine.conflict) > 0


class TestIdentityGeneratorIntegration:
    """Integration tests with full choice workflows."""

    def test_full_humiliation_workflow(self):
        """Full workflow: choices -> validation -> identity -> yaml."""
        choices = {
            1: {"primary": "humiliation"},
            2: {"genre": "netorare"},
            3: {"scope_contract": "focused"},
            4: {
                "want": "want-dignity",
                "resistance": "resistance-rival-superiority",
                "change": "change-accept",
                "stakes": "honor and social standing"
            },
            5: {"subplot": "subplot-rival-perspective"},
            6: {"pov_structure": "pov-limited-mc"},
            7: {"pacing": "pacing-slow-burn"},
            8: {"tone": "tone-suffocating"},
            9: {"theme": "theme-powerlessness"},
        }

        # Should generate without error
        identity = IdentityGenerator.from_choices(
            core_id="classic_humiliation",
            choices=choices
        )

        # Should validate
        diagnostics = identity.validate_identity()
        errors = [d for d in diagnostics if hasattr(d, 'severity') and "error" in str(d.severity).lower()]
        assert len(errors) == 0

        # Should serialize to YAML
        yaml_str = IdentityGenerator.to_yaml(identity)
        assert len(yaml_str) > 50

        # Should round-trip
        parsed = yaml.safe_load(yaml_str)
        reconstructed = StoryIdentity(**parsed)
        assert reconstructed.title == identity.title

    def test_multiple_templates_generate_correct_genres(self):
        """Each template core_id generates identity with appropriate genre."""
        test_cases = [
            ("classic_humiliation", "netorare"),
            ("horror", "horror"),
            ("mystery", "netorare"),
        ]

        for core_id, expected_genre in test_cases:
            if core_id == "classic_humiliation":
                choices = {
                    4: {
                        "want": "want-dignity",
                        "resistance": "resistance-rival-superiority",
                        "change": "change-accept",
                        "stakes": "self-worth"
                    },
                }
            elif core_id == "horror":
                choices = {
                    4: {
                        "want": "want-escape",
                        "resistance": "resistance-inescapable",
                        "change": "change-transform",
                        "stakes": "sanity and reality"
                    },
                }
            else:  # mystery
                choices = {
                    4: {
                        "want": "want-truth",
                        "resistance": "resistance-hidden-truth",
                        "change": "change-witness",
                        "stakes": "innocence and truth"
                    },
                }

            identity = IdentityGenerator.from_choices(
                core_id=core_id,
                choices=choices
            )

            assert identity.story_type.genre.value == expected_genre, \
                f"core_id {core_id} should generate {expected_genre}, got {identity.story_type.genre.value}"
