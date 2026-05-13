# PRD: Structure Workflow Contract Hardening

**Status:** Ready for implementation  
**Date:** 2026-05-13  
**Source:** grill-with-docs session — structure workflow boundary analysis

---

## Problem Statement

The structure workflow's contract boundaries are ambiguous in three places:

1. **Proposal artifacts are opaque.** A `StructureProposal` YAML in `structure/proposals/` does not declare whether the author should resolve it with `auteur audit --accept` or `auteur structure apply`. Both commands write identical `StructureProposal` artifacts but perform structurally different resolution acts — one stamps a `decision` in-place, the other merges `data` into the blueprint. A future agent or author has no way to determine the correct command from the artifact alone.

2. **The full structure workflow is untested end-to-end.** Unit tests cover schema parsing, proposal generation, and apply logic in isolation. No test exercises the complete CLI path: `auteur structure propose-repairs` → author selects an option → `auteur structure apply`. The `_cmd_structure_apply` double-path (reconciling `selection` vs `decision`) is not covered by any integration-level test.

3. **CONTEXT.md is missing three entries.** The term `Structure Diagnostic` is not defined, the proposal lifecycle (diagnose → propose-repairs → select → apply) is not described, and the command ownership table (which command resolves which proposal type) is absent. A future agent must read source code to recover information that should be in the glossary.

---

## Solution

Harden the structure workflow contract by:

1. Adding a `source_domain` field to `StructureProposal` that self-describes the resolution path.
2. Writing an end-to-end CLI fixture test that exercises the full `propose-repairs → apply` workflow.
3. Filling the three CONTEXT.md gaps.
4. Capturing two architectural decisions in ADRs (shared proposal format; `bible_audit.py` temporary placement).
5. Refactoring `write_audit_repair_proposals` so that proposal generation logic is co-located with the structure path's `propose_repairs_from_diagnostics`, not mixed into the resolution module.

---

## User Stories

1. As an author, I want a `StructureProposal` YAML to tell me which CLI command resolves it, so that I do not have to read source code to resolve a Decision Packet.
2. As an author, I want `auteur structure apply` to reject a proposal that was created by a Bible audit, so that I do not accidentally apply a lore-repair to my blueprint.
3. As an author, I want `auteur audit --accept` to reject a proposal that was created by `auteur structure propose-repairs`, so that I do not accidentally stamp a structural proposal as a Bible audit resolution.
4. As an author, I want the CONTEXT.md glossary to define `Structure Diagnostic` in contrast with `Bible Audit`, so that I understand when each command applies.
5. As an author, I want the CONTEXT.md glossary to document the proposal lifecycle, so that I can follow the workflow without reading CLI help text.
6. As an author, I want CONTEXT.md to list which command resolves which proposal type, so that the contract is readable in one place.
7. As a developer, I want a fixture test that runs the full `propose-repairs → apply` CLI sequence, so that regressions in the end-to-end workflow are caught automatically.
8. As a developer, I want the `source_domain` field to be optional with `None` as the default, so that existing YAML artifacts are backward-compatible and validate without a migration.
9. As a developer, I want the `_cmd_audit --accept` path to be covered by an explicit test that confirms it stamps `decision` and does not mutate the blueprint, so that the two resolution semantics are independently verified.
10. As a developer, I want the `write_audit_repair_proposals` generation logic to live in `proposal_generation.py` alongside `propose_repairs_from_diagnostics`, so that the two proposal-generation paths are co-located and the resolution module stays focused.
11. As a developer, I want an ADR capturing why `StructureProposal` is shared across both audit and structure paths, so that a future refactor has context for the trade-off.
12. As a developer, I want an ADR capturing why `bible_audit.py` lives temporarily in `auteur.structure`, so that the precondition for moving it is documented.
13. As a future agent, I want `source_domain` to be a `Literal["structure", "bible_audit"]` field (nullable), so that type-checking is possible without a runtime lookup.
14. As a future agent, I want the fixture test to assert on the output YAML content after apply, not just file existence, so that the contract is verifiable without reading source code.

---

## Implementation Decisions

- **`source_domain` field on `StructureProposal`**: Add `source_domain: Literal["structure", "bible_audit"] | None = None` to the Pydantic model. Existing artifacts without the field parse as `None` (backward-compatible). Both `propose_repairs_from_diagnostics` (structure path) and the Bible audit generation function will populate it at creation time.

- **`write_audit_repair_proposals` split**: The function currently bundles proposal generation + disk I/O. Split it: generation logic moves into `proposal_generation.py` as a new function (mirroring `propose_repairs_from_diagnostics`), and the CLI handler calls it directly (mirroring `_cmd_structure_propose_repairs`). The re-export in `proposals.py` is updated.

- **Fixture test shape**: The end-to-end test uses `tmp_path` (pytest), writes a minimal blueprint YAML, invokes `main(["structure", "propose-repairs", ...])` via the CLI entrypoint, reads the output proposal YAML from disk, sets `selected_option_id`, writes it back, invokes `main(["structure", "apply", ...])`, and asserts the output blueprint has the expected field value. No mocking of the file system — real I/O only.

- **CONTEXT.md additions**: Add `Structure Diagnostic` term (contrast with `Bible Audit`), add `Proposal Lifecycle` section describing the four steps (diagnose → propose-repairs → author selects → apply), add a command ownership table in the Relationships section.

- **ADR 002**: Shared `StructureProposal` format across structure and Bible audit paths, with `source_domain` added. Records the alternative (separate artifact schemas) and why it was rejected (single format reduces tooling surface).

- **ADR 003**: `bible_audit.py` temporary residence in `auteur.structure`, with the precondition for moving it documented (shared `DiagnosticLayer`/`RepairOptions` infrastructure must first be extracted to `auteur.diagnostics` or similar).

- **Canonical verb**: `resolution`/`resolve` is the canonical term for the author's act of selecting and locking a proposal option. The CLI flag `--accept` is a known divergence — rename deferred until after the fixture test provides a regression safety net.

---

## Testing Decisions

- **Good tests** verify CLI behavior through public entrypoints (`main()`) or through the `StructureProposal` model's public API. They do not assert on internal function names or private state.
- **Modules under test**:
  - `StructureProposal` schema (`source_domain` field, backward-compat parse of old YAMLs)
  - `propose_repairs_from_diagnostics` (source_domain is set correctly)
  - Bible audit generation path (source_domain is set correctly)
  - `_cmd_structure_propose_repairs` + `_cmd_structure_apply` via `main()` (end-to-end fixture)
  - `_cmd_audit --accept` via `main()` (resolution stamps decision, does not mutate blueprint)
- **Prior art**: `test_proposal_accept_apply.py`, `test_structure_analyzer.py`, `test_cli.py`

---

## Out of Scope

- Renaming the CLI flag `--accept` to `--resolve` (deferred until post-fixture).
- Moving `bible_audit.py` out of `auteur.structure` (deferred until shared infra is extracted).
- Adding `source_domain` enforcement (i.e., `auteur structure apply` rejecting `bible_audit` proposals) — the field is added and tested; enforcement is a follow-on slice.
- Story State Manager multi-layer coordination (separate PRD).

---

## Further Notes

The `next-step-discovery.md` heuristic ("close the weakest contract boundary") points squarely at the fixture test as the highest-value deliverable. The schema change and CONTEXT.md updates are preconditions that unlock the fixture without introducing their own complexity. The `write_audit_repair_proposals` refactor is a cleanup that follows naturally from the fixture, because the fixture will import the new generation function and make the move safe.
