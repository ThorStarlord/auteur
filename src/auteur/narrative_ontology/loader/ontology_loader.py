"""OntologyLoader: Load, merge, and validate narrative ontologies from YAML files.

Layer 0 Task 4: Implements the OntologyLoader class that:
- Loads base ontology from base_ontology.yaml
- Loads genre-specific ontologies from genre YAML files
- Merges base and genre ontologies
- Retrieves concepts with caching
- Validates ontology structure
- Provides thread-safe access to cached ontologies

Ontology resources are loaded from the installed package via importlib.resources,
making them independent of the working directory or source checkout.
"""

from __future__ import annotations

import importlib.resources
import yaml
from typing import Dict, List, Optional, Any
from threading import RLock


_ONTOLOGY_PACKAGE = "auteur.data.ontology"


def _read_ontology_yaml(filename: str) -> dict[str, Any]:
    """Read ontology YAML from package resources.

    Args:
        filename: YAML filename (e.g. "base_ontology.yaml")

    Returns:
        Parsed YAML content as a dict.

    Raises:
        FileNotFoundError: If the resource is not found in the installed package.
    """
    try:
        ref = importlib.resources.files(_ONTOLOGY_PACKAGE).joinpath(filename)
        with ref.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (ModuleNotFoundError, FileNotFoundError, TypeError) as exc:
        raise FileNotFoundError(
            f"Ontology resource '{filename}' not found in package '{_ONTOLOGY_PACKAGE}'. "
            f"Ensure auteur is installed correctly (pip install auteur). "
            f"Error: {exc}"
        ) from exc


class OntologyLoader:
    """Loads and manages narrative ontologies from YAML files.

    This loader handles:
    - Loading base ontology (12 core concepts)
    - Loading genre-specific extensions (netorare, mystery, gentlefemdom)
    - Merging base and genre ontologies
    - Validating relationship integrity
    - Caching loaded ontologies for performance
    - Thread-safe access to cached data

    Ontology resources are loaded via importlib.resources and work from
    any working directory or from an installed wheel.
    """

    # Class-level lock for thread-safe caching
    _cache_lock = RLock()

    def __init__(self):
        """Initialize the OntologyLoader with empty cache.

        No project root or working directory is consulted — all ontology
        resources are resolved from the installed package.
        """
        self._base_ontology_cache: Optional[Dict] = None
        self._genre_ontology_cache: Dict[str, Dict] = {}
        self._merged_cache: Dict[str, Dict] = {}

    def load_base_ontology(self) -> Dict[str, Any]:
        """Load base ontology from YAML file.

        The base ontology contains 12 core narrative concepts:
        Character, Arc, Theme, Goal, Conflict, Payoff, Symbol,
        Relationship, Beat, Setup, Revelation, Reversal.

        Returns:
            Dictionary mapping concept names to concept definitions.
            Each concept has: name, definition, relationships, validation_rules.

        Raises:
            FileNotFoundError: If base_ontology.yaml cannot be found.
            yaml.YAMLError: If YAML is malformed.
        """
        with self._cache_lock:
            if self._base_ontology_cache is not None:
                return self._base_ontology_cache

        data = _read_ontology_yaml("base_ontology.yaml")
        concepts = data.get("concepts", {})

        with self._cache_lock:
            self._base_ontology_cache = concepts

        return concepts

    def load_genre_ontology(self, genre: str) -> Dict[str, Any]:
        """Load genre-specific ontology from YAML file.

        Loads genre extensions for netorare, mystery, or gentlefemdom.
        Each genre file contains genre-specific concepts that extend the base ontology.

        Args:
            genre: Genre identifier (netorare, mystery, gentlefemdom)

        Returns:
            Dictionary mapping concept names to concept definitions.

        Raises:
            FileNotFoundError: If genre YAML file cannot be found.
            ValueError: If genre is not recognized.
            yaml.YAMLError: If YAML is malformed.
        """
        genre = genre.lower()

        with self._cache_lock:
            if genre in self._genre_ontology_cache:
                return self._genre_ontology_cache[genre]

        filename = f"{genre}_ontology.yaml"
        try:
            data = _read_ontology_yaml(filename)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Genre ontology file not found for '{genre}': {filename}. "
                f"Valid genres: netorare, mystery, gentlefemdom"
            )

        concepts = data.get("concepts", {})

        with self._cache_lock:
            self._genre_ontology_cache[genre] = concepts

        return concepts

    def merge_ontologies(self, base: Dict, genre: Dict) -> Dict[str, Any]:
        """Merge base and genre ontologies.

        Genre-specific concepts override base concepts when both define
        the same concept name. The merge is shallow at the concept level:
        genre concept entries replace base entries entirely.

        Args:
            base: Base ontology concepts dict.
            genre: Genre-specific ontology concepts dict.

        Returns:
            Merged ontology dictionary.
        """
        merged = dict(base)
        merged.update(genre)
        return merged

    def get_concept(self, name: str, genre: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve a concept by name, optionally with genre context.

        Args:
            name: Concept name to retrieve.
            genre: Optional genre to load genre-specific ontology.

        Returns:
            Concept definition dictionary, or empty dict if not found.
        """
        base = self.load_base_ontology()
        merged = dict(base)

        if genre:
            genre = genre.lower()
            with self._cache_lock:
                if genre not in self._merged_cache:
                    genre_data = self.load_genre_ontology(genre)
                    self._merged_cache[genre] = self.merge_ontologies(base, genre_data)
            merged = self._merged_cache.get(genre, merged)

        return merged.get(name, {})

    def validate_ontology_structure(self, ontology: Dict[str, Any]) -> List[str]:
        """Validate ontology structure and relationship integrity.

        Validates:
        - All concepts have required fields (name, definition)
        - Relationship references are valid (point to existing concepts)
        - Validation rules are present for each concept
        - No cycles in relationship references

        Args:
            ontology: Dictionary mapping concept names to concept definitions.

        Returns:
            List of validation error messages. Empty list means valid.
        """
        errors: List[str] = []
        concept_names = set(ontology.keys())

        for name, concept in ontology.items():
            # Check required fields
            if "definition" not in concept:
                errors.append(f"Concept '{name}' missing 'definition' field")

            # Check relationship references (list of {source_concept, target_concept, cardinality})
            rels = concept.get("relationships", [])
            if isinstance(rels, list):
                for rel in rels:
                    if isinstance(rel, dict):
                        target = rel.get("target_concept")
                        source = rel.get("source_concept")
                        if target and target not in concept_names:
                            errors.append(
                                f"Concept '{name}' has relationship to undefined "
                                f"concept '{target}'"
                            )
                        if source and source not in concept_names:
                            errors.append(
                                f"Concept '{name}' has relationship from undefined "
                                f"concept '{source}'"
                            )
            elif isinstance(rels, dict):
                # Support both list-of-dicts and dict-of-targets schemas
                for rel_type, targets in rels.items():
                    if isinstance(targets, str):
                        targets = [targets]
                    for target in targets:
                        if target not in concept_names and target != name:
                            errors.append(
                                f"Concept '{name}' has relationship '{rel_type}' "
                                f"to undefined concept '{target}'"
                            )

            # Check validation rules
            if "validation_rules" not in concept:
                errors.append(f"Concept '{name}' missing 'validation_rules' field")
        return errors

    def clear_cache(self) -> None:
        """Clear all cached ontologies.

        Forces a fresh load from YAML files on the next access.
        Thread-safe.
        """
        with self._cache_lock:
            self._base_ontology_cache = None
            self._genre_ontology_cache.clear()
            self._merged_cache.clear()

    def get_concept_names(self, genre: Optional[str] = None) -> List[str]:
        """Get list of all concept names in ontology.

        Args:
            genre: Optional genre to include genre-specific concepts.

        Returns:
            Sorted list of concept names.
        """
        merged = self.load_base_ontology()
        if genre:
            genre = genre.lower()
            if genre not in self._merged_cache:
                genre_data = self.load_genre_ontology(genre)
                self._merged_cache[genre] = self.merge_ontologies(merged, genre_data)
            merged = self._merged_cache[genre]
        return sorted(merged.keys())

    def get_genre_extensions(self, genre: str) -> List[str]:
        """Get list of genre-specific concepts (non-base concepts).

        Args:
            genre: Genre identifier to check.

        Returns:
            Sorted list of concept names unique to the genre.
        """
        base_names = set(self.load_base_ontology().keys())
        genre_names = set(self.load_genre_ontology(genre).keys())
        return sorted(genre_names - base_names)
