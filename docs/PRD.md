# PRD: Auteur narrative-engine toolkit

> **Provenance:** seeded 2026-09-04 from `README.md`, `CONTEXT.md`, and the
> guidance-layer interview (Rounds 1-3). This is a *derived seed*, not an
> original product document - correct it directly; the factory rereads it
> whenever MISSION.md is regenerated.

## Problem

Creative beginners with a raw story idea face an infinite blank page. Turning a
premise into a working long-form story requires structural craft knowledge most
beginners do not have, and existing tools either do the writing for them or offer
no opinionated guidance at all.

## Users

- **Primary:** creative beginners using guided authoring with progressive
  disclosure - they should reach the first valuable outcome without editing YAML,
  understanding Pydantic, or touching a CLI.
- **Secondary:** advanced authors and engineers who use the Python CLI, library,
  and YAML/JSON/Markdown artifacts directly.

## MVP scope (capability areas)

1. Story Discovery - multiple plausible StoryIdentity interpretations, bounded
   advisory judge, recommendation with tradeoffs, author acceptance
2. Opinionated Story Identity - validation, seeding, rationale, rejected
   directions, author overrides
3. Genre Packs - applicability, recommendations, honest `no_applicable_pack`,
   genre-aware diagnostics, overrides, subgenre modifiers
4. Structure Generation (top-down) and Structure Diagnosis (bottom-up)
5. Deterministic diagnostics (20+ rules) with the full proposal lifecycle
6. State management across the five semantic layers and five scopes
7. Outline compiling (cartographer)
8. Chapter contracts and TDD drafting (plan - draft - critique - iterate)
9. Interactive genre pipelines (netorare, mystery, gentlefemdom) on the neutral
   runtime
10. Dual LLM provider support (Anthropic, OpenAI) with retry and model routing

## Non-goals

No auto-acceptance of recommendations. No cloud/multi-author/collaboration
service. No auto-publishing to external platforms. No native GUI app. No
payments or subscription billing. No scraping or importing third-party story
content.

## Success metrics

A discovery run on a fixture premise returns multiple engines with honest
tradeoffs; canonical story state is never mutated before explicit author
acceptance; validation is deterministic; a failed write leaves prior state
byte-identical.

## Open questions

TBD: escalation channel command (decided at trigger phase); whether work
arrives as local `issues/` files or GitHub issues (start local, revisit at
Phase 4).
