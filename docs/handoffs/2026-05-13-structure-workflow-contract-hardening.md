---
type: handoff
session: structure-workflow-contract-hardening
date: 2026-05-13
status: GREEN
next_task: Write ADR 002 enforcement slice — auteur structure apply rejects bible_audit proposals
---

# Session Summary — Structure Workflow Contract Hardening

## Commits

This session's changes are unstaged (working-tree edits against HEAD `029ec19`). No new commits were made during the session. All changes are ready to commit.

HEAD (origin/main): `029ec19 feat: Add Next Step Discovery document for workflow guidance`

## Files Modified/Created

**CONTEXT.md** — Added `Structure Diagnostic` term, `Proposal Lifecycle` four-step sequence, `Proposal Resolution` canonical verb clarification, and command ownership table mapping proposal source to resolution command.

**docs/prd-structure-workflow-contract.md** *(new)* — Full PRD for the structure workflow contract hardening: problem statement, user stories, implementation decisions, testing decisions, out-of-scope items.

**docs/adr/002-shared-structure-proposal-format.md** *(new)* — ADR capturing why a single `StructureProposal` YAML format is shared across the structure and Bible audit paths, and why `source_domain` was added.

**docs/adr/003-bible-audit-placement.md** *(new)* — ADR documenting `bible_audit.py`'s temporary residence in `auteur.structure`, with the precondition for moving it (extract shared `DiagnosticLayer`/`RepairOptions` infrastructure).

**src/auteur/structure/bible_audit.py** — Updated module docstring to reference ADR 003 and mark the file as a temporary resident.

**src/auteur/structure/proposal_models.py** — Added `source_domain: str | None = None` field to `StructureProposal`. Backward-compatible: existing YAMLs without the field parse as `None`.

**src/auteur/structure/proposal_generation.py** — `propose_repairs_from_diagnostics` now sets `source_domain="structure"` on each proposal. Added new function `propose_repairs_from_audit_diagnostics` (mirrors `propose_repairs_from_diagnostics` for the Bible audit path, sets `source_domain="bible_audit"`).

**src/auteur/structure/proposal_resolution.py** — `write_audit_repair_proposals` refactored: generation logic removed, now delegates to `propose_repairs_from_audit_diagnostics`. Function handles I/O only.

**src/auteur/structure/proposals.py** — Added `propose_repairs_from_audit_diagnostics` to re-exports.

**tests/test_source_domain.py** *(new)* — 7 tests: schema backward-compat, `source_domain` round-trip, `propose_repairs_from_diagnostics` sets `"structure"`, `write_audit_repair_proposals` sets `"bible_audit"`.

**tests/test_structure_workflow_fixture.py** *(new)* — 4 end-to-end CLI fixture tests: full `propose-repairs → apply` sequence (asserts output blueprint field value, `.meta.yaml`, original blueprint immutability), default output dir behaviour, `structure_report.json` path, `audit --accept` stamps `decision` without mutating blueprint.

**tests/test_audit_proposal_generation.py** *(new)* — 6 tests: `propose_repairs_from_audit_diagnostics` callable, sets `source_domain`, preserves `source_rule`, options match `repair_options`, `write_audit_repair_proposals` regression, structural guard asserting generation logic does not re-appear in `proposal_resolution.py`.

## Verification

Run this before starting any new work:

```bash
python -m pytest tests/ -q --tb=no
```

Expected output: `155 passed` (or more if other tests were added). 0 failures.

## Global Status

Ran full test suite: **155 passed, 0 failed, 0 warnings**.  
Global status: **GREEN**

## Architectural Decisions

- **Decision**: Add `source_domain: str | None = None` to `StructureProposal`  
  **Why**: A `StructureProposal` YAML in `structure/proposals/` now self-describes its resolution path. Without it, a future agent or author cannot determine whether to run `auteur structure apply` (merges into blueprint) or `auteur audit --accept` (stamps YAML only).  
  **Alternative**: Separate YAML schemas per domain (`StructureProposal` vs `BibleAuditProposal`). Rejected because the artifact format is structurally identical and a single discriminant field is cheaper than doubling the tooling surface.

- **Decision**: Extract generation logic from `write_audit_repair_proposals` into `propose_repairs_from_audit_diagnostics` in `proposal_generation.py`  
  **Why**: `proposal_resolution.py` should only resolve (stamp decisions); proposal construction belongs in `proposal_generation.py` alongside `propose_repairs_from_diagnostics`. Co-location makes both generation paths discoverable from one module.  
  **Alternative**: Leave generation in `proposal_resolution.py`. Rejected because it creates a module with two responsibilities and makes the Bible audit generation path undiscoverable without reading the resolution module.

- **Decision**: `bible_audit.py` stays in `auteur.structure` as a temporary resident  
  **Why**: It imports `DiagnosticLayer`, `DiagnosticSeverity`, `RepairOptions` from `auteur.structure.diagnostics`. Moving it requires first extracting that infrastructure to a shared location — a separate architectural decision not yet made.  
  **Alternative**: Move `bible_audit.py` now by duplicating types or adding re-exports. Rejected because duplication creates maintenance burden and re-exports obscure rather than resolve the boundary.

- **Decision**: Write end-to-end CLI fixture test as the primary deliverable  
  **Why**: Per `next-step-discovery.md`, the weakest contract boundary is the one most likely to confuse a future agent. The full `propose-repairs → apply` sequence was untested at the CLI level. The fixture makes the workflow provable without reading four separate unit test files.  
  **Alternative**: Doc update only. Rejected because documentation without a test is unverifiable.

## Locked ADRs

- **ADR 001**: Structure Proposal Artifact Format — defines the `StructureProposal` YAML schema and the `data`-merge workflow for `auteur structure apply`.
- **ADR 002**: Shared StructureProposal Format — rationale for a single proposal format across structure and Bible audit paths, with `source_domain` discriminant.
- **ADR 003**: bible_audit.py Placement — temporary residence in `auteur.structure`; preconditions for moving documented.

## Frontier

**Next task**: Add `source_domain` enforcement to `auteur structure apply` — reject proposals with `source_domain == "bible_audit"` with a clear error message. Corresponding test: assert `main(["structure", "apply", ...])` returns exit code 1 and prints an appropriate error when the proposal YAML has `source_domain: bible_audit`. File: `tests/test_structure_workflow_fixture.py`, new test `test_structure_apply_rejects_bible_audit_proposal`. Implementation: `_cmd_structure_apply` in `src/auteur/cli.py`, add a guard after proposal validation.

## Blockers (if any)

None. All 155 tests pass. Working tree has uncommitted changes — commit before starting the next session.
