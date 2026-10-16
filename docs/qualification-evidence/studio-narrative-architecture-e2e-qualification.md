# Studio Narrative Architecture — End-to-End Qualification Evidence (2026-10-15)

This record covers the qualification run defined in
`docs/superpowers/plans/2026-10-15-studio-narrative-architecture-e2e-qualification.md`.
It reports four claims independently. No label implies a higher level than was observed.

## Decision matrix

| Claim | Outcome | Basis |
|---|---|---|
| 1. Automated engineering regression | **PASS for the Studio slice; repo-wide suite has 16 inherited failures** | Node 51/51, focused Python 48/48, Stage B 23/23 on three consecutive post-fix runs, full suite 5615 passed / 16 failed / 2 skipped (all 16 fail identically on `origin/main`). |
| 2. Manual coding-agent E2E (paladin vision → real agent → graph) | **BLOCKED — coding-agent capability unavailable** | No locally installed agent could produce a model response from this session (see Agent probes). The runner's Browser stage ran and stopped at the agent boundary. |
| 3. Automatic connected-host E2E (Browser → trusted executor) | **BLOCKED — no attached executor exists** | No host executor is implemented or attached. Not implemented as a fake. |
| 4. Human usability comprehension | **NOT TESTED** | No human participant walkthrough was performed. |

Overall: **not qualified** for the bounded manual author-architecture E2E. The
product-readiness hold stands.

## Exact source identity

| Ref | SHA |
|---|---|
| `origin/main` (baseline used for classification) | `bb9c102d6cc4e9473ca7cffc5253ed72361ef37a` |
| Local `main` (310 commits behind `origin/main`; not used) | `3836c26d` |
| PR #440 `docs/2026-10-15-creative-collaboration-plan` | `a6a23d0e3747e84f0731e1473d6128030e70fb6f` |
| PR #441 `feat/studio-creative-collaboration-20261015` | `e804d278bf110a54d2c91570abf8c89a58d9c317` |
| PR #442 `feat/studio-creative-explanations-20261015` | `a54967691aa7aba2b3754d918edc4703a32ff651` |
| PR #443 `test/studio-real-agent-e2e-20261015` (stack head) | `573e8c76b4c7be455fcd2dde63ef9f2bd30b1c18` |
| Qualification head (#443 + harness fix) | `a2b86d77a788889f8efd35c16bb42161bd4a78d9` |

Ancestry verified: #441 ⊂ #442 ⊂ #443. #440 is documentation only. All PRs were draft
with `mergeStateStatus: CLEAN` at inspection time. No status checks were reported by
GitHub (`statusCheckRollup: []`); absence of statuses is not evidence of green CI.

Isolated worktree: `auteur-qualification` at `a2b86d77`, clean at each evidence run.
`import auteur` resolved to that worktree's `src/`.

## Environment

- Windows 10 Home 10.0.19045; PowerShell + Git Bash.
- Python 3.14.3 in a disposable venv (`pip install -e ".[dev]"`); Playwright (Python) driving the
  installed **Google Chrome 154.0.8037.98**.
- Node v24.14.1.
- No `CHROMIUM_PATH` was preset; Stage B and the runner used Chrome via explicit path.

## Automated engineering regression

| Suite | Command | Result |
|---|---|---|
| Node Studio units | `node --test tests/test_studio_author_intent.mjs tests/test_studio_agent_handoff.mjs tests/test_studio_unfolding_controller.mjs tests/test_studio_explanations_unit.mjs tests/test_studio_explanation_views.mjs` | 51 pass, 0 fail |
| Python Studio contracts + E2E driver | `pytest tests/test_studio_architecture_e2e_driver.py tests/test_beginner_studio_architecture.py tests/test_studio_mentor_agent.py tests/test_beginner_studio_mentor_http.py tests/test_beginner_studio_explanation_navigation.py` | 48 pass, 0 fail |
| Served Chromium Stage B | `python scripts/studio_stage_b_check.py <fresh dir>` | 23/23 PASS on three consecutive runs after the harness fix (see Repairs) |
| Full repository suite (serial, final) | `pytest -p no:cacheprovider --tb=no -rfE -q` on `a2b86d77` | **5615 passed, 16 failed, 2 skipped** of 5633 collected |

Note: the project `addopts` already sets `-q`, so passing `-q` again suppresses pytest's
summary line. Totals above come from the progress characters and the collection count (5633).

### Full-suite failures classified against baseline

The 16 failures reproduce on `origin/main` (`bb9c102d`) with the identical set of IDs
(verified by diff). They are **inherited, not introduced by the Studio stack**. They concern CLI formatters,
dashboard, series, book comparison, story discovery, and state reporting.
One further test, `tests/test_f2_context_prompt.py::test_f2_prompt_consumer_probe_preserves_context_authority`,
failed in the parallel (`-n 4`) run and on baseline, but passed in the serial run. Treat it as an
order- or timing-dependent inherited flake.

The full suite also rewrites the tracked file `examples/identity/validation_report.json` and creates
`.auteur/` and `temp/` in the checkout. This is a test-hygiene defect: tests should not dirty tracked
files. It is not repaired here (out of scope); restored and removed after each run.

## Repairs made during qualification

**`scripts/studio_stage_b_check.py`** (commit `a2b86d77`, branch
`fix/studio-stage-b-harness-timing-20261015`):

1. *Port reuse race.* After `terminate()`+`wait()`, Windows kept the port listening for about one second.
   The immediate restart raised `port 65214 is already in use`. Reproduced deterministically (isolated
   probe: listener present ~1s after exit). Fix: wait for the port to be released (bounded, 10 s) before restart.
2. *Title assertion.* `"Second canvas note" in t3` tested list membership, but Browser `innerText` renders
   `Second canvas notenote · Working`. Fix: substring match. The same pattern at the autosave check was
   tightened identically.

RED evidence: run with the original harness raised the port error (run A) and reported `FAIL root reopens
the most recently edited canvas` (run B). GREEN: three consecutive runs, 23 PASS / 0 FAIL each.

**Unexplained intermittent:** one post-start run timed out waiting 5 s for `#architecture-copy-request`
to become visible after clicking develop. A 4-trial probe of the identical steps passed 4/4 with status
"Request prepared, but no coding agent is connected". Not root-caused; recorded as intermittent, not fixed.

## Manual coding-agent E2E — BLOCKED

### Runner behavior verified

`scripts/studio_architecture_e2e.py --report <receipt> --chromium <Chrome> --agent <missing exe>`
against the clean head `a2b86d77` (receipt `docs/qualification-evidence/2026-10-15-studio-narrative-architecture-e2e-blocked.json`):

- Started the real Auteur server (`--studio-development-default`) and launched Chrome.
- Saved the exact Story Vision and prepared a `studio_architecture` request:
  `architecture_request_sha256 = f9c95f613f053fea664a84b7feaa34a1fdc8f59d300bd3ced0b724ceb6ebfe43`.
- Stopped with `BLOCKED: coding-agent executable not available`, exit code 2.
- Earlier (before commit), the runner refused a dirty checkout with `BLOCKED: dirty checkout ...`,
  confirming the exact-head guard works.

**Limitation:** `canonical_file_hashes` is empty because the disposable project had no accepted story
files. "canonical_unchanged: true" is therefore vacuous. Canonical protection was not proven here.

### Agent probes (no model call succeeded)

| Runtime | Finding | Action the author must take |
|---|---|---|
| Claude Code 2.1.266 (`claude`) | `auth status`: `loggedIn: false`; `-p` returned `Failed to authenticate: OAuth session expired` | `claude login` (author action) |
| Codex 0.153.4 (`codex`) | Logged in with ChatGPT. Configured default model `gpt-6-luna` rejected ("not supported when using Codex with a ChatGPT account"); `gpt-5` and `gpt-5-codex` also rejected | Set a model supported for this account in Codex config |
| Gemini CLI | `IneligibleTierError`: client no longer supported for this account tier | Account migration (author action) |
| OpenCode | Default provider LM Studio `qwen3-coder-30b` unreachable; `github-copilot/claude-sonnet-5.5` returned HTTP 402 `quota_exceeded` (retry after 2026-11-01) | Start LM Studio, or wait for quota reset |

No `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` was present in the environment. No synthetic, self-authored,
or canned candidate was substituted; the manual lane has no admissible proof.

**Consequently the paladin Story Vision → real agent candidate → graph → mentor alternatives →
keep → reopen journey was NOT executed.** Steps 6–13 of the mission (graph inspection, mentor
divergence, reopen, canonical diff under a real project) are unverified.

## Automatic connected-host E2E — BLOCKED

No Browser-to-trusted-executor connection exists in the product, and the runner reports
`connected_host_e2e: BLOCKED: no attached executor proven`. The manual lane does not establish it.

## Human usability — NOT TESTED

No participant walkthrough was performed. No UX validation is claimed.

## Items not performed

- Adversarial probes requiring a live agent (malformed/late/wrong-SHA response through a real agent).
  Unit-level coverage exists in `tests/test_studio_architecture_e2e_driver.py` and the Python Studio tests.
- Mutation-sensitivity checks on the runner.
- Second premise / genre-general run.
- Narrow-screen (390px) and keyboard checks of the agent-produced graph (requires the live journey).
- Protected integration of PRs #440–#443 (not performed; see next steps).

## Next actionable steps (author-owned)

1. Restore one authorized coding-agent runtime (re-login Claude Code, or set a supported Codex model),
   then re-run:
   `python scripts/studio_architecture_e2e.py --report <path>.json --chromium "<Chrome>" --agent <adapter> <args>`
   on a clean checkout of `a2b86d77` or its descendant.
2. Use a project with an accepted story file so the canonical hash check is meaningful.
3. Decide whether the stage-B-fix and this record should be integrated before the #441 → #443 stack.

## Superseding observed qualification — 2026-10-16

The historical BLOCKED run above is preserved. The following observations supersede
its capability findings, without converting earlier failures into successful runs.

### Frozen source and independent outcomes

- Product commit: `06fa522b5174ea8c3ffa6366a780299e353f9899`.
- Integrated tree: `835ce7cdf4e3163baec9e8de0db720e2836980c9`.
- Fresh remote main: `bb9c102d6cc4e9473ca7cffc5253ed72361ef37a`.
- Stack: #441 → #442 → #443 → existing #444 → #445 → #446 → #447.
  #440 remains the independent approved specification/runbook. This evidence-only
  publication commit is distinct from the tested product commit.
- Each live run began with a clean tree. Imports/server assets resolved from
  `H:/codex/qualification/auteur-narrative-20261016/host-attachment/src`.
- Windows 10 19045, Python 3.12.8, Node 24.14.1, pytest 8.4.2,
  Playwright 1.64.0, Chromium 156.0.8078.4, Pydantic 2.14.1.

| Claim | Observed outcome |
|---|---|
| Automated engineering regression | Final selected Python **67 passed**, Node **54 passed**, unmodified served Stage B **23/23 passed**. Full checkpoint has baseline failures, below. |
| Complete manual coding-agent E2E | **PASS, paladin-only bounded journey, 21/21 steps** at the product commit. |
| Automatic connected-host E2E | **PASS for architecture**, with an explicitly attached real CLI worker. Default server remains unconnected; mentor fulfillment remains manual. |
| Human usability comprehension | **NOT TESTED**. No human walkthrough, general author-readiness or genre-general claim. |

Machine receipts: [manual journey](2026-10-16-studio-manual-e2e.json),
[connected architecture](2026-10-16-studio-connected-e2e.json), and
[adversarial/canary replay](2026-10-16-studio-adversarial.json).

### Actual agents and author-visible behavior

The manual runner wrote each exact request to an operator handoff directory; actual
Codex agent `/root/live_architecture_agent` read it, generated original creative
material, schema-validated it, and atomically wrote the response. The handoff script
only transported files and waited; it generated nothing. That agent's exact model
identifier was unavailable. Its self-report alone is not the proof: the observed
agent dispatches, source-bound files, Auteur validation and Browser steps agree.

The complete journey saved the owner's verbatim generous-paladin premise, displayed
14 nodes and 17 declared links, separated author wording from AI hypotheses,
inspected Genre/Trope/Structure relationships, compared real mentor mechanisms and
tradeoffs, deliberately kept one working idea, and reopened the same proposal,
vision and idea. No required moral flaw was imposed on generosity. Missing verified
genre coverage remained uncertainty. Chromium recorded zero page errors and no
horizontal overflow at 390px. This proves execution, not literary merit.

Manual architecture request: `2c6893ee0569fba652e4149d27ec72e453914887bff4ac8485752493cc3a6cb9`.
Manual mentor request: `8d1e5ea99bdf253d329a42d42114836248b1ec29f93845ccf1b5b2f4ae29f040`.
Their canonical JSON payload fingerprints are in the manual receipt; byte-level
file hashes are separately retained locally and are not interchangeable.

The connected Browser submitted its exact request to an operator-registered,
single-worker executor. That worker actually invoked authenticated **Codex CLI
0.153.4**, requesting **gpt-6-astra**, then used the existing completion validator.
CLI events include a completed model turn and token usage. No manual packet or
response transfer occurred. Underlying provider model revision is unavailable.
Request: `fee354c504a6d0beb34eecfc0c96c1a3969870102cd5d3ebf971c77c0bd6f1b9`.
Source fingerprint: `b29640432cf7399a6284ef89d6f0007a345282188784526400e5cd7ab6624a97`.

### Repairs, falsification and limits

- #445: explicit UTF-8 transport; minimal operator-only CLI adapter with private
  invocation evidence; exact original premise. ANSI-locale Unicode failure was RED.
- #446: read collapsed mentor packet through textContent; reopen saved vision with
  its author control; terminate timed-out launcher descendants at both boundaries.
  All three failures were reproduced before correction. Timeout metadata survives.
- #447: opt-in typed host attachment, source/fingerprint checks, submission ownership
  against duplicate calls, same-origin/loopback/JSON execution guard, truthful
  re-entry capability and completed-result handling. Independent review found the
  duplicate/foreign-origin/ready-state defects; behavioral regressions were RED/GREEN.
- A real connected CLI candidate was rejected for prose in genre_contract.role.
  The request omitted that enum. Its accepted values are now explicit, with a
  failing-then-passing schema/prompt contract test; the validator was not weakened.
- Final adversarial replay refused wrong IDs/fingerprints, malformed/incomplete
  candidates, cross-canvas replies, and a late reply after an author edit. Pending
  requests survived re-entry without phantom generation. Keyboard inspection worked.
- Three nonempty accepted-path canaries (existing valid identity fixture, manuscript
  bytes and relations file) retained identical SHA-256 values. These are disposable
  test canaries, not an actual author's accepted book. Empty-project live hash
  checks are reported separately and remain vacuous for pre-existing accepted files.
- Earlier CLI failure, partial manual failures, invalid connected response and
  intermittent Stage B failures remain in the local attempt logs. Final unmodified
  Stage B and an instrumented diagnostic both passed 23/23; intermittent missing
  scripts/controls under concurrent runs were not root-caused. No stability guarantee.

### Reproduction and regression accounting

Local evidence root: `H:/codex/qualification/auteur-narrative-20261016/`.
It retains exact commands/logs, request/response bytes, CLI events, invocation argv,
traces, screenshots, JUnit XML, failed attempts and orchestration scripts. Private
CLI stderr is not published. The connected composition is `connected_check.py`;
manual transport is `manual_handoff.py`. Both run outside the product checkout.

At the clean product commit, use the external venv's `Scripts/python.exe` with
`PYTHONPATH=<checkout>/src`. Commands actually exercised:

```text
python -m pytest -o addopts="--tb=short -W ignore::UserWarning" -q tests/test_beginner_studio_host_dispatch.py tests/test_beginner_studio_architecture.py tests/test_studio_mentor_agent.py tests/test_beginner_studio_mentor_http.py tests/test_beginner_studio_explanation_navigation.py tests/test_studio_architecture_e2e_driver.py tests/test_studio_live_agent_adapter.py
node --test tests/test_studio_author_intent.mjs tests/test_studio_agent_handoff.mjs tests/test_studio_unfolding_controller.mjs tests/test_studio_explanations_unit.mjs tests/test_studio_explanation_views.mjs
python scripts/studio_stage_b_check.py
python scripts/studio_architecture_e2e.py --report <external>/native-live-final.json --agent-timeout 660 --agent <external-venv-python> <external>/manual_handoff.py
python <external>/connected_check.py
python <external>/manual_adversarial_final.py
```

Stage B used `AUTEUR_PYTHON=H:/Python/Python312/python.exe` and PYTHONPATH containing
the exact source plus external venv site-packages. This avoids the observed Windows
venv-launcher restart issue. Existing #444 supplies its bounded port-release wait.

The explicit L3 checkpoint at `62e1df9f7331bab4f5b332b0c9ab852144f838f2`
(before subsequent bounded repairs) ran `python -m pytest -n 4 -o addopts="--tb=short
-W ignore::UserWarning" -q`: **5,641 collected = 5,622 passed + 17 failed + 2 skipped;
0 xfailed, 0 xpassed, 0 errors**, exit 1. All 17 failing IDs reproduced on the pinned
main baseline. Failure shapes match; differing text contains temporary paths,
timestamps or generated IDs. This is a known baseline failure set, not green L3,
and is not a full-suite result for the later product commit. Later repairs received
the named L1/L2 and actual journey checks above; no release candidate was selected.

### Protected integration handoff

All #440–#447 structural guards passed against their declared dependency bases:
no protected/secret/binary paths and each PR below 500 changed lines/12 files.
No PR was merged. Fresh main and PR heads were re-read; GitHub reports no checks,
which is not a CI pass. Integrated evidence does not independently qualify every
historical standalone PR head. Integrate the dependency chain in order and recheck
contemporary main before each protected transition.

The configured factory agent is Claude and `claude auth status` reports logged out;
the protected factory autonomy default remains 0. Independent factory validation,
mutation-sensitivity gate and code-controlled integration have not run. They were
not replaced by direct GitHub merging or a manufactured passing verdict. Operator
restoration/authorization of that protected process is required. #360 tracks broader
Browser qualification and #369 the separate human-value study. Human participation,
protected integration and release remain unclaimed.
