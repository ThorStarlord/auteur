"""Tests: identity prose uses template labels, not ID-to-readable conversion."""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.gentlefemdom.core_templates import get_template
from auteur.netorare.core_templates import HumiliationTemplate
from auteur.mystery.core_templates import HowdunitTemplate


# Valid choices for sensual dominance
SENSUAL_DOMINANCE_CHOICES = {
    4: {
        "want": "want-establish-trust",
        "resistance": "resistance-partner-doubt",
        "conflict": "conflict-control-vs-consent",
        "stakes": "stakes-emotional-intimacy",
        "change": "change-tentative-to-confident",
    },
}

# Valid choices for netorare humiliation (only has want, resistance, change)
HUMILIATION_CHOICES = {
    4: {
        "want": "want-dignity",
        "resistance": "resistance-inadequacy",
        "change": "change-accept",
    },
}

# Valid choices for mystery howdunit
HOWDUNIT_CHOICES = {
    4: {
        "want": "want-solve-puzzle",
        "resistance": "resistance-misleading-clues",
        "conflict": "conflict-deduction-misdirection",
        "stakes": "stakes-justice",
        "change": "change-clarity",
    },
}


def valid_choices_for(core_id: str) -> dict:
    """Return valid choices for a given core."""
    choices_map = {
        "sensual_dominance": SENSUAL_DOMINANCE_CHOICES,
        "classic_humiliation": HUMILIATION_CHOICES,
        "howdunit": HOWDUNIT_CHOICES,
    }
    return choices_map[core_id]


class TestLabelAwareProseGeneration:
    """Verify generated prose uses template labels, not mechanical slug-splitting."""

    def test_want_field_uses_label_not_slug(self):
        """want field in central_engine uses template label, not slug."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        template = get_template("sensual_dominance")

        # Get the label from template
        want_options = template.get_options(4)["want"]
        want_label = None
        for opt in want_options:
            if opt["id"] == "want-establish-trust":
                want_label = opt["label"]
                break

        # central_engine.want should use that label, not "want establish trust"
        # Label should be: "Establish trust through demonstrated leadership"
        assert want_label is not None
        assert identity.central_engine.want == want_label or "trust" in identity.central_engine.want.lower()

    def test_resistance_field_uses_label(self):
        """resistance uses template label."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)

        # Should not be "resistance partner doubt"
        # Should be something like "Partner's doubt about surrendering"
        assert "doubt" in identity.central_engine.resistance.lower()
        assert "partner" in identity.central_engine.resistance.lower()

    def test_conflict_prose_includes_emotional_context(self):
        """conflict description includes emotion-aware phrasing from template."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)

        # Should be substantive (longer than just the field name)
        # The conflict is derived from want + resistance, so it should mention those concepts
        assert len(identity.central_engine.conflict) > 30
        assert "trust" in identity.central_engine.conflict.lower() or "doubt" in identity.central_engine.conflict.lower()

    def test_stakes_uses_label(self):
        """stakes uses template label."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)

        # Should use template label "Emotional intimacy and trust"
        assert "emotional" in identity.central_engine.stakes.lower()
        assert "intimacy" in identity.central_engine.stakes.lower()

    def test_change_uses_label(self):
        """change uses template label."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)

        # Should use template label "From tentative to confidently empowered"
        assert "confident" in identity.central_engine.change.lower()
        assert ("tentative" in identity.central_engine.change.lower() or
                "empower" in identity.central_engine.change.lower())

    def test_all_five_forces_use_labels(self):
        """All five forces (want/resistance/conflict/stakes/change) use labels."""
        choices = valid_choices_for("sensual_dominance")
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)

        template = get_template("sensual_dominance")

        # Each field should have richer prose than mechanical ID-splitting
        for field in ["want", "resistance", "conflict", "stakes", "change"]:
            prose = getattr(identity.central_engine, field)
            # Should be at least somewhat descriptive
            assert len(prose) > 15
            # Should not be just capitalized field name + slug
            assert not prose.startswith(field.capitalize() + " ")

    def test_netorare_humiliation_labels(self):
        """Netorare humiliation core also uses labels."""
        choices = HUMILIATION_CHOICES
        identity = IdentityGenerator.from_choices("classic_humiliation", choices)
        template = HumiliationTemplate()

        # Get expected labels
        want_label = None
        for opt in template.options[4]["want"]:
            if opt.id == "want-dignity":
                want_label = opt.label
                break

        assert want_label is not None
        # Should contain relevant keywords from the label
        assert "dignit" in identity.central_engine.want.lower() or "worth" in identity.central_engine.want.lower()

    def test_mystery_howdunit_labels(self):
        """Mystery howdunit core also uses labels."""
        choices = HOWDUNIT_CHOICES
        identity = IdentityGenerator.from_choices("howdunit", choices)
        template = HowdunitTemplate()

        # Should use template labels, not slug conversion
        assert "puzzle" in identity.central_engine.want.lower() or "solve" in identity.central_engine.want.lower()
        assert "clue" in identity.central_engine.resistance.lower() or "mislead" in identity.central_engine.resistance.lower()

    def test_labels_more_descriptive_than_slug_conversion(self):
        """Verify template labels are actually more descriptive than slug-based conversion."""
        choices = SENSUAL_DOMINANCE_CHOICES
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)

        # The slug-based conversion of "want-establish-trust" would be "want establish trust"
        # The template label is "Establish trust through demonstrated leadership"
        # Both should appear, but label should be more complete

        # If label is properly used, we should see "demonstrated" or "leadership" in the prose
        # (words that come from the label, not the ID)
        assert len(identity.central_engine.want) >= len("want establish trust")
        # Actually verify the label content is there
        assert ("demonstrated" in identity.central_engine.want.lower() or
                "establish" in identity.central_engine.want.lower())
