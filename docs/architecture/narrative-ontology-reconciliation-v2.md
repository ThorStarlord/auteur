# Narrative Ontology Reconciliation V2

Status: **Accepted implementation contract**

This document reconciles Auteur's historical Layer-0 ontology with the current narrative architecture. It does not introduce a fifth foundational architecture, a second canonical story store, or a new long-horizon experiment.

## Goal

Narrative Ontology defines reusable narrative concepts, relation types, value vocabularies, and deterministic semantic invariants. Identity, Structure, Realization, and Expression own story-instance artifacts that use that vocabulary.

Ontology is therefore a semantic foundation, not a story artifact that is progressively transformed into Identity.

## Preserved invariants

- The canonical semantic layers remain Ontology, Identity, Structure, Realization, Expression.
- Scope remains independent from semantic layer.
- Candidate, Derived, and Canonical authority remain independent from semantic layer and scope.
- Publication is not acceptance.
- Accepted history remains inspectable; revision order does not replace narrative order.
- Global Map, Focus, dependency indexes, and interpretive relations remain derived and rebuildable.
- Ontology lookup is read-only with respect to authorial and canonical state.

## Artifact coordinates

A narrative artifact is classified by four independent coordinates:

`semantic layer x scope x authority x revision/temporal position`

The four-coordinate model is an explanatory model of existing architecture, not a new foundational architecture.

## Ownership taxonomy

| Category | Owns | Examples |
| --- | --- | --- |
| ONTOLOGY_CONCEPT | reusable semantic meaning | Character, Theme, StructuralBeat, Event, StateTransition |
| ONTOLOGY_RELATION_TYPE | reusable relation vocabulary | depends_on, affects, fulfills, sets_up |
| ONTOLOGY_VALUE_VOCABULARY | bounded semantic values | relation origin, entry kind, segment kind |
| IDENTITY_ARTIFACT | authorial commitments | StoryIdentity, SeriesDirection, DirectionCommitment |
| STRUCTURE_ARTIFACT | plans and intended organization | blueprint, scene plan, structural beat instances |
| REALIZATION_ARTIFACT | accepted occurrences and state change | accepted fact, event, state transition |
| EXPRESSION_ARTIFACT | language realization | draft prose, dialogue, narration |
| PROVENANCE_METADATA | source and revision evidence | source ref, revision id, content hash |
| AUTHORITY_STATE | authority/currentness | candidate, derived, canonical, stale, superseded |
| DERIVED_REASONING_ARTIFACT | rebuildable projections | GlobalMapEntry, Focus, relation index |
| WORKFLOW_STATE | orchestration state | proposal/session/run state |
| IMPLEMENTATION_DETAIL | storage/runtime mechanics | file paths, cache keys, proposal ids |
| LEGACY_OR_DUPLICATE | compatibility-only representation | Python ontology object registries after registry migration |

## Reconciliation matrix

| Term | Current owner | Desired owner | Deterministic? | Authoritative? | Action |
| --- | --- | --- | --- | --- | --- |
| Character | Layer-0 base ontology | ONTOLOGY_CONCEPT | yes | vocabulary only | preserve |
| Arc | Layer-0 base ontology | ONTOLOGY_CONCEPT | yes | vocabulary only | preserve; remove universal craft claims |
| Theme | Layer-0 base ontology | ONTOLOGY_CONCEPT | yes | vocabulary only | preserve |
| Goal | Layer-0 base ontology | ONTOLOGY_CONCEPT | yes | vocabulary only | preserve |
| Conflict | Layer-0 base ontology | ONTOLOGY_CONCEPT | yes | vocabulary only | preserve; separate heuristics |
| Relationship | Layer-0 base ontology | legacy alias for CharacterRelationship | yes | vocabulary only | disambiguate |
| Beat | Layer-0 base ontology | legacy alias / broad concept; prefer StructuralBeat for plans | yes | vocabulary only | sharpen |
| Setup / Payoff | Layer-0 base ontology | ONTOLOGY_CONCEPT | yes | vocabulary only | preserve; many-to-many compatibility |
| Revelation / Reversal | Layer-0 base ontology | ONTOLOGY_CONCEPT | mixed | vocabulary only | move surprise/effectiveness to interpretive criteria |
| StructuralBeat | implicit Structure vocabulary | ONTOLOGY_CONCEPT | yes | vocabulary only | add |
| NarrativeThread | Structure | ONTOLOGY_CONCEPT | yes | vocabulary only | add |
| Event | Realization semantics | ONTOLOGY_CONCEPT | yes | vocabulary only | add |
| Fact | Series/realization semantics | ONTOLOGY_CONCEPT | yes | vocabulary only | add |
| State | realization semantics | ONTOLOGY_CONCEPT | yes | vocabulary only | add |
| StateTransition | Series runtime | ONTOLOGY_CONCEPT + REALIZATION_ARTIFACT instances | yes | instance may be canonical | add semantic definition; keep runtime ownership |
| StoryIdentity | identity.py | IDENTITY_ARTIFACT | yes | candidate/canonical by lifecycle | no ontology migration |
| DirectionCommitment | Series Direction | IDENTITY_ARTIFACT | yes | candidate/canonical by lifecycle | no ontology migration |
| GlobalMapEntry | Series map | DERIVED_REASONING_ARTIFACT | yes | derived only | keep out of Layer 0 |
| CausalSupportRelation | Series map | story-instance relation | origin-dependent | never promoted by index | keep out of Layer 0 |
| PressureGroupRelation | Series map | story-instance relation | origin-dependent | never promoted by index | keep out of Layer 0 |
| proposal/session identifiers | workflows | IMPLEMENTATION_DETAIL | yes | no | keep out of Layer 0 |

## Three relationship domains

1. **RelationType** — Layer-0 vocabulary describing the meaning of a possible relation.
2. **CharacterRelationship / CharacterRelationshipState** — story concepts and realized relationship state.
3. **StoryInstanceRelation** — a concrete declared, deterministic, or interpretive assertion between story facts/artifacts.

`Relation type != relation assertion`.

A derived relation index cannot promote a story-instance assertion to canon. Confidence may rank an interpretive assertion but cannot change its authority.

## Validation taxonomy

Validation is split into four classes:

- **SchemaConstraint** — deterministic shape/reference constraint; hard failure.
- **SemanticInvariant** — deterministic narrative-semantic invariant backed by a named executor; hard failure when violated.
- **CraftHeuristic** — advisory craft signal; never ontological invalidity.
- **InterpretiveCriterion** — requires human/model judgment; routed to diagnostics/reasoning, never silently enforced as canon.

Free-text conditions are retained only as documentation/compatibility. They are never evaluated as code.

## Source-of-truth policy

`src/auteur/data/ontology/` is the canonical ontology specification source. Runtime objects are parsed from packaged YAML through a typed `OntologyRegistry`. Historical Python concept modules may remain only as compatibility facades while callers migrate.

Adding a concept or genre extension must not require editing a parallel Python registry.

## Genre policy

The ontology separates:

`Core Ontology + Genre Vocabulary Extension + Genre Craft Pack`

Only semantic concepts/relations belong in an ontology extension. Recommendations about pacing, surprise, emotional effectiveness, escalation, or reader response are craft/interpretive knowledge.

A genre with no ontology extension uses the core ontology rather than being rejected merely because no YAML extension exists.

## Scope direction

The existing serialized/runtime scopes remain unchanged in this reconciliation. The medium-neutral semantic direction is:

`Universe -> Series/Collection -> Entry -> Segment -> Scene`

Presentation aliases include:

- Entry: Book, Episode, Film, Story, Route, Mission
- Segment: Chapter, Act, Sequence, Section, Mission

Book/Chapter remain compatibility terms. This change does not mass-migrate Series storage or introduce Episode realization.

## Closed Episode branch

PR #167 was closed without merge. Its bounded Episode-1 implementation is therefore not part of current-main authority and is not used as a migration base here.

## Completion criteria

- one documented Layer-0 ownership contract;
- one packaged ontology specification source feeding the runtime registry;
- no hardcoded three-genre gate in the typed schema/validator;
- relation types separated from story-instance assertions;
- structural and realization primitives have explicit meanings;
- deterministic validation is executor-backed, while craft/interpretive rules remain advisory;
- ontology integrity rejects duplicate ids and dangling parents/relationship targets;
- ontology APIs cannot accept or mutate canonical narrative state;
- legacy public APIs remain compatible while duplicate semantic definitions are retired.