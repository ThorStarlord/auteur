# Auteur Long-Horizon Narrative Intelligence Campaign — Specification

**Type:** campaign governance (how the campaign is run)
**Companion:** `auteur-long-horizon-campaign-state.md` (where the campaign currently is)

## 1. Mission

Reliable long-horizon narrative intelligence for very long fiction (dozens/hundreds of Books) without reconstructing entire history per decision.

**North Star:** Preserve and reconstruct narrative meaning across story too large for working context.

## 2. Semantic Authority

`docs/narrative-architecture.md` (and its detailed elaboration in `docs/architecture/detailed-narrative-architecture-v1.md`) is the sole authority for semantic layer names, count, ownership, and boundaries.

- Five semantic layers: 0 Ontology, 1 Identity, 2 Structure, 3 Realization, 4 Expression
- Five scope containers: Universe, Series, Book, Chapter, Scene (scopes ≠ layers)
- Global Map, Focus, and story-instance relation indexes are **derived, rebuildable, non-canonical** (ADR 019). Accepted Series/Book Direction and realization revisions remain the sole canonical store.
- Root agent files may summarize but must not define competing layer models.

## 3. Campaign Structure

This is a **whole-story structure engine** campaign first, chapter drafting second.

- Global constraints are first-class: target experience, genre/subgenre hierarchy, mode, medium, scope, scale.
- Whole-story engine: main thread + subordinate threads, each with want, resistance, conflict, stakes, change, thematic function.
- Schema vs diagnostics separation:
  - Pydantic models = is the blueprint shaped correctly?
  - `auteur.structure` analyzers = is it complete/coherent? (deterministic, no LLM calls)
- Prefer proposal/report artifacts over direct blueprint mutation.
- Keep authorial choices explicit; do not silently fill or rewrite the story spine.

## 4. Loop Governance

Each loop iteration selects **one bounded responsibility** with:

- `decision_supported` — what decision this loop enables
- `alternatives_considered` — what was deferred and why
- `evidence_type` — ARCHITECTURE | PRODUCT-VALUE | MECHANICAL
- `evidence_produced` — commit SHA, fixture probe, or pilot observation

**Grilling workflow:** ask one question at a time, give recommended answer, wait for approval before locking decisions. Capture approved conceptual decisions in `docs/` before implementing schema/analyzer/CLI/pipeline.

**Qualification gates** per `docs/engineering/release-qualification.md`:

1. Never call work "qualified" before evidence gate is complete.
2. Record exact candidate SHA before qualification.
3. Any source/test/version/packaging change invalidates downstream evidence.
4. Report pytest categories separately (collected/passed/skipped/xfailed/xpassed/failed/errors).
5. Timed-out command = incomplete evidence.
6. Build/test artifacts from exact frozen SHA.
7. Publication requires explicit authorization separate from qualification.

**Baseline failure policy:** REGRESSION (fails on candidate, passes on baseline) → BLOCK; KNOWN BASELINE FAILURE (fails identically on both) → proceed if untouched; SHIFTED FAILURE → INVESTIGATE. Check via `scripts/check.py`.

**Completion language:** implemented ≠ focused tests pass ≠ source-qualified ≠ artifact-qualified ≠ release-ready ≠ published.

## 5. Product Validation Method

- **Pilot V1** (`docs/product-validation/global-map-focus-productization-pilot-v1.md`): frozen SHA `c60958a`, bounded dogfood on one real project (6–10 Books), author observes Focus before/after + revision impact. Disposition: PARTIALLY VALIDATED (revision safety POSITIVE, Focus decision support NEGATIVE).
- **Next validation:** bounded re-dogfood of enriched Focus on same pilot project/protocol; extraction gate remains NO.
- **Empirical support:** Architecture Value V3 (`20260829-agent-native-sonnet-opus-v3`) — C 13/2/0 vs B 6/6/3 vs A 6/6/3; pressure grouping + causal trace is strongest C-over-B mechanism.

## 6. Current Horizons

- **Horizon A (now):** Contextual, author-readable relevance explanation for Focus and revision impact. Shape: `story fact → narrative meaning → connection to current decision → consequence if ignored/changed`. Affects `why_matters_now` in `repeated_map_focus.py`, `vertical_slice_models.py:GlobalMapEntry.explanation`, `vertical_slice_formatters.py`.
- **Horizon B (deferred):** Minimal ontology enrichment (STORE vs DERIVE vs INTERPRET), richer pressure-group member roles, scale to 20+ Books if information-load remains.

Deferred unconditionally: automatic extraction, universal graph ontology/graph DB, 50+/100+ budgeting, generalized commitment lifecycle, LLM-assisted interpretation.

## 7. Repository Truth

Before work whose correctness depends on identity/isolation:

```
git rev-parse --show-toplevel
git rev-parse --git-common-dir
git rev-parse HEAD
# determine standalone vs linked worktree before branch/worktree changes
```

Branch switch ≠ repo change; `cd` ≠ session workspace change. Linked worktree shares object/ref universe; standalone clone has its own. See `docs/agents/workspace-isolation.md`.

Required history:

```
auteur/main
└── Productization Pilot V1 merged (1a686f5)
    └── feature/contextual-relevance-explanation-v1 (from origin/main + cherry-picked explanation)
        ├── explanation implementation (7492362)
        └── campaign-state update (98ab936)
```

`auteur/docs/campaign/` holds `auteur-long-horizon-narrative-intelligence-campaign.md` (governance) + `auteur-long-horizon-campaign-state.md` (position). `sensemaking-skills` holds no campaign artifacts.

## 8. Fresh-Context Reconstruction

Next agent reads this file + `auteur-long-horizon-campaign-state.md` + `global-map-focus-productization-pilot-v1.md` + `detailed-narrative-architecture-v1.md` to reconstruct mission, demonstrated vs hypothesized, and why contextual explanation is next.

## 9. Acceptance Conditions (abridged)

NOT COMPLETE. Mechanical history/revision safety partially satisfied; contextual explanation (conditions 9,10,13) remains NEGATIVE until re-dogfood flips to POSITIVE. Real-author long-horizon value = PARTIALLY VALIDATED.

Full 18 conditions tracked in campaign state.

## 10. Owner Checkpoints

- Merge vertical slice + explanation to `main` only after re-dogfood POSITIVE.
- Preserve author authority: any Layer 1 mutation requires explicit author action, atomic persistence, auditable provenance.

---
*Created 2026-09-02 from campaign diagnosis + productization pilot + detailed architecture V1. Update only via explicit grilling decision.*
