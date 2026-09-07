---
id: 0006
title: Persist safe Tutor advisory sessions
state: untriaged
priority: high
area: Decision-Oriented Tutor
filed-by: roadmap-author
opened: 2026-09-07
---

## Starting point

Assumes issues < 0004 and < 0005 merged.

Production now has a deterministic, derived Decision Card and adapters from existing guidance/diagnostics. What is missing is a small local advisory-session lifecycle that can persist a card, remember which source fingerprints it was based on, detect when those sources change, and record an explicit author response without mutating narrative authority.

If provisional session code already exists on the branch, audit it against this contract rather than creating a parallel store.

Reference implementation may be inspected READ-ONLY at commit 844fc84 (branch origin/codex/future-roadmap-implementation). Do NOT merge, checkout, or bulk-copy that branch. Port ONLY the subsystem named above; reimplement it adapted to the current production architecture.

M1 authority contract for every change in this issue:

- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- `tutor choose` records an advisory response and MUST NOT accept StoryIdentity, update blueprints, rewrite canon, or repair structure.
- Session persistence records user interaction with advice only. It must not become a shadow canonical history.

Applicable M1 IN scope for this issue:

- `TutorSession` local model.
- Atomic JSON persistence under the project-local `.auteur` workspace.
- Source fingerprints from the merged Decision Card/fingerprint contract.
- Stale-session detection.
- Explicit responses: `choose`, `keep_unresolved`, `reject_finding`, `request_alternatives`.
- Session status sufficient to distinguish active, stale, and resolved advisory state.
- Focused persistence/lifecycle tests.

Tutor depth (`recommend`, `explain`, `teach`, `challenge`, `quiz`) remains presentation-only in M1. Session state may remember the card/depth shown, but it must not infer skill, modify story meaning, or change authority.

## What should exist

Implement or harden a local Tutor session service, preferably under `src/auteur/story_design_packs/session.py` if that matches current production layout.

A session must persist at least:

- schema version;
- deterministic or otherwise stable session ID derived without randomness when practical;
- Decision Card ID and serialized Decision Card;
- source fingerprint mapping captured when the session was created;
- lifecycle status (`active`, `stale`, `resolved` or equivalent);
- stale reason when stale;
- explicit response action and optional response value when one has been recorded.

Persistence requirements:

- Store sessions only beneath a project-local path such as `.auteur/tutor/sessions/`.
- Use atomic write semantics: write a temporary file in the target directory, flush/fsync where the repository's persistence conventions require it, then replace the target atomically.
- Clean temporary files on success and on handled failure.
- Loading/inspecting a stale session remains allowed.
- Comparing current source fingerprints to stored fingerprints marks the session stale when any relevant source differs.
- Once stale, the session must not silently return to active merely because a later call omits current fingerprints. Explicit regeneration should create a fresh card/session instead of reviving stale advice.

Response rules:

- Only actions allowed by the card and M1 contract may be recorded.
- `choose`, `keep_unresolved`, and `reject_finding` resolve the advisory session.
- `request_alternatives` may remain active, but it records only a request; it does not synthesize or apply new story content here.
- Any substantive response to a stale session (`choose`, `keep_unresolved`, `reject_finding`, `request_alternatives`) must fail closed with a clear error.
- Recording a response changes only the Tutor session file.

Stale protection is a service-level invariant, not a caller convention:
`record_response()` must establish currentness itself before accepting any
response. If a session has source bindings/fingerprints and current source
evidence is absent, incomplete, malformed, or cannot be resolved, the service
must fail closed. Callers must not be able to bypass this by calling
`record_response()` directly or by omitting a refresh step.

Locally verifiable acceptance criteria:

- Add or update `tests/test_tutor_session.py` for create/save/load round-trip, stable source fingerprints, stale detection, allowed response actions, resolved status, and stale-response rejection.
- Add an atomic-write failure test using a temporary directory and a controlled failure (for example monkeypatching the replace step) that proves an existing valid session file is not corrupted and temporary files are cleaned up.
- Create sentinel `story_identity.yaml` and `blueprint.yaml` files in a temporary project; after create/save/refresh/record-response operations their bytes must be unchanged.
- A stale session remains inspectable but every substantive response action is rejected.
- An unknown/disallowed response action is rejected instead of being persisted as arbitrary session state.
- Focused tests pass: `python -m pytest -q tests/test_tutor_session.py tests/test_tutor_decision_cards.py`.
- Existing Tutor/Story Design Pack regressions pass: `python -m pytest -q tests/test_story_design_pack_tutor.py tests/test_story_design_pack_golden_path.py`.
- Exact-head CI passes at the validation tier selected by the repository's risk-based validation policy; changes touching high-risk boundaries must pass the full supported Python matrix.
- Local verification stack passes: `python scripts/check.py --skip-pytest`.

Must-never-happen assertions:

- A Tutor session must never become canonical story state.
- Saving or responding to a Tutor session must never accept StoryIdentity, update a blueprint, rewrite canon, create a structure repair, or apply a diagnostic recommendation.
- A stale session must never accept `choose`, `keep_unresolved`, `reject_finding`, or `request_alternatives`.
- A missing freshness check must never silently convert a stale session back to active.
- Session storage must never overwrite canonical files or store itself outside the local `.auteur` advisory area.
- A response value must never be interpreted as an accepted story transformation.

## Why it matters

A decision-oriented Tutor becomes dangerous if yesterday's advice can be acted on after the story changed, or if recording a response silently crosses into story authority. Atomic, source-aware, local sessions let Auteur remember an advisory interaction while making currentness and authority explicit. They also give the CLI a safe persistence layer without inventing a new canon system.

## Out of scope for this issue

Do not implement or port any of the following:

- root `auteur tutor` parser/CLI workflow;
- automatic alternative generation;
- StoryIdentity acceptance or any new acceptance path;
- blueprint/structure mutation;
- automatic diagnostic repair;
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
- prose generation changes.
