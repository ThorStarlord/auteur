"""Tests: All genres preserve emotional intent through pipeline.

Phase 6: Comprehensive regression tests ensuring all 9 cores (3 netorare, 3 mystery,
3 gentlefemdom) preserve their distinct emotional intent through the entire pipeline
from templates to identity generation.

These tests catch any future regression where emotional intent is lost or collapsed.
"""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.netorare.core_templates import HumiliationTemplate, HorrorTemplate, MysteryTemplate
from auteur.mystery.core_templates import HowdunitTemplate, ParanoiaTemplate, CozyTemplate
from auteur.gentlefemdom.core_templates import (
    SensualDominanceTemplate, TenderSurrenderTemplate, RomanticAuthorityTemplate
)
from auteur.identity import StoryIdentity
from auteur.blueprint import Genre


# Helper data for valid choices per core
VALID_CHOICES = {
    "classic_humiliation": {
        4: {
            "want": "want-dignity",
            "resistance": "resistance-inadequacy",
            "conflict": "conflict-shame-vs-restoration",
            "stakes": "stakes-self-image",
            "change": "change-acceptance-defeat",
        }
    },
    "horror": {
        4: {
            "want": "want-escape",
            "resistance": "resistance-inescapable",
            "change": "change-transform",
            "stakes": "sanity and reality",
        }
    },
    "mystery": {
        4: {
            "want": "want-truth",
            "change": "change-witness",
            "resistance": "resistance-hidden-truth",
        }
    },
    "howdunit": {
        4: {
            "want": "want-solve-puzzle",
            "resistance": "resistance-misleading-clues",
            "conflict": "conflict-deduction-misdirection",
            "stakes": "stakes-justice",
            "change": "change-clarity",
        }
    },
    "paranoia": {
        4: {
            "want": "want-understand-threat",
            "resistance": "resistance-hidden-enemies",
            "conflict": "conflict-perception-vs-reality",
            "stakes": "stakes-sanity",
            "change": "change-fragmentation-certainty",
        }
    },
    "cozy": {
        4: {
            "want": "want-solve-mystery",
            "resistance": "resistance-misled-clues",
            "conflict": "conflict-investigation-friendship",
            "stakes": "stakes-community-peace",
            "change": "change-confusion-resolution",
        }
    },
    "sensual_dominance": {
        4: {
            "want": "want-establish-trust",
            "resistance": "resistance-partner-doubt",
            "conflict": "conflict-control-vs-consent",
            "stakes": "stakes-emotional-intimacy",
            "change": "change-tentative-to-confident",
        }
    },
    "tender_surrender": {
        4: {
            "want": "want-release-control",
            "resistance": "resistance-fear-vulnerability",
            "conflict": "conflict-self-protection-vs-desire",
            "stakes": "stakes-emotional-walls",
            "change": "change-defended-to-open",
        }
    },
    "romantic_authority": {
        4: {
            "want": "want-provide-protect",
            "resistance": "resistance-partner-independence",
            "conflict": "conflict-leadership-vs-partnership",
            "stakes": "stakes-relationship-balance",
            "change": "change-uncertain-to-confident",
        }
    },
}


class TestNetorareEmotionalPreservation:
    """Netorare cores preserve their distinct emotions."""

    @pytest.mark.parametrize("core_class,core_id,expected_emotion", [
        (HumiliationTemplate, "classic_humiliation", "humiliation"),
        (HorrorTemplate, "horror", "dread"),
        (MysteryTemplate, "mystery", "voyeurism"),
    ])
    def test_netorare_primary_emotion_preserved(self, core_class, core_id, expected_emotion):
        """Netorare cores preserve primary emotion from template to identity.

        Validates:
        - Template has correct primary_emotion attribute
        - Identity generator sources primary from template
        - Generated identity has matching primary emotion
        """
        # Verify template has expected emotion
        template = core_class()
        assert template.primary_emotion == expected_emotion

        # Generate identity from valid choices
        choices = VALID_CHOICES[core_id]
        identity = IdentityGenerator.from_choices(core_id, choices)

        # Verify identity preserves emotion
        assert identity is not None
        assert isinstance(identity, StoryIdentity)
        assert identity.target_experience.primary == expected_emotion
        assert identity.target_experience.primary == template.primary_emotion


class TestMysteryEmotionalPreservation:
    """Mystery cores preserve their distinct emotions."""

    @pytest.mark.parametrize("core_class,core_id,expected_emotion", [
        (HowdunitTemplate, "howdunit", "puzzle-solving"),
        (ParanoiaTemplate, "paranoia", "dread"),
        (CozyTemplate, "cozy", "comfort"),
    ])
    def test_mystery_primary_emotion_preserved(self, core_class, core_id, expected_emotion):
        """Mystery cores preserve primary emotion from template to identity.

        Validates:
        - Template has correct primary_emotion attribute
        - Identity generator sources primary from template
        - Generated identity has matching primary emotion
        """
        # Verify template has expected emotion
        template = core_class()
        assert template.primary_emotion == expected_emotion

        # Generate identity from valid choices
        choices = VALID_CHOICES[core_id]
        identity = IdentityGenerator.from_choices(core_id, choices)

        # Verify identity preserves emotion
        assert identity is not None
        assert isinstance(identity, StoryIdentity)
        assert identity.target_experience.primary == expected_emotion
        assert identity.target_experience.primary == template.primary_emotion


class TestGentlefemdomEmotionalPreservation:
    """Gentle femdom cores preserve their distinct emotions."""

    @pytest.mark.parametrize("core_class,core_id,expected_emotion", [
        (SensualDominanceTemplate, "sensual_dominance", "playful_control"),
        (TenderSurrenderTemplate, "tender_surrender", "safe_vulnerability"),
        (RomanticAuthorityTemplate, "romantic_authority", "cherished_leadership"),
    ])
    def test_gentlefemdom_primary_emotion_preserved(self, core_class, core_id, expected_emotion):
        """Gentle femdom cores preserve primary emotion from template to identity.

        Validates:
        - Template has correct primary_emotion attribute
        - Identity generator sources primary from template
        - Generated identity has matching primary emotion
        - Emotion does NOT collapse to generic netorare/mystery emotions (dread, tragic)
        """
        # Verify template has expected emotion
        template = core_class()
        assert template.primary_emotion == expected_emotion

        # Generate identity from valid choices
        choices = VALID_CHOICES[core_id]
        identity = IdentityGenerator.from_choices(core_id, choices)

        # Verify identity preserves emotion
        assert identity is not None
        assert isinstance(identity, StoryIdentity)
        assert identity.target_experience.primary == expected_emotion
        assert identity.target_experience.primary == template.primary_emotion

        # Verify emotion does NOT collapse to generic fallback emotions
        assert identity.target_experience.primary != "dread"
        assert identity.target_experience.primary != "tragic"
        assert identity.target_experience.primary != "humiliation"


class TestCrossGenreDistinctness:
    """All nine cores produce distinctly different identities."""

    def test_no_two_cores_produce_same_primary_emotion(self):
        """Cores have distinct primary emotions (some may intentionally overlap).

        This regression test catches the bug where all cores collapsed to identical
        emotions (like all becoming "dread" or all becoming "tragic").

        Note: Horror and Paranoia both intentionally have "dread" as their primary emotion,
        which is correct - they are both dread-based genres. The important thing is that:
        - Not all 8 cores collapse to the same emotion
        - Gentlefemdom cores have their own distinct emotions (not dread)
        - Netorare has humiliation (not dread)
        """
        cores = [
            HumiliationTemplate(),
            HorrorTemplate(),
            HowdunitTemplate(),
            ParanoiaTemplate(),
            CozyTemplate(),
            SensualDominanceTemplate(),
            TenderSurrenderTemplate(),
            RomanticAuthorityTemplate(),
        ]
        emotions = [c.primary_emotion for c in cores]

        # Should have at least 6 unique emotions (some can overlap intentionally)
        # Critical: gentlefemdom cores should NOT collapse to dread or other generic emotions
        unique_emotions = set(emotions)
        assert len(unique_emotions) >= 6, \
            f"Too many duplicates: {emotions}. Expected >= 6 unique, got {len(unique_emotions)}"

        # Should not contain fallback or collapsed values
        assert "unknown" not in emotions

        # Gentlefemdom emotions should be distinct from netorare/mystery
        gentlefemdom_emotions = {
            SensualDominanceTemplate().primary_emotion,
            TenderSurrenderTemplate().primary_emotion,
            RomanticAuthorityTemplate().primary_emotion,
        }
        netorare_mystery_dread = {"dread", "humiliation"}

        # No gentlefemdom emotion should be in the netorare/mystery dread set
        assert len(gentlefemdom_emotions & netorare_mystery_dread) == 0, \
            f"Gentlefemdom emotions collapsed to generic: {gentlefemdom_emotions & netorare_mystery_dread}"

    def test_identity_progression_contains_core_emotion_keywords(self):
        """Progression text includes keywords from core emotion.

        Validates that identity progression is semantically coherent with the core,
        not generic or formulaic.
        """
        test_cases = [
            (SensualDominanceTemplate(), "sensual_dominance",
             ["playful", "teasing", "connection", "trust"]),
            (TenderSurrenderTemplate(), "tender_surrender",
             ["opening", "trust", "release", "vulnerability"]),
            (RomanticAuthorityTemplate(), "romantic_authority",
             ["admiration", "deference", "leadership", "respect"]),
        ]

        for template, core_id, expected_keywords in test_cases:
            choices = VALID_CHOICES[core_id]
            identity = IdentityGenerator.from_choices(core_id, choices)

            # Get progression text and normalize
            progression_lower = identity.target_experience.progression.lower()

            # Should contain at least one keyword from the expected set
            found = [kw for kw in expected_keywords if kw in progression_lower]
            assert len(found) > 0, \
                f"{core_id} progression missing expected keywords {expected_keywords}. " \
                f"Got: {progression_lower}"


class TestGenreContractNonFallback:
    """Generated identities use real genre contracts, not fallback."""

    def test_gentlefemdom_contract_not_generic(self):
        """Gentle femdom identity contract is not generic fallback.

        Validates that gentlefemdom uses its own genre-specific contracts,
        not the netorare fallback contract.
        """
        choices = VALID_CHOICES["sensual_dominance"]
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)

        # Get the contract snapshot
        contract = identity.genre_contract_snapshot

        # Should NOT have the generic netorare fallback text
        assert "Actions have consequences and characters have clear intent." not in contract.core_truth, \
            "Identity incorrectly using generic netorare fallback contract"

        # Should have gentlefemdom-specific text (consent, care, power, etc.)
        contract_truth_lower = contract.core_truth.lower()
        has_gentlefemdom_content = (
            "consent" in contract_truth_lower or
            "care" in contract_truth_lower or
            "power" in contract_truth_lower or
            "trust" in contract_truth_lower or
            "intimate" in contract_truth_lower
        )
        assert has_gentlefemdom_content, \
            f"Identity missing gentlefemdom-specific contract content. " \
            f"Got contract: {contract.core_truth}"


class TestAllNineCoresGenerateValidIdentities:
    """All nine cores successfully generate valid StoryIdentity objects."""

    @pytest.mark.parametrize("core_id,template_class", [
        ("classic_humiliation", HumiliationTemplate),
        ("horror", HorrorTemplate),
        ("mystery", MysteryTemplate),
        ("howdunit", HowdunitTemplate),
        ("paranoia", ParanoiaTemplate),
        ("cozy", CozyTemplate),
        ("sensual_dominance", SensualDominanceTemplate),
        ("tender_surrender", TenderSurrenderTemplate),
        ("romantic_authority", RomanticAuthorityTemplate),
    ])
    def test_all_cores_generate_valid_identities(self, core_id, template_class):
        """All nine cores can generate valid StoryIdentity objects.

        Validates end-to-end pipeline: template -> validation -> identity generation.
        """
        # Get valid choices for this core
        choices = VALID_CHOICES[core_id]

        # Generate identity
        identity = IdentityGenerator.from_choices(core_id, choices)

        # Verify it's a valid StoryIdentity
        assert identity is not None
        assert isinstance(identity, StoryIdentity)

        # Verify core fields are populated
        assert identity.title is not None and len(identity.title) > 0
        assert identity.core_answer is not None and len(identity.core_answer) > 0
        assert identity.central_engine is not None
        assert identity.target_experience is not None
        assert identity.target_experience.primary is not None

        # Verify story type is correct
        assert identity.story_type is not None
        expected_genre = {
            "classic_humiliation": Genre.NETORARE,
            "horror": Genre.HORROR,
            "mystery": Genre.NETORARE,
            "howdunit": Genre.MYSTERY,
            "paranoia": Genre.MYSTERY,
            "cozy": Genre.MYSTERY,
            "sensual_dominance": Genre.GENTLEFEMDOM,
            "tender_surrender": Genre.GENTLEFEMDOM,
            "romantic_authority": Genre.GENTLEFEMDOM,
        }[core_id]
        assert identity.story_type.genre == expected_genre


class TestEmotionalCoreMappingAccuracy:
    """Verify primary_emotion mapping is accurate for all cores."""

    def test_netorare_cores_have_correct_emotions(self):
        """Netorare cores have expected primary emotions."""
        expected_map = {
            "classic_humiliation": "humiliation",
            "horror": "dread",
            "mystery": "voyeurism",
        }
        for core_id, expected_emotion in expected_map.items():
            template = IdentityGenerator._get_template_for_core(core_id)
            assert template.primary_emotion == expected_emotion

    def test_mystery_cores_have_correct_emotions(self):
        """Mystery cores have expected primary emotions."""
        expected_map = {
            "howdunit": "puzzle-solving",
            "paranoia": "dread",
            "cozy": "comfort",
        }
        for core_id, expected_emotion in expected_map.items():
            template = IdentityGenerator._get_template_for_core(core_id)
            assert template.primary_emotion == expected_emotion

    def test_gentlefemdom_cores_have_correct_emotions(self):
        """Gentle femdom cores have expected primary emotions."""
        expected_map = {
            "sensual_dominance": "playful_control",
            "tender_surrender": "safe_vulnerability",
            "romantic_authority": "cherished_leadership",
        }
        for core_id, expected_emotion in expected_map.items():
            template = IdentityGenerator._get_template_for_core(core_id)
            assert template.primary_emotion == expected_emotion
