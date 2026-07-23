# Changelog



## v0.8.1 (2026-07-23) — Packaging Fix: composition resources in wheel

### Fixed (Issue #37)

- **Packaged `data/composition/` under `src/auteur/data/composition/`** so that
  composition constraint rules are included in the built wheel and remain
  accessible after installation.
- **Updated `CompositionRulesLoader`** to use `importlib.resources.files()`
  instead of brittle `Path(__file__).parents[...]` traversal. The loader now
  resolves resources from the `auteur.data.composition` package regardless of
  whether running from source checkout, editable install, or an installed wheel.
- **Eliminated 25 pre-existing `FileNotFoundError` failures** in
  `test_rules_loader.py`. These failures existed since v0.7.0 (confirmed on base
  commit `bd7f762`), were waived in v0.8.0, and are now fully resolved.

### Backward compatibility

- The `yaml_path` parameter on `CompositionRulesLoader.__init__()` continues to
  work for explicit path arguments. When `None` (the default), resources are
  loaded via `importlib.resources` instead of the old `Path(__file__).parents`
  traversal.
- Composition rule contents, identifiers, ordering, validation results, and
  CLI-visible behavior are unchanged.

### Tests

- 5 new regression tests in `TestPackagingFix` covering package-resource loading,
  explicit-path backward compat, missing-resource errors, and wheel content
  verification.
- All 25 formerly-failing tests now pass.
- Complete repository inventory: 3,215 tests (3,210 baseline + 5 new).
  Zero v0.8.1-caused failures.

### Wheel

- `auteur-0.8.1-py3-none-any.whl` — built from commit `%V0.8.1_SHA%`.
- Version metadata: 0.8.1 (pyproject.toml, `auteur.__version__`, wheel METADATA).
- Wheel contains: `auteur/data/composition/__init__.py`,
  `auteur/data/composition/composition_constraints.yaml`,
- `auteur-0.8.1-py3-none-any.whl` — built from commit `86ba700`.
- Fresh-install qualification: 10/10 scenarios pass.
  Working-directory independence confirmed (loads from `C:\`).
  No source-checkout path required.

### Previous waiver removed

The v0.8.0 acceptance report's known-baseline-failures waiver for
`test_rules_loader.py` is rescinded. All 25 pre-existing failures are
eliminated.
## v0.8.0 (2026-07-22) — Decision Orchestration and Evidence Integration

### Decision Lifecycle and Lineage

- **`auteur decision history <id>`**: Shows snapshot history with readiness, state, freshness.
- **`auteur decision lineage <id>`**: Shows snapshot chain with lineage depth and preceding IDs.
- **`auteur decision diff <a> <b>`**: Field-level diff between two snapshots.
- All snapshots carry deterministic `snapshot_id` and link via `preceding_snapshot_id`.

### Versioned Contract Schemas

- All decision artifacts versioned with `schema_version` field (`"decision-snapshot-v1"`).
- v0.7.0 snapshots auto-detected and upgraded on load.
- Fixture factories for testing (`make_snapshot_fixture`, `make_evidence_fixture`, etc.).

### Direct Reasoning Integration

- New `ReasoningAdapter` reads critic reports and synthesis reviews per candidate.
- Reasoning evidence mapped to `DecisionEvidence` with preservation of nuanced findings.
- Staleness detection via source content hash comparison.
- Missing reasoning surfaces as `NEEDS_EVALUATION`.

### Direct Reconciliation Integration

- New `ReconciliationAdapter` wraps `ReconciliationStore` from expression layer.
- Conflict classification: technical (`NEEDS_RECONCILIATION`) vs creative (`NEEDS_AUTHOR_DECISION`).
- Proposal application and prose merging kept outside automatic execution.

### Decision Conflict Model

- `ConflictType`: FACTUAL, STRUCTURAL, INTERPRETIVE, CREATIVE.
- `ResolutionBoundary`: RECOMPUTE, RECONCILE, REQUEST_AUTHOR_CHOICE, BLOCK_ACCEPTANCE.
- No single subsystem is silently authoritative — all conflicting claims preserved.
- CLI: `auteur decision conflicts <id>`.

### Downstream Impact Preview

- `auteur decision impact-preview <id> --candidate <cand>` simulates acceptance consequences.
- Definite and inferred impact classification via dependency graph.
- Completely read-only: no canonical or accepted-state mutation.

### Bidirectional Workflow Integration

- `workflow next` queries the Decision Workspace when a `decision_service` is configured.
- Decision actions (blocked, needs-author, evaluation, acceptance-ready) rank alongside workflow actions.
- Safe decision actions (inspect, compare, conflicts, impact-preview) eligible for auto-execution through the engine.
- Authority-bearing decision actions refused by `can_execute()`.
- Workflow and non-safe decision subcommands blocked from recursive/auto dispatch.
- When no decisions are open, behavior is identical to v0.7.0.

### Executable Safe Actions

- `SAFE_DECISION_ACTIONS` registry: generate-candidate, evaluate-candidate, compare-candidates, prepare-acceptance, refresh-impact-analysis, refresh-decision-snapshots, run-deterministic-validation.
- Idempotent snapshot refreshes (`auteur decision refresh`).
- Deterministic validation (`auteur decision revalidate`).
- All operations preserve failure diagnostics.

### Acceptance Preparation

- Enriched `AcceptancePreparation` with satisfied/unsatisfied prerequisites, candidate tradeoffs, reasoning and reconciliation summaries, downstream impact, and stale-after-acceptance identification.
- Typed acceptance request generated only when all prerequisites met.
- Acceptance itself is never performed automatically.

### Status Improvements

- `auteur decision list` supports filters: `--readiness`, `--stale`, `--fresh`, `--requires-author`, `--bypass-low-priority`.
- Grouping by chapter, target, and readiness.
- Decisions sorted deterministically by chapter then ID.

### Qualification Harness

- 10 canonical qualification scenarios in `tests/qualification/`.
- Each scenario uses subprocess CLI invocations against deterministic fixture projects.
- Verifies exit codes, JSON output, and no canonical/accepted-state mutation.
- Scenarios: impact creates decision, no candidate, unevaluated candidate, candidate comparison, stale reasoning, reconciliation conflict, author choice, acceptance-ready, blocked acceptance, decision resolution.

### Architecture

- New `src/auteur/decision/contracts.py` — versioned schema definitions.
- New `src/auteur/decision/adapters/` — subsystem adapter pattern.
- New `src/auteur/decision/conflict_detector.py` — cross-evidence conflict classification.
- Adapters are the only integration points importing from their target subsystem.
- All existing tests preserved with zero regressions.

## v0.7.0 (2026-07-21) — Author Decision Workspace

### New decision workspace subsystem

- **`auteur decision status`**: Shows project-level decision status including
  open impact findings, decisions by readiness, and highest-priority blocker.
- **`auteur decision list`**: Lists all assembled decisions from impact and
  convergence state with readiness, freshness, and lifecycle state.
- **`auteur decision inspect <id>`**: Full decision detail with evidence,
  candidates, blockers, and unresolved choices.
- **`auteur decision evidence <id>`**: Evidence grouped by classification
  (fact, derived_inference, recommendation, author_choice).
- **`auteur decision compare <id>`**: Candidate comparison with dimensions,
  conflicts, and recommendation.
- **`auteur decision next <id>`**: Recommended next action with authority level
  and safe-to-execute flag.
- **`auteur decision prepare-acceptance <id> --candidate <id>`**: Readiness
  verification without performing acceptance. Checks freshness, reasoning
  evidence, obligations, author choices, and reconciliation.
- All commands support `--project` and `--json`.

### Decision lifecycle model

- 6 lifecycle states: OPEN → EVIDENCE_INCOMPLETE → READY_FOR_ACCEPTANCE →
  AUTHOR_DECISION_REQUIRED → BLOCKED → STALE
- 9 readiness levels: BLOCKED, NEEDS_AUTHOR_DECISION, NEEDS_RECONCILIATION,
  NEEDS_COMPARISON, NEEDS_EVALUATION, NEEDS_CANDIDATE, READY_FOR_ACCEPTANCE,
  RESOLVED, STALE
- Evidence classification: FACT, DERIVED_INFERENCE, RECOMMENDATION, AUTHOR_CHOICE
- Evidence freshness: CURRENT, STALE, UNKNOWN

### Subsystem integration

- Impact findings → decisions from `auteur.impact.analyzer` with evidence mapping.
- Convergence targets → decisions from `auteur.convergence` with candidate loading.
- Reconciliation conflicts loaded from convergence proposals.
- Next action recommendation based on decision readiness with authority-level
  gating for safe-to-execute actions.

### Architecture

- New `src/auteur/decision/` package with clean separation:
  `models.py` (decision types), `assembler.py` (subsystem → decision mapping),
  `persistence.py` (immutable snapshots), `service.py` (workspace composition),
  `cli.py` (subcommand registration and handlers).
- Composes with `auteur.impact`, `auteur.convergence`, `auteur.workflow`,
  `auteur.provenance`.
- No LLM calls. Deterministic composition from persisted subsystem state.
- Immutable snapshots under `.auteur/decisions/`.

### Tests

- 41 new tests covering decision models, assembler, persistence, store, and
  workspace service integration.
- Deterministic fixture projects with impact and convergence state.
- Semantic assertions for readiness, evidence, candidates, and lifecycle.
## v0.6.0 (2026-07-21) — Realization Convergence and Scene-Level Revision Workflow

### New convergence subsystem

- **`auteur realization status`**: Shows convergence status for a chapter/scene
  including target info, obligations, preserved regions, and candidates.
- **`auteur realization revise`**: Inspects or initializes a revision workflow
  for a bounded target. Does not rewrite content.
- **`auteur realization candidates`**: Lists candidates for a revision target
  with status, freshness, and strategy.
- **`auteur realization generate-candidate`**: Generates a noncanonical candidate
  realization using a specified strategy (minimal_repair, continuity_preserving,
  structural_alternative, full_regeneration).
- **`auteur realization register-candidate`**: Registers an externally authored
  candidate from a file path. No model call required.
- **`auteur realization compare`**: Deterministic, multidimensional comparison
  of candidates with obligation coverage, freshness, evaluation status, and
  preservation conflict detection.
- **`auteur realization reconcile`**: Creates a typed reconciliation proposal
  with satisfied/unsatisfied obligations, conflicts, continuity risks, and
  authority-required choices.
- All commands support `--project`, `--json`, `--chapter`, `--scene`.

### Architecture

- New `src/auteur/convergence/` package with clean separation:
  `models.py` (typed models), `scope.py` (target resolution), `obligations.py`
  (obligation collection from structure/identity/impact),
  `preservation.py` (preservation analysis), `candidates.py` (candidate
  lifecycle, generation, registration), `comparison.py` (deterministic
  comparison), `planner.py` (reconciliation proposals), `persistence.py`
  (immutable artifact storage), `cli.py` (CLI subcommand registration).
- Composes with existing `auteur.impact.models` (ImpactSeverity, PreservationStatus),
  `auteur.workflow.models` (WorkflowAction, AuthorityLevel),
  `auteur.provenance` (artifact lifecycle, content hashing).
- No parallel acceptance, provenance, or reconciliation system.
- Deterministic, offline, no LLM calls for workflow/inspection/comparison.

### Central invariant

- Candidate generation ≠ reconciliation ≠ acceptance ≠ canonical mutation.
- Generated and registered candidates are always noncanonical.
- No accepted prose is ever silently replaced.
- Acceptance remains explicit and authority-bearing.

### Tests

- 61 new convergence tests across 2 test files:
  - `test_convergence.py` — target resolution, obligations, preservation,
    candidate lifecycle, comparison, reconciliation, persistence, acceptance
    boundary, strategies (53 tests)
  - `test_convergence_e2e.py` — end-to-end dogfood scenarios including
    changed outline requiring repair, external registration, preserved beats,
    missing boundaries, JSON output, missing project, stale candidates (8 tests)
- Semantic assertions (not snapshots) for IDs, status, authority, lifecycle.
- Zero new xfails or skips.
- All pre-existing xfails unchanged (Layer 3 SceneOutline only).

## v0.5.0 (2026-07-20) — Structural Revision Propagation and Impact Planning

### New impact planning subsystem

- **`auteur impact status`**: Shows unresolved impact summary (blocked,
  reconcile, regenerate, review counts) with human-readable or `--json` output.
- **`auteur impact analyze`**: Detects content-hash changes, traces dependency
  graph, classifies direct and transitive impact with severity taxonomy.
- **`auteur impact explain <artifact-or-id>`**: Shows dependency paths,
  propagation rules, preservation status, and recommended actions.
- **`auteur impact plan`**: Generates ordered repair plan with deterministic
  ordering (BLOCKED > RECONCILE > REGENERATE_CANDIDATE > REVIEW, by chapter).
- All commands support `--project`, `--json`, `--save` for persistence.

### Architecture

- New `src/auteur/impact/` package with clean separation:
  `models.py` (types), `graph.py` (dependency graph), `analyzer.py`
  (change detection + propagation), `rules.py` (rule catalog R001–R017),
  `planner.py` (repair plan), `persistence.py` (immutable reports),
  `cli.py` (handlers + formatters).
- Composes with existing `auteur.provenance.store.ArtifactStore` —
  reuses content hashing, lifecycle, dependency records; does not duplicate.
- Integrates with `auteur workflow` via `ImpactAnalyzer.workflow_actions()`.
- Deterministic, offline, no LLM calls.

### Impact taxonomy

- 5-level severity: NONE → REVIEW → RECONCILE → REGENERATE_CANDIDATE → BLOCKED
- 5-level preservation: PRESERVE → PRESERVE_WITH_REVIEW → PARTIAL_PRESERVATION
  → REGENERATE → UNKNOWN
- 14+ explicit propagation rules covering the full workflow chain
- Severity combination: highest severity wins, all paths preserved

### Repair planning

- Deterministic ordering: missing deps → BLOCKED → RECONCILE → REGENERATE →
  REVIEW, by chapter index, alphabetical tie-break
- Prerequisite tracking between actions
- Safe-to-execute flag based on authority level
- Preservation guidance with preserved artifact list

### Persistence

- Immutable historical analysis and plan reports under `.auteur/impact/`
- `latest.yaml` convenience pointer (replaced, not appended)
- `authority: derived`, `canonical: false`

### Tests

- 111 new focused tests across 8 test files:
  - `test_graph.py` — construction, cycles, missing deps, serialization (21)
  - `test_rules.py` — rule matching, severity combination (12)
  - `test_analyzer.py` — graph building, change detection, propagation (14)
  - `test_planner.py` — ordering, prerequisites, blocking (10)
  - `test_persistence.py` — save/load, immutability, latest pointer (12)
  - `test_cli.py` — registration, handlers, missing project (14)
  - `test_models.py` — model roundtrip, enums, defaults (16)
  - `test_workflow_integration.py` — unresolved impact, workflow actions (6)
  - `test_dogfood.py` — 10 dogfood scenarios (16)
- Semantic assertions (not snapshots) for artifact IDs, severity, ordering
- No broad skips or xfails

## v0.4.0 (2026-07-20) — Guided Author Workflow

### New workflow module

- **`auteur workflow status`**: Shows current workflow stage, blockers, and
  recommended actions. Composes with `auteur.status.gather_status()` for
  project state and layers typed workflow semantics on top.
- **`auteur workflow next`**: Displays the single next recommended action with
  authority level. Supports `--execute` flag for safe actions (read-only,
  derived artifact, candidate generation).
- **`auteur workflow explain`**: Explains a specific stage or the current
  workflow state. Accepts optional stage name argument.
- All workflow commands support `--json` output for programmatic use.
- Deterministic, no LLM calls, no shared mutable state.

### Workflow engine

- 9-stage model: Identity → Structure → Realization → Drafting → Reasoning →
  Reconciliation → Acceptance → Assembly → Publishing
- 8-category blocker taxonomy: missing_prerequisite, invalid_artifact,
  stale_artifact, blocking_reasoning, unresolved_reconciliation,
  authority_required, ambiguous_candidate, unsupported_state
- 6-level authority classification: read_only, derived_artifact,
  candidate_generation, proposal_generation, authority_bearing,
  canonical_mutation
- Safe execution boundary: only first 3 authority levels eligible for `--execute`

### Architecture

- New `src/auteur/workflow/` package with clean separation:
  `models.py` (types), `rules.py` (detection), `engine.py` (composition),
  `cli.py` (handlers + formatters)
- Composes with existing `status.py`, does not duplicate or replace it
- Follows existing CLI patterns: HandlerResult → format_* → dispatch
- No changes to existing expert commands

### Tests

- 42 new tests covering models, rules, engine, CLI, and project fixtures
- Deterministic fixture projects for each workflow stage
- Semantic assertions (not snapshots) for stage detection, blocker inference,
  recommendation ranking, and execution safety boundary

## v0.3.2 (2026-07-19) — Reasoning Runtime Completeness

### Normalized synthesis

- `_reasoning_sections()` no longer manufactures synthetic `hypotheses` or `evaluation`
  sections; claims and observations faithfully preserve critic, severity, rule,
  evidence, and requested_change from source findings
- Removed dead `_normalize_findings_for_synthesis` function (duplicated the same
  flawed approach but was never called)

### Provider/metadata capture

- Provider and model fields captured from formal LLM client attributes
  (`provider`, `model`) only — no `_provider`/`_model` prefix fallback, no
  module-name heuristic that could return misleading values
- Fields persisted in ExecutionOutcome and draft_review artifacts

### Timeout enforcement

- `critic_timeout` parameter on `ReasoningRuntime.__init__()` enables bounded
  per-critic execution deadlines via `concurrent.futures.wait()`
- Hung critics are killed and recorded as `FAILED` with `reason="critic timed out"`
- Timeout handling tested with slow critics that exceed deadline
- Default `None` preserves backward-compatible behavior (no timeout)

### Test rigor

- 12 new platform tests covering timeout enforcement, provider metadata
  (explicit, prefixed, absent, no module-name leak), and faithful normalization
- 61 total focused reasoning tests passing
- Backward compatibility tests for v0.3.0/v0.3.1 artifact reading
- Negative CLI tests for missing/malformed/empty files
- Failure semantics tests (multi-failure coexistence, no false pass)

### Other

- `concurrent.futures.wait()` replaces `as_completed()` in runtime pool
  execution for cleaner timeout semantics
- Acceptance proof corrected: baseline is v0.3.1, not v0.3.0


## v0.3.1 (2026-07-18) — Reasoning Runtime Hardening

### Concurrent critic execution

- `_dependency_layers()` groups critics by dependency depth; each layer executes
  via `ThreadPoolExecutor(max_workers=5)`; deterministic ordering preserved
- Token accounting: per-critic `input_tokens`/`output_tokens` captured from LLM
  client; aggregated in run/review artifacts; displayed in Markdown review
- Duration tracking in `ExecutionOutcome.duration_ms`
- Synthesis adaptation: CriticFinding fields mapped into reasoning sections
- Runtime dependency injection: `PipelineRunner.__init__(reasoning_runtime=None)`

### CLI qualification

- `format_review()` and `reasoning inspect` support string `freshness` fields and
  bare-name critic fallback (`contract` → `draft.contract`)
- All commands work without API key using persisted fixtures
- 42 new tests across 3 files


## v0.3.0 (2026-07-18) — Production Reasoning Runtime Integration

- Created `src/auteur/reasoning/draft_critics.py` — 5 critic adapters
- Created `src/auteur/reasoning/draft_review.py` — atomic persistence, freshness detection
- Modified `PipelineRunner.draft_chapter()` to call runtime
- Compatibility projection: `ExecutionOutcome` → `CriticFinding` → `ValidationReport`
- Real-provider dogfood (Gemini 2.5 Flash) verified all 5 critics
- 18 new tests

## v0.2.1 (2026-07-18) — Release Integrity and Product Invariants Hardening

### Repository hygiene

- Removed tracked Windows temp/scratch files (Claude Code scratchpad artifacts)
- Removed `examples/canonical_story/temp_lantern_phase_a/` dogfood output
- Removed tracked `.superpowers/` development artifacts
- Updated `.gitignore` with narrow patterns to prevent recurrence
- `uv.lock` retained as intentional package-management lockfile

### Ontology install-safe packaging

- Moved runtime ontology resources into `src/auteur/data/ontology/` package namespace
- `OntologyLoader` uses `importlib.resources` instead of repository-root path traversal
- Ontology loading works from installed wheel, editable install, and source checkout
- Added `pyproject.toml` package-data declarations
- Clear missing-resource error messages

### Publishing integrity

- Accepted Book manuscript content hash verified before any output is produced
- Tampered manuscript blocks all publishing (HTML/EPUB) atomically
- No partial output, snapshot, or run record remains after integrity failure
- No `latest.yaml` pointer is moved on failure

### EPUB3 conformance

- `mimetype` is always the first ZIP entry
- `mimetype` uses `ZIP_STORED` (uncompressed) per EPUB3 spec
- Output hash computed over raw binary bytes (not decoded/re-encoded text)
- Fixed ZIP timestamps (`1980-01-01 00:00:00`) for deterministic archives

### Deterministic output

- Wall-clock dates removed from rendered content (replaced with stable Auteur version string)
- Fixed ZIP timestamps replace runtime `date_time` values
- Identical accepted source + config + version produces byte-identical output
- Tests verify across separate invocations and directories

### Version metadata

- Hardcoded `auteur_version: "0.1.0"` replaced with `importlib.metadata.version("auteur")`
- Package version, `auteur.__version__`, and publishing snapshots share one source
- Binary output hashed with `sha256_binary()` over raw bytes

### Markdown renderer

- `markdown-it-py` declared as a required dependency (no silent fallback to `<p>`-only renderer)

### Status correctness

- Identity display reads current `story_type.genre` schema (not obsolete `genre.primary` nesting)
- Suggested commands are syntactically valid CLI invocations
- No write operations during status collection (confirmed by audit)

### CI hardening

- Python version matrix: 3.11, 3.12, 3.13
- Wheel build + installed-wheel smoke test
- Installed CLI exercises: `--help`, `ontology list`

### Test verification

- 52 existing publishing tests preserved
- New tests: ontology packaging (4), publishing integrity (6), EPUB structure (5),
  determinism (4), version metadata (3), status correctness (8), output hashing (2),
  markdown renderer (1)
- Total: ~85 tests

### Key metrics

- Files changed: ~15 (modified + new)
- Runtime dependencies added: `markdown-it-py>=3.0`

## v0.2.0 (2026-07-18) — Auteur v1.1 Product Readiness

### Major features

- **auteur publish** — Immutable HTML/EPUB rendering pipeline. Accepts a
  canonical Book expression and produces distributable artifacts with zero
  Auteur internal markers, no new dependencies (stdlib EPUB3 via zipfile +
  ElementTree), deterministic output bytes, and an immutable publishing
  snapshot model.
  - `PublishingSnapshot` captures accepted Book state (content-addressed,
    written-once snapshot ID)
  - HTML renderer: title page, table of contents, default CSS, custom CSS
    support
  - EPUB3 renderer: valid EPUB archive (XHTML chapters, OPF manifest, nav
    document, stylesheet, mimetype-first ordering, forward-slash paths)
  - Snapshot model separates publication identity (`pub_<id>.yaml`, immutable)
    from run records (`runs/run_<ts>.yaml`, each invocation) with a
    `latest.yaml` convenience pointer
  - CLI: `auteur publish --format html|epub --output <path>`

- **auteur status** — Author workspace primitive (like `git status` for a
  novel). Aggregates identity, blueprint, structure, chapter, book, and
  reconciliation health into a single view with stale-item detection,
  blockers, and recommended next command. Supports `--json` and `--verbose`.

- **Book reconciliation (Phases A–C4, 300+ tests)** — Complete provenance-rich
  workflow: candidate publication, decisions (accept/reject/defer), pointer-based
  recomposition, deterministic comparison, 20-point acceptance gate, and
  reconciliation completion. Source-of-truth authority model with three
  decoupled tiers.

### Infrastructure

- **Schema versioning** — `Project.init()` writes `.auteur/project.yaml` with
  `schema_version`; `Project.load()` validates and warns on mismatch.
- **Dead code removal** — 3 stale genre CLI adapters removed, ~107 lines of
  legacy handler branches removed, 2 dead test files deleted, 5 misplaced test
  files moved from `src/` to `tests/`.
- **Quality infrastructure** — Ruff config (E/F/W selects), coverage config,
  pytest `--tb=short`, `.pre-commit-config.yaml` (ruff auto-fix + format).
- **Shared bootstrap cache** — Session-scoped `CanonicalStoryBootstrap` cache
  with `pytest-xdist` support, reducing per-test-file setup from ~6s to
  sub-second.

### Test verification

- 52 publishing pipeline tests (30 unit + 22 release qualification)
- Deterministic HTML/EPUB byte verification
- EPUB3 conformance (mimetype ordering, forward slashes, OPF metadata, spine,
  navigation)
- Unicode handling, output-path collision, stale/missing book handling
- Manuscript tampering detection, cross-format consistency
- CLI parser and module packaging verification

### Key metrics

- 3 commits in this release stage (7413af6, 85a6593, 3b4a0a6)
- +1,290 lines, -457 lines across all v1.1 work
- 0 new runtime dependencies added
