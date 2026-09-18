"""Negative/rejection qualification for ontology specification integrity."""

from __future__ import annotations

from copy import deepcopy

from auteur.narrative_ontology.loader import OntologyLoader
from auteur.narrative_ontology.registry import OntologyRegistry


class _InjectedLoader(OntologyLoader):
    def __init__(
        self,
        *,
        base=None,
        semantic=None,
        relations=None,
        genres=None,
        compatibility=None,
    ) -> None:
        super().__init__()
        real = OntologyLoader()
        self._base = deepcopy(base if base is not None else real.load_base_ontology())
        self._semantic = deepcopy(
            semantic if semantic is not None else real.load_semantic_vocabulary()
        )
        self._relations = deepcopy(
            relations if relations is not None else real.load_relation_types()
        )
        self._genres = deepcopy(genres if genres is not None else {})
        self._compatibility = deepcopy(
            compatibility if compatibility is not None else {"aliases": {}, "genre_themes": {}}
        )

    def load_base_ontology(self):
        return self._base

    def load_semantic_vocabulary(self):
        return self._semantic

    def load_core_ontology(self):
        return self.merge_ontologies(self._base, self._semantic)

    def load_relation_types(self):
        return self._relations

    def load_compatibility(self):
        return self._compatibility

    def available_genre_extensions(self):
        return sorted(self._genres)

    def has_genre_extension(self, genre: str) -> bool:
        return genre in self._genres

    def load_genre_ontology(self, genre: str):
        return self._genres[genre]


def test_loader_rejects_undefined_parent_reference() -> None:
    loader = OntologyLoader()
    ontology = {
        "Child": {
            "name": "Child",
            "definition": "test",
            "parent_concepts": ["MissingParent"],
            "relationships": [],
            "validation_rules": [],
        }
    }
    errors = loader.validate_ontology_structure(ontology)
    assert any("undefined parent concept" in error for error in errors)


def test_loader_rejects_undefined_relationship_target() -> None:
    loader = OntologyLoader()
    ontology = {
        "Source": {
            "name": "Source",
            "definition": "test",
            "parent_concepts": [],
            "relationships": [
                {
                    "source_concept": "Source",
                    "target_concept": "MissingTarget",
                    "cardinality": "one-to-one",
                    "description": "broken",
                }
            ],
            "validation_rules": [],
        }
    }
    errors = loader.validate_ontology_structure(ontology)
    assert any("undefined concept 'MissingTarget'" in error for error in errors)


def test_registry_rejects_duplicate_concept_ids_across_sources() -> None:
    real = OntologyLoader()
    duplicate = {
        "Character": {
            "name": "Character",
            "definition": "duplicate",
            "parent_concepts": [],
            "relationships": [],
            "validation_rules": [],
        }
    }
    registry = OntologyRegistry(
        _InjectedLoader(
            base=real.load_base_ontology(),
            semantic=duplicate,
            relations=real.load_relation_types(),
        )
    )
    errors = registry.validate_integrity()
    assert any("Duplicate concept id 'Character'" in error for error in errors)


def test_registry_rejects_undefined_relation_type_id() -> None:
    real = OntologyLoader()
    semantic = deepcopy(real.load_semantic_vocabulary())
    semantic["Event"]["relationships"][0]["relation_type"] = "does_not_exist"
    registry = OntologyRegistry(
        _InjectedLoader(
            base=real.load_base_ontology(),
            semantic=semantic,
            relations=real.load_relation_types(),
        )
    )
    errors = registry.validate_integrity()
    assert any("undefined relation type 'does_not_exist'" in error for error in errors)


def test_registry_rejects_executable_rule_without_executor() -> None:
    real = OntologyLoader()
    semantic = deepcopy(real.load_semantic_vocabulary())
    semantic["StateTransition"]["validation_rules"][0].pop("executor")
    registry = OntologyRegistry(
        _InjectedLoader(
            base=real.load_base_ontology(),
            semantic=semantic,
            relations=real.load_relation_types(),
        )
    )
    errors = registry.validate_integrity()
    assert any("missing an executor" in error for error in errors)
