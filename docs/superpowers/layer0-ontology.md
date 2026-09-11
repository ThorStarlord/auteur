# Layer 0: Narrative Ontology

> **Status:** compatibility overview. The canonical specification is `docs/architecture/narrative-ontology-v2.md`; the reconciliation rationale and ownership matrix live in `docs/architecture/narrative-ontology-reconciliation-v2.md`.

## What Layer 0 is

Layer 0 is Auteur's reusable narrative semantic foundation. It defines vocabulary, relation types, value vocabularies, and deterministic semantic invariants used by Identity, Structure, Realization, and Expression.

It answers questions such as:

- What does `Character` mean?
- What is the difference between a planned `StructuralBeat` and a realized `Event`?
- What relation type does `depends_on` describe?
- Which objective specification constraints can be checked deterministically?

It does **not** own an author's commitments, plans, accepted events, prose, workflow state, or derived recommendations.

## The five semantic layers

```text
                   Narrative Ontology
              vocabulary / types / invariants
                          |
                          v
Identity ------> Structure ------> Realization ------> Expression
commitments        plans             facts/state         language
```

Ontology supplies semantics to the other four layers. The arrow does not mean a project ontology artifact is transformed into Identity.

## Historical compatibility core

The original twelve names remain supported:

`Character`, `Arc`, `Theme`, `Goal`, `Conflict`, `Payoff`, `Symbol`, `Relationship`, `Beat`, `Setup`, `Revelation`, `Reversal`.

`src/auteur/narrative_ontology/core/narrative_concepts.py` preserves the old public constants for compatibility. It is no longer an independent source of definitions.

New code should normally use:

```python
from auteur.narrative_ontology import OntologyRegistry

registry = OntologyRegistry()
character = registry.get_concept("Character", "literary")
event = registry.get_concept("Event", "literary")
registry.assert_valid()
```

## Modern semantic vocabulary

V2 supplements the compatibility core with concepts needed by the current architecture, including:

- `Information`, `Misdirection`, `Checkpoint`;
- `StructuralBeat`, `NarrativeThread`, `SetupIntent`, `PayoffIntent`;
- `Event`, `Fact`, `State`, `StateTransition`;
- `CharacterRelationship`.

Important distinctions:

```text
StructuralBeat != Event != StateTransition
RelationType != StoryInstanceRelation
CharacterRelationship != derived relationship index
```

A planned beat does not prove an event happened. A relation type does not create a story assertion. A derived map cannot promote itself to canon.

## Validation categories

Narrative Ontology V2 distinguishes:

1. **SchemaConstraint** — objective shape/reference requirement.
2. **SemanticInvariant** — objective narrative-semantic rule with a named deterministic executor.
3. **CraftHeuristic** — advisory craft guidance.
4. **InterpretiveCriterion** — human/model judgment.

Only the first two execute as ontology validation. `condition` text in YAML is human-readable documentation and is never evaluated as code.

## Source of truth

Canonical ontology specifications are packaged under:

```text
src/auteur/data/ontology/
```

Key files include:

- `base_ontology.yaml` — historical twelve-concept compatibility core;
- `semantic_vocabulary.yaml` — modern cross-layer vocabulary;
- `relation_types.yaml` — reusable relation semantics;
- `compatibility.yaml` — historical aliases/theme metadata;
- `<genre>_ontology.yaml` — optional genre semantic extensions.

The runtime flow is:

```text
packaged YAML -> OntologyLoader -> typed OntologyRegistry -> OntologyValidator
```

Do not maintain a second hand-written Python ontology registry.

## Genre behavior

Genre extensions are discovered from packaged `*_ontology.yaml` resources. Product genres without an ontology extension inherit the core ontology; absence of an extension does not make the genre invalid.

Genre craft guidance should remain outside hard ontology validity unless it introduces genuine semantic vocabulary.

## Scope vocabulary

ADR 020 introduces medium-neutral semantic terms:

```text
Universe -> Series/Collection -> Entry -> Segment -> Scene
```

Existing persisted `Book`/`Chapter` contracts remain supported. `Entry` and `Segment` are semantic/generic vocabulary, not an automatic storage migration.

## Adding concepts

Follow `docs/superpowers/examples/add-concept.md`. The key rule is simple: edit the packaged ontology specification once, then let the typed registry project it into runtime objects.

## Historical note

Earlier versions of this document described free-text validation conditions as if they were executable and required changes to both YAML and Python when adding concepts. Those instructions are superseded by Narrative Ontology V2.

**Last updated:** 2026-09-11
