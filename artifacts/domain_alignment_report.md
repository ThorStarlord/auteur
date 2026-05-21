# Domain Alignment Report

## 1. Repository Analyzed
**Auteur** — `H:\GithubRepositories\auteur`
A narrative engineering toolkit for long-form fiction. Whole-story structure engine first, chapter drafting engine second.

## 2. Contradictions

### C1: Layer Numbering Mismatch — Theme at Layer 8 vs Layer 9
- **Claim**: CONTEXT.md 9-Layer Engine table places "Resonance / Coherence" at Layer 9 with `theme` as its programmatic key.
- **Reality**: `src/auteur/structure/state.py` `_LAYER_ORDER` maps `DiagnosticLayer.THEME` to Layer 8, skipping `MODULATION` entirely (only showing layers 1-8).
- **Evidence**:
  - `CONTEXT.md` lines 143-153: "| **Layer 7** | **Representation** | ... | Layer 8: Modulation | Layer 9: Resonance/Coherence |"
  - `src/auteur/structure/state.py` lines 166-173: `(8, DiagnosticLayer.THEME, "Theme / Resonance")` — no MODULATION entry.
- **Resolution**: Update `state.py` `_LAYER_ORDER` to include Layer 9 (`THEME` at 9) and Layer 8 (`MODULATION` at 8), or update CONTEXT.md to match the programmatic reality.

### C2: `open-ended` vs `open_ended` — Canonical Form Mismatch
- **Claim**: CONTEXT.md uses `open-ended` (hyphenated) as the canonical form for Recommendation Mode.
- **Reality**: `src/auteur/identity.py` `RecommendationMode` enum has `OPEN_ENDED = "open_ended"` (underscore). The CLI converts `"open-ended"` to `"open_ended"` at runtime.
- **Evidence**:
  - `CONTEXT.md` line 115: "open-ended" mode is an exploratory escape hatch.
  - `src/auteur/identity.py` line ~15: `OPEN_ENDED = "open_ended"`
  - `src/auteur/cli.py` line ~150: `if rec_mode == "open-ended": rec_mode = "open_ended"`
- **Resolution**: Add CONTEXT.md glossary entry noting the CLI accepts `--recommend-mode open-ended` which normalizes to enum value `"open_ended"`. Or update CONTEXT.md to document both forms.

### C3: `state_check` vs `auteur audit` — Layer 7 Ownership
- **Claim**: CONTEXT.md Layer-to-Command Matrix says Layer 7 (Representation) is owned by `auteur audit` / Cartographer.
- **Reality**: `auteur audit` does NOT call `outline_audit` — it calls `run_all_diagnostics(blueprint, bible)` without passing an outline. Layer 7 is only reachable via `auteur state check --outline <path>`.
- **Evidence**:
  - `CONTEXT.md` Layer-to-Command Matrix: "| **Layer 7** | ... | `auteur audit` / Cartographer |"
  - `src/auteur/cli.py` `_cmd_audit` calls `run_all_diagnostics(blueprint, bible)` — no outline kwarg.
  - `src/auteur/cli.py` `state check` branch loads outline and passes it: `state_check(args.project, outline=outline)`.
- **Resolution**: Update CONTEXT.md matrix to say `auteur state check --outline` owns Layer 7, or add `--outline` support to `auteur audit`.

### C4: `scripts/validate-repo.py` Hyphen vs Expected Underscore
- **Claim**: The file `scripts/validate_repo.py` (underscore) is referenced in expectations.
- **Reality**: The actual file is `scripts/validate-repo.py` (hyphen). `scripts/check.py` references it correctly with the hyphenated name.
- **Evidence**:
  - `scripts/check.py` line 11: `(sys.executable, "scripts/validate-repo.py")`
  - Filesystem: `validate-repo.py` exists, `validate_repo.py` does not.
- **Resolution**: No code change needed — `check.py` already references the correct filename. Resolve by noting the correct name in docs.

## 3. Fuzzy Language

### F1: "Diagnostic" — Three Meanings
- **Current Usage**: (a) A deterministic finding from any diagnostic pass (CONTEXT.md glossary). (b) `StructureDiagnostic` Pydantic model in `diagnostics.py`. (c) `BibleAuditDiagnostic` hand-rolled class in `bible_audit.py`.
- **Proposed Canonical Term**: Keep "StructureDiagnostic" vs "BibleAuditDiagnostic" as distinct types. CONTEXT.md should note the asymmetry as temporary (ADR-003).
- **Evidence**: `src/auteur/structure/bible_audit.py` line 37: `class BibleAuditDiagnostic:` — hand-rolled, not Pydantic.

### F2: "Proposal" — Two Sources, Same Model
- **Current Usage**: `propose_repairs_from_diagnostics()` (source_domain="structure") and `propose_repairs_from_audit_diagnostics()` (source_domain="bible_audit") both produce `StructureProposal`.
- **Proposed Canonical Term**: Keep as-is — `source_domain` field discriminates. Not fuzzy in code, but the naming overload is worth noting.
- **Evidence**: `src/auteur/structure/proposal_generation.py` lines ~320 and ~420.

## 4. Undocumented Concepts

### U1: `GenreOverride` / `OverrideType` — Four Override Classes
- **Concept**: GenreOverride model with four types: safe_variation, compression, subversion, reclassification.
- **Definition**: Declared author overrides that bypass genre contract violations when the author has a deliberate creative reason.
- **Where Found**: `src/auteur/blueprint.py` — `OverrideType` enum, `GenreOverride` model. Used in `analyzer.py` for forbidden mismatch and runway checks.
- **Relationships**: Used by `genre.forbidden_mismatch.override_bypassed` and `genre.runway.override_bypassed` diagnostic rules in `analyzer.py`.

### U2: `ScopeContract` Model Fields
- **Concept**: The full ScopeContract model fields: recommended_complexity, narrative_runway, mechanical_load, setting_footprint, etc.
- **Definition**: A detailed budget specifying the story's complexity, runway, mechanical load, and scope warnings.
- **Where Found**: `src/auteur/blueprint.py` — `ScopeContract` model.
- **Relationships**: Stored under `StructuralConstants.scope_contract`. Related to ScopeProfile (on GenreContract).

### U3: `MediumContract` Fields
- **Concept**: Full MediumContract model with medium, format, release_model, interaction_model, unit_of_delivery, etc.
- **Definition**: The delivery grammar for a story — not just the medium but how it's formatted, released, and interacted with.
- **Where Found**: `src/auteur/blueprint.py` — `MediumContract` model.
- **Relationships**: Stored under `ProjectIdentity.medium_contract`.

### U4: `SupportFunction` Enum Values
- **Concept**: Seven support functions: complicats, mirrors, contrasts, escalates, reveals, pressures_change, pays_off.
- **Definition**: How a subordinate thread serves the main thread.
- **Where Found**: `tests/test_structure_analyzer.py`, `src/auteur/blueprint.py` — `SupportFunction` enum.
- **Relationships**: Used by `diagnostics.py` rule `thread.supports_main_by.lacks_escalation_or_pressure`.

### U5: `ProposalType.GENERATION`
- **Concept**: ProposalType enum with GENERATION and REPAIR values.
- **Definition**: GENERATION creates proposals from scratch (e.g., propose_story_engine), REPAIR creates proposals from diagnostics.
- **Where Found**: `src/auteur/blueprint.py` — `ProposalType` enum.
- **Relationships**: Used in `proposal_generation.py`.

### U6: `CartographerOutline` Model
- **Concept**: Schema model for validated cartographer outline files.
- **Definition**: Pydantic model representing a validated Cartographer outline with scene structure, character state changes, and POV tracking.
- **Where Found**: Referenced in `proposal_resolution.py` line ~160.
- **Relationships**: Used by outline audit and state prepare commands.

## 5. ADR Candidates

### ADR-011: CI Pipeline Architecture
- **Decision**: `scripts/check.py` is the single CI entrypoint, orchestrating three validation steps: test-validators, validate-repo, pytest.
- **Evidence**: `.github/workflows/validation.yml` — runs `python scripts/check.py`. `scripts/check.py` — hardcoded tuple of three commands.
- **Alternatives**: pytest markers, Makefile targets, tox/nox environments.
- **Reversibility**: Medium — changing CI pipeline affects all PRs and the main branch guard.
- **ADR Status**: `not_created` — needs creation.

### ADR-012: Per-Agent Model Routing
- **Decision**: Different LLM models for different agents (Bard, Cartographer, Critic) via `build_client(provider, model, agent_type=..., blueprint=...)` and `StoryBlueprint.agent_models` dict.
- **Evidence**: `src/auteur/llm/factory.py`, `src/auteur/cli.py` — all agent invocations pass `agent_type`.
- **Alternatives**: Single model for all agents, model discovery from blueprint only.
- **Reversibility**: High — affects cost, latency, and output quality system-wide.
- **ADR Status**: `not_created` — has CONTEXT.md glossary entry but no ADR.

### ADR-013: `state_confirm` Recovery Merge Workflow
- **Decision**: `state_confirm` validates and merges recovery-run locked layers into blueprint and bible in a single transactional operation with rollback on validation failure.
- **Evidence**: `src/auteur/structure/state.py` — `state_confirm()` function.
- **Alternatives**: Separate blueprint-update and bible-update commands.
- **Reversibility**: Medium — once merged, the atomic operation is hard to undo manually.
- **ADR Status**: `not_created` — has PRD at `docs/prd-story-state-commands.md` but no ADR.

## 6. Glossary Mutations

| Action | Term | Before | After | Section |
|--------|------|--------|-------|---------|
| `added` | GenreOverride | (not present) | Declared author overrides that bypass genre contract violations with four classification types | Language |
| `added` | ScopeContract (fields) | (not present) | Model-level explanation of complexity, runway, and mechanical load fields | Language |
| `added` | MediumContract (fields) | (not present) | Model-level explanation of format, release, interaction, and failure mode fields | Language |
| `resolved_ambiguity` | Diagnostic (three meanings) | "A deterministic finding" (generic) | StructureDiagnostic (Pydantic) vs BibleAuditDiagnostic (hand-rolled, ADR-003) | Language |
| `updated` | Layer 7 ownership | "auteur audit / Cartographer" | "auteur state check --outline" | Layer-to-Command Matrix |
| `added` | CI Pipeline Architecture | (not present) | ADR-011 entry | (new ADR) |
| `added` | Per-Agent Model Routing | (not present) | ADR-012 entry | (new ADR) |
| `added` | state_confirm Recovery Merge | (not present) | ADR-013 entry | (new ADR) |
| `added` | open_ended (underscore) | (not present) | Note that CLI normalizes `open-ended` to enum `open_ended` | Language (Recommendation Mode) |

## 7. ADRs Created

| File | Title | Rationale |
|------|-------|-----------|
| `docs/adr/011-ci-pipeline-architecture.md` | CI Pipeline Architecture | CI entrypoint design affects all contributions and is hard to change safely. |
| `docs/adr/012-per-agent-model-routing.md` | Per-Agent Model Routing | Architectural decision affecting cost, latency, and output quality with no existing documentation. |
| `docs/adr/013-state-confirm-recovery-merge.md` | state_confirm Recovery Merge Workflow | Atomic merge operation with rollback is a hard-to-reverse design choice. |

## 8. Summary
- Contradictions found: 4
- Fuzzy terms sharpened: 2
- Undocumented concepts discovered: 6
- ADRs created: 3
- Glossary entries added: 6
- Glossary entries updated: 2
