# Beginner Workspace Agent-Simulated Qualification

Status: **AUTOMATED GATE PASSES, HUMAN GATE PENDING — slice NOT qualified,
NOT release-ready.** This file records an agent-simulated walkthrough plus
bounded automated evidence only. It is NOT a human walkthrough, NOT a human
qualification, and NOT release evidence. It does not touch release evidence
files or `v1.0-qualification-record`.

## Scope

- Candidate SHA: `749e5a2ec9adbf778a493c0987697e449df2ef88`
- Worktree: `H:\GithubRepositories\auteur\.worktrees\beginner-workspace-vslice`
  (linked worktree; git common dir `H:/GithubRepositories/auteur/.git`,
  branch `codex/beginner-workspace-vslice`)
- Pre-existing working-tree modification at evidence time: `M uv.lock`
  (not made by this task; this task stages and commits only the new file
  created here).
- Driver: `BeginnerWorkspaceApplication` (`src/auteur/beginner/application.py`)
  plus fixture `tests/fixtures/beginner_sealed_elevator.py`, run with
  `PYTHONPATH=<worktree>;<worktree>\src` (both entries required: repo root
  for `tests.*`, `src` for `auteur.*`).
- In scope: sealed-elevator Discover -> Direction -> Identity -> Structure
  walk (one cancelled revision, one accepted revision), plus a second
  Mystery workspace on a different author-supplied premise (transfer check).
- Out of scope: browser screenshots, human usability judgment, release
  qualification, any claim about prose/drafting quality.

## Automated gate (exact counts)

Focused qualification file `tests/test_beginner_workspace_qualification.py`:

| Category | Count |
|---|---:|
| collected | 8 |
| passed | 8 |
| skipped | 0 |
| xfailed | 0 |
| xpassed | 0 |
| failed | 0 |
| errors | 0 |

Result: `8 passed in 30.27s`. Focused tests pass (only the named file).

Reconciliation evidence — current `origin/main` baseline `3001b3543bd7bf31483cd2609b788121e5270a82`:

- Historical #228 CLI failures were reproduced from the archived CI run but
  did not reproduce on current main; no baseline repair was committed.
- Current-main L1 CLI/tutor boundary slice: 99 passed.
- Current-main repository checks: 25 validator cases passed and
  repo/release-scope/vendored-contract checks passed. Full-repository Ruff
  reports four known baseline findings in untouched `cli_formatters.py` and
  `ui/workspace.py`; changed-path Ruff passed for the recovery fix.
- Post-recovery full-suite L3 checkpoint: 4,857 collected, 4,829 passed,
  1 skipped, 27 documented xfailed, 0 xpassed, 0 failed, and 0 errors.

Reconciled feature regression set — beginner (`test_beginner_workspace_server`,
`test_beginner_workspace_qualification`,
`test_beginner_workspace_persistence`,
`test_beginner_workspace_contracts`,
`test_beginner_workspace_browser`,
`test_beginner_workspace_authority`,
`test_beginner_workspace_application`,
`test_beginner_mystery_adapter`) + genre_pipeline (cli, identity,
registry, runtime, server, session, templates, validation) +
`test_structure_freshness` + `test_acceptance_registry`:

| Category | Count |
|---|---:|
| collected | 196 |
| passed | 195 |
| skipped | 1 |
| xfailed | 0 |
| xpassed | 0 |
| failed | 0 |
| errors | 0 |

Result: `195 passed, 1 skipped`. The single skip is
`tests\test_beginner_workspace_persistence.py:761` (symlinked-workspace
escape test): symlink creation unavailable on this Windows host
(`WinError 1314`, missing privilege) — environment limitation, not a
product failure. No full-suite run was attempted, so no timeout applies;
evidence is bounded to the listed files and was rerun after reconciliation
with current main.

Ruff on the created file: not applicable (markdown, no Python changed) —
skipped.

## Agent-simulated walkthrough (NOT human)

Everything below is labelled AGENT-OBSERVED: projections read from live
`app.projection()` output by a coding agent driving the documented command
contracts, not by a human author. Guidance inventory is fixed (10 cards:
3 `discover.*`, 4 `story_identity.*`, 3 `structure.*`; see Transfer check
for card list). All selections below used each card's guided recommendation.

### Stage 1 — Discover start (AGENT-OBSERVED)

- Where am I: card `discover.story-experience`, stage `discover`,
  `session_version` 1. Navigator: discover working/available 0-of-3,
  identity not_started/locked, structure not_started/locked.
- What matters now: "Which mystery experience or lens should the story
  promise?"
- Why: why_this_matters names the sealed-elevator premise
  ("This decision determines how the story's central question operates for
  'A sealed elevator opens on an empty shaft.'"); principle: "The genre
  contract tells the reader what kind of investigation to expect."
- Options: Detective procedural / Police/investigation procedural /
  Locked-room puzzle / Intricate puzzle structure; recommendation
  "Detective procedural"; selected none.
- Consequences: downstream "The selected genre contract determines the
  investigation mode presented to the reader."; warnings contrast
  procedural vs puzzle lens; blockers list unanswered counts for all
  three stages.
- Working vs canonical: canonical empty; no tensions; no active revision.
- Next action: no review available on any stage; answer the 3 discover
  cards.

### Stage 2 — Discover answered (AGENT-OBSERVED)

- Where am I: card `discover.investigation-approach` (cursor = last
  answered card), `session_version` 6. Navigator: discover
  complete/available 3-of-3, review available, ready to accept.
- What matters now: "Which investigation approach should guide the
  inquiry?"
- Why: premise-specific why_this_matters; principle: "The
  investigation-style phase defines how the inquiry proceeds."
- Options: Logical deduction / Intuitive investigation / By-the-book
  procedure; recommendation "Logical deduction"; selected
  "Logical deduction".
- Consequences: downstream names the deduction/intuition/procedure fork;
  discover blockers empty; identity/structure still list unanswered
  counts.
- Working vs canonical: canonical still empty (answering is working
  state only); no tensions.
- Next action: discover review available and ready — open milestone
  review, then accept story direction. Review-open changed only
  `opened: true`; all other fields identical (observed).

### Stage 3 — Direction accepted (AGENT-OBSERVED)

- `accept_story_direction` returned `accepted=True, revision=1`.
- Where am I: cursor moved to `story_identity.protagonist-want`,
  `session_version` 8. Navigator: discover complete/available (review
  still open), identity working/available 0-of-4, structure still locked.
- Question: "Which practical investigation want should drive the
  protagonist?"; recommendation "Want: Solve the puzzle".
- Working vs canonical: canonical now `["story_direction"]`; exactly one
  stage unlocked (identity), structure still locked — matches the
  never-unlock-more-than-next-stage contract.
- Next action: answer the 4 identity cards.

### Stage 4 — Identity answered and accepted (AGENT-OBSERVED)

- Answered (`session_version` 15): cursor `story_identity.truth-opposition`,
  "Which resistance should protect the hidden truth?", recommendation
  "Resistance: Misleading clues", selected accordingly; identity
  review available and ready; structure blockers list 3 unanswered.
- `accept_story_identity` returned `accepted=True, revision=1`
  (`session_version` 17); canonical
  `["story_direction", "story_identity"]`; structure unlocked to
  working/available 0-of-3, cursor `structure.investigation-disruption`
  ("What pacing rhythm should govern the investigation's disruption?",
  recommendation "Steady rhythm of discovery").

### Stage 5 — Structure answered and accepted (AGENT-OBSERVED)

- Answered (`session_version` 22): cursor `structure.final-revelation`,
  "How directly should the final revelation follow from the clues?",
  recommendation "Solution is one of several reasonable readings",
  selected accordingly; all stage blockers empty; all reviews ready.
- `accept_whole_story_structure` returned `accepted=True, revision=1`
  (`session_version` 24); canonical
  `["story_direction", "story_identity", "whole_story_structure"]`;
  structure lifecycle COMPLETE, `answered == total == 3`,
  `review_available`/`ready_to_accept` true, `stale` false,
  `at_risk_if_accepted` false.

### Revision 1 — Cancelled (AGENT-OBSERVED)

- Opened `rev-cancel-1` (`session_version` 26), set an exploratory
  alternative on `structure.investigation-disruption`. Projection:
  revision `("rev-cancel-1", True, [])` — active exploration but EMPTY
  at-risk list (single-stage touch marks nothing downstream at risk);
  one nonblocking tension on the touched card; canon unchanged.
- `cancel_revision` (`session_version` 27): canon JSON byte-identical
  before/after (`CANCEL_IDENTICAL:True`), canonical refs equal,
  revision `(None, False, [])`, tensions empty, all navigator entries
  `at_risk_if_accepted` false and `stale` false.

### Revision 2 — Accepted (AGENT-OBSERVED)

- Opened `rev-accept-1`, set exploratory alternative on
  `story_identity.protagonist-want`. Projection pre-accept:
  revision `("rev-accept-1", True, ["story_structure"])` — structure
  flagged at-risk while nothing marked stale (preview risk without
  staleness, as contracted).
- `accept_revised_story_identity` returned `accepted=True, revision=2`;
  identity refs show revisions `[1, 2]` (provenance preserved);
  revision cleared; structure `stale=True`, `at_risk_if_accepted=False`.
- Agent-observed nuance (see Friction log 2): post-accept, ALL three
  stages rendered lifecycle BLOCKED with blocker "Materially stale
  assumptions: reassess guidance before accepting" and `stale=True`,
  not only downstream structure. Canon held 4 refs
  (`story_direction`, `story_identity`, `whole_story_structure`,
  `story_identity` rev 2).

## Transfer check

Second workspace `lighthouse-keeper`, author-supplied premise "A
lighthouse keeper vanishes during a storm, leaving the lamp lit.",
`guidance_genre` mystery — same grammar, different content:

- Card inventory identical: 10 cards, same IDs in the same three
  prefixes (`discover`: story-experience, personal-stakes,
  investigation-approach; `story_identity`: protagonist-want,
  relationship-pressure, information-contract, truth-opposition;
  `structure`: investigation-disruption, clue-distribution,
  final-revelation), same options and recommendations. Only the
  `why_this_matters` premise interpolation changed.
- Start projection structurally identical to sealed-elevator start
  (same navigator shape, same questions/options; `session_version` 1).
- Full journey completed on the transfer premise: direction accepted
  rev 1, identity accepted rev 1, structure accepted rev 1; canonical
  `['story_direction', 'story_identity', 'whole_story_structure']`.
- Transfer verdict (agent-observed): interaction grammar is
  premise-independent; premise text flows only into content fields.
  Bounded: transfer exercised acceptance only, not revision flows.

## Friction log (agent-as-user confusion)

1. Command envelope duality: journey commands accept either a
   `MutationCommand` envelope or keyword args. The projection does not
   document the grammar; the agent had to read the fixture
   (`command_for`) to build envelopes, and the first driver attempt
   failed with `ModuleNotFoundError: No module named 'tests'` until
   both repo root and `src` were on PYTHONPATH.
2. Stale scope after accepted revision broader than "downstream": all
   stages (including already-accepted discover) flipped to BLOCKED/stale
   with "Materially stale assumptions". The agent could not tell from
   projection data alone whether this is intended global digest
   invalidation or over-invalidation. Recorded as observed, not judged.
3. "Where am I" needs two fields: post-acceptance the focused
   `decision_card` still shows the last answered card while the
   navigator `current_card_id` is None. Neither surface alone answers
   orientation; the agent had to join them.
4. `LifecycleStatus.COMPLETE` is ambiguous: it means both "review
   available and ready" (pre-acceptance) and "canonically accepted".
   Distinguishing required cross-checking `canonical_refs`, not the
   lifecycle value.
5. Cursor shows the last answered card rather than the next unanswered
   one at stage completion (e.g. `discover.investigation-approach` after
   all 3 answered). The agent initially misread this as "one card left"
   until checking `answered == total` on the navigator entry.
6. Card order for answering is not surfaced by the projection; the agent
   relied on the fixture helper (`choose_required_options` answers in
   inventory order with `continue_decision` between cards).

## Bounded status

- AUTOMATED GATE: PASSES for the listed files (focused 8/8; regression
  set 270 passed + 1 environment-skipped, 0 failed, 0 errors).
- HUMAN GATE: PENDING — no human walkthrough or usability judgment was
  performed or claimed.
- This slice is NOT qualified and NOT release-ready. The walkthrough
  above is agent-simulated evidence only, bounded to the Mystery adapter
  and the two premises exercised.
