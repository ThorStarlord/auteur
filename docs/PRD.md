# PRD: Auteur narrative-engine toolkit

> **Provenance:** seeded 2026-09-04 from `README.md`, `CONTEXT.md`, and the
> guidance-layer interview (Rounds 1-3), then reconciled 2026-09-20 against the
> contemporary integrated product. This remains a derived product contract:
> correct it directly when product intent changes; the factory rereads it when
> `MISSION.md` is regenerated.

## Problem

Creative beginners with a raw story idea face an infinite blank page. Turning a
premise into a working long-form story requires structural craft knowledge most
beginners do not have, and existing tools either do the writing for them or offer
no opinionated guidance at all.

Auteur should help an author make the next bounded narrative decision while
keeping accepted story state under explicit author control.

## Users

- **Primary:** creative beginners using guided authoring with progressive
  disclosure - they should reach valuable narrative decisions without editing
  YAML, understanding Pydantic, or depending on the CLI.
- **Secondary:** advanced authors and engineers who use the Python CLI, library,
  and YAML/JSON/Markdown artifacts directly.

## Current product scope

1. **Story Discovery and StoryIdentity** - multiple plausible interpretations,
   bounded advisory recommendation with tradeoffs, explicit author acceptance,
   validation, rationale, rejected directions, and author overrides.
2. **Genre knowledge** - Genre Packs, applicability, honest
   `no_applicable_pack`, diagnostics, overrides, subgenre modifiers, and
   interactive genre pipelines on the neutral runtime.
3. **Whole-story Structure** - top-down generation, bottom-up diagnosis,
   deterministic diagnostics, noncanonical proposals, explicit proposal
   selection, revision planning/validation, derived change preview, and
   confirmed application through the owning Structure workflow.
4. **Guided narrative decisions** - Story Design Packs / Tutor, Decision Cards,
   explanation and tradeoffs, advisory choices, derived authority handoffs,
   source-currentness checks, bounded reassessment, and Author Attention.
5. **Beginner story-development continuation** - accepted foundation to
   whole-story outline, Chapter planning, scene planning, drafting handoff,
   post-draft review, explicit existing-owner Chapter acceptance, contextual
   Chapter N+1 planning, and read-only whole-book/reconciliation orientation.
6. **State, authority, and provenance** - deterministic state management across
   the five semantic layers and five scopes, atomic authority transitions,
   currentness checks, accepted-history reconstruction, and failure-safe
   persistence.
7. **Book reconciliation** - external Book inspection/routing, deterministic
   application planning, candidate decisions, accepted-source tracking,
   recomposition, comparison, explicit Book acceptance, and administrative
   completion while preserving authority boundaries.
8. **Series / long-horizon support** - accepted-history/current-state
   reconstruction, continuity support, and derived Global Map/Focus projections
   without creating a second canon.
9. **Outline and drafting** - Cartographer outline compilation, chapter
   contracts, Bard/Critics drafting, retry, critique, and explicit acceptance.
10. **Runtime and provider support** - deterministic repository/runtime
    infrastructure plus Anthropic/OpenAI provider support, retry, and model
    routing.

## Product phase

The primary architecture and guided-author loop are established. Contemporary
development should default to product integration, simplification,
discoverability, maintainability, and qualification before introducing new
semantic concepts.

For product evolution, prefer:

```text
bounded workflow evidence
-> cheap scripted simulation when it can answer the question
-> first concrete friction
-> classify the owning layer
-> smallest useful intervention
-> verify in the workflow
-> real-author validation when the claim or consequence requires it
```

A roadmap candidate is not implementation authority. New product construction
should be selected from concrete workflow evidence rather than from architectural
novelty alone. Scripted simulation is admissible for provisional, reversible
product work when it exercises the real workflow and preserves authority
boundaries; it is not evidence that real authors find the result useful or
understandable.

## Non-goals

No auto-acceptance of recommendations. No cloud/multi-author/collaboration
service. No auto-publishing to external platforms. No native GUI app. No
payments or subscription billing. No scraping or importing third-party story
content.

## Success criteria

- A premise can move through discovery into multiple plausible story engines
  with honest tradeoffs and explicit acceptance.
- The guided author can continue from accepted foundation through Structure,
  bounded decisions, Chapter 1 review/acceptance, and contextual Chapter 2
  planning without a parallel authority system.
- Canonical narrative state is never mutated by recommendation, projection,
  diagnosis, preview, or proposal alone.
- Authority-bearing writes are explicit, atomic, provenance-bearing, and
  failure-safe.
- Deterministic validation returns the same verdict for the same state and
  choices.
- Beginner-facing orientation makes the next safe action understandable without
  requiring knowledge of repository internals.

## Beginner Narrative Architecture and transition requirements

The architecture-first Beginner experience is a product explanation surface, not
just a classifier. It must preserve these durable requirements:

- **Explain composition, not only components.** Beginner orientation should show
  how the main narrative engine, genre/story traditions, aesthetic framing,
  major trope families, relationship/thematic dynamics, narrative structure,
  and intended reader experience affect one another in this particular story.
  A flat list of detected labels is insufficient when Auteur already has enough
  evidence to explain their relationship.
- **Keep uncertainty honest.** If the premise does not establish a dimension
  such as aesthetic framing, Auteur should say that it is not yet established
  and may invite author exploration. It must not manufacture framing, genre
  confidence, recommendations, or canonical commitments merely to fill every
  section.
- **Make authority and phase transitions obvious.** Completion state, accepted
  authority state, and the next safe action must agree. Once a milestone is
  accepted, the UI must not continue instructing the author to accept it, and
  the primary next action should be visually and semantically distinct from
  secondary exploration/help actions without relying on color alone.
- **Keep no-provider degradation product-coherent.** When rich reasoning is
  unavailable, deterministic fallback may provide bounded premise-sensitive
  interpretation, multiple plausible directions, and generic structural
  guidance. It must preserve explicit author choice and must not pretend that a
  bounded deterministic heuristic has made a creative judgment the author has
  not accepted.
- **Make action hierarchy a backend product contract.** A workspace may expose
  many technically valid actions, but beginner presentation should receive one
  deterministic primary next action from the application projection. Raw
  `available_actions` remain a compatibility/debug surface; browser code must
  not infer product priority from list ordering. Projecting an action never
  executes it or changes its authority.

These requirements do not create a new semantic layer or a universal narrative
taxonomy. They constrain how existing Narrative Architecture, Discovery,
Identity, Structure, and authority boundaries are presented and connected.

### Story Lens first-screen contract

After premise submission, the default Beginner surface is a **Story Architecture
Overview** built from composable, derived Story Lenses rather than a
questionnaire or a flat list of architecture facets.

The default lens set is:

- **Main story engine** — the recurring machinery generating story pressure;
- **Emotional & aesthetic framing** — how events are expected to feel;
- **Common tropes** — recurring situations and expectations;
- **Structural shape** — a bounded inferred story pattern, explicitly not the
  later accepted Whole-Story Structure;
- **Reader experience** — the expected emotional/cognitive progression.

Each lens supports a summary view and a detailed inspector. Direct lenses refine
the existing Narrative Architecture components through existing versioned,
idempotent commands; synthesized lenses route refinement back to their source
lenses rather than creating shadow state.

Card ordering is a presentation preference only. Reordering Story Lenses must
not mutate `SessionEnvelope`, create a story command, change `session_version`,
or cross an authority boundary. Missing or uncertain lenses must remain
explicitly unestablished rather than being filled with invented certainty.

The transition remains:

```text
premise
-> derived Story Lens overview
-> optional interpretation refinement
-> Story Discovery
-> explicit Story Direction selection
-> explicit Story Direction acceptance
```

The implementation contract and failure/recovery rules live in
`docs/design/2026-09-24-story-lens-first-screen-ux.md`.

## Current product-selection rule

Issue #249's simulation-first premise-to-Chapter-2 evidence remains valid
mechanical/workflow evidence. A later 2026-09-23 human Beginner walkthrough
provided claim-appropriate experiential evidence and selected a bounded
**Beginner Narrative-Architecture Coherence / deterministic fallback** package
rather than a new roadmap feature family.

The active package addresses concrete friction in no-provider interpretation and
Discovery, generic non-Mystery Structure, per-engine Identity mapping,
projection/mutation coherence, phase-transition clarity, and integrated
Narrative Architecture explanation. The correction lives on one combined
candidate that carries both the deterministic-fallback work and the PR #283
phase-transition and explanation corrections, and that selected behavior has been
reconciled onto current `main` so it can coexist with the later post-draft
continuation, whole-book progress, Book acceptance, and authority/projection
semantics. Under explicit owner direction, this package closed on synthetic
verification (automated E2E over the real no-provider server) rather than a
second manual walkthrough. That waiver is a one-time owner decision for this
package; the durable rule below is unchanged — real-author usability still
requires human evidence and is not claimed by synthetic acceptance.

The general product-selection rule remains:

```text
claim-appropriate workflow evidence or deliberate product-lane selection
-> first concrete material friction / goal
-> classify the owning layer
-> smallest useful intervention
-> focused verification
-> human validation when the claim/consequence requires it
```

Simulation remains admissible for provisional, reversible product work when it
directly exercises the real workflow and preserves authority boundaries. Human
product evidence remains required before claiming real-author usefulness,
comprehension, relevance, confidence, preference, or subjective story quality.

The previous Beginner coherence package is closed. On 2026-09-24 the owner
explicitly selected the next bounded responsibility: the **Story Lens
first-screen UX**, defining the premise -> interpretation -> Story Direction
transition through composable Story Lenses. This is deliberate product-lane
selection rather than an automatically invented roadmap successor.

After this selected package closes, do not invent another successor merely to
continue the roadmap. `NO_CHANGE` remains valid until new evidence or explicit
product intent selects another bounded responsibility.