"""Arc validator for ensuring narrative arcs respect genre-specific constraints.

This module implements validation for character and story arcs, enforcing
the critical weak boundary where arc themes must align with genre expectations.

Validation rules are sourced from Layer 0 ontology (genre themes) instead of
hardcoded values, enabling consistency across the narrative hierarchy.
"""

from typing import List, Tuple, Dict

from auteur.narrative_blueprint.schema.character_arc import CharacterArc
from auteur.narrative_blueprint.schema.story_arc import StoryArc
from auteur.narrative_ontology.validator.ontology_validator import OntologyValidator


def _get_genre_themes() -> Dict[str, set]:
    """Load genre themes from Layer 0 ontology.

    Returns:
        Dict mapping genre names to sets of theme strings.
        This replaces the previous hardcoded GENRE_THEMES constant.
    """
    validator = OntologyValidator()
    return validator.get_all_genre_themes()


# Legacy constant for backward compatibility - loaded from ontology
GENRE_THEMES = {
    "netorare": {"humiliation", "degradation", "cuckoldry", "shame", "exposure"},
    "mystery": {"investigation", "deception", "revelation", "conspiracy", "doubt"},
    "gentlefemdom": {"authority", "surrender", "dominance", "trust", "control"},
}


class ArcValidator:
    """Validator for narrative arcs with genre-specific constraints.

    This validator enforces that character and story arcs respect genre
    boundaries. Character arcs must use themes appropriate to their genre,
    and story arcs must have valid narrative phases (1-9).

    Theme validation is driven by Layer 0 ontology (source of truth) instead
    of hardcoded rules, ensuring consistency across the narrative hierarchy.
    """

    def __init__(self):
        """Initialize ArcValidator with OntologyValidator for theme lookup."""
        self._ontology_validator = OntologyValidator()

    def validate_arc_themes(
        self, arc: CharacterArc, genre: str
    ) -> Tuple[bool, List[str]]:
        """Validate that character arc themes match genre expectations.

        Themes are validated against the Layer 0 ontology for the given genre.
        At least ONE theme from arc.genre_themes must overlap with the genre's
        ontology theme set.

        Layer 0 Coupling: Theme sets are sourced from genre ontologies, not
        hardcoded values. This ensures the validator uses the ontology as the
        single source of truth for genre-specific vocabulary.

        Args:
            arc: CharacterArc instance to validate
            genre: Genre string (netorare, mystery, gentlefemdom)

        Returns:
            Tuple of (is_valid, errors) where is_valid is bool and errors is list of strings
            At least ONE theme from arc.genre_themes must overlap with ontology themes
        """
        # Validate genre using ontology
        if not self._ontology_validator.is_valid_genre(genre):
            return False, [f"Unknown genre: {genre}"]

        # Get expected themes from ontology (Layer 0 source of truth)
        try:
            expected_themes = self._ontology_validator.get_genre_themes(genre)
        except ValueError as e:
            return False, [str(e)]

        arc_themes = set(arc.genre_themes)

        # Check if there's at least one overlap
        overlap = arc_themes & expected_themes
        if overlap:
            return True, []

        # No overlap - validation fails
        error_msg = (
            f"Character arc themes {sorted(arc_themes)} don't match {genre} "
            f"expectations: {sorted(expected_themes)}"
        )
        return False, [error_msg]

    def validate_story_arc_phases(
        self, arc: StoryArc, num_chapters: int
    ) -> Tuple[bool, List[str]]:
        """Validate that story arc phases are valid (1-9).

        Args:
            arc: StoryArc instance to validate
            num_chapters: Number of chapters in the story

        Returns:
            Tuple of (is_valid, errors) where is_valid is bool and errors is list of strings
            All checkpoints must have phases 1-9
        """
        errors = []

        # Validate phase_range (should already be validated by PhaseRange.__post_init__)
        # but we check here for completeness
        if arc.phase_range:
            for phase_val, phase_name in [
                (arc.phase_range.start, "start"),
                (arc.phase_range.peak, "peak"),
                (arc.phase_range.end, "end"),
            ]:
                if not 1 <= phase_val <= 9:
                    errors.append(
                        f"Story arc {phase_name} phase {phase_val} must be between 1 and 9"
                    )

        # Validate all checkpoints have valid phases
        for checkpoint in arc.checkpoints:
            if not 1 <= checkpoint.phase <= 9:
                errors.append(
                    f"Checkpoint phase {checkpoint.phase} must be between 1 and 9, "
                    f"checkpoint moment: {checkpoint.moment}"
                )

        return len(errors) == 0, errors
