# Runtime and Domain Context

> Current repository status: [STATUS.md](STATUS.md).  
> Canonical architecture: [Narrative Architecture](docs/narrative-architecture.md).  
> Layer-0 contract: [Narrative Ontology V2](docs/architecture/narrative-ontology-v2.md).  
> Durable mission: [MISSION.md](MISSION.md).  
> Release policy: [Release Qualification](docs/engineering/release-qualification.md).

This document defines runtime/domain terminology and compatibility context for Auteur's built-in interactive genre pipelines, versioned Genre Packs, Narrative Ontology, and selected cross-scope behavior. It is **not** the repository roadmap or current milestone handoff; use `STATUS.md` for present-tense development state.

## Narrative Ontology V2 runtime boundary

Narrative Ontology is the semantic substrate of the existing Narrative Architecture. It defines reusable concepts, relation types, value vocabularies, and deterministic semantic invariants; it does not own project-specific authorial commitments, plans, accepted facts, prose, workflow state, or derived map assertions.

The runtime path is:

```text
src/auteur/data/ontology/*.yaml
        -> OntologyLoader
        -> OntologyRegistry
        -> OntologyValidator
```

`src/auteur/data/ontology/` is the single canonical ontology specification location. The historical `narrative_ontology.core.narrative_concepts` module and genre-specific Python classes are compatibility surfaces, not independent semantic sources for production validation.

Ontology validation uses four rule categories:

- `schema_constraint` — deterministic structural/reference validity;
- `semantic_invariant` — deterministic semantic validity implemented by a named executor;
- `craft_heuristic` — advisory guidance only;
- `interpretive_criterion` — human/model judgment only.

Free-text rule conditions are documentation and are never evaluated as executable code. Craft or interpretive guidance cannot silently acquire canonical authority.

Product genres do not require a genre ontology extension. If a genre exists in the product genre enum but has no `<genre>_ontology.yaml`, it inherits the core ontology. Packaged genre extensions add semantic vocabulary only.

### Relationship domains

Keep these meanings separate:

1. `RelationType` — reusable ontology vocabulary, such as `depends_on` or `affects`;
2. `CharacterRelationship` / relationship state — narrative concept and realized character/entity relationship state;
3. story-instance relations — declared, deterministically derived, or interpretive assertions between actual narrative facts/artifacts.

A relation type is not a story assertion. A derived story-instance relation index cannot promote itself into canon.

### Structure and Realization terms

Prefer:

- `StructuralBeat` for a planned structural moment/function;
- `Event` for an occurrence represented as having happened;
- `StateTransition` for a realized state change.

A planned StructuralBeat does not itself prove an Event or StateTransition occurred.

### Medium-neutral scope vocabulary

ADR 020 introduces a semantic vocabulary of:

```text
Universe -> Series/Collection -> Entry -> Segment -> Scene
```

Existing Book/Chapter runtime and serialized contracts remain compatible. Entry may be presented as Book, Episode, Film, Story, Route, or Mission; Segment may be presented as Chapter, Act, Sequence, Section, or another medium-appropriate subdivision. This is a semantic compatibility layer, not a mass persistence migration.

## Interactive Genre Pipelines vs Genre Packs

Auteur has two distinct genre mechanisms.

### Interactive Genre Pipelines

Interactive pipelines are deterministic authoring workflows that collect
genre-specific choices and compile them into a `StoryIdentity`.

They own:
- interactive session state;
- phase choices;
- browser/runtime orchestration;
- deterministic completion validation;
- explicit ratification.

Their working state is non-canonical until explicitly compiled and
accepted.

### Genre Packs

Genre Packs are versioned bodies of genre knowledge used to:
- evaluate whether a pack applies to a premise;
- recommend one strongest profile inside an applicable pack;
- explain rejected alternatives;
- diagnose accepted story commitments.

Genre Packs do not constitute a new semantic layer.

A recommendation is advisory and causes no Layer 1 mutation until explicit
acceptance or override.

When no installed pack is a strong fit, Auteur returns an honest
`no_applicable_pack` advisory rather than forcing the only available pack.

### Shared authority rule

`StoryIdentity` remains the canonical Layer 1 authority. Pipeline sessions,
Genre Pack recommendations, advisories, diagnostics, and generated
blueprints are working, proposed, or derived artifacts unless explicitly
promoted through the documented author-confirmation path.

## Authority and mutation

Any operation that modifies `StoryIdentity` must:
1. require explicit author action;
2. show the proposed change;
3. persist atomically;
4. retain provenance and rationale;
5. leave the prior state unchanged on failure.

Recommendation acceptance and author override require explicit
confirmation.

## Applicability scores

Genre Pack applicability scores are deterministic heuristic policy scores,
not calibrated probabilities or unrestricted semantic judgments.

Known limitations include curated phrase coverage, nested negation,
coreference, euphemism, and low-margin classifications.

## Genre Pipeline

A genre pipeline is a deterministic Narrative Engine workflow that turns an
author's genre-specific choices into a validated `StoryIdentity`. Netorare, mystery,
and gentlefemdom are built-in pipelines. A built-in pipeline is not an external
plugin and is separate from project-local contracts created by Genre Builder.

Each pipeline supplies genre-specific intent through a `GenrePipelineSpec`:

- genre and stable slug;
- supported emotional core IDs and their default core;
- template factory and deterministic choice validator;
- genre-contract loader and core identity profile;
- browser title, default port, and author-visible mode default.

The registry is operational: public genre commands resolve a specification and
execute through `auteur.genre_pipeline`. Runtime code does not dispatch on genre
names or import another genre's command, session, server, or identity generator.

## Genre phases and dimensions

Genre pipelines use nine genre-specific phases/dimensions. These are not
Auteur semantic architecture layers.

1. Emotional core
2. Genre contract
3. Scope and scale
4. Structural forces: want, resistance, conflict, stakes, change
5. Threads or the core-specific fifth design dimension
6. Carriers or the core-specific sixth design dimension
7. Representation or the core-specific seventh design dimension
8. Modulation or the core-specific eighth design dimension
9. Resonance and ratification

Templates expose phase names, options, constraints, and a primary emotion. The
runtime normalizes existing mapping-shaped and flat option layouts into one
browser descriptor. A phase without options is derived context and requires no
stored author selection.

## Runtime Ownership

`auteur.genre_pipeline` owns:

- versioned interactive session state;
- normalization of template data for the browser;
- localhost HTTP endpoints and packaged browser assets;
- deterministic choice and completion validation;
- neutral compilation of completed choices into `StoryIdentity`;
- orchestration shared by all public built-in genre commands.

Genre packages own their templates and validation rules. The operational
registry owns core identity profiles, while `auteur.genres` owns genre contracts.
Project-local custom contracts do not become browser pipelines automatically.

## Canonical State

Browser session state is a non-canonical working artifact stored at:

```text
<project>/.auteur/genre_sessions/<genre-slug>/session.json
```

The author may change choices, working title, and story mode while the session is
incomplete. Browser completion is explicit ratification of those choices. The CLI
then compiles and validates a `StoryIdentity`; error diagnostics block the write,
while warnings are reported. Existing `story_identity.yaml` files are never
silently overwritten.

Legacy `<project>/netorare/session.json` files are detected but never silently
migrated. They remain non-canonical and require an explicit author decision.

## Public Commands

The public entry points remain:

```text
auteur netorare init <project>
auteur mystery init <project>
auteur gentlefemdom init <project>
auteur gentlefemdom resume <project>
```

Each is a thin adapter over the same runtime. Core choices and default ports come
from the registry. Story mode has a visible core-specific default and remains
author-overridable. `--provider` is compatibility-only because interactive genre
authoring performs no LLM call.

`resume` reopens an existing incomplete session. Completed and archived sessions
remain immutable. Project-local custom genre IDs are prompt guidance only in V1;
they are not valid canonical `StoryIdentity.story_type.genre` values.

## Extension Rule

Adding a built-in genre requires templates, deterministic validation, core
identity profiles, a genre contract, one registry entry, and tests. It must not
require edits to session, server, browser, or identity compilation logic.

Adding a **genre ontology extension** is a separate concern. It requires one packaged `<genre>_ontology.yaml` specification and integrity tests; it must not require a parallel Python registry edit.

## Series Continuity & Universe Propagation (ADR 018)

Series narratives are validated for continuity across books using deterministic validators:

- **Thematic Progression**: Arcs introduced must progress or resolve; gaps are flagged.
- **Character Continuity**: Character states must evolve logically; impossible transitions are errors.
- **Relationship Continuity**: Relationship state changes without justification trigger warnings.
- **Lore Consistency**: Lore contradictions without explanation are flagged.
- **Chronology**: Timeline events must respect causality; impossible dates are errors.
- **Setup/Payoff Tracking**: Unresolved setups past their deadline generate warnings.

**Universe-to-Series Propagation (ADR 018):**

Universe constraints propagate downward to Series and Books. Constraints are classified:

1. **Structured Constraints** (deterministic, blocking):
   - Finite-domain values (genres, character states, thematic arcs)
   - Boolean conditions
   - Enumerated relationships
   - Violations produce ERROR diagnostics and block compilation

2. **Natural-Language Principles** (advisory, non-blocking):
   - Free-text guidance
   - Generate WARNING diagnostics only
   - Do not block Series compilation

3. **LLM-Assisted Interpretation** (optional, V1 non-blocking):
   - Semantic similarity checks
   - Marked as uncertain (INFO level)
   - Never block in V1

Series may **strengthen but not weaken** Universe constraints. All diagnostics include:
- Originating constraint
- Conflicting field
- Severity level
- Actionable explanation

Validation is opt-in via `universe_constraint_path` in `SeriesIdentity`; the older
`universe_contract` path remains a compatibility alias. Universe YAML may carry
`structured_constraints`, which are converted into deterministic Series diagnostics.
Missing or invalid referenced contracts are errors, not silently skipped.

**Canonical Ownership (ADR 018):**
- `SeriesIdentity` (series_identity.yaml) is the canonical author-edited contract
- `SeriesBible` (series_bible.json) is a compiled operational artifact derived from identity, book plans, and continuity state

## Genre Pipeline Compatibility Notes

**Warning Persistence:** Validation warnings are now persisted in session.json and survive browser reload via GET /session.

**409 Conflict for Completed Sessions:** Mutations of completed sessions return HTTP 409 (not 422) to distinguish state conflicts from data validity.

**Occupied-Port Preflight:** Port availability is checked before session creation, preventing orphaned sessions from failed server startup.

**Regression Tests:** Horror end-to-end flow and actual three-CLI subprocess invocations are regression-tested.

**Operational Extensions:** `/health` reports session readiness; warning acknowledgments
are stored with session state; terminal sessions are immutable; archived sessions live
under `genre_sessions/<genre>/history/` with lock-protected transitions.
`auteur universe build` canonicalizes a UniverseIdentity, and `auteur book build`
compiles one BookPlan into a StoryIdentity. Series graph output includes a Mermaid
companion beside the YAML graph.

Last reconciled: 2026-09-11.
