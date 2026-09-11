# Narrative Ontology V2

Status: **Canonical Layer-0 semantic specification**

See also `docs/narrative-architecture.md`, `docs/architecture-constitution.md`, ADR 019, ADR 020, and `docs/architecture/narrative-ontology-reconciliation-v2.md`.

## Purpose

Narrative Ontology is Auteur's shared semantic vocabulary. It defines what reusable narrative concepts and relation types mean and which invariants can be checked deterministically.

Ontology does not contain a project's accepted story facts, authorial commitments, prose, workflow state, recommendations, or derived map entries.

## Layer relationship

```
                   NARRATIVE SEMANTIC FOUNDATION
                           Ontology
                              |
              vocabulary / relation types / invariants
                              v

Identity ------> Structure ------> Realization ------> Expression
commitments        plans             facts/state         language
```

The arrow from Ontology means "supplies semantic vocabulary". It does not mean an ontology artifact is transformed into a story artifact.

## Independent artifact coordinates

Every narrative artifact can be reasoned about through independent coordinates:

1. semantic layer;
2. scope;
3. authority;
4. revision / temporal position.

No coordinate silently implies another. In particular, a Realization artifact is not canonical merely because it is a Realization artifact, and a derived Series map is not authoritative merely because it was computed deterministically.

## Core semantic families

### Story concepts

The historical base concepts remain supported: Character, Arc, Theme, Goal, Conflict, Payoff, Symbol, Relationship, Beat, Setup, Revelation, Reversal.

`Relationship` and `Beat` are compatibility-era broad terms. New architecture should prefer the sharper meanings below when precision matters.

### Structure vocabulary

- **StructuralBeat** — an intended structural moment/function in a plan. It is not proof that an occurrence happened.
- **NarrativeThread** — a planned continuity of narrative concern across structural units.
- **SetupIntent** — a structural intention to establish material for later use.
- **PayoffIntent** — a structural intention to deliver or resolve prior setup.

### Realization vocabulary

- **Event** — an occurrence represented as having happened in the story world or narrative presentation.
- **Fact** — an accepted proposition about narrative state/history.
- **State** — a snapshot/value of a narrative entity or relationship at a narrative position.
- **StateTransition** — an accepted change from one state to another.

A `StructuralBeat` can be realized by zero or more Events. An Event can produce zero or more StateTransitions. Plans do not silently become facts.

### Relationship vocabulary

- **RelationType** — reusable semantics for a possible relation.
- **CharacterRelationship** — a relationship between characters/entities as a story concept.
- **CharacterRelationshipState** — realized state of such a relationship.
- **StoryInstanceRelation** — a concrete relation assertion between accepted facts/artifacts.

Recommended relation type ids include `pursues`, `participates_in`, `explores`, `sets_up`, `pays_off`, `depends_on`, `affects`, `fulfills`, `supersedes`, `governed_by`, `incompatible_with`, `may_be_realized_as`, and `may_produce`.

Story-instance relations retain origin semantics such as declared, deterministic derivation, and interpretive. Origin/authority are properties of the assertion, not the relation type.

## Validation semantics

### SchemaConstraint

Checks data shape, identifiers, references, cardinality representation, and other objective schema rules.

### SemanticInvariant

Checks deterministic narrative semantics through a named executor. Executors are registered code; YAML never contains executable expressions.

### CraftHeuristic

Represents useful but non-universal craft guidance. It may produce diagnostics but cannot make ontology loading or canonical acceptance fail by itself.

### InterpretiveCriterion

Represents judgments such as whether a reversal is surprising or a conflict creates effective tension. It belongs in advisory reasoning/criticism, not hard ontology validation.

## Source of truth

Packaged specifications under `src/auteur/data/ontology/` are canonical. `OntologyRegistry` parses and validates these resources into typed runtime models.

Compatibility modules may expose historical class/function APIs but must derive semantic definitions from the registry or be explicitly marked legacy. They are not an independent source of ontology truth.

## Genre extensions

A genre extension may introduce concepts or relation vocabulary that genuinely changes the semantic vocabulary. A genre craft pack contains expectations/advice and remains outside hard ontology validity.

Genres without an extension inherit the core ontology. Missing optional extension data is not equivalent to an invalid genre.

## Authority invariants

Ontology code must not:

- accept StoryIdentity, Structure, or Realization proposals;
- mutate canonical project state;
- turn a derived or interpretive assertion into canon;
- write Global Map or Focus as canonical state;
- infer authorial acceptance from publication or model confidence.

## Compatibility

Historical terms remain available while migration is incremental:

- `Beat` remains valid; prefer `StructuralBeat` for planned structural semantics.
- `Relationship` remains valid; prefer `CharacterRelationship` when the domain is specifically character/entity relationships.
- Book/Chapter serialized scopes remain valid while medium-neutral Entry/Segment vocabulary is introduced at semantic boundaries.

Compatibility aliases must be visible and non-destructive; they may not silently change stored authority or provenance.