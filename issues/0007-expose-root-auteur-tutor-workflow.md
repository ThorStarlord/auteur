---
id: 0007
title: Expose the root Tutor workflow
state: untriaged
priority: high
area: Decision-Oriented Tutor
filed-by: roadmap-author
opened: 2026-09-07
---

## Starting point

Assumes issues < 0004, < 0005, and < 0006 merged.

Production has Story Design Pack CLI commands and may already expose legacy `auteur design tutor ...` guidance. The merged M1 model, adapters, and session service now need a small root command surface for working through one derived author decision. There is no bug to reproduce for this issue.

If provisional root `auteur tutor` wiring already exists, treat it as scaffolding: reconcile it to this issue, preserve compatible behavior, and do not create a duplicate command group.

Reference implementation may be inspected READ-ONLY at commit 844fc84 (branch origin/codex/future-roadmap-implementation). Do NOT merge, checkout, or bulk-copy that branch. Port ONLY the subsystem named above; reimplement it adapted to the current production architecture.

M1 authority contract for every change in this issue:

- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- `tutor choose` records an advisory response and MUST NOT accept StoryIdentity, update blueprints, rewrite canon, or repair structure.
- Existing explicit story acceptance/revision commands remain the only routes that can change canonical story state.

Applicable M1 IN scope for this issue:

- Root `auteur tutor` command group.
- `auteur tutor next`.
- `auteur tutor show`.
- `auteur tutor explain`.
- `auteur tutor choose`.
- Human-readable and `--json` output where consistent with repository CLI conventions.
- Use of merged Decision Card adapters and Tutor session service.
- Source-fingerprint input/currentness checks sufficient to enforce stale-session safety.
- Focused parser/dispatch/CLI tests.

Tutor depth values are `recommend`, `explain`, `teach`, `challenge`, `quiz`, and depth is presentation-only in M1. If a `--depth` option is exposed, it changes only how the same decision is presented. `explain` may be a convenience presentation path, but it must not create a different canonical or semantic decision.

## What should exist

Wire the root commands through the repository's existing CLI registration and dispatch architecture. Prefer extending the existing Story Design Pack/Tutor CLI module and root parser/dispatcher instead of adding a second CLI framework.

Required behavior:

`auteur tutor next`

- Builds one Decision Card from existing production Tutor guidance/diagnostics already in scope.
- Selects exactly one next decision from the supplied production source and
  existing deterministic guidance/diagnostic ordering. It does not invent a
  new ranking model, search future roadmap systems, or choose among story
  alternatives on the author's behalf. If no eligible decision exists, return
  an explicit empty/no-decision result rather than fabricating a card.
- May persist a local Tutor session when a project/session option is requested.
- Prints a clear Decision Card in human mode and a stable serialized payload in JSON mode.
- Human output must include the authority boundary, e.g. `DERIVED / NOT CANON` or equivalent explicit wording.
- Creating/displaying the card does not mutate story canon.

`auteur tutor explain`

- Presents the same underlying decision at a deeper explanation depth.
- Does not silently change the recommendation, evidence, card semantic identity, or story state.
- May persist a session only through the same local advisory mechanism as `next`.

`auteur tutor show <session_id>`

- Loads and displays a local session, including stale/resolved state.
- Stale sessions remain inspectable.
- If current source fingerprints are supplied, refresh/check staleness before rendering status.

`auteur tutor choose <session_id> <action>`

- Supports exactly the merged M1 advisory actions (`choose`, `keep_unresolved`, `reject_finding`, `request_alternatives`) subject to the card's allowed actions.
- Records the response in the local Tutor session only.
- Before recording a response, enforce the stale-source contract. If the session contains source fingerprints and current fingerprints are required to establish freshness, fail closed rather than assuming the session is current.
- A stale session cannot record a substantive action.
- Must print/serialize that the result remains advisory/noncanonical.

Source-fingerprint CLI handling:

- Reuse the merged deterministic fingerprint contract. Do not invent a second hash format in CLI code.
- Resolve the selected production source artifacts and compute their current fingerprints from their actual stable content. Do not treat caller-supplied hash strings as proof that a source is current.
- If the current production CLI already accepts explicit `key=value` source identifiers, preserve compatibility only as identifiers to resolve; extend `show`/`choose` as needed for a real stale check.
- Reject malformed fingerprint arguments with an actionable error.
- Do not infer freshness merely from file timestamps.

Backward compatibility:

- Existing `auteur design pack ...` commands must continue to parse and run.
- Existing `auteur design tutor ...` commands must remain functional unless the repository already marks them deprecated; do not remove them in this issue.
- Existing Story Discovery acceptance remains unchanged.

Locally verifiable acceptance criteria:

- Add or update `tests/test_story_design_pack_cli.py` to exercise root `tutor next`, `show`, `explain`, and `choose` through the real `auteur.cli.main`/parser path.
- Test both human-readable output and at least one JSON path.
- Test malformed source-fingerprint input.
- Test a persisted session becoming stale after a source fingerprint changes; `show` can inspect it, while `choose` rejects every substantive action.
- Create sentinel `story_identity.yaml` and `blueprint.yaml` files before `next`, `explain`, `show`, and `choose`; assert their bytes are unchanged afterward.
- Verify `auteur design pack list` and legacy `auteur design tutor recommend` still parse/run in the focused CLI tests.
- Focused CLI/session tests pass: `python -m pytest -q tests/test_story_design_pack_cli.py tests/test_tutor_session.py tests/test_tutor_decision_cards.py`.
- Existing Story Design Pack/Tutor golden-path regressions pass: `python -m pytest -q tests/test_story_design_pack_tutor.py tests/test_story_design_pack_golden_path.py`.
- Exact-head CI passes at the validation tier selected by the repository's risk-based validation policy; changes touching high-risk boundaries must pass the full supported Python matrix.
- Local verification stack passes: `python scripts/check.py --skip-pytest`.

Must-never-happen assertions:

- `auteur tutor next` or `explain` must never accept StoryIdentity, mutate a blueprint, rewrite canon, or apply structure repairs.
- `auteur tutor choose` must never call or emulate StoryIdentity acceptance/promotion.
- `auteur tutor choose` must never treat the response value as a blueprint transformation or canonical field update.
- A stale session must never accept `choose`, `keep_unresolved`, `reject_finding`, or `request_alternatives`.
- `auteur tutor show` must never refresh stale advice back to active merely by omission of source inputs.
- Tutor depth must never change canonical state or create a different semantic decision.
- Adding the root command must never break or silently repurpose existing Story Design Pack, Genre Pack, Story Discovery, or structure commands.

## Why it matters

M1 is a product milestone only when a beginner can actually move through one decision using a stable command surface. The root workflow should make the author boundary obvious: Auteur can orient, teach, recommend, compare, and remember the response, but only existing explicit story-authority commands can change canon. Stale-source checks also prevent the CLI from inviting an author to act on obsolete advice.

## Out of scope for this issue

Do not implement or port any of the following:

- automatic StoryIdentity acceptance after `choose`;
- blueprint/structure mutation or automatic repair;
- automatic generation of new alternatives beyond existing guidance;
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
