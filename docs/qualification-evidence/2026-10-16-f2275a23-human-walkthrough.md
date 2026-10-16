# Human usability walkthrough kit: Narrative Architecture at f2275a23

**Status: NOT TESTED.** No human participant has been observed. Every result in the repository so far comes from automated Browser probes, which do not establish human usability. This document is a ready-to-run protocol and a blank observation sheet. Do not record PASS from it until a real author has completed it.

Product candidate: `f2275a2391d3d579db3c2740717e262b80758563` (PR #449). Evidence: PR #450.

## 1. Launch

Run from a clone of the candidate worktree, using the repository's own server entry point. No API key is needed: without `--provider` the server runs in manual mode.

```bash
cd "H:/codex/qualification/auteur-narrative-20261016/onboarding"
```

```bash
PYTHONPATH="$PWD/src" "H:/codex/qualification/auteur-narrative-20261016/venv/Scripts/python.exe" -m auteur.beginner.server --project "H:/codex/qualification/auteur-narrative-20261016/walkthrough/populated-project" --port 8765
```

Open `http://127.0.0.1:8765/studio.html` in a normal browser window at a desktop width, and keep the console visible for the facilitator.

For the first-session task, use the empty project instead:

```bash
PYTHONPATH="$PWD/src" "H:/codex/qualification/auteur-narrative-20261016/venv/Scripts/python.exe" -m auteur.beginner.server --project "H:/codex/qualification/auteur-narrative-20261016/walkthrough/empty-project" --port 8766
```

Both projects are disposable copies outside the repository. Do not point this at a real manuscript. Reset a project by copying its pristine source again. The populated project was produced by the manual E2E replay, so it already contains a proposal architecture, a Story Vision, and one kept working idea. **Do not tell the participant that.**

Do not click "Develop architecture" during the session. In manual mode it waits for a coding agent, which is outside this walkthrough.

## 2. Facilitator rules

- Read each task aloud as written. Do not add hints, names of features, or conclusions about what anything means.
- If the participant asks what something means, answer with a question: "What do you think it means?" Note the question and the answer.
- Time each task from the moment you read it until the participant states they are done, or gives up.
- Record "unaided" only if you gave no help. Record "assisted" if you gave any hint.
- Write observations in the participant's words where possible.

## 3. Tasks

Each prompt is neutral. The success check is what you observe, not what the participant says.

| # | Prompt (read aloud) | Success observed (no hint) |
|---|---|---|
| 1 | "Open the architecture view of this project and tell me what you see." | Participant reaches the Narrative Architecture view and can say what is on the screen. |
| 2 | "What does this graph represent, as you understand it?" | Participant describes the graph in their own words. Note whether they call it a plan, a story, a suggestion, or something else. |
| 3 | "Find the text that is yours, and the text that the system produced." | Participant distinguishes the Story Vision from the AI proposal, and points to the labels that separate them. |
| 4 | "Pick one concept on the graph and tell me how it relates to the others." | Participant selects a node and reads its meaning and links. |
| 5 | "Look at the genres, tropes, structure, and emotional goals. Tell me one thing you learn from each." | Participant uses the facets (Genres, Tropes, Structure, Emotions) and reads an explanation from each. |
| 6 | "Show me an alternative way the system suggests this story could work, and tell me the trade-off between the alternatives." | Participant reaches a comparison of at least two alternatives and states one difference between them. Note: the compare control may be disabled until a concept is selected. See section 5. |
| 7 | "Keep one idea you find useful, or reject one you don't. Tell me what changes when you do." | Participant performs a keep or reject, and their description of the result matches what the screen shows. |
| 8 | "Close this and reopen the project. Tell me what you expect to still be there, and check." | Participant reopens, and identifies what was preserved (Story Vision, proposal, kept idea, graph). |
| 9 | "Which of these things are settled story material, and which are only proposals?" | Participant separates accepted canon from working proposals, and gives a reason. Note any answer that calls the AI proposal "accepted". |

For the first-session check, use the empty project, then read: "Start a story from this empty project." Success: the participant finds the onboarding start, chooses a starting point, and adds a first working idea.

## 4. Observation sheet

Copy this table per participant. Do not record names. Use "P1", "P2" and so on, and keep consent forms outside this repository.

| Task | Unaided? (Y/N/assisted) | Time (s) | Difficulty (1-5) | Confusing labels or interactions | Wrong assumption about AI output | Wrong assumption about canon | Navigation problem | Alternatives understandable and useful? |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | n/a |
| 2 | | | | | | | | n/a |
| 3 | | | | | | | | n/a |
| 4 | | | | | | | | n/a |
| 5 | | | | | | | | n/a |
| 6 | | | | | | | | |
| 7 | | | | | | | | n/a |
| 8 | | | | | | | | n/a |
| 9 | | | | | | | | n/a |

Also record, in the participant's words: what they thought the system would do next, what they expected a "keep" to change, and whether the proposed story direction respected the Story Vision.

## 5. Hypotheses to test, not conclusions

These come from automated inspection and screenshots. They are not observed user problems. Treat each as something to confirm or refute, and do not raise them with the participant.

1. **Compare control is disabled with no visible reason.** `#contrast-explore` is disabled until a concept is selected (`studio.js`, the line that sets `disabled = !state.selectedCandidate ...`). Its explanatory message fires only on click, and a disabled button never fires a click. A participant may see a greyed button with no reason. Watch task 6.
2. **Stale-proposal banner.** In the populated project the proposal panel shows "Older proposal; your working Story Vision has changed." Ask the participant what it means after task 3, and do not explain it.
3. **Graph partly below the fold** at a 900 px tall window. Watch whether the participant finds the rest of the graph without being told to scroll.
4. **Paladin and protagonist.** The candidate proposal and mentor advice were written to avoid imposing a moral flaw on the author's generous protagonist. Ask the participant only: "Did the suggestions respect what you wanted?" Do not ask whether they are good.

## 6. Results

| Participant | Date | Project used | Tasks completed unaided | Notes | Status |
|---|---|---|---|---|---|
| (none yet) | | | | | **NOT TESTED** |

Human usability is NOT TESTED until at least one real author completes the protocol and the sheet above is filled in.
