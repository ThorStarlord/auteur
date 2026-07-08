"""Tests verifying emotion arc propagation from templates into StoryIdentity.

These tests confirm that IdentityGenerator.from_choices() populates
target_experience fields (primary, progression, secondary, avoid) from
the gentlefemdom core template's primary_emotion and the corresponding
emotion arc, rather than leaving them at generic netorare/mystery defaults.
"""

import pytest

from auteur.netorare.identity_generator import IdentityGenerator
from auteur.gentlefemdom.emotion_arcs import get_emotion_arc


SENSUAL_DOMINANCE_CHOICES = {
    4: {
        "want": "want-establish-trust",
        "resistance": "resistance-partner-doubt",
        "conflict": "conflict-control-vs-consent",
        "stakes": "stakes-emotional-intimacy",
        "change": "change-tentative-to-confident",
    },
}

TENDER_SURRENDER_CHOICES = {
    4: {
        "want": "want-release-control",
        "resistance": "resistance-fear-vulnerability",
        "conflict": "conflict-self-protection-vs-desire",
        "stakes": "stakes-emotional-walls",
        "change": "change-defended-to-open",
    },
}

ROMANTIC_AUTHORITY_CHOICES = {
    4: {
        "want": "want-provide-protect",
        "resistance": "resistance-partner-independence",
        "conflict": "conflict-leadership-vs-partnership",
        "stakes": "stakes-relationship-balance",
        "change": "change-uncertain-to-confident",
    },
}


class TestEmotionPropagation:
    """Verify each gentlefemdom core's primary emotion propagates to the identity."""

    def test_sensual_dominance_emotion_propagates(self):
        identity = IdentityGenerator.from_choices("sensual_dominance", SENSUAL_DOMINANCE_CHOICES)
        assert identity.target_experience.primary == "playful_control"

    def test_tender_surrender_emotion_propagates(self):
        identity = IdentityGenerator.from_choices("tender_surrender", TENDER_SURRENDER_CHOICES)
        assert identity.target_experience.primary == "safe_vulnerability"

    def test_romantic_authority_emotion_propagates(self):
        identity = IdentityGenerator.from_choices("romantic_authority", ROMANTIC_AUTHORITY_CHOICES)
        assert identity.target_experience.primary == "cherished_leadership"


class TestEmotionArcFieldsPopulated:
    """Verify progression, secondary, and avoid fields are populated from the emotion arc."""

    def test_emotion_progression_populated(self):
        arc = get_emotion_arc("sensual_dominance")
        identity = IdentityGenerator.from_choices("sensual_dominance", SENSUAL_DOMINANCE_CHOICES)
        assert identity.target_experience.progression == arc["progression"]

    def test_secondary_emotions_populated(self):
        arc = get_emotion_arc("tender_surrender")
        identity = IdentityGenerator.from_choices("tender_surrender", TENDER_SURRENDER_CHOICES)
        assert identity.target_experience.secondary == arc["secondary"]

    def test_avoided_experiences_populated(self):
        arc = get_emotion_arc("romantic_authority")
        identity = IdentityGenerator.from_choices("romantic_authority", ROMANTIC_AUTHORITY_CHOICES)
        assert identity.target_experience.avoid == arc["avoid"]


class TestDifferentCoresProduceDifferentIdentities:
    """Verify emotion fields differ across cores rather than sharing generic defaults."""

    def test_different_cores_produce_different_identities(self):
        sensual = IdentityGenerator.from_choices("sensual_dominance", SENSUAL_DOMINANCE_CHOICES)
        tender = IdentityGenerator.from_choices("tender_surrender", TENDER_SURRENDER_CHOICES)
        romantic = IdentityGenerator.from_choices("romantic_authority", ROMANTIC_AUTHORITY_CHOICES)

        primaries = {
            sensual.target_experience.primary,
            tender.target_experience.primary,
            romantic.target_experience.primary,
        }
        assert len(primaries) == 3

        progressions = {
            sensual.target_experience.progression,
            tender.target_experience.progression,
            romantic.target_experience.progression,
        }
        assert len(progressions) == 3
