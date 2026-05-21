# Problem Frame

## 1. Raw Fog

Auteur has completed domain alignment hardening (docs-aligner), had its PRD produced, issues decomposed, triaged, and two issues implemented via TDD (MODULATION in _LAYER_ORDER, _parse_layers mapping). Three frontier items remain:

- Wire `scripts/validate-repo.py` into CI pipeline
- Refactor `BibleAuditDiagnostic` to Pydantic (ADR-003 pending)
- Add `GenreOverride` validation rules (concept documented in CONTEXT.md but no behavior)

The repo is in a "domain-aligned but not production-hardened" state — 265 tests green, but CI is absent, key diagnostics use raw dicts instead of Pydantic models, and the GenreOverride system is defined in the glossary but not enforced at the code level.

## 2. Problem Under the Problem

Auteur's weakest boundary is that its structural analysis layer runs without enforced validation. GenreOverrides are documented but not actionable — they can't be parsed, validated, or tested. BibleAuditDiagnostic is a loose dict structure that can silently drift from spec. And neither the validator scripts nor the main analysis pipeline have CI automation to catch regressions.

The root tension: the project has sophisticated *analysis* but zero *enforcement* at any layer (validation, CI, model contracts). Every piece of analysis output is trusted by convention, not by code.

## 3. Object Under Pressure

The intersection of three files/systems:

1. `scripts/validate-repo.py` — exists, works locally, but has no CI trigger or integration with the project's test suite
2. `src/auteur/structure/bible_audit.py` — contains `BibleAuditDiagnostic` (raw NamedTuple, no Pydantic model, no serialization contract)
3. `src/auteur/structure/genre.py` — contains the genre contract system. `GenreOverride` is a CONTEXT.md concept only, absent from the code

## 4. Failure Mode

If left unaddressed:
- A contributor changes `BibleAuditDiagnostic` fields and nothing catches the drift — outputs silently break
- GenreOverrides remain unimplemented while the glossary refers to them as a first-class concept — documentation vs code drift gets worse
- validate-repo.py evolves independently from the test suite, creating two validation layers that diverge

## 5. Success Condition

- `BibleAuditDiagnostic` is a Pydantic BaseModel with proper serialization/deserialization
- `validate-repo.py` is wired into CI (GitHub Actions) and produces consistent output with pytest
- `GenreOverride` is a Pydantic model with validation rules: `safe_variation`, `compression`, `subversion`, `reclassification` types, stored under `ProjectIdentity.genre_overrides`
- All 265+ existing tests still pass

## 6. What Must Be True

- ADR-003 (BibleAuditDiagnostic → Pydantic) is still the pending decision — need to confirm it's still desired
- `scripts/validate-repo.py` has an exit code contract — it must return non-zero on failure for CI to detect it
- `ProjectIdentity` model exists and can accept `genre_overrides` as an optional field
- The `genre.forbidden_mismatch.override_bypassed` and `genre.runway.override_bypassed` diagnostic rules referenced in CONTEXT.md have defined rule IDs

## 7. Next Artifact

Unknowns Map — to decompose knowns vs unknowns for each of the three frontier items.
