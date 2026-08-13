# Repository Sensemaking Brief

## 1. Repository goal

Auteur is an opinionated **narrative-engine toolkit for long-form fiction**. It turns raw creative input into a recommended story engine (`story_identity.yaml`), validates that engine deterministically, compiles a structural `blueprint.yaml`, runs deterministic structure diagnostics, and treats chapter outlining and prose generation as optional downstream stages. Its core architectural claim is that **deterministic code owns schemas, project files, validation models, artifact writing, and retry flow**, while LLM calls supply only creative planning, prose, and critic judgment (`README.md:3`, `README.md:25-29`).

## 2. Current shape

- **Package**: `src/auteur` — ~44 submodules spanning `narrative_ontology`, `narrative_blueprint`, `narrative_realization`, `reasoning`, `structure`, `decision`, `planning`, `review`, `simulation`, `genre_packs`, and three genre pipelines (`netorare`, `mystery`, `gentlefemdom`).
- **CLI**: `auteur = "auteur.cli:main"` (`pyproject.toml:23`), with `identity`, `blueprint`, `structure`, `cartographer`, `plan`, `simulate`, `draft`, `accept`, `retry`, and `state` command families.
- **Skills**: `skills/` holds 29 skills, including a vendored sensemaking-skills ecosystem (`repo-sensemaker`, `workflow-orchestrator`, `problem-framer`, `unknowns-mapper`, `tdd`, `to-issues`, `triage`, etc.).
- **Validation**: `scripts/` holds 15 `validate-*.py` validators plus `check.py` (the aggregate verification entrypoint) and an `orchestration-runner.py`.
- **Docs**: 510 markdown files — 18 ADRs, architecture/acceptance/review docs, plus `docs/archived/` and `docs/superpowers/` planning notes.
- **Tests**: 248 `test_*.py` files under `tests/` (741 total test-pattern files counted repo-wide by the probe).

## 3. Strong signals

1. **Verification gap is zero.** The README's declared check (`scripts/check.py`) is actually enforced in CI: `verification_gap.vg = 0.0`, `declared=['scripts/check.py']`, `enforced=['pytest', 'scripts/check.py']` (`docs/reviews/2026-08-13-auteur-repo-sensemaking-probe-report.yaml`; `README.md:337-343`; `.github/workflows/validation.yml:28-32`). The "deterministic rails" claim is genuinely wired, not aspirational.
2. **Version is consistent.** Probe `relationships.version.findings` is empty; declared version `0.37.1` (`pyproject.toml:7`) is the single distinct value across 114 doc/test version claims. No version drift.
3. **Mature decision history.** 18 ADRs, all `Accepted`, 001-017 (`docs/reviews/2026-08-13-auteur-repo-sensemaking-probe-report.yaml` `relationships.adr.catalog`).
4. **Deterministic validation culture.** 15 validators, 73% fixture coverage, aggregated under `scripts/check.py` -> `test-validators.py` + `validate-repo.py` + ruff + pytest (`scripts/check.py:11-16`).
5. **Clean working tree** (dirty=1, one unrelated file `.claude/settings.json`).

## 4. Missing pieces

1. **Duplicate ADR identifier.** Two files both claim `013`: `docs/adr/013-series-graph-semantics.md` ("Series Dependency Graph Semantics") and `docs/adr/013-universe-to-series-propagation.md` ("Universe-to-Series Constraint Propagation"). The probe's ADR catalog records both with `id: '013'`. One should be renumbered (the sequence continues 014-017).
2. **Stale root-level `HANDOFF.md`.** It describes Cartographer as "newly implemented" and claims "All **184 unit and integration tests** pass cleanly" (`HANDOFF.md:64`), with absolute `file:///h:/GithubRepositories/...` links (`HANDOFF.md:57`) — long superseded by the current 0.37.1 state (741 test files).
3. **Working-tree artifact sprawl.** ~9,576 ignored root-level reasoning-report JSON files (`Get-ChildItem *.json` = 9576) plus 36 root `pytest-*`/`qualification-*` log+xml files. Reports are written by `ReasoningRuntime` to `self.report_dir / f"{report_id}.json"` (`src/auteur/reasoning/runtime.py:339-341`); the intended path is `project/.auteur/reasoning` (`src/auteur/cli_dispatch.py:66`), but a test/dogfood path has been emitting them into the repo root, and `.gitignore`'s `/*.json` (`:37`) hides them instead of enforcing the location.
4. **4 validators without fixtures.** `fixtures_coverage.missing_fixtures = [validate-mode-coverage, validate-project-classification, validate-repo, validate-workflow-design]` — including `validate-repo.py`, the script that certifies repo alignment.

## 5. Improvement opportunities

- Renumber the duplicate ADR and add a `validate-repo.py` guard that rejects duplicate `docs/adr/NNNN-*` identifiers.
- Archive or delete `HANDOFF.md` (point-in-time handoff), or move it under `docs/handoffs/`.
- Define and enforce a canonical `report_dir` for `ReasoningRuntime`; add a `git clean -fdX` or `reasonix-clean.ps1` step to README/CI so root sprawl cannot recur.
- Add `tests/fixtures/<validator>/{valid,invalid}` for the 4 uncovered validators.

## 6. Weakest boundary

The most fragile boundary is the **repository's self-description: its decision registry and handoff documents no longer uniquely or accurately name the current state.** The sharpest, mechanically-verified defect is the duplicate ADR identifier `013` (two distinct decisions sharing one canonical name), compounded by a stale root `HANDOFF.md` whose state-vocabulary ("newly implemented", "184 tests") describes a superseded release.

**Weakness type:** Vocabulary Drift

## 6.5. Problem classification (fog type)

**docs_fog** — the blocking problem is drift between documentation/registry identifiers and verified reality (duplicate ADR number, stale handoff), not unclear user needs (product), screen/flow design (ui), or module coupling/performance (architecture).

## 7. Evidence

<!-- mode: investigative -->

`docs/adr/013-series-graph-semantics.md:1` and `docs/adr/013-universe-to-series-propagation.md:1` both declare `# ADR 013` for two different topics ("Series Dependency Graph Semantics" vs. "Universe-to-Series Constraint Propagation"); the probe catalog confirms both entries carry `id: '013'` (`docs/reviews/2026-08-13-auteur-repo-sensemaking-probe-report.yaml: relationships.adr.catalog`). `HANDOFF.md:57` still links `file:///h:/GithubRepositories/auteur/...` absolute paths and `HANDOFF.md:64` claims "184 unit and integration tests", whereas the probe counts 741 test files today. `scripts/validate-repo.py:13-54` enumerates the core-file/registry contracts but has no check for duplicate ADR numbers, and its `file:///` check (`scripts/validate-repo.py:338-339`) only scans `examples/`, so `HANDOFF.md`'s absolute paths are unguarded.

Logic trace: the repo's trust model is "deterministic code owns artifact writing and validation rails" (`README.md:25-29`), and CI genuinely enforces the declared check (`verification_gap.vg = 0.0`). The rail that is *not* enforced is the one that keeps the repo's own names canonical: two ADRs share identifier `013` (no validator rejects the collision), and the root handoff document still speaks in a superseded release's vocabulary. Because the verified current state (741 test files, 18 accepted ADRs, v0.37.1) disagrees with the registered state (duplicate 013, "184 tests"), the self-description boundary is the weakest — a human or downstream skill reading "ADR 013" cannot tell which decision it names.

## 8. Evidence excerpts

```yaml
evidence_excerpts:
  - file: docs/adr/013-series-graph-semantics.md
    lines: L1
    quote: "# ADR 013: Series Dependency Graph Semantics"
    supports_claim: "First of two files declaring the canonical identifier ADR 013."
  - file: docs/adr/013-universe-to-series-propagation.md
    lines: L1
    quote: "# ADR 013: Universe-to-Series Constraint Propagation"
    supports_claim: "Second file declaring ADR 013 for a different decision -> duplicate identifier."
  - file: HANDOFF.md
    lines: L57
    quote: "* **Cartographer Compiler & Splitting**: Verified in [test_cartographer_compiler.py](file:///h:/GithubRepositories/auteur/tests/test_cartographer_compiler.py)."
    supports_claim: "Stale handoff uses absolute file:/// paths to a specific machine."
  - file: HANDOFF.md
    lines: L64
    quote: "All **184 unit and integration tests** in the suite pass cleanly."
    supports_claim: "Claims '184 unit and integration tests' vs. current 741 test files (probe)."
  - file: src/auteur/reasoning/runtime.py
    lines: L339-L341
    quote: |
      self.report_dir.mkdir(parents=True, exist_ok=True)
      (self.report_dir / f"{report_id}.json").write_text(
          json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    supports_claim: "ReasoningRuntime writes {report_id}.json into a caller-supplied report_dir."
  - file: .gitignore
    lines: L33-L37
    quote: |
      # ReasoningRuntime report output (generated test artifacts)
      reports/

      # Root-level JSON files (test/report artifacts)
      /*.json
    supports_claim: "reports/ and /*.json are reactively ignored; root report files are hidden, not relocated."
```

## 9. Why this boundary matters

If the registry/handoff drift stays weak, "ADR 013" is permanently ambiguous (two decisions claim one name), a downstream skill or contributor can cite the wrong decision, and the working tree keeps accumulating ~9,576 derived JSON reports that slow tooling and risk being misread as canonical state — the probe's own `git status --ignored` hit its 30s cap trying to enumerate them (which is why `context_entropy.ce` falsely read `0.0` despite the sprawl).

## 10. Candidate next steps

1. Renumber the second ADR 013 (e.g. to 018) and update any references.
2. Add a `validate-repo.py` rule that errors on duplicate `docs/adr/NNNN-*` identifiers.
3. Move/delete the stale `HANDOFF.md` (or relocate it to `docs/handoffs/` with a dated name).
4. Enforce a canonical `report_dir` and clean the ~9,576 root JSON + 36 pytest/qualification files.
5. Add test fixtures for the 4 uncovered validators.

## 11. Recommended next step

Renumber the duplicate ADR and add a `validate-repo.py` duplicate-identifier guard. This is the smallest, highest-leverage fix and closes the registry-drift boundary with a deterministic check, consistent with the repo's existing "deterministic validation rails" philosophy. (Verified current state per `docs/reviews/2026-08-13-auteur-repo-sensemaking-probe-report.yaml: relationships.adr.catalog` — both `013` entries `Accepted`.)

## 12. Recommended workflow

`docs-contract-reconciliation` — its stated purpose ("resolve drift between documentation, registries, artifact contracts, templates, and validator rules") matches the diagnosed boundary exactly, and its first step is `repo-sensemaker` with `output_artifact: repository_sensemaking_brief` (`workflow-registry.yaml`).

## 13. Machine-readable handoff

```yaml
artifact_id: repository_sensemaking_brief
schema_version: 1
source_intent_ref: docs/reviews/2026-08-13-auteur-repo-sensemaking-intent.md
user_implied_fog_type: unknown
primary_fog_type: docs_fog
diagnosis_conflict: false
escalation_recommended: false
evidence:
  - "docs/adr/013-series-graph-semantics.md (L1): declares ADR 013 - Series Dependency Graph Semantics"
  - "docs/adr/013-universe-to-series-propagation.md (L1): also declares ADR 013 - duplicate identifier"
  - "HANDOFF.md (L57, L64): stale handoff - absolute file:/// paths and '184 tests' claim vs 741 current"
  - "src/auteur/reasoning/runtime.py (L339-341): writes {report_id}.json into caller-supplied report_dir"
  - ".gitignore (L33-37): reactive reports/ and /*.json rules hide root report sprawl"
  - "docs/reviews/2026-08-13-auteur-repo-sensemaking-probe-report.yaml fixtures_coverage: missing_fixtures [validate-mode-coverage, validate-project-classification, validate-repo, validate-workflow-design]"
recommended_workflow_id: docs-contract-reconciliation
recommended_execution_mode: plan_only
weakest_boundary: "Documentation/registry self-description drift (duplicate ADR 013; stale HANDOFF.md; unenforced reasoning-report output location)"
weakness_type: Vocabulary Drift
weakness_type_explanation: null
required_inputs:
  - user_intent
  - repository_state
created_at: "2026-08-13T03:42:20Z"
immutable: true
```

## 14. Ready-to-copy prompt

> Run `docs-contract-reconciliation` on `H:\GithubRepositories\auteur` in `plan_only` mode. The repository_sensemaking_brief diagnosis is `docs_fog` with weakness type `Vocabulary Drift`. Fix, in order: (1) renumber the duplicate `docs/adr/013-universe-to-series-propagation.md` to the next free number (018) and update every reference to "ADR 013" that intended the universe-to-series decision; (2) add a `scripts/validate-repo.py` guard that errors on any duplicate `docs/adr/NNNN-*` identifier; (3) archive or relocate the stale root `HANDOFF.md` (it still links `file:///` paths and claims 184 tests vs. the current 741); (4) reconcile the reasoning-report output contract — the canonical location is `project/.auteur/reasoning` (`src/auteur/cli_dispatch.py:66`) but ~9,576 ignored reports sit in the repo root, so document the contract, relocate the stray files, and clean the root. Do not touch unrelated code; stop before execution and present the reconciliation plan for review.
