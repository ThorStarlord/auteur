# Tiered Validation and Agent Autonomy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make ordinary Auteur development use cheap focused validation, reserve targeted integration for named boundaries, move full regression to explicit stabilization checkpoints, keep exact-SHA qualification release-only, and grant coding agents bounded low-level implementation authority after initial authorization.

**Architecture:** `.github/workflows/validation.yml` is the cheap development gate. `.github/workflows/stabilization.yml` is the explicit L3 full-regression checkpoint. `.github/workflows/release-qualification.yml` is the frozen-candidate gate: Python 3.11/3.13 Linux and Python 3.13 Windows provide compatibility evidence, while the canonical `scripts/release_evidence.py` owns Python 3.12 full-suite accounting plus installed-wheel qualification and durable exact-SHA evidence. `scripts/check.py` preserves its historical full-repository default but accepts explicit Ruff paths so L1 can lint only Python files changed inside the historical `src`/`tests` Ruff scope.

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

## Task 1 — Machine-checkable workflow policy

**Files:**
- `tests/test_validation_workflow_policy.py`

**Status:** COMPLETE.

Evidence:

- Initial RED: 3 failures against the old workflow shape.
- The policy test requires exactly one ordinary development job, explicit manual stabilization/release workflows, no ordinary Windows/release qualification, and changed-file Ruff scoping.

---

## Task 2 — Split development, stabilization, and release workflows

**Files:**
- `.github/workflows/validation.yml`
- `.github/workflows/stabilization.yml`
- `.github/workflows/release-qualification.yml`

**Status:** COMPLETE.

### L1 development workflow

```text
trigger: pull_request + push(main)
runner: Ubuntu
Python: 3.12
pytest: changed tests/*.py when present; otherwise CLI + engine smoke
validators: repository validator stack
Ruff: changed Python files under src/tests only
no Windows
no Python matrix
no full-suite fallback
no wheel/release qualification
```

### L3 stabilization workflow

Manual `workflow_dispatch` only:

```text
Linux Python 3.12
full pytest regression suite
repository verification stack
```

No release evidence, wheel qualification, or Windows matrix runs here.

### Release qualification workflow

Manual `workflow_dispatch`, required exact `candidate_sha`:

```text
Linux Python 3.11 -> complete source suite
Linux Python 3.13 -> complete source suite
Windows Python 3.13 -> complete source suite
Linux Python 3.12 -> scripts/release_evidence.py
                         ↳ complete source suite
                         ↳ installed-wheel qualification
                         ↳ durable exact-SHA evidence
```

Every release job checks out and verifies the requested candidate SHA.

---

## Task 2A — Preserve full verifier semantics while making L1 cheap

**Files:**
- `scripts/check.py`
- `tests/test_check_script.py`
- `.github/workflows/validation.yml`
- `tests/test_validation_workflow_policy.py`

**Status:** COMPLETE.

### Failure discovered by exact-head L1

The first PR run showed:

```text
focused policy test: PASS
validator suite: PASS (25/25)
repo validator: PASS
release-scope validator: PASS
vendored contract: PASS
Ruff: FAIL (5 errors)
```

All five Ruff errors were in existing #228/UI-polish files not changed by this branch:

```text
src/auteur/cli_formatters.py
src/auteur/story_design_packs/cli.py
src/auteur/ui/workspace.py
```

The branch diff contained no changes to those files, so this was inherited baseline lint debt, not a candidate regression.

### Root cause

`python scripts/check.py --skip-pytest` still ran repository-wide:

```text
ruff check src tests
```

Using that command unchanged inside L1 allowed unrelated baseline lint debt to block focused development, contradicting the approved cost/risk model.

### Minimal fix

`CHECK_COMMANDS` and the default `scripts/check.py` behavior remain unchanged. A new optional `--ruff-paths` scope lets L1 replace the global Ruff target with explicitly changed `src/tests` Python paths, or omit Ruff when no such Python file changed.

Focused RED test before implementation:

```text
2 failed: commands_for did not exist
```

Focused GREEN after implementation:

```text
2 passed
```

`tests/test_check_script.py` also reconciles the old CI-matrix contract to the new focused-development contract.

### Exact-head remote result

PR #229 exact head `fe66077f120a55b2edc9bb0776ecf37c20da1c5e`:

```text
L1 focused validation: PASS
focused verification stack: PASS
job conclusion: SUCCESS
```

The job used one Ubuntu/Python 3.12 runner and did not execute Windows, a Python matrix, L3, or release qualification.

---

## Task 3 — Qualification terminology and evidence claims

**File:**
- `docs/engineering/release-qualification.md`

**Status:** COMPLETE.

Implemented vocabulary:

```text
L1 Focused Validation — default implementation feedback and ordinary development gate.
L2 Targeted Integration Validation — only with a named changed boundary/risk.
L3 Full Regression Validation — explicit milestone/stabilization/recovery checkpoint.
Release Qualification — exact frozen-candidate evidence; separate from L3.
```

Preserved:

- baseline failure classification;
- candidate invalidation;
- exact release invariant;
- test accounting;
- publication boundary;
- evidence-bounded completion language.

`main` is explicitly the latest stable development state rather than a continuously release-qualified artifact.

---

## Task 4 — Bounded coding-agent implementation authority

**Files:**
- `AGENTS.md`
- `CLAUDE.md`

**Status:** COMPLETE.

The blanket implementation rule is replaced with:

> Infer within the delegation envelope; escalate material ambiguity.

Delegated decisions include local naming, helper extraction, behaviorally equivalent algorithms, local refactoring required by scope, test organization, L1 selection, justified L2 selection, internal data flow, commit decomposition, and minor descriptive docs.

Owner-reserved decisions remain product intent/user-visible semantics not implied by the prompt, semantic architecture, canonical narrative/Layer-1 commitments, public compatibility, destructive migration, security/privacy/credentials/new external transmission, deployment/publication, permanent scope constraints, material scope expansion, hard-invariant changes, and irreconcilable requirements.

Author authority is unchanged.

---

## Task 5 — Branch scope and draft PR

**Changed paths permitted in this package:**

```text
.github/workflows/validation.yml
.github/workflows/stabilization.yml
.github/workflows/release-qualification.yml
AGENTS.md
CLAUDE.md
docs/engineering/release-qualification.md
docs/superpowers/specs/2026-09-15-tiered-validation-and-agent-autonomy-design.md
docs/superpowers/plans/2026-09-15-tiered-validation-and-agent-autonomy-implementation.md
scripts/check.py
tests/test_check_script.py
tests/test_validation_workflow_policy.py
```

No `src/auteur/**`, UI/CLI product implementation, or UI/CLI product tests are changed.

### Validation disposition

- **L1:** required and executed.
- **L2:** intentionally not run; no product integration boundary changed.
- **L3:** intentionally deferred; this policy package is not a product stabilization checkpoint.
- **Release qualification:** intentionally not run; no release candidate is frozen.

### PR

Draft PR: **#229 — `ci: separate cheap development validation from release qualification`**.

The PR must remain a human review boundary because it changes CI/governance policy. Do not auto-merge it.

### Final exact-head gate

After this execution-record update, allow the same cheap PR L1 workflow to validate the final documentation head. Do not escalate to L2/L3/release qualification unless a new material trigger appears.
