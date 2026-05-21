# To-Issues Output: Repo Sensemaker Research-Test

Source PRD: docs/prd-repo-sensemaker-research-test.md
Publication: skipped (local only)

## Proposed Vertical Slices

1. Title: Align README Structure Capability Contract
- Type: AFK
- Blocked by: None - can start immediately
- User stories covered: 1, 4, 7
- What to build:
  - Update README status text to reflect implemented structure diagnose/propose/apply and proposal/report artifacts.
- Acceptance criteria:
  - README no longer claims missing implemented structure CLI/proposal capabilities.
  - README still documents remaining known limitations accurately.
  - Existing CLI behavior docs remain coherent with docs/project-format.md.

2. Title: Add Repo Sensemaker Reference Pack
- Type: AFK
- Blocked by: None - can start immediately
- User stories covered: 2, 8
- What to build:
  - Add docs/references/repo-analysis-template.md
  - Add docs/references/weakness-types.md
  - Add docs/references/evidence-rules.md
- Acceptance criteria:
  - All three reference docs exist with stable headings used by the sensemaking brief workflow.
  - Weakness types include vocabulary drift, contract mismatch, ghost features, safety gaps, implicit dependencies, zero validation, orphaned examples.
  - Evidence rules require file citations, structural proof, contrastive evidence, logic trace, and no vibe-based diagnosis.

3. Title: Enforce Boundary Checks with Deterministic Validator
- Type: AFK
- Blocked by: Slice 1 and Slice 2
- User stories covered: 3, 5, 7
- What to build:
  - Add a repository validation command/script that checks README contract drift and required reference docs.
  - Add pytest coverage for pass/fail behavior.
- Acceptance criteria:
  - Validator fails when stale README sentence appears.
  - Validator fails when any reference doc is missing.
  - Validator passes in normal repository state.

## Dependency Order

- Execute Slice 1 and Slice 2 first (parallel-safe).
- Execute Slice 3 after 1+2.
