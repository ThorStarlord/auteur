# Auteur Narrative Architecture

This is the canonical architecture specification for Auteur. It supersedes
active documentation that presents scopes, genre phases, or workflow concerns
as semantic layers. Historical ADRs and archived plans retain their original
terminology as historical context.

## Semantic layers

| Layer | Core question | Knowledge type | Owns | Does not own |
|---|---|---|---|---|
| 0. Ontology | What reusable narrative concepts and relations exist? | Semantic vocabulary | Concepts, relation types, value vocabularies, deterministic semantic invariants | Authorial commitments, story-instance plans/facts, prose, workflow state |
| 1. Identity | What commitments define this narrative? | Commitments | Genre, subgenre, medium, scope, scale, target experience, emotional core, theme, core engine | Detailed sequencing, realized events, wording |
| 2. Structure | How is the narrative planned and organized? | Plans | Threads, arcs, structural beats, entry/segment plans, setup/payoff intentions, thematic progression | Realized events, moment-to-moment states, prose |
| 3. Realization | What concrete events and state changes occur? | Events and state changes | Scenes, event order, accepted facts, knowledge, location, inventory, relationship and character deltas | Sentence-level language and style |
| 4. Expression | How are those events rendered as language and prose? | Language | Voice, diction, POV, dialogue, imagery, pacing, sentence form, prose revision | Canonical plot commitments and event facts |

These layers describe kinds of knowledge. They are not a requirement that every
project produce one artifact for every layer.

### Ontology is a semantic substrate

Layer 0 supplies shared vocabulary to Identity, Structure, Realization, and
Expression. It should not be interpreted as a project artifact that is
transformed into Identity and then discarded. A `RelationType`, for example,
defines reusable semantics; it is not itself a story-instance relation.

```text
                   NARRATIVE SEMANTIC FOUNDATION
                           Ontology
                              |
              vocabulary / relation types / invariants
                              v

Identity ------> Structure ------> Realization ------> Expression
commitments        plans             facts/state         language
```

See `docs/architecture/narrative-ontology-v2.md` for the canonical Layer-0
contract.

## Independent artifact coordinates

Semantic layer is only one coordinate. A narrative artifact is reasoned about
through four independent coordinates:

`semantic layer x scope x authority x revision/temporal position`

This is an explanatory model of the existing architecture, not a new
foundational architecture. In particular:

- a Realization artifact is not canonical merely because it is Realization;
- a deterministic projection is not authoritative merely because it is computed;
- a revised artifact keeps its narrative position even when revision order changes;
- publication does not imply acceptance.

## Scope axis

The persisted/runtime compatibility vocabulary remains:

| Scope | Responsibility | Status | Examples |
|---|---|---|---|
| Universe | Shared world constraints and lore | Optional | World rules, chronology, factions |
| Series | Cross-entry continuity and progression | Optional | Entry arcs, recurring relationships, setup/payoff |
| Book | One complete narrative contract and structure | Canonical compatibility form of Entry | Story identity, blueprint, book plan |
| Chapter | A bounded contribution to a Book | Compatibility form of Segment | Chapter function, scene grouping, state changes |
| Scene | A concrete local realization | Optional until needed | Location, action, knowledge, outcome |

ADR 020 establishes medium-neutral semantic vocabulary for generic boundaries:

`Universe -> Series/Collection -> Entry -> Segment -> Scene`

Presentation aliases include Book/Episode/Film/Story/Route/Mission for Entry and
Chapter/Act/Sequence/Section/Mission for Segment. This does not rewrite existing
Book/Chapter persistence, provenance, or accepted artifacts.

Scopes are containers across which semantic layers may be applied. They are not
additional semantic layers. Not every scope/layer cell requires an artifact.

## Cross-cutting systems

Validation, orchestration, editing, versioning, diagnostics, import/export, and
provenance operate across the semantic layers. There is no permanent Layer 2.5.
Structure composition and outline coordination are Structure work coordinated by
the orchestration system.

Reasoning/Tutor systems may recommend changes but do not acquire authority by
producing a recommendation. Acceptance remains an explicit authorial boundary.

## Canonical and derived artifacts

Author-declared identity contracts and plans are canonical when explicitly
accepted by the author. Accepted Realization facts/state changes become
canonical through their own lifecycle. Compiled bibles, Global Map, Focus,
relationship/dependency indexes, reports, diagnostics, session state, and other
projections are derived and must not silently replace the source contract.
Draft prose is an Expression artifact; editing is a cross-cutting workflow whose
findings may require review of Expression, Realization, Structure, or Identity.

Derived story-instance relation indexes may contain declared, deterministic, or
interpretive relations, but the index cannot promote an assertion into canon.
Confidence may rank an interpretation; it cannot change authority.

## Structure versus Realization vocabulary

Use the following distinction when precision matters:

- `StructuralBeat` — an intended structural moment/function in a plan;
- `Event` — an occurrence represented as having happened;
- `StateTransition` — a realized change from one narrative state to another.

A plan may be realized through events; a plan does not silently become a fact.

## Progressive disclosure

### Short story

`Story Identity -> lightweight Structure -> Scenes -> Prose`

An Entry-level Identity and enough Structure to preserve the author's
commitments are required. Universe, Series, detailed Segment artifacts, and full
state tracking are optional and may be added later.

### Standalone novel

`Story Identity -> Entry/Segment Structure -> Scene Realization -> Expression`

Entry Identity is required (currently commonly persisted as Book Identity). Some
form of Structure is recommended and may be lightweight, inferred, or expanded
later. Scene Realization and Expression are added when the author proceeds
toward drafting. Universe and Series scopes remain optional.

### Series

`Universe or Series Identity -> Entry Identities -> Cross-entry Structure -> Entry Realization -> Expression`

Series Identity and Entry Identities are required as the narrative grows.
Universe Identity is optional. Existing Series V1 storage may still express the
Entry form as Book. Continuity plans, compiled bibles, and detailed realization
state can be added progressively.

## Unresolved specifications

The following boundaries are intentionally not implemented by this document:

1. **Emotional trajectory contract:** define story emotional core, segment
   function, scene experiential effect, and character emotional state without a
   rigid state machine. Support milestones, variation, masking, contradiction,
   regression, sudden transition, and intentional divergence.
2. **Revision and staleness semantics:** define which downstream plans,
   realizations, expressions, and reports become stale or require review after
   each class of upstream change. The Minimal V1 pilot is specified in
   [Revision and Staleness Semantics](revision-and-staleness-semantics.md).
3. **Expression boundary:** define which language-level choices belong to
   Expression and which realized event facts remain canonical upstream.
4. **Entry/Segment persistence migration:** ADR 020 ratifies the semantic
   vocabulary but does not require immediate Book/Chapter storage migration.

## Current implementation mapping

| Concern | Current implementation | Canonical placement |
|---|---|---|
| Concepts/relation vocabulary | `narrative_ontology`, packaged ontology data, ontology CLI | Ontology |
| World and series contracts | `universe`, `series`, `book` | Identity and Structure at their scopes |
| Story identity and discovery | `identity`, genre pipelines, Genre Builder, Story Discovery | Identity |
| Blueprint and diagnostics | `narrative_blueprint`, `structure`, Cartographer | Structure |
| Composition coordination | `narrative_orchestration` | Structure, coordinated by Orchestration |
| Events and state | `narrative_realization`, Bible/state, relations projections | Realization |
| Drafting and prose critics | `pipeline`, Bard, `critic` | Expression and cross-cutting Validation |
| Editing | `editing` | Cross-cutting, producing Expression-facing reports |
| Import/export and graph projections | `roundtrip`, serializers, graph/report artifacts | Cross-cutting |
| Global Map / Focus / dependency views | `series` derived projections | Cross-cutting derived reasoning/projection |

## Four-coordinate view

```text
                   NARRATIVE SEMANTIC FOUNDATION
                           Ontology
                              |
  Identity ----------> Structure ----------> Realization ----------> Expression
  Commitments            Plans                Events/state             Language

                              x

  Universe ----------> Series ----------> Entry ----------> Segment ----------> Scene
                       (Book/Episode...)       (Chapter/Act...)

                              x

                 Candidate | Derived | Canonical

                              x

           Revision history | narrative position | currentness

  CROSS-CUTTING: Validation · Orchestration · Editing · Versioning · Diagnostics
                 Import/Export · Provenance · Reasoning/Tutor
```
