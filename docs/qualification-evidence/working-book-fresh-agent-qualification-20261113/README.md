# Fresh-agent Book construction qualification (The Spring Ledger, Book 24)

**Status: not completed.** No fresh participant returned a Book candidate, and nothing was submitted by a participant. The construction stage, and every stage that depends on it (participant revision, fresh continuation, and independent evaluation of a participant's Book), could not be performed. No coordinator-authored Book was substituted for one. What follows records the baseline, the input boundary, the two participant attempts and their outcome, and the product-side checks that were possible.

**Date:** 2026-11-13. **Baseline:** `origin/main` at `229037c5`. **Authority:** every Book in this record is noncanonical. Nothing was accepted, and no accepted Series, Book, Story, or ontology state was touched.

## 1. Baseline

| Item | Verified |
|---|---|
| `origin/main` | `229037c5` (PR #560 merge) |
| PR #558 merge `9fdef0e5` | ancestor of main |
| PR #559 merge `fe06f2c4` | ancestor of main |
| PR #560 merge `229037c5` | ancestor of main |
| PR #557 | closed, not merged (historical design only) |
| W6 Series candidate at `fa85b7f1:experiments/spring-ledger-working-architecture/02-working-candidate-W6.json` | sha256 `dde2b0f6…` (matches the staged copy) |
| Author intentions at `fa85b7f1:…/03-author-intentions.md` | sha256 `ce954da7…` |
| Author's Book 24 responsibility at `fa85b7f1:…/cold-start/packet-as-given/00-task.md` (verbatim blockquote) | sha256 `8374f3a4…` |
| Book 24 cold-start function at `fa85b7f1:…/cold-start/output/book-24-function.corrected-2.md` | **excluded.** Only its existence was checked, with `git cat-file -t`. It was not read by the coordinator and was not given to any participant. |

The participant's Python source was taken from `origin/main` with `git archive`, so it is the canonical code.

## 2. Canvas and the develop request

The disposable canvas `spring-ledger-qual` contains only:

- the Series working architecture W6, developed through the Studio bridge (status `ready`);
- the Story Vision (the author's identity paragraph and the four directives);
- the four author-directed intentions, recorded with `keep-intention`;
- the author's verbatim Book 24 responsibility, as a working item in group `book-24`.

`book-prepare --book 24` (run by the coordinator) produced request `77e0f638…`. It has a 43,610-character packet and a 3,347-character system instruction, and it contains 16 Series open questions, indexed and hashed. Its visible source is six items: one author brief, one Story Vision, and four intentions (`coordinator/request-summary.json`). Series node summaries and open questions reach the request through the Series architecture, not as separate source items.

## 3. Input boundary

Given to the participant (`inputs/participant-task.md` and the request file):

1. The author's responsibility, verbatim, labelled as historical author text.
2. Operator framing, labelled as created for the test and not as an author declaration (position after Book 23, no finale selection, no arbitrary antagonist, provisional status).
3. The develop request, including the system instruction describing the candidate format.
4. The Book operation contract: `inputs/product-instructions-book.md`, extracted from the bridge guide on `origin/main`.
5. The CLI and the disposable project path. The source used for those commands is the `origin/main` copy.

Withheld from the participant: the Book 24 cold-start function and its correction history; the PR #555 challenge and correction reports; the PR #558 and PR #560 candidates; the previous evaluator answers; and the historical task packet, which lists the expected deliverables. The coordinator held that packet back deliberately.

**Exposure not controlled.** The participant ran in the repository's working directory. Nothing prevented it from opening other repository files. Its transcript was not observable (see section 4), so no access, and no absence of access, is recorded.

## 4. Participant attempts

Both attempts were fresh general-purpose subagents with no inherited conversation. Each was given the task file and nothing else. Neither returned.

| Attempt | Task file | Outcome |
|---|---|---|
| 1 | `inputs/participant-task-attempt1.md` | No candidate file, no submission. Stopped after about two and a half hours of waiting. |
| 2 | `inputs/participant-task.md` (adds section 7: first action is to read the request, and a 15,000 to 35,000-character bound) | No candidate file, no submission. Stopped after about two hours of waiting. |

The participants' output folder and the canvas's Book directory stayed unchanged for the whole waiting period (the request file was the only Book artifact). The subagent transcript files were empty until each agent was stopped, so tool-call counts and any access were unobservable. The record therefore makes no claim about how far either participant got, or whether it was reasoning, stuck, or never started. Each was stopped after a bounded wait. A `SendMessage` time check to attempt 1 did not produce output either. The mission allowed one replacement, and this is that replacement.

Earlier in this session, two other subagents launched for the revision work also failed to return. They were a reviewer and a fresh-context answerer, both stopped. Their outcomes are recorded in the revision evidence, not here.

## 5. Mechanical controls (not a Book)

To test the product on the real pending request without authoring a Book, the coordinator submitted one deliberately malformed candidate (`coordinator/negative-control-malformed.json`, truncated JSON). Results:

- The CLI rejected it (exit 1; `json_invalid`).
- The snapshot before and after shows **no changed files** (`coordinator/snapshots/`).
- The pending request remained in place.
- `book-resume` still reported `not_started`.

This shows that validation rejects invalid input without persisting anything. It says nothing about the quality of a valid Book.

## 6. Classification

| Evidence | Class |
|---|---|
| Two participants produced no returned work over more than four hours in total | **Orchestration or evidence infrastructure** is the most plausible cause, since several longer-running subagents in this session also did not return. **Insufficient evidence** to separate that from participant non-progress, because transcripts were unavailable until stop. |
| Source material and the request contain what the task needed | Not a source-availability or context-delivery failure. Nothing in the request was missing from the evidence. |
| The malformed candidate was rejected, and nothing changed | Mechanical operation behaved correctly. |
| No product behaviour was observed on a valid participant candidate | Product capability for construction, revision, and continuation is **unqualified** in this mission. |

No product defect was found. No production change is warranted by this mission's evidence.

## 7. The fifteen questions, answered from observation

1. **Did a fresh agent construct its own Book?** No. Two fresh participants returned nothing.
2. **What input was available?** The inputs in section 3, and the request in section 2.
3. **Did the artifact preserve creative structure?** Not assessable. There is no artifact.
4. **Could Auteur validate and persist?** Validation rejected malformed input without persisting it (section 5). Acceptance of a valid candidate was not observed in this mission. Earlier missions observed it.
5. **Could it be recovered in another process?** Not assessed for this mission. The resume returned `not_started` correctly for the empty state.
6. **Could an agent revise through the lifecycle?** Not assessed here. The revision lifecycle was exercised in the revision mission (PR #560), by the implementing agent.
7. **Did the agent identify the right scope?** Not assessable.
8. **Which dependencies were explicit, inferred, missed, or unverifiable?** Not assessable.
9. **Did a fresh agent recover enough understanding to continue?** Not assessed.
10. **Did Auteur's knowledge contribute?** Not assessed.
11. **Were authorial commitments and accepted state preserved?** Yes, for everything observed. The canvas contained only working items, and the snapshots show no file changed across the rejected submission.
12. **Limitations:** orchestration, not product (section 6).
13. **Which findings warrant production changes?** None from this mission.
14. **Smallest valuable next responsibility:** obtain one returned fresh construction under a process that reports checkpoints, so that the attempt can be observed while it runs. That is an evidence and orchestration responsibility, not a product change.

## 8. What the record can and cannot support

It supports: the baseline identities; a source-clean input boundary for a fresh construction; the develop request's contents; and a malformed-input rejection with no side effects.

It does not support any claim that a fresh agent can construct, revise, or continue a Working Book Architecture. Every such claim remains unqualified.

## Files

- `inputs/` — the two task-file versions (attempt 1 and the replacement) and the product instructions.
- `coordinator/` — the request summary, the negative control, and the protected-state snapshots before and after it.
