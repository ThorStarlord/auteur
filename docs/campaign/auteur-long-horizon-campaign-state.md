# Auteur Long-Horizon Narrative Intelligence Campaign — State

**Mission:** Reliable long-horizon narrative intelligence for very long fiction (dozens/hundreds of Books) without reconstructing entire history per decision.

**North Star:** Preserve and reconstruct narrative meaning across story too large for working context.

## Current Product State (2026-09-02, auteur/main @ 1a686f5 + feature/contextual-relevance-explanation-v1)

- **Architecture doc:** `docs/architecture/detailed-narrative-architecture-v1.md` — ACCEPTED for V1 vertical-slice implementation (human-reviewed). 5 semantic layers + scope axis unchanged. Global Map = derived rebuildable projection; Focus = derived relevance projection; derived != canon (ADR 019).
- **Vertical slice + Productization Pilot V1:** MERGED to `auteur/main @ 1a686f5`. Proves: accepted revisioned history, current-state projection, typed CausalSupportRelation|PressureGroupRelation, Global Map snapshot, Focus via pure Map selector, revision impact propagation without silent rewrite, rebuild equivalence. P0 death tests pass; full suite retains 3 known baseline Story Discovery failures. Pilot disposition remains PARTIALLY VALIDATED (revision safety POSITIVE; original Focus decision support NEGATIVE/INSUFFICIENT).
- **Contextual Relevance Explanation V1:** IMPLEMENTED on `feature/contextual-relevance-explanation-v1` (7492362, cherry-picked from a42be9f), with campaign-state update 98ab936 and specification c59aabd. Comparative author re-dogfood is COMPLETE with MIXED / PARTIALLY VALIDATED author value: narrative meaning POSITIVE, decision-specific relevance MIXED / INSUFFICIENT, pressure explanation MIXED / INSUFFICIENT, long-range connection explanation MIXED, revision safety POSITIVE unchanged, and impact explanation NOT ADDRESSED.
- **Remote durability:** `feature/contextual-relevance-explanation-v1` is published at frozen evidence candidate `52912a38df5cb1a1bfae30ba8f22d0ea2a285dd3` on GitHub.
- **Empirical evidence:** Architecture Value V3 (`20260829-agent-native-sonnet-opus-v3`) — C (rich ledger) 13/2/0 vs B (shipped Map/Focus) 6/6/3 vs A (baseline) 6/6/3. C dominates paired P03/P05 Book-4 family; pressure grouping + causal/supporting-history trace is strongest C-over-B mechanism.
- **Productization Pilot V1 (frozen baseline):** `docs/product-validation/global-map-focus-productization-pilot-v1.md` — FROZEN SHA c60958a, author dogfood COMPLETE, disposition PARTIALLY VALIDATED. Revision safety POSITIVE; Focus decision support NEGATIVE/INSUFFICIENT.
- **Mechanical capabilities DEMONSTRATED:** accepted-history reconstruction, stable identity (ArtifactStore revisions), narrative vs revision order separation, long-range causal support, pressure grouping, Global Map rebuild, Focus derivation, semantic-impact propagation (valid/stale/suspect/contradictory), downstream preservation.

## Author-Validated vs Mechanical

- **Mechanically validated:** history, currentness, grouping, Map/Focus mechanics, revision impact (via V3 + slice qualification).
- **Author-validated POSITIVE:** downstream impact without silent rewrite (pilot).
- **Author-validated NEGATIVE:** Focus surfaces facts but fails to explain narrative context that makes them relevant to current decision. Provenance without YAML also insufficient.
- **Author-validated MIXED:** contextual explanation materially improved narrative-meaning intelligibility, while decision-specific relevance and pressure explanation remained mixed/insufficient; scale beyond ~10 entries remains unvalidated.

## Primary Product Failure (Pilot Friction)

> Focus identified relevant facts and relationships, but did not explain the narrative context that makes them relevant to the current creative decision.

Example insufficient: `operative_network.integration_state = peer_ambivalence_integrated` → "Book 9 explicitly references this fact." Desired: fact → narrative meaning → connection to decision → consequence if ignored/changed.

Required shape (pilot): `story fact → narrative meaning → connection to current decision → consequence`

## Previously Selected Capability Boundary (historical)

**Historical Horizon A (superseded) — Contextual, author-readable relevance explanation for Focus and revision impact.**

- Affects: `why_matters_now` generation in `repeated_map_focus.py`, `vertical_slice_models.py` entry fields, and `vertical_slice_formatters.py` author-facing rendering.
- Current limitation: `why_matters_now` templates are mechanical ("Accepted fact X sets current Y to Z but planning does not reference it") and provenance is ID-centric. No narrative-meaning field exists.
- Historical rationale: this boundary blocked Focus from providing value even when selection was correct; the pilot selected it as the single next capability at that time. The resulting evidence and current position are recorded below; extraction gate remains NO.

## Open Representation Questions (Horizon B deferred unless needed for explanation)

- Minimal ontology enrichment needed to support narrative meaning without new author bookkeeping burden (STORE vs DERIVE vs INTERPRET).
- Whether pressure-group explanation needs richer member roles/narrative gloss vs reusing existing commitment statements.

## Completed Responsibility Boundary

The contextual-explanation implementation and comparative author re-dogfood
are completed and recorded above. This state does not preselect a successor.
After each completed responsibility, control returns to campaign-level
reassessment before another bounded responsibility is selected.

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
- Pilot disposition (historical): extraction gate NO; contextual explanation was the selected next capability at that stage (not extraction/ontology/scaling). Subsequent V1 re-dogfood and Decision-Specific Relevance Bridge V0 conclusions supersede that next-capability statement.
- Architecture V1 human-reviewed for slice implementation; implementation frozen at c60958a for pilot evidence.

## Deferred / Not Warranted Now

- Automatic story-instance relationship extraction (gate NO).
- Universal graph ontology / graph DB.
- Scaling to 50+/100+ entries with budgeted selector (P2).
- Generalized commitment lifecycle beyond slice.
- LLM-assisted interpretation.

## Owner Decisions Required

- Campaign-level reassessment is now warranted. No successor responsibility is selected by this closure state.

## Campaign Acceptance Status

NOT COMPLETE. See 18 acceptance conditions in campaign mission — mechanical
history/revision safety partially satisfied; Productization Pilot V1 remains
PARTIALLY VALIDATED; Contextual Relevance Explanation V1 is materially improved
but only PARTIALLY VALIDATED; Decision-Specific Relevance Bridge V0 is EVIDENCE
COMPLETE with H3 primary and H4 guardrail. Ontology admission is NO, extraction
gate is NOT CROSSED, and production implementation is NOT AUTHORIZED.
Campaign-level reassessment is now warranted; no next responsibility is
selected here.

## Fresh-Context Reconstruction Test

Next agent should read this file + `docs/product-validation/global-map-focus-productization-pilot-v1.md` + `docs/architecture/detailed-narrative-architecture-v1.md` to reconstruct the completed evidence, demonstrated capabilities, unresolved uncertainties, and current campaign-level reassessment.

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

## Completed Responsibility: Decision-Specific Relevance Bridge V0

- Campaign status: COMPLETE / EVIDENCE COMPLETE.
- Responsibility status: COMPLETE.
- Type: Research + Architecture + Owner Evaluation.
- Implementation authorization: NO.
- Decision supported: determine the smallest semantic/reasoning capability Auteur requires to explain why accumulated narrative history matters to one particular current author decision.
- Central research question: Can Auteur derive useful, author-readable explanations of why accepted narrative history bears on a current creative decision by combining existing accepted narrative meaning with an interpretively derived and owner-validated Decision Frame, without adding new canonical narrative storage?
- Impact explanation: known unresolved product gap; out of scope for this responsibility.
- Current phase: V0_EVIDENCE_COMPLETE. Owner Gate A validated Frame B as the working frame (PARTIALLY_ACCURATE), Frame C remains a downstream narrative-test lens, six bounded cases were analyzed, and Semantic Bridge Critic, Evidence Auditor, and Owner Gate B are complete. H3 is the primary disposition with an H4 guardrail; no implementation is authorized.

## Decision-Specific Relevance Bridge V0 Reconciliation

- V0 status: EVIDENCE COMPLETE for the bounded Superhero case.
- Owner Gate B: complete. D18, D19, D20, D23, and persistent pressure retain
  bounded owner-confirmed bridges; D18→D19 is NO BRIDGE for semantic causation,
  preserving only ordered adjacency.
- Primary synthesis: H3 — decision relevance remains substantially
  interpretive. H4 is an architectural guardrail against a persisted or
  universal DecisionRelevanceBridge.
- H1 is supported only in the bounded sense that accepted meaning and
  provenance supply useful material; H2 is not admitted because no recurring
  universal representation gap was demonstrated.
- No generic narrative-gloss storage, persisted DecisionFrame, production
  bridge, extraction, scale test, or impact-explanation implementation is
  authorized.
- Next action: campaign-level reassessment of the next bounded responsibility;
  do not automatically continue this responsibility to V1.

## Campaign Closure: Decision-Specific Relevance Bridge V0

- Responsibility: Decision-Specific Relevance Bridge V0.
- Status: COMPLETE / EVIDENCE COMPLETE for the bounded Superhero case.
- Primary result: H3 — decision relevance remains substantially interpretive.
- Architectural guardrail: H4 — do not universalize or persist
  DecisionRelevanceBridge.
- Ontology admission: NO.
- Extraction: gate NOT CROSSED.
- Scale: NOT WARRANTED.
- Focus explanation: materially improved but PARTIALLY VALIDATED.
- Revision safety: strongest currently demonstrated product value.
- Impact explanation: separate unresolved product gap.
- Current next action: campaign-level reassessment.
- No successor responsibility is selected in this closure state.

Candidates for campaign reassessment only:

- Revision Impact Explanation.
- Decision-specific interpretive reasoning workflow.
- Persistent-pressure explanation under contradictory history.
- Broader ontology research if newly warranted.
- Trajectory/arc reasoning.
- Epistemic-state reasoning.
- Long-horizon scale and information-load behavior.

## Selected Responsibility: D19 Revision Review-Value Explanation V0

- Owner authorization: APPROVED.
- Type: Research + Product-Value + Mechanical-Boundary Clarification.
- Implementation authorization: NO.
- Current phase: EVIDENCE_COMPLETE / OWNER_GATE_CLOSED.
- Status: COMPLETE / EVIDENCE COMPLETE.
- Semantic/mechanical result: POSITIVE.
- Product-value result: INCONCLUSIVE for this case; H4 primary because prior
  owner exposure prevents a clean before/after decision delta.
- Review result: D20 REVIEW for direct reconciliation attention; D21–D23
  NO_REVIEW for now, pending any D20 decision that reaches them.
- Next checkpoint: CAMPAIGN-LEVEL REASSESSMENT.
- Successor responsibility: NONE SELECTED.
- Scope boundary: this responsibility does not authorize ontology, extraction,
  scale, automatic reconciliation, automatic rewriting, or production changes.
