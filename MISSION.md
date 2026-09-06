# Mission

**Derived from:** `docs/PRD.md` - vendored 2026-09-04, from the guidance-layer interview.

## What this is

Auteur is an opinionated narrative-engine toolkit for long-form fiction: a
literary compiler that turns a raw premise into multiple plausible story
engines, recommends the strongest direction with explicit tradeoffs, and keeps
canonical story state under the author's control. Deterministic code owns
schemas, project files, validation, artifacts, and retry rails; LLM calls own
creative planning, prose, and critique. The whole-story structure engine comes
first; chapter drafting comes second.

## Users

Creative beginners using guided authoring with progressive disclosure (the
intended default experience), and advanced authors and engineers using the
Python CLI and YAML/JSON/Markdown artifacts directly.

## In scope

Story discovery and acceptance; opinionated story identity; genre packs,
overrides, and subgenre modifiers; structure generation and diagnosis;
deterministic diagnostics with repair proposals; state management across the
semantic layers and scopes; outline compiling; chapter contracts and TDD
drafting; interactive genre pipelines on the neutral runtime; dual LLM
provider support.

## Out of scope, forever

- **No auto-accept.** A recommendation never becomes canonical state without an
  explicit author action. No request may add an auto-accept mode.
- **No cloud, multi-author, or real-time collaboration service.** Auteur is
  single-author and local-first.
- **No auto-publishing** to external platforms (Kindle, WebNovel, RoyalRoad,
  or any other).
- **No native GUI app.** The browser phase visualization stays; a desktop app
  does not appear.
- **No payments or subscription billing.** *[owner-confirmed 2026-09-04]*
- **No scraping or importing third-party story content.** *[owner-confirmed
  2026-09-04]*

## Hard invariants - no request may argue these away

1. **Author authority.** Any operation modifying StoryIdentity requires an
   explicit author action, shows the proposed change, persists atomically,
   retains provenance and rationale, and leaves prior state unchanged on
   failure.
2. **No author data loss.** A failed write never corrupts or half-destroys the
   prior state.
3. **Deterministic validation.** Same input, same choices, same verdict -
   always.
4. **No special cases in infrastructure.** No `if genre == X` in the neutral
   genre-pipeline runtime; new genres need only templates, validation, and
   identity transformation.
5. **Backwards compatibility.** No breaking changes to existing Series, Book,
   or Story Identity layers.

## Permanently human

Feel and prose quality; genre wisdom beyond the curated rules; whether a story
"works"; readability of artifacts for a newcomer; creative taste of every kind.
A green gate never means "the product is good" - only that the invariants and
the journey survived. The factory owns the compiler, not the literature.

## The journey - checked on every change

Run story discovery on a fixture premise -> see multiple engines with honest
tradeoffs -> accept one -> `story_identity.yaml` is written - and canonical
state was unchanged at every step before acceptance.

**APP proof:** a known CLI command prints a specific, greppable line. A process
that starts, hangs, and returns zero must be indistinguishable from nothing.
