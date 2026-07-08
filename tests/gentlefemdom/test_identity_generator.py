"""Tests for gentle femdom identity generation."""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.gentlefemdom.core_templates import (
    SensualDominanceTemplate, TenderSurrenderTemplate, RomanticAuthorityTemplate
)
from auteur.identity import StoryIdentity
from auteur.blueprint import Genre


class TestGentlefemdomIdentityGeneratorBasics:
    """Test basic identity generation for gentle femdom cores."""

    def test_from_choices_sensual_dominance(self):
        """Test generating identity from sensual_dominance choices."""
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident"
            }
        }
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        assert identity is not None
        assert isinstance(identity, StoryIdentity)
        assert identity.story_type.genre == Genre.GENTLEFEMDOM

    def test_from_choices_tender_surrender(self):
        """Test generating identity from tender_surrender choices."""
        choices = {
            4: {
                "want": "want-release-control",
                "resistance": "resistance-fear-vulnerability",
                "conflict": "conflict-self-protection-vs-desire",
                "stakes": "stakes-emotional-walls",
                "change": "change-defended-to-open"
            }
        }
        identity = IdentityGenerator.from_choices("tender_surrender", choices)
        assert identity is not None
        assert isinstance(identity, StoryIdentity)
        assert identity.story_type.genre == Genre.GENTLEFEMDOM

    def test_from_choices_romantic_authority(self):
        """Test generating identity from romantic_authority choices."""
        choices = {
            4: {
                "want": "want-provide-protect",
                "resistance": "resistance-partner-independence",
                "conflict": "conflict-leadership-vs-partnership",
                "stakes": "stakes-relationship-balance",
                "change": "change-uncertain-to-confident"
            }
        }
        identity = IdentityGenerator.from_choices("romantic_authority", choices)
        assert identity is not None
        assert isinstance(identity, StoryIdentity)
        assert identity.story_type.genre == Genre.GENTLEFEMDOM


class TestGentlefemdomIdentityValidation:
    """Test validation during gentlefemdom identity generation."""

    def test_from_choices_validates_before_generating_sensual_dominance(self):
        """Validates choices before generating sensual_dominance identity."""
        invalid_choices = {
            4: {
                "want": "want-establish-trust",
                "change": "want-establish-trust",  # Invalid: same as want
            }
        }

        with pytest.raises(ValueError) as exc_info:
            IdentityGenerator.from_choices(
                core_id="sensual_dominance",
                choices=invalid_choices
            )

        assert "validation" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()

    def test_from_choices_validates_before_generating_tender_surrender(self):
        """Validates choices before generating tender_surrender identity."""
        invalid_choices = {
            4: {
                "want": "want-release-control",
                "change": "want-release-control",  # Invalid: same as want
            }
        }

        with pytest.raises(ValueError) as exc_info:
            IdentityGenerator.from_choices(
                core_id="tender_surrender",
                choices=invalid_choices
            )

        assert "validation" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()

    def test_from_choices_validates_before_generating_romantic_authority(self):
        """Validates choices before generating romantic_authority identity."""
        invalid_choices = {
            4: {
                "want": "want-provide-protect",
                "change": "want-provide-protect",  # Invalid: same as want
            }
        }

        with pytest.raises(ValueError) as exc_info:
            IdentityGenerator.from_choices(
                core_id="romantic_authority",
                choices=invalid_choices
            )

        assert "validation" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()


class TestGentlefemdomIdentityTransformation:
    """Test transformation of choices to StoryIdentity for gentlefemdom."""

    def test_sensual_dominance_choice_values_become_identity_fields(self):
        """Choice values are correctly mapped for sensual_dominance."""
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="sensual_dominance",
            choices=choices
        )

        assert identity.central_engine.want == "want-establish-trust"
        assert identity.central_engine.resistance == "resistance-partner-doubt"
        assert identity.central_engine.change == "change-tentative-to-confident"
        assert "emotional-intimacy" in identity.central_engine.stakes or "intimacy" in identity.central_engine.stakes.lower()

    def test_tender_surrender_choice_values_become_identity_fields(self):
        """Choice values are correctly mapped for tender_surrender."""
        choices = {
            4: {
                "want": "want-release-control",
                "resistance": "resistance-fear-vulnerability",
                "conflict": "conflict-self-protection-vs-desire",
                "stakes": "stakes-emotional-walls",
                "change": "change-defended-to-open"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="tender_surrender",
            choices=choices
        )

        assert identity.central_engine.want == "want-release-control"
        assert identity.central_engine.resistance == "resistance-fear-vulnerability"
        assert identity.central_engine.change == "change-defended-to-open"

    def test_romantic_authority_choice_values_become_identity_fields(self):
        """Choice values are correctly mapped for romantic_authority."""
        choices = {
            4: {
                "want": "want-provide-protect",
                "resistance": "resistance-partner-independence",
                "conflict": "conflict-leadership-vs-partnership",
                "stakes": "stakes-relationship-balance",
                "change": "change-uncertain-to-confident"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="romantic_authority",
            choices=choices
        )

        assert identity.central_engine.want == "want-provide-protect"
        assert identity.central_engine.resistance == "resistance-partner-independence"
        assert identity.central_engine.change == "change-uncertain-to-confident"


class TestGentlefemdomIdentityCoherence:
    """Test that generated gentlefemdom identities are coherent."""

    def test_sensual_dominance_identity_coherent(self):
        """Generated sensual_dominance identity has coherent central_engine."""
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="sensual_dominance",
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

    def test_tender_surrender_identity_coherent(self):
        """Generated tender_surrender identity has coherent central_engine."""
        choices = {
            4: {
                "want": "want-release-control",
                "resistance": "resistance-fear-vulnerability",
                "conflict": "conflict-self-protection-vs-desire",
                "stakes": "stakes-emotional-walls",
                "change": "change-defended-to-open"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="tender_surrender",
            choices=choices
        )

        engine = identity.central_engine
        assert engine.want != engine.change
        assert len(engine.want) > 0
        assert len(engine.resistance) > 0
        assert len(engine.change) > 0
        assert len(engine.stakes) > 0
        assert len(engine.conflict) > 0

    def test_romantic_authority_identity_coherent(self):
        """Generated romantic_authority identity has coherent central_engine."""
        choices = {
            4: {
                "want": "want-provide-protect",
                "resistance": "resistance-partner-independence",
                "conflict": "conflict-leadership-vs-partnership",
                "stakes": "stakes-relationship-balance",
                "change": "change-uncertain-to-confident"
            },
        }

        identity = IdentityGenerator.from_choices(
            core_id="romantic_authority",
            choices=choices
        )

        engine = identity.central_engine
        assert engine.want != engine.change
        assert len(engine.want) > 0
        assert len(engine.resistance) > 0
        assert len(engine.change) > 0
        assert len(engine.stakes) > 0
        assert len(engine.conflict) > 0


class TestGentlefemdomIdentityIntegration:
    """Integration tests for gentlefemdom identity workflows."""

    def test_all_gentlefemdom_cores_generate_correct_genre(self):
        """Each gentlefemdom core generates identity with GENTLEFEMDOM genre."""
        test_cases = [
            ("sensual_dominance", "want-establish-trust", "resistance-partner-doubt", "conflict-control-vs-consent", "stakes-emotional-intimacy", "change-tentative-to-confident"),
            ("tender_surrender", "want-release-control", "resistance-fear-vulnerability", "conflict-self-protection-vs-desire", "stakes-emotional-walls", "change-defended-to-open"),
            ("romantic_authority", "want-provide-protect", "resistance-partner-independence", "conflict-leadership-vs-partnership", "stakes-relationship-balance", "change-uncertain-to-confident"),
        ]

        for core_id, want, resistance, conflict, stakes, change in test_cases:
            choices = {
                4: {
                    "want": want,
                    "resistance": resistance,
                    "conflict": conflict,
                    "stakes": stakes,
                    "change": change
                },
            }

            identity = IdentityGenerator.from_choices(
                core_id=core_id,
                choices=choices
            )

            assert identity.story_type.genre == Genre.GENTLEFEMDOM, \
                f"core_id {core_id} should generate GENTLEFEMDOM genre, got {identity.story_type.genre}"
