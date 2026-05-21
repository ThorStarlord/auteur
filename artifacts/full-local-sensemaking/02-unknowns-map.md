# Unknowns Map

## 1. Knowns

- 265 tests pass, 0 fail
- MODULATION layer added to `_LAYER_ORDER`, `_parse_layers` mapping fixed
- `GenreOverride` Pydantic model exists in `auteur.blueprint` with 4 types matching glossary (`safe_variation`, `compression`, `subversion`, `reclassification`). Fields: `load_bearing_expectation`, `user_override`, `override_type`, `rationale`
- `OverrideType` enum exists with all 4 values
- `ProjectIdentity.genre_overrides` field exists (`dict[str, GenreOverride]`, default factory `{}`)
- `scripts/validate-repo.py` exists (385 lines) — validates core files, YAML, registry contracts, template headers, examples. Exits with code 0 on any errors (prints warnings).
- `BibleAuditDiagnostic` is a plain class with `__init__`, not a Pydantic model. Has `as_structure_diagnostic()` adapter function.
- No CI config exists (no `.github/workflows/` directory)
- `genre.forbidden_mismatch.override_bypassed` and `genre.runway.override_bypassed` rule IDs are documented in CONTEXT.md glossary but absent from code

## 2. Unknowns

1. **U1**: What should `validate-repo.py` do when it encounters CI-relevant errors vs just printing warnings? Currently always exits 0 — CI can't detect failure.
2. **U2**: What's the exact shape of the Pydantic migration for `BibleAuditDiagnostic`? Does it keep the `RepairOptions` adapter or just become a BaseModel directly?
3. **U3**: Where should the GenreOverride diagnostic rules (`genre.forbidden_mismatch.override_bypassed`, `genre.runway.override_bypassed`) actually live — in `genres.py` or `diagnostics.py` or a new file?
4. **U4**: Does `scripts/validate-repo.py` need to be integrated into the test suite (pytest) or only into CI (GitHub Actions)?
5. **U5**: What GitHub Actions runner/os is this repo targeting?

## 3. Assumptions

1. **A1**: The test suite (`pytest -q tests`) is considered the canonical validation — `validate-repo.py` is supplementary and can be called from CI as a separate step.
2. **A2**: `BibleAuditDiagnostic` migration to Pydantic should preserve the exact same API (same field names, same `__init__` signature) so adapters like `as_structure_diagnostic()` still work.
3. **A3**: GenreOverride diagnostic rules should validate that overrides declared in `ProjectIdentity.genre_overrides` are actually referenced in the relevant genre contract checks.
4. **A4**: GitHub Actions is the CI platform (standard for Python projects).

## 4. Risks

1. **R1**: If `validate-repo.py` exits non-zero in CI, it might fail on pre-existing issues (it currently prints warnings for multiple missing/invalid things). Would need to either fix those issues first, or only exit non-zero for new failures.
2. **R2**: Pydantic migration of `BibleAuditDiagnostic` could break the wire format of `run_all_diagnostics` if any serialization/deserialization code depends on the plain-class shape.
3. **R3**: GenreOverride validation rules are conceptually defined in CONTEXT.md but the actual `genre.forbidden_mismatch` and `genre.runway` diagnostic producers don't exist yet — creating the rules implies creating the diagnostics that emit them.

## 5. Research Paths

1. **RP1** (for U1): Read `validate-repo.py` error accumulation — are the errors structured enough to separate "critical" vs "warning"? Exit-code contract needed.
2. **RP2** (for U2): Read ADR-003 to understand the full migration plan. Check if `StructureDiagnostic` (Pydantic already?) gives a model to follow.
3. **RP3** (for U3): Search for `genres.py` or genre-related diagnostic files. Check how `forbidden_mismatch` and `runway` diagnostics are currently produced.
4. **RP4** (for U4): Search for existing CI setup (GitHub Actions, Jenkins, git hooks). Check pyproject.toml for pytest config.
5. **RP5** (for U5): Check pyproject.toml and any existing CI configs.

## 6. Stopping Rule

Strong: Stop when each known has been verified against the codebase, each unknown has at least one concrete research path with a specific file target, each assumption has at least one validation action, and the `research_needed` heuristic can be computed with confidence.

## 7. Machine-readable routing

```yaml
clarity_assessment: "medium"
unknowns_count: 5
assumptions_count: 4
research_needed: true
```
