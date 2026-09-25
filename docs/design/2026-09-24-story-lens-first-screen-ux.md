# Story Lens First-Screen UX Specification

**Status:** implementation contract  
**Selected by owner:** 2026-09-24  
**Product surface:** Beginner Workspace — premise -> interpretation -> Story Direction  
**Base dependency:** PR #285 / current-main Beginner coherence reconciliation  
**Authority:** Story Lenses are derived product projections. They do not create a
new narrative layer, acceptance system, or canonical story store.

## Goal

After an author submits an initial premise, the first valuable screen should
make the latent story architecture visible before asking the author to answer a
questionnaire.

The default overview exposes five connected Story Lenses:

1. **Main story engine** — what repeatedly generates story pressure.
2. **Emotional & aesthetic framing** — how the story is meant to feel.
3. **Common tropes** — recurring situations and expectations.
4. **Structural shape** — a likely story pattern, explicitly not an outline.
5. **Reader experience** — the expected emotional/cognitive progression.

The author can inspect/refine direct lenses, reorder the visible cards as a
presentation preference, and then continue into Story Discovery. None of those
operations silently creates canon.

---

# Stage 1 — Divergent breadth pass

## Approach A — Fixed five-panel dashboard

Hard-code five first-screen panels directly in browser code.

**Implementation complexity & weight:** low initially, but every new lens or
container variant increases browser-specific branching.

**End-user ergonomics:** visually simple, but difficult to personalize and
likely to become a rigid taxonomy.

**Operational actionability:** weak. The browser owns presentation semantics, so
operators cannot inspect one stable lens contract through the API.

**State cleanliness:** acceptable if read-only, but UI logic risks recreating
narrative interpretation and ordering rules client-side.

## Approach B — Derived Story Lens registry over existing architecture state

Add a typed, read-only Story Lens projection built from the existing
`NarrativeArchitectureAnalysis`. Direct lenses reference existing architecture
components; synthesized lenses derive bounded structural/reader-facing
interpretations. Browser layout order is a local presentation preference only.

**Implementation complexity & weight:** moderate and bounded. One projection
module plus browser rendering; no new canonical store.

**End-user ergonomics:** strongest. The default screen is immediately useful,
lenses are composable, and detail is progressively disclosed.

**Operational actionability:** strong. The same API exposes lens states,
sources, uncertainty, fallback mode, and actionable diagnostics.

**State cleanliness:** strongest. Narrative state remains in the existing
analysis/session; refinements reuse existing commands; layout preference never
enters story authority.

## Approach C — New persisted Story Architecture Workspace aggregate

Create a separate durable aggregate/event stream whose lens records can be
independently edited, reordered, accepted, and later reconciled into Identity /
Structure.

**Implementation complexity & weight:** high.

**End-user ergonomics:** potentially rich, but the user now interacts with a
second quasi-canonical story model before StoryIdentity.

**Operational actionability:** high in isolation, but creates another lifecycle
operators must reason about.

**State cleanliness:** poor for current needs. Lens state would shadow existing
architecture components and introduce reconciliation problems without evidence
that a second durable model is necessary.

## Selection

**Selected: Approach B — Derived Story Lens registry over existing architecture
state.**

It delivers the composable UI and detailed inspection contract while preserving
Auteur's strongest invariant: derived interpretation remains separate from
authority. A new persisted workspace would add architectural weight and
reconciliation risk without creating additional user value for this bounded
first-screen job.

---

# Stage 2 — Convergent depth specification

## 1. Interface and service contracts

### Python product contract

`src/auteur/beginner/story_lenses.py` defines:

```text
StoryLensType
StoryLensState
StoryLensItem
StoryLensProjection
StoryLensDiagnostics
build_story_lenses(...)
```

Default lens IDs are stable:

```text
story_engine
aesthetic_framing
common_tropes
structural_shape
reader_experience
```

A `StoryLensProjection` contains:

```text
lens_id
lens_type
title
eyebrow
summary
detail
state
authority_status
source_component_ids
items
related_lens_ids
refinement_mode
```

`StoryLensItem` is a read-only view of one existing
`ArchitectureComponent`; it does not duplicate persistence.

### Workspace API

The existing endpoint remains the public first-screen API:

```http
GET /api/beginner/workspaces/{workspace_id}
```

Relevant response fragment:

```json
{
  "story_orientation": {
    "story_lenses": [
      {
        "lens_id": "common_tropes",
        "lens_type": "common_tropes",
        "title": "Common tropes",
        "eyebrow": "Recurring situations and expectations",
        "summary": "Secret identity",
        "detail": "...",
        "state": "inferred",
        "authority_status": "DERIVED / NOT CANON",
        "source_component_ids": ["trope_family:..."],
        "items": [],
        "related_lens_ids": ["story_engine", "structural_shape"],
        "refinement_mode": "direct"
      }
    ],
    "lens_diagnostics": {
      "schema_version": 1,
      "analysis_id": "...",
      "analyzer_id": "...",
      "source_mode": "provider | deterministic_fallback",
      "stale": false,
      "active_component_count": 4,
      "suppressed_component_count": 1,
      "author_adjustment_count": 0,
      "unestablished_lens_ids": ["aesthetic_framing"],
      "needs_attention_lens_ids": ["aesthetic_framing"]
    }
  }
}
```

### Mutation commands

Story Lens refinement deliberately reuses existing versioned/idempotent commands:

```text
confirm-architecture-component
suppress-architecture-component
restore-architecture-component
rename-architecture-component
choose-architecture-alternative
set-architecture-component-role
add-architecture-component
reanalyze-premise
```

Envelope:

```json
{
  "workspace_id": "workspace-1",
  "expected_session_version": 3,
  "command_id": "client-generated-idempotency-key",
  "payload": {
    "component_id": "...",
    "rationale": "..."
  }
}
```

No `accept-story-lens`, `move-story-lens`, or `pin-story-lens` narrative
command exists.

### Transition into Story Direction

```text
premise
-> NarrativeArchitectureAnalysis
-> Story Lens overview
-> optional component refinement
-> continue-architecture
-> Story Discovery directions
-> explicit direction selection
-> explicit Story Direction acceptance
```

`continue-architecture` is a transition to Discovery, not acceptance of the
lens set.

## 2. Persistence and operational data model

### Narrative persistence

No new narrative persistence schema is introduced.

Existing durable authority remains:

```text
SessionEnvelope.architecture_analysis
SessionEnvelope.working_composition
SessionEnvelope.discovery_recommendation
accepted_milestones
command receipts
```

This means lens projection can always be rebuilt from durable state.

### Presentation preference persistence

Card ordering is intentionally browser-local:

```json
{
  "schema_version": 1,
  "order": [
    "story_engine",
    "common_tropes",
    "structural_shape",
    "aesthetic_framing",
    "reader_experience"
  ]
}
```

Storage key:

```text
auteur.beginner.story-lenses.v1:{workspace_id}
```

Layout corruption, unavailable storage, or quota errors fall back to the
server-provided default order and never block story work.

### Operational diagnostics

Do not introduce click counts, engagement scores, "creativity scores", or
conversion-style vanity metrics.

`StoryLensDiagnostics` exposes only decision-actionable state:

- whether rich/provider or deterministic fallback analysis produced the lenses;
- whether the analysis is stale;
- active versus suppressed component counts;
- count of explicit author adjustments;
- which lenses remain unestablished;
- which lenses need attention because they are stale, absent, or contain
  uncertainty.

These signals answer operational questions such as:

```text
Did the provider degrade?
Is the first screen stale?
Which story dimensions lack evidence?
Has the author actually changed the interpretation?
```

They do not claim whether the user liked the screen or whether the story is
good.

## 3. Full workflow progression

### Scenario A — Rich interpretation

```text
premise
-> provider architecture analysis
-> five Story Lenses
-> direct evidence/detail inspection
-> optional refinement
-> regenerated lens projection
-> Discovery
```

### Scenario B — Deterministic/no-provider fallback

```text
premise
-> bounded explicit-signal analyzer
-> evidence-backed lenses where supported
-> "Not established yet" where unsupported
-> structural/reader lenses synthesized only from recognized engine/genre basis
-> Discovery fallback
```

No missing lens is filled with invented certainty.

### Scenario C — Author confirms or changes a direct lens

```text
open lens inspector
-> existing architecture-component command
-> optimistic version check + idempotent receipt
-> durable architecture analysis update
-> working composition refresh
-> prior Discovery recommendation invalidated when material
-> Story Lenses rebuilt
```

No canonical milestone is created.

### Scenario D — Presentation composition

```text
move lens card
-> browser validates current lens IDs
-> local layout preference changes
-> screen rerenders
-> session_version unchanged
-> no HTTP mutation
```

### Scenario E — Premise reanalysis

```text
premise edit
-> reanalyze-premise
-> existing author adjustments reconciled by stable semantic component match
-> Story Lenses rebuilt from new analysis
-> stale/invalid Discovery state cleared
```

### Scenario F — Continue to Story Direction

```text
Story Lens overview
-> continue-architecture
-> multiple Story Directions
-> author selects one
-> explicit accept-direction
```

The interpretation screen remains explanatory; Story Direction is the first
explicit milestone in this sequence.

## 4. Fault tolerance and confound defenses

### Network loss

A failed refinement request leaves the current browser projection visible with
an error message. The client does not optimistically mutate narrative state.

### Duplicate/retried requests

Existing command receipts make architecture refinements idempotent. Replaying
the same command ID returns the durable result rather than applying the
adjustment twice.

### Concurrent tabs / stale client

Every mutation carries `expected_session_version`. A version mismatch returns
409 and preserves the newer durable session.

### Partial write / process interruption

Architecture mutations reuse the existing atomic session store and command
receipt recovery behavior. Story Lenses add no second persistence phase that can
fall out of sync.

### Provider/environment failure

The resilient analyzer falls back to deterministic premise signals. Diagnostics
record `source_mode=deterministic_fallback`; missing dimensions remain explicit
rather than being attributed to author error.

### Local layout-storage failure

Malformed JSON, unavailable local storage, or persistence failure returns the
default server lens order. This is presentation failure only.

### Boundary isolation

```text
lens inference != canon
author-confirmed lens component != StoryIdentity acceptance
layout order != story state
structural shape != Whole-Story Structure
reader-experience projection != accepted TargetExperience
continue-architecture != accept direction
```

---

# Stage 3 — Implemented vertical stack

## Domain / projection

- `src/auteur/beginner/story_lenses.py`
- `src/auteur/beginner/architecture_projection.py`
- `src/auteur/beginner/__init__.py`

## User interface

- `src/auteur/beginner/browser/index.html`
- `src/auteur/beginner/browser/app.js`
- `src/auteur/beginner/browser/styles.css`

The browser renders an anchor Story Engine card plus a reorderable Story Lens
grid. Any lens opens the existing right-hand inspector. Direct lenses expose
Keep/confirm, Reduce/remove, Restore, Rename, and bounded alternative actions
through existing commands. Derived Structural Shape and Reader Experience
lenses explicitly route refinement back through their source lenses.

## Verification

- `tests/test_beginner_story_lenses.py`
  - complete five-lens contract;
  - honest unknowns;
  - provider vs deterministic fallback diagnostics;
  - author-confirmed/modified states;
  - stale analysis handling;
  - idempotent noncanonical refinement and Discovery invalidation.
- `tests/test_beginner_workspace_browser.py`
  - composable layout wiring;
  - local-only layout persistence;
  - inspector/refinement command reuse;
  - no parallel Story Lens mutation authority.
- `tests/test_beginner_synthetic_walkthrough_claims.py`
  - real no-provider server;
  - first-screen lens set before Discovery;
  - common tropes, structural shape, reader experience, and honest missing
    aesthetic framing;
  - no canonical refs before the explicit Story Direction transition;
  - continued end-to-end journey through accepted Structure and outline
    continuation.

## Claim boundary

This implementation establishes repository-level functional behavior and
synthetic workflow evidence.

It does **not** claim:

- human preference for this layout;
- universal beginner comprehension;
- literary quality;
- that every premise admits one structural pattern;
- that Story Lenses are canonical story state;
- release qualification.

External human usability testing remains post-construction as explicitly
directed by the owner.
