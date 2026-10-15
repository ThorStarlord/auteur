# Contextual Narrative Mentorship — Integration and Qualification Handoff

**Date:** 2026-10-14
**Scope:** Auteur graph-first Studio; implementation drafts #425, #427–#434; source contract in
`2026-10-13-contextual-narrative-mentorship.md`.
**Authority:** Development plan and evidence boundary only; does not approve merge, release,
canonical semantic-layer changes or automated author story acceptance.

## Reconciliation after PR #436 merge — 2026-10-14

The historical M0/M1 sections below describe the pre-merge plan and are retained as a record; their statements that PR #436 is unmerged or that a runnable checkout is unavailable are superseded by this section.

PR #436 merged as `4122321fe09d1959278fdd087fc29f85e2f3a9d2`. Its exact source qualification SHA was `97354ee6ea293df6c6b15783406e6c1d560403bf`. Recorded checks were Node 64/64, focused Python 28, `-k studio` 163, Stage B 16/16 and unfolding 11/11. The serial full Python suite reported 5,591 passed, 24 failed and 2 skipped; all 24 failures matched exact-main baseline, with no candidate-only failure recorded. No GitHub Actions runs were recorded. This is merged source evidence, not a claim that every suite passed.

A fresh agent mentorship sample against the merged backend completed through CanvasStore and passed strict response validation. It produced three materially different mechanisms while preserving the supplied author constraints. This is one response only; no real-author session, broad scenario set, narrow-screen UX study, or creative-product-readiness claim is established.

The 2026-10-14 post-merge product-use run found a Windows newline translation defect in exact-byte Chapter persistence. `Project.write_draft` and `Project.write_final` now request LF output; byte-level regression assertions accompany the repair. The focused chapter-generation, acceptance, and project tests pass (34 total) when `PYTHONPATH=src` ensures imports come from the isolated worktree. The repair remains an uncommitted worktree change on top of the merge SHA, so the recorded #436 qualification does not qualify this repair.

Issue #318 product use reached only Glass Archive Chapter 1. After repairing persistence, the frozen outline generated and explicitly accepted a 946-word Working scene in the disposable fixture. The pre-repair failed acceptance had written Bible events before exact-byte reconciliation failed; retrying that interrupted acceptance duplicated authority events in the fixture. The run stopped there; Chapters 2–6 and the F2/X3 journey gate remain unqualified. See [the full evidence packet](../qualification-evidence/4122321-post436-product-use.json).

Issue #310 used four fresh host-agent Quick Draft cases: mystery, character-driven, speculative and intentionally vague. All remain Working drafts. Browser `awaiting_host_agent` displayed a waiting state with the editor disabled, but did not expose the request prompt/hash in the page or naturally notify the active host agent during this run. The API accepted a response; reopening the session displayed the draft, while in-place completion was not observed. Per-request model and trustworthy latency were unavailable. Two scenes fell below the approximate 1,400-word target. These are agent dogfood results, not human author feedback; exact packets are in the evidence file linked above.

Current evidence does not establish product readiness, human usability, or completion of #318. It does establish that #436 is merged, that focused tests pass for the local newline repair, and that the selected product-use surfaces exposed concrete persistence and Browser handoff behavior. Continue by freezing the repair candidate SHA and qualifying it, then resume #318 from a clean controlled fixture. Reconcile #310 with the observed Browser interaction gap. Do not infer or implement a host bridge from this one observation.
## Objective and completed source work

An author can:
1. start from a working Story Vision and graph focus;
2. receive relevant explanations and source-attributed candidate questions/tensions;
3. explicitly ask a neutral coding agent for scoped advice (instead of replacing the entire architecture);
4. answer naturally, examine differing mechanisms and consequences;
5. review a candidate interpretation/alternative in an editable working preview;
6. keep a deliberate working idea using CanvasStore, leaving accepted story unchanged;
7. return to Focus/Full or Story Realization without an unintended write.

Source work is distributed across:
- #425 mentor mode projection + interaction;
- #427 read-only source-labelled author intent;
- #428 strict host-agent mentor request/response and local CLI;
- #429 served HTTP tests;
- #430 dialogue UI and scoped route;
- #431 author-reviewed working choice;
- #432 minimum divergence contract;
- #433 progressive-disclosure/quiet UI;
- #434 combined synthetic authoring journey.

**Actual evidence at the latest #436 integrated source checkpoint:** 107/107 isolated
JavaScript simulation checks passed: 16 model/context, 29 Focused Unfolding,
27 dialogue, 2 combined creative journey, 11 local suggestion/adoption,
8 Full Architecture, 10 explanation-view and 4 canvas-navigation checks. HTML script-route,
duplicate-ID and classic-JavaScript syntax checks also passed. These do not
represent an actual Node process, Python import/test, served browser or human study.
**NOT established:** exact Node test process; Python/persistence/HTTP suite; complete
served browser; accessibility with a screen reader; a capable live coding agent fulfilling
a real mentor request; author creative outcomes or 390px screenshot acceptability.

## M0 — main-preserving source integration assembled (#436)

**Current candidate:** `integration/studio-mentor-mainline-20261014`, draft PR #436,
based on `main@88f7219f4d533deaa76ce1b2c14a33cd2988b348`.
The initial assembly commit `c6d533e` overlays 90 paths, preserving 36
main-only files that the older Studio tip did not contain.

Further commits `5897940` and `5247aa5` reconciled #404's nine browser-source
fix hunks and four server default/fallback hunks with later mentor code. The
base-relative edits were checked for overlap and had **zero overlapping hunks**.
The assembled branch includes #404's safety Stage-B script, eight #404 regression
test file versions and the complete mentor source through #435.

**GitHub comparison vs current main at the integration checkpoint:**
90 files changed, 81 added, 9 modified, zero removed, branch ahead with
no main commits behind. Large scope is deliberate for an integration roll-up,
not an excuse to relax qualification.

**M0 is source-integrated, not executable-qualified.** Git object assembly,
source syntax and simulated interactions do not establish an actual checkout,
successful Python imports, complete Node test exit status, server startup,
served Chromium behavior or backend creative quality. Ancestor PRs remain
available until the integrated source is proven equivalent.

**Next real gate:** fetch/check out the exact #436 head in an environment with
the repository and Python/Node/Chromium dependencies. Reconfirm latest `main`
before integration promotion; if it advanced, reconcile real differences rather
than force-pushing or fabricating a merge.


### Integration hardening after initial assembly

Source review identified bounded authority and data-loss defects, repaired on
the same integration PR rather than starting another feature stack:

- Backend mentor context now cites **only actually disclosed** working and
  candidate sources, never hidden working items or stale candidate questions.
  Connected candidate summaries, relation verbs and candidate authority are
  included where properly source-bound.
- Working item IDs are independent from AI candidate node IDs. Equal ID text
  cannot silently transfer candidate links or open questions to working notes.
- Malformed host-agent response envelopes (missing required fields, null
  response text, or invalid elapsed-time types) are **400-class client
  validation errors**, not opaque HTTP 500s; the pending request and working
  canvas remain intact. The new Python regression cases are committed but
  still need actual Python/HTTP execution.
- Mentor dialogue clears previously visible advice and Keep controls after
  canvas/source changes or a stale server response, not merely at save time.
- The shared working-command controller refuses to create/keep questions or
  adopt local/agent suggestions while the working editor has unsaved text.
  Explicit Save of that editor remains available.

**Regression additions:** six focused Python/HTTP cases for source visibility,
stale sources, independent node-ID namespaces and malformed envelopes; five
JavaScript tests across conversational and Focused Unfolding controls. The
JavaScript cases were executed in isolation against exact GitHub source bytes;
the new Python and real HTTP tests are still **NOT RUN**.

### Adversarial author and coding-agent proxy exploration (2026-10-14)

**This is not an independent coding-agent run or real user study.**
The coding assistant authored four explicit `MentorAdvice` packets in
`tests/fixtures/studio_mentor_proxy_author_cases.json`; they are scripted
proxies that deliberately exercise creative interpretation and option comparison.
A parametrized Python roundtrip suite in
`tests/test_studio_mentor_proxy_replays.py` will validate those packets through
the real neutral host-agent/CanvasStore boundary when an executable checkout
exists. The browser dialogue test already replays all four packets against
the exact JavaScript controller, with no implicit story change.

| Scenario | Recommended proxy default | What the test can establish |
| --- | --- | --- |
| Exceptional generous paladin + independent companions | Reject the false dilemma that competence diminishes the hero; explore institutions, companion judgment, exceptional escalation | Scripted choices retain author intention and express differing structural mechanisms |
| Deliberately unconventional fantasy structure | Ask how cyclical consequences change over time; do not demand a three-act template | The authored packet avoids asserting genre orthodoxy |
| Desirable optimistic academy + occasional horror | Preserve ordinary life and make restoration visibly consequential | The authored packet keeps horror from mechanically forcing nihilism |
| Genre, tone and structure unknown | Ask one useful question and avoid fabrication | The authored packet can elect not to recommend ungrounded directions |

**Proxy findings:** the four manually written responses supply eight provisional
directions across distinct axes, three different creative contexts plus a
low-evidence no-option case. The dialogue controller displays tradeoffs, keeps
author-reply attribution, and requires author review before a CanvasStore-shaped
working write. Added adversarial JavaScript cases also exercise slow focus
changes, failed host requests, double save attempts, server errors, unsafe-looking
strings, repeated render, and lossless rejection of unsaved working-idea text.

**Limits:** a human-authored/sample answer passing its own assertions does
not demonstrate that a fresh coding-agent response would be as good. Semantic
paraphrases can also pass the simple duplicate-mechanism validator; real
generative divergence remains a qualitative open question. Prior user walkthrough
evidence for the old Beginner UI is not an actual usability test of this new
graph-first mentorship surface. Do not rerun old tests as ceremony; target the
changed Focus/mentor/write/return seam and a narrow-screen walkthrough.

**Safe provisional owner decisions:** graph remains the primary UI, mentor
remains optional and can go quiet, sources are attributed, unknown Genre Pack
evidence stays unknown, hopeful/unconventional premises are not overridden by
generic genre prejudice, and author acceptance remains explicit. These are
already-grounded engineering defaults, not synthetic owner preference updates.

### Additional source-freshness repair

- The browser now tracks the actual architecture response status. A stale,
  pending or review-ready candidate cannot supply attributed mentor links,
  candidate questions, or optional graph alternatives as if the source were
  current.
- Pure working-idea mentorship remains available when an unrelated candidate
  architecture is stale, with a **null candidate source SHA** matching the
  backend's allowed provenance.
- Four scenario proxy packets and the Python roundtrip test were added.
  The earlier 94/94 V8 checkpoint included ten additional dialogue cases plus
  source-status and working-focus regressions. **Python proxy tests are
  committed, not executed.**

### Author data-loss reproduction and bounded repairs (#436 continuation)

Two previously undetected source-level defects were reproduced against the
exact committed browser controllers, not inferred from stylistic preference.

1. **Focused working editor lost text on re-render.** The prior implementation
   cleared and rebuilt `unfolding-author-edit` from the saved CanvasStore item
   every time `render()` ran; a typed but unsaved body reverted immediately.
   Repair: preserve dirty working-editor drafts in memory keyed by canvas and
   item, including across Focus changes, until explicit author Save. The shared
   command boundary now checks hidden drafts as well as visible edits; browser
   navigation and the legacy-interface handoff treat these drafts as unsaved.
   Recorded source-level rerender/focus and failed-save regression tests now pass,
   for **29/29 Focused controller checks**.
2. **Editable mentor preview could silently disappear.** A fresh follow-up,
   closing the dialogue, replacing a chosen interpretation, or stale source
   projection could conceal a carefully rewritten proposed idea. Repair:
   edited preview remains available until the author explicitly keeps or
   discards it. A local Discard control is visible only with the preview;
   stale preview remains copyable but is **not** eligible for saving against
   invalid provenance. Four new dialogue regressions pass, for **27/27
   conversational controller checks**.

The combined synthetic author journey continues to pass **2/2**.
The remaining model/context, adoption, Full Architecture and explanation
suites were rechecked against the connected GitHub source. A third adjacent
data-loss path was reproduced: a canvas switch could navigate despite an
unsaved Focus draft. It now blocks before navigation, restores the picker
value, and checks queued saves again. Four additional navigation tests pass.
Across the available suites, **107/107 exact-source isolated JavaScript
checks pass**. The current HTML has no duplicate
IDs; 10 script sources resolve to served routes; changed classic-JS sources
parse successfully.

**These are not actual Node, Python, served Chromium or human UX results.**
The execution container has Node 22, Python 3.13, pytest, Pydantic 2 and
Playwright available, but cannot resolve `github.com`,
`api.github.com` or `raw.githubusercontent.com`; no complete Auteur checkout
is mounted. Connected GitHub returns text files and Git objects but does not
provide a runnable command executor. GitHub Actions billing remains a prior
explicit constraint; no paid CI run was initiated. This is an external
qualification dependency, **not** a pass/fail verdict on the full application.

**First resumed executable action:** check out this PR's exact head; rerun
`node --test` and focused Python/HTTP tests, then Playwright Stage-B and a
new browser check that types an unsaved working-editor draft, re-renders/switches
Focus, verifies draft preservation, explicitly saves, reloads, and verifies
canonical files remain untouched. Re-run the full suites after bounded fixes.
Do not reimplement these two repairs without fresh contradictory runtime
evidence.

## M1 — real Studio mechanical qualification

Run from the assembled source:

```sh
node --test tests/test_studio_mentorship.mjs tests/test_studio_mentor_context.mjs tests/test_studio_unfolding_controller.mjs tests/test_studio_mentor_dialogue.mjs tests/test_studio_mentor_synthetic_journey.mjs tests/test_studio_canvas_navigation.mjs
python -m pytest -q tests/test_studio_mentor_agent.py tests/test_beginner_studio_mentor_http.py tests/test_studio_mentor_proxy_replays.py
python -m pytest -q tests -k studio
python scripts/studio_stage_b_check.py
```

Before asserting any command passed, confirm prerequisites and local test
configuration; report actual stdout/exit code. Use exact-head evidence, not a
previous branch result.

Required real served HTTP/CanvasStore cases:
- Work from empty Story Vision through initial architecture proposal and Focus.
- Reopen project, select working/derived architecture, create and edit ideas.
- Exercise mentoring request, complete valid/invalid HostAgentResponse packets,
  stale source, duplicate request, missing focus, and API failures.
- Keep one source-bound working suggestion; confirm exact stored provenance and
  no change to accepted Identity, Structure, Realization or prose.
- Simulate simultaneous editing, stale canvas revision, failed write and
  conflicting command ID. Verify no success claim or dropped author text.
- Switch Focus, Full, Review and writing and back; preserve viewport, notes,
  selected focus, narrative content and response context as applicable.
- Test keyboard traversal, focus restoration, scroll, 1440px and 390px viewport,
  high information density, and relationship labels without relying on color.

No mandatory GitHub Actions: use local checks while billing is constrained.

## M2–M5 — semantic / model-backed qualification

A real capable coding agent should fulfill the prepared mentorship request
through the backend-neutral contract. Example:

```sh
python -m auteur.beginner.studio_mentor --project PROJECT --canvas CANVAS show
python -m auteur.beginner.studio_mentor --project PROJECT --canvas CANVAS complete-file --advice mentor-advice.json
```

The `mentor-advice.json` file here contains the model's raw strict MentorAdvice
JSON, not the HostAgentResponse envelope; the CLI performs neutral wrapping.
The UI supports an already-wrapped envelope when supplied by the host.

Test three distinct narrative directions:
- hopeful paladin and companion agency: challenge mechanism without imposing cynicism;
- genre-subversive intention: do not mechanically restore convention;
- multi-genre or missing Genre Pack: do not invent binding genre conventions.

For each, inspect how alternatives differ in causal engine, choices, agency,
emotional effects, structural demands and tradeoffs. The deterministic
`distinguishing_factor` and duplicate-mechanism validation are a floor,
not proof of creative diversity. Require author-relevant comparative outputs
rather than a numeric creativity score.

Test full dialogue:
source-backed question -> author's exact-language reply -> model interpretation
-> author correction or rejection -> editable working idea -> graph consequences.
No model interpretation becomes accepted authority automatically.
Author replies remain quoted and separately labelled from AI hypotheses.

## M6 — visual and flow qualification

Observe an actual authoring journey:
- Is the graph visually primary?
- Does the inspector show just one useful mentor contribution at a time?
- Is the collapsed alternative-mode control discoverable without taking over
  the first screen?
- Do the mentor overlay, Full view and response details obstruct composition
  at narrow viewport widths?
- Does quiet mode remain reversible, and is writing uninterrupted?
- Are provenance, proposal, working state and explicit acceptance legible?

Correct demonstrated friction at the smallest owning UI surface. Avoid a second
permanent chat column, new ontology or speculative personalized agent storage.

## Claim / promotion boundaries

| Claim | Evidence required | Current disposition |
| --- | --- | --- |
| Source files and regression specifications exist | GitHub commit/ref and diff | Established on integration PR #436 |
| Simulated JavaScript interaction correctness | Exact-source V8 isolated runs | 107/107 exact-source isolated checks PASS; not Node/browser |
| Main-based integration source assembly | Git tree overlay + #404 hunk reconciliation | Constructed on branch #436; runnable checkout NOT established |
| Backend mentor protocol correctness | Python contract and real HTTP tests | Not executed |
| Real author working persistence | Served Browser/CanvasStore and reload | Not executed |
| Authentic model creative quality | Actual neutral host-agent responses | Not executed |
| Human usability and flow | Real author walkthrough | Not established |
| Merge / rollout / release ready | Explicit owning gates and authority | NOT claimed |

## No new owner decision is needed for the next bounded engineering step

The next responsible actor should CHECK OUT and QUALIFY PR #436, not rebuild
the same source integration or ask the owner to restate the product design. If verification
finds defects, repair the nearest demonstrated cause, repeat the failing
test, and continue within existing author-authority invariants.

A blocked local runtime is an evidence limit, not a reason to mark all
independent source development complete or to invent success.
