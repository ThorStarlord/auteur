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

Validation, orchestration, editing, versioning, diagnostics, import/export, and
provenance operate across the semantic layers. There is no permanent Layer 2.5.
Structure composition and outline coordination are Structure work coordinated by
the orchestration system.

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

## Unresolved specifications

The following boundaries are intentionally not implemented by this document:

1. **Emotional trajectory contract:** define story emotional core, chapter
   function, scene experiential effect, and character emotional state without a
   rigid state machine. Support milestones, variation, masking, contradiction,
   regression, sudden transition, and intentional divergence.
2. **Revision and staleness semantics:** define which downstream plans,
   realizations, expressions, and reports become stale or require review after
   each class of upstream change. Author-declared artifacts must not be silently
   overwritten.
3. **Expression boundary:** define which language-level choices belong to
   Expression and which realized event facts remain canonical upstream.

## Current implementation mapping

| Concern | Current implementation | Canonical placement |
|---|---|---|
| Concepts | `narrative_ontology` and ontology CLI | Ontology |
| World and series contracts | `universe`, `series`, `book` | Identity and Structure at their scopes |
| Story identity and discovery | `identity`, genre pipelines, Genre Builder, Story Discovery | Identity |
| Blueprint and diagnostics | `narrative_blueprint`, `structure`, Cartographer | Structure |
| Composition coordination | `narrative_orchestration` | Structure, coordinated by Orchestration |
| Events and state | `narrative_realization`, Bible/state, relations projections | Realization |
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
                 Import/Export · Provenance
```
