# Auteur Long-Horizon Narrative Intelligence Campaign — State

**Mission:** Reliable long-horizon narrative intelligence for very long fiction (dozens/hundreds of Books) without reconstructing entire history per decision.

**North Star:** Preserve and reconstruct narrative meaning across story too large for working context.

## Current Product State (2026-09-02, feature/global-map-focus-productization-v1 @ 138d03c)

- **Architecture doc:** `docs/architecture/detailed-narrative-architecture-v1.md` — ACCEPTED for V1 vertical-slice implementation (human-reviewed). 5 semantic layers + scope axis unchanged. Global Map = derived rebuildable projection; Focus = derived relevance projection; derived != canon (ADR 019).
- **Vertical slice:** IMPLEMENTED on feature branch `feature/global-map-focus-productization-v1` (c15ceff..138d03c), NOT merged to main. Proves: accepted revisioned history, current-state projection, typed CausalSupportRelation|PressureGroupRelation, Global Map snapshot, Focus via pure Map selector, revision impact propagation without silent rewrite, rebuild equivalence. P0 death tests pass; full suite retains 3 known baseline Story Discovery failures.
- **Empirical evidence:** Architecture Value V3 (`20260829-agent-native-sonnet-opus-v3`) — C (rich ledger) 13/2/0 vs B (shipped Map/Focus) 6/6/3 vs A (baseline) 6/6/3. C dominates paired P03/P05 Book-4 family; pressure grouping + causal/supporting-history trace is strongest C-over-B mechanism.
- **Productization Pilot V1:** `docs/product-validation/global-map-focus-productization-pilot-v1.md` — FROZEN SHA c60958a, author dogfood COMPLETE, disposition PARTIALLY VALIDATED. Revision safety POSITIVE; Focus decision support NEGATIVE/INSUFFICIENT.
- **Mechanical capabilities DEMONSTRATED:** accepted-history reconstruction, stable identity (ArtifactStore revisions), narrative vs revision order separation, long-range causal support, pressure grouping, Global Map rebuild, Focus derivation, semantic-impact propagation (valid/stale/suspect/contradictory), downstream preservation.

## Author-Validated vs Mechanical

- **Mechanically validated:** history, currentness, grouping, Map/Focus mechanics, revision impact (via V3 + slice qualification).
- **Author-validated POSITIVE:** downstream impact without silent rewrite (pilot).
- **Author-validated NEGATIVE:** Focus surfaces facts but fails to explain narrative context that makes them relevant to current decision. Provenance without YAML also insufficient.
- **Not yet author-validated:** contextual explanation value; scale beyond ~10 entries.

## Primary Product Failure (Pilot Friction)

> Focus identified relevant facts and relationships, but did not explain the narrative context that makes them relevant to the current creative decision.

Example insufficient: `operative_network.integration_state = peer_ambivalence_integrated` → "Book 9 explicitly references this fact." Desired: fact → narrative meaning → connection to decision → consequence if ignored/changed.

Required shape (pilot): `story fact → narrative meaning → connection to current decision → consequence`

## Highest-Leverage Capability Boundary

**Horizon A — Contextual, author-readable relevance explanation for Focus and revision impact.**

- Affects: `why_matters_now` generation in `repeated_map_focus.py`, `vertical_slice_models.py` entry fields, and `vertical_slice_formatters.py` author-facing rendering.
- Current limitation: `why_matters_now` templates are mechanical ("Accepted fact X sets current Y to Z but planning does not reference it") and provenance is ID-centric. No narrative-meaning field exists.
- Why it matters: blocks Focus from providing value even when selection is correct; pilot chose this as single next capability; extraction gate remains NO.

## Open Representation Questions (Horizon B deferred unless needed for explanation)

- Minimal ontology enrichment needed to support narrative meaning without new author bookkeeping burden (STORE vs DERIVE vs INTERPRET).
- Whether pressure-group explanation needs richer member roles/narrative gloss vs reusing existing commitment statements.

## Current / Next Warranted Responsibility

**JUST COMPLETED:** Bounded contextual-explanation enrichment (see above). Next warranted responsibility to select at next loop iteration:

- Candidate next boundaries: (a) author re-dogfood of enriched Focus on same pilot project to validate decision-support improvement; (b) merge vertical slice + explanation to main after re-dogfood positive; (c) scale stress case to 20+ Books if re-dogfood shows residual information-load issues.
- Decision-changing uncertainty for next: Does enriched explanation actually change author decision-support judgment from NEGATIVE to POSITIVE, or does deeper narrative ontology still required?
- Recommended next: bounded re-dogfood evaluation on `feature/global-map-focus-productization-v1 @ a42be9f` with same pilot protocol (single project, author observes Focus before/after).

## Previously Selected Responsibility (completed)

Bounded contextual-relevance explanation research → prototype → minimal implementation for Focus.

- **Decision supported:** What minimal explanation enrichment makes Focus decision-useful without speculative ontology or manual database administration?
- **Resolution:** Narrative meaning derivable from existing `transition.explanation` + commitment statements without new author bookkeeping. Added derived `explanation` propagation through `GlobalMapEntry` (not new canonical store) and enriched `why_matters_now` / connection summaries.
- **Evidence type:** ARCHITECTURE + PRODUCT-VALUE (repo evidence + fixture probe + formatter demo).
- **Alternatives considered:** (1) Merge slice to main first, (2) scale, (3) universal ontology — deferred.
- **Evidence produced:** Commit a42be9f; formatter demo shows `archive-protected — The treaty protects the admitting custodian — it matters now because its narrative meaning directly informs this decision; if ignored, the decision loses its historical grounding.`

## Completed Campaign Responsibilities

1. 2026-09-02 — Campaign diagnosis + state establishment (this file).
2. 2026-09-02 — Bounded contextual-explanation enrichment for Focus (commit a42be9f): enriched `why_matters_now` with narrative meaning from `transition.explanation` (fact→meaning→connection→consequence), added `GlobalMapEntry.explanation`, enriched `FocusConnection` causal summaries, enriched pressure-group explanations; all vertical-slice tests pass (127), `scripts/check.py --skip-pytest` passes.

## Ratified Decisions

- ADR 019: Global Map / Focus / relation index are derived, rebuildable, non-canonical.
- Pilot disposition: extraction gate NO; next capability is contextual explanation (not extraction/ontology/scaling).
- Architecture V1 human-reviewed for slice implementation; implementation frozen at c60958a for pilot evidence.

## Deferred / Not Warranted Now

- Automatic story-instance relationship extraction (gate NO).
- Universal graph ontology / graph DB.
- Scaling to 50+/100+ entries with budgeted selector (P2).
- Generalized commitment lifecycle beyond slice.
- LLM-assisted interpretation.

## Owner Decisions Required

- None at this state. Next owner checkpoint after explanation prototype qualification.

## Campaign Acceptance Status

NOT COMPLETE. See 18 acceptance conditions in campaign mission — mechanical history/revision safety partially satisfied; contextual explanation (conditions 9,10,13) remains NEGATIVE; ontology remains minimal-by-design; real-author value for long-horizon capability is PARTIALLY VALIDATED (revision safety positive, Focus explanation negative).

## Fresh-Context Reconstruction Test

Next agent should read this file + `docs/product-validation/global-map-focus-productization-pilot-v1.md` + `docs/architecture/detailed-narrative-architecture-v1.md` to reconstruct mission, demonstrated vs hypothesized, and why contextual explanation is next.
