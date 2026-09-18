"""Typed, authority-safe registry for Narrative Ontology V2.

The registry is the runtime projection of packaged ontology YAML. It owns no
project state and exposes no mutation/acceptance operations.
"""

from __future__ import annotations

from functools import cached_property
from typing import Any, Dict, Iterable, Optional

from pydantic import ValidationError

from auteur.narrative_ontology.loader.ontology_loader import OntologyLoader
from auteur.narrative_ontology.schema.ontology_types import Concept, RelationType


class OntologyIntegrityError(ValueError):
    """Raised when packaged ontology specifications violate deterministic integrity."""


class OntologyRegistry:
    """Read-only typed projection of the canonical packaged ontology specs."""

    def __init__(self, loader: Optional[OntologyLoader] = None) -> None:
        self.loader = loader or OntologyLoader()

    @cached_property
    def compatibility(self) -> Dict[str, Any]:
        return self.loader.load_compatibility()

    @cached_property
    def relation_types(self) -> Dict[str, RelationType]:
        raw = self.loader.load_relation_types()
        return {key: RelationType.model_validate(value) for key, value in raw.items()}

    @property
    def available_genre_extensions(self) -> tuple[str, ...]:
        return tuple(self.loader.available_genre_extensions())

    def is_supported_genre(self, genre: str) -> bool:
        """Return whether Auteur recognizes a genre.

        A recognized product genre does not need a Layer-0 extension; in that
        case it inherits the core ontology. Packaged extension ids are also
        recognized so custom extension work remains data-driven.
        """

        normalized = genre.strip().lower()
        if not normalized:
            return False
        if self.loader.has_genre_extension(normalized):
            return True
        try:
            from auteur.blueprint import Genre

            return normalized in {item.value for item in Genre}
        except (ImportError, AttributeError):
            return False

    def _genre_raw(self, genre: Optional[str]) -> Dict[str, Any]:
        if not genre:
            return {}
        normalized = genre.strip().lower()
        if not self.loader.has_genre_extension(normalized):
            return {}
        return self.loader.load_genre_ontology(normalized)

    def _compatibility_concepts(self, genre: Optional[str]) -> Dict[str, Any]:
        if not genre:
            return {}
        normalized = genre.strip().lower()
        return dict(
            self.compatibility.get("compatibility_concepts", {}).get(normalized, {})
        )

    def _aliases(self, genre: Optional[str]) -> Dict[str, str]:
        aliases: Dict[str, str] = {}
        if genre:
            normalized = genre.strip().lower()
            aliases.update(self.compatibility.get("aliases", {}).get(normalized, {}))
        for key, declaration in self._merged_raw(genre, include_compatibility=False).items():
            for alias in declaration.get("aliases", []):
                aliases.setdefault(alias, key)
        for key, declaration in self._compatibility_concepts(genre).items():
            for alias in declaration.get("aliases", []):
                aliases.setdefault(alias, key)
        return aliases

    def _merged_raw(
        self,
        genre: Optional[str] = None,
        *,
        include_compatibility: bool = True,
    ) -> Dict[str, Any]:
        merged = self.loader.load_core_ontology()
        merged = self.loader.merge_ontologies(merged, self._genre_raw(genre))
        if include_compatibility:
            merged = self.loader.merge_ontologies(
                merged, self._compatibility_concepts(genre)
            )
        return merged

    def resolve_name(self, name: str, genre: Optional[str] = None) -> Optional[str]:
        merged = self._merged_raw(genre)
        if name in merged:
            return name
        target = self._aliases(genre).get(name)
        return target if target in merged else None

    def get_concept(self, name: str, genre: Optional[str] = None) -> Optional[Concept]:
        resolved = self.resolve_name(name, genre)
        if resolved is None:
            return None
        declaration = self._merged_raw(genre)[resolved]
        concept = Concept.model_validate(declaration)
        if resolved != name:
            aliases = sorted(set(concept.aliases) | {resolved})
            concept = concept.model_copy(update={"name": name, "aliases": aliases})
        return concept

    def get_all_concepts(
        self,
        genre: Optional[str] = None,
        *,
        include_aliases: bool = True,
    ) -> Dict[str, Concept]:
        concepts = {
            key: Concept.model_validate(value)
            for key, value in self._merged_raw(genre).items()
        }
        if include_aliases:
            for alias, target in self._aliases(genre).items():
                if alias in concepts or target not in concepts:
                    continue
                target_concept = concepts[target]
                concepts[alias] = target_concept.model_copy(
                    update={
                        "name": alias,
                        "aliases": sorted(set(target_concept.aliases) | {target}),
                    }
                )
        return concepts

    def get_relation_type(self, relation_type_id: str) -> Optional[RelationType]:
        return self.relation_types.get(relation_type_id)

    def get_validation_rule(self, rule_id: str, genre: Optional[str] = None):
        for concept in self.get_all_concepts(genre, include_aliases=False).values():
            for rule in concept.validation_rules:
                if rule.rule_id == rule_id:
                    return rule
        return None

    def get_genre_extension(self, genre: str) -> Dict[str, Concept]:
        normalized = genre.strip().lower()
        raw = self._genre_raw(normalized)
        raw = self.loader.merge_ontologies(raw, self._compatibility_concepts(normalized))
        concepts = {key: Concept.model_validate(value) for key, value in raw.items()}
        for alias, target in self._aliases(normalized).items():
            if target in concepts and alias not in concepts:
                target_concept = concepts[target]
                concepts[alias] = target_concept.model_copy(
                    update={"name": alias, "aliases": sorted(set(target_concept.aliases) | {target})}
                )
        return concepts

    def get_genre_themes(self, genre: str) -> set[str]:
        return set(
            self.compatibility.get("genre_themes", {}).get(
                genre.strip().lower(), []
            )
        )

    def validate_integrity(self, genre: Optional[str] = None) -> list[str]:
        """Return deterministic specification integrity errors."""

        errors: list[str] = []
        base = self.loader.load_base_ontology()
        semantic = self.loader.load_semantic_vocabulary()
        extension = self._genre_raw(genre)
        compatibility = self._compatibility_concepts(genre)

        sources = [
            ("base", base),
            ("semantic", semantic),
            ("genre", extension),
            ("compatibility", compatibility),
        ]
        seen: dict[str, str] = {}
        for source_name, concepts in sources:
            for concept_name in concepts:
                previous = seen.get(concept_name)
                if previous is not None:
                    errors.append(
                        f"Duplicate concept id '{concept_name}' in {previous} and {source_name}"
                    )
                else:
                    seen[concept_name] = source_name

        merged = self._merged_raw(genre)
        known = set(merged)
        relation_type_ids = set(self.loader.load_relation_types())

        errors.extend(self.loader.validate_ontology_structure(merged))

        for concept_name, declaration in merged.items():
            try:
                concept = Concept.model_validate(declaration)
            except ValidationError as exc:
                errors.append(f"Concept '{concept_name}' fails typed schema: {exc}")
                continue
            for relation in concept.relationships:
                if relation.relation_type and relation.relation_type not in relation_type_ids:
                    errors.append(
                        f"Concept '{concept_name}' references undefined relation type "
                        f"'{relation.relation_type}'"
                    )
                if relation.source_concept not in known:
                    errors.append(
                        f"Concept '{concept_name}' has unresolved relation source "
                        f"'{relation.source_concept}'"
                    )
                if relation.target_concept not in known:
                    errors.append(
                        f"Concept '{concept_name}' has unresolved relation target "
                        f"'{relation.target_concept}'"
                    )
            for rule in concept.validation_rules:
                if rule.kind.value in {"schema_constraint", "semantic_invariant"} and not rule.executor:
                    errors.append(
                        f"Executable rule '{rule.rule_id}' on '{concept_name}' is missing an executor"
                    )

        for alias, target in self._aliases(genre).items():
            if target not in known:
                errors.append(f"Alias '{alias}' targets undefined concept '{target}'")

        for key, relation_type in self.loader.load_relation_types().items():
            try:
                parsed = RelationType.model_validate(relation_type)
            except ValidationError as exc:
                errors.append(f"Relation type '{key}' fails typed schema: {exc}")
                continue
            if parsed.id != key:
                errors.append(
                    f"Relation type key '{key}' does not match declared id '{parsed.id}'"
                )

        return errors

    def assert_valid(self, genres: Optional[Iterable[str]] = None) -> None:
        """Fail closed when canonical ontology specifications are inconsistent."""

        checks = [None]
        if genres is None:
            checks.extend(self.available_genre_extensions)
        else:
            checks.extend(genres)
        errors: list[str] = []
        for genre in checks:
            for error in self.validate_integrity(genre):
                prefix = "core" if genre is None else genre
                errors.append(f"[{prefix}] {error}")
        if errors:
            raise OntologyIntegrityError("Ontology integrity failure:\n- " + "\n- ".join(errors))
