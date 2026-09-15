# Tiered Validation and Agent Autonomy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make ordinary Auteur development use cheap focused validation, reserve targeted integration for named boundaries, move full regression to explicit stabilization checkpoints, keep exact-SHA qualification release-only, and grant coding agents bounded low-level implementation authority after initial authorization.

**Architecture:** `.github/workflows/validation.yml` is the cheap development gate. `.github/workflows/stabilization.yml` is the explicit L3 full-regression checkpoint. `.github/workflows/release-qualification.yml` is an explicit frozen-candidate gate: Python 3.11/3.13 Linux and Python 3.13 Windows provide compatibility evidence, while the canonical `scripts/release_evidence.py` owns Python 3.12 full-suite accounting plus installed-wheel qualification and durable exact-SHA evidence. Governance documents define the same L1/L2/L3/qualification vocabulary and delegation envelope.

**Tech Stack:** GitHub Actions YAML, Python/pytest policy tests, Markdown governance docs.

**Spec:** `docs/superpowers/specs/2026-09-15-tiered-validation-and-agent-autonomy-design.md`

## Global Constraints

- Normal implementation iteration uses L1 focused validation only.
- L2 requires a named integration boundary or risk justification.
- L3 requires a named stabilization/recovery/cross-cutting/release trigger.
- Exact-SHA release qualification requires an explicitly selected frozen candidate.
- `main` is the latest stable development state, not continuously release-qualified.
- Author authority over canonical narrative commitments remains unchanged.
- Product intent, semantic architecture, destructive changes, security/privacy, external publication, and material scope expansion remain owner-reserved.
- Unsupervised agents must not gain authority to weaken their own governance.
- Do not modify UI/CLI product implementation or #228 regression files in this package; reconcile those after the parallel UI-polish task finishes.

---

### Task 1: Add cheap machine-checkable workflow-policy tests

**Files:**
- Create: `tests/test_validation_workflow_policy.py`

**Interfaces:**
- Consumes: the three workflow YAML files under `.github/workflows/`.
- Produces: focused assertions that prevent ordinary validation from regaining unconditional full-suite/Windows/release behavior and prove that explicit stabilization/release workflows remain separate.

- [x] **Step 1: Write the failing policy test**

The test loads workflows with `yaml.BaseLoader` and asserts:

```python
assert set(validation["jobs"]) == {"focused-validation"}
assert set(stabilization["on"]) == {"workflow_dispatch"}
assert set(release["on"]) == {"workflow_dispatch"}
assert release["on"]["workflow_dispatch"]["inputs"]["candidate_sha"]["required"] == "true"
```

It also guards against `windows-latest` and `scripts/release_evidence.py` returning to ordinary development validation, and verifies the release matrix remains present only in the explicit release workflow.

- [x] **Step 2: Verify RED**

Run:

```bash
python -m pytest -q tests/test_validation_workflow_policy.py --tb=short
```

Observed before implementation: 3 failures. The old workflow still contained the Windows/full/release jobs and the two explicit workflows were absent.

- [x] **Step 3: Commit RED test**

Commit: `test: define tiered validation workflow policy`.

---

### Task 2: Split development validation, stabilization, and release qualification

**Files:**
- Modify: `.github/workflows/validation.yml`
- Create: `.github/workflows/stabilization.yml`
- Create: `.github/workflows/release-qualification.yml`
- Test: `tests/test_validation_workflow_policy.py`

**Interfaces:**
- Consumes: changed test files, smoke tests, `scripts/check.py --skip-pytest`, `scripts/release_evidence.py`.
- Produces: cheap PR/main development validation, explicit L3 full-regression checkpoint, explicit exact-candidate release qualification.

- [x] **Step 1: Make `validation.yml` the cheap development gate**

Rules:

```text
trigger: pull_request + push(main)
Python: 3.12 only
pytest: changed tests/*.py when present, otherwise CLI + engine smoke tests
repository verification: scripts/check.py --skip-pytest
no Windows suite
no supported-version matrix
no full-suite fallback
no wheel/release qualification
```

- [x] **Step 2: Add explicit L3 stabilization workflow**

`stabilization.yml` is `workflow_dispatch` only and runs exactly one Linux Python 3.12 full regression suite plus the repository verification stack.

It does not run `scripts/release_evidence.py`, does not build a wheel, and does not run Windows.

- [x] **Step 3: Add explicit release-qualification workflow**

`release-qualification.yml` is `workflow_dispatch` only and requires `candidate_sha`.

The workflow checks out and verifies that exact SHA in every job. It preserves release compatibility without duplicating canonical evidence work:

```text
Linux Python 3.11 -> complete source suite
Linux Python 3.13 -> complete source suite
Windows Python 3.13 -> complete source suite
Linux Python 3.12 -> scripts/release_evidence.py
                         ↳ complete source suite
                         ↳ installed-wheel qualification
                         ↳ durable exact-SHA evidence
```

The evidence artifact is uploaded with `if: always()` so recorded non-green evidence remains inspectable when the producer writes an artifact before failing the gate.

- [x] **Step 4: Verify GREEN**

Run against the exact committed workflow contents:

```bash
python -m pytest -q tests/test_validation_workflow_policy.py --tb=short
```

Observed: `3 passed`.

- [ ] **Step 5: Repository verification on exact PR head**

The local sandbox cannot clone GitHub, so `python scripts/check.py --skip-pytest` cannot be run against the whole repository there. The draft PR's new focused CI is the authoritative exact-head execution of this cheap repository verification.

---

### Task 3: Reconcile qualification terminology and evidence claims

**Files:**
- Modify: `docs/engineering/release-qualification.md`

- [x] Define L1 Focused Validation as the default development feedback/gate.
- [x] Define L2 Targeted Integration as evidence-triggered by a named boundary/risk.
- [x] Define L3 Full Regression as an explicit stabilization/recovery/checkpoint activity.
- [x] Define Release Qualification as a separate exact-frozen-candidate lifecycle event.
- [x] Preserve candidate invalidation, exact release invariant, test accounting, baseline classification, and publication boundaries.
- [x] State that `main` is the latest stable development state, not a continuously release-qualified artifact.
- [x] State that a passing development gate does not imply L3 or release qualification.

---

### Task 4: Grant bounded implementation autonomy without weakening author authority

**Files:**
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`

- [x] Replace blanket `Ask, don't assume` implementation behavior with:

```text
Infer within the delegation envelope; escalate material ambiguity.
```

- [x] Delegate routine decisions including naming, helper extraction, local refactoring, behaviorally equivalent algorithms, test organization, L1 selection, justified L2 selection, internal data flow, commit decomposition, and minor descriptive docs.
- [x] Reserve product intent, semantic architecture, canonical narrative authority, compatibility, destructive migration, security/privacy, external actions, publication/release authorization, hard-invariant changes, and material scope expansion to the owner.
- [x] Preserve explicit author authority for Layer 1/canonical narrative commitments.
- [x] Add the same L1/L2/L3/qualification test budget to the contributor guide.
- [x] Remove test-count targets as a default optimization; prefer a small number of high-signal tests where they prove behavior more cheaply.

---

### Task 5: Reconcile branch scope and open a draft PR

**Allowed changed paths:**

```text
.github/workflows/validation.yml
.github/workflows/stabilization.yml
.github/workflows/release-qualification.yml
AGENTS.md
CLAUDE.md
docs/engineering/release-qualification.md
docs/superpowers/specs/2026-09-15-tiered-validation-and-agent-autonomy-design.md
docs/superpowers/plans/2026-09-15-tiered-validation-and-agent-autonomy-implementation.md
tests/test_validation_workflow_policy.py
```

- [x] **Confirm branch scope**

`main...codex/testing-qualification-autonomy` changes exactly the nine allowed files above. No `src/auteur/**`, UI implementation file, CLI implementation file, or UI/CLI product test is touched.

- [x] **Run L1 workflow-policy verification**

Exact committed workflow contents: `3 passed`.

- [x] **Defer L2 deliberately**

No product integration boundary changed in this package, so L2 is not justified.

- [x] **Defer L3 deliberately**

This governance/CI package is not itself a product stabilization checkpoint. The explicit L3 workflow is the mechanism to use when the UI-polish/recovery work reaches that checkpoint.

- [x] **Do not run release qualification**

No release candidate has been frozen.

- [ ] **Open a draft PR and let exact-head focused CI verify repository checks**

The PR body must state that this is human-authorized governance/CI work, UI/CLI implementation is excluded, L1 policy tests passed, L2/L3/release qualification were intentionally not run, and merge is not automatic.

- [ ] **Do not merge automatically**

The branch changes CI/governance policy and remains a human review boundary even under the new delegated implementation model.
