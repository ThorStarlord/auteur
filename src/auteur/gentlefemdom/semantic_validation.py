"""Semantic coherence validation for gentle femdom identities.

Ensures that generated identities have emotions matching their template's emotional core.
This catches silent semantic failures where structure is valid but meaning is wrong.
"""

from typing import Dict, Any


class SemanticCoherenceRule:
    """Validates that identity emotion matches template's primary emotional core.

    A structurally valid identity can still fail semantically if the generated
    emotion doesn't align with the template's intended emotional experience.
    """

    def __init__(self):
        """Initialize the semantic coherence rule."""
        self.name = "semantic_coherence"
        self.description = (
            "Verifies generated identity emotion matches template emotional core"
        )

    def validate(self, identity: Any, template: Any) -> Dict[str, Any]:
        """Validate that identity emotion matches template's primary emotion.

        Args:
            identity: StoryIdentity instance with target_experience field
            template: Template instance with primary_emotion field

        Returns:
            Dict with "passed" bool and either "reason" (on success) or "error" (on failure).
            Format:
            - {"passed": True} - emotions match
            - {"passed": True, "reason": "author_override"} - author override active
            - {"passed": False, "error": "message"} - mismatch with explanation
        """
        # Check for author override first
        if hasattr(identity, "author_overrides"):
            # author_overrides can be a dict or list depending on how it's used
            if isinstance(identity.author_overrides, dict):
                if identity.author_overrides.get("emotional_arc") is True:
                    return {"passed": True, "reason": "author_override"}
            elif isinstance(identity.author_overrides, list):
                # Check if it's a list containing the override marker
                if "emotional_arc" in identity.author_overrides:
                    return {"passed": True, "reason": "author_override"}

        # Get the identity's primary emotion
        identity_emotion = identity.target_experience.primary

        # Get the template's primary emotion
        template_emotion = template.primary_emotion

        # Check if they match
        if identity_emotion == template_emotion:
            return {"passed": True}

        # They don't match - construct error message
        error_message = (
            f"Semantic coherence violation: Selected template has primary emotion "
            f"'{template_emotion}' but generated identity has '{identity_emotion}'. "
            f"This indicates the template's emotional intent was not propagated during "
            f"identity generation. Override with author_overrides['emotional_arc'] = True "
            f"if intentional."
        )

        return {"passed": False, "error": error_message}
