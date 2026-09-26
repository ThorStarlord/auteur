# System Ownership and Product Compression

**Role:** architecture/product-integration rule for keeping Auteur's internal
capability growth compatible with a simple author experience.

**Authority:** this document does not create a narrative layer, acceptance
workflow, or new source of story truth. Canonical semantic and authority rules
remain in `docs/narrative-architecture.md`, `MISSION.md`, and the owning
domain workflows.

## Why this exists

Auteur now contains substantially more internal capability than a beginner
should have to understand. The repository therefore treats **visible complexity
as a product concern distinct from internal capability depth**.

The governing direction is:

```text
internal systems may stay specialized
-> product projections compose them
-> beginner surfaces expose one coherent state
-> one primary next action is obvious
-> explanation/evidence remain available on demand
```

Do not solve product complexity by flattening distinct authority owners into one
god object. Do not solve it by exposing every subsystem to the author.

## Ownership map

| Capability family | Semantic/domain owner | Authority owner | Product projection |
| --- | --- | --- | --- |
| Narrative concepts | `narrative_ontology` | owning accepted artifact | Beginner explanation / advanced CLI |
| Story direction / identity | Story Discovery + `identity` | explicit StoryIdentity acceptance | Beginner Discovery / Identity surfaces |
| Whole-story planning | `structure`, Blueprint, Cartographer | Structure proposal/revision/acceptance workflows | Beginner Structure + continuation |
| Events and story state | `narrative_realization`, Bible/state, relations | owning Realization acceptance path | derived orientation / downstream drafting |
| Prose and manuscript | `expression`, Bard/Critics | Chapter/Book Expression acceptance | post-draft review / Book progress |
| Reusable craft knowledge | Genre Packs + Story Design Packs | none by itself | Tutor / Beginner guidance |
| Change consequences | `impact` | none by itself | explanation / attention |
| Candidate repair | `convergence` | existing owning artifact workflow | review / decision support |
| Author decisions | `decision`, `author_decisions` | explicit author choice plus owning workflow | Tutor / Author Attention |
| Review lifecycle | `review` | owning artifact acceptance command | guided review surfaces |
| Project work order | `planning` | none | dashboard / attention |
| Counterfactuals | `simulation`, `portfolio` | none until explicit promotion/owner action | advanced decision support |
| Long-horizon continuity | `series`, Universe support | existing Series/Book authorities | derived Global Map / Focus |
| Provenance and freshness | `provenance` | metadata only | blockers / explanation |
| Workflow safety | `workflow` | delegates to existing owner | safe next-action projection |
| Beginner product | `beginner` application/projections | **never a parallel authority** | primary author-facing surface |
| Dashboard / Author Attention | `ui` | read-only | cross-system orientation |
| Providers | `llm` | none | hidden infrastructure |
| Publishing | `publish` | accepted Book is prerequisite | export surface only |

If a new capability cannot identify its semantic owner, authority owner, and
product projection, that is a design warning. Creating a new subsystem is not
the default answer.

## Product-compression contract

Beginner-facing surfaces follow progressive disclosure:

```text
Level 0 — Where am I? What is the one primary next action?
Level 1 — Why does this action matter? What will it change?
Level 2 — What evidence, trade-offs, blockers, and alternatives exist?
Level 3 — Raw artifacts, advanced commands, provenance, diagnostics, internals.
```

A user may move deeper at any time. The product should not require a beginner to
start at Level 2 or Level 3.

### One primary action

A workspace can have many technically available actions while still presenting
one primary action.

The Beginner API therefore keeps two distinct surfaces:

```text
available_actions
= complete compatibility / capability set

primary_action
= deterministic product-level hierarchy over that set
```

The browser must not infer priority from `available_actions` ordering.
Presentation consumes `primary_action`; raw actions remain available for
secondary controls, advanced inspection, testing, and backwards compatibility.

A projected primary action:

- does **not** execute itself;
- does **not** grant authority;
- does **not** rank creative alternatives;
- may point to an explicit author-authority action when that is the next valid
  workflow transition;
- prefers forward workflow continuation over optional revision-entry actions;
- may be absent when no single forward action is warranted.

## Boundary rules

### 1. Product projection is not domain ownership

`beginner`, Dashboard, and Author Attention may compose status from many
systems. They do not become the canonical owner of those systems.

### 2. Cross-cutting intelligence is not canon

Impact, reasoning, planning, simulation, portfolio comparison, Tutor guidance,
maps, and attention projections remain derived/advisory unless an existing
authority workflow explicitly accepts a resulting change.

### 3. UX friction does not authorize ontology

When a capability exists but is hard to discover, explain, or sequence, repair
the product projection before inventing a new narrative concept.

Preferred diagnostic order:

```text
presentation
-> workflow connection
-> reusable craft knowledge
-> existing domain model
-> new domain concept only when the earlier layers cannot express the need
```

### 4. No parallel acceptance path

Beginner convenience may route to StoryIdentity, Structure, Chapter, Book, or
other existing acceptance owners. It must not recreate their authority in a
Beginner-specific database or mutation path.

### 5. Continuity requires executable composition

A capability is not beginner-complete merely because the backend owns it, the
projection advertises an action, or the browser renders a button. A continuity
claim requires the product path to execute through the real application/API
boundary into the existing owner.

For a projected transition, verify all of these together:

```text
projected next action
-> browser control
-> HTTP/application dispatch
-> owning workflow
-> persisted/recoverable result
-> unchanged authority boundary
```

Static string/DOM assertions are useful sentinels, but they are not sufficient
evidence for a cross-layer transition. At least one focused integration test
must execute the transition through the same dispatch surface used by the
browser whenever that boundary changes.

### 6. Preserve specialized systems internally

Decision, Review, Impact, Convergence, Planning, Simulation, Portfolio,
Commitment, and related systems model genuinely different responsibilities.
Product compression means composing them for the author, not erasing their
semantic boundaries.

## Admission check for future systems

Before adding a new top-level subsystem, answer:

1. What recurring responsibility cannot be owned by an existing system?
2. Is the problem actually presentation or workflow integration?
3. Which semantic layer/scope does the new state describe, if any?
4. Who owns authority-bearing mutation?
5. What is derived versus accepted?
6. How will a beginner encounter the capability without learning its internal
   vocabulary?
7. Does the projected action execute through the real product dispatch surface
   into the existing owner?
8. Can the capability be added behind an existing product projection instead?

If these questions do not produce clear boundaries, prefer a bounded extension
of an existing owner.

## Current application

The Beginner Narrative-Architecture Coherence package applies this contract by
moving next-action priority into the backend projection:

```text
many available actions
-> deterministic primary_action
-> browser renders one primary control
-> secondary/revision controls remain available
```

This is intentionally a small integration seam. It does not create a generic
Strategic Planner, universal workflow router, or new narrative authority.
