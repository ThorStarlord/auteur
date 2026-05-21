# PRD: Genre Override Enforcement & Diagnostic Hardening

Status: Proposed
Date: 2026-05-21
Input: artifacts/implementation-workflow-2/01-domain-alignment-report.md

## 1. Executive Summary

Resolve four contradictions between CONTEXT.md, the CI pipeline, and the codebase. The core gaps: GenreOverride is documented with enforcement rules that don't exist, validate-repo.py is decorative in CI, and BibleAuditDiagnostic is the last non-Pydantic diagnostic type.

## 2. Features

### F1: Fix validate-repo.py exit code

Add severity split. Critical errors (missing core files, invalid YAML, registry contract violations) exit non-zero. Warnings (template header formatting, example validator failures) still print but don't fail CI.

### F2: Migrate BibleAuditDiagnostic to Pydantic BaseModel

Convert `BibleAuditDiagnostic` from plain class with `__init__` to Pydantic BaseModel. Mirror `StructureDiagnostic` fields. Add `genre_recommendation_flow` field. Keep `as_structure_diagnostic()` as a simple dict conversion. Don't move the file (per ADR-003).

### F3: Create genre.py with diagnostic rules

Create `src/auteur/structure/genre.py` with `genre.forbidden_mismatch.override_bypassed` and `genre.runway.override_bypassed` diagnostic rules. Rules check `ProjectIdentity.genre_overrides` and emit `StructureDiagnostic` findings when violations exist without matching overrides. Follows ADR-010 design.

## 3. Out of Scope

- Moving `bible_audit.py` out of `auteur.structure` (ADR-003 precondition pending)
- Extracting shared diagnostic types to separate module
- Adding GenreOverride validation to `pipelines.py` or Cartographer/Bard routing
- Changing `.github/workflows/validation.yml`

## 4. Acceptance Criteria

- [F1] `validate-repo.py` exits non-zero when critical errors exist, exits 0 when only warnings
- [F1] `python scripts/check.py` propagates the exit code correctly
- [F2] `BibleAuditDiagnostic` is a Pydantic BaseModel with `severity`, `layer`, `rule`, `message`, `evidence`, `repair_options`, `genre_recommendation_flow`
- [F2] `as_structure_diagnostic()` still works and all tests pass
- [F3] `from auteur.structure.genre import check_genre_overrides` works
- [F3] `check_genre_overrides()` produces `StructureDiagnostic` findings referencing `override_bypassed` rule IDs
- [F3] 265 existing tests still pass

## 5. Machine-Readable Handoff

```yaml
artifact_id: prd
schema_version: 1
source_intent_ref: artifacts/full-local-sensemaking/05-prompt-handoff.md
user_goal_preserved_as: exact_match
scope_expansion_proposed: false
scope_expansion_requires_approval: false
scope_expansion_status: exact_match
created_at: 2026-05-21T12:00:00Z
```
