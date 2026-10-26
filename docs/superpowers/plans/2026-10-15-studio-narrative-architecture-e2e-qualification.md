# Studio Narrative Architecture End-to-End Qualification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the complete, author-visible Narrative Architecture journey on a clean, exact integrated Auteur tree using a genuine coding agent and a real served Chromium Browser; repair demonstrated defects, then hand eligible PRs to protected integration.

**Architecture:** Verify the pre-existing source-bound CanvasStore / HostAgentRequest / ArchitectureCandidate / MentorAdvice workflow; never create a second story owner. Use the existing Stage B browser checks for mechanical regression and PR #443's operator-initiated `scripts/studio_architecture_e2e.py` for an authentic manual-agent run. A Browser-to-host automatic executor and human comprehension are independent qualification lanes, not silent substitutes.

**Tech Stack:** Python >=3.11, pytest, Pydantic v2, Node test runner, Playwright/Chromium, git worktrees, actual locally authenticated coding-agent CLI (if available), existing Auteur local HTTP server.

**Spec:** `docs/superpowers/specs/2026-10-15-studio-creative-collaboration.md` (especially section 7); also `docs/superpowers/plans/2026-10-15-studio-creative-collaboration.md` Task 6.

## Global Constraints

- **Current inspected refs (2026-10-15):** main `bb9c102d6cc4e9473ca7cffc5253ed72361ef37a`; #441 `e804d278bf110a54d2c91570abf8c89a58d9c317`; #442 `a54967691aa7aba2b3754d918edc4703a32ff651`; combined #443 `573e8c76b4c7be455fcd2dde63ef9f2bd30b1c18`. Re-fetch immediately before acting; fail closed on changed heads, never silently use old evidence.
- **PR layout:** #440 documentation is independent on main; code PRs are stacked #441 -> #442 -> #443. No merging only to run tests; the #443 tree already contains the preceding code changes.
- **Protected policy:** `FACTORY_RULES.md` forbids weakening tests, canned LLM responses as proof, touching protected files, PRs above 500 changed lines/12 files, and model-controlled protected merge. Two failed repair attempts require escalation. A technical GitHub mergeable flag is not integration authorization.
- Keep all test projects disposable and empty at entry. Never run acceptance on an author's real Book; never generate, accept, publish, or rewrite canonical narrative.
- Do not assume GitHub Actions, connected provider credentials, installed Chromium or a callable coding agent. A missing capability is **BLOCKED**, not green. Do not install/switch providers, transmit new content classes externally, or change credentials without the required existing authorization.
- **Four separate claims:** component regression; **manual coding-agent E2E**; genuine **connected/automatic host E2E**; observed **human UX comprehension**. Report each independently.
- Preserve source identity, real request/response fingerprints, actual runtime/model labels or `UNAVAILABLE`, failure attempts, and canonical/story SHA-256. No screenshots or self-reported agent statements substitute for executed proof.
- Changes must remain in independently reviewable PRs; fix the smallest observed defect only. Do not update this plan's own protected rules to clear a gate.

## Review Focus — five risky inputs

1. An agent executable prints valid canned JSON without ever invoking a model. **Task 3 test:** the receipt must retain independent real-agent invocation evidence and never infer model authenticity from valid JSON alone.
2. Windows terminal uses a non-UTF-8 subprocess code page. **Task 3 test:** a Unicode paladin/genre payload must round-trip to the actual adapter without replacement characters or hidden truncation.
3. A late response belongs to an old canvas, request, or author revision. **Task 5 test:** malformed/wrong-source/stale completion must be refused without replacing the current proposal or accepted canon.
4. A worked idea makes the original architecture projection stale after explicit Keep. **Task 4/5 tests:** existing proposal and kept working item remain identifiable after reload even when freshness is `stale`; do not fabricate a new accepted state.
5. The graph displays nodes but genre/trope/structure explanations lack real links or reliable provenance. **Task 4 test:** inspect a declared relation and source coverage, and verify author prose is visibly distinct from optional AI interpretations.

---

### Task 1: Freeze a clean executable stack and establish honest baselines

**Files:** Read `pyproject.toml`, `FACTORY_RULES.md`, `scripts/studio_stage_b_check.py`, and PRs #440-443; no production edits. Evidence goes in an external scratch log; do not commit empty PASS receipts.

**Interfaces:** Produces `PINNED_CODE_SHA`, clean checkout path, Python/Node/Chromium versions, available runtime/agent capability, and exact baseline failures; consumed by Tasks 2-8.

- [ ] **Fetch/pin:** On the coding-agent's local machine, create an isolated worktree at the **freshly verified** head of PR #443 (which includes #441/#442). If current head differs from the pin above, inspect the PR diff and update the pin; never mix evidence between two commits. Use `superpowers:using-git-worktrees`; verify ignored worktree location first.
- [ ] **Read-only commands:** `git rev-parse HEAD`, `git status --porcelain`, `python --version`, `node --version`, `python -m pip show auteur pytest playwright` and `git diff --name-only main...HEAD`. Expected: exact pinned commit, clean index, supported Python >=3.11, no protected-file mutations.
- [ ] **Environment:** Install project dev deps in a disposable virtual environment using `python -m pip install -e ".[dev]"`, and Playwright/Chromium only if needed and permitted; use `python -m playwright install chromium` or the existing `CHROMIUM_PATH`. Never alter protected `pyproject.toml`/lock files to pass qualification.
- [ ] **Source guard:** Show that `import auteur` and the launched server resolve into this exact checkout, not a global installed version. Use `python -c "import auteur; print(auteur.__file__)"` plus `git rev-parse HEAD`. Expected: package path belongs to the worktree.
- [ ] **Baseline check:** Run `python -m pytest -q tests/test_studio_architecture_e2e_driver.py`. Expected on unchanged #443 as previously observed: 9 tests, 0 failures. If not, record actual failures and investigate before assuming implementation correctness.
- [ ] **Record:** Create a non-committed evidence working log with commands, exit codes, exact SHAs, OS, dependency versions, test attempts, and any unavailable capability. A dirty tree or an inaccessible dependency blocks exact-SHA proof.

### Task 2: Qualify existing author-intent, mentor, request and graph contracts

**Files:** Test `tests/test_studio_author_intent.mjs`, `tests/test_studio_agent_handoff.mjs`, `tests/test_studio_unfolding_controller.mjs`, `tests/test_studio_explanations_unit.mjs`, `tests/test_studio_explanation_views.mjs`, `tests/test_beginner_studio_architecture.py`, `tests/test_studio_mentor_agent.py`, `tests/test_beginner_studio_mentor_http.py` and `tests/test_beginner_studio_explanation_navigation.py`. No feature changes unless a test demonstrates a specific defect.

**Interfaces:** Consumes `PINNED_CODE_SHA`. Produces a per-suite result ledger: passed/failed counts, known baseline failures, and a repair list.

- [ ] **Node regressions:** Run `node --test tests/test_studio_author_intent.mjs tests/test_studio_agent_handoff.mjs tests/test_studio_unfolding_controller.mjs tests/test_studio_explanations_unit.mjs tests/test_studio_explanation_views.mjs`. Expected: zero candidate-only failures; report exact count.
- [ ] **Python regressions:** Run `python -m pytest -q tests/test_beginner_studio_architecture.py tests/test_studio_mentor_agent.py tests/test_beginner_studio_mentor_http.py tests/test_beginner_studio_explanation_navigation.py tests/test_studio_architecture_e2e_driver.py`. Expected: zero candidate-only failures, including refusal of stale/wrong-SHA requests.
- [ ] **Served Browser baseline:** Run `python scripts/studio_stage_b_check.py` against a fresh disposable project. Expected: actual server start, real Chromium, each explicit check PASS, zero page errors, and no canonical/story mutation; record failures rather than trusting a final green count.
- [ ] **Broader regression:** Run `python -m pytest -q` once on the exact tree. If baseline failures are reported, reproduce each relevant assertion on the pinned main baseline before classifying it as pre-existing. Do not weaken tests or claim broad-suite green.
- [ ] **Decision:** Repair demonstrated candidate defects with Task 6; otherwise preserve the exact tree and proceed to real-agent qualification. A failed suite does not silently disappear from the integration ledger.

### Task 3: Admit and prove an actual coding-agent command

**Files:** Existing `src/auteur/host_agent.py`, `src/auteur/beginner/studio_architecture.py`, `src/auteur/beginner/studio_mentor.py`, `scripts/studio_architecture_e2e.py`. Only if genuinely required, add a minimal adapter `scripts/studio_live_agent_adapter.py` and its test `tests/test_studio_live_agent_adapter.py` in a **separate narrow PR**.

**Interfaces:** The runner's `run_agent(argv: list[str], request: dict, timeout: int) -> dict` writes one exact `HostAgentRequest` on stdin and expects a single raw JSON object on stdout; roles are `studio_architecture` (schema v2 `ArchitectureCandidate`) and `studio_mentor` (schema v1 `MentorAdvice`). It never invokes a Browser-side provider.

- [ ] **Discover only:** Check locally installed coding-agent executables and their official help/credentials status. Select one already authorized, accessible runtime; do not guess CLI flags, log in on the author's behalf, or use an unapproved cloud provider.
- [ ] **TDD adapter if needed:** Write `test_live_agent_adapter_preserves_unicode_and_role`: feed an exact JSON packet with non-ASCII author text, verify one valid JSON object on stdout with no surrounding logs, and reject missing/ambiguous role, timeouts, and non-JSON output. Observe RED before implementing only the needed CLI wrapper; run GREEN and relevant suite. Unit synthetic envelopes test the transport, **not** the creative-generation claim.
- [ ] **Real invocation:** Issue one disposable live packet to the selected agent, confirm a genuine recorded model/session call and valid schema output, then exercise the second role. Preserve request SHA, payload fingerprint, elapsed time and actual runtime/model identity if observable. A wrapper that merely echoes fixtures is inadmissible.
- [ ] **Security:** Do not print provider tokens, private CLI stderr, raw secrets, or internal prompts to public PR evidence. Prefer UTF-8 stdout/stderr behavior on Windows and fail on invalid output rather than silently replacing characters.
- [ ] **Admission outcome:** If no real agent can be called, write `BLOCKED — coding-agent capability unavailable`, retain Task 2 results, and do **not** represent the manual architecture E2E as executed.

### Task 4: Execute authentic paladin Story Vision -> agent -> spatial graph

**Files:** Run `scripts/studio_architecture_e2e.py` at the clean code SHA; if it fails, repair the responsible source/test through Task 6. Save the run receipt outside the checkout, then reconcile into `docs/qualification-evidence/studio-narrative-architecture-e2e-qualification.md` only after actual evidence exists.

**Interfaces:** Consumes Tasks 1-3. Produces manual-E2E `PASS`, `FAIL` or `BLOCKED`, with linked source/request/payload SHA identifiers and browser observations.

- [ ] **Execute:** From the pinned clean worktree, run `python scripts/studio_architecture_e2e.py --report <EXTERNAL_RECEIPT_PATH>.json --agent <REAL_AGENT_EXECUTABLE> <VERIFIED_ARGS>`. `--agent` must be last: it consumes the remaining arguments. Supply `--chromium <PATH>` **before** `--agent` when using an installed Browser.
- [ ] **Check receipt:** The runner must open the actual local server/Chromium; save the exact generous-paladin vision; prepare a `studio_architecture` request; receive a real agent candidate; validate it with Auteur's existing API; and display a nonempty graph. A success-shaped HTTP payload alone is insufficient.
- [ ] **Author meaning:** Inspect a declared link and its verb, the emotion/genre/trope/structure relationships, differences between exact authored Story Vision and AI-proposed character flaws, Genre Pack coverage uncertainty, and return to graph. No silent acceptance.
- [ ] **Divergent mentoring:** Select a current proposal, request real `studio_mentor` alternatives, compare at least two genuinely different mechanisms and tradeoffs, explicitly Keep one **working** idea, and verify canvas persistence.
- [ ] **Re-entry and safety:** Reopen Browser at the same canvas, verify proposal and kept working idea (including legitimate stale state), check 390px and keyboard path, page errors, and before/after canonical/story hashes.
- [ ] **Result rule:** `PASS - bounded manual E2E` requires exit code 0 **and** independent proof the external agent actually executed. Agent unavailable -> `BLOCKED`; validation/browser failure -> `FAIL`. This does **not** prove Browser one-click connected execution, genre generality, or human understanding.

### Task 5: Exercise falsification and a second narrative premise

**Files:** Extend `tests/test_studio_architecture_e2e_driver.py`, `tests/test_beginner_studio_architecture.py` or the existing Stage B test **only for demonstrated gaps**. Preserve existing tests; no canned model response can stand in for a live-agent E2E.

**Interfaces:** Consumes the Task 4 candidate/request SHAs and canon hash snapshot. Produces adversarial evidence and an explicitly limited generality claim.

- [ ] **RED failure probes:** Missing agent must exit 2/`BLOCKED`; malformed agent response must exit nonzero/`FAIL`; wrong SHA and changed author revision must be rejected with unchanged accepted files. Re-run candidate request through another canvas to prove context isolation. Observe test failure on the uncorrected behavior before any repair.
- [ ] **Recovery:** Interrupt a pending request, reload Browser, and verify status remains actionable; a late old response cannot silently replace a new vision/candidate. Compare actual state from both the Browser and the persistent API.
- [ ] **Adversarial originality:** Without a verified Progression/Heroic Fantasy pack, Genre/Trope views must say evidence is unavailable rather than inventing an originality or genre-rule verdict.
- [ ] **Second premise:** If claiming genre-general functionality, run a materially different genuine agent case (for example a nonheroic mystery) on a fresh disposable project with a separately tracked receipt. Otherwise retain the paladin-only bounded claim and do not expand the current scope merely for optics.
- [ ] **Review:** Record whether each negative probe demonstrably failed when corrupted and passed when correct (mutation-sensitivity evidence), not merely the final PASS count.

### Task 6: Repair observed defects without reopening product scope

**Files:** Only failing owners from Tasks 2, 4 or 5, e.g. `studio_agent_handoff.js`, `studio.js`, `studio_architecture_e2e.py` and their matching Node/Python tests; choose paths from evidence, not speculation.

**Interfaces:** Consumes concrete failing step, exact SHA, Browser trace/test assertion. Produces a narrow repair PR and new pinned head if required.

- [ ] **Diagnose:** Reproduce the same failure on the pinned candidate and compare the same assertion against base main where feasible. Identify product defect vs test harness timing vs missing external capability.
- [ ] **RED -> GREEN:** Write a failing behavioral regression for the actual defect, run it and confirm expected RED, implement smallest correction, rerun focused tests and required broader regression suites. Do not weaken or skip failed assertions.
- [ ] **PR discipline:** Keep each fix under 500 changed lines/12 files, protect all `FACTORY_RULES` paths, allow at most 2 fix attempts under repository policy, and leave historical failed receipts intact. Update exact heads and rerun Task 4 for any change touching the tested journey.
- [ ] **Stop condition:** If blocked by credentials, external agent access, security-sensitive data egress, protected integration, or repeated failed repair, record the external/owner gate and stop that branch, not all independent work.

### Task 7: Independently observe actual author comprehension

**Files:** Human observation protocol and only actual evidence in `docs/qualification-evidence/studio-narrative-architecture-e2e-qualification.md`; no software edits unless an observed defect justifies Task 6.

**Interfaces:** Consumes a qualified disposable Book/Studio and a real participant. Produces `HUMAN UX OBSERVED` with findings, or `NOT TESTED` if no participant is available.

- [ ] **15-minute protocol:** Without coaching, have the participant identify authored vs agent-invented paladin assumptions; locate a narrative node and explain a declared link; compare alternative arcs; explain genre/trope evidence gaps; return to the original graph; and reopen to identify current creative state.
- [ ] **Observe rather than prompt answers:** Capture actual task completion, hesitation, mistaken acceptance beliefs, unexpected clicks and need for assistance. Check keyboard navigation and 390px layout on relevant tasks.
- [ ] **Integrity:** Do not have the participant accept canon or generate chapters. Record a real observation timestamp and anonymized notes; never fabricate human testing or treat simulated Browser clicks as UX validation.
- [ ] **Verdict:** Human assessment is separate from the engineering/manual E2E gate. Without a participant, state `NOT TESTED` and maintain the product-readiness hold.

### Task 8: Publish evidence and hand off protected integration

**Files:** Create/update `docs/qualification-evidence/studio-narrative-architecture-e2e-qualification.md` in a small dedicated evidence PR after an actual run; update PR #440, #441, #442 and #443 descriptions with true pinned evidence only.

**Interfaces:** Consumes all run receipts and Task 1's baseline ledger. Produces an independently reviewable evidence package plus an authorized protected-integration handoff.

- [ ] **Evidence receipt:** Record test commands, actual exit codes/counts, base/PR/integrated SHAs, project path identifier, Browser trace/screenshots/console errors where available, source SHA, request and candidate/mentor output hashes, agent runtime/model proof or `UNAVAILABLE`, canonical hash diff, failures/retries and their dispositions. Redact any secret/provider data.
- [ ] **Decision matrix:** Write distinct outcomes for component regression, manual agent E2E, connected-host E2E, and human UX (`PASS`, `FAIL`, `BLOCKED` / `NOT TESTED`). No label should imply higher qualification than observed.
- [ ] **Review/gates:** Check independent review of the exact tree, factory `APP_STARTED` and `E2E_PASSED` markers/counts where applicable, validator evidence and mutation sensitivity, no protected/secret files, size caps, and latest mergeability/status checks. Absence of GitHub statuses is **not** proof of green CI.
- [ ] **Integration:** Prepare PR #440 (documents) and sequential #441 -> #442 -> #443 for the repository's **protected code-controlled** merge transition only if its conditions hold. Do not call GitHub's direct merge as a substitute, rewrite evidence, or promote to production.
- [ ] **Close or stop:** Declare `QUALIFIED: bounded manual author-architecture E2E` only with genuine step evidence and eligible protection gates. If automatic host remains unattached, explicitly defer it to a separate product/engineering plan; broad release requires an independent authorization and usability decision.

## Execution Order and Owner Rulings

**Owner-selected priority:** Finish already-open implementation and proof; do not create new exploratory UX scope. Tasks 1-3 are sequential admission. Tasks 4-5 exercise and challenge the real product; Task 6 is conditional repair invoked only from a reproduced failure. Task 7 requires a genuine human and may remain unqualified; Task 8 reconciles the actual evidence and controlled integration. No repeated permissions questions for routine local tests, but respect `FACTORY_RULES.md` `5 authorization boundaries.

**Definition of done:** A reviewer can reproduce the same complete manually mediated Browser-to-agent-to-graph journey from the exact tested tree, match the observed receipts and request identities, see no silent canon changes, and distinguish everything still blocked. If no real agent is available, the correct terminal result is a defensible **BLOCKED**, not a fictitious release or a claim that every task is finished.

**Standalone connected host:** A true one-click Browser -> trusted executor feature is a separate contingent program. Admit it only when an actual callable host is available; require its own spec, threat boundary, tests and real connected E2E. It must not delay a truthful bounded manual workflow.
