# Beginner Chapter 1 Production Continuity

**Status:** Authorized for construction  
**Date:** 2026-09-25  
**Base:** `main @ c1c8e6e9e75fe7f9275e07b91aae7af6c530a9df`

## Problem

The Beginner journey is continuous through accepted Chapter 1 scene plans, but the
next projected action is not executable in the browser. `prepare-draft-handoff`
still points at `auteur draft <project> 1`, while the Beginner server exposes no
`draft-chapter-1` command. The post-draft API is also project-root scoped even
though Auteur Home now creates and reopens multiple workspace-owned stories.

This creates one bounded product discontinuity across otherwise existing owners:

```text
accepted scene plans
-> CLI-only drafting handoff
-> project-root post-draft endpoints
-> explicit chapter acceptance
```

## Selected responsibility

Make Chapter 1 production workspace-owned and reachable from the normal Beginner
browser without changing narrative authority.

The normal path becomes:

```text
accepted scene plans
-> prepare draft
-> generate candidate draft in the active workspace
-> review candidate
-> retry/revise when warranted
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

## State and persistence

Chapter production artifacts live under the active Beginner workspace root:

```text
.auteur/beginner/workspaces/<workspace_id>/
  story_identity.yaml
  chapters/01/
    outline.yaml
    draft_vN.md
    validation_vN.json
    final.md                # only after explicit acceptance
```

The browser and server address post-draft operations through the workspace id.
No raw workspace id is requested from the author; the browser already owns the
active workspace identity.

The operational Blueprint and Bible required by the existing chapter owner may
be materialized inside the workspace from already accepted state. They are
implementation artifacts, not new author decisions.

## Drafting contract

The Beginner drafting service:

1. requires an accepted foundation and accepted Chapter 1 scene plans;
2. compiles the accepted `StoryIdentity` through existing
   `compile_to_blueprint`;
3. derives a Cartographer-compatible Chapter 1 outline from the accepted Chapter
   and Scene plans;
4. invokes the existing Bard and critic runtime;
5. writes exactly one new candidate draft version and matching validation report
   per author action;
6. never writes `final.md` and never records accepted Bible events;
7. on a later retry, supplies the previous candidate and findings to the Bard;
8. returns the workspace projection so the next action becomes review.

If no provider-backed LLM client is configured, the browser receives a bounded
product error rather than a CLI command or silent fallback prose.

## Review, revision, and acceptance

Post-draft review, revision handoff, outcome, and acceptance are resolved against
the active workspace root. Review remains derived. Revision remains
noncanonical. Acceptance retains the existing explicit confirmation in the
browser and delegates to the chapter acceptance owner.

Chapter 2 continuation is not part of this construction goal. Existing
next-chapter capabilities may remain available internally, but the Chapter 1
journey is complete once `final.md` exists through explicit acceptance.

## Failure handling

Relevant normal-use classifications:

- `CLI_ONLY_DEPENDENCY` — removed by in-app draft execution.
- `UI_INACCESSIBLE_CAPABILITY` — removed by binding the projected draft action.
- `PROJECTION_INTEGRATION_GAP` — removed by projecting candidate artifacts as
  drafted/reviewable state.
- `PERSISTENCE_OR_RECOVERY_GAP` — removed by workspace-scoping chapter
  production and post-draft operations.
- `AUTHORITY_BOUNDARY_GAP` — prevented by candidate-only drafting and explicit
  acceptance.

## Validation

L1 should cover candidate-only drafting, no premature `final.md`, retry from a
previous candidate, server command routing, workspace-scoped post-draft routes,
and browser removal of the visible CLI handoff.

L2 is warranted because this changes the browser -> server -> drafting ->
post-draft -> authority-owner boundary. The smallest useful integration is the
scripted Beginner journey from accepted foundation through explicit Chapter 1
acceptance using an injected fake LLM and acceptance owner where necessary.

Human prose-quality and usability judgment remain post-construction gates.
