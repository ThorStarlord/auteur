# Repository Sensemaking Brief

## 1. Repository goal

Auteur is a narrative engineering system — a "literary compiler" for long-form fiction. It takes a story blueprint and produces structured analysis (diagnostics), scene outlines, and eventually modulated draft output. The repo contains the structure engine (diagnostic layers 1-9), CLI, Pydantic models, validator scripts, and orchestration workflows.

## 2. Current shape

- 265 tests, all green
- Uncommitted Layer 7 (Scene Representation) work — `outline_audit.py` exists and is wired into `run_all_diagnostics`
- CI already set up: `.github/workflows/validation.yml` → `scripts/check.py` → [test-validators, validate-repo, pytest]
- `validate-repo.py` exists but always exits 0 (prints warnings only)
- `BibleAuditDiagnostic` is a plain class (non-Pydantic) — adapter via `as_structure_diagnostic()` bridges to Pydantic `StructureDiagnostic`
- `GenreOverride` Pydantic model exists with 4 types; `ProjectIdentity.genre_overrides` field exists
- No genre validation diagnostic rules implemented — `genre.forbidden_mismatch.override_bypassed` and `genre.runway.override_bypassed` are glossary-only concepts
- ADR-003 documents bible_audit.py as temporary resident pending shared type extraction
- 3 new ADRs from recent domain alignment: 011 (CI), 012 (model routing), 013 (state_confirm recovery)

## 3. Strong signals

- Full test suite passes with 265 tests
- CI pipeline exists and works — just the validate-repo step is a no-op
- Pydantic model discipline is strong — `StructureDiagnostic`, `GenreOverride`, `ProjectIdentity` all use Pydantic
- The adapter pattern (`as_structure_diagnostic`) cleanly separates plain and Pydantic layers
- Glossary and code have been recently aligned (GenreOverride types match CONTEXT.md)

## 4. Missing pieces

- GenreOverride validation rules — documented in glossary but code doesn't enforce them
- `validate-repo.py` has no exit-code contract for CI — it's decorative
- `BibleAuditDiagnostic` is the last non-Pydantic diagnostic type — a refactoring island
- No `genres.py` module exists — genre validation is scattered or absent

## 5. Improvement opportunities

- `validate-repo.py` could differentiate "critical" vs "warning" errors and exit non-zero for criticals
- `BibleAuditDiagnostic` → Pydantic BaseModel migration after shared type extraction
- Genre diagnostic rules: minimal first pass creates a `genres.py` with override-awareness

## 6. Weakest boundary

**Genre override enforcement** — the intersection of documented intent and coded behavior. CONTEXT.md defines GenreOverride as a first-class concept with specific diagnostic rules (`override_bypassed`), but those rules don't exist. The Pydantic model stores the data but no code reads it for validation. This creates a documentation-vs-code drift that will compound if new diagnostics are added referencing these rules.

Counter-argument: `validate-repo.py`'s decorative exit code is a simpler, higher-leverage fix — CI currently can't detect repo drift at all. But fixing the exit code is a one-line change. Genre override rules are an architectural gap that requires design and implementation.

## 6.5. Problem classification (fog type)

**architecture_fog** — the weakest boundary is between the domain model (GenreOverride glossary + Pydantic model) and the enforcement layer (missing diagnostic rules). This is a structural/code design problem, not a documentation or product problem.

## 7. Evidence

- `src/auteur/blueprint.py` — `GenreOverride` Pydantic model exists with all 4 OverrideTypes
- `src/auteur/structure/diagnostics.py` — `StructureDiagnostic` is Pydantic, has `genre_recommendation_flow` field
- `src/auteur/structure/bible_audit.py` — `BibleAuditDiagnostic` is plain class, not Pydantic
- `scripts/validate-repo.py` — L369-371 always exits 0
- `.github/workflows/validation.yml` — CI exists, runs check.py
- `scripts/check.py` — chains test-validators → validate-repo → pytest
- `CONTEXT.md` — GenreOverride glossary entry references `genre.forbidden_mismatch.override_bypassed` and `genre.runway.override_bypassed`

## 8. Evidence excerpts

```yaml
evidence_excerpts:
  - file: src/auteur/blueprint.py
    lines: "ProjectIdentity.genre_overrides field"
    quote: "annotation=dict[str, GenreOverride] required=False default_factory=dict"
    supports_claim: "GenreOverride storage exists but no enforcement"
  - file: scripts/validate-repo.py
    lines: L369-L371
    quote: "sys.exit(0) called after printing errors"
    supports_claim: "validate-repo is decorative in CI"
  - file: src/auteur/structure/bible_audit.py
    lines: L36-L50
    quote: "class BibleAuditDiagnostic with __init__ (not BaseModel)"
    supports_claim: "Refactoring island — last non-Pydantic diagnostic"
```

## 9. Why this boundary matters

If GenreOverride remains glossary-only while new diagnostic rules are added (e.g., a structural forces check that should consider overrides), those new rules will miss the override context. The documentation and code will drift further, requiring a larger reconciliation later. Meanwhile, the decorative `validate-repo.py` exit code means CI silently ignores repo validation failures — a smaller but more immediately practical gap.

## 10. Candidate next steps

1. Fix `validate-repo.py` exit code — add severity split, exit non-zero for critical errors
2. Create `genres.py` with `forbidden_mismatch` and `runway` override-aware diagnostic rules
3. Migrate `BibleAuditDiagnostic` to Pydantic after shared type extraction
4. Extract `DiagnosticLayer`, `DiagnosticSeverity`, `RepairOptions` to shared module (precondition for both 2 and 3)

## 11. Recommended next step

**Fix `validate-repo.py` exit code** — one-line change that makes CI actually enforce repo validation. This is the highest-leverage, lowest-effort improvement. It also creates a precedent for `check.py` to be a real CI gate.

## 12. Recommended workflow

`implementation-workflow` — the alignment, PRD, issues, triage, TDD, handoff chain. The problem is architecture_fog, and this is the standard workflow for code/design problems.

## 13. Machine-readable handoff

### Stage 1: Intent-Aware Fields (Required)
```yaml
artifact_id: repository_sensemaking_brief
source_intent_ref: artifacts/full-local-sensemaking/01-problem-frame.md
user_implied_fog_type: architecture_fog
primary_fog_type: architecture_fog
diagnosis_conflict: false
escalation_recommended: false
```

### Standard Fields
```yaml
recommended_workflow_id: implementation-workflow
recommended_execution_mode: guided_execution
weakest_boundary: genre_override_enforcement
required_inputs:
  - user_intent
  - repository_state
```

### Complete Example
```yaml
artifact_id: repository_sensemaking_brief
schema_version: 1
source_intent_ref: artifacts/full-local-sensemaking/01-problem-frame.md
recommended_workflow_id: implementation-workflow
recommended_execution_mode: guided_execution
weakest_boundary: genre_override_enforcement
required_inputs:
  - user_intent
  - repository_state
user_implied_fog_type: architecture_fog
primary_fog_type: architecture_fog
diagnosis_conflict: false
escalation_recommended: false
created_at: 2026-05-21T12:00:00Z
```

## 14. Ready-to-copy prompt

```markdown
/implementation-workflow
The repo-sensemaker found the weakest boundary is genre override enforcement — GenreOverride is stored in Pydantic but no diagnostic rules consume it. The highest-leverage next step is fixing validate-repo.py exit code, then creating the genre override validation rules. Discovery findings are at artifacts/full-local-sensemaking/03-discovery-findings.md.
```
