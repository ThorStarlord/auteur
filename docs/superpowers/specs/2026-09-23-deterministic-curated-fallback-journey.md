# Deterministic Curated Fallback Journey

Status: **APPROVED 2026-09-23 — implementation in progress**

Date: 2026-09-23

Amends: `docs/superpowers/specs/2026-09-19-premise-to-narrative-architecture-beginner-flow.md`
("Provider availability and fallback", and the non-goals on universal taxonomy).

Trigger: an agent-observed walkthrough at `d7966dc3` found that the documented
default launch (`npm start`, no `--provider`) produces a fallback-only
experience: the architecture interpretation is a shallow explicit-signal
fallback, Story Discovery is `unavailable` ("No reasoning provider configured"),
and the journey dead-ends at the architecture → Discovery seam. See
`docs/engineering/beginner-workspace-qualification.md`, "2026-09-23
architecture-first walkthrough at main HEAD".

## Purpose

Make the no-provider path a **usable, honest, bounded curated journey** from
premise through accepted Whole-Story Structure, without fabricating rich
analysis and without building a universal genre/trope taxonomy.

## Amendment to the fallback policy

The approved spec currently says:

> The fallback must not fabricate rich analysis. A provider failure must not
> silently degrade into confident unsupported interpretation.

This amendment keeps that intent but replaces the effective dead end with an
explicit **Deterministic Curated Mode**:

- Auteur may reflect explicit premise terms, deterministic pack/profile matches,
  and **bounded curated direction, identity, and structure templates**.
- Every surface and artifact produced in this mode must be labeled as
  deterministic/curated and noncanonical.
- Derivation is limited to `premise-explicit` and `curated-match`. Deterministic
  Mode must never claim `model-inference`.
- If no curated knowledge matches the premise, Auteur says so and does not
  invent an interpretation.
- Bounded curated templates are permitted. A universal taxonomy of every genre
  or trope remains out of scope (spec non-goal unchanged).

## Design

### 1. Premise-sensitive deterministic architecture

Owner: `DeterministicArchitectureAnalyzer` (`architecture_analysis.py`).

- Replace the blind pin `if mystery_signal is not None or mystery_source is not None`
  (line 271). Emit Mystery only on a real premise signal or an explicit
  configured genre.
- Introduce a bounded signal catalog. Each entry maps premise keywords to one or
  more architecture components plus a candidate engine. Starting set:
  mystery/investigation, superhero, relationship betrayal, secret identity
  (existing), plus romance, thriller/suspense, horror, speculative/fantasy.
- Derive the **primary** genre and engine from the highest-priority detected
  group instead of hardcoding "Investigation and revelation".
- No-signal state: zero components, honest summary and `availability_note`;
  Discovery still offers generic directions (below).

### 2. Deterministic Discovery

Owner: new `DeterministicDiscoveryRecommender` (`discovery.py`), wired into
`default_runtime_dependencies()` (`server.py:59`).

- Produce up to three **causally distinct** directions from the active
  components by selecting distinct engine emphases:
  - engine-led (primary narrative engine);
  - relationship-led (`relationship_dynamic`, when present);
  - identity/world-led (`trope_family`/`setting_world`, when present);
  - pad with generic engine variants (external investigation vs internal moral
    dilemma) when fewer facets exist.
- Each `DiscoveryDirection` carries a synthesized `StoryIdentity` candidate:
  - `story_type.genre` mapped to a canonical `Genre` (mystery→MYSTERY,
    romance→ROMANCE, thriller→THRILLER, horror→HORROR, else OTHER);
  - `target_experience` and `central_engine` from curated engine→template
    entries specialized with the architecture labels;
  - `title` and `core_answer` from templates.
- Status `NEEDS_AUTHOR_CHOICE`; no manufactured recommendation (decision point
  1). Rationale states the direction is deterministic/curated and derived from
  the working architecture.

### 3. Story Identity

- Reuse the existing candidate/accept authority boundary unchanged.
- A synthesized deterministic candidate must pass `StoryIdentity.validate_identity()`
  with no ERROR diagnostics; enforced by test.

### 4. Structure

Owner: `structure_inventory_for` (`decision_inventory.py`).

- When Mystery is material, keep the existing Mystery Structure cards.
- Otherwise, return a **bounded generic inventory** (~3 cards) from a new
  curated adapter: escalation pattern, reversal/revelation placement, resolution
  shape. The adapter registers an evidence source so `QualificationCard`
  evidence contracts hold.
- This is a bounded curated set, not a per-genre taxonomy.

### 5. Working Composition / mapping

- Ensure deterministic architecture components project into WorkingComposition
  dimensions so mapping and promotion work for non-Mystery premises. Currently
  dimensions appear pack-driven; this seam needs investigation (decision point 3).

## Decision points for approval

1. Discovery posture: `NEEDS_AUTHOR_CHOICE` with no recommendation
   (recommended) vs `READY` with a deterministic recommendation.
2. Catalog breadth: minimal (existing groups + 4 generic) vs a wider set.
3. Composition projection: include in this work package (recommended, required
   for non-Mystery promotion) vs defer to a follow-up.

## Staging (each stage TDD, verified before the next)

```text
1. deterministic architecture (premise-sensitive)
2. deterministic Discovery + Identity candidates
3. generic Structure inventory
4. composition/mapping projection for non-Mystery
5. rerun the same agent walkthrough A-H; record
```

### Implementation progress

- Stage 1 — DONE. `DeterministicArchitectureAnalyzer` is premise-sensitive: the
  blind Mystery pin is removed, a bounded signal catalog (mystery, thriller,
  horror, romance, superhero, speculative) derives the primary genre and engine
  from real premise signals, and the no-signal state is honest. Tests:
  `tests/test_beginner_architecture_analysis.py` (15 passed).
- Stage 2 — DONE. `DeterministicDiscoveryRecommender` produces up to three
  causally distinct directions with synthesized `StoryIdentity` candidates,
  `NEEDS_AUTHOR_CHOICE`, no manufactured recommendation; wired into
  `default_runtime_dependencies()`. Tests: `tests/test_beginner_discovery.py`
  (6 passed); server default-path test added.
- Stage 3 — PENDING. Requires a bounded generic Structure inventory plus
  `guidance.py` routing: `_option_impacts`, `_why_this_matters`, and
  `guidance_for` all key off Mystery card IDs today, and `_current_digest`
  (application) vs `guidance_for` tutor-session fingerprints must stay
  consistent for staleness. This is a deeper routing refactor than the bounded
  amendment assumed.
- Stage 4 — PENDING. `mapping.py::_candidate_for` hardcodes
  `PRIMARY_ENGINE -> story_type.genre = "mystery"`; needs a per-engine genre
  candidate checked against the mapping vocabulary.
- Stage 5 — DONE for Mystery-material premises. Verified end-to-end against the
  running default server (no provider): a superhero/mystery/betrayal premise
  produced a premise-sensitive interpretation, three distinct deterministic
  directions, accepted Story Direction and Story Identity, the curated Mystery
  Structure decisions, and accepted Whole-Story Structure (`primary_surface:
  complete`). Non-Mystery-only premises still lack a Structure inventory
  (Stage 3).

### Discovered integration gap (latent, not fixed here)

`_composition_preview` computes a composition tension for the projection, but
`acknowledge_tension` reads `session.working_composition`, so a tension shown in
the projection can be unacknowledgeable and block Identity acceptance. Stage 2
avoids the common case by having the synthesized candidate integrate the
relationship dimension's emotional promise; the underlying persistence gap
remains and should be addressed when Stage 3/4 touch this area.


### Known baseline failures (not caused by this work)

- `tests/test_beginner_workspace_mapping.py::test_preview_links_semantic_change_to_mapping_and_reports_impact`
  (asserts `story_type.genre`, code emits `story_type`) — fails identically on
  the unmodified checkout.
- `tests/test_beginner_workspace_server.py::test_root_serves_beginner_browser_entrypoint`
  (Windows `mimetypes` returns `application/javascript`) — fails identically on
  the unmodified checkout.


## Non-goals

- No new semantic layer; no canon from deterministic artifacts.
- No universal genre/trope taxonomy.
- No LLM call added to deterministic analysis.
- Does not change the provider-backed rich path.
