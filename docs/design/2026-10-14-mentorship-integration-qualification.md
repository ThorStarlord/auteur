# Contextual Narrative Mentorship — Integration and Qualification Handoff

**Date:** 2026-10-14
**Scope:** Auteur graph-first Studio; implementation drafts #425, #427–#434; source contract in
`2026-10-13-contextual-narrative-mentorship.md`.
**Authority:** Development plan and evidence boundary only; does not approve merge, release,
canonical semantic-layer changes or automated author story acceptance.

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

**Actual evidence at the latest #436 integrated source checkpoint:** 81/81 isolated
JavaScript simulation checks passed: 15 model/context, 22 Focused Unfolding,
13 dialogue, 2 combined creative journey, 11 local suggestion/adoption,
8 Full Architecture and 10 explanation-view checks. HTML script-route, duplicate-ID
and classic-JavaScript syntax checks also passed. None are real served-browser tests.
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
- A malformed host-agent response missing required envelope fields is a
  **400-class client validation error**, not an opaque HTTP 500; the pending
  mentor request and working canvas remain intact.
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

## M1 — real Studio mechanical qualification

Run from the assembled source:

```sh
node --test tests/test_studio_mentorship.mjs tests/test_studio_mentor_context.mjs tests/test_studio_unfolding_controller.mjs tests/test_studio_mentor_dialogue.mjs tests/test_studio_mentor_synthetic_journey.mjs
python -m pytest -q tests/test_studio_mentor_agent.py tests/test_beginner_studio_mentor_http.py
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
| Simulated JavaScript interaction correctness | Exact-source V8 isolated runs | 81/81 focused source checks PASS; not browser |
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
