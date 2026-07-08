"""
Emotion arc constants and functions for gentle femdom genre.

Defines the emotional progression for each gentle femdom core,
including primary emotions, secondary emotional layers, and
experiences to avoid for safety and consent integrity.
"""

EMOTION_ARCS = {
    "sensual_dominance": {
        "primary": "playful_control",
        "progression": "intrigue -> playful_teasing -> deepening_connection -> intimate_confidence -> sustained_delight",
        "secondary": ["trust", "enjoyment", "agency", "anticipation"],
        "avoid": ["shame", "humiliation_without_consent", "coercion", "fear"],
    },
    "tender_surrender": {
        "primary": "safe_vulnerability",
        "progression": "defensiveness -> curiosity -> gradual_opening -> blissful_release -> cherished_security",
        "secondary": ["trust", "freedom", "emotional_growth", "acceptance"],
        "avoid": ["coercion", "manipulation", "abandonment", "exposure"],
    },
    "romantic_authority": {
        "primary": "cherished_leadership",
        "progression": "admiration -> willing_deference -> secure_interdependence -> mutual_respect -> sustained_love",
        "secondary": ["respect", "care", "partnership", "confidence"],
        "avoid": ["inequality", "control_without_care", "diminishment", "resentment"],
    },
}


def get_emotion_arc(core_id: str) -> dict:
    """
    Retrieve the emotion arc for a given gentle femdom core.

    Args:
        core_id: One of "sensual_dominance", "tender_surrender", or "romantic_authority"

    Returns:
        dict: The emotion arc containing primary, progression, secondary, and avoid keys

    Raises:
        ValueError: If core_id is not a known gentle femdom core
    """
    if core_id not in EMOTION_ARCS:
        valid_cores = list(EMOTION_ARCS.keys())
        raise ValueError(
            f"Unknown gentle femdom core: {core_id}. Valid cores: {valid_cores}"
        )
    return EMOTION_ARCS[core_id]
