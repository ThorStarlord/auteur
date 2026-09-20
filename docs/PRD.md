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
real author workflow
-> first material friction
-> classify the owning layer
-> smallest useful intervention
-> verify in the workflow
```

A roadmap candidate is not implementation authority. New product construction
should be selected from observed author need rather than from architectural
novelty alone.

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

## Current selection gate

The next product package is intentionally evidence-gated by issue #249's
real-author premise-to-Chapter-2 journey. Preserve the first material friction
separately from any proposed fix, classify it as UX/presentation, workflow,
craft knowledge, domain model, or infrastructure, and select the smallest
intervention that addresses the observed problem.

Until that evidence exists, roadmap candidates such as broader Author Attention,
Current Author Intent, Existing-Manuscript Reverse Engineering, richer
Book-level reasoning, and Episode 1 Direction remain candidates rather than
selected implementation work.
