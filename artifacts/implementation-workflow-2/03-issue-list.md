# Issue List: Genre Override Enforcement & Diagnostic Hardening

Source PRD: artifacts/implementation-workflow-2/02-prd.md
Publication: skipped (local only)

## Issues Generated

### Issue 1: Fix validate-repo.py exit code contract
- Type: Bug
- Title: Add severity split to validate-repo.py — critical errors exit non-zero
- Effort: 0.5 day / Priority: P0 / Dependencies: None
- Files: `scripts/validate-repo.py`
- Acceptance: `python scripts/validate-repo.py` exits non-zero when critical errors exist (missing core files, invalid YAML, registry violations). Warnings (template headers, example errors) still print but don't fail.

### Issue 2: Migrate BibleAuditDiagnostic to Pydantic BaseModel
- Type: Refactor
- Title: Convert BibleAuditDiagnostic from plain class to Pydantic BaseModel
- Effort: 0.5 day / Priority: P1 / Dependencies: None
- Files: `src/auteur/structure/bible_audit.py`, `src/auteur/structure/diagnostics.py` (read-only reference)
- Acceptance: `BibleAuditDiagnostic` is a BaseModel with fields: severity, layer, rule, message, evidence, repair_options, genre_recommendation_flow. `as_structure_diagnostic()` still works. All 265 tests pass.

### Issue 3: Create genre.py with override_bypassed diagnostic rules
- Type: Feature
- Title: Create genre.py module with forbidden_mismatch and runway override validation rules
- Effort: 1 day / Priority: P1 / Dependencies: Issue 2
- Files: `src/auteur/structure/genre.py` (new), `src/auteur/structure/analyzer.py` (wire it in)
- Acceptance: `check_genre_overrides()` produces `StructureDiagnostic` findings with rule IDs `genre.forbidden_mismatch.override_bypassed` and `genre.runway.override_bypassed`. `run_all_diagnostics` calls it. All tests pass.

## Release Scope

Total issues: 3
Total effort: 2 days
Core features: 3
