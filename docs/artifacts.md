# Auteur Narrative Artifacts

> Canonical architecture: [Narrative Architecture](narrative-architecture.md).  
> Realization semantics: [Realization State Contract](realization-state-contract.md).  
> Character/relationship ownership: [Character and Relationship Architecture](character-and-relationship-architecture.md).

This document describes durable and workflow-significant artifacts that Auteur
produces across its semantic layers and scopes. A filename alone does not grant
authority: canonical status comes from the owning acceptance/persistence
workflow and provenance contract.

## Layered Story Architecture

Auteur uses five semantic layers across optional narrative scopes. Not every
scope/layer cell requires a persistent artifact. Universe, Series, Book,
Chapter, and Scene are scopes, not layers.

```text
Ontology → Identity → Structure → Realization → Expression
```

The semantic axis is Ontology → Identity → Structure → Realization → Expression.
Each scope/layer cell is optional unless a workflow explicitly requires it.

---

## Layer Artifacts

### Universe scope (`universe_identity.yaml`)

Defines world rules, constraints, and lore that apply to all descendant Series.

**Current `UniverseIdentity` fields:**
- `name`: Universe name
- `slug`: Stable project-safe identifier
- `description`: Human-readable description
- `setting_profile`: setting type, primary location, known locations, and optional worldbuilding scope
- `magic_system`: World magic/system rules when present
- `core_mythology`: Governing mythology/cosmology summary
- `timeline`: current era, era description, and years of history
- `forbidden_elements`: elements descendant stories must avoid
- `required_elements`: elements descendant stories must preserve
- `cross_story_constraints`: rules with applicability and severity
- `structured_constraints`: typed constraints used by contemporary validation

Historical Universe specs may show older field names. The current model under
`src/auteur/universe/models.py` and this artifact map are authoritative for the
persisted schema.

**Canonical:** Yes — author edits directly  
**Usage:** Propagates constraints to Series and Books  
**Validation:** Universe constraints block Series compilation if violated

---

### Series scope (`series_identity.yaml`)

Defines multi-book continuity, character arcs, thematic throughlines, and relationships.

**Core Fields:**
- `title`: Series name
- `series_type`: duology, trilogy, quartet, limited_series, ongoing
- `book_count`: Number of books
- `core_question`: Series-level mystery or premise
- `target_experience`: Reader's intended emotional journey
- `global_arc`: Series structure (beginning, midpoint, ending)

**Book Plans:**
- `book_plans`: List of BookPlan objects (1-N books)
  - Each includes: number, title, series_function, core_answer, target_experience, story_type, central_engine

**Continuity (ADR 018):**
- `universe_constraint_path` (optional): Path to universe_identity.yaml for constraint validation
- `universe_contract` (compatibility alias): Older name for the same path
- `thematic_arcs`: Thematic progression across books
  - `theme`: Thematic statement (e.g., "Power destroys intimacy")
  - `books`: Which books develop this theme
  - `progression`: Map of book → state (introduces, deepens, resolves)
- `character_states`: Character states per book
  - `character_id`, `book`, `state` (dict of key-value pairs)
- `relationships`: Relationship states with justification
  - `party_a`, `party_b`, `book`, `state`, `notes`
- `lore_entries`: Lore with consistency tracking
  - `id`, `book`, `content`, `consistency_notes`
- `timeline_events`: Event dating with absolute/relative options
  - `id`, `absolute_date` (optional), `relative_book`, `relative_position`, `duration`
- `narrative_setups`: Setups to be paid off
  - `id`, `book_introduced`, `description`, `expected_payoff_by_book`, `status`, `payoff_id`

**Arcs (Legacy, pre-ADR 018):**
- `character_arcs`: Character progression across series
- `relationship_arcs`: Relationship evolution
- `faction_arcs`: Faction state changes
- `mysteries`: Cross-book mysteries with payoff tracking

**Canonical:** Yes — author edits directly  
**Usage:** Compiled into Series Bible; validated against Universe constraints  
**Validation:** Continuity diagnostics for thematic, character, relationship, lore, chronology, and setup/payoff consistency

---

### Derived Series Bible (`series_bible.json`)

Compiled operational reference derived from `series_identity.yaml` and book-level state.

**NOT canonical** — generated artifact, do not edit directly.

**Structure:**
```json
{
  "title": "Series name",
  "core_question": "Series premise",
  "characters": [...],
  "relationships": [...],
  "factions": [...],
  "mysteries": [...],
  "timeline": [...],
  "character_state_matrix": { "Character": { "1": "state", "2": "state" } },
  "relationship_state_matrix": { "rel_id": { "1": "state", "2": "state" } },
  "faction_state_matrix": { "Faction": { "1": "state", "2": "state" } },
  "mystery_status_by_book": { "1": [...], "2": [...] },
  "payoff_schedule": { "1": [...], "2": [...] },
  "unresolved_threads": [...],
  "continuity_diagnostics": [
    {
      "id": "THEMATIC_ARC_NOT_DEVELOPED",
      "severity": "WARNING",
      "constraint": "Theme must progress",
      "conflict": "Arc introduced but not developed",
      "explanation": "..."
    }
  ]
}
```

**Generated by:** `auteur series bible`  
**Includes:** Compiled continuity and Universe diagnostics with explanations

---

### Book Identity (`story_identity.yaml`)

Defines a single book's genre, emotional core, mode, and narrative blueprint contract.

**Fields:**
- `title`: Book title
- `story_type`:
  - `genre`: netorare, mystery, gentlefemdom (or custom contract)
  - `mode`: tragic, procedural, intimate (depends on genre)
- `emotional_core`: Core-specific (e.g., classic_humiliation, howdunit, sensual_dominance)
- `target_experience`: Reader's intended emotional arc
- `central_engine`: High-level want, resistance, stakes

**Produced by:** `auteur {genre} init` (interactive browser session)  
**Canonical:** Yes — author creates once, rarely edits  
**Validation:** Validated against the StoryIdentity schema and deterministic identity diagnostics

---

### Project relationship state (`relations.yaml`)

Defines canonical project-level character relationship state under ADR 015.
It is separate from Blueprint relationship intent, Series continuity, Scene
Realization, and derived story-instance relations.

**Current state includes:**
- directional `from_character` / `to_character`;
- public role and private truth;
- trust, resentment, dependency, attraction, fear, and obligation;
- optional `last_changed_in` provenance/context.

Chapter-scoped `relation_changes.yaml` files describe explicit deltas. The
`auteur relations apply` workflow produces the updated relationship state;
validation, diagnostics, and graphs do not mutate canon.

**Canonical:** Yes, when persisted through the owning relation-state workflow  
**Derived companions:** `relations_graph.yaml`, `relations_diagnostics.json`  
**Contract:** [Character and Relationship Architecture](character-and-relationship-architecture.md)

---

### Structure: Blueprint (`blueprint.yaml`)

Scene-by-scene narrative structure aligned to the 9-phase genre structure.

**Structure:**
- `story_identity_ref`: Link back to story_identity.yaml
- `phases`: 9-phase breakdown with scene lists
  - Each phase: target emotion, setup scenes, climax scenes, resolution scenes

**Produced by:** `auteur blueprint seed` (from story identity)  
**Usage:** Input to Outline layer; validates against emotional core constraints  
**Validation:** Ensures phase assignments and emotional progression align with genre

---

### Structure/Realization boundary: Outline (`chapters/NN/outline.yaml`)

Scene-by-scene breakdown (via Cartographer or manual authoring).

**Structure:**
- Scene cards with:
  - POV character
  - Location
  - Key emotional beat
  - Functional purpose (setup, complication, revelation, reversal, climax, resolution)
  - Character states before/after

**Produced by:** Cartographer (scene-by-scene decision engine)  
**Usage:** Input to Draft layer; reference for consistency checking  
**Validation:** POV consistency, timeline continuity, emotional pacing

---

### Realization: Scene state (`realization.yaml` / scene YAML)

Records a concrete Scene Realization: what happens and what state is true
because it happens.

A ready scene includes:

- scene/chapter identity and narrative position;
- story time and optional follows/parallel relationships;
- POV character and participants;
- goal, opposition, turn, decision, and outcome;
- entry and exit knowledge/emotional state;
- arc-beat realization degree;
- setups created and payoffs triggered.

The central transition is:

```text
entry_state
+ dramatic action / outcome
= exit_state
```

For the current knowledge schema, every `Outcome.knowledge_added` value must
exactly equal a persisted `exit_state.knowledge[].what` value. Entry knowledge
continues unless that exact fact is explicitly questioned; deterministic
validation does not infer paraphrase equivalence.

**Produced/managed by:** Realization workflows such as
`auteur realization seed|validate|inspect|graph` and accepted-scene persistence  
**Canonical:** Accepted Scene Realization is narrative authority; draft/template
files are not canonical merely because they exist  
**Usage:** Source for Expression and downstream state/continuity reasoning  
**Contract:** [Realization State Contract](realization-state-contract.md)

---

### Expression: Draft (`chapters/NN/draft_vN.md`)

Actual prose generation and management.

**Structure:**
- Full manuscript text
- Inline metadata (chapter breaks, scene markers)
- Optional: word-count tracking, revision history

**Produced by:** LLM generation or manual authoring  
**Usage:** Source for editing workflow  
**Validation:** UTF-8 encoding, BOM handling, narrative coherence checks

---

### Cross-cutting Editing (`<book>_review.md` / `<book>_drift_report.json`)

Refinement, review, and drift validation.

Editing is cross-cutting. Its findings may require review of Expression,
Realization, Structure, or Identity; an editing report does not silently rewrite
those canonical sources.

**Review Artifact (`<book>_review.md`):**
- Generated editorial feedback
- Marked sections requiring attention
- Actionable next steps

**Drift Report (`<book>_drift_report.json`):**
- Relationship changes between declared identity and actual prose
- Unresolved narrative threads
- Emotional arc deviation
- Character state inconsistencies

**Round-Trip Import (`imported_draft.md`):**
- Re-imported prose after external editing
- BOM stripped for clean comparison

---

## Session Artifacts

### Genre Pipeline Session (`.auteur/genre_sessions/<genre>/session.json`)

Working artifact during interactive story-identity authoring.

**Fields:**
- `schema_version`: 1
- `id`: Session UUID
- `genre`: netorare, mystery, gentlefemdom
- `core_id`: Emotional core
- `mode`: Story mode
- `working_title`: Author's working title
- `choices`: Dict[phase: Dict[field: value]] — nine-phase choices
- `warnings`: List of validation warnings (persisted, survives reload)
- `status`: incomplete, complete
- `created_at`, `updated_at`: Timestamps

**Lifecycle:**
- Created: `auteur {genre} init`
- Mutated: Browser UI updates choices/settings
- Warnings generated and persisted: Validation runs after each update
- Completed: Author clicks "Complete"; generates story_identity.yaml
- Immutable: After completion, all mutations return 409 Conflict

**Storage:**
```text
<project>/.auteur/genre_sessions/<genre>/session.json
```

Legacy path (`<project>/<genre>/session.json`) is detected but never silently migrated.

---

## Diagram: Artifact Flow

```
universe_identity.yaml
       ↓
       └─→ (constraints propagate)
           ↓
    series_identity.yaml ← (validates against universe)
           ↓
      series_bible.json (generated, includes diagnostics)
           ↓
    story_identity.yaml ← (validates against universe)
           ↓
      blueprint.yaml
           ↓
    chapters/NN/outline.yaml
           ↓
    Scene Realization YAML
      ↙             ↘
relations.yaml      Scene Expression / draft
      ↘             ↙
   review / reconciliation / acceptance
           ↓
   Book composition / publication
```

---

## Artifact Validation

| Artifact | Validates Against | Produces Diagnostics? |
|---|---|---|
| story_identity.yaml | Genre contract, Universe constraints | Errors (blocking) |
| series_identity.yaml | Universe constraints, continuity rules | Errors + warnings |
| series_bible.json | SeriesIdentity, continuity and Universe diagnostics | Errors block compilation; warnings persist |
| blueprint.yaml | Story Identity and structure contracts | Warnings / deterministic diagnostics |
| chapters/NN/outline.yaml | Blueprint structure and planning contracts | Planning/continuity diagnostics |
| Scene Realization YAML | Scene schema, temporal, knowledge, and realization contracts | Errors + warnings |
| relations.yaml / relation_changes.yaml | Relation schema and explicit relationship-state rules | Errors + deterministic diagnostics |
| Expression candidates | Accepted/fresh Realization plus Expression constraints | Validation / divergence status |
| <book>_drift_report.json | Declared identity/state vs. actual prose | Deviations only |

---

## Persistence & Version Control

All artifacts should be version-controlled:

```text
project/
  .auteur/
    genre_sessions/
      netorare/
        session.json           (non-canonical; retained until explicit archive)
  universe_identity.yaml        (VCS)
  series_identity.yaml          (VCS)
  series_bible.json             (generated, can be VCS'd for audit trail)
  story_identity.yaml           (VCS)
  blueprint.yaml                (VCS)
  relations.yaml                (VCS when relation-state workflow is used)
  chapters/
    NN/
      outline.yaml              (VCS)
      relation_changes.yaml     (VCS when present)
      scenes/
        <scene>/realization.yaml (VCS; accepted authority via owning workflow)
      draft_vN.md               (VCS)
  <book>_review.md              (VCS)
  <book>_drift_report.json      (VCS for audit trail)
```

---

**Last reconciled:** 2026-09-28  
**Related:** [Narrative Architecture](narrative-architecture.md),
[Realization State Contract](realization-state-contract.md),
[Character and Relationship Architecture](character-and-relationship-architecture.md),
ADR 015 (relationship state), and ADR 018 (Universe-to-Series propagation)

## Operational Extensions

Genre sessions expose a read-only `/health` endpoint, persist warnings and explicit
acknowledgments, and can be archived into a history directory. `auteur universe build`
and `auteur book build` create canonical YAML-derived artifacts without LLM calls.
`auteur series graph` writes both `dependency_graph.yaml` and a Mermaid `.mmd`
visualization.
