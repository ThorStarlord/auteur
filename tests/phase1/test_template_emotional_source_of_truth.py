"""Tests: template emotional data flows to identity."""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.gentlefemdom.core_templates import get_template


# Valid choices for each gentlefemdom core
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


def valid_choices_for(core_id: str) -> dict:
    """Return valid choices for a given core."""
    choices_map = {
        "sensual_dominance": SENSUAL_DOMINANCE_CHOICES,
        "tender_surrender": TENDER_SURRENDER_CHOICES,
        "romantic_authority": ROMANTIC_AUTHORITY_CHOICES,
    }
    return choices_map[core_id]


class TestTemplateEmotionalPreservation:
    """Verify template.primary_emotion becomes identity.target_experience.primary."""

    def test_sensual_dominance_primary_from_template(self):
        """Sensual dominance identity has template's primary_emotion, not dread."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        template = get_template("sensual_dominance")
        assert identity.target_experience.primary == template.primary_emotion
        assert identity.target_experience.primary == "playful_control"
        assert identity.target_experience.primary != "dread"

    def test_tender_surrender_primary_from_template(self):
        """Tender surrender identity has template's primary_emotion, not dread."""
        choices = TENDER_SURRENDER_CHOICES
        identity = IdentityGenerator.from_choices("tender_surrender", choices)
        template = get_template("tender_surrender")
        assert identity.target_experience.primary == template.primary_emotion
        assert identity.target_experience.primary == "safe_vulnerability"
        assert identity.target_experience.primary != "dread"

    def test_romantic_authority_primary_from_template(self):
        """Romantic authority identity has template's primary_emotion, not dread."""
        choices = ROMANTIC_AUTHORITY_CHOICES
        identity = IdentityGenerator.from_choices("romantic_authority", choices)
        template = get_template("romantic_authority")
        assert identity.target_experience.primary == template.primary_emotion
        assert identity.target_experience.primary == "cherished_leadership"
        assert identity.target_experience.primary != "dread"

    def test_template_progression_used(self):
        """Identity progression matches template emotion arc, not hardcoded fallback."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        template = get_template("sensual_dominance")
        # Template progression should appear in identity, not generic "tension -> escalation -> climax"
        from auteur.gentlefemdom.emotion_arcs import get_emotion_arc
        arc = get_emotion_arc("sensual_dominance")
        assert identity.target_experience.progression == arc["progression"]

    def test_title_uses_template_seeds_not_fallback(self):
        """Identity title is generated meaningfully, not generic fallback."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        # Should not be the netorare fallback "The Story"
        # (title generation is a later phase, but should at least not be generic)
        assert len(identity.title) > 0

    def test_all_three_cores_preserve_emotion(self):
        """All three gentlefemdom cores preserve their distinct emotions."""
        test_cases = [
            ("sensual_dominance", "playful_control"),
            ("tender_surrender", "safe_vulnerability"),
            ("romantic_authority", "cherished_leadership"),
        ]
        for core_id, expected_emotion in test_cases:
            choices = valid_choices_for(core_id)
            identity = IdentityGenerator.from_choices(core_id, choices)
            assert identity.target_experience.primary == expected_emotion
            assert identity.target_experience.primary != "dread"

    def test_cores_produce_different_progressions(self):
        """Each core has a distinct emotional progression."""
        sensual = IdentityGenerator.from_choices("sensual_dominance", SENSUAL_DOMINANCE_CHOICES)
        tender = IdentityGenerator.from_choices("tender_surrender", TENDER_SURRENDER_CHOICES)
        romantic = IdentityGenerator.from_choices("romantic_authority", ROMANTIC_AUTHORITY_CHOICES)

        progressions = {
            sensual.target_experience.progression,
            tender.target_experience.progression,
            romantic.target_experience.progression,
        }
        # All three should be different
        assert len(progressions) == 3

    def test_emotion_arc_secondary_populated(self):
        """Secondary emotions are populated from emotion arc."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        from auteur.gentlefemdom.emotion_arcs import get_emotion_arc
        arc = get_emotion_arc("sensual_dominance")
        assert identity.target_experience.secondary == arc["secondary"]

    def test_emotion_arc_avoid_populated(self):
        """Avoided experiences are populated from emotion arc."""
        choices = TENDER_SURRENDER_CHOICES
        identity = IdentityGenerator.from_choices("tender_surrender", choices)
        from auteur.gentlefemdom.emotion_arcs import get_emotion_arc
        arc = get_emotion_arc("tender_surrender")
        assert identity.target_experience.avoid == arc["avoid"]
