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
