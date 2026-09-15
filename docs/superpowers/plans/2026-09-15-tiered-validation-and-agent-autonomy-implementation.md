# Tiered Validation and Agent Autonomy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ordinary Auteur development use cheap focused validation, reserve targeted integration for named boundaries, move full regression to explicit stabilization checkpoints, keep exact-SHA qualification release-only, and grant coding agents bounded low-level implementation authority after initial authorization.

**Architecture:** Keep three lifecycle surfaces separate. `.github/workflows/validation.yml` is the cheap development gate; `.github/workflows/stabilization.yml` is the explicit L3 full-regression checkpoint; `.github/workflows/release-qualification.yml` qualifies an explicitly supplied frozen candidate by running the existing canonical `scripts/release_evidence.py`. Governance documents define the same L1/L2/L3/qualification vocabulary and the delegation envelope. UI/CLI product implementation is explicitly out of scope for this branch until the parallel UI-polish task lands.

**Tech Stack:** GitHub Actions YAML, Python/pytest policy tests, Markdown governance docs.

**Spec:** `docs/superpowers/specs/2026-09-15-tiered-validation-and-agent-autonomy-design.md`

## Global Constraints

- Normal implementation iteration uses L1 focused validation only.
- L2 requires a named integration boundary or risk justification.
- L3 is prohibited unless a stabilization/high-risk/release trigger exists.
- Exact-SHA release qualification is prohibited unless a candidate is explicitly being qualified.
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
- Produces: focused pytest assertions that fail if ordinary validation regains unconditional full-suite/Windows/release behavior or if explicit stabilization/release workflows disappear.

- [ ] **Step 1: Write the failing policy tests**

Create tests that load workflow YAML with `yaml.BaseLoader` and assert:

```python
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    return yaml.load((WORKFLOWS / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_development_validation_is_focused_and_not_release_qualification():
    workflow = _load("validation.yml")
    jobs = workflow["jobs"]
    assert "test-windows" not in jobs
    assert "release-qualification" not in jobs
    rendered = (WORKFLOWS / "validation.yml").read_text(encoding="utf-8")
    assert "python -m pytest -q --tb=short" not in rendered
    assert "scripts/release_evidence.py" not in rendered


def test_stabilization_is_explicit_and_runs_full_regression():
    workflow = _load("stabilization.yml")
    assert set(workflow["on"]) == {"workflow_dispatch"}
    rendered = (WORKFLOWS / "stabilization.yml").read_text(encoding="utf-8")
    assert "python -m pytest -q --tb=short" in rendered
    assert "scripts/release_evidence.py" not in rendered


def test_release_qualification_is_explicit_exact_candidate_evidence():
    workflow = _load("release-qualification.yml")
    assert set(workflow["on"]) == {"workflow_dispatch"}
    candidate = workflow["on"]["workflow_dispatch"]["inputs"]["candidate_sha"]
    assert candidate["required"] == "true"
    rendered = (WORKFLOWS / "release-qualification.yml").read_text(encoding="utf-8")
    assert "scripts/release_evidence.py" in rendered
    assert "ref: ${{ inputs.candidate_sha }}" in rendered
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python -m pytest -q tests/test_validation_workflow_policy.py --tb=short
```

Expected: FAIL because `validation.yml` still contains unconditional Windows/full/release behavior and the two explicit workflows do not yet exist.

- [ ] **Step 3: Commit the RED test separately if useful for review**

```bash
git add tests/test_validation_workflow_policy.py
git commit -m "test: define tiered validation workflow policy"
```

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

- [ ] **Step 1: Make `validation.yml` the cheap development gate**

Keep triggers on pull requests and pushes to `main`. Use one supported development Python version (`3.12`). Select changed `tests/*.py` files when present; otherwise run `tests/test_cli_smoke.py tests/test_engine_v1_smoke.py`. Run repository validators with `python scripts/check.py --skip-pytest`. Do not run an unconditional Windows suite, supported-version matrix, or `scripts/release_evidence.py` here.

The focused pytest command must be structurally different from the full-suite signature guarded by the policy test, for example:

```yaml
- name: Run L1 focused validation
  run: python -m pytest -q $FOCUSED_TESTS --tb=short
```

- [ ] **Step 2: Add explicit L3 stabilization workflow**

Create `.github/workflows/stabilization.yml` with `workflow_dispatch` only, one Linux Python 3.12 job, repository validators, and exactly one complete source regression run:

```yaml
- name: Run L3 full regression suite
  run: python -m pytest -q --tb=short
```

Do not call `scripts/release_evidence.py` and do not build release artifacts in this workflow.

- [ ] **Step 3: Add explicit release-qualification workflow**

Create `.github/workflows/release-qualification.yml` with `workflow_dispatch` only and required string input `candidate_sha`. Checkout exactly `${{ inputs.candidate_sha }}`, install release dependencies, verify `git rev-parse HEAD` equals the requested candidate, then run:

```yaml
- name: Produce exact-SHA qualification evidence
  run: python scripts/release_evidence.py
```

Upload `docs/qualification-evidence/*.json` as the evidence artifact. Do not duplicate the full pytest or wheel run outside the canonical evidence producer because `release_evidence.py` already owns both.

- [ ] **Step 4: Run the focused workflow-policy test and verify GREEN**

```bash
python -m pytest -q tests/test_validation_workflow_policy.py --tb=short
```

Expected: PASS.

- [ ] **Step 5: Run cheap repository verification**

```bash
python scripts/check.py --skip-pytest
```

Expected: repository validators/ruff complete without a new regression attributable to these workflow files.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/validation.yml .github/workflows/stabilization.yml .github/workflows/release-qualification.yml tests/test_validation_workflow_policy.py
git commit -m "ci: separate development stabilization and release validation"
```

---

### Task 3: Reconcile qualification terminology and evidence claims

**Files:**
- Modify: `docs/engineering/release-qualification.md`

**Interfaces:**
- Consumes: the approved design vocabulary and existing candidate-invalidation/exact-release invariants.
- Produces: one authoritative policy distinguishing L1, L2, L3, and release qualification without weakening exact-SHA evidence rules.

- [ ] **Step 1: Replace the old broad full-validation PR rule**

Document:

```text
L1 Focused Validation — default implementation feedback and ordinary development gate.
L2 Targeted Integration Validation — only when a named changed boundary/risk justifies it.
L3 Full Regression Validation — explicit milestone/stabilization/recovery checkpoint.
Release Qualification — exact frozen-candidate evidence; separate from L3.
```

Preserve baseline failure classification, candidate invalidation, exact release invariant, test accounting, publication boundary, and evidence-bounded completion language.

- [ ] **Step 2: State `main` lifecycle semantics explicitly**

Add that a push to `main` is a development integration event and does not implicitly create a release candidate or require exact-SHA release qualification.

- [ ] **Step 3: State escalation rules for validation cost**

Record that L2 must name a boundary/risk, L3 must name a checkpoint trigger, and release qualification requires explicit candidate selection.

- [ ] **Step 4: Verify documentation references**

Run:

```bash
git diff --check
python scripts/check.py --skip-pytest
```

- [ ] **Step 5: Commit**

```bash
git add docs/engineering/release-qualification.md
git commit -m "docs: separate development validation from release qualification"
```

---

### Task 4: Grant bounded implementation autonomy without weakening author authority

**Files:**
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: initial human prompt/spec, repository hard invariants, qualification policy.
- Produces: explicit delegation envelope and owner-reserved stop conditions for coding agents.

- [ ] **Step 1: Replace blanket approval-per-detail language in `AGENTS.md`**

Replace the blanket `Ask, don't assume` implementation rule with:

```text
Infer within the delegation envelope; escalate material ambiguity.
```

Define agent-delegated decisions: local naming, helper extraction, behaviorally equivalent algorithms, local refactoring required by scope, focused test selection, justified targeted integration selection, test-fixture organization, internal data flow, commit decomposition, minor descriptive docs.

Define owner-reserved decisions: product intent/user-visible semantics not implied by the prompt, semantic architecture, canonical narrative/Layer-1 commitments, public compatibility, destructive migration, security/privacy/credentials/new external transmission, deployment/publication, permanent scope constraints, material scope expansion, hard-invariant changes, irreconcilable requirements.

Preserve explicit author authority and qualification claim language.

- [ ] **Step 2: Align `CLAUDE.md` development velocity guidance**

Add the L1/L2/L3 test-budget rule and state that an approved work package executes continuously without human pauses for low-level implementation choices until a stop condition is reached.

Do not change narrative architecture or genre-specific behavior.

- [ ] **Step 3: Verify docs only**

```bash
git diff --check
python scripts/check.py --skip-pytest
```

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md CLAUDE.md
git commit -m "docs: grant bounded coding-agent implementation authority"
```

---

### Task 5: Reconcile branch scope and open a draft PR without touching UI-polish implementation

**Files:**
- Review only: branch diff against `main`.

**Interfaces:**
- Consumes: Tasks 1-4.
- Produces: a reviewable governance/CI PR isolated from the parallel UI-polish implementation.

- [ ] **Step 1: Confirm no UI/CLI product files changed**

Run:

```bash
git diff --name-only main...HEAD
```

Allowed implementation-package paths are limited to:

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

No `src/auteur/**` or UI/CLI product test files may be changed in this package.

- [ ] **Step 2: Run only L1 policy verification**

```bash
python -m pytest -q tests/test_validation_workflow_policy.py --tb=short
python scripts/check.py --skip-pytest
git diff --check
```

Do not run L3. The governance/CI package itself is not a stabilization checkpoint.

- [ ] **Step 3: Open a draft pull request**

PR body must explicitly state:

- this is human-authorized governance/CI work;
- L1 was run;
- L2 was not required because no product integration boundary changed;
- L3 was intentionally deferred;
- release qualification was intentionally not run;
- UI/CLI implementation is excluded until the parallel UI-polish task lands;
- merging should wait for review of the workflow-policy change and any required exact-head lightweight CI.

- [ ] **Step 4: Do not merge automatically**

The branch changes CI/governance policy and therefore remains a review boundary even under the new delegated implementation model.
