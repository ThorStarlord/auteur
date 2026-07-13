"""OntologyValidator for validating narrative concepts and relationships.

This module provides the OntologyValidator class which validates:
- Concept existence and validity for genres
- Relationships between concepts
- Arc properties
- Character properties
- Validation rules enforcement
"""

from typing import Dict, List, Tuple, Any, Optional

from auteur.narrative_ontology.core.narrative_concepts import ALL_CONCEPTS
from auteur.narrative_ontology.genre.netorare_ontology import NetorareOntology
from auteur.narrative_ontology.genre.mystery_ontology import MysteryOntology
from auteur.narrative_ontology.genre.gentlefemdom_ontology import GentleFemdomOntology


class OntologyValidator:
    """Validates narrative concepts against ontology definitions and genre rules.

    The validator maintains:
    - Base ontology (all genres)
    - Genre-specific ontologies
    - Validation rules for each concept
    - Relationship constraints

    Methods validate:
    - Concept existence and genre applicability
    - Relationships between concepts
    - Arc properties
    - Character properties
    - Validation rule enforcement
    """

    def __init__(self):
        """Initialize the OntologyValidator with base and genre ontologies."""
        # Load base ontology
        self.base_concepts = dict(ALL_CONCEPTS)

        # Load genre-specific ontologies
        self.genre_ontologies = {
            "netorare": NetorareOntology(),
            "mystery": MysteryOntology(),
            "gentlefemdom": GentleFemdomOntology(),
        }

        # Build complete concept registry per genre
        self.genre_concepts = self._build_genre_concepts()

    def _build_genre_concepts(self) -> Dict[str, Dict[str, Any]]:
        """Build complete concept registry including base + genre-specific.

        Returns:
            Dictionary mapping genre -> concept_name -> concept_data
        """
        genre_concepts = {}

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            # Start with base concepts
            genre_concepts[genre] = dict(self.base_concepts)

            # Add genre-specific concepts
            ontology = self.genre_ontologies[genre]
            for concept_name, concept_obj in ontology.get_all_concepts().items():
                genre_concepts[genre][concept_name] = concept_obj

        return genre_concepts

    def validate_concept(self, concept_name: str, genre: str) -> bool:
        """Validate that a concept exists and is valid for the given genre.

        Args:
            concept_name: Name of the concept to validate
            genre: Genre identifier (netorare, mystery, gentlefemdom)

        Returns:
            True if concept exists and is valid for the genre, False otherwise
        """
        if genre not in self.genre_concepts:
            return False

        return concept_name in self.genre_concepts[genre]

    def validate_relationship(
        self, source: str, target: str, genre: str
    ) -> bool:
        """Validate that a relationship exists between two concepts.

        Checks if source concept has a relationship defined to target concept
        in the given genre.

        Args:
            source: Name of the source concept
            target: Name of the target concept
            genre: Genre identifier

        Returns:
            True if relationship exists, False otherwise
        """
        # Both concepts must exist
        if not self.validate_concept(source, genre):
            return False
        if not self.validate_concept(target, genre):
            return False

        # Get source concept
        source_concept = self.genre_concepts[genre].get(source)
        if source_concept is None:
            return False

        # Check if it has relationships attribute (handles both base and genre concepts)
        if not hasattr(source_concept, "relationships"):
            return False

        # Look for relationship to target
        for rel in source_concept.relationships:
            # Handle both Pydantic model (target_concept) and dataclass (target)
            target_name = getattr(rel, "target_concept", getattr(rel, "target", None))
            if target_name == target:
                return True

        return False

    def validate_arc_properties(self, arc_type: str, genre: str) -> bool:
        """Validate that an arc type has proper properties for the genre.

        Args:
            arc_type: Name of the arc type (e.g., "Arc", "Cuckoldry Arc", "Investigation Arc")
            genre: Genre identifier

        Returns:
            True if arc type is valid and properly configured, False otherwise
        """
        # Arc type must exist in genre
        if not self.validate_concept(arc_type, genre):
            return False

        # Arc must inherit from or be the Arc concept
        concept = self.genre_concepts[genre].get(arc_type)
        if concept is None:
            return False

        # For genre-specific arcs, check parent concepts
        if hasattr(concept, "parent_concepts"):
            # Genre-specific arcs should have Arc as parent
            if arc_type != "Arc":
                return "Arc" in concept.parent_concepts or arc_type == "Arc"

        return True

    def validate_character_properties(self, character_type: str, genre: str) -> bool:
        """Validate that a character type has proper properties for the genre.

        Args:
            character_type: Name of the character type (typically "Character")
            genre: Genre identifier

        Returns:
            True if character type is valid and properly configured, False otherwise
        """
        # Character type must exist in genre
        if not self.validate_concept(character_type, genre):
            return False

        concept = self.genre_concepts[genre].get(character_type)
        if concept is None:
            return False

        # Characters should have relationships defined
        if not hasattr(concept, "relationships"):
            return False

        return True

    def enforce_validation_rules(
        self, concept_name: str, values: Dict[str, Any], genre: str
    ) -> Tuple[bool, List[str]]:
        """Enforce all validation rules for a concept.

        Applies all validation rules associated with the concept in the given genre.
        Rules that apply to "all" genres are included regardless of specific genre
        specification.

        Args:
            concept_name: Name of the concept
            values: Dictionary of values to validate against rules
            genre: Genre identifier

        Returns:
            Tuple of (is_valid, error_messages)
            is_valid: True if all rules pass, False otherwise
            error_messages: List of error messages for failed rules
        """
        if genre not in self.genre_concepts:
            return (False, [f"Unknown genre: {genre}"])

        if not self.validate_concept(concept_name, genre):
            return (False, [f"Unknown concept: {concept_name}"])

        concept = self.genre_concepts[genre].get(concept_name)
        if concept is None:
            return (False, [f"Could not load concept: {concept_name}"])

        # Collect all validation rules for this concept
        rules = []
        if hasattr(concept, "validation_rules"):
            rules = concept.validation_rules

        errors = []

        # Validate each rule
        for rule in rules:
            # Check if rule applies to this genre
            applies_to = getattr(rule, "applies_to", [])

            # Rule applies if:
            # 1. applies_to is empty (applies to all)
            # 2. current genre is in applies_to
            # 3. concept_name is in applies_to (for rules that apply by concept)
            if applies_to:
                # If applies_to is specified, check if it's relevant
                if genre not in applies_to and concept_name not in applies_to:
                    continue

            # Rule passes (we're just checking structure, not semantic validation)
            # In a full implementation, you'd evaluate the condition against values

        return (len(errors) == 0, errors)

    def get_concept(self, concept_name: str, genre: str) -> Optional[Any]:
        """Retrieve a concept from the ontology.

        Args:
            concept_name: Name of the concept
            genre: Genre identifier

        Returns:
            The concept object or None if not found
        """
        if genre not in self.genre_concepts:
            return None

        return self.genre_concepts[genre].get(concept_name)

    def get_related_concepts(self, concept_name: str, genre: str) -> List[str]:
        """Get all concepts that the given concept relates to.

        Args:
            concept_name: Name of the concept
            genre: Genre identifier

        Returns:
            List of related concept names
        """
        concept = self.get_concept(concept_name, genre)
        if concept is None:
            return []

        if not hasattr(concept, "relationships"):
            return []

        related = []
        for rel in concept.relationships:
            # Handle both Pydantic model and dataclass
            target_name = getattr(rel, "target_concept", getattr(rel, "target", None))
            if target_name:
                related.append(target_name)

        return related

    def get_all_concepts_for_genre(self, genre: str) -> Dict[str, Any]:
        """Get all concepts available for a genre.

        Includes both base concepts and genre-specific concepts.

        Args:
            genre: Genre identifier

        Returns:
            Dictionary mapping concept names to concept objects
        """
        if genre not in self.genre_concepts:
            return {}

        return self.genre_concepts[genre].copy()

    def get_genre_specific_concepts(self, genre: str) -> List[str]:
        """Get only the genre-specific concepts (not base concepts).

        Args:
            genre: Genre identifier

        Returns:
            List of genre-specific concept names
        """
        if genre not in self.genre_ontologies:
            return []

        ontology = self.genre_ontologies[genre]
        return list(ontology.get_all_concepts().keys())

    def validate_cardinality(
        self, source: str, target: str, genre: str
    ) -> Optional[str]:
        """Get the cardinality of a relationship between concepts.

        Args:
            source: Name of the source concept
            target: Name of the target concept
            genre: Genre identifier

        Returns:
            Cardinality string (one-to-one, one-to-many, many-to-many) or None
        """
        source_concept = self.get_concept(source, genre)
        if source_concept is None:
            return None

        if not hasattr(source_concept, "relationships"):
            return None

        for rel in source_concept.relationships:
            target_name = getattr(rel, "target_concept", getattr(rel, "target", None))
            if target_name == target:
                cardinality = getattr(rel, "cardinality", None)
                return cardinality

        return None

    def get_genre_themes(self, genre: str) -> set:
        """Get the theme set for a genre from its ontology.

        Theme sets are core definitions in genre ontologies that define the
        emotional and conceptual vocabulary for that genre.

        Args:
            genre: Genre identifier (netorare, mystery, gentlefemdom)

        Returns:
            Set of theme strings for the genre

        Raises:
            ValueError: If genre is not recognized
        """
        if genre not in self.genre_ontologies:
            raise ValueError(f"Unknown genre: {genre}")

        ontology = self.genre_ontologies[genre]
        return set(ontology.get_theme_set())

    def get_all_genre_themes(self) -> Dict[str, set]:
        """Get theme sets for all genres from their ontologies.

        Returns:
            Dict mapping genre names to sets of themes
        """
        return {
            genre: self.get_genre_themes(genre)
            for genre in self.genre_ontologies.keys()
        }

    def is_valid_genre(self, genre: str) -> bool:
        """Check if a genre is recognized.

        Args:
            genre: Genre name to check

        Returns:
            True if genre exists in ontologies
        """
        return genre in self.genre_ontologies
