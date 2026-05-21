# Prompt Handoff

## 1. Target Skill

`implementation-workflow` (orchestrated chain: docs-aligner → to-prd → to-issues → triage → tdd → handoff)

## 2. Context to Preserve

The `full-local-sensemaking` workflow has run on the current repo state (after domain alignment hardening). It produced:

1. **Problem Frame** — three frontier items identified: validate-repo.py exit code, BibleAuditDiagnostic Pydantic migration, GenreOverride validation rules
2. **Unknowns Map** — 5 unknowns, all resolved by discovery research
3. **Discovery Findings** — all 5 research paths executed. Key finding: validate-repo.py already in CI but always exits 0
4. **Repository Sensemaking Brief** — weakest boundary: genre override enforcement. Recommended next step: fix validate-repo.py exit code

## 3. Task

Run `implementation-workflow` (docs-aligner → to-prd → to-issues → triage → tdd → handoff) on the frontier items identified by the sensemaking:

1. **P0**: Fix `validate-repo.py` exit code — add severity split, exit non-zero for critical errors instead of always exiting 0
2. **P1**: Migrate `BibleAuditDiagnostic` to Pydantic BaseModel (mirroring `StructureDiagnostic` fields)
3. **P1**: Create `genres.py` module with `genre.forbidden_mismatch.override_bypassed` and `genre.runway.override_bypassed` diagnostic rules

## 4. Constraints

- All 265 existing tests must remain green after changes
- Do not move `bible_audit.py` out of `auteur.structure` (ADR-003 precondition not met — shared types not extracted)
- `GenreOverride` Pydantic model must not change (it matches the glossary and is used in `ProjectIdentity`)
- `validate-repo.py` must maintain its in-repo contract (called from `check.py`) — only the exit code should change
- Do not modify `.github/workflows/validation.yml` — it already calls `check.py` correctly

## 5. Inputs

- `artifacts/full-local-sensemaking/04-repository-sensemaking-brief.md` — diagnosis and recommended workflow
- `artifacts/full-local-sensemaking/03-discovery-findings.md` — resolved unknowns
- `scripts/validate-repo.py` — code to fix (line 369-371)
- `src/auteur/structure/bible_audit.py` — code to refactor
- `src/auteur/structure/diagnostics.py` — Pydantic model to mirror

## 6. Expected Output

1. `validate-repo.py` exits non-zero for critical errors (or adds a `--strict` flag), warnings still print but don't fail CI
2. `BibleAuditDiagnostic` is a Pydantic `BaseModel` with same fields, adapter function simplified or removed
3. `auteur/structure/genres.py` exists with at least 2 diagnostic rules referencing `GenreOverride`
4. All 265+ tests still pass

## 7. Stop Condition

Stop when:
- `validate-repo.py` exit code fix is done and `check.py` still works
- `BibleAuditDiagnostic` migration compiles and all tests pass
- Genre rule creation doesn't break existing tests
- If any change breaks tests, stop and report the failure — do not force-push

---

## 8. Ready-to-copy Prompt

```markdown
/implementation-workflow
Run the full implementation-workflow chain (docs-aligner → to-prd → to-issues → triage → tdd → handoff) on the current repo state.

The full-local-sensemaking workflow already ran and produced these artifacts:
- artifacts/full-local-sensemaking/04-repository-sensemaking-brief.md (diagnosis)
- artifacts/full-local-sensemaking/03-discovery-findings.md (resolved unknowns)

Three P0/P1 items to implement:

1. Fix scripts/validate-repo.py exit code — currently always sys.exit(0) on error (line 371). Add severity split: critical errors exit non-zero, warnings still print. All existing behavior preserved.

2. Migrate BibleAuditDiagnostic in src/auteur/structure/bible_audit.py from plain class to Pydantic BaseModel. Mirror StructureDiagnostic fields. Keep adapter function simplified. ADR-003 says don't move the file — just refactor in place.

3. Create src/auteur/structure/genres.py with diagnostic rules genre.forbidden_mismatch.override_bypassed and genre.runway.override_bypassed. These rules check ProjectIdentity.genre_overrides against genre contract violations and emit StructureDiagnostic findings when an override-worthy mismatch is detected but no override is declared.

Constraints:
- 265 existing tests must stay green
- Do not modify .github/workflows/validation.yml
- Do not move bible_audit.py out of auteur.structure
- GenreOverride model stays as-is
```
