# Campaign 2 — Series Vertical Slice V1 Validation Integration

**Date:** 2026-08-25
**Reconstructed from:** `f0d8795` (post-PR-137 `origin/main`)

---

## Candidate identification

| Field | Value |
|---|---|
| Integration candidate SHA | `a5761ad3eb8adf88219aa10e5a4eed9fddf66808` |
| Candidate type | Merge commit |
| Parent 1 (remote main, post-PR-137) | `f0d8795610c29e3eb83ffb714d2a364d07115951` |
| Parent 2 (Campaign 2 tip) | `ca6e1c43927dda8a9b3020e0c737bcc8bad5d6b5` |
| Integration branch | `publish/series-vertical-slice-v1-validation-integration-v2` |
| Historical note | `e989533` (previous attempt) was **superseded** — it integrated against `dd2db5d` (pre-merge V1 head), not `f0d8795` (post-PR-137 main). This document records the corrected topology. |

---

## Historical qualification references

This qualification **replaces and supersedes** the previous incorrect attempt:

```
Previous candidate:   e989533 (wrong base: dd2db5d, not f0d8795)
Previous evidence:    e989533 (docs: record series vertical slice qualification)
Previous claim:       Series Vertical Slice V1 integration qualified against pre-merge head
                      (not eligible — did not contain post-PR-137 origin/main)
```

The new claim is narrowly:

> **Campaign 2 integration is qualified against current remote Story Discovery main (`f0d8795`), with installed-wheel artifact qualification.**

---

## Merge analysis

### Correct topology

The integration candidate `a5761ad3` has **two parents**:

| Parent | SHA | Meaning |
|---|---|---|
| First parent | `f0d8795610c29e3eb83ffb714d2a364d07115951` | `origin/main` after PR #137 merge (Series V1 integration + remote main) |
| Second parent | `ca6e1c43927dda8a9b3020e0c737bcc8bad5d6b5` | Historical Campaign 2 standalone qualification tip |

### Verified ancestry

```text
git merge-base --is-ancestor f0d8795610c29e3eb83ffb714d2a364d07115951 a5761ad3
→ TRUE  (f0d8795 is ancestor of M2)
git merge-base --is-ancestor ca6e1c4 a5761ad3
→ TRUE  (ca6e1c4 is ancestor of M2)
git rev-list --parents -n 1 a5761ad3
→ a5761ad3 f0d8795... ca6e1c4...  (both parents confirmed)
```

### Merge method

`git merge ca6e1c4 --no-ff --allow-unrelated-histories` — forced merge commit because the two histories share only `ee3ed74` as common ancestor and diverged after that.

### Net diff against `origin/main @ f0d8795...`

| File | Change |
|---|---|
| `docs/engineering/campaign-2-integration-qualification-v2.md` | New (this qualification record) |
| `docs/engineering/series-vertical-slice-v1-focus-authority-clarification-qualification.md` | Preserved from V1 integration |
| `docs/product-validation/series-vertical-slice-v1-synthetic-stress-test.md` | New (Campaign 2) |
| `docs/product-validation/series-vertical-slice-v1-synthetic-wording-experiment.md` | New (Campaign 2) |
| `docs/product-validation/series-vertical-slice-v1-user-validation.md` | New (Campaign 2) |
| `src/auteur/series/vertical_slice_formatters.py` | Modified (+4 lines) |
| `tests/test_series_vertical_slice_cli.py` | Modified (+4 tests) |

**6 files changed, +1063/-0 insertions/deletions** (additive only)

No Story Discovery source files touched. No remote work deleted or reverted.

### Excluded from scope

- Repeated Map/Focus V2, Boundary 2, Probe Surface Enablement
- Campaigns 3–4
- Any user-dirty file modifications

---

## Test results

### Environment

- Python: 3.14.3
- pytest: 9.0.3
- Package: auteur 0.37.1 (installed from M2 candidate wheel)

### Focused: Series V1 / authority clarification suite

```
tests/test_series_vertical_slice_cli.py
tests/test_series_vertical_slice_models.py
```

**Result: 15 passed, 0 failed, 0 skipped**

### Focused: Story Discovery regression suite

```
tests/test_story_discovery_recommendation_basis.py
tests/test_story_discovery_review.py
```

**Result: 15 passed, 3 failed** (all 3 are **KNOWN BASELINE FAILURES** — confirmed identical against `f0d8795` in clean worktree; no new regressions from Campaign 2)

### Full targeted suite

**Result: 30 passed, 3 failed, 0 skipped**

| Test | Result | Classification |
|---|---|---|
| `test_qualified_comparative_non_adjudicable_is_a_valid_project_state` | FAIL | **KNOWN BASELINE FAILURE** (confirmed against `f0d8795...`) |
| `test_recommendation_review_reconstructs_writer_facing_evidence` | FAIL | **KNOWN BASELINE FAILURE** (confirmed against `f0d8795...`) |
| `test_composed_review_explains_borrows_and_preserved_primary` | FAIL | **KNOWN BASELINE FAILURE** (confirmed against `f0d8795...`) |

No new failures introduced by Campaign 2.

### Wheel artifact qualification

- Wheel built from exact M2 candidate SHA `a5761ad3eb8adf88219aa10e5a4eed9fddf66808`
- Wheel filename: `auteur-0.37.1-py3-none-any.whl`
- Wheel SHA-256: `8485d6ece0de50bab8fddfd82eb7c2a302c67d6c91ec571491efd857afc386f9`
- All 10 installed-wheel matrix checks passed (import, pack list, pack inspect, opinionated recommendation, durability, zero pre-acceptance mutation, explicit acceptance, restart persistence, pack version/hash persist, genre validation, genre diagnosis)

---

## Qualification evidence ancestry

```
ee3ed74 (Series V1 historical tip)
        │
        ├─ f0d8795 (PR #137 merge: main + V1 integration)
        │    │
        │    └─ a5761ad3 (this M2 candidate: f0d8795 + ca6e1c4)
        │         └─ [wheel qualification + source suite evidence documented here]
        │
        └─ ca6e1c4 (historical standalone Campaign 2 qualification)
             └─ d3bb1eb (historical Campaign 2 production candidate)
```

---

## Superseded integration attempt

The prior commitment `e989533` ("Merge Campaign 2 into publish/series-vertical-slice-v1-integration") is **not publication-eligible** because:

- Its first parent was `dd2db5d` (the V1 integration head **before** PR #137 merge into main)
- It did **not** contain post-PR-137 `origin/main @ f0d8795...`
- Its wheel qualification and source suite were valid for its own topology, but that topology does not represent integration against the current remote main lineage

This document does not delete or rewrite `e989533`; it records the topology error and documents the correct candidate `a5761ad3` for publication.

---

## Publication preflight checklist

Before opening PR 2, verify:

```text
f0d8795... is ancestor of new M2 a5761ad3  ✅ (verified)
ca6e1c4 is ancestor of new M2 a5761ad3  ✅ (verified)
d3bb1eb is ancestor of new M2 a5761ad3  ✅ (verified, via ca6e1c4)
source/tests at PR tip == new M2  ✅ (byte-identical)
PR diff vs current main == Campaign 2 + qualification evidence only  ✅ (6 files, 1063 additions)
Campaign 3+ absent  ✅ (confirmed)
user-dirty files untouched  ✅ (confirmed)
```

---

## Authorization

If all source and installed-artifact qualification gates pass, the author is prepared to:

1. Open PR 2 against `origin/main @ f0d8795...`
2. Title: `feat: Campaign 2 — Focus Authority Clarification + Series V1 user-validation integration`
3. Base: `origin/main @ f0d8795...`
4. Head: `publish/series-vertical-slice-v1-validation-integration-v2 @ a5761ad3...`
5. Merge method: `--merge` (preserves qualified commit ancestry)
6. Do not merge until separate authorization

---

## Superseded evidence preserved (not for publication)

| Commit | SHA | Status |
|---|---|---|
| `e989533` | old M2 merge (wrong base) | Superseded — documented above, not for publication |
| `d3bb1eb` | historical Campaign 2 production candidate | Preserved as historical record |
| `ca6e1c4` | historical Campaign 2 qualification | Preserved as historical record |
| `4ef6666` | V1 integration candidate | Previously qualified and merged (PR #137) |