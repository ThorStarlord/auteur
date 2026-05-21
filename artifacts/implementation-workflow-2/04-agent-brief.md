# Agent Brief: Genre Override Enforcement & Diagnostic Hardening

## Execution Order

| Seq | ID | Title | Priority | Effort | Depends On |
|-----|----|-------|----------|--------|------------|
| 1 | ISSUE-001 | Fix validate-repo.py exit code | P0 | 0.5d | None |
| 2 | ISSUE-002 | Migrate BibleAuditDiagnostic to Pydantic | P1 | 0.5d | None |
| 3 | ISSUE-003 | Create genre.py with override_bypassed rules | P1 | 1d | ISSUE-002 |

## TDD Entry Points

### ISSUE-001: Fix validate-repo.py exit code
- Test file: `tests/test_check_script.py`
- Test approach: `subprocess.run([sys.executable, "scripts/validate-repo.py"], cwd=root)`, check return code. Currently always 0. After fix, should be non-zero for critical errors.
- Assert: When validate-repo.py encounters a missing core file (critical), it exits non-zero.

### ISSUE-002: Migrate BibleAuditDiagnostic to Pydantic
- Test file: `tests/test_story_state_commands.py`
- Test approach: `from auteur.structure.bible_audit import BibleAuditDiagnostic`. Assert it's a BaseModel (has `model_fields`), that `BibleAuditDiagnostic(**fields)` constructs correctly, and that `as_structure_diagnostic()` still works.
- Assert: `isinstance(BibleAuditDiagnostic(severity=..., layer=..., rule="...", message="..."), BaseModel)` is True.

### ISSUE-003: Create genre.py
- Test file: `tests/test_structure_analyzer.py` or new `tests/test_genre.py`
- Test approach: Create a `StoryBlueprint` with genre overrides and a genre mismatch. Assert that `check_genre_overrides()` produces diagnostics with the expected rule IDs when overrides are missing.
- Assert: `run_all_diagnostics()` with a blueprint that has `genre_overrides={}` and a genre mismatch returns diagnostics with rule `.startswith("genre.")`.

## Verification
- `python -m pytest tests -q --tb=no` must pass after each issue.
