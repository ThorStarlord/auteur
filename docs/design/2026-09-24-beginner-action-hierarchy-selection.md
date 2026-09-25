# Beginner Action-Hierarchy Selection (Breadth → Depth)

Date: 2026-09-24
Status: selected and implemented; verification is synthetic (owner-directed)

## Context

The 2026-09-23 human Beginner walkthrough found transition and explanatory
friction: phase-ending / phase-transition actions lacked salience, and the
explanation exposed components without connecting them. The owner then directed a
breadth → depth UX pass for the Beginner action hierarchy and authorized
**synthetic** acceptance in place of a second manual playthrough. This record
captures the breadth options, the depth down-selection, the chosen component
hierarchy, and how the choice is verified.

This is a presentation decision. It does not create a semantic layer, change
authority boundaries, or add a universal taxonomy. It constrains how existing
Narrative Architecture, Discovery, Identity, Structure, and continuation
surfaces are presented.

## Breadth pass — three candidate architectures

The search space for exposing "you finished this → do this next" was reduced to
three structurally distinct options.

### Option A — Sequential wizard stepper

One stage per screen; a top stepper shows completed / current / locked; the only
forward control is "Next". Secondary exploration is hidden until the step ends.

- Strengths: maximum transition clarity; impossible to see two actions at once.
- Weaknesses: hides already-valid non-linear transitions
  (`open-revision:*`, `open-review:*`); fights the existing
  `primary_surface` + `available_actions` contract; risks implying that
  exploration is forbidden.

### Option B — Reactive milestone cards with explicit next-action priority (selected)

The existing navigator/milestone surface stays, but each stage gains an explicit
lifecycle state, and the active surface always names one primary next action.
After the foundation is accepted, a phase-completion status banner and a
`Next: outline your story` transition block appear, with a single
`primary-next-action` control.

- Strengths: preserves the authority contract and non-linear transitions;
  makes completion and next action unambiguous; degrades gracefully for the
  no-provider path; testable as data (projection) plus static wiring (served
  bundle).
- Weaknesses: requires discipline so that only one action is styled primary at a
  time.

### Option C — Split-pane narrative inspector

A permanent story map/composition pane beside a detail pane; actions live in
context inside the detail pane.

- Strengths: strong "explain composition, not components" affordance.
- Weaknesses: largest visual change; the composition explanation is already
  available through the integrated `How these parts work together` projection and
  the on-demand guidance inspector; on narrow screens the split pane collapses
  into the same drawer pattern, so most of the benefit duplicates existing
  surfaces for a larger regression surface.

## Depth pass — down-selection

Evaluated against the durable Beginner requirements (composition explanation,
honest uncertainty, obvious transitions, coherent no-provider degradation) and
the repository constraints (authority invariants, accessibility, no new
semantic layer, minimal blast radius):

| Criterion | A | B | C |
| --- | --- | --- | --- |
| Transition salience | high | high | medium |
| Single primary action | forced | explicit | implicit |
| Preserves non-linear transitions | no | yes | yes |
| Reuses existing contract | weak | strong | medium |
| Accessibility / narrow-screen behavior | medium | strong | weak |
| Regression / blast radius | high | low | high |

**Selected: Option B.** It resolves the observed friction with the smallest
change that preserves the authority and projection contract, and it is directly
verifiable by a synthetic E2E over the real server plus the served bundle. Option
A would break valid transitions; Option C duplicates existing explanation
surfaces for a much larger change.

## Chosen component hierarchy and state transitions

```
Story navigator (milestone cards)
  └─ entry states: working → complete (is-accepted styling)
Decision workspace (active surface, driven by primary_surface)
  └─ Decision card → select (autosave) → continue → review
Review panel
  └─ accept-* button rendered only when the accept action is available,
     styled as the single primary action
  └─ once whole_story_structure is accepted and no revision is active:
        phase-complete-banner ("Story foundation complete")
Continuation panel
  └─ phase-transition block ("Next: outline your story")
  └─ exactly one primary-next-action for the first available continuation action
  └─ after propose-outline: accept-outline becomes available
Guidance inspector (on demand) — integrated composition explanation + honest unknowns
```

Primary-action invariant: at most one control is styled as the primary action on
the active surface; acceptance controls disappear from `available_actions` once
the milestone is accepted.

## Verification

- Synthetic E2E: `tests/test_beginner_synthetic_walkthrough_claims.py` drives the
  real no-provider server through the owner premise and asserts the four claims
  (transition salience, single primary next action, integrated explanation with
  honest unknowns, credible fallback with explicit choice), plus the served
  `index.html` / `app.js` / `styles.css` action-hierarchy wiring.
- Static wiring regressions: `tests/test_beginner_workspace_browser.py`.
- Claim boundary: this is synthetic/agent evidence. Human usability is not
  claimed; the owner explicitly waived the second manual walkthrough for this
  package and accepted synthetic verification instead.
