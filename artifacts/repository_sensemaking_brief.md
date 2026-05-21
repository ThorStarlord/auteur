# Repository Sensemaking Brief

## 1. Repository goal
The goal of Auteur is to provide a narrative engineering toolkit for long-form fiction. It aims to prevent narrative drift (lore inconsistencies and character location teleportation) by structuring narrative design and execution around a 9-Layer Engine, prioritizing a whole-story structure engine first and a chapter drafting engine second.

## 2. Current shape
- `src/auteur/structure/state.py` implements the unified multi-layer state manager and coordinates CLI commands (`check`, `update`, `prepare`, `canon`, `confirm`).
- `src/auteur/structure/bible_audit.py` runs deterministic checks for location teleportation using the `StoryBible` event log.
- `src/auteur/structure/analyzer.py` runs structural diagnostics for layers 1 to 5, plus layer 9.
- `tests/` contains unit tests for testing state commands, proposals, and character teleportation.
- `docs/` contains PRDs and architecture decision records (like ADR 003).

## 3. Strong signals
- The Pydantic model validations for `StoryBlueprint` and `StoryBibleModel` provide solid schema-enforced boundaries for the core project ledgers.
- The unit test suite is comprehensive and passes completely.
- The 9-layer cascading philosophy is well-documented in `CONTEXT.md` and provides a clear theoretical framework.

## 4. Missing pieces
- There is no automated validation mapping for Layer 8 (Modulation) or Layer 9 (Resonance/Coherence Check) inside the `_LAYER_ORDER` of `state_check`.
- The CLI command `state check` does not check `outline.yaml` (Layer 7 representation), ignoring the scene sequence constraints mentioned in `docs/prd-story-state-commands.md`.
- `auteur audit` lacks the full interactive pipeline CLI hooks for `--repair` and `--accept` as detailed in the `CONTEXT.md` command ownership matrix.

## 5. Improvement opportunities
- Moving `bible_audit.py` out of `auteur.structure` (as proposed in ADR 003) to a shared area like `auteur.audit` to eliminate domain boundary blending.
- Extending `state_check` to run validation on scene outlines (`outline.yaml`) to ensure that scene-level representation matches the bible carriers before drafting.

## 6. Weakest boundary
The weakest boundary in the current codebase falls under **Ghost Features** and **Vocabulary Drift**. 

**Logic Trace**:
1. PRD (docs/prd-story-state-commands.md) describes `state check` as running a 'Carrier Check' to verify transition consistency across `bible.json` and `outline.yaml`.
2. Inspecting `src/auteur/structure/state.py` shows that `state_check` loads `blueprint.yaml` and `bible.json` but completely ignores `outline.yaml`.
3. Inspecting `src/auteur/structure/analyzer.py` confirms that `run_all_diagnostics` only runs structural blueprint validation and location audits on `StoryBible` (Layer 6).
4. Therefore, the outlined Layer 7 representation checks against `outline.yaml` are undocumented ghost features in the implementation.

Specifically, the CLI subcommand `auteur state check` is designed to verify character state transition consistency across both `bible.json` and `outline.yaml`. However, the code in `src/auteur/structure/state.py` only instantiates and passes the blueprint and bible models to `run_all_diagnostics()`. The outline file (`outline.yaml`) is never loaded, read, or validated during this check, meaning scene-level carrier transitions are completely unenforced. Additionally, the location of `bible_audit.py` within `auteur.structure` is a case of vocabulary/domain drift, as noted in `docs/adr/003-bible-audit-placement.md`.

## 6.5. Problem classification (fog type)
- **architecture_fog** (Code structure boundaries, missing validation of outline files, and structural placement anomalies).

## 7. Evidence
- In `src/auteur/structure/state.py:144`, `state_check` invokes `run_all_diagnostics` passing only the blueprint and the bible.
- In `src/auteur/structure/analyzer.py:21-38`, `run_all_diagnostics` only calls `analyze_structure` and `audit_bible_locations`, omitting any outline validation logic.
- In `src/auteur/structure/bible_audit.py:52`, the `audit_bible_locations` function only takes a `StoryBible` instance and does not inspect `outline.yaml`.

## 8. Evidence excerpts
```yaml
evidence_excerpts:
  - file: src/auteur/structure/state.py
    lines: L144-L145
    quote: "raw_diagnostics = run_all_diagnostics(blueprint, bible)"
    supports_claim: "The state_check command runs diagnostics on blueprint and bible but does not load or validate outline.yaml, despite the PRD stating it should verify character state transition consistency across bible.json and outline.yaml."
  - file: src/auteur/structure/bible_audit.py
    lines: L52-L53
    quote: "def audit_bible_locations(bible: StoryBible) -> list[BibleAuditDiagnostic]:"
    supports_claim: "The bible audit process runs entirely on the StoryBible event log and does not ingest or analyze scene outlines."
```

## 9. Why this boundary matters
If the scene outlines in `outline.yaml` are not validated against the carrier states in `bible.json` before drafting, the drafting pipeline will execute using inconsistent scene constraints. This results in narrative drift accumulating at draft time, forcing expensive and token-heavy LLM repair loops or leading to lore rot.

## 10. Candidate next steps
1. Extend the `state check` command to load and validate `outline.yaml` against character carrier states.
2. Relocate `bible_audit.py` out of `auteur.structure` to a new shared `auteur.audit` package to align with ADR 003.
3. Decouple outline generation from drafting to ensure structural validation can run as a blocking gate before any prose generation begins.

## 11. Recommended next step
Implement the missing `outline.yaml` parser and integration into `state_check` so that character location and state transitions are validated at the scene outline level (Layer 7) prior to drafting.

## 12. Recommended workflow
`implementation-workflow`

## 13. Machine-readable handoff
```yaml
artifact_id: repository_sensemaking_brief
schema_version: 1
source_intent_ref: artifacts/05-orchestration-run/00-user-intent.md
recommended_workflow_id: implementation-workflow
recommended_execution_mode: guided_execution
weakest_boundary: ghost_features_state_check
required_inputs:
  - user_intent
  - repository_state
user_implied_fog_type: docs_fog
primary_fog_type: architecture_fog
diagnosis_conflict: false
escalation_recommended: false
created_at: "2026-05-19T21:52:00Z"
```

## 14. Ready-to-copy prompt
```
We need to address the weakest boundary identified in the repository sensemaking brief: the outline.yaml file is not validated during state check. Implement a validator for outline.yaml (Layer 7 Representation) to check character state transitions and location consistency at the outline level prior to starting drafting. Ensure that all tests remain green.
```
