# Discovery Findings

## Research Path Results

### RP1: validate-repo.py exit code contract

**Finding**: `validate-repo.py` currently calls `sys.exit(0)` unconditionally on line 371. It accumulates errors in a list and prints them as "Validation warnings (ignored for execution)". No distinction is made between warnings and failures.

The CI pipeline (`validation.yml`) runs `check.py` which calls `validate-repo.py` as step 2. If the exit code were fixed, CI would catch failures — but only if the pre-existing issues (recursive orchestrator calls, unregistered artifacts) are cleaned up first, or if a "critical vs warning" severity split is introduced.

**Evidence**: `scripts/validate-repo.py` L369-L371:
```python
if errors:
    print("Validation warnings (ignored for execution):")
    for err in errors:
        print(f" - {err}")
    sys.exit(0)
```

### RP2: BibleAuditDiagnostic Pydantic migration

**Finding**: `BibleAuditDiagnostic` is a plain class with `__init__`, using the same field shape as `StructureDiagnostic` but not inheriting from it. `StructureDiagnostic` is already a Pydantic `BaseModel`. The adapter function `as_structure_diagnostic()` converts between them.

ADR-003 says `bible_audit.py` is a temporary resident and the move precondition requires extracting shared types first. The migration to Pydantic would be straightforward: make `BibleAuditDiagnostic` a `BaseModel` with the same fields. The adapter function becomes a simple `.model_dump()` / `StructureDiagnostic(**d)` conversion, or `BibleAuditDiagnostic` could be split out entirely.

**Key constraint**: `DiagnosticLayer`, `DiagnosticSeverity`, and `RepairOptions` are currently in `diagnostics.py`. Any migration must either keep them there or extract them first — a separate architectural decision.

**Evidence**: `src/auteur/structure/bible_audit.py` L36-L50 (plain class), `src/auteur/structure/diagnostics.py` L37-L44 (Pydantic model).

### RP3: GenreOverride diagnostic rules

**Finding**: No `genre.forbidden_mismatch.override_bypassed` or `genre.runway.override_bypassed` rules exist anywhere in the codebase. No `genres.py` file exists. The genre validation system currently handles:
- Genre selection (via `StoryEngine.genre`)
- Genre override storage (via `ProjectIdentity.genre_overrides` → `GenreOverride` Pydantic model)
- Medium and scale validation in the analyzer

The diagnostic rules documented in CONTEXT.md are aspirational — they describe what the system *should* do but hasn't been implemented yet. Creating them would require:
1. Creating a `genres.py` or extending `analyzer.py` with override-aware diagnostics
2. Adding `forbidden_mismatch` and `runway` rule IDs to the diagnostic system
3. Making genre contract checks aware of `ProjectIdentity.genre_overrides`

**Evidence**: `from auteur.blueprint import GenreOverride` works (model exists), `ProjectIdentity.genre_overrides` field exists, but `grep -r "override_bypassed" src/` returns nothing.

### RP4: CI integration

**Finding**: CI is already set up. `.github/workflows/validation.yml` runs on pull_request and push to main. It uses `ubuntu-latest` with Python 3.11, installs dev dependencies, and runs `python scripts/check.py`. The `check.py` script chains: `test-validators.py` → `validate-repo.py` → `pytest tests`.

The gap is not missing CI but that `validate-repo.py` exits 0 even on errors, making the second step a no-op from a CI perspective. The pytest step (step 3) is the actual gate.

### RP5: Test suite integration

**Finding**: `validate-repo.py` is NOT part of the pytest suite. It's called as a separate step in `check.py`. There's a separate `test_check_script.py` test file that validates the `check.py` runner itself.

## Resolved Unknowns

- **U1** (exit code contract): Needs fix — should exit non-zero for real errors, or add severity split
- **U2** (Pydantic migration shape): Should mirror `StructureDiagnostic` as BaseModel — same fields
- **U3** (genre rule location): No existing file — would need new module or analyzer extension
- **U4** (CI integration path): Already wired — just needs exit code fix
- **U5** (CI platform): GitHub Actions, ubuntu-latest, Python 3.11

## Updated Assumptions

- **A1** (canonical validation): Confirmed — pytest is step 3, validate-repo is supplementary
- **A2** (Pydantic API preservation): Feasible — adapter. `as_structure_diagnostic()` can simplify
- **A3** (GenreOverride rule design): Needs design work — rules reference glossary but don't exist
- **A4** (GitHub Actions): Confirmed

## Stopping Rule

Strong stop condition met: all 5 unknowns have concrete answers backed by code evidence. The `research_needed` count drops from 5 to 0 after this discovery pass.
