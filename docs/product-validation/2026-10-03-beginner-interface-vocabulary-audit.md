# Beginner Interface Vocabulary Audit & Translation Pass

**Date:** 2026-10-03  
**Scope:** user-facing Browser UI, Guided Author Workspace, CLI help/output, prompt-facing copy, and human-readable formatters  
**Source baseline:** `feat/beginner-ergonomics-compression @ 952e8c5e2f47eeb04276e18f039cef43ba48bc15`  
**Patch branch:** `fix/beginner-vocabulary-translation`

Line numbers below refer to the **pre-patch baseline** so the audit remains stable after copy changes shift the files.

## Translation rule

Keep backend vocabulary precise; translate only the front door.

```text
internal contract / command / field name
-> remains stable

human-facing help / heading / status / error
-> translated into story-craft language
```

This pass deliberately does **not** rename compatible CLI commands such as
`ontology`, `reconcile`, or `accept-candidate`, nor backend identifiers such
as `candidate_id`, `reconciliation_status`, `canonical_refs`,
`DraftReviewProjection`, or `StoryIdentity`.

## Jargon audit

| File & baseline line | Current jargon | Plain-English translation |
|---|---|---|
| `src/auteur/beginner/browser/app.js:1319` | Will become canonical | Will become part of the accepted story |
| `src/auteur/beginner/browser/app.js:1320` | May contribute to canon | May shape the accepted story |
| `src/auteur/beginner/browser/app.js:1321` | context / provenance | supporting context |
| `src/auteur/beginner/browser/app.js:1322` | provenance | source history |
| `src/auteur/beginner/browser/app.js:1473` | internal artifacts | planning details |
| `src/auteur/beginner/browser/app.js:1616` | DERIVED / NOT CANON | WORKING / NOT ACCEPTED |
| `src/auteur/beginner/browser/app.js:1677` | Chapter candidate prose | Chapter draft prose |
| `src/auteur/beginner/browser/index.html:157` | Reconciliation | Story updates |
| `src/auteur/beginner/browser/index.html:158` | Next owning command | Next technical action |
| `src/auteur/ui/workspace.py:15,192` | DERIVED WORKSPACE / READ ONLY | READ-ONLY STORY VIEW |
| `src/auteur/ui/workspace.py:21` | Explicit authority action | Confirm the change |
| `src/auteur/ui/workspace.py:49` | where authority lives | which decisions need you |
| `src/auteur/ui/workspace.py:146` | Workspace projection failed | Workspace view failed |
| `src/auteur/ui/author_attention.py:134,147` | LOCAL / NONCANONICAL | ADVICE ONLY / NOT PART OF STORY YET |
| `src/auteur/ui/author_attention.py:173-174` | noncanonical proposal / NONCANONICAL PROPOSAL | suggested story change / SUGGESTED CHANGE |
| `src/auteur/ui/author_attention.py:187` | NONCANONICAL PROPOSAL / NOT APPLIED | SUGGESTED CHANGE / NOT APPLIED |
| `src/auteur/ui/author_attention.py:229` | explicit authority action | confirm it |
| `src/auteur/cli_formatters.py:487` | candidates | story options |
| `src/auteur/cli_formatters.py:526-534,557` | Layer N; Target Experience; Promise/Constraints; Structural Forces; Carriers; Modulation | Reader experience; Story promises & limits; Core conflict; Characters & story elements; Pacing & intensity |
| `src/auteur/cli_formatters.py:603` | Recovery candidate layers ... blueprint and bible | recovered story choices ... story setup and continuity notes |
| `src/auteur/cli_handlers.py:596` | canonical StoryIdentity genre | accepted story setup |
| `src/auteur/cli_handlers.py:645` | not canon | not accepted story facts |
| `src/auteur/cli_handlers.py:2031` | Canonical Reference Manual | Accepted Story Reference |
| `src/auteur/cli_handlers.py:2130` | candidate_locked_layers / candidate_locked_state | story choices to restore |
| `src/auteur/cli_handlers.py:2193` | Recovery merge validation failed. Transaction rolled back. | recovered story changes could not be applied safely; nothing changed |
| `src/auteur/cli_parser.py:149` | structural revision ... reconcile | story-structure change ... review downstream effects |
| `src/auteur/cli_parser.py:175` | Reconcile impact and freshness | Review downstream story effects |
| `src/auteur/cli_parser.py:284` | non-canonical Story Discovery brief | Story Discovery brief not part of the accepted story yet |
| `src/auteur/cli_parser.py:292` | StoryIdentity candidates / architectural comparison | story-setup options / creative tradeoffs |
| `src/auteur/cli_parser.py:313` | promote a Story Discovery candidate | accept a Story Discovery option as the story setup |
| `src/auteur/cli_parser.py:387` | recovery locked layers / canonical state | recovered story choices / accepted story |
| `src/auteur/cli_dispatch.py:835` | Impact reconciliation | Story impact review |
| `src/auteur/cli_dispatch.py:967-973` | candidate data / Story Discovery candidates | story option data / Story Discovery options |
| `src/auteur/cli_dispatch.py:981,986,998,1004,1014` | Candidate / parse candidate / promoted candidate | Story option / read story option / selected story option |
| `src/auteur/cli_dispatch.py:1024` | discovery provenance | discovery history |
| `src/auteur/cli_dispatch.py:1216-1266` | candidate file/hash/directory / promote candidate | story option file/check/folder / accept story option |
| `src/auteur/cli_dispatch.py:1322` | state canon failed | accepted story reference failed |
| `src/auteur/expression/cli.py:77-112` | Scene Realization prose candidates / prose candidate | scene drafts / scene draft from the current scene plan |
| `src/auteur/expression/cli.py:175-264` | Book reconciliation / Book candidate / noncanonical / canonical | Book change review / working Book version / not accepted yet / accepted version |
| `src/auteur/expression/cli.py:269-341` | Chapter manuscript reconciliation / reconciliation proposals / candidates | Chapter change review / suggested story updates / working versions |
| `src/auteur/expression/formatters.py:51` | Candidate | Scene draft |
| `src/auteur/expression/formatters.py:134-418` | Reconciliation application/publication/inspection; canonical artifacts; candidates | Change application/prepared change set/change review; accepted story material; working versions |
| `src/auteur/expression/formatters.py:441-963` | Book candidate; Book reconciliation; noncanonical; Canonical; Reconciliation completed | Working Book version; Book change review; not accepted yet; Accepted; Change review completed |
| `src/auteur/convergence/cli.py:43-70` | candidates / candidate realization / reconciliation proposal | working scene versions / working scene version / story-update proposal |
| `src/auteur/convergence/cli.py:148-408` | Candidates / Generated candidate / Reconciliation Proposal | Working versions / Generated working version / Story Update Proposal |
| `src/auteur/narrative_ontology/cli_ontology.py:22,46,63` | narrative ontology / concepts in ontology / validate ontology | story concept library / story concepts / check the story concept library |
| `src/auteur/narrative_ontology/cli_ontology.py:162-204,268` | ontology validation / ontology metadata | story concept check / story concept library |
| `src/auteur/genre_packs/cli.py:81-110` | recommendation candidate / StoryIdentity | recommendation option / story setup |
| `src/auteur/impact/cli.py:126` | Needs reconcile | Needs story update review |
| `src/auteur/roundtrip/cli.py:114` | canon update proposals | accepted-story update suggestions |
| `src/auteur/universe/cli.py:29-31` | canonical universe_identity / Canonical output path | accepted universe setup / Accepted universe setup output path |
| `src/auteur/series/vertical_slice_formatters.py:199,300` | Book canon | accepted Book |
| `src/auteur/series/vertical_slice_formatters.py:501` | narrative authority | accepted story material |

## Machine-status translation

The Beginner whole-book API still returns stable backend values such as
`partially_reconciled` and `DERIVED / NOT CANON`. The Browser now translates
those values at render time instead of changing the backend contract:

| Backend value | Beginner surface |
|---|---|
| `not_started` | not started |
| `reconciled` | up to date |
| `partially_reconciled` | partly updated |
| `divergent` | needs review |
| `abandoned` | stopped |
| `superseded` | replaced by a newer update |
| `DERIVED / NOT CANON` | WORKING / NOT ACCEPTED |

## Terms intentionally retained

These remain unchanged because they are stable command/API identifiers rather
than explanatory UI copy:

- `auteur ontology ...`
- `auteur expression reconcile ...`
- `auteur ... accept-candidate`
- `candidate_id`
- `canonical_refs`
- `reconciliation_status`
- `DraftReviewProjection`
- `StoryIdentity`
- serialized JSON status/enumeration values

Beginner-facing explanations around those identifiers are translated.

## Resulting vocabulary

The primary human vocabulary after this pass is:

- **Story setup**
- **Story direction**
- **Story shape**
- **Scene plan**
- **Scene draft / Chapter draft**
- **Accepted story / accepted version**
- **Working version**
- **Story updates / change review**
- **Story concept library**
- **Source history**
- **Confirm the change**

The product can therefore keep precise internal architecture without requiring a
beginner to learn that architecture merely to write.
