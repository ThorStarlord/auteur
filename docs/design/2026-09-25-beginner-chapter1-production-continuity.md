# Beginner Chapter 1 Production Continuity

**Status:** Authorized for construction  
**Date:** 2026-09-25  
**Base:** `main @ c1c8e6e9e75fe7f9275e07b91aae7af6c530a9df`

## Problem

The Beginner journey is continuous through accepted Chapter 1 scene plans, but the
next projected action is not executable in the browser. `prepare-draft-handoff`
still points at `auteur draft <project> 1`, the projection advertises
`draft-chapter-1`, and the Beginner server exposes no corresponding command.

The existing post-draft review, revision-handoff, and explicit acceptance owners
are already browser/API reachable once candidate artifacts exist. The missing
responsibility is therefore the bridge that creates those candidate artifacts
from the already accepted Beginner planning state.

## Selected responsibility

Make Chapter 1 candidate production executable inside the normal Beginner
browser without changing narrative or persistence ownership.

The normal path becomes:

```text
accepted scene plans
-> prepare draft
-> generate candidate draft in app
-> review candidate
-> revise/retry in app when warranted
-> explicitly accept latest candidate
```

## Ownership and authority

- Accepted `StoryIdentity` remains Layer 1 authority.
- Accepted Whole-Story Structure, outline, chapter plan, and scene plans remain
  the inputs to Chapter 1 production.
- Bard and the existing critic runtime own prose generation and mechanical review.
- `draft_vN.md` and `validation_vN.json` are candidate/derived artifacts.
- `final.md` remains the accepted Chapter Expression.
- Drafting must never write `final.md` or record accepted Bible state.
- Explicit Chapter acceptance continues to delegate to the existing chapter
  acceptance owner.
- A successful critic pass is evidence, not author acceptance.
- Existing project-root ownership of story artifacts remains unchanged; the
  Beginner workspace id continues to scope session state, not a parallel story
  artifact model.

## Drafting contract

The Beginner drafting service:

1. requires an accepted foundation and accepted Chapter 1 scene plans;
2. compiles the already accepted `StoryIdentity` through existing
   `compile_to_blueprint`;
3. derives a Cartographer-compatible Chapter 1 outline from the accepted Chapter
   and Scene plans;
4. invokes the existing Bard and critic runtime;
5. writes exactly one new candidate draft version and matching validation report
   per author action;
6. never writes `final.md` and never records accepted Bible events;
7. on a later retry, supplies the previous candidate and findings to the Bard;
8. returns the workspace projection so the next action becomes review.

The draft service may use a noncanonical scratch Bible for critic context before
Chapter 1 acceptance. The existing chapter acceptance owner remains responsible
for materializing accepted Bible state.

If no provider-backed LLM client is configured, the browser receives a bounded
product error rather than a CLI command or silent fallback prose.

## Browser continuity

The visible continuation surface must stop rendering the developer CLI handoff.
It must expose `Draft Chapter 1` when the projection selects that action and
must treat `Review Chapter 1` as a browser review transition rather than an
unimplemented mutation command.

The existing post-draft revision handoff remains noncanonical. After recording
that handoff, the normal browser path must be able to generate the next
candidate draft without asking the author to execute a CLI retry.

## Projection and restart behavior

The workspace projection determines draft state from candidate artifacts:

- no candidate + prepared handoff -> `ready`;
- at least one `draft_vN.md` -> `drafted`;
- `final.md` created by explicit acceptance -> `accepted`.

An accepted Chapter 1 exposes no further Chapter 1 drafting action. Chapter 2
construction is outside this bounded goal.

Because draft/review/acceptance artifacts already persist on disk, reopening the
same Beginner session reconstructs the correct next action without manual
handoff.

## Failure handling

Relevant normal-use classifications:

- `CLI_ONLY_DEPENDENCY` — removed by in-app draft execution.
- `UI_INACCESSIBLE_CAPABILITY` — removed by binding the projected draft action.
- `PROJECTION_INTEGRATION_GAP` — removed by recognizing candidate rather than
  accepted artifacts as the drafted/reviewable state.
- `AUTHORITY_BOUNDARY_GAP` — prevented by candidate-only drafting and explicit
  acceptance.

## Validation

L1 should cover candidate-only drafting, no premature `final.md`, retry from a
previous candidate, projection state reconstruction, server command routing, and
browser removal of the visible CLI handoff.

L2 is warranted because this changes the browser -> server -> Bard/critics ->
post-draft -> authority-owner boundary. The smallest useful integration is the
scripted Beginner journey from accepted foundation through candidate review and
explicit Chapter 1 acceptance using an injected fake LLM.

Human prose-quality and usability judgment remain post-construction gates.

## Post-merge continuity correction

A post-merge journey re-check found that `draft-chapter-1` was present in the
server command registry and browser, but was omitted from the server's rich
command-dispatch set. The HTTP layer therefore attempted the legacy
`handler(command=envelope)` call shape even though
`draft_chapter_one(...)` requires `expected_session_version` and
`command_id`.

The repair adds `draft-chapter-1` to the same rich dispatch path as the other
continuation commands and adds a server-level regression that actually executes
candidate generation over HTTP and verifies that `draft_v1.md` /
`validation_v1.json` are created while `final.md` is still absent.

Durable lesson:

```text
registered action + rendered button
!= executable beginner continuity

real browser/API dispatch + owning workflow + preserved authority
= executable beginner continuity
```

Future cross-layer continuation changes should keep static browser wiring tests
as cheap sentinels, but they must also carry at least one focused executable
dispatch test for the changed boundary.

