# Narrative Architecture Visual Explanation — Product Design Specification

**Decision date:** 2026-10-12  
**Status:** Owner endorsed exploratory direction; no winner selected, no production implementation authorized by this document.  
**Scope:** Auteur Living Story Studio / Narrative Architecture information design.  
**Evidence:** Six owner-provided screenshots (2026-10-12), existing graph/facets/timeline in draft PRs #387–#392, and existing genre/data contracts on main.

## 1. Problem and product outcome

The latest interface improves information access, navigation, color and phase summaries, yet fails to explain narrative meaning proportionally. Genres, Tropes and Structure remain primarily a long inventory beside a dimmed version of the same dense graph. The viewport has a crowded upper node cluster, repeated navigation/legend/status, unused lower canvas, and a persistent mostly-empty inspector. The screenshot evidence supports these layout and comprehension hypotheses, not claims about measured user failure.

**Goal:** An author can answer what a genre generally promises, what its convention does, which parts this story adopts/adapts/creates, and how a story-specific mechanism aims to produce its effects—without reading a database dump or losing the spatial Overview.

**Product identity:** The author's particular story remains the hero. Reusable genre knowledge is an explanatory reference layer, not the main narrative authority or a prescribed recipe.

## 2. Authorized design choices

1. Preserve graph-first **Overview** for relationships and spatial construction; do not force the identical graph to be the hero of every explanatory perspective.
2. Explore three materially different candidates with **the same story fixtures**: (A) Genre Anatomy, (B) Convention vs. Invention, (C) Narrative Mechanism Map. Existing compact Timeline/Genre Rhythm is a complementary mode, not a fourth mandatory prototype.
3. In Genres, prefer a diagram of audience promise, engine, characteristic conflicts, rhythm and payoff. In Tropes, show convention/variant plus narrative function. In Structure, show how pressure, choices, changes and intended experience connect.
4. Keep the current graph accessible in one action. Hide inactive details; reveal the inspector when a selected item warrants it rather than reserving an empty column.
5. Use readable text, shapes and relation verbs alongside restrained color; preserve keyboard and narrow-screen paths.
6. Do not turn illustrative prototype judgments into verified audience consensus or required genre truths.

## 3. Two independent semantic axes

**Genre relationship:** Pack-backed hard constraint / strong default / common pattern / optional technique / intentional subversion point / boundary warning, where actually defined. For legacy genre contracts, preserve source labels (e.g. required_tropes) without silently promoting them to universal law. For missing or uncertain knowledge, show "inferred", "not classified", or "no applicable pack".

**Story treatment:** proposed adoption / proposed adaptation / proposed story-specific mechanism / proposed subversion / unresolved. These describe the **proposal's** suggested function, not an author-accepted choice. One story element may relate differently to multiple genres.

**Separate metadata:** source kind and exact locator; genre ID and pack/version/hash when available; explicit premise vs curated match vs model inference vs author-added; certainty; freshness; canonical authority. "Pack knowledge", "proposed recommendation", "author acceptance" and "compiled structure" must remain distinct.

## 4. Source and classification policy

- Reuse src/auteur/genre_packs/models.py, the versioned Erotic Fiction Genre Pack, legacy src/auteur/genres/data/*.yaml, and src/auteur/story_design_packs/models.py rather than defining a rival genre ontology.
- Reuse actual candidate/genre-contract/phase IDs and source-local field paths. A trope_functions phrase without an actual stable shared ID stays source-scoped.
- At present the versioned built-in collection includes erotic_fiction; Progression Fantasy and Heroic Fantasy do **not** have an equivalent verified versioned pack. Do not claim pack-backed conventions for them in the pilot.
- **Not documented** is not **not expected**, **forbidden**, or **original**. Silence or absent pack coverage cannot prove negative genre expectations or literary novelty; an exclusion requires explicit sourced evidence. "Story-specific" means distinctive within this proposal, not unprecedented in fiction.
- Epic Fantasy's legacy contract contains tropes listed as "required"; treat this as contract data with provenance and contestable defaults, not as a literary universal.
- A mechanism arrow may express an intended or hypothesized narrative function, not a proven psychological effect. No connecting edges purely from word similarity.
- No new canonical semantic layer, accepted story store, automatic genre obligation, or external provider invocation is needed for the discovery prototype.

## 5. Common fixture scenarios

**P — Paladin progression fantasy:** The screenshot's premise and labels, including Progression Fantasy / Heroic Fantasy / Epic Fantasy, Challenge–Effort–Growth, Earned Breakthrough, Generosity that Creates Capacity, Ethical Commitment, and Joy. Reconstructed items are clearly marked as illustrative when exact IDs/source packets are unavailable. Progression/Heroic genre morphology is hypothesis-backed until curated pack knowledge exists.

**H — Long-form genre transition:** Ground the structure in the existing tests/test_beginner_studio_architecture.py example of wonder, mystery, horror and parallel intervals. Extend only as an explicitly synthetic usability fixture if needed. This scenario challenges overlap, conflicting genre expectations, density, long text and unknown scope.

**C — Coverage/mismatch probes:** At least one missing pack, an ambiguous multiple-genre trope, a disputed legacy "required" trope, an absent causal link and a replaced/stale proposal.

All candidates must use the **same** fixture inputs, text labels, reading order and navigation tasks; variant-only wording changes require documenting why.

## 6. Candidate specifications

### A — Genre Anatomy
Hero is a compact genre grammar: reader promise → engine cycle → characteristic pressures/conflicts → plausible payoffs. Nodes/edges are labeled, and each visible convention reveals evidence strength and genre source. Prefer a small explanatory loop over another full node-link graph. Risk: presenting flexible genre tendencies as a deterministic formula.

### B — Convention vs. Invention
Hero is a comparison between a genre expectation (with provenance and strength) and what the proposal does with it, followed by the distinct story mechanism. Show adoption/variation/subversion/independence as text, not solely positional styling. Risk: an overly binary impression or unsupported assertions of originality. A missing pack must remain visibly unclassified.

### C — Narrative Mechanism Map
Hero is a *bounded* directed causal/functional chain (trope or condition → action/choice/pressure → structural change → intended reader experience), explicitly labeling the relation and its evidence/uncertainty. Keep a text-equivalent path and one-hop drilldown. Risk: chains that make conjectural causation look established.

## 7. Evaluation and decision

Compare the current graph as baseline against A/B/C on the five tasks: locate a genre promise; distinguish a convention from a story variation; trace a trope to its structural and intended emotional function; explain a missing pack without inventing rules; return to the original focus after exploring a linked item. Add the dense hybrid/phase-shift scenario and a narrow viewport.

Record task completion, wrong inferences, navigation detours, reading burden, visually competing surfaces, and source/authority misstatements. Distinguish expert heuristic walkthroughs, coding-agent simulations, and actual author feedback. Do not call mocked-DOM or source tests real browser research.

**Selection:** Choose one candidate, a bounded combination, or no change using evidence. If none clearly beats the baseline on semantic understanding without material clutter/authority regression, stop and refine the problem instead of advancing a preferred rendering by default.

## 8. Boundaries for eventual integration

Only **after** choosing an explanatory grammar, create a separate integration plan against the then-current Studio branch. Keep Overview and Story Realization intact, add perspective-specific visual content from read-only projections, preserve navigation/reopen/source identity, and test browser/keyboard/mobile/persistence. Consider pilot Genre Packs for Progression/Heroic Fantasy as a separate editorial/versioned-content responsibility **only if** absent curated knowledge demonstrably prevents useful explanation.

Do not merge experimental UI into main, alter author acceptance rules, or declare the unmerged PR #392 qualified through this design exploration.
