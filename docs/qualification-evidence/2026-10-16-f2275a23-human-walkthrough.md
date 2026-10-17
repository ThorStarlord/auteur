# Human usability walkthrough kit: Narrative Architecture at f2275a23

**Status: NOT TESTED.** No human participant has been observed. Every result in the repository so far comes from automated Browser probes, which do not establish human usability. This document is a ready-to-run protocol and a blank observation sheet. Do not record PASS from it until a real author has completed it.

Product candidate: `f2275a2391d3d579db3c2740717e262b80758563` (PR #449). Stale-notice fix: `12c6971c` (PR #451, stacked on #449). Evidence: PR #450.

## 1. Fixtures

Three disposable project copies live in `walkthrough/`, outside the repository. Reset any of them by copying the pristine source again.

| Fixture | State | Use it for |
|---|---|---|
| `current-project` | Story Vision and one current proposal. No working ideas added after the proposal. | Tasks 1–7 and 9. Comparison (task 6) only works here. |
| `stale-project` | Same proposal, plus one kept working idea ("Capability ladder") added after it was generated. | Task 8 (reopen) and optional task 10 (recovery). |
| `empty-project` | Nothing. | First-session check. |

### Why the fixtures differ (verified, not assumed)

- In `stale-project` the proposal's source digest was recorded when the working items were empty (`working_items: []`). The Story Vision is unchanged since then. The only later change is the kept working idea.
- The backend marks a proposal stale when the Story Vision **or** any working idea or connection changes, so the kept idea alone makes it stale. This is why the notice now says "your Story Vision or working ideas changed".
- While stale, "Compare alternative interpretations" stays disabled even after a concept is selected. The button requires `architectureSourceStatus === "ready"`.
- Probe results on `stale-project`: the status line shows the stale wording; compare is disabled before and after selecting a node. On `current-project`: the status reads as a current proposal; compare is disabled before selection and enabled after selecting a node.
- Removing the kept idea from a copy is the only change between the two fixtures. The Story Vision and proposal are unchanged.

## 2. Launch

Run from the candidate worktree. No API key is needed: without `--provider` the server runs in manual mode.

```bash
cd "H:/codex/qualification/auteur-narrative-20261016/onboarding"
```

Current proposal (tasks 1–7 and 9):

```bash
PYTHONPATH="$PWD/src" "H:/codex/qualification/auteur-narrative-20261016/venv/Scripts/python.exe" -m auteur.beginner.server --project "H:/codex/qualification/auteur-narrative-20261016/walkthrough/current-project" --port 8765
```

Stale proposal (task 8 and optional task 10):

```bash
PYTHONPATH="$PWD/src" "H:/codex/qualification/auteur-narrative-20261016/venv/Scripts/python.exe" -m auteur.beginner.server --project "H:/codex/qualification/auteur-narrative-20261016/walkthrough/stale-project" --port 8766
```

First session:

```bash
PYTHONPATH="$PWD/src" "H:/codex/qualification/auteur-narrative-20261016/venv/Scripts/python.exe" -m auteur.beginner.server --project "H:/codex/qualification/auteur-narrative-20261016/walkthrough/empty-project" --port 8767
```

Open `http://127.0.0.1:<port>/studio.html` in a normal browser window at a desktop width. The launch command was verified to serve HTTP 200.

Do not click "Develop architecture" during a session. In manual mode it waits for a coding agent, which is outside this walkthrough.

## 3. Facilitator rules

- Read each task aloud as written. Do not add hints, names of features, or conclusions about what anything means.
- If the participant asks what something means, answer with a question: "What do you think it means?" Note the question and the answer.
- Time each task from the moment you read it until the participant says they are done, or gives up.
- Record "unaided" only if you gave no help. Record "assisted" if you gave any hint.
- Write observations in the participant's words where possible.
- Do not tell the participant about the fixtures' history, the kept idea, or the stale state.

## 4. Tasks

| # | Fixture | Prompt (read aloud) | Success observed (no hint) |
|---|---|---|---|
| 1 | current | "Open the architecture view of this project and tell me what you see." | Reaches the Narrative Architecture view and can say what is on screen. |
| 2 | current | "What does this graph represent, as you understand it?" | Describes it in their own words. Note whether they call it a plan, a story, a suggestion, or something else. |
| 3 | current | "Find the text that is yours, and the text that the system produced." | Distinguishes the Story Vision from the AI proposal, and points to the labels that separate them. |
| 4 | current | "Pick one concept on the graph and tell me how it relates to the others." | Selects a node and reads its meaning and links. |
| 5 | current | "Look at the genres, tropes, structure and emotional goals. Tell me one thing you learn from each." | Uses the facets (Genres, Tropes, Structure, Emotions) and reads an explanation from each. |
| 6 | current | "Show me an alternative way the system suggests this story could work, and tell me the trade-off between the alternatives." | Reaches a comparison of at least two alternatives and states one difference. Compare requires a selected concept first. |
| 7 | current | "Keep one idea you find useful, or reject one you don't. Tell me what changes when you do." | Performs a keep or reject, and their description matches what the screen shows. |
| 8 | stale | "Close this and reopen the project. Tell me what you expect to still be there, and check." | Reopens and identifies what was preserved: Story Vision, proposal, the kept idea, and the graph. |
| 9 | current | "Which of these things are settled story material, and which are only proposals?" | Separates accepted canon from working proposals and gives a reason. Note any answer that calls the AI proposal "accepted". |
| 10 (optional) | stale | "This panel says the proposal is older. What do you think changed, and what would you do next?" | Participant states a plausible cause and a next step. Do not confirm or correct. |

Task 7 changes the working state of `current-project`. That is intended. Task 8 uses `stale-project`, whose kept idea is already present.

For the first-session check, use `empty-project`, then read: "Start a story from this empty project." Success: the participant finds the onboarding start, chooses a starting point, and adds a first working idea.

## 5. Observation sheet

Copy per participant. Use "P1", "P2" and so on. Do not record names. Keep consent records outside this repository.

| Task | Fixture | Unaided? (Y/N/assisted) | Time (s) | Difficulty (1-5) | Confusing labels or interactions | Wrong assumption about AI output | Wrong assumption about canon | Navigation problem | Alternatives understandable and useful? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | current | | | | | | | | n/a |
| 2 | current | | | | | | | | n/a |
| 3 | current | | | | | | | | n/a |
| 4 | current | | | | | | | | n/a |
| 5 | current | | | | | | | | n/a |
| 6 | current | | | | | | | | |
| 7 | current | | | | | | | | n/a |
| 8 | stale | | | | | | | | n/a |
| 9 | current | | | | | | | | n/a |
| 10 | stale | | | | | | | | n/a |

Also record: what the participant expected a "keep" to change, whether the proposed direction respected the Story Vision in their own view, and any moment they asked what "stale" or "older" meant.

## 6. Hypotheses to test, not conclusions

These come from code and automated probes. They are not observed user problems. Confirm or refute them, and do not raise them with the participant.

1. **Compare is disabled until a concept is selected, and the reason is not visible.** The explanation fires only on click, and a disabled button never fires a click. Watch task 6.
2. **In a stale proposal, compare stays disabled even after a selection.** This is verified in the code and the probe. Whether an author understands why is untested. Task 10 covers it.
3. **The stale notice is now accurate but may still be unclear.** Watch whether the participant understands "older proposal" without explanation.
4. **The kept idea can cover the first graph node.** On `stale-project` the kept node sat over the first graph node and intercepted clicks in the probe. Watch for accidental selection or confusion during tasks 4 and 8.
5. **Graph partly below the fold** at 900 px height. Watch whether the participant finds the rest of the graph without being told to scroll.
6. **Protagonist framing.** The candidate proposal and mentor advice were written to avoid imposing a moral flaw on the author's generous protagonist. Ask only: "Did the suggestions respect what you wanted?" Do not ask whether they are good.

## 7. Results

| Participant | Date | Fixture(s) used | Tasks completed unaided | Notes | Status |
|---|---|---|---|---|---|
| (none yet) | | | | | **NOT TESTED** |

Human usability is NOT TESTED until at least one real author completes the protocol and the sheet above is filled in.
