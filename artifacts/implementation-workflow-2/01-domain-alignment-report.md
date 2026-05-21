# Domain Alignment Report — Genre Override Enforcement & Diagnostic Hardening

Status: Proposed
Date: 2026-05-21
Input: artifacts/full-local-sensemaking/*

## Contradictions Found

### C1: CONTEXT.md GenreOverride claims enforced diagnostic rules that don't exist

The glossary entry says GenreOverride is "Enforced by `genre.forbidden_mismatch.override_bypassed` and `genre.runway.override_bypassed` diagnostic rules." Neither rule ID exists in any code file. No `genres.py` module exists.

**Evidence**: CONTEXT.md GenreOverride entry. `grep -r "override_bypassed" src/` returns nothing.

### C2: validate-repo.py claims to validate but always exits 0

The CI pipeline (`validation.yml` → `check.py` → `validate-repo.py`) calls validate-repo as step 2 of the validation chain, but it always exits 0 even on errors. This makes the CI step decorative — failures are printed but never fail the build.

**Evidence**: `scripts/validate-repo.py` L369-371: `sys.exit(0)` unconditional.

### C3: BibleAuditDiagnostic is the only non-Pydantic diagnostic type

`StructureDiagnostic` is a Pydantic BaseModel. `BibleAuditDiagnostic` is a plain class with `__init__`. The adapter function `as_structure_diagnostic()` bridges them but adds unnecessary complexity. ADR-010 requires `genre_recommendation_flow` on diagnostics — this should be a BaseModel field like `StructureDiagnostic`.

**Evidence**: `src/auteur/structure/diagnostics.py` has `StructureDiagnostic` as BaseModel. `src/auteur/structure/bible_audit.py` has `BibleAuditDiagnostic` as plain class.

### C4: BibleAuditDiagnostic doesn't carry genre_recommendation_flow

ADR-010 section 2 defines `genre_recommendation_flow` on `StructureDiagnostic`. `BibleAuditDiagnostic` is a separate class and doesn't have this field, so Bible audit findings can't carry genre override context.

**Evidence**: `StructureDiagnostic.genre_recommendation_flow` exists. `BibleAuditDiagnostic` lacks it.

## Summary

| # | Severity | Area | Fix |
|---|----------|------|-----|
| C1 | HIGH | GenreOverride | Create `genres.py` with `override_bypassed` rules |
| C2 | MEDIUM | CI hardening | Fix validate-repo.py exit code |
| C3 | MEDIUM | BibleAuditDiagnostic | Migrate to Pydantic BaseModel (in place, per ADR-003) |
| C4 | LOW | BibleAuditDiagnostic | Add `genre_recommendation_flow` field during migration |
