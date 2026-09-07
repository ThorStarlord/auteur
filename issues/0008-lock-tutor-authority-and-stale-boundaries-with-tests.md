---
id: 0008
title: Lock Tutor authority boundaries with tests
state: untriaged
priority: high
area: Decision-Oriented Tutor
filed-by: roadmap-author
opened: 2026-09-07
---

## Starting point

Assumes issues < 0004 through < 0007 merged.

The production M1 path now has Decision Cards, adapters, local advisory sessions, stale-source handling, and the root `auteur tutor` workflow. This issue is a boundary-test lap: turn the architectural invariants into regression tests that fail if later work accidentally promotes advice into canon or lets stale sessions act on obsolete story state.

Do not redesign M1 in this issue. If a new death test exposes a bounded defect inside the already-merged M1 behavior, make the smallest production fix required to satisfy the invariant and keep the test. Do not expand product scope.

Reference implementation may be inspected READ-ONLY at commit 844fc84 (branch origin/codex/future-roadmap-implementation). Do NOT merge, checkout, or bulk-copy that branch. Port ONLY the subsystem named above; reimplement it adapted to the current production architecture.

M1 authority contract for every change in this issue:

- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- `tutor choose` records an advisory response and MUST NOT accept StoryIdentity, update blueprints, rewrite canon, or repair structure.
- Deterministic evidence, user selection, and session resolution do not grant story authority.

Applicable M1 IN scope for this issue:

- Regression/death tests for Decision Card authority.
- Regression/death tests for adapter side effects.
- Regression/death tests for Tutor session locality, atomicity, and staleness.
- Regression/death tests for root CLI authority and stale-session blocking.
- Regression tests that existing Story Design Pack, Story Discovery, Structure diagnostic, and Genre Pack behavior remains intact.
- Minimal M1-only fixes if a required test exposes a real defect.

Tutor depth (`recommend`, `explain`, `teach`, `challenge`, `quiz`) is presentation-only in M1 and must be tested as such.

## What should exist

Strengthen the M1 tests so the following invariants are executable rather than only documented.

Canonical-mutation fixture:

- In a temporary project, create sentinel canonical/authoritative files before invoking Tutor behavior. At minimum include a non-empty `story_identity.yaml` and `blueprint.yaml`; include existing structure proposal/application paths if the current test helpers make that practical.
- Record bytes or hashes before the operation.
- Exercise Decision Card creation, guidance/diagnostic conversion, session save/load/refresh, and root CLI `next`, `explain`, `show`, and `choose`.
- Assert the authoritative files are byte-identical afterward.
- Assert only expected local `.auteur/tutor/...` advisory files may change when persistence is requested.

Required death-test coverage:

1. Decision Card construction cannot become canon automatically.
2. Tutor session persistence cannot modify StoryIdentity.
3. `tutor choose` cannot accept/promote StoryIdentity.
4. `tutor choose` cannot update a blueprint or apply a structure proposal.
5. Diagnostic-to-card conversion cannot repair Structure automatically.
6. A stale session cannot record `choose`.
7. A stale session cannot record `reject_finding`.
8. A stale session cannot record `keep_unresolved`.
9. A stale session cannot record `request_alternatives`.
10. Regenerating or re-rendering advice cannot mutate accepted story state.
11. Identical semantic Decision Card inputs produce the same ID.
12. A relevant semantic input change changes the card ID and/or relevant source fingerprint so obsolete sessions can be detected.
13. Changing only Tutor depth does not change the semantic card ID or canonical state.
14. Existing Story Design Pack CLI still works.
15. Existing Story Discovery candidate/acceptance path still owns StoryIdentity acceptance; Tutor code does not bypass it.
16. Existing Genre Pack recommendation/acceptance behavior still works and is not rerouted through Tutor sessions.

Prefer extending the focused files already associated with M1 (`tests/test_tutor_decision_cards.py`, `tests/test_tutor_session.py`, `tests/test_story_design_pack_cli.py`) plus the smallest new boundary-focused test file only if that makes the fixtures substantially clearer.

Locally verifiable acceptance criteria:

- All must-never-happen assertions above are represented by explicit tests, not comments only.
- At least one test drives the real root CLI path end-to-end against sentinel canonical files.
- At least one test drives a real existing structure diagnostic through the Decision Card adapter and proves no repair/application artifact is created.
- At least one test demonstrates source change -> stale session -> all substantive response actions rejected.
- At least one test demonstrates missing, incomplete, or unresolvable current
  source evidence -> fail-closed response rejection, even when
  `record_response()` is called directly without a prior refresh.
- At least one test demonstrates depth-only presentation change keeps the semantic Decision Card identity stable.
- Focused M1 suite passes: `python -m pytest -q tests/test_tutor_decision_cards.py tests/test_tutor_session.py tests/test_story_design_pack_cli.py tests/test_story_design_pack_tutor.py tests/test_story_design_pack_golden_path.py`.
- Story Discovery regressions pass: `python -m pytest -q tests -k "story_discovery"`.
- Genre Pack regressions pass: `python -m pytest -q tests -k "genre_pack"`.
- Exact-head CI passes at the validation tier selected by the repository's risk-based validation policy; changes touching high-risk boundaries must pass the full supported Python matrix.
- Local verification stack passes: `python scripts/check.py --skip-pytest`.

Must-never-happen assertions:

- DecisionCard cannot become canon automatically.
- TutorSession cannot modify StoryIdentity or any accepted artifact.
- `tutor choose` cannot accept StoryIdentity, update blueprints, rewrite canon, or repair structure.
- Diagnostic advice cannot apply itself.
- A stale session cannot accept any substantive response action.
- Regenerating advice cannot mutate accepted story state.
- Currentness/fingerprint evidence cannot be interpreted as narrative causality, correctness, or authority.
- Existing author acceptance paths cannot be replaced, wrapped, or silently bypassed by Tutor code.

## Why it matters

The most damaging M1 regressions would not look like crashes; they would look like convenient behavior that quietly collapses advice into authority. These tests make Auteur's core separation executable: derived guidance can be deterministic and useful while still remaining noncanonical, and stale advice can be inspected without being acted on. This is the safety net needed before treating the Decision-Oriented Tutor as normal production infrastructure.

## Out of scope for this issue

Do not implement or port any of the following:

- new Tutor features or commands;
- new Decision Card fields unless strictly required to express an existing M1 invariant;
- automatic StoryIdentity acceptance;
- blueprint/structure mutation or repair automation;
- epistemic state;
- character trajectories;
- relationship trajectories;
- promise/payoff reasoning;
- causal graph;
- counterfactual reasoning;
- Series context reconstruction;
- new Story Design Pack kinds;
- new Story Design Packs;
- learning progression or adaptive curriculum;
- experiment tooling or experiment execution;
- reasoning-report productionization;
- GUI/workspace work;
- prose generation changes;
- remote CI, wheel qualification, or installed-wheel smoke work.
