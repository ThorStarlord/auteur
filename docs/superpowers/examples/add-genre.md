# How to Add a Genre Ontology Extension

> Current for Narrative Ontology V2. A product genre does not need a Layer-0 extension merely to be valid; genres without an extension inherit the core ontology.

## First decide whether an extension is warranted

Create a genre ontology extension only when the genre introduces **reusable semantic vocabulary** not adequately expressed by the core ontology.

Do not use Layer 0 to store pacing recommendations, expected emotional intensity, reader-response judgments, genre formulas, critic prompts, or workflow configuration. Those belong in Auteur's genre/craft/reasoning systems.

## 1. Ensure the product genre exists where appropriate

If the genre is intended as a first-class product genre, add it to the relevant product/medium genre registry (for example `auteur.blueprint.Genre`) according to that subsystem's contract. This is independent from ontology extension discovery.

## 2. Add one packaged ontology extension

Create:

```text
src/auteur/data/ontology/<genre>_ontology.yaml
```

Files ending in `_ontology.yaml` are discovered automatically by `OntologyLoader`; there is no parallel hardcoded ontology genre set.

Example:

```yaml
extends: base

concepts:
  UnreliableNarrator:
    name: UnreliableNarrator
    definition: A character whose presented perspective is materially incomplete, distorted, or untrustworthy.
    category: genre-specific
    parent_concepts: [Character]
    relationships:
      - source_concept: UnreliableNarrator
        target_concept: Information
        relation_type: affects
        cardinality: many-to-many
        description: The narrator affects access to or interpretation of information.
        required: false
    validation_rules:
      - rule_id: unreliable_narrator_effective_distortion
        kind: interpretive_criterion
        condition: The distortion should materially affect audience interpretation.
        error_message: The unreliable perspective may not affect interpretation.
        applies_to: [psychological_thriller]

metadata:
  version: "1.0"
  genre: psychological_thriller
  extends: base
```

All parent concepts and relationship targets must resolve against the core plus this extension.

## 3. Use relation vocabulary deliberately

When a relationship has reusable semantics, use a `relation_type` registered in `src/auteur/data/ontology/relation_types.yaml`. Add a new relation type only when the relation meaning is genuinely reusable.

`RelationType != StoryInstanceRelation`

A relation type never creates or accepts a story fact.

## 4. Classify rules

Choose the correct authority category: `schema_constraint`, `semantic_invariant`, `craft_heuristic`, or `interpretive_criterion`.

Only the first two execute in `OntologyValidator`, and every executable rule must name a deterministic executor with structured parameters. Free-text `condition` is documentation only. Genre expectations such as "must create suspense" or "must feel surprising" are interpretive criteria, not hard ontology failures.

## 5. Add compatibility aliases only when needed

If an existing public API used another display/name form, map it in `src/auteur/data/ontology/compatibility.yaml`. Do not create a second Python ontology class solely for the alias.

Legacy Python genre ontology classes remain compatibility surfaces for older callers/tests; new production lookup goes through `OntologyRegistry`.

## 6. Verify discovery and integrity

```python
from auteur.narrative_ontology import OntologyRegistry

registry = OntologyRegistry()
assert "psychological_thriller" in registry.available_genre_extensions
registry.assert_valid()

concept = registry.get_concept("UnreliableNarrator", "psychological_thriller")
assert concept is not None
```

If the genre is a valid product genre but has no extension, that is also valid:

```python
assert registry.get_concept("Character", "literary") is not None
```

## Qualification checklist

- [ ] The genre needs new semantic vocabulary rather than only craft guidance.
- [ ] The extension exists once under `src/auteur/data/ontology/`.
- [ ] No parallel ontology Python registry was edited.
- [ ] Parent concepts resolve.
- [ ] Relationship targets resolve.
- [ ] Relation-type ids resolve.
- [ ] Rule authority categories are explicit.
- [ ] Every executable rule uses a known named executor.
- [ ] Positive lookup tests pass.
- [ ] Invalid-reference/relation tests fail closed.
- [ ] Core-only genres remain valid without extensions.
- [ ] `OntologyRegistry.assert_valid()` passes.

**Last updated:** 2026-09-11
