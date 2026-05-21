# Agent Brief

## 1. Issue List Consumed

- **Issue list**: `artifacts/issue_list.md`
- **Total**: 4 issues (1 completed: TASK-007)

## 2. Escalation Check

**No escalation**.

## 3. Dependency Graph

```
TASK-004 (independent)
TASK-005 (depends on TASK-004 — negative fixtures need valid ones working first)
TASK-006 (independent — can be done in parallel with TASK-004)
TASK-007 (completed)
```

## 4. Execution Order

| Seq | ID | Title | Priority | Effort | Depends On |
|-----|----|-------|----------|--------|------------|
| 1 | TASK-006 | Create REGRESSIONS.yaml | P2 | 0.5 days | — |
| 2 | TASK-004 | Fix 7 positive validator fixture failures | P1 | 2 days | — |
| 3 | TASK-005 | Fix all 15 negative validator fixtures | P1 | 1 day | TASK-004 |

TASK-006 first (it's quick and independent, fast win). TASK-004 is the meat of the work. TASK-005 follows once positive fixtures are stable.

## 5. TDD Entry Points

### TASK-006: Create REGRESSIONS.yaml
**File**: `tests/test_check_script.py`
**Function**: `test_regressions_yaml_exists`
**Assert**: `(ROOT / "tests" / "fixtures" / "REGRESSIONS.yaml").exists()`
**Why this test first**: Minimal RED — file doesn't exist yet.

### TASK-004: Fix positive fixtures
**File**: `tests/test_check_script.py`
**Function**: `test_test_validators_positive_passes`
**Assert**: All positive validator fixtures pass (0 unexpected failures in valid/ directory)
**Why this test first**: Currently 7 fail. Fix each until all pass.

### TASK-005: Fix negative fixtures
**File**: `tests/test_check_script.py`
**Function**: `test_test_validators_negative_passes`
**Assert**: All invalid validator fixtures trigger failure with correct error messages
**Why this test first**: Currently 15 negative fixtures don't trigger expected failures.

## 6. Clarification Flags

**All issues are clear. No clarification needed.**

## 7. Machine-Readable Handoff

```yaml
artifact_id: agent_brief
schema_version: 1
source_intent_ref: artifacts/issue_list.md
issue_list_ref: artifacts/issue_list.md
execution_order:
  - TASK-006
  - TASK-004
  - TASK-005
issues_ready: 3
issues_flagged: 0
escalation_required: false
created_at: "2026-05-21T12:20:00Z"

issues:
  - id: TASK-006
    title: Create REGRESSIONS.yaml
    sequence: 1
    priority: P2
    effort_days: 0.5
    dependencies: []
    status: ready
    tdd_entry_point:
      file: tests/test_check_script.py
      function: test_regressions_yaml_exists
      assert: True
  - id: TASK-004
    title: Fix remaining 7 positive validator fixture failures
    sequence: 2
    priority: P1
    effort_days: 2
    dependencies: []
    status: ready
    tdd_entry_point:
      file: tests/test_check_script.py
      function: test_test_validators_positive_passes
      assert: All positive fixtures pass
  - id: TASK-005
    title: Fix all 15 negative validator fixtures
    sequence: 3
    priority: P1
    effort_days: 1
    dependencies: [TASK-004]
    status: ready
    tdd_entry_point:
      file: tests/test_check_script.py
      function: test_test_validators_negative_passes
      assert: All invalid fixtures fail with correct expected_error_contains
```
