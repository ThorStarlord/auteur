"""Authority-safe Narrative Ontology validation.

The validator preserves the historical public API while delegating semantic
lookup to the YAML-backed :class:`OntologyRegistry`. Only schema constraints and
deterministic semantic invariants execute here. Craft heuristics and
interpretive criteria remain advisory and are never treated as canonical proof.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from auteur.narrative_ontology.registry import OntologyRegistry
from auteur.narrative_ontology.schema.ontology_types import (
    Concept,
    ValidationRule,
    ValidationRuleKind,
)


RuleExecutor = Callable[[Dict[str, Any], Dict[str, Any]], List[str]]


def _required_fields(values: Dict[str, Any], parameters: Dict[str, Any]) -> List[str]:
    """Require named fields to be present and non-None."""

    fields = list(parameters.get("fields", []))
    missing = [field for field in fields if field not in values or values[field] is None]
    if not missing:
        return []
    return [f"Missing required field(s): {', '.join(missing)}"]


_DEFAULT_EXECUTORS: dict[str, RuleExecutor] = {
    "required_fields": _required_fields,
}


class _RegistryGenreView:
    """Small compatibility view replacing legacy hardcoded genre containers."""

    def __init__(self, registry: OntologyRegistry, genre: str) -> None:
        self.registry = registry
        self.genre = genre

    def get_all_concepts(self) -> Dict[str, Concept]:
        return self.registry.get_genre_extension(self.genre)

    def get_theme_set(self) -> List[str]:
        return sorted(self.registry.get_genre_themes(self.genre))

    def get_concept(self, concept_name: str) -> Concept:
        concept = self.registry.get_concept(concept_name, self.genre)
        if concept is None:
            raise KeyError(concept_name)
        return concept

    def validate_concept(self, concept_name: str) -> bool:
        return concept_name in self.get_all_concepts()


class OntologyValidator:
    """Validate ontology vocabulary without acquiring story authority."""

    def __init__(
        self,
        registry: Optional[OntologyRegistry] = None,
        *,
        rule_executors: Optional[Dict[str, RuleExecutor]] = None,
    ) -> None:
        self.registry = registry or OntologyRegistry()
        self.rule_executors = dict(_DEFAULT_EXECUTORS)
        if rule_executors:
            self.rule_executors.update(rule_executors)

        # Fail closed on shipped ontology specification errors. This validates
        # package metadata only; it does not inspect or mutate project state.
        self.registry.assert_valid()

        # Compatibility attributes retained for callers/tests that inspect the
        # validator directly. Definitions still originate in packaged YAML.
        base_raw = self.registry.loader.load_base_ontology()
        self.base_concepts: Dict[str, Concept] = {
            name: Concept.model_validate(value) for name, value in base_raw.items()
        }
        self.genre_ontologies = {
            genre: _RegistryGenreView(self.registry, genre)
            for genre in self.registry.available_genre_extensions
        }
        self.genre_concepts = {
            genre: self.registry.get_all_concepts(genre)
            for genre in self.registry.available_genre_extensions
        }

    def validate_concept(self, concept_name: str, genre: str) -> bool:
        if not self.is_valid_genre(genre):
            return False
        return self.registry.get_concept(concept_name, genre) is not None

    def validate_relationship(self, source: str, target: str, genre: str) -> bool:
        if not self.validate_concept(source, genre) or not self.validate_concept(target, genre):
            return False
        source_concept = self.registry.get_concept(source, genre)
        if source_concept is None:
            return False
        target_resolved = self.registry.resolve_name(target, genre) or target
        for relation in source_concept.relationships:
            relation_target = self.registry.resolve_name(relation.target_concept, genre) or relation.target_concept
            if relation_target == target_resolved:
                return True
        return False

    def validate_arc_properties(self, arc_type: str, genre: str) -> bool:
        concept = self.get_concept(arc_type, genre)
        if concept is None:
            return False
        if arc_type == "Arc" or concept.name == "Arc":
            return True
        return "Arc" in concept.parent_concepts

    def validate_character_properties(self, character_type: str, genre: str) -> bool:
        concept = self.get_concept(character_type, genre)
        return concept is not None and bool(concept.relationships)

    def _rule_applies(
        self, rule: ValidationRule, concept_name: str, genre: str
    ) -> bool:
        if not rule.applies_to:
            return True
        return genre in rule.applies_to or concept_name in rule.applies_to

    def enforce_validation_rules(
        self, concept_name: str, values: Dict[str, Any], genre: str
    ) -> Tuple[bool, List[str]]:
        """Execute deterministic rules only.

        Legacy free-text conditions, craft heuristics, and interpretive criteria
        are intentionally not executed. Unknown deterministic executors fail
        closed rather than silently passing.
        """

        if not self.is_valid_genre(genre):
            return False, [f"Unknown genre: {genre}"]
        concept = self.get_concept(concept_name, genre)
        if concept is None:
            return False, [f"Unknown concept: {concept_name}"]

        errors: List[str] = []
        executable_kinds = {
            ValidationRuleKind.SCHEMA_CONSTRAINT,
            ValidationRuleKind.SEMANTIC_INVARIANT,
        }
        for rule in concept.validation_rules:
            if not self._rule_applies(rule, concept_name, genre):
                continue
            if rule.kind not in executable_kinds:
                continue
            if not rule.executor:
                errors.append(
                    f"Rule '{rule.rule_id}' is executable but has no named executor"
                )
                continue
            executor = self.rule_executors.get(rule.executor)
            if executor is None:
                errors.append(
                    f"Rule '{rule.rule_id}' references unknown executor '{rule.executor}'"
                )
                continue
            failures = executor(values, rule.parameters)
            if failures:
                errors.append(rule.error_message)
                errors.extend(failures)

        return not errors, errors

    def get_concept(self, concept_name: str, genre: str) -> Optional[Concept]:
        if not self.is_valid_genre(genre):
            return None
        concept = self.registry.get_concept(concept_name, genre)
        if concept is None:
            return None

        # Preserve the historical OntologyValidator observation that base rules
        # explicitly list the three legacy genre extensions. The canonical V2
        # registry still stores an empty applies_to list to mean "global"; this
        # projection is limited to the legacy validator API and does not alter
        # registry semantics, rule execution, relationships, or persistence.
        legacy = self.base_concepts.get(concept.name)
        if legacy is not None:
            legacy_rules = {rule.rule_id: rule for rule in legacy.validation_rules}
            projected_rules = []
            changed = False
            for rule in concept.validation_rules:
                legacy_rule = legacy_rules.get(rule.rule_id)
                if (
                    not rule.applies_to
                    and legacy_rule is not None
                    and genre in legacy_rule.applies_to
                ):
                    projected_rules.append(
                        rule.model_copy(update={"applies_to": list(legacy_rule.applies_to)})
                    )
                    changed = True
                else:
                    projected_rules.append(rule)
            if changed:
                concept = concept.model_copy(update={"validation_rules": projected_rules})

        return concept

    def get_related_concepts(self, concept_name: str, genre: str) -> List[str]:
        concept = self.get_concept(concept_name, genre)
        if concept is None:
            return []
        return [relation.target_concept for relation in concept.relationships]

    def get_all_concepts_for_genre(self, genre: str) -> Dict[str, Concept]:
        if not self.is_valid_genre(genre):
            return {}
        return self.registry.get_all_concepts(genre).copy()

    def get_genre_specific_concepts(self, genre: str) -> List[str]:
        normalized = genre.strip().lower()
        if normalized not in self.registry.available_genre_extensions:
            return []
        return list(self.registry.get_genre_extension(normalized).keys())

    def validate_cardinality(self, source: str, target: str, genre: str) -> Optional[str]:
        source_concept = self.get_concept(source, genre)
        if source_concept is None:
            return None
        target_resolved = self.registry.resolve_name(target, genre) or target
        for relation in source_concept.relationships:
            relation_target = self.registry.resolve_name(relation.target_concept, genre) or relation.target_concept
            if relation_target == target_resolved:
                return relation.cardinality
        return None

    def get_genre_themes(self, genre: str) -> set[str]:
        normalized = genre.strip().lower()
        if normalized not in self.registry.available_genre_extensions:
            if self.is_valid_genre(normalized):
                return set()
            raise ValueError(f"Unknown genre: {genre}")
        return self.registry.get_genre_themes(normalized)

    def get_all_genre_themes(self) -> Dict[str, set[str]]:
        return {
            genre: self.registry.get_genre_themes(genre)
            for genre in self.registry.available_genre_extensions
        }

    def is_valid_genre(self, genre: str) -> bool:
        return self.registry.is_supported_genre(genre)
