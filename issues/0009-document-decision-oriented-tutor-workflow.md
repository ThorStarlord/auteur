---
id: 0009
title: Document the decision-oriented Tutor workflow
state: untriaged
priority: high
area: Decision-Oriented Tutor
filed-by: roadmap-author
opened: 2026-09-07
---

## Starting point

Assumes issues < 0004 through < 0008 merged.

The production M1 workflow is now implemented and protected by local authority/staleness regression tests. What is missing is concise production documentation that tells a beginner and a future coding agent what a Decision Card is, how the root `auteur tutor` workflow behaves, where advisory sessions live, how stale sources are handled, and - most importantly - what the Tutor does not have authority to change. There is no bug to reproduce for this issue.

Reference implementation may be inspected READ-ONLY at commit 844fc84 (branch origin/codex/future-roadmap-implementation). Do NOT merge, checkout, or bulk-copy that branch. Port ONLY the subsystem named above; reimplement it adapted to the current production architecture.

M1 authority contract that the documentation must state explicitly:

- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- `tutor choose` records an advisory response and MUST NOT accept StoryIdentity, update blueprints, rewrite canon, or repair structure.
- Canon changes only through Auteur's existing explicit author-authority/acceptance/revision paths.

Applicable M1 IN scope for this issue:

- Decision-Oriented Tutor concepts and workflow documentation.
- Decision Card field/authority overview.
- Tutor depth modes: `recommend`, `explain`, `teach`, `challenge`, `quiz`.
- Root `auteur tutor next/show/explain/choose` usage.
- Local Tutor session storage/lifecycle.
- Source fingerprints and stale-session behavior.
- Explanation of how existing Tutor guidance/diagnostics become advisory Decision Cards.
- Explicit author-boundary and no-automatic-repair language.

Tutor depth is presentation-only in M1. Documentation must not imply that higher depth has more authority, changes canon, tracks skill, or makes a different story decision.

## What should exist

Create or update one primary production document in the repository's normal user/design documentation surface, preferably `docs/design/decision-oriented-tutor.md` if that path is already established. If a short design stub already exists, expand/replace it rather than creating a competing document. Add only the smallest index/README link needed to make the document discoverable if the repository has an established documentation index.

The document must cover:

1. **Purpose**
   - The Tutor helps the author make one creative decision at a time.
   - It can orient, explain a craft principle, recommend, compare alternatives/trade-offs, and record an advisory response.
   - It does not own story canon.

2. **Decision Card contract**
   - Explain the important user-facing fields: decision, why it matters, craft concept, recommendation, alternatives, trade-offs, beginner trap, downstream consequences, evidence/provenance, allowed actions, authority status.
   - Explain deterministic card identity and source fingerprints at a conceptual level without promising more semantic meaning than they provide.

3. **Authority hierarchy**
   - Accepted/revisioned story authority remains authoritative.
   - Deterministic projections/findings can inform a Decision Card.
   - Decision Cards and Tutor sessions remain derived/local.
   - An explicit Tutor response is not canonical acceptance.
   - Include a clear statement equivalent to: "Nothing canonical changes until you explicitly change the story through an existing story-authority workflow."

4. **Tutor depth**
   - Document all five modes.
   - State that depth changes presentation/scaffolding only in M1.
   - Do not mention learning progression or automatic adaptation.

5. **Session lifecycle**
   - Where local sessions are stored.
   - Active -> stale/resolved semantics.
   - Source fingerprint changes make existing advice stale.
   - Stale sessions remain inspectable but cannot record substantive actions; regenerate a fresh card/session instead.

6. **CLI walkthrough**
   - Current syntax for `auteur tutor next`, `auteur tutor explain`, `auteur tutor show`, and `auteur tutor choose` as implemented in production.
   - Include one short human-readable example and one `--json` example if the command supports it.
   - Do not invent flags that the parser does not actually support.

7. **Relationship to existing systems**
   - Existing Story Design Packs remain reusable priors/context, not story instance canon.
   - Existing structure diagnostics remain findings; converting one to a Decision Card does not apply a repair.
   - Existing Story Discovery/StoryIdentity acceptance remains the canonical acceptance path where applicable.

Before writing examples, inspect the real parser/help and current tests so every documented command matches production exactly.

Locally verifiable acceptance criteria:

- The primary Decision-Oriented Tutor document exists in the repository documentation tree and is discoverable from an established nearby index/guide surface if one exists.
- Every documented CLI example matches the actual merged parser; no nonexistent flag, action, or positional argument is documented.
- The document contains the exact authority statuses `DERIVED / NOT CANON` and `LOCAL / NONCANONICAL` (or the repository's exact serialized equivalents if model output differs, with the conceptual wording still explicit).
- The document explicitly states that `tutor choose` does not accept StoryIdentity, update blueprints, rewrite canon, or repair structure.
- The document explicitly states that stale sessions are inspectable but cannot record substantive responses.
- The document explicitly states that Tutor depth is presentation-only in M1.
- Focused behavior tests used to validate examples remain green: `python -m pytest -q tests/test_story_design_pack_cli.py tests/test_tutor_decision_cards.py tests/test_tutor_session.py tests/test_story_design_pack_tutor.py tests/test_story_design_pack_golden_path.py`.
- Exact-head CI passes at the validation tier selected by the repository's risk-based validation policy; changes touching high-risk boundaries must pass the full supported Python matrix.
- Local verification stack passes: `python scripts/check.py --skip-pytest`.

Must-never-happen assertions for the documentation:

- Documentation must never imply that a Decision Card is canon.
- Documentation must never imply that a Tutor session is canonical history.
- Documentation must never describe `tutor choose` as StoryIdentity acceptance, blueprint update, canon rewrite, or structure repair.
- Documentation must never tell users that stale advice can be acted on without regeneration/currentness validation.
- Documentation must never imply that `teach`, `challenge`, or `quiz` measures writer skill or changes story authority.
- Documentation must never present a diagnostic recommendation as an automatically applied fix.

## Why it matters

The Decision-Oriented Tutor deliberately separates useful guidance from story authority. That distinction is easy to lose if users or future agents see a `choose` command and assume it means "apply this to the story." Production documentation makes the workflow legible, teaches the stale-source safety model, and prevents later implementation from drifting toward a second acceptance system.

## Out of scope for this issue

Do not implement or port any of the following:

- production code changes except a minimal documentation-link correction if required for discoverability;
- new Tutor commands, flags, actions, or models;
- StoryIdentity acceptance or any new acceptance path;
- blueprint/structure mutation or automatic repair;
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
- GUI/workspace design;
- prose-generation behavior;
- remote CI, wheel qualification, or installed-wheel smoke work.
