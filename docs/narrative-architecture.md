# Auteur Narrative Architecture

This is the canonical architecture specification for Auteur. It supersedes
active documentation that presents scopes, genre phases, or workflow concerns
as semantic layers. Historical ADRs and archived plans retain their original
terminology as historical context.

## Semantic layers

| Layer | Core question | Knowledge type | Owns | Does not own |
|---|---|---|---|---|
| 0. Ontology | What narrative concepts exist? | Concepts | Concepts, relationships, vocabularies, domain rules | Authorial commitments, plot plans, prose |
| 1. Identity | What commitments define this narrative? | Commitments | Genre, subgenre, medium, scope, scale, target experience, emotional core, theme, core engine | Detailed sequencing, realized events, wording |
| 2. Structure | How is the narrative planned and organized? | Plans | Threads, arcs, beats, chapter plans, setup/payoff intentions, thematic progression | Realized events, moment-to-moment states, prose |
| 3. Realization | What concrete events and state changes occur? | Events and state changes | Scenes, event order, knowledge, location, inventory, relationship and character deltas | Sentence-level language and style |
| 4. Expression | How are those events rendered as language and prose? | Language | Voice, diction, POV, dialogue, imagery, pacing, sentence form, prose revision | Canonical plot commitments and event facts |

These layers describe kinds of knowledge. They are not a requirement that every
project produce one artifact for every layer.

## Scope axis

| Scope | Responsibility | Status | Examples |
|---|---|---|---|
| Universe | Shared world constraints and lore | Optional | World rules, chronology, factions |
| Series | Cross-book continuity and progression | Optional | Book arcs, recurring relationships, setup/payoff |
| Book | One complete narrative contract and structure | Canonical for a standalone book; may begin as a minimal identity | Story identity, blueprint, book plan |
| Chapter | A bounded contribution to a book | Optional | Chapter function, scene grouping, state changes |
| Scene | A concrete local realization | Optional until needed | Location, action, knowledge, outcome |

Scopes are containers across which semantic layers may be applied. They are not
additional semantic layers. Not every scope/layer cell requires an artifact.

## Cross-cutting systems

Validation, orchestration, editing, versioning, diagnostics, import/export,
provenance, and optional audience-effect analysis operate across the semantic
layers. There is no permanent Layer 2.5 and no audience-effect semantic layer.
Structure composition and outline coordination are Structure work coordinated by
the orchestration system. Mass-Appeal Narrative Architecture (MANA) is a derived,
noncanonical audience-side projection over existing evidence; see
[Mass-Appeal Narrative Architecture](mass-appeal-narrative-architecture.md).

## Pre-Identity creative search

Creative search that asks **what story should be developed at all** sits before
accepted Identity rather than forming another semantic layer.

Story Opportunity Discovery may produce working preferences, influence
decompositions, critique interpretations, candidate premises, differentiators,
and opportunity comparisons. Those outputs are advisory / noncanonical and do
not become Identity merely because they are persisted or agent-generated.

The boundary is:

    Story Opportunity Discovery
    -> working opportunity / premise / Discovery Brief
    -> optional Premise Fitness
    -> Story Discovery
    -> candidate Story Identity
    -> explicit acceptance
    -> canonical Identity

Premise Fitness is also pre-Identity and noncanonical. It evaluates whether a
working premise is fit for the intended genre, experience, scope, complexity,
and posture; it does not create a new semantic layer or universal quality rank.

See [Story Opportunity Discovery](story-opportunity-discovery.md) and
[Premise Fitness](premise-fitness.md).

## Canonical and derived artifacts

Author-declared identity contracts and plans are canonical when explicitly
accepted by the author. Compiled bibles, graphs, reports, diagnostics, session
state, and other projections are derived and must not silently replace the
source contract. Draft prose is an Expression artifact; editing is a
cross-cutting workflow whose findings may require review of Expression,
Realization, Structure, or Identity.

## Progressive disclosure

### Short story

`Story Identity → lightweight Structure → Scenes → Prose`

Book Identity and enough Structure to preserve the author’s commitments are
required. Universe, Series, detailed chapter artifacts, and full state tracking
are optional and may be added later.

### Standalone novel

`Story Identity → Book/Chapter Structure → Scene Realization → Expression`

Book Identity is required. Some form of Structure is recommended and may be
lightweight, inferred, or expanded later. Scene Realization and Expression are
added when the author proceeds toward drafting. Universe and Series scopes
remain optional.

### Series

`Universe or Series Identity → Book Identities → Cross-book Structure → Book Realization → Expression`

Series Identity and Book Identities are required. Universe Identity is optional.
Continuity plans, compiled bibles, and detailed realization state can be added
progressively.

## Supplemental canonical contracts

This document defines the five-layer × scope architecture. Focused contracts
define important boundaries without creating additional semantic layers:

1. [Realization State Contract](realization-state-contract.md) — concrete scene
   events/state, exact knowledge continuity, temporal/state ownership, and the
   Realization → Expression boundary.
2. [Emotional Trajectory Contract](emotional-trajectory-contract.md) — separates
   reader promise, structural emotional progression, character felt state, and
   emotional rendering without a rigid state machine.
3. [Character and Relationship Architecture](character-and-relationship-architecture.md)
   — distinguishes character commitments/plans, concrete state, canonical
   `relations.yaml`, Series continuity, and derived relationship projections.
4. [Theme and Motif Contract](theme-and-motif-contract.md) — distinguishes
   thematic commitment, progression, realized evidence, rendering, and motifs.
5. [Revision and Staleness Contract](revision-staleness-contract.md) — defines
   downstream freshness behavior after upstream changes.
6. [Expression Boundary](expression-boundary.md) — defines language-level
   freedom versus canonical realized event/state facts.
7. [Mass-Appeal Narrative Architecture](mass-appeal-narrative-architecture.md) —
   defines optional, stage-sensitive audience-effect analysis across the existing
   layers without adding canon, a quality score, or an automatic winner rule.

Historical plans, ADRs, and research records retain their original terminology
as evidence. Where an older example conflicts with a current canonical contract,
the canonical architecture + focused contract + current schema take precedence.

## Current implementation mapping

| Concern | Current implementation | Canonical placement |
|---|---|---|
| Concepts | `narrative_ontology` and ontology CLI | Ontology |
| World and series contracts | `universe`, `series`, `book` | Identity and Structure at their scopes |
| Story identity and discovery | `identity`, genre pipelines, Genre Builder, Story Discovery | Identity |
| Blueprint and diagnostics | `narrative_blueprint`, `structure`, Cartographer | Structure |
| Composition coordination | `narrative_orchestration` | Structure, coordinated by Orchestration |
| Events and state | `narrative_realization`, Bible/state, canonical relation state + derived projections | Realization |
| Drafting and prose critics | `pipeline`, Bard, `critic` | Expression and cross-cutting Validation |
| Editing | `editing` | Cross-cutting, producing Expression-facing reports |
| Import/export and graph projections | `roundtrip`, serializers, graph/report artifacts | Cross-cutting |

## Two-dimensional view

```text
                         SEMANTIC AXIS

  Ontology ─────▶ Identity ─────▶ Structure ─────▶ Realization ─────▶ Expression
  Concepts       Commitments      Plans             Events/state       Language

                         SCOPE AXIS

  Universe ─────────────────────────────────────────────────────────────────────
  Series   ─────────────────────────────────────────────────────────────────────
  Book     ─────────────────────────────────────────────────────────────────────
  Chapter ─────────────────────────────────────────────────────────────────────
  Scene    ─────────────────────────────────────────────────────────────────────

  CROSS-CUTTING: Validation · Orchestration · Editing · Versioning · Diagnostics
                 Import/Export · Provenance · Audience-Effect Analysis (MANA)
```
