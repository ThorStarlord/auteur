# Studio Narrative Architecture qualification at f2275a23

Candidate: `f2275a2391d3d579db3c2740717e262b80758563` (tree `89bf11a86b705eb203feff6229b468794072dff1`).
Product change over the prior frozen candidate `06fa522b5174ea8c3ffa6366a780299e353f9899`: one line in `studio_unfolding_controller.js` and one regression test, so the start panel no longer covers a populated proposal graph. Product PR: #449 (draft, stacked on #447).

This document is new evidence for `f2275a23`. The receipts for `06fa522b` stay as recorded and are not reused for this candidate.

## Results

| Check | Result at `f2275a23` | Receipt or log |
|---|---|---|
| Node focused suites | 55 / 55 pass (new regression RED then GREEN) | local run, `tests/test_studio_unfolding_controller.mjs` and four sibling suites |
| Python selected suites | 67 passed | local run, host dispatch, architecture, mentor, explanation navigation, E2E driver, live adapter |
| Served Stage B journey | 23 / 23 pass | local log `stage-b-onboarding.log` |
| Manual coding-agent E2E | PASS, 21 / 21 | `2026-10-16-f2275a23-studio-manual-e2e.json` |
| Connected Browser → attached CLI | NOT RUN: external blocker (below) | `2026-10-16-f2275a23-studio-connected-blocker.json` |
| Browser screenshot, populated graph, no selection | start panel hidden, 13 nodes visible, no page errors | `2026-10-16-f2275a23-studio-screenshots/f2275a23-populated-graph-no-selection.png` |
| Before/after on the same probe | at `06fa522b` the start panel covers the graph; at `f2275a23` it does not | `…/06fa522b-populated-graph-no-selection.png` |
| First-session empty project | onboarding panel visible ("What should your reader experience?"), no page errors | `…/f2275a23-first-session-empty.png` |
| Broader regression (L3) | not rerun for this candidate; see Scope | earlier checkpoint at `62e1df9f` |

## Manual coding-agent E2E at f2275a23 (21/21)

Steps passed: exact Story Vision request prepared by the Browser; agent response accepted by the backend; wrong-source response rejected without changing the candidate; graph of 13 nodes with declared links; author words and AI summary visibly separate; source-declared link verb inspectable; Genre, Trope and Structure facets explain the proposal; return to graph; no horizontal overflow at narrow width; at least two non-identical mechanisms; mentor alternative validates; explicit Keep creates only a working story item; re-entry preserves the verbatim Story Vision and restores the proposal and the kept working idea; reopened Browser exposes the graph; no page errors; all canonical and story file hashes unchanged.

Architecture candidate payload SHA-256: `7683ba6bc64c99f8eed49c4440a35cdd0330c01385434eb3f6883d7977967c08`.
Mentor payload SHA-256: `48926bd8d688eab76f8fd68d64fe854c5d947ccc7d95080af658b4015290c385`.

**Agent identity disclosure.** The coding agent in this run was Claude (Claude Code, claude-haiku-5-5) acting manually in the same session: it read each exact request packet from disk and wrote the response file. It was not the Codex CLI, and no Codex model was used. The receipt records the runtime as "operator-supplied executable; model unverified" because the runner does not know who wrote the file. This is an authentic manual coding-agent exchange in the sense of the manual lane, but it is a different agent identity from the earlier Codex manual run at `06fa522b`. The mentor advice and the architecture are both agent proposals; neither is accepted story material.

## Connected Browser → attached CLI at f2275a23: blocked

Two probes of the Codex CLI were made. The first failed because the directory was not trusted, which is an invocation problem. The second, run from the trusted worktree, failed with "Your workspace is out of credits. Ask your workspace owner to refill in order to continue." Nothing was retried after that. The connected lane therefore has no result at `f2275a23`. Its last PASS remains the one recorded at `06fa522b` (`2026-10-16-studio-connected-e2e.json`) and is not reused here.

## Scope and limits

- Human usability was not tested (`human_usability: NOT_TESTED`).
- The full 5,641-test regression was not rerun. The change is one line in one controller, and the controller's suite, the Python selected suites and the served Stage B journey all pass. The earlier checkpoint at `62e1df9f` had 17 failures, all of which reproduce on pinned `main`; this candidate was not compared against that set again.
- Protected integration is held. The configured factory validator is logged out and autonomy is 0. No merge and no release.
- Mentor fulfilment is still manual in the default server. The connected lane, when unblocked, is the only path where an attached executor runs.
