# Auteur 1.0 Release Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Auteur coherent and stable enough for a deliberately bounded 1.0 release by closing release-blocking contract, artifact, workflow, documentation, and qualification gaps.

**Architecture:** Preserve the five semantic layers and existing canonical/derived/candidate/acceptance vocabulary. Add only narrow adapters and validators at existing seams; do not introduce a sixth layer, a second decision system, or automatic author mutation.

**Tech Stack:** Python 3.11+, Pydantic 2, PyYAML, argparse, pytest, pytest-xdist, Ruff, Hatchling.

**Spec:** `docs/narrative-architecture.md`, `docs/architecture-constitution.md`, `MISSION.md`, and `docs/engineering/release-qualification.md`.

## Global Constraints

- No recommendation, tutor result, diagnostic, proposal, simulation, or derived report may mutate canonical narrative state.
- Any canonical mutation requires explicit author action, atomic persistence, provenance, rationale, and failure safety.
- Deterministic analyzers remain offline, deterministic, and explainable.
- Structure generation and diagnosis remain whole-story Narrative Engine work.
- Existing Story Identity, Book, Series, Genre Pack, CLI, and packaged-resource behavior remains backward compatible.
- Every production behavior change is preceded by a failing regression test.
- Release claims use exact candidate-SHA evidence and separate pytest categories.

---

### Task 1: Freeze and publish the 1.0 support contract

**Files:**
- Create: `docs/1.0-scope.md`
- Modify: `README.md`
- Modify: `docs/capability-coverage.md`
- Test: `tests/test_release_integrity.py`

- [x] Define the supported 1.0 golden path and explicitly classify Book-level reasoning/editing, long-horizon tutor learning, advanced series context, markerless mapping, merge/split, and collaboration as supported, experimental, or deferred.
- [x] Add a machine-checkable scope file and a test that required supported commands are documented.
- [x] Reconcile README and coverage language with the scope file.
- [x] Verify documentation tests and the scope validator.

### Task 2: Add repository self-description consistency checks

**Files:**
- Modify: `scripts/validate-repo.py`
- Modify: `scripts/test-validators.py`
- Create: `tests/fixtures/validate-repo/valid/`
- Create: `tests/fixtures/validate-repo/invalid/`
- Test: `tests/test_validate_repo.py`

- [x] Add duplicate ADR identifier detection (already present on the starting HEAD).
- [ ] Add checks for stale local `file:///` links and references to removed public modules/commands where the validator already has sufficient context.
- [ ] Add valid and invalid fixtures for repository, mode coverage, project classification, and workflow-design validators.
- [x] Keep third-party baseline failures separately classified rather than hiding them.
- [x] Verify the validator suite and Ruff.

### Task 3: Enforce canonical derived-artifact locations

**Files:**
- Modify: `src/auteur/reasoning/runtime.py`
- Modify: `src/auteur/reasoning/cli.py`
- Modify: `src/auteur/cli_dispatch.py`
- Modify: `.gitignore`
- Test: `tests/test_reasoning_runtime.py`
- Test: `tests/test_repo_contract.py`

- [x] Define one project-relative default for reasoning reports under `.auteur/reasoning` (already present on the starting HEAD).
- [x] Reject repository-root report destinations.
- [x] Ensure the Book reasoning CLI and runtime expose the same resolution rule while preserving isolated test directories.
- [x] Add a regression test proving generated reports do not land in the repository root (already present on the starting HEAD).
- [x] Verify existing report readers and all reasoning tests.

### Task 4: Close the operational freshness contract

**Files:**
- Modify: `src/auteur/provenance/`
- Modify: `src/auteur/structure/freshness.py`
- Modify: `src/auteur/impact/`
- Create: `docs/revision-staleness-contract.md`
- Test: `tests/test_structure_freshness.py`
- Test: `tests/test_release_integrity.py`

- [ ] Document the minimum upstream-change-to-downstream-staleness matrix.
- [x] Verify stale inputs block unsafe promotion and never silently substitute newer revisions across the existing structure, expression, and Book gates.
- [x] Verify unaffected derived artifacts remain reusable only when their explicit dependencies remain fresh in the existing freshness tests.
- [x] Add and verify revision-sensitive tests for reasoning, structure, realization, expression, and Book paths.
- [x] Verify no canonical mutation occurs on stale failure in the existing acceptance and publication tests.

### Task 5: Normalize supported artifact lifecycle behavior

**Files:**
- Modify: `src/auteur/identity.py`
- Modify: `src/auteur/blueprint.py`
- Modify: `src/auteur/structure/`
- Modify: `src/auteur/narrative_realization/`
- Test: corresponding existing lifecycle, proposal, publish, and acceptance tests

- [ ] Inventory each supported artifact’s create/validate/reason/propose/publish/decide/accept behavior.
- [ ] Add only missing narrow adapters using existing proposal, provenance, and decision seams.
- [x] Ensure unsupported operations fail with explicit, documented messages rather than appearing available.
- [ ] Verify Identity, Blueprint, Structure, Scene Realization, Chapter Expression, and Book workflows independently.

### Task 6: Improve the author-facing golden path

**Files:**
- Modify: `src/auteur/workflow/`
- Modify: `src/auteur/cli_formatters.py`
- Modify: `src/auteur/cli_parser.py`
- Modify: `src/auteur/cli_dispatch.py`
- Create: `docs/guides/author-golden-path-1.0.md`
- Test: `tests/test_workflow_story_discovery_front_door.py`
- Test: `tests/test_cli_smoke.py`

- [ ] Make `workflow next` reliably identify the first useful action in a fresh project.
- [ ] Present authority, mutation, and next-step information in human-readable output.
- [ ] Preserve JSON output for automation.
- [x] Add recovery guidance for stale, incomplete, rejected, and deferred work.
- [ ] Verify the complete CLI golden path in a temporary project.

### Task 7: Bound Book reasoning/editing and advanced capabilities

**Files:**
- Modify: `src/auteur/reasoning/`
- Modify: `src/auteur/book/`
- Modify: `src/auteur/editing/`
- Modify: `src/auteur/review/`
- Test: `tests/test_book_reasoning.py`
- Test: `tests/test_book_reconciliation_application.py`

- [x] Implement the smallest Book-level reasoning adapter over existing critic/report contracts (already present on the starting HEAD).
- [x] Remove the review service's false-success acceptance stub; unsupported review acceptance now fails closed.
- [x] Keep Book findings derived and route repairs through existing proposal and decision paths; the Book critic remains read-only and the golden path documents proposal/decision ownership.
- [x] Clearly label markerless mapping, merge/split, grouped decisions, and broad Series intelligence as deferred unless their existing contracts can be completed without new authority semantics.
- [ ] Verify Book reasoning does not alter accepted Book, Chapter, Structure, Realization, or Expression artifacts.

### Task 8: Release qualification and installed-artifact evidence

**Files:**
- Modify: `.github/workflows/validation.yml`
- Modify: `scripts/release_evidence.py`
- Modify: `scripts/verify_wheel.py`
- Create: `docs/engineering/v1.0-qualification-record.md`
- Test: `tests/test_release_evidence.py`
- Test: `tests/test_release_integrity.py`

- [x] Add an exact-SHA qualification record template; actual candidate qualification remains gated on a clean frozen commit.
- [ ] Reconcile serial and parallel pytest categories.
- [ ] Compare validator failures against a frozen baseline.
- [ ] Build and install the wheel from the exact candidate SHA in a fresh environment.
- [x] Verify installed import path, CLI help, ontology resources, genre resources, and golden-path commands with `scripts/verify_wheel.py`.
- [x] Expand installed-wheel smoke checks to verify site-packages import resolution and golden-path command help.
- [ ] Do not call the repository release-ready until every release gate has evidence.

### Task 9: Final coherence review

- [ ] Scan active documentation for superseded architecture vocabulary.
- [ ] Scan public CLI commands against README and scope documentation.
- [ ] Scan artifact writers for undeclared canonical mutations.
- [ ] Run full source and artifact qualification from a clean candidate SHA.
- [ ] Record remaining deferred capabilities and known non-blocking baseline failures.

---

## Detailed execution order

The tasks are intentionally ordered by release risk rather than by package
layout. A later task must not widen an earlier contract without updating its
tests and this plan.

### Phase 0: Baseline and working-tree safety

1. Run `git rev-parse --show-toplevel`, `git rev-parse --git-common-dir`,
   `git rev-parse HEAD`, `git status --short`, and record the candidate context.
2. Confirm the checkout is the intended standalone repository and that the
   active import path is this checkout's `src` directory.
3. Run `python scripts/check.py --skip-pytest`, recording validator warnings
   separately from failures.
4. Run the current source suite with `PYTHONPATH=src` and record all pytest
   categories. Do not use an installed editable package from another worktree.

### Phase 1: Release contract and documentation integrity

1. Review `docs/1.0-scope.md` against `MISSION.md`,
   `docs/architecture-constitution.md`, and the README command table.
2. Add a scope validator fixture and a negative test for each required section.
3. Add active-document scans for superseded layer names, unsupported commands,
   stale version claims, and invalid local links. Historical documents under
   `docs/archived/` remain exempt but must be clearly marked historical.
4. Add ADR filename/header/number uniqueness checks and a regression fixture
   containing two files claiming the same ADR number.
5. Run the validator harness and repository check before changing product code.

**Exit criterion:** a clean checkout can mechanically answer what 1.0 supports,
what is experimental, and what is permanently out of scope.

### Phase 2: Artifact and freshness safety

1. Inventory every `ReasoningRuntime`, report synthesizer, proposal writer, and
   publication writer call site with `rg -n "ReasoningRuntime|write_text|write_bytes|report_dir"`.
2. Write failing tests for project-local report paths, repository-root refusal,
   missing source revision behavior, and stale promotion refusal.
3. Implement one canonical path resolver for derived reasoning output. It must
   accept a project root and optional project-relative subdirectory; it must not
   silently reinterpret an absolute path outside the project.
4. Update CLI and pipeline callers to use that resolver. Keep direct temporary
   directories valid for isolated unit tests.
5. Add the revision/staleness matrix to the provenance and freshness tests:
   Identity → Blueprint, Blueprint → Structure, Structure → Realization, and
   Realization → Expression.
6. Verify that stale failures leave source files, accepted pointers, and
   provenance records byte-for-byte unchanged.

**Exit criterion:** no supported promotion path can silently use a stale or
unknown source, and derived reports cannot accumulate in the repository root.

### Phase 3: Artifact lifecycle consistency

1. Build an inventory table from the current CLI parser and dispatch code:
   command, input artifact, output artifact, authority, freshness requirement,
   and acceptance owner.
2. For every supported row, identify whether the operation is create,
   validate, reason, propose, publish, decide, or accept.
3. Add missing tests before adding adapters. Tests must assert authority status,
   provenance, source hash, and zero mutation of unrelated artifacts.
4. Implement only the smallest adapter at the existing owning module. Do not
   make `ReviewService`, `WorkflowEngine`, or a critic directly own another
   artifact's canonical pointer.
5. Replace any remaining fake-success or placeholder acceptance with either a
   real delegation to the owning acceptance seam or a structured fail-closed
   error.
6. Add CLI help and error-message coverage for deliberately deferred features.

**Exit criterion:** every advertised supported operation has one clear owner;
every unsupported operation explains the correct next command.

### Phase 4: Author-facing workflow

1. Create a fresh temporary project from a premise and capture each
   `workflow next` result.
2. Write failing tests for the first action, current stage, blocker severity,
   authority level, mutation warning, and suggested recovery command.
3. Implement formatter changes behind the existing typed `WorkflowState`; do
   not duplicate stage detection in CLI formatting.
4. Preserve `--json` output as a stable machine-readable projection.
5. Add recovery paths for: missing identity, rejected discovery candidate,
   stale structure report, incomplete chapter, deferred candidate, and failed
   draft iteration.
6. Run the complete temporary-project golden path without an API key using fake
   clients where creative generation is not the behavior under test.

**Exit criterion:** a new author can identify the next safe action without
opening internal JSON, while automation receives the same facts structurally.

### Phase 5: Book reasoning and explicitly bounded advanced work

1. Verify the existing `book.manuscript` critic against a two-Chapter fixture.
2. Add failing integration tests proving its reports are derived, carry source
   evidence, and cannot alter accepted Book or Chapter artifacts.
3. Route any Book repair recommendation through existing proposal and decision
   mechanisms; never call acceptance directly from a critic.
4. Keep markerless mapping, paragraph movement, Scene merge/split, grouped
   decisions, and broad long-horizon Series inference outside the 1.0 support
   contract unless a separate design contract is added first.
5. Add explicit CLI/documentation labels for those deferred capabilities.

**Exit criterion:** Book reasoning is useful and non-authoritative; deferred
   transformations cannot be mistaken for supported behavior.

### Phase 6: Qualification

1. Freeze the candidate SHA only after all source, test, resource, and build
   changes are complete.
2. Run serial pytest through the evidence producer and record collected,
   passed, skipped, xfailed, xpassed, failed, and error counts.
3. Run the parallel suite and reconcile its categories against serial output.
4. Run `scripts/check.py --skip-pytest`; classify validator failures against a
   frozen baseline as regression, shifted failure, or known baseline failure.
5. Build the wheel from the frozen SHA and install it into a fresh environment.
6. Verify that `auteur.__file__` resolves inside site-packages, then run CLI
   help, ontology resource, genre resource, and golden-path smoke commands.
7. Write `docs/engineering/v1.0-qualification-record.md` with exact SHA,
   artifact hash, environment versions, command lines, category arithmetic,
   baseline comparison, skips/xfails, and known warnings.
8. Re-run `git status --short` and confirm no candidate-invalidating change
   occurred after the freeze. If one did, discard the qualification record and
   restart from the new SHA.

**Exit criterion:** the release record proves the exact source SHA, built wheel,
installed package, and final release commit are identical for qualification.

## Required final report

The implementation handoff must include:

- files changed and why;
- supported/experimental/deferred 1.0 capability table;
- exact candidate SHA;
- pytest category arithmetic for serial and parallel runs;
- validator and Ruff results;
- wheel hash and installed import path;
- known baseline failures and warnings;
- any work deliberately left outside 1.0.

Do not use “fully repaired,” “qualified,” “merge-ready,” or “release-ready”
unless the corresponding evidence gate in
`docs/engineering/release-qualification.md` has completed.
