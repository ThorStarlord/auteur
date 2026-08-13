# Docs Contract Reconciliation — Implementation Plan

- **Date:** 2026-08-13
- **Branch:** `feat/docs-contract-reconciliation` (worktree `H:\GithubRepositories\auteur-docs-contract-reconciliation`)
- **Base:** main @ `c578555`
- **Source:** `docs/reviews/2026-08-13-auteur-repo-sensemaking-brief.md` (recommended workflow `docs-contract-reconciliation`, execution mode **plan_only**)
- **Status:** plan only — stops for human review before any fix is executed

## 1. Diagnosis (verified, not assumed)

All brief claims re-verified against the current tree (probe head `3acf8a1` predates
main `c578555` by PR #71 + the delegated-authority envelope commit; every claim still holds):

| # | Issue | Verified evidence |
|---|-------|-------------------|
| 1 | **Duplicate ADR identifier `013`** | `docs/adr/013-series-graph-semantics.md` and `docs/adr/013-universe-to-series-propagation.md` both declare `# ADR 013`; files run 001–017, so next free number is **018** |
| 2 | **Stale root `HANDOFF.md`** | L56–58, L70 use absolute `file:///h:/GithubRepositories/...` links; L64 claims "184 unit and integration tests" vs 741 test files today; not in `validate-repo.py` core files and no validator depends on it (safe to move) |
| 3 | **Reasoning-report output sprawl** | `src/auteur/reasoning/runtime.py:339-341` writes `{report_id}.json` into caller-supplied `report_dir`; canonical path is `project/.auteur/reasoning` (`cli_dispatch.py:66`); root cause = `src/auteur/pipeline/runner.py:41` passes `report_dir=Path()`; `.gitignore:33-37` reactively ignores `reports/` + `/*.json`; **9,576 root `*.json` + 35 root `pytest-*`/`qualification-*` files** sit in main's working tree |
| 4 | **No duplicate-ADR guard** | `scripts/validate-repo.py` has zero `adr` mentions; its `file:///` check (L335–343) only walks `examples/`, so `HANDOFF.md` paths are unguarded |
| 5 | **Fixture-coverage conflict** (brief's #4 — *needs human decision*, see §4.5) | Probe reports 4 validators missing fixtures (`validate-mode-coverage`, `validate-project-classification`, `validate-repo`, `validate-workflow-design`), but commit `9994238` **deliberately retired** their `invalid/` fixtures ("unsatisfiable negative fixtures for repo-wide validators"); `test-validators.py` requires only that the fixture dir exists, so the repo's own gate treats them as covered. The probe's `valid`+`invalid` metric is incompatible with that decision |

## 2. Agreed scope (recommended fixes, in execution order)

1. Add `validate-repo.py` duplicate-ADR-identifier guard (written **first**, TDD: fails on the live duplicate).
2. Renumber `013-universe-to-series-propagation.md` → `018` and update every reference that means the universe-to-series decision.
3. Archive/relocate stale root `HANDOFF.md`.
4. Reconcile the reasoning-report output contract: fix `runner.py:41`, document the canonical path, clean the root sprawl, and add a deterministic guard.
5. Resolve the fixture-coverage conflict per the decision in §4.5 (default recommendation: accept the `9994238` retirement, align the gate to the valid-only convention).

## 3. Non-goals

- **No LLM/behavior/product changes.** Docs + validators + report-path plumbing only.
- **No edits to evidence artifacts.** `docs/reviews/2026-08-13-*.{md,yaml}` are `immutable: true`; they record the state at probe time.
- **No wholesale merge of `fix/adr-id-collision`** (271b9be). It is based on a stale main (predates PRs #68–71), bundles unrelated harness work (reasonix scripts, AGENTS.md protocol), and its reference updates are incomplete. Fixes are redone fresh here; the branch is kept for reference and retired after this PR merges.
- **No `git clean -fdX`.** It would delete ignored-but-wanted files (e.g. main's `.venv`). Root cleanup is a **targeted** deletion (§4.4).
- No changes to `013-series-graph-semantics.md` beyond confirmation it keeps number `013`.

## 4. Steps with acceptance criteria

### 4.1 Fix 2 first: `validate-repo.py` duplicate-ADR guard (TDD)

- Add a rule to `scripts/validate-repo.py`: scan `docs/adr/`, parse the `NNN` prefix from `NNN-*.md` filenames, error on any duplicate number. Also verify the in-file `# ADR NNN` header matches the filename number (cheap, deterministic).
- **Criterion:** on the current tree (duplicate `013` still present) `python scripts/validate-repo.py` must **fail** citing both `013` files; after §4.2 it must **pass**.

### 4.2 Fix 1: renumber duplicate ADR `013` → `018`

- `git mv docs/adr/013-universe-to-series-propagation.md docs/adr/018-universe-to-series-propagation.md`; update the `# ADR 013` header to `# ADR 018`.
- Update references that mean the universe-to-series decision:
  - `CONTEXT.md` L168, L179, L210
  - `docs/artifacts.md` L60, L78, L316
  - `src/auteur/series/universe_integration.py` L1, L17, L207
  - `docs/handoffs/2026-05-21-implementation-workflow-domain-alignment.md` L17 — **review context first**; update only if it clearly names the universe-to-series decision, otherwise leave with a note.
- **Do not touch:** `docs/reviews/*` (immutable), `013-series-graph-semantics.md`.
- **Criterion:** `rg "ADR 013"` (repo-wide, excluding `docs/reviews/`) returns only series-graph-semantics + the intentional `pre-ADR 013`/legacy phrasing in `docs/artifacts.md`; `rg "013-universe"` returns nothing.

### 4.3 Fix 3: archive/relocate `HANDOFF.md`

- Recommendation: `git mv HANDOFF.md docs/handoffs/2026-08-13-root-handoff-superseded.md` (point-in-time handoff, dated per `docs/handoffs/` convention), with a one-line header noting it is superseded by `docs/reviews/2026-08-13-auteur-repo-sensemaking-brief.md`.
- Verify nothing breaks: `HANDOFF.md` is not in `validate-repo.py` core files; `validate-brief.py`'s "HANDOFF" refers to the machine-readable handoff YAML block, not this file.
- Optional (ask at review): extend `validate-repo.py`'s `file:///` check from `examples/` to all root-level + `docs/` markdown, so absolute machine paths can never re-enter.
- **Criterion:** root contains no `HANDOFF.md`; `scripts/check.py` validators still pass; no dangling relative links to `HANDOFF.md`.

### 4.4 Fix 4: reasoning-report output contract

1. **Code fix (TDD):** `src/auteur/pipeline/runner.py:41` — replace `report_dir=Path()` with the project-relative canonical path (`<project>/.auteur/reasoning`, matching `cli_dispatch.py:66`). Thread project context through `_run_critics_via_runtime`/`_get_runtime` as needed; if project path is unavailable at that call site, default to `<cwd>/.auteur/reasoning`.
   - **Regression test:** run the pipeline's critic path (focused test) and assert **no** `*.json` is written to the repo root and reports land under `.auteur/reasoning/`.
2. **Document the contract:** add a short section to `docs/engineering/` (or the ADR-adjacent runtime doc) stating: *reasoning reports are written to `<project>/.auteur/reasoning/<report_id>.json`; the repo root is never a report target.*
3. **Guard:** add a `validate-repo.py` rule — error if any root-level `*.json` exists (repo root must not accumulate derived artifacts). Root `*.json` are all gitignored (`/*.json`), so the rule cannot false-positive on tracked files.
4. **Clean main's working tree (housekeeping, on main after merge or on explicit approval):** targeted deletion of the 9,576 root `*.json` + 35 root `pytest-*`/`qualification-*` files. Never `git clean -fdX`.
   - **Criterion:** `Get-ChildItem <repo-root>/*.json` = 0; `scripts/check.py` passes; focused pipeline test proves reports land under `.auteur/reasoning/`.

### 4.5 Fix 5: fixture-coverage conflict — decision needed (recommendation: Option B)

The brief's "add `{valid,invalid}` for the 4 uncovered validators" conflicts with commit `9994238`
("retire unsatisfiable negative fixtures for repo-wide validators"): repo-wide validators run against
the whole repo, so a file that makes them fail is not constructible as a portable fixture.

- **Option A — restore `invalid/` placeholders:** rejected. Fake, unsatisfiable tests; contradicts `9994238`.
- **Option B (recommended) — accept the retirement, align the gate:** keep valid-only fixtures; extend `scripts/test-validators.py` to explicitly recognize the valid-only convention (each validator needs `valid/` **or** a documented valid-only exemption) so the repo's own gate is precise and the probe's `0.73` metric is explained as incompatible rather than a defect.
- **Option C — patch the vendored probe tool** (`sensemaking-skills probe-repo v1`) to accept valid-only coverage for repo-wide validators: out of scope for this repo (external skill), optional follow-up owned by the sensemaking-skills project.

## 5. Verification plan

1. **TDD order:** guard (4.1) fails → renumber (4.2) → guard passes → move HANDOFF (4.3) → report_dir fix + regression test (4.4) → fixture decision (4.5).
2. **Focused:** `python scripts/validate-repo.py`, `python scripts/test-validators.py`, the new regression test, `ruff check`.
3. **Full gate:** `scripts/check.py` (aggregates validators + ruff + pytest) from the worktree venv; pytest with the repo's known-good invocation (`.venv` python, `-n auto`, fresh `--basetemp .pytest-tmp/...`).
4. **Probe re-run (optional):** external `probe-repo` tool to confirm the next brief reports the fixes; not a merge gate.

## 6. Publication

- Commit the plan and (after approval) the fixes to `feat/docs-contract-reconciliation`.
- Open PR to `main`; CI is the merge gate (per `docs/engineering/release-qualification.md` and the standing delegated-authority envelope).
- Cleanup after merge: `scripts/reasonix-clean.ps1 docs-contract-reconciliation`; retire `fix/adr-id-collision` (branch + worktree) as superseded.

## 7. Risks / open questions

- **Fixture metric mismatch (§4.5)** — needs human selection before execution of fix 5.
- **`docs/handoffs/2026-05-21-...:17` "ADR-013"** — ambiguous reference; resolved during implementation by reading context (conservative: leave if not clearly universe-to-series).
- **Runner threading** — `_get_runtime` is a module-level singleton with no project context; the fix may require passing project path from the pipeline entry. If plumbing is invasive, the <cwd> default + regression test is the fallback (still closes the root-sprawl defect).
- **Root cleanup is on main's disk** (ignored files) — executed as housekeeping after merge/approval, never in the branch commit.
- **`013-series-graph-semantics.md` keeps `013`** — no renumber of the other file; double-check no accidental swap during `git mv`.
