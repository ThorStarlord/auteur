# Product Requirements Document

## 1. Executive Summary

Fix the remaining 22 validator test case failures (7 positive + 15 negative) in `scripts/test-validators.py`, fix the CONTEXT.md stale Layer 7 row (already done), and add REGRESSIONS.yaml for regression tracking.

## 2. User Goal (As Stated)

Run the implementation-workflow on the updated repo-sensemaker output to fix the remaining validator fixture quality gaps.

docs-aligner step completed — CONTEXT.md Layer 7 row fixed, domain_alignment_report.md written.

## 3. Goal Preservation & Expansion

**user_goal_preserved_as**: exact_match

**scope_expansion_proposed**: false
**scope_expansion_requires_approval**: false
**scope_expansion_status**: exact_match

## 4. Features

### Feature 1: Fix remaining validator fixture failures

The 22 failures break into 4 categories:

**Category A — CLI arg mismatch (4 validators, 8 failures)**: 
- `validate-artifact.py` takes `artifact_id [artifact_path]` — test harness passes fixture path as first positional, causing usage error
- `validate-mode-coverage.py` takes no positional args — test harness passes fixture path anyway
- `validate-output.py` requires `artifact_id artifact_path` — test harness passes only one positional
- `validate-workflow-design.py` takes optional `[registry_path]` — has `--repo-root` issue
- **Fix**: Update these validators to accept and ignore a fixture path positional when not needed, or update the test harness to not pass fixture path for these validators

**Category B — Fixture content too simple (3 validators, 6 failures)**:
- `validate-plan.py`: Fixture YAML doesn't match the exact structure validated against the registry
- `validate-run-log.py`: Valid fixture needs `validator_stack` in step; fixture needs exact failure mode class and correct source report path
- **Fix**: Create fixtures that match the actual validator schemas

**Category C — Negative fixtures not triggering (15 failures)**:
- All 15 invalid fixtures don't produce the expected `expected_error_contains` substring in their output
- **Fix**: Update each invalid fixture such that the validator actually fails with predictable output

### Feature 2: Update test harness for validator CLI compatibility (done)

The test harness in `test-validators.py` runs every validator the same way: `python validate-X.py <fixture_path> --repo-root .`. Validators that don't accept a positional fixture path will always fail.

**Fix**: Add `validator_args` frontmatter support to fixtures so the test harness can pass extra arguments.

### Feature 3: Add REGRESSIONS.yaml

Create a `tests/fixtures/REGRESSIONS.yaml` file to enable regression tracking and excluded validators.

## 5. Out of Scope

- Adding `ui-flow`/`ui-screen-spec` skills to the skill registry (separate initiative)
- Relocating `bible_audit.py` to `auteur.audit` (ADR 003)
- Implementing `--repair`/`--accept` CLI hooks for `auteur audit`

## 6. Acceptance Criteria

### Feature 1
- [ ] 4 CLI-arg-mismatch validators accept the test harness calling convention without usage errors
- [ ] `validate-plan.py` fixture passes with all Section 11 structure checks satisfied
- [ ] `validate-run-log.py` fixture passes (no errors)
- [ ] `validate-skill-improvement-plan.py` fixture passes (no errors)
- [ ] All 15 invalid fixtures produce output containing their `expected_error_contains` string
- [ ] `scripts/test-validators.py` reports >= 15 passing cases

### Feature 2
- [ ] Test harness reads `validator_args` from fixture frontmatter
- [ ] Validators with non-standard CLI signatures can be properly tested

### Feature 3
- [ ] `REGRESSIONS.yaml` exists with `excluded_validators` and `required_cases`

## 7. Non-Functional Requirements

- All 264 existing tests must continue to pass
- No changes to Engine v1 CLI or core logic

## 8. Approval Gate

Not required — exact match.

## 9. Machine-Readable Handoff

```yaml
artifact_id: prd
schema_version: 1
source_intent_ref: artifacts/domain_alignment_report.md
user_goal_preserved_as: exact_match
scope_expansion_proposed: false
scope_expansion_requires_approval: false
scope_expansion_status: exact_match
created_at: "2026-05-21T12:15:00Z"
```
