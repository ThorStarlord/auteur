# Auteur 1.0.0-rc.1 Release Remediation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development to implement this plan task-by-task. Do not begin implementation until the release scope and task ordering are confirmed by the repository owner.

**Goal:** Establish a defensible `1.0.0-rc.1` for Auteur's bounded local, single-author Campaign workflow: persistence, validation, semantic inspection, handoff/resume, bundle exchange, stable CLI/Python contracts, and exact-SHA release governance.

**Architecture:** Keep Campaign as a local persisted coordination record over existing authoritative Story Identity, Blueprint, Structure, Realization, Expression, decision, and review artifacts. Derived inspections, handoffs, bundles, and reports must remain proposals or projections; only the owning artifact command may perform canonical mutation after explicit author action. Reuse existing `Project`, provenance, acceptance, round-trip, workflow, and release-evidence seams rather than introducing a second persistence or authority model.

**Tech Stack:** Python 3.11+, Pydantic 2, PyYAML, `argparse`, pytest/pytest-xdist, Ruff, Hatchling, GitHub Actions.

---

## Release scope and ordering

The candidate includes only the local Campaign persistence and inspection path,
deterministic validation, handoff/resume, bundle handling, the documented CLI
and Python contracts, and release governance. LLM-backed drafting, cloud or
collaborative execution, GUI/browser support, markerless manuscript mapping,
merge/split transforms, grouped dependent decisions, and broad long-horizon
intelligence remain excluded or experimental and must not be made to appear
stable by this plan.

Implement in dependency order:

1. Freeze the RC scope and artifact ownership model.
2. Implement Campaign persistence and recovery invariants.
3. Add deterministic validation and semantic inspection.
4. Add resumable handoff records and safe resume planning.
5. Harden bundle export/import as a versioned, non-mutating exchange.
6. Reconcile and freeze CLI/Python contract behavior.
7. Run exact-SHA source/artifact qualification and complete governance.

Human approval is required only where a task changes authorial authority,
promotes a canonical artifact, or authorizes release publication. Approval is
not required to run read-only probes, write regression tests, or prepare a
candidate report.

---

### Task RC-P0-01: Freeze the bounded RC contract and ownership map

**Priority:** P0

**Objective:** Make the RC promise mechanically legible: define Campaign as a
local coordination/persistence concern, identify the owning command for every
canonical artifact, and prevent experimental or deferred commands from being
interpreted as supported.

**Exact files or areas likely affected:**

- `docs/1.0-scope.md`
- `docs/releases/v1.0.0.md`
- `CHANGELOG.md`
- `docs/architecture-constitution.md`
- `docs/engineering/public-api-contract.md`
- `docs/engineering/cli-contract.md`
- `src/auteur/cli_parser.py`
- `src/auteur/cli_dispatch.py`
- `tests/test_release_integrity.py`
- `tests/test_cli_contract.py`
- `tests/test_public_api_contract.py`

**Acceptance criteria:**

- The RC scope explicitly lists local Campaign persistence, validation,
  semantic inspection, handoff/resume, and bundle handling as supported or
  bounded-supported capabilities.
- Each supported operation has exactly one owning module and one canonical
  mutation command; workflow, review, inspection, and bundle commands cannot
  silently write another artifact's canonical pointer.
- Stable, experimental, deprecated, and unsupported CLI/Python surfaces are
  represented by explicit sets or tables that tests can compare with the
  parser and package exports.
- Deferred features produce a nonzero, deterministic, documented failure and
  do not create partial artifacts.
- No documentation claims cloud, collaboration, GUI, automatic migration,
  markerless mapping, or grouped-decision support.

**Verification command or evidence required:**

- `python -m pytest tests/test_release_integrity.py tests/test_cli_contract.py tests/test_public_api_contract.py -q`
- `python scripts/validate-release-scope.py`
- A reviewed command/ownership matrix committed as part of the RC evidence,
  with every stable command mapped to its input, output, authority, and
  freshness requirement.

**Risk:** Medium. Over-freezing the surface could exclude an already-supported
  local workflow; under-freezing it leaves SemVer promises ambiguous.

**Human approval required:** Yes, for the final supported/experimental scope
  and owning-command decisions. The implementation of the agreed matrix does
  not require approval.

**Blocks:** Both `1.0.0-rc.1` and final `1.0.0`.

---

### Task RC-P0-02: Establish atomic local Campaign persistence

**Priority:** P0

**Objective:** Add one versioned, project-local Campaign record that can be
loaded, validated, updated, and recovered without corrupting canonical story
artifacts or silently losing author decisions.

**Exact files or areas likely affected:**

- Create `src/auteur/campaign/__init__.py`
- Create `src/auteur/campaign/models.py`
- Create `src/auteur/campaign/persistence.py`
- Modify `src/auteur/project.py`
- Modify `src/auteur/artifact_schema.py`
- Modify `src/auteur/provenance/`
- Modify `src/auteur/acceptance.py`
- Create `tests/test_campaign_persistence.py`
- Extend `tests/test_project.py`
- Extend `tests/test_acceptance_registry.py`
- Extend `docs/engineering/artifact-compatibility.md`

**Acceptance criteria:**

- Campaign persistence has an explicit schema version, stable identifier,
  project identity, current phase, source artifact revisions/hashes, pending
  handoff references, and recovery status.
- Writes use the repository's atomic persistence convention: write and flush a
  temporary sibling, replace the target, and leave the prior valid file intact
  when validation or replacement fails.
- Loading rejects malformed, unsupported, stale, or ambiguous Campaign state
  with a typed/machine-readable error; malformed state is never treated as
  absence.
- Campaign updates do not mutate Story Identity, Blueprint, Structure,
  Realization, Expression, or accepted pointers unless an owning acceptance
  operation is explicitly invoked.
- Interrupted writes leave either the previous valid Campaign or a clearly
  inspectable recovery record; startup does not replay mutations
  automatically.
- Compatibility behavior for the existing project/artifact loaders is
  preserved and explicitly documented.

**Verification command or evidence required:**

- `python -m pytest tests/test_campaign_persistence.py tests/test_project.py tests/test_acceptance_registry.py -q`
- Failure-oriented cases for malformed YAML/JSON, unsupported schema version,
  permission-denied replacement, interrupted replacement, stale source hash,
  duplicate Campaign IDs, and restart persistence.
- Byte-for-byte before/after snapshots proving failed operations do not alter
  canonical artifacts or accepted pointers.

**Risk:** High. Persistence defines the durable state boundary and can create
  unrecoverable author-data loss if atomicity or compatibility is wrong.

**Human approval required:** Yes before defining any field that asserts
  authorial/canonical authority; no for the atomic write implementation after
  the schema decision is approved.

**Blocks:** Both `1.0.0-rc.1` and final `1.0.0`.

---

### Task RC-P0-03: Add deterministic Campaign validation and semantic inspection

**Priority:** P0

**Objective:** Separate shape validation from semantic inspection and make the
  RC's critical Campaign state transitions deterministic, explainable, and
  fail-closed.

**Exact files or areas likely affected:**

- Create `src/auteur/campaign/validation.py`
- Create `src/auteur/campaign/inspection.py`
- Modify `src/auteur/structure/freshness.py`
- Modify `src/auteur/provenance/`
- Modify `src/auteur/workflow/engine.py`
- Modify `src/auteur/workflow/models.py`
- Create `tests/test_campaign_validation.py`
- Create `tests/test_campaign_inspection.py`
- Extend `tests/test_workflow_engine.py`
- Extend `tests/test_provenance_pilot.py`
- Extend `docs/1.0-scope.md` with the validation/inspection distinction

**Acceptance criteria:**

- Schema validation answers whether the persisted record is shaped correctly;
  semantic inspection separately reports missing prerequisites, stale source
  revisions, unsupported states, unresolved handoffs, and cross-artifact
  inconsistencies.
- Identical inputs produce identical machine-readable findings, ordering,
  severity, and exit code; no LLM or wall-clock value affects a verdict.
- Unknown, malformed, stale, or conflicting source state is reported as
  blocking/unavailable rather than silently downgraded to an empty or current
  result.
- Inspection is read-only and records source paths/revisions/hashes and the
  rule/inspector version used.
- Workflow status consumes the typed inspection result rather than duplicating
  state heuristics in formatters or CLI dispatch.

**Verification command or evidence required:**

- `python -m pytest tests/test_campaign_validation.py tests/test_campaign_inspection.py tests/test_workflow_engine.py tests/test_provenance_pilot.py -q`
- Run the same inspection twice in separate processes and compare normalized
  JSON output byte-for-byte.
- Run invalid, stale, missing, permission-denied, and contradictory fixture
  cases and verify nonzero/blocking outcomes with no file mutation.

**Risk:** High. Incorrect semantic severity can either block valid author work
  or allow corrupt state to proceed.

**Human approval required:** Yes for the definition of authorial invariants
  and severity of ambiguous semantic findings; no for deterministic mechanics.

**Blocks:** Both `1.0.0-rc.1` and final `1.0.0`.

---

### Task RC-P0-04: Define resumable handoff and recovery semantics

**Priority:** P0

**Objective:** Make handoff/resume a persisted, inspectable protocol rather
  than an implicit continuation or automatic replay mechanism.

**Exact files or areas likely affected:**

- Create `src/auteur/campaign/handoff.py`
- Modify `src/auteur/acceptance.py`
- Modify `src/auteur/workflow/engine.py`
- Modify `src/auteur/workflow/cli.py`
- Modify `src/auteur/cli_parser.py`
- Modify `src/auteur/cli_dispatch.py`
- Modify `docs/engineering/public-api-contract.md`
- Modify `docs/engineering/cli-contract.md`
- Create `tests/test_campaign_handoff.py`
- Extend `tests/test_acceptance_registry.py`
- Extend `tests/test_workflow_engine.py`

**Acceptance criteria:**

- A handoff records source Campaign revision, source artifact hashes, current
  stage, pending operation, required inputs, authority level, and a stable
  handoff ID.
- `handoff inspect` is read-only and reconstructs the next safe action from
  the record; `handoff resume` revalidates every dependency before producing
  a proposal or invoking the owning command.
- Resume refuses stale, missing, malformed, ambiguous, already-completed, and
  unsupported handoffs with stable error codes and no mutation.
- A process interruption leaves a recoverable report; resume is explicit and
  never automatically replays a partial canonical mutation.
- Human-facing and JSON outputs expose whether the result is advisory,
  proposal-producing, or canonical-mutating, and identify the required owner
  action.

**Verification command or evidence required:**

- `python -m pytest tests/test_campaign_handoff.py tests/test_acceptance_registry.py tests/test_workflow_engine.py -q`
- Subprocess qualification covering create → interrupt → inspect → resume,
  source revision changed before resume, repeated resume, and permission
  failure during final acceptance.
- Evidence that all failed resume paths leave Campaign and canonical artifacts
  byte-for-byte unchanged.

**Risk:** High. Resume is a common place for duplicate writes, stale replay,
  or accidental authority escalation.

**Human approval required:** Yes before any resume action that can reach a
  canonical owner; inspection and proposal-only resume need no per-run approval.

**Blocks:** Both `1.0.0-rc.1` and final `1.0.0`.

---

### Task RC-P0-05: Harden versioned bundle export/import

**Priority:** P0

**Objective:** Provide a bounded local bundle format for Campaign state and
  required artifacts that is portable, integrity-checked, non-mutating on
  import, and safe to inspect before acceptance.

**Exact files or areas likely affected:**

- Modify `src/auteur/roundtrip/serializers.py`
- Modify `src/auteur/roundtrip/handlers.py`
- Modify `src/auteur/roundtrip/cli.py`
- Modify `src/auteur/project.py`
- Modify `src/auteur/provenance/`
- Create `src/auteur/campaign/bundle.py`
- Create `tests/test_campaign_bundle.py`
- Extend `tests/test_roundtrip_export_import.py`
- Modify `docs/project-format.md`
- Create or extend `docs/engineering/artifact-compatibility.md`

**Acceptance criteria:**

- Bundle format has a schema version, manifest, file list, content hashes,
  source Campaign revision, tool version, and declared artifact roles.
- Export is deterministic for the same source state: normalized ordering,
  stable metadata rules, and no timestamps in hashed content unless explicitly
  excluded from the digest.
- Import validates path safety, duplicate entries, manifest hashes, schema
  compatibility, artifact ownership, and source revision before writing.
- Import writes only an isolated staging/result directory and reports proposed
  changes; it does not overwrite canonical files or accepted pointers.
- Promotion from a verified bundle uses the owning acceptance path, requires
  explicit confirmation, and records provenance linking bundle hash to the
  resulting artifact revision.
- Unsupported future bundle versions and corrupted archives fail closed with
  stable machine-readable errors.

**Verification command or evidence required:**

- `python -m pytest tests/test_campaign_bundle.py tests/test_roundtrip_export_import.py -q`
- Export the same fixture twice and compare manifests/hashes.
- Import valid, corrupted, path-traversal, duplicate-file, unsupported-version,
  stale-source, and permission-denied bundles.
- Fresh-process evidence that inspect/import is zero-mutation and explicit
  promotion changes only the owning artifact plus provenance.

**Risk:** High. Bundle import is an externalized write boundary and can cause
  data overwrite, path traversal, or provenance loss.

**Human approval required:** Yes for promotion/acceptance; no for export or
  isolated import inspection.

**Blocks:** Both `1.0.0-rc.1` and final `1.0.0`.

---

### Task RC-P1-06: Reconcile and freeze CLI/Python contract behavior

**Priority:** P1

**Objective:** Make the supported contract surfaces stable enough for RC
  consumers and ensure semantic behavior, errors, and output formats match the
  published contract.

**Exact files or areas likely affected:**

- `src/auteur/__init__.py`
- `src/auteur/cli.py`
- `src/auteur/cli_parser.py`
- `src/auteur/cli_dispatch.py`
- `src/auteur/cli_serializers.py`
- `src/auteur/cli_formatters.py`
- `src/auteur/acceptance.py`
- `docs/engineering/public-api-contract.md`
- `docs/engineering/cli-contract.md`
- `tests/test_public_api_contract.py`
- `tests/test_cli_contract.py`
- `tests/test_cli_serializers.py`
- `tests/test_cli_smoke.py`
- `tests/test_release_integrity.py`

**Acceptance criteria:**

- The stable Python export set is tested exactly; accidental root exports fail
  the contract test.
- Supported CLI groups, flags, exit codes, JSON keys, stdout/stderr routing,
  confirmation rules, and stable error codes are tested from a subprocess.
- User-input, stale-state, unavailable-environment, internal-error, and
  unsupported-operation failures are distinguishable and do not emit success
  JSON or partial canonical output.
- Version metadata in `pyproject.toml`, `src/auteur/__init__.py`, wheel
  metadata, CLI version output, and release notes agrees on `1.0.0`/RC policy.
- Compatibility aliases are either tested and documented or removed from the
  supported surface; no undocumented command is implied by examples.

**Verification command or evidence required:**

- `python -m pytest tests/test_public_api_contract.py tests/test_cli_contract.py tests/test_cli_serializers.py tests/test_cli_smoke.py tests/test_release_integrity.py -q`
- Subprocess snapshots for stable human and `--json` output.
- `python -m build --wheel` followed by inspection of wheel `METADATA` and
  installed `auteur.__version__`.

**Risk:** Medium. Contract tightening can break existing scripts, but leaving
  behavior implicit creates a larger final-release compatibility hazard.

**Human approval required:** Yes for removing or reclassifying an existing
  command/export; no for documenting and testing already-supported behavior.

**Blocks:** `1.0.0-rc.1` if any stable-scope contract is inconsistent; otherwise
  final `1.0.0`.

---

### Task RC-P1-07: Build failure-oriented local integration qualification

**Priority:** P1

**Objective:** Prove the recommended local Campaign journey at the CLI and
  installed-package seams, including corruption, interruption, stale input,
  and partial-failure behavior.

**Exact files or areas likely affected:**

- `scripts/verify_wheel.py`
- `scripts/release_evidence.py`
- `scripts/probe-repo.py`
- Create `tests/qualification/test_campaign_rc1.py`
- Extend `tests/qualification/conftest.py`
- Extend `tests/qualification/test_qualification.py`
- Modify `.github/workflows/validation.yml`
- Modify `docs/engineering/v1.0-qualification-record.md`

**Acceptance criteria:**

- A temporary project can execute the documented local path: initialize
  Campaign → persist/load → validate → inspect → create handoff → resume
  proposal → export bundle → isolated import → explicit owner acceptance.
- The matrix includes fresh process boundaries and verifies that all derived
  operations are zero-mutation before acceptance.
- Invalid input, malformed persisted state, stale dependency, interrupted
  write, permission failure, duplicate operation, and unsupported version each
  produce the expected blocking result.
- The same matrix runs against source and an installed wheel from the same
  candidate, with import resolution proven to be site-packages for the wheel.
- CI executes the required qualification on the relevant protected branch or
  dispatch and preserves logs/evidence sufficient to identify the exact SHA.

**Verification command or evidence required:**

- `python -m pytest tests/qualification/test_campaign_rc1.py -q`
- `python scripts/verify_wheel.py`
- `python scripts/check.py --skip-pytest`
- CI run URL and artifact bundle for the exact candidate SHA.

**Risk:** Medium-high. Integration tests can pass while missing a packaging or
  environment boundary unless source and installed-wheel runs are separate.

**Human approval required:** No for test execution; yes to accept an explicitly
  excluded integration/environment limitation in the RC release record.

**Blocks:** `1.0.0-rc.1` if the local supported journey is not proven; final
  `1.0.0` in all cases.

---

### Task RC-P0-08: Complete exact-SHA release governance and recovery record

**Priority:** P0

**Objective:** Convert passing implementation checks into a defensible RC
  candidate with reproducible source/artifact identity, explicit known
  limitations, rollback/recovery instructions, and separate publication
  authorization.

**Exact files or areas likely affected:**

- `docs/engineering/v1.0-qualification-record.md`
- `docs/engineering/release-qualification.md`
- `docs/releases/v1.0.0.md`
- `CHANGELOG.md`
- `scripts/release_evidence.py`
- `scripts/verify_wheel.py`
- `.github/workflows/validation.yml`
- Git branch/tag/release metadata outside the working tree

**Acceptance criteria:**

- Candidate SHA, branch/ref, clean-tree status, Python versions, qualification
  date, exact commands, and all pytest categories are recorded.
- Serial and parallel results reconcile; expected skips/xfails and any
  baseline-identical validator warnings are named rather than reported as
  passes.
- Wheel is built from the exact candidate SHA in a fresh environment, with
  filename, SHA-256, installed import path, and qualification output recorded.
- Release notes identify supported surfaces, deferred/experimental surfaces,
  compatibility/migration behavior, known limitations, and rollback/recovery
  procedure (restore the prior valid Campaign/artifact revision and never
  replay an interrupted mutation automatically).
- The final release invariant is checked: source-qualified commit equals
  artifact-built commit equals installed-qualified commit equals tag target.
- Publication authorization is a separate recorded decision; no tag, push, or
  registry publication occurs as part of qualification alone.

**Verification command or evidence required:**

- `git status --porcelain` is empty at freeze.
- `git rev-parse HEAD` is recorded before qualification.
- `python scripts/check.py`
- `python -m pytest -n auto -q --tb=short --junitxml=qualification.xml`
- `python scripts/verify_wheel.py`
- `git show-ref --tags` and remote inspection after any authorized publication.

**Risk:** High if skipped: the project can have passing local tests but no
  defensible claim that the published artifact corresponds to the qualified
  source.

**Human approval required:** Yes for candidate freeze, release-owner risk
  acceptance, tag creation, push, and publication. Automated checks and record
  preparation do not require approval.

**Blocks:** Both `1.0.0-rc.1` and final `1.0.0`.

---

### Task RC-P2-09: Prevent accidental support claims from experimental surfaces

**Priority:** P2

**Objective:** Keep post-1.0 ideas physically and contractually recognizable
  as experimental/deferred so their presence cannot be mistaken for RC support.

**Exact files or areas likely affected:**

- `docs/1.0-scope.md`
- `docs/releases/v1.0.0.md`
- `docs/engineering/cli-contract.md`
- `README.md`
- `src/auteur/cli_parser.py` help text
- `src/auteur/cli_dispatch.py` unsupported/deferred handlers
- `tests/test_release_integrity.py`
- `tests/test_cli_contract.py`

**Acceptance criteria:**

- Experimental/deferred commands and modules are labeled consistently in help,
  scope docs, and release notes.
- No experimental feature is included in the RC golden-path qualification
  matrix or described with a support guarantee.
- Unsupported commands fail closed without mutating state.
- Historical acceptance documents remain historical and are not used as
  current release evidence.

**Verification command or evidence required:**

- `python scripts/validate-release-scope.py`
- `python -m pytest tests/test_release_integrity.py tests/test_cli_contract.py -q`
- Repository scan showing no current release document promises excluded
  capabilities.

**Risk:** Low-medium. Mislabeling does not usually corrupt data, but it creates
  support and compatibility obligations the RC cannot satisfy.

**Human approval required:** Yes only if a capability is promoted into or
  removed from the stable scope.

**Blocks:** Does not block RC if current scope is already mechanically enforced;
  blocks final `1.0.0` if accidental support claims remain.

---

## Completion gate

The minimum defensible RC is achieved only when RC-P0-01 through RC-P0-05 and
RC-P0-08 are complete, RC-P1-06 and RC-P1-07 have no unexplained failures, and
the exact candidate is frozen. RC-P2-09 may be deferred only when the current
scope validator and contract tests already prove that excluded capabilities
cannot be interpreted as supported.

No task may be marked “release-ready” merely because its focused tests pass.
The final state must distinguish implemented behavior, source qualification,
artifact qualification, candidate freeze, and publication authorization.

## Self-review against the audit brief

- Local Campaign persistence: RC-P0-02.
- Validation and semantic inspection: RC-P0-03.
- Handoff/resume and recovery: RC-P0-04.
- Bundle handling: RC-P0-05.
- CLI/Python contracts: RC-P0-01 and RC-P1-06.
- Failure-domain and integration evidence: RC-P1-07.
- Exact-SHA release governance: RC-P1-08.
- Prevention of accidental post-1.0 support claims: RC-P2-09.
- Cloud, collaboration, GUI, markerless mapping, merge/split, grouped
  decisions, and broad Series intelligence are intentionally not proposed as
  implementation work.
