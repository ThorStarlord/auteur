---
id: 0004
title: Define the Decision Card contract
state: untriaged
priority: high
area: Decision-Oriented Tutor
filed-by: roadmap-author
opened: 2026-09-07
---

## Starting point

Production already has the Story Design Pack and Tutor V1 vocabulary, including derived `TutorGuidance` and deterministic, side-effect-free guidance generation. The Decision-Oriented Tutor needs a production contract for one author-decidable `DecisionCard`, presentation depth, deterministic card identity, and deterministic source fingerprints. There is no bug to reproduce for this issue.

If the repository already contains provisional types with these names, do not create duplicates. Audit the existing implementation against this issue and change only what is necessary to make the contract explicit, deterministic, and production-safe.

Reference implementation may be inspected READ-ONLY at commit 844fc84 (branch origin/codex/future-roadmap-implementation). Do NOT merge, checkout, or bulk-copy that branch. Port ONLY the subsystem named above; reimplement it adapted to the current production architecture.

M1 authority contract for every change in this issue:

- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- `tutor choose` records an advisory response and MUST NOT accept StoryIdentity, update blueprints, rewrite canon, or repair structure.
- Existing accepted/revisioned story authority remains the only story authority. No new Tutor type may invent a second canon or acceptance path.

Applicable M1 IN scope for this issue:

- `DecisionCard` typed contract.
- `TutorDepth` values: `recommend`, `explain`, `teach`, `challenge`, `quiz`.
- Deterministic Decision Card IDs.
- Deterministic source-fingerprint type/helper suitable for later stale-source checks.
- Focused model/identity tests for those contracts.

Tutor depth is presentation-only in M1. Changing depth must not change story meaning, canonical authority, or the semantic identity of an otherwise identical decision.

## What should exist

Implement or harden a small typed contract in the existing Story Design Pack/Tutor model surface. Prefer the existing `src/auteur/story_design_packs/models.py` and existing hashing conventions instead of creating a new subsystem.

A `DecisionCard` must be able to represent, at minimum:

- schema version;
- deterministic `card_id`;
- decision being made;
- orientation/context;
- why the decision matters;
- craft concept/principle;
- recommendation;
- alternatives;
- trade-offs;
- beginner trap/common failure;
- downstream consequences;
- evidence references;
- Story Design Pack provenance when present;
- presentation depth;
- optional source rule/diagnostic identifier;
- allowed advisory author actions;
- fixed authority status `DERIVED / NOT CANON`.

The contract must not contain methods that accept or mutate StoryIdentity, blueprints, structure proposals, or any other canonical artifact.

Deterministic card identity must satisfy all of the following:

- identical semantic inputs produce the same ID across repeated runs;
- JSON/dict key ordering does not affect the ID;
- a relevant semantic input change changes the ID;
- presentation-only depth does not change the semantic card ID;
- the ID is derived without filesystem, clock, random, network, or model side effects.

Define the semantic identity payload explicitly. It consists of `schema_version`,
`decision`, `orientation`, `why_it_matters`, `craft_concept`, `recommendation`,
`alternatives`, `tradeoffs`, `beginner_trap`, `downstream_consequences`,
`evidence`, `pack_sources`, and `source_rule`. It excludes `card_id`,
presentation-only `depth`, `author_actions`, and the fixed authority status.
Depth-only presentation changes must therefore preserve the same semantic ID.

Prevent in-place mutation of semantic fields after construction. If a different
presentation depth is needed, create an explicit presentation copy whose
semantic fields and `card_id` remain consistent; do not permit a mutable card to
silently diverge from its ID. Use a typed vocabulary for advisory
`author_actions` rather than accepting arbitrary strings.

Add a deterministic source-fingerprint helper/type for M1 consumers. It must accept a stable serialized/content representation and return a stable content fingerprint. Do not add session persistence here. A source-content change must yield a different fingerprint; identical source content must yield the same fingerprint.

Locally verifiable acceptance criteria:

- Add or update `tests/test_tutor_decision_cards.py` to cover the typed fields, fixed authority status, all five `TutorDepth` values, deterministic card IDs, depth-only ID stability, and relevant-input ID changes.
- Add focused tests for deterministic source fingerprints: same content -> same fingerprint; changed content -> changed fingerprint; mapping key order does not matter when the logical content is identical.
- Constructing a Decision Card or fingerprint must not create or modify `story_identity.yaml`, `blueprint.yaml`, structure proposal files, or other story artifacts in a temporary project.
- Existing Tutor V1 behavior remains green: `python -m pytest -q tests/test_story_design_pack_tutor.py tests/test_story_design_pack_golden_path.py`.
- Focused Decision Card tests pass: `python -m pytest -q tests/test_tutor_decision_cards.py`.
- Exact-head CI passes at the validation tier selected by the repository's risk-based validation policy; changes touching high-risk boundaries must pass the full supported Python matrix.
- Local verification stack passes: `python scripts/check.py --skip-pytest`.

Must-never-happen assertions:

- A `DecisionCard` must never become canon automatically.
- Constructing or serializing a `DecisionCard` must never accept StoryIdentity, update a blueprint, rewrite canon, or repair structure.
- Tutor depth must never change canonical state or semantic card identity.
- A source fingerprint must never infer narrative meaning or authority; it is content-currentness evidence only.
- A new Tutor model must never become a second story-authority or acceptance system.

## Why it matters

The Decision Card is the stable boundary between derived Tutor reasoning and explicit author decision-making. If its identity, provenance, source currentness, or authority semantics are ambiguous, later sessions and CLI commands can accidentally treat advice as story state. A small deterministic contract gives the rest of M1 a safe object to persist, render, compare for staleness, and test without crossing Auteur's established authority boundary.

## Out of scope for this issue

Do not implement or port any of the following:

- existing-guidance or diagnostic-to-card adapters;
- Tutor session persistence or session lifecycle;
- stale-session mutation/response handling;
- root `auteur tutor` CLI commands;
- StoryIdentity acceptance or any new acceptance path;
- structure application or automatic repair;
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
