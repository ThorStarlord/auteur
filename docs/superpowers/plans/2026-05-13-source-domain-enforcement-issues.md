# Issue Breakdown — Source Domain Enforcement In Structure Apply

Source PRD: docs/prd-structure-apply-source-domain-enforcement.md
Publication: Skipped (local planning artifact only)
Approval mode: auto-approved per session instruction

## Slice 1 (Highest Priority)
Title: Add failing fixture for bible_audit rejection
Type: AFK
Blocked by: None - can start immediately
User stories covered: 1, 2, 3, 6, 7

What to build:
Add a tracer-bullet fixture test that invokes `main(["structure", "apply", ...])` with a proposal YAML containing `source_domain: bible_audit`.

Acceptance criteria:
- [ ] Test fails before implementation.
- [ ] Asserts return code is `1`.
- [ ] Asserts stderr includes guidance to use `auteur audit --accept`.
- [ ] Asserts source blueprint file content is unchanged.

## Slice 2
Title: Enforce source ownership in structure apply
Type: AFK
Blocked by: Slice 1
User stories covered: 1, 2, 3, 4, 5

What to build:
Implement a guard in `_cmd_structure_apply` that rejects proposals with `source_domain == "bible_audit"` before any blueprint load/apply work.

Acceptance criteria:
- [ ] Guard checks validated proposal object.
- [ ] Command returns `1` for bible_audit proposal.
- [ ] Error message points to audit resolution path.
- [ ] Legacy `source_domain: null` continues to work.

## Slice 3
Title: Regression proof and cleanup
Type: AFK
Blocked by: Slice 2
User stories covered: 5, 6, 8

What to build:
Run targeted and full test suites; keep messaging deterministic and ensure no behavior changes for existing structure apply flow.

Acceptance criteria:
- [ ] New fixture test passes.
- [ ] Existing structure workflow fixture tests still pass.
- [ ] Full test suite remains green.
- [ ] No unrelated schema/analyzer changes introduced.
