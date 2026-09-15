# Post-#229 Finalization and Discoverability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land PR #229 as the repository's active validation/authority policy, then add a minimal README/STATUS signpost without expanding `AGENTS.md`.

**Architecture:** Treat PR #229 as the governance transition boundary. After it is merged, make one small documentation-only follow-up that points contributors to the canonical policy and records the current stabilization posture; do not mix #228/UI recovery into either package.

**Tech Stack:** GitHub pull requests/actions, Markdown.

**Spec:** `docs/superpowers/specs/2026-09-15-tiered-validation-and-agent-autonomy-design.md`

## Global Constraints

- Do not add more policy to `AGENTS.md`.
- Do not run L3 or release qualification for PR #229.
- Do not touch `src/auteur/**` or UI/CLI product tests in these two packages.
- `main` is the latest stable development state, not a continuously release-qualified state.
- The canonical detailed policy remains `docs/engineering/release-qualification.md`.

---

### Task 1: Finalize and merge PR #229

**Files:**
- Review only: PR #229 and its exact-head CI.

**Interfaces:**
- Consumes: PR #229 head and `Validation` workflow result.
- Produces: merged testing/authority policy on `main`.

- [ ] Confirm PR #229 still changes only governance/CI/verifier/test-policy files and does not touch `src/auteur/**`.
- [ ] Confirm the latest exact-head `L1 focused validation (Python 3.12)` run is successful.
- [ ] Confirm L2 is not justified, L3 is not triggered, and release qualification is not applicable.
- [ ] Mark PR #229 ready for review.
- [ ] Merge PR #229 into `main` without adding another policy change to the PR.
- [ ] Record the resulting merge SHA for the documentation follow-up.

---

### Task 2: Add the minimal README/STATUS discoverability note

**Files:**
- Modify: `README.md`
- Modify: `STATUS.md`
- Do not modify: `AGENTS.md`

**Interfaces:**
- Consumes: merged #229 policy and merge SHA.
- Produces: a short stable entry point for humans/agents plus current operational handoff.

- [ ] Add this compact README section near the contributor/development documentation surface:

```markdown
## Development Validation

Auteur uses risk-tiered validation:

- **L1 Focused Validation** — default development and PR gate.
- **L2 Targeted Integration** — used only when a changed integration boundary or named risk justifies it.
- **L3 Full Regression** — reserved for explicit stabilization, recovery, and milestone checkpoints.
- **Release Qualification** — separate exact-SHA qualification for an explicitly frozen release candidate.

`main` represents the latest stable development state; it is not continuously release-qualified.

See [docs/engineering/release-qualification.md](docs/engineering/release-qualification.md) for the canonical policy.
```

- [ ] Update `STATUS.md` with the #229 merge SHA and a short current validation posture:

```markdown
### Development validation posture

- L1 is the normal development gate.
- L2 requires a named changed boundary or risk.
- L3 is reserved for explicit stabilization/recovery/milestone checkpoints.
- Release qualification requires an explicitly frozen candidate.
- Normal integration into `main` does not imply release qualification.

The post-#228 product baseline has not yet been re-established. The next stabilization package is: reconcile UI-polish work, repair remaining #228 regressions with L1, run the justified CLI L2 slice, then run one L3 checkpoint and record the new known-good baseline SHA.
```

- [ ] Keep existing product/architecture documentation unchanged except where needed to remove a directly contradictory old CI statement.
- [ ] Run the ordinary documentation L1 gate only; do not run L3 or release qualification.
- [ ] Merge the documentation follow-up once its exact-head L1 check is green.

---

### Exit condition

The package is complete when #229 is active on `main`, README points to the four validation states and canonical policy, STATUS records the current post-#228 recovery posture, `AGENTS.md` is unchanged, and no product implementation was pulled into the work.