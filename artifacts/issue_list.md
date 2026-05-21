# Issue List

## 1. PRD Consumed

- **PRD**: `artifacts/prd.md`
- **Scope**: exact_match, no expansion

## 2. Scope Status

**Exact Match**: All features address the repo-sensemaker recommendations.

## 3. Issues Generated

### TASK-004: Fix remaining 7 positive validator fixture failures

**Type**: Tech Debt
**Title**: Fix 4 CLI-arg-mismatch and 3 content-depth validator fixture failures

**Acceptance Criteria**:
- [ ] `validate-artifact.py` accepts the test harness fixture path without usage error
- [ ] `validate-mode-coverage.py` accepts the test harness calling convention
- [ ] `validate-output.py` accepts the test harness fixture path without usage error
- [ ] `validate-workflow-design.py` accepts the test harness calling convention
- [ ] `validate-plan.py` valid fixture passes (no Section 11 errors)
- [ ] `validate-run-log.py` valid fixture passes (no errors)
- [ ] `validate-skill-improvement-plan.py` valid fixture passes (no errors)
- [ ] Positive fixture pass count >= 15

**Effort**: 2 days
**Priority**: P1

### TASK-005: Fix all 15 negative validator fixtures

**Type**: Tech Debt
**Title**: Fix invalid fixtures so each validator produces a predictable error message

**Acceptance Criteria**:
- [ ] Each invalid fixture's `expected_error_contains` matches the actual validator error output
- [ ] Invalid fixture pass count >= 15
- [ ] No validator exits 0 on its invalid fixture

**Effort**: 1 day
**Priority**: P1

### TASK-006: Create REGRESSIONS.yaml

**Type**: Tech Debt
**Title**: Create tests/fixtures/REGRESSIONS.yaml for validator exclusion and regression tracking

**Acceptance Criteria**:
- [ ] `tests/fixtures/REGRESSIONS.yaml` exists with proper structure
- [ ] Excluded validators listed (if any)
- [ ] Required regression cases defined

**Effort**: 0.5 days
**Priority**: P2

### TASK-007: CONTEXT.md Layer 7 row fix (DONE)

**Type**: Tech Debt
**Title**: Update stale "PLANNED" row in Layer-to-Command Matrix
**Status**: ✅ Already completed during docs-aligner step

## 4. Release Scope

- **Total issues**: 4 (1 already done)
- **Total effort**: 3.5 days
- **Test count**: 264 passing (no regression expected)

## 5. Phasing Strategy

TASK-004 (core fixture fixes) → TASK-005 (negative fixtures) → TASK-006 (regressions)

## 6. Out of Scope

- Adding missing skills to registries
- ADR creation
- bible_audit relocation

## 7. Testing Plan

Run `scripts/test-validators.py` after each task to validate fixture pass rate.

## 8. Machine-Readable Handoff

```yaml
artifact_id: issue_list
schema_version: 1
source_intent_ref: artifacts/prd.md
user_goal_preserved_as: exact_match
scope_expansion_proposed: false
scope_expansion_status: exact_match
issues_generated: 4
core_issues_count: 4
expansion_issues_count: 0
issues:
  - id: TASK-004
    type: Tech Debt
    title: Fix remaining 7 positive validator fixture failures
    effort_days: 2
    priority: P1
  - id: TASK-005
    type: Tech Debt
    title: Fix all 15 negative validator fixtures
    effort_days: 1
    priority: P1
    dependencies: [TASK-004]
  - id: TASK-006
    type: Tech Debt
    title: Create REGRESSIONS.yaml
    effort_days: 0.5
    priority: P2
  - id: TASK-007
    type: Tech Debt
    title: Fix CONTEXT.md Layer 7 stale row
    effort_days: 0
    priority: P0
    status: completed
created_at: "2026-05-21T12:18:00Z"
```
