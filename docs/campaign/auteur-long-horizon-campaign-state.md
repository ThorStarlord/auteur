# Auteur Long-Horizon Narrative Intelligence Campaign — State

**Mission:** Reliable long-horizon narrative intelligence for very long fiction (dozens/hundreds of Books) without reconstructing entire history per decision.

**North Star:** Preserve and reconstruct narrative meaning across story too large for working context.

## Current Product State (2026-09-02, auteur/main @ 1a686f5 + feature/contextual-relevance-explanation-v1)

- **Architecture doc:** `docs/architecture/detailed-narrative-architecture-v1.md` — ACCEPTED for V1 vertical-slice implementation (human-reviewed). 5 semantic layers + scope axis unchanged. Global Map = derived rebuildable projection; Focus = derived relevance projection; derived != canon (ADR 019).
- **Vertical slice + Productization Pilot V1:** MERGED to `auteur/main @ 1a686f5`. Proves: accepted revisioned history, current-state projection, typed CausalSupportRelation|PressureGroupRelation, Global Map snapshot, Focus via pure Map selector, revision impact propagation without silent rewrite, rebuild equivalence. P0 death tests pass; full suite retains 3 known baseline Story Discovery failures. Pilot disposition remains PARTIALLY VALIDATED (revision safety POSITIVE; original Focus decision support NEGATIVE/INSUFFICIENT).
- **Contextual Relevance Explanation V1:** IMPLEMENTED on `feature/contextual-relevance-explanation-v1` (7492362, cherry-picked from a42be9f), with campaign-state update 98ab936 and specification c59aabd. Mechanically exercised (`why_matters_now` fact→meaning→connection→consequence, `GlobalMapEntry.explanation`, enriched `FocusConnection` summaries) but NOT YET AUTHOR-VALIDATED.
- **Remote durability:** `feature/contextual-relevance-explanation-v1` is published at `c59aabd` on GitHub; this state will be reconciled to the new frozen candidate SHA after docs-only correction.
- **Empirical evidence:** Architecture Value V3 (`20260829-agent-native-sonnet-opus-v3`) — C (rich ledger) 13/2/0 vs B (shipped Map/Focus) 6/6/3 vs A (baseline) 6/6/3. C dominates paired P03/P05 Book-4 family; pressure grouping + causal/supporting-history trace is strongest C-over-B mechanism.
- **Productization Pilot V1 (frozen baseline):** `docs/product-validation/global-map-focus-productization-pilot-v1.md` — FROZEN SHA c60958a, author dogfood COMPLETE, disposition PARTIALLY VALIDATED. Revision safety POSITIVE; Focus decision support NEGATIVE/INSUFFICIENT.
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

**JUST COMPLETED:** Bounded contextual-explanation enrichment (see above). Next warranted responsibility:

**Bounded comparative re-dogfood of Contextual Relevance Explanation V1.**

- Use: same Superhero source snapshot; same D16-D23 horizon; same Book 9 planning question; same D19/Wren revision scenario; original Pilot V1 outputs preserved as baseline; new exact candidate SHA frozen before run.
- Question: Does the enriched Focus materially improve author decision support, especially whether the author understands the SPECIFIC narrative connection between a surfaced item and the current decision?
- Legitimate dispositions: POSITIVE / MIXED / NEGATIVE — determine the new author-value disposition relative to the original negative baseline. Do not precommit to a flip to POSITIVE.
- After re-dogfood, review whether the explanation candidate warrants merge to `main`. Do not precommit to merge; POSITIVE, MIXED, and NEGATIVE are all legitimate outcomes.
- Scale stress case to 20+ Books only if re-dogfood shows residual information-load issues (deferred).

- Decision-changing uncertainty: Does propagating existing accepted narrative meaning (transition.explanation + commitment statements) solve the author's "why is this here?" complaint, or does it merely make opaque Focus output more verbose — indicating the missing abstraction is the decision-specific semantic relationship itself?
- Recommended next: freeze exact SHA of `feature/contextual-relevance-explanation-v1` after this reconciliation commit and run the comparative re-dogfood on that frozen candidate.

## Previously Selected Responsibility (completed)

Bounded contextual-relevance explanation research → prototype → minimal implementation for Focus.

- **Decision supported:** What minimal explanation enrichment makes Focus decision-useful without speculative ontology or manual database administration?
- **Resolution:** Narrative meaning derivable from existing `transition.explanation` + commitment statements without new author bookkeeping. Added derived `explanation` propagation through `GlobalMapEntry` (not new canonical store) and enriched `why_matters_now` / connection summaries.
- **Evidence type:** ARCHITECTURE + PRODUCT-VALUE (repo evidence + fixture probe + formatter demo).
- **Alternatives considered:** (1) Merge slice to main first, (2) scale, (3) universal ontology — deferred.
 - **Evidence produced:** Commit a42be9f (cherry-picked as 7492362 on `feature/contextual-relevance-explanation-v1`); formatter demo shows `archive-protected — The treaty protects the admitting custodian — it matters now because its narrative meaning directly informs this decision; if ignored, the decision loses its historical grounding.`

## Completed Campaign Responsibilities

1. 2026-09-02 — Campaign diagnosis + state establishment (this file).
2. 2026-09-02 — Bounded contextual-explanation enrichment for Focus (commit a42be9f / 7492362): enriched `why_matters_now` with narrative meaning from `transition.explanation` (fact→meaning→connection→consequence), added `GlobalMapEntry.explanation`, enriched `FocusConnection` causal summaries, enriched pressure-group explanations; all vertical-slice tests pass (127), `scripts/check.py --skip-pytest` passes.
3. 2026-09-02 — Branch migration: created `feature/contextual-relevance-explanation-v1` from `origin/main @ 1a686f5`, cherry-picked explanation, added campaign specification (c59aabd), published to GitHub.

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

NOT COMPLETE. See 18 acceptance conditions in campaign mission — mechanical history/revision safety partially satisfied; Productization Pilot V1 remains PARTIALLY VALIDATED (revision safety POSITIVE, original Focus explanation NEGATIVE); contextual explanation (conditions 9,10,13) is now mechanically implemented but NOT YET AUTHOR-VALIDATED — re-dogfood will determine new disposition (POSITIVE / MIXED / NEGATIVE) relative to original baseline. Ontology remains minimal-by-design; do not precommit to merge.

## Fresh-Context Reconstruction Test

Next agent should read this file + `docs/product-validation/global-map-focus-productization-pilot-v1.md` + `docs/architecture/detailed-narrative-architecture-v1.md` to reconstruct mission, demonstrated vs hypothesized, and why contextual explanation is next.

## Reconciliation: Contextual Relevance Explanation V1 Owner Re-Dogfood

- Evidence candidate: `feature/contextual-relevance-explanation-v1 @ 52912a38df5cb1a1bfae30ba8f22d0ea2a285dd3`.
- Author re-dogfood: COMPLETE.
- Author evidence class: OWNER_DOGFOOD.
- Author value disposition: MIXED.
- Improvement over Pilot V1: YES — MATERIAL.
- Narrative-meaning value: POSITIVE.
- Decision-specific relevance value: MIXED / INSUFFICIENT.
- Pressure explanation value: MIXED / INSUFFICIENT.
- Long-range connection explanation: MIXED.
- Revision-safety value: POSITIVE, unchanged.
- Impact explanation: NEGATIVE / NOT ADDRESSED.
- Strongest demonstrated improvement: Auteur can propagate accepted authored narrative meaning into Focus, making previously opaque implementation/state vocabulary substantially more intelligible.
- Primary remaining friction: Auteur often states that a historical fact “directly informs this decision” without explaining the specific semantic mechanism through which that history bears on the present creative choice.
- Representation consequence: do not add generic narrative-gloss storage from this evidence. Existing accepted explanation fields appear capable of supplying much of narrative meaning; investigate instead the decision-specific relationship between narrative history and the current author decision.
- Extraction reopening gate: NOT CROSSED.

## Selected Responsibility: Decision-Specific Relevance Bridge V0

- Campaign status: ACTIVE.
- Responsibility status: SELECTED.
- Type: Research + Architecture + Owner Evaluation.
- Implementation authorization: NO.
- Decision supported: determine the smallest semantic/reasoning capability Auteur requires to explain why accumulated narrative history matters to one particular current author decision.
- Central research question: Can Auteur derive useful, author-readable explanations of why accepted narrative history bears on a current creative decision by combining existing accepted narrative meaning with an interpretively derived and owner-validated Decision Frame, without adding new canonical narrative storage?
- Impact explanation: known unresolved product gap; out of scope for this responsibility.
- Current phase: PHASE_A_PACKET_COMPLETE_AWAITING_OWNER_GATE_A. The Decision-Frame Socratic Critic completed independent challenge; no six-case bridge analysis is authorized until the owner validates or corrects a working frame.
