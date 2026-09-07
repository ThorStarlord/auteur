---
id: 0005
title: Convert existing guidance into Decision Cards
state: untriaged
priority: high
area: Decision-Oriented Tutor
filed-by: roadmap-author
opened: 2026-09-07
---

## Starting point

Assumes issues < 0004 merged.

Production already has derived `TutorGuidance`, `TutorDiagnosticGuidance`, Story Design Pack provenance, and deterministic structure diagnostics. The merged Decision Card contract is now the author-facing envelope, but existing guidance and diagnostics still need narrow, side-effect-free adapters into that envelope.

Reference implementation may be inspected READ-ONLY at commit 844fc84 (branch origin/codex/future-roadmap-implementation). Do NOT merge, checkout, or bulk-copy that branch. Port ONLY the subsystem named above; reimplement it adapted to the current production architecture.

M1 authority contract for every change in this issue:

- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- `tutor choose` records an advisory response and MUST NOT accept StoryIdentity, update blueprints, rewrite canon, or repair structure.
- Existing accepted/revisioned story authority remains the only story authority. Adapters may translate evidence and recommendations; they may not promote either into canon.

Applicable M1 IN scope for this issue:

- Adapter from existing `TutorGuidance` to `DecisionCard`.
- Adapter from existing deterministic structure diagnostics / diagnostic Tutor guidance to `DecisionCard`.
- Preservation of existing pack provenance, evidence, alternatives, trade-offs, consequences, and diagnostic rule identity.
- Focused adapter tests.

Tutor depth (`recommend`, `explain`, `teach`, `challenge`, `quiz`) is presentation-only in M1. Adapters may set or accept a depth for rendering, but depth must not change the underlying recommendation, evidence, story meaning, or canonical authority.

## What should exist

Add or harden narrow conversion functions in the existing Tutor surface, preferably `src/auteur/story_design_packs/tutor.py` unless current production architecture provides a better existing home.

For existing `TutorGuidance` -> `DecisionCard` conversion:

- preserve the original decision and orientation;
- map the craft concept/principle without inventing new story facts;
- preserve the recommendation, alternatives, trade-offs, beginner failure/trap, and consequence;
- preserve Story Design Pack provenance exactly;
- carry existing architecture evidence into card evidence;
- use the merged deterministic card-ID contract rather than local ad hoc hashing;
- remain side-effect-free;
- leave the source guidance object unchanged.
- preserve a resolvable source binding alongside human-readable evidence. The
  binding must identify the source artifact/subject and carry the deterministic
  current fingerprint (or the repository's equivalent typed reference), so the
  later session service can recompute freshness. Free-text evidence alone is
  insufficient, and adapters must not trust an opaque caller-supplied hash as
  proof of currentness.

For deterministic diagnostic -> `DecisionCard` conversion:

- preserve the diagnostic rule/source identifier;
- preserve the diagnostic message as the reason the decision matters;
- represent repair options as advisory recommendation/alternatives, never as applied changes;
- carry structured diagnostic evidence when available;
- include explicit author actions appropriate for a finding: `choose`, `keep_unresolved`, `reject_finding`, `request_alternatives`;
- when no repair option exists, recommend inspection/review rather than fabricating a repair;
- remain side-effect-free and leave the diagnostic unchanged.
- preserve the same resolvable source binding for diagnostic inputs, including
  the source artifact/subject and deterministic current fingerprint needed by
  later stale checks.

Do not add adapters for prototype-only reasoning reports, promise/payoff models, epistemic findings, causal graphs, counterfactuals, or Series context in this issue.

Locally verifiable acceptance criteria:

- Add or update `tests/test_tutor_decision_cards.py` with at least one real existing `TutorGuidance` conversion and one real existing structure-diagnostic conversion.
- Guidance conversion preserves `pack_sources`, evidence, recommendation, alternatives, and `DERIVED / NOT CANON`.
- Diagnostic conversion preserves rule identity and available evidence and exposes advisory author actions including `reject_finding`.
- Both adapters leave their input objects byte/structure-equivalent to their pre-conversion state.
- Running either adapter against a temporary project must not create or modify `story_identity.yaml`, `blueprint.yaml`, structure proposals, or accepted artifacts.
- Existing Tutor regressions pass: `python -m pytest -q tests/test_story_design_pack_tutor.py tests/test_story_design_pack_golden_path.py`.
- Focused adapter tests pass: `python -m pytest -q tests/test_tutor_decision_cards.py`.
- Exact-head CI passes at the validation tier selected by the repository's risk-based validation policy; changes touching high-risk boundaries must pass the full supported Python matrix.
- Local verification stack passes: `python scripts/check.py --skip-pytest`.

Must-never-happen assertions:

- Converting `TutorGuidance` must never accept or mutate StoryIdentity.
- Converting a diagnostic must never apply a repair or modify Structure.
- A diagnostic recommendation must never be treated as author acceptance.
- Decision Card conversion must never rewrite canon, create a canonical artifact, or bypass an existing acceptance path.
- Adapter output must never gain authority merely because it contains deterministic evidence.
- Changing presentation depth must never change the underlying story recommendation or acceptance semantics.

## Why it matters

M1 should not replace working Tutor and diagnostic systems with a parallel reasoning stack. The safe move is to adapt existing derived outputs into one consistent author-facing decision envelope. That preserves proven V1 behavior, makes provenance visible, and keeps the distinction between a finding, a recommendation, and an accepted story decision explicit.

## Out of scope for this issue

Do not implement or port any of the following:

- Tutor session persistence;
- stale-session lifecycle;
- root `auteur tutor` CLI commands;
- StoryIdentity acceptance or any new acceptance path;
- automatic diagnostic repair or blueprint mutation;
- reasoning-report adapters or productionization;
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
- GUI/workspace work;
- prose generation changes.
