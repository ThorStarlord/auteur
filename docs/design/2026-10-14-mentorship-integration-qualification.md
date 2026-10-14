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

**Actual evidence:** exact-source JavaScript simulator checks passed (15 model/context,
20 controller, 10 dialogue, 2 combined journey: 47/47 isolated checks).
**NOT established:** exact Node test process; Python/persistence/HTTP suite; complete
served browser; accessibility with a screen reader; a capable live coding agent fulfilling
a real mentor request; author creative outcomes or 390px screenshot acceptability.

## M0 — integration: first genuine prerequisite

The current `main` is not identical to #404 or the #424–#434 stack. Do NOT
fabricate a merge by replacing `main`'s tree with the draft branch.

1. In a runnable checkout, fetch fresh `main` and all relevant PR heads.
2. Inspect Git ancestry. #404 integrates #346–#403 but may include corrections
   absent from the later continuation stack; compare them at file/behavior level.
3. Review #408–#413 focused authoring and #419–#424 Full Architecture integration.
   #416's Full Architecture projection was merged independently: avoid duplicate
   implementations.
4. Construct one reproducible integration branch from current `main`, resolving
   actual conflicts and preserving Studio development-default/legacy fallback.
5. Include #425, #427–#434 by bounded cherry-picks or equivalent reviewed patches.
   Reconcile this doc branch after the final implementation head.
6. Run source/build checks and record exact branch SHA; do not close ancestor PRs
   until integrated changes are independently verified and ancestry is clear.
7. Prefer one bounded integration PR with transparent change/evidence review,
   not an unreviewable mass merge.

**Stop condition:** a reproducible Studio baseline exists without losing current
`main` fixes, canonical authority, or the previous Beginner fallback. If local
checkout is unavailable, mark `WORKSPACE_UNAVAILABLE`; independent branch work
may continue without pretending integration passed.

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
| Source files and regression specifications exist | GitHub commit/ref and diff | Established on draft stack |
| Simulated JavaScript interaction correctness | Exact-source V8 isolated runs | Model/context 15; focused 20; dialogue 10; combined 2 PASS |
| Runnable repository integration | Current main + assembled branch + build/run | Not established |
| Backend mentor protocol correctness | Python contract and real HTTP tests | Not executed |
| Real author working persistence | Served Browser/CanvasStore and reload | Not executed |
| Authentic model creative quality | Actual neutral host-agent responses | Not executed |
| Human usability and flow | Real author walkthrough | Not established |
| Merge / rollout / release ready | Explicit owning gates and authority | NOT claimed |

## No new owner decision is needed for the next bounded engineering step

The next responsible actor should integrate and execute the current stack
rather than ask the owner to restate the product design. If verification
finds defects, repair the nearest demonstrated cause, repeat the failing
test, and continue within existing author-authority invariants.

A blocked local runtime is an evidence limit, not a reason to mark all
independent source development complete or to invent success.
