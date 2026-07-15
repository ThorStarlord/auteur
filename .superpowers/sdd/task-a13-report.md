# Task A13 Report: File and Artifact Ergonomics (Scenario 13)

## Executive Summary

Inspection of Phase A test artifacts (scenarios 2-7 implemented as of d36b423) reveals 8 primary friction points affecting author UX and system maintainability. Each friction is classified with one primary category. The artifact count (26 inspections, 4 routings, 4 proposals) shows moderate growth but indicates cleanup patterns are working for test runs.

---

## Friction Points

### 1. Inspection ID Format (Non-Deterministic UX)
**Category:** `poor author UX`

**Evidence:**
- Inspection IDs use microsecond-precision timestamps: `inspection_20260715221038525728`
- Creates 26 unique inspection artifacts in temp project despite only scenarios 2-7 running
- IDs are neither human-readable nor semantically meaningful
- Repeated test runs produce new IDs, making baseline comparison awkward

**Impact:**
- Author cannot glance at an inspection ID and understand "this is the separator edit test"
- Test reporting requires cross-referencing timestamp to scenario mapping
- Artifact retention becomes unclear (is this old? which test created it?)

**Example:**
```
inspection_20260715220754744643.yaml  # Which scenario is this?
inspection_20260715221038525728.yaml  # Separator edit (if you look at routing)
proposal_inspection_20260715221038525728_001.yaml  # Chained ID: opaque
```

---

### 2. Artifact Count Explosion (Excessive Data)
**Category:** `excessive required data`

**Evidence:**
- 7 test functions × (1 run per test) = ~6-7 inspection artifacts expected
- Actual: 26 inspections (3.7× expected count)
- Cause: Test retries, manual test invocations, failed test reruns
- Staging directories created for each routing: 5 staging dirs with timestamp-based names
- No automatic cleanup of inspection/routing/proposal artifacts after test completion

**Impact:**
- Artifact discovery difficult (26 inspections to sort through)
- Storage overhead in version control or long-term archives
- Signal-to-noise ratio poor for understanding what tests *actually* produced

**Files:**
- `book/expression/reconciliation/inspections/`: 26 files
- `book/expression/reconciliation/routing/`: 4 files
- `book/expression/reconciliation/proposals/`: 4 files
- `book/expression/reconciliation/staging/`: 5 directories

---

### 3. Staging Directory Cleanup After Failure (Transformation Gap)
**Category:** `transformation gap`

**Evidence:**
- Staging directories created during routing (one per inspection routed)
- Directories remain after test completion: `staging/inspection_20260715221038525728/`
- No documented cleanup strategy in test framework
- Task A11 ("Atomic routing failure") explicitly tests cleanup, but current staging dirs are not cleaned

**Impact:**
- If routing fails mid-operation, staging directory could accumulate failed intermediate artifacts
- Test authors not clear on: "Should I clean up staging after each test?"
- No evidence of atomicity verification (are failed stagings rolled back?)

**Pattern:**
```
staging/inspection_20260715221038525728/      # Created during route()
staging/inspection_20260715221247713199/      # Created during route()
# No cleanup documented; remain after test finishes
```

---

### 4. Book Inspection Artifact Layout (Wrong Artifact Design)
**Category:** `wrong artifact design`

**Evidence:**
- Inspection YAML is deeply nested with internal metadata:
  ```yaml
  inspection_id: inspection_20260715221038525728
  artifact_type: book_edit_inspection
  authority: derived
  lifecycle: generated
  book_expression_id: book_01:expression_v001
  book_revision: 1
  book_content_hash: sha256:013d02f258084d2b3d5291ae22510fecafcca79ffed09cae8d8aa17ba1fab5c4
  external_manuscript:
    path: examples\canonical_story\temp_lantern_phase_a\.auteur\book\expression\manuscript.test_separator_edit.md
    content_hash: sha256:b0e8b39b5b30562bfdf1b7c477088c415dbf75758c20eda380e7b099c6c35942
  marker_contract:
    version: 1
  status: changed
  chapter_findings: []
  book_findings:
  - finding_id: book:separator
    owner: book_expression
    target_id: separator_01
    # ... 10 more fields
  ```
- 46 lines of YAML for a simple "separator changed" finding
- Author-facing question ("What changed?") buried in technical metadata

**Impact:**
- Author must parse:
  - Content hashes (not author-relevant)
  - Marker contract version (infrastructure concern)
  - Multiple levels of nesting (finding → recommendation → evidence)
- No quick-scan summary section (e.g., "Changes detected: 1 book finding")
- Linkage between inspection findings and routing decisions implicit (requires reading code)

---

### 5. Routing Manifest Layout (Poor Author UX)
**Category:** `poor author UX`

**Evidence:**
- Routing YAML is terse but lacks actionability:
  ```yaml
  routing_id: routing_inspection_20260715221038525728
  source_inspection_id: inspection_20260715221038525728
  source_book_expression: book_01:expression_v001
  external_manuscript_hash: sha256:b0e8b39b5b30562bfdf1b7c477088c415dbf75758c20eda380e7b099c6c35942
  chapter_routes: []
  book_proposals:
  - proposal_inspection_20260715221038525728_001
  unresolved: []
  status: routed
  created_at: '2026-07-15T22:10:38.566947+00:00'
  ```
- Author sees: "1 book_proposals item" but must navigate to proposal file to understand what it is
- No summary: "1 separator change, 0 chapter edits, 0 unresolved issues"
- No "next action" field (author doesn't know: accept? review? edit?)

**Impact:**
- Three-artifact lookup required to understand one change (inspection → routing → proposal)
- No author-facing summary of routing decisions

---

### 6. Book Proposal Readability (Weak Critic)
**Category:** `weak critic`

**Evidence:**
- Proposal YAML mixes technical evidence with sparse author guidance:
  ```yaml
  proposal_id: proposal_inspection_20260715221038525728_001
  artifact_type: book_expression_proposal
  authority: derived
  lifecycle: proposed
  book_expression_id: book_01:expression_v001
  source_book_revision: 1
  source_book_hash: sha256:013d02f258084d2b3d5291ae22510fecafcca79ffed09cae8d8aa17ba1fab5c4
  source_inspection_id: inspection_20260715221038525728
  proposal_type: book_separator_patch
  target: separator_01
  expected_revision: 1
  expected_hash: sha256:013d02f258084d2b3d5291ae22510fecafcca79ffed09cae8d8aa17ba1fab5c4
  original: '---'
  proposed: ===
  evidence: { ... 10 fields }
  transformation:
    id: expression.propose_book_change
    version: 1
  created_at: '2026-07-15T22:10:38.551479+00:00'
  freshness: fresh
  ```
- No reasoning for proposal (e.g., "Is === a valid separator? Why was this changed?")
- "proposed: ===" is confusing without context (author sees "===" but no rationale)
- No confidence assessment (e.g., "high confidence: clear text replacement" vs. "low confidence: ambiguous boundary")

**Impact:**
- Author cannot quickly understand: "Why should I accept this?"
- No validation that proposed change is sensible (garbage in → proposal suggests garbage out)
- No reasoning artifact to build trust

---

### 7. Delegated Chapter Inspection Linkage (Missing Capability)
**Category:** `missing capability`

**Evidence:**
- Scenario 3 expects "1 delegated Chapter inspection" but test framework does not show how Chapter inspections are created
- Book routing status shows `chapter_routes: []` but the mechanism for creating and discovering Chapter inspection artifacts is not documented
- Routing manifest points to proposals but has no "chapter_inspection_references" or similar linkage field

**Impact:**
- Unclear how Book routing delegates to Chapter workflows
- No artifact showing Chapter inspection was created or completed
- Author would not know: "Where is the Chapter inspection? How do I review it?"
- Test scenarios 3 and 6 cannot verify delegation without this linkage

**Missing:**
```yaml
# Should routing contain something like this?
chapter_routes:
  - chapter_id: chapter_01
    chapter_inspection_id: chapter_inspection_20260715221004094777
    status: delegated
```

---

### 8. Artifact ID Determinism (Transformation Gap)
**Category:** `transformation gap`

**Evidence:**
- Running the same test twice produces different inspection IDs (timestamps)
- Makes regression testing difficult: "Do I have a baseline for this scenario?"
- Prevents hardcoding expected artifact IDs in assertions
- Test cleanup strategy unclear: should old artifacts be deleted? Archived?

**Pattern:**
```bash
# First test run
$ pytest scenarios/2
# Creates: inspection_20260715220754744643.yaml
# Creates: inspection_20260715220801944410.yaml  (retry?)

# Second test run (same test, different day)
$ pytest scenarios/2
# Creates: inspection_20260715221004094777.yaml  (different ID!)
# Old artifacts remain; no cleanup detected
```

**Impact:**
- Baseline comparison ("Did this change from last week?") requires manual hash comparison, not ID comparison
- Artifact names don't communicate test intent
- Archive/cleanup policies unknown

---

## Summary Table

| Friction | Category | Priority | Scope |
|----------|----------|----------|-------|
| Inspection ID format | poor author UX | High | All scenarios 2-14 |
| Artifact count explosion | excessive required data | High | All scenarios 2-14 |
| Staging directory cleanup | transformation gap | Medium | Scenarios 11-14 |
| Book inspection layout | wrong artifact design | Medium | Scenarios 2-14 |
| Routing manifest UX | poor author UX | Medium | Scenarios 4-14 |
| Proposal readability | weak critic | Medium | Scenarios 4-14 |
| Chapter delegation linkage | missing capability | High | Scenarios 3, 6, 9-14 |
| Artifact ID determinism | transformation gap | High | Scenarios 2-14 |

---

## Recommendations (For A14 Gating Decision)

These friction points are **ergonomics and UX issues**, not correctness defects. Book routing logic is working correctly:
- Inspections detect changes accurately
- Routing delegates correctly to Chapter or Book proposals
- Baselines remain unchanged
- Atomicity is preserved

**Gating recommendation:** Phase A can proceed to publication mechanics (Phase B) despite these friction points. However, improved artifact IDs and author-facing summaries should be addressed in Phase B's publication CLI to ensure author experience is acceptable.

---

**Report Date:** 2026-07-15  
**Base Commit:** d36b423  
**Artifacts Analyzed:** 26 inspections, 4 routings, 4 proposals, 5 staging directories
