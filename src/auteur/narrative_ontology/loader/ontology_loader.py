"""Package-resource loader for Narrative Ontology specifications.

`src/auteur/data/ontology/` is the canonical specification source. The loader
preserves its historical dictionary API as an explicit compatibility projection
while exposing raw V2 specification methods consumed by :class:`OntologyRegistry`.
"""

from __future__ import annotations

from copy import deepcopy
import importlib.resources
from threading import RLock
from typing import Any, Dict, List, Optional

import yaml


_ONTOLOGY_PACKAGE = "auteur.data.ontology"
_LEGACY_GENRES = ["netorare", "mystery", "gentlefemdom"]


def _resource_root():
    try:
        return importlib.resources.files(_ONTOLOGY_PACKAGE)
    except (ModuleNotFoundError, TypeError) as exc:
        raise FileNotFoundError(
            f"Ontology package '{_ONTOLOGY_PACKAGE}' is unavailable: {exc}"
        ) from exc


def _read_ontology_yaml(filename: str) -> dict[str, Any]:
    """Read one UTF-8 YAML document from packaged ontology resources."""

    try:
        ref = _resource_root().joinpath(filename)
        with ref.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Ontology resource '{filename}' not found in package '{_ONTOLOGY_PACKAGE}'"
        ) from exc


class OntologyLoader:
    """Load, merge, cache, and structurally inspect ontology documents."""

    _cache_lock = RLock()

    def __init__(self) -> None:
        self._document_cache: Dict[str, Dict[str, Any]] = {}
        self._merged_cache: Dict[str, Dict[str, Any]] = {}

    def load_document(self, filename: str) -> Dict[str, Any]:
        """Load an arbitrary packaged ontology YAML document with caching."""

        with self._cache_lock:
            cached = self._document_cache.get(filename)
            if cached is not None:
                return cached
        data = _read_ontology_yaml(filename)
        with self._cache_lock:
            self._document_cache[filename] = data
        return data

    def resource_names(self) -> List[str]:
        """Return packaged ontology YAML filenames."""

        return sorted(
            item.name
            for item in _resource_root().iterdir()
            if item.name.endswith(".yaml")
        )

    def available_genre_extensions(self) -> List[str]:
        """Discover genre extensions from packaged `*_ontology.yaml` files."""

        suffix = "_ontology.yaml"
        return sorted(
            name[: -len(suffix)]
            for name in self.resource_names()
            if name.endswith(suffix) and name != "base_ontology.yaml"
        )

    def has_genre_extension(self, genre: str) -> bool:
        return genre.strip().lower() in set(self.available_genre_extensions())

    def load_base_document(self) -> Dict[str, Any]:
        return self.load_document("base_ontology.yaml")

    def load_base_spec(self) -> Dict[str, Any]:
        """Return the canonical raw historical-core specification.

        New V2 runtime code should use this method (usually indirectly through
        :class:`OntologyRegistry`) when exact canonical YAML semantics matter.
        """

        return self.load_base_document().get("concepts", {})

    def _legacy_base_projection(self) -> Dict[str, Any]:
        """Project raw base YAML into the pre-V2 loader observation contract."""

        projected = deepcopy(self.load_base_spec())
        for concept in projected.values():
            for rule in concept.get("validation_rules", []):
                if not rule.get("applies_to"):
                    rule["applies_to"] = list(_LEGACY_GENRES)
        setup = projected.get("Setup", {})
        for relation in setup.get("relationships", []):
            if relation.get("target_concept") == "Payoff":
                relation["cardinality"] = "one-to-one"
        return projected

    def load_base_ontology(self) -> Dict[str, Any]:
        """Return the historical 12-concept loader compatibility projection.

        This public method intentionally preserves pre-V2 observations such as
        explicit applicability to the three historical genre extensions and
        Setup->Payoff's former one-to-one cardinality. Canonical V2 semantics
        live in :meth:`load_base_spec` / :meth:`load_core_ontology`.
        """

        cache_key = "legacy-base"
        with self._cache_lock:
            cached = self._merged_cache.get(cache_key)
            if cached is not None:
                return cached
        projected = self._legacy_base_projection()
        with self._cache_lock:
            self._merged_cache[cache_key] = projected
        return projected

    def load_semantic_vocabulary(self) -> Dict[str, Any]:
        return self.load_document("semantic_vocabulary.yaml").get("concepts", {})

    def load_core_ontology(self) -> Dict[str, Any]:
        """Return canonical raw base semantics plus V2 semantic vocabulary."""

        return self.merge_ontologies(
            self.load_base_spec(), self.load_semantic_vocabulary()
        )

    def load_relation_types(self) -> Dict[str, Any]:
        return self.load_document("relation_types.yaml").get("relation_types", {})

    def load_compatibility(self) -> Dict[str, Any]:
        return self.load_document("compatibility.yaml")

    def load_genre_document(self, genre: str) -> Dict[str, Any]:
        genre = genre.strip().lower()
        filename = f"{genre}_ontology.yaml"
        if not self.has_genre_extension(genre):
            raise FileNotFoundError(f"Genre ontology file not found for '{genre}': {filename}")
        return self.load_document(filename)

    def load_genre_ontology(self, genre: str) -> Dict[str, Any]:
        """Return concept declarations for a packaged genre extension."""

        return self.load_genre_document(genre).get("concepts", {})

    def merge_ontologies(self, base: Dict, genre: Dict) -> Dict[str, Any]:
        merged = dict(base)
        merged.update(genre)
        return merged

    def get_concept(self, name: str, genre: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve a concept through the historical dictionary compatibility API.

        V2 runtime lookup should use ``OntologyRegistry.get_concept``. This API
        remains case-sensitive and preserves historical base-field observations.
        """

        merged = self.merge_ontologies(
            self.load_base_ontology(), self.load_semantic_vocabulary()
        )
        if genre:
            genre_key = genre.strip().lower()
            cache_key = f"legacy-core+{genre_key}"
            with self._cache_lock:
                cached = self._merged_cache.get(cache_key)
            if cached is None:
                genre_data = self.load_genre_ontology(genre_key)
                cached = self.merge_ontologies(merged, genre_data)
                with self._cache_lock:
                    self._merged_cache[cache_key] = cached
            merged = cached
        return merged.get(name, {})

    def validate_ontology_structure(
        self,
        ontology: Dict[str, Any],
        *,
        known_concepts: Optional[set[str]] = None,
    ) -> List[str]:
        """Validate objective structure/reference integrity.

        `known_concepts` may include parent/core concepts when checking an
        extension in isolation. Craft quality is intentionally not evaluated.
        """

        errors: List[str] = []
        concept_names = set(ontology) | set(known_concepts or set())

        for key, concept in ontology.items():
            if not isinstance(concept, dict):
                errors.append(f"Concept '{key}' must be a mapping")
                continue
            if "name" not in concept:
                errors.append(f"Concept '{key}' missing 'name' field")
            elif concept["name"] != key:
                errors.append(
                    f"Concept key '{key}' does not match declared name '{concept['name']}'"
                )
            if "definition" not in concept:
                errors.append(f"Concept '{key}' missing 'definition' field")

            for parent in concept.get("parent_concepts", []):
                if parent not in concept_names:
                    errors.append(
                        f"Concept '{key}' has undefined parent concept '{parent}'"
                    )

            relationships = concept.get("relationships", [])
            if not isinstance(relationships, list):
                errors.append(f"Concept '{key}' relationships must be a list")
                relationships = []
            for relation in relationships:
                if not isinstance(relation, dict):
                    errors.append(f"Concept '{key}' contains a non-mapping relationship")
                    continue
                source = relation.get("source_concept")
                target = relation.get("target_concept")
                if source and source not in concept_names:
                    errors.append(
                        f"Concept '{key}' has relationship from undefined concept '{source}'"
                    )
                if target and target not in concept_names:
                    errors.append(
                        f"Concept '{key}' has relationship to undefined concept '{target}'"
                    )

            rules = concept.get("validation_rules")
            if rules is None:
                errors.append(f"Concept '{key}' missing 'validation_rules' field")
            elif not isinstance(rules, list):
                errors.append(f"Concept '{key}' validation_rules must be a list")

        return errors

    def clear_cache(self) -> None:
        with self._cache_lock:
            self._document_cache.clear()
            self._merged_cache.clear()

    def get_concept_names(self, genre: Optional[str] = None) -> List[str]:
        merged = self.load_core_ontology()
        if genre:
            merged = self.merge_ontologies(merged, self.load_genre_ontology(genre))
        return sorted(merged)

    def get_genre_extensions(self, genre: str) -> List[str]:
        base_names = set(self.load_core_ontology())
        genre_names = set(self.load_genre_ontology(genre))
        return sorted(genre_names - base_names)
