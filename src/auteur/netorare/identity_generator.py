"""Generate validated story_identity.yaml from netorare choice decisions.

This module bridges the browser UI choice pipeline with auteur's StoryIdentity schema.
It accepts raw choices, validates them, transforms them into a StoryIdentity Pydantic
model, and serializes to YAML that passes auteur's identity validate command.
"""

from typing import Dict, Any
import yaml

from auteur.netorare.validation import validate_choices
from auteur.netorare.core_templates import HumiliationTemplate, HorrorTemplate, MysteryTemplate
from auteur.identity import StoryIdentity, StoryType, HighLevelCentralEngine
from auteur.blueprint import StoryMode, StoryMedium, TargetAudience, Genre, TargetExperience, LengthClass


class IdentityGenerator:
    """Generate StoryIdentity from netorare choice decisions."""

    # Map core_id to template class
    TEMPLATE_MAP = {
        "classic_humiliation": HumiliationTemplate,
        "horror": HorrorTemplate,
        "mystery": MysteryTemplate,
        # Mystery-specific cores
        "howdunit": "mystery",  # Will use mystery validation
        "paranoia": "mystery",  # Will use mystery validation
        "cozy": "mystery",  # Will use mystery validation
        # Gentle femdom cores
        "sensual_dominance": "gentlefemdom",  # Will use gentlefemdom validation
        "tender_surrender": "gentlefemdom",  # Will use gentlefemdom validation
        "romantic_authority": "gentlefemdom",  # Will use gentlefemdom validation
    }

    # Map core_id to genre
    CORE_ID_TO_GENRE = {
        "classic_humiliation": Genre.NETORARE,
        "horror": Genre.HORROR,
        "mystery": Genre.MYSTERY,
        # Mystery-specific cores
        "howdunit": Genre.MYSTERY,
        "paranoia": Genre.MYSTERY,
        "cozy": Genre.MYSTERY,
        # Gentle femdom cores
        "sensual_dominance": Genre.GENTLEFEMDOM,
        "tender_surrender": Genre.GENTLEFEMDOM,
        "romantic_authority": Genre.GENTLEFEMDOM,
    }

    @classmethod
    def from_choices(cls, core_id: str, choices: Dict[int, Dict[str, str]]) -> StoryIdentity:
        """
        Generate a validated StoryIdentity from raw browser UI choices.

        Args:
            core_id: The core template identifier (classic_humiliation, horror, mystery, howdunit, paranoia, cozy)
            choices: Dict mapping phase (1-9) -> {field: value}

        Returns:
            Validated StoryIdentity model

        Raises:
            ValueError: If choices fail validation
            KeyError: If core_id is not recognized
        """
        # Get the template class
        if core_id not in cls.TEMPLATE_MAP:
            raise KeyError(f"Unknown core_id: {core_id}. Must be one of {list(cls.TEMPLATE_MAP.keys())}")

        template_or_name = cls.TEMPLATE_MAP[core_id]

        # Handle mystery-specific cores (howdunit, paranoia, cozy)
        if core_id in ["howdunit", "paranoia", "cozy"]:
            # Use mystery-specific validation
            from auteur.mystery.core_templates import get_template as get_mystery_template
            template = get_mystery_template(core_id)
            from auteur.mystery.validation import validate_choices as validate_mystery_choices
            is_valid, errors, warnings = validate_mystery_choices(template, choices)
        # Handle gentlefemdom-specific cores (sensual_dominance, tender_surrender, romantic_authority)
        elif core_id in ["sensual_dominance", "tender_surrender", "romantic_authority"]:
            # Use gentlefemdom-specific validation
            from auteur.gentlefemdom.core_templates import get_template as get_gentlefemdom_template
            template = get_gentlefemdom_template(core_id)
            from auteur.gentlefemdom.validation import validate_choices as validate_gentlefemdom_choices
            is_valid, errors, warnings = validate_gentlefemdom_choices(template, choices)
        else:
            # Use netorare validation
            template = template_or_name()
            is_valid, errors, warnings = validate_choices(template, choices)

        if not is_valid:
            error_msg = "; ".join(errors)
            raise ValueError(f"Choices validation failed: {error_msg}")

        # Transform choices into StoryIdentity
        identity = cls._transform_choices_to_identity(core_id, choices)

        return identity

    @classmethod
    def _transform_choices_to_identity(cls, core_id: str, choices: Dict[int, Dict[str, str]]) -> StoryIdentity:
        """
        Internal: Transform validated choices into StoryIdentity schema.

        Maps each layer of choices to corresponding StoryIdentity fields:
        - Layer 1 (emotional_core) -> TargetExperience
        - Layer 2 (genre_contract) -> Story Type fields
        - Layer 3 (scope) -> Story Type fields
        - Layer 4 (structural_forces) -> central_engine + conflict generation
        - Layers 5-9 -> metadata (open_questions, alternatives, etc.)
        """
        layer1 = choices.get(1, {})
        layer2 = choices.get(2, {})
        layer3 = choices.get(3, {})
        layer4 = choices.get(4, {})
        layer5 = choices.get(5, {})
        layer6 = choices.get(6, {})
        layer7 = choices.get(7, {})
        layer8 = choices.get(8, {})
        layer9 = choices.get(9, {})

        # Extract core engine components
        want = layer4.get("want", "")
        resistance = layer4.get("resistance", "")
        change = layer4.get("change", "")
        stakes = layer4.get("stakes", "")

        # Generate derived conflict
        conflict = cls._generate_conflict(want, resistance, change)

        # Create central engine
        central_engine = HighLevelCentralEngine(
            want=want,
            resistance=resistance,
            conflict=conflict,
            stakes=stakes,
            change=change,
        )

        # Determine genre
        genre = cls.CORE_ID_TO_GENRE.get(core_id, Genre.NETORARE)

        # Create story type
        story_type = StoryType(
            medium=StoryMedium.NOVEL,
            mode=StoryMode.TRAGIC,
            genre=genre,
            subgenres=[],
            target_audience=TargetAudience.ADULT,
            length_class=LengthClass.NOVEL,
        )

        # Create target experience
        target_experience = TargetExperience(
            primary=cls._get_primary_emotion(core_id),
            progression=cls._get_progression(core_id, change),
            avoid=cls._get_avoided_experiences(core_id),
        )

        # For gentlefemdom cores, populate secondary emotions from emotion arc
        # (netorare/mystery don't have structured secondary emotions yet)
        try:
            if core_id in ("sensual_dominance", "tender_surrender", "romantic_authority"):
                from auteur.gentlefemdom.emotion_arcs import get_emotion_arc

                emotion_arc = get_emotion_arc(core_id)
                target_experience.secondary = emotion_arc["secondary"]
        except (ImportError, ValueError, KeyError):
            # Fall back to no secondary emotions if emotion arc unavailable
            pass

        # Generate title and core answer
        title = cls._generate_title(core_id, want, resistance)
        core_answer = cls._generate_core_answer(core_id, want, resistance, change)

        # Collect metadata from later layers
        open_questions = cls._generate_open_questions(core_id, layer7, layer8, layer9)
        alternatives = cls._generate_alternatives(core_id)

        # Create the StoryIdentity
        identity = StoryIdentity(
            title=title,
            core_answer=core_answer,
            target_experience=target_experience,
            story_type=story_type,
            central_engine=central_engine,
            open_questions=open_questions,
            alternatives=alternatives,
            confidence=0.75,
        )

        return identity

    @classmethod
    def _generate_conflict(cls, want: str, resistance: str, change: str) -> str:
        """Generate a coherent conflict statement from engine components."""
        if not want or not resistance:
            return "The protagonist faces an impossible choice."

        # Extract readable versions from choice IDs
        want_readable = cls._readable_from_id(want)
        resistance_readable = cls._readable_from_id(resistance)
        change_readable = cls._readable_from_id(change)

        # Generate conflict that describes the dramatic tension
        templates = [
            f"The drive to {want_readable} is blocked by {resistance_readable}, forcing a choice between accepting loss and fighting back.",
            f"{want_readable.capitalize()} conflicts with {resistance_readable}, leaving only the option to {change_readable}.",
            f"Attempting to {want_readable} collides with {resistance_readable}, resulting in inevitable {change_readable}.",
        ]

        return templates[0]  # Use first template for consistency

    @classmethod
    def _readable_from_id(cls, choice_id: str) -> str:
        """Convert choice ID (e.g., 'want-dignity') to readable phrase."""
        if not choice_id:
            return "proceed"

        # Remove prefix and capitalize
        parts = choice_id.split("-", 1)
        if len(parts) == 2:
            phrase = parts[1].replace("-", " ")
        else:
            phrase = choice_id.replace("-", " ")

        return phrase.lower()

    @classmethod
    def _get_template_for_core(cls, core_id: str):
        """Get template for any core, regardless of genre.

        Tries netorare first (for backwards compatibility), then mystery, then gentlefemdom.
        """
        # Try netorare
        if core_id in ("classic_humiliation", "horror", "mystery"):
            from auteur.netorare.core_templates import get_template as get_netorare_template
            return get_netorare_template(core_id)

        # Try mystery-specific cores
        if core_id in ("howdunit", "paranoia", "cozy"):
            from auteur.mystery.core_templates import get_template as get_mystery_template
            return get_mystery_template(core_id)

        # Try gentlefemdom
        if core_id in ("sensual_dominance", "tender_surrender", "romantic_authority"):
            from auteur.gentlefemdom.core_templates import get_template as get_gentlefemdom_template
            return get_gentlefemdom_template(core_id)

        # Unknown core
        raise ValueError(f"Unknown core_id: {core_id}")

    @classmethod
    def _get_primary_emotion(cls, core_id: str) -> str:
        """Get primary target emotion for the core type.

        Sources this from the core's template rather than hardcoded maps,
        ensuring all genres consistently use their template's primary_emotion.
        """
        try:
            # Try to get template for any genre (netorare, mystery, gentlefemdom, etc.)
            template = cls._get_template_for_core(core_id)
            if hasattr(template, 'primary_emotion'):
                return template.primary_emotion
        except (ImportError, ValueError, AttributeError):
            pass

        # Fallback for unknown cores
        return "unknown"

    @classmethod
    def _get_progression(cls, core_id: str, change: str) -> str:
        """Get emotional progression for the core type.

        Sources this from the core's emotion arc (if available) rather than hardcoded maps,
        ensuring consistent emotion propagation from template to identity.
        """
        try:
            # Try to get emotion arc for gentlefemdom cores
            if core_id in ("sensual_dominance", "tender_surrender", "romantic_authority"):
                from auteur.gentlefemdom.emotion_arcs import get_emotion_arc
                arc = get_emotion_arc(core_id)
                return arc["progression"]
        except (ImportError, ValueError, KeyError):
            pass

        # Fallback: use hardcoded progressions for netorare/mystery cores
        fallback_progressions = {
            "classic_humiliation": "unease -> suspicion -> humiliation -> acceptance",
            "horror": "unease -> dread -> cosmic horror -> transformation",
            "mystery": "curiosity -> suspicion -> revelation -> complicity",
            "howdunit": "curiosity -> suspicion -> revelation -> complicity",
            "paranoia": "unease -> suspicion -> paranoia -> transformation",
            "cozy": "curiosity -> discovery -> comfort -> satisfaction",
        }
        return fallback_progressions.get(core_id, "tension -> escalation -> climax")

    @classmethod
    def _get_avoided_experiences(cls, core_id: str) -> list[str]:
        """Get list of experiences to avoid for the core type.

        Sources this from the core's emotion arc (if available) rather than hardcoded maps,
        ensuring consistent emotion propagation from template to identity.
        """
        try:
            # Try to get emotion arc for gentlefemdom cores
            if core_id in ("sensual_dominance", "tender_surrender", "romantic_authority"):
                from auteur.gentlefemdom.emotion_arcs import get_emotion_arc
                arc = get_emotion_arc(core_id)
                return arc["avoid"]
        except (ImportError, ValueError, KeyError):
            pass

        # Fallback: use hardcoded avoidances for netorare/mystery cores
        avoid_map = {
            "classic_humiliation": [
                "triumphant vindication",
                "cozy comfort",
                "clean redemption",
            ],
            "horror": [
                "cozy safety",
                "triumphant power fantasy",
                "return to normalcy",
            ],
            "mystery": [
                "ignorant innocence",
                "pure heroic victory",
                "easy answers",
            ],
            "howdunit": [
                "ignorant innocence",
                "pure heroic victory",
                "easy answers",
            ],
            "paranoia": [
                "cozy safety",
                "absolute trust",
                "simple solutions",
            ],
            "cozy": [
                "dark secrets exposed",
                "cynicism confirmed",
                "harmony destroyed",
            ],
        }
        return avoid_map.get(core_id, [])

    @classmethod
    def _generate_title(cls, core_id: str, want: str, resistance: str) -> str:
        """Generate a dramatic title from core elements."""
        templates = {
            "classic_humiliation": [
                "The Cost of Love",
                "Where Dignity Fails",
                "Powerless",
                "The Fall",
                "When the Truth Emerges",
            ],
            "horror": [
                "The Inescapable",
                "What Cannot Be Undone",
                "The Deep",
                "Transformations",
                "The Price of Knowledge",
            ],
            "mystery": [
                "The Hidden Truth",
                "Complicity",
                "What We Discover",
                "The Reckoning",
                "Questions Without Answers",
            ],
        }

        titles = templates.get(core_id, ["The Story"])
        # Use first title consistently
        return titles[0]

    @classmethod
    def _generate_core_answer(cls, core_id: str, want: str, resistance: str, change: str) -> str:
        """Generate a compelling core answer describing the story's essence."""
        want_readable = cls._readable_from_id(want)
        resistance_readable = cls._readable_from_id(resistance)
        change_readable = cls._readable_from_id(change)

        templates = {
            "classic_humiliation": f"A story about the impossible pursuit of {want_readable} in the face of {resistance_readable}, ending in {change_readable}.",
            "horror": f"A narrative where attempts to {want_readable} are thwarted by {resistance_readable}, transforming the protagonist through {change_readable}.",
            "mystery": f"An investigation seeking {want_readable} discovers {resistance_readable}, forcing the seeker into {change_readable}.",
        }

        return templates.get(core_id, f"A story where the protagonist attempts to {want_readable} but is blocked by {resistance_readable}.")

    @classmethod
    def _generate_open_questions(cls, core_id: str, layer7: dict, layer8: dict, layer9: dict) -> list[str]:
        """Generate open questions based on core type and layer choices."""
        questions = {
            "classic_humiliation": [
                "How much does the MC's own failings contribute to the humiliation?",
                "Will there be any moment of grace or connection before the final fall?",
                "How aware are others of the MC's struggle?",
                "Is there any path to dignity that doesn't involve surrender?",
            ],
            "horror": [
                "What is the true nature of the inescapable threat?",
                "How much of the protagonist's transformation is inevitable?",
                "Can knowledge bring safety, or does it deepen the horror?",
                "What remains after the transformation?",
            ],
            "mystery": [
                "What happens when the truth is finally known?",
                "How does the discovery change the investigator?",
                "Are there other truths buried beneath the surface?",
                "Who else is complicit in the hidden truth?",
            ],
        }

        return questions.get(core_id, [
            "What is at stake in this story?",
            "How will the protagonist change?",
            "What remains unresolved?",
        ])

    @classmethod
    def _generate_alternatives(cls, core_id: str) -> list[str]:
        """Generate alternative directions for the story."""
        alternatives = {
            "classic_humiliation": [
                "A version where the rival is unaware of the humiliation's impact.",
                "A version where the MC chooses confrontation instead of acceptance.",
                "A version told from multiple perspectives.",
            ],
            "horror": [
                "A version where resistance is possible.",
                "A version where the transformation is reversed.",
                "A version where others can help.",
            ],
            "mystery": [
                "A version where the truth was never meant to be found.",
                "A version where others were protecting the secret.",
                "A version where the investigator was complicit all along.",
            ],
        }

        return alternatives.get(core_id, [
            "Alternative approach: shift the emotional focus",
            "Alternative approach: change the resolution type",
            "Alternative approach: expand the scope",
        ])

    @staticmethod
    def to_yaml(story_identity: StoryIdentity) -> str:
        """
        Serialize a StoryIdentity to YAML format.

        Args:
            story_identity: The StoryIdentity model to serialize

        Returns:
            YAML-formatted string suitable for story_identity.yaml file

        Note:
            The output YAML can be validated with: auteur identity validate story_identity.yaml
        """
        # Convert to dict using Pydantic's model_dump with serialization mode
        identity_dict = story_identity.model_dump(
            mode="json",  # Use JSON mode to serialize enums to strings
            exclude_none=True,
            by_alias=False,
        )

        # Serialize to YAML with nice formatting
        yaml_str = yaml.dump(
            identity_dict,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        )

        return yaml_str
