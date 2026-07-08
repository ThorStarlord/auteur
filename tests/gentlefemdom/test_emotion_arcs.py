"""
Tests for gentle femdom emotion arc data structures and API.
"""

import pytest
from auteur.gentlefemdom.emotion_arcs import EMOTION_ARCS, get_emotion_arc


class TestEmotionArcStructure:
    """Validate the structure and API contract of emotion arcs."""

    def test_emotion_arcs_dict_exists(self):
        """EMOTION_ARCS dict is defined and not None."""
        assert EMOTION_ARCS is not None
        assert isinstance(EMOTION_ARCS, dict)

    def test_all_three_cores_defined(self):
        """All three gentle femdom cores are defined in EMOTION_ARCS."""
        expected_cores = {"sensual_dominance", "tender_surrender", "romantic_authority"}
        assert set(EMOTION_ARCS.keys()) == expected_cores

    def test_emotion_arc_schema_sensual_dominance(self):
        """sensual_dominance arc has required keys with correct types."""
        arc = EMOTION_ARCS["sensual_dominance"]
        assert "primary" in arc and isinstance(arc["primary"], str)
        assert "progression" in arc and isinstance(arc["progression"], str)
        assert "secondary" in arc and isinstance(arc["secondary"], list)
        assert "avoid" in arc and isinstance(arc["avoid"], list)

    def test_emotion_arc_schema_tender_surrender(self):
        """tender_surrender arc has required keys with correct types."""
        arc = EMOTION_ARCS["tender_surrender"]
        assert "primary" in arc and isinstance(arc["primary"], str)
        assert "progression" in arc and isinstance(arc["progression"], str)
        assert "secondary" in arc and isinstance(arc["secondary"], list)
        assert "avoid" in arc and isinstance(arc["avoid"], list)

    def test_emotion_arc_schema_romantic_authority(self):
        """romantic_authority arc has required keys with correct types."""
        arc = EMOTION_ARCS["romantic_authority"]
        assert "primary" in arc and isinstance(arc["primary"], str)
        assert "progression" in arc and isinstance(arc["progression"], str)
        assert "secondary" in arc and isinstance(arc["secondary"], list)
        assert "avoid" in arc and isinstance(arc["avoid"], list)

    def test_progression_strings_are_substantive(self):
        """Each progression string is non-empty."""
        for core_id, arc in EMOTION_ARCS.items():
            assert len(arc["progression"]) > 0, f"{core_id} progression is empty"

    def test_secondary_emotions_are_lists_of_strings(self):
        """Secondary emotions are non-empty lists containing only strings."""
        for core_id, arc in EMOTION_ARCS.items():
            assert len(arc["secondary"]) > 0, f"{core_id} secondary is empty"
            for emotion in arc["secondary"]:
                assert isinstance(emotion, str), f"{core_id} secondary contains non-string: {emotion}"

    def test_avoided_experiences_are_lists_of_strings(self):
        """Avoided experiences are non-empty lists containing only strings."""
        for core_id, arc in EMOTION_ARCS.items():
            assert len(arc["avoid"]) > 0, f"{core_id} avoid is empty"
            for experience in arc["avoid"]:
                assert isinstance(experience, str), f"{core_id} avoid contains non-string: {experience}"

    def test_get_emotion_arc_function_exists(self):
        """get_emotion_arc function exists and is callable."""
        assert callable(get_emotion_arc)

    def test_get_emotion_arc_handles_invalid_core(self):
        """get_emotion_arc raises ValueError for unknown core_id."""
        with pytest.raises(ValueError) as exc_info:
            get_emotion_arc("nonexistent_core")
        error_msg = str(exc_info.value)
        assert "Unknown gentle femdom core" in error_msg


class TestEmotionArcContents:
    """Validate the semantic correctness of emotion arc content."""

    def test_sensual_dominance_primary_emotion(self):
        """sensual_dominance primary emotion is 'playful_control'."""
        arc = EMOTION_ARCS["sensual_dominance"]
        assert arc["primary"] == "playful_control"

    def test_sensual_dominance_avoids_non_consent(self):
        """sensual_dominance avoids non-consensual experiences."""
        arc = EMOTION_ARCS["sensual_dominance"]
        avoid = arc["avoid"]
        assert "shame" in avoid
        assert "humiliation_without_consent" in avoid
        assert "coercion" in avoid
        assert "fear" in avoid

    def test_tender_surrender_primary_emotion(self):
        """tender_surrender primary emotion is 'safe_vulnerability'."""
        arc = EMOTION_ARCS["tender_surrender"]
        assert arc["primary"] == "safe_vulnerability"

    def test_tender_surrender_progression_describes_journey(self):
        """tender_surrender progression describes emotional journey."""
        arc = EMOTION_ARCS["tender_surrender"]
        progression = arc["progression"]
        # Check for key waypoints in the journey
        assert "defensiveness" in progression
        assert "curiosity" in progression
        assert "opening" in progression
        assert "release" in progression
        assert "security" in progression

    def test_romantic_authority_primary_emotion(self):
        """romantic_authority primary emotion is 'cherished_leadership'."""
        arc = EMOTION_ARCS["romantic_authority"]
        assert arc["primary"] == "cherished_leadership"

    def test_romantic_authority_progression_shows_partnership(self):
        """romantic_authority progression shows interdependence and mutual respect."""
        arc = EMOTION_ARCS["romantic_authority"]
        progression = arc["progression"]
        # Check for key aspects of partnership
        assert "admiration" in progression
        assert "deference" in progression
        assert "interdependence" in progression
        assert "respect" in progression
        assert "love" in progression

    def test_all_secondary_emotions_are_lowercase(self):
        """All secondary emotions are lowercase strings."""
        for core_id, arc in EMOTION_ARCS.items():
            for emotion in arc["secondary"]:
                assert emotion == emotion.lower(), \
                    f"{core_id} secondary contains non-lowercase: {emotion}"

    def test_no_duplicates_in_secondary_or_avoid(self):
        """No duplicate values within secondary or avoid lists per core."""
        for core_id, arc in EMOTION_ARCS.items():
            secondary = arc["secondary"]
            avoid = arc["avoid"]
            assert len(secondary) == len(set(secondary)), \
                f"{core_id} secondary has duplicates"
            assert len(avoid) == len(set(avoid)), \
                f"{core_id} avoid has duplicates"
