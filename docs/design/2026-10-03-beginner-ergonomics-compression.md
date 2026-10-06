# Beginner Ergonomics Compression — Premise to Chapter 1

**Date:** 2026-10-03  
**Tracking:** #303  
**Scope:** Beginner Browser human-facing interaction path only  
**Baseline:** measured 22 visible interactions to Chapter review on `main @ 725a3b5`  
**Target:** approximately 8 visible interactions on the default path to visible Chapter 1 prose

## Product problem

The measured Beginner flow asked the writer to supervise too many intermediate
planning and state transitions before receiving the first prose payoff.

The primary ergonomic distinction is:

```text
consequential creative commitment
!=
reversible execution scaffolding
```

Auteur should ask the writer to control story meaning while handling reversible
planning machinery with progressive disclosure.

## Selected interaction model

```text
maximum author control over meaning
+
minimum author administration of machinery
```

The implementation keeps existing internal artifacts and commands. It changes
which of those operations must become separate writer-facing ceremonies.

## Default path contract

The intended first-time default path is:

| # | Visible author interaction | Meaning |
|---:|---|---|
| 1 | Enter **Your story idea** | Create the premise |
| 2 | **Explore this story →** | Ask Auteur to interpret it |
| 3 | **That feels right →** | Continue with Auteur's working read |
| 4 | **Use this direction** | Select and commit one Story Direction in one author action |
| 5 | **Yes, keep going** | Keep the synthesized story core |
| 6 | **Use recommended story shape** | Apply Auteur's recommended Structure decisions as one author action |
| 7 | **Plan Chapter 1 →** | Build and retain outline, Chapter plan, scene plans, and draft handoff as one planning action |
| 8 | **Draft Chapter 1 →** | Generate Chapter 1 and immediately show the candidate prose |

The count is a product target for the uncomplicated recommended path, not a
universal invariant. Premises with genuine ambiguity, blocking contradictions,
provider failures, revisions, or explicit author customization may require more
interactions.

## Authority and reversibility decisions

### Story Direction

One visible **Use this direction** action performs the existing selection and
direction-acceptance transitions.

The author still explicitly chooses the direction. The UI no longer asks for a
second click that merely confirms the immediately preceding choice.

### Story core

The existing Story Identity authority remains unchanged.

The primary surface presents it as **What this story is becoming** and
**Yes, keep going**. Mapping/canon/provenance details remain available under
advanced disclosure rather than defining the first-time experience.

### Story shape

The existing Structure cards remain the source of the actual craft decisions.

The default path adds **Use recommended story shape**, which walks the current
recommended card choices through the existing `select`, `continue`,
`open-review`, and `accept-structure` commands.

**Customize story shape** restores the existing card-by-card controls.

No parallel Structure model is introduced.

### Chapter planning

The existing internal sequence remains:

```text
propose outline
-> accept outline
-> propose Chapter 1 plan
-> accept Chapter 1 plan
-> propose scene plans
-> accept scene plans
-> prepare draft handoff
```

The default Browser path now treats that sequence as reversible execution
scaffolding behind one explicit **Plan Chapter 1** action.

The output remains inspectable in a Chapter Launch summary. **Plan step by step**
preserves the previous granular path.

No outline, Chapter plan, scene plan, or handoff artifact is deleted or merged
internally.

### Drafting

**Draft Chapter 1** means:

```text
generate current candidate
-> open Chapter 1
-> render candidate prose
```

Candidate prose remains noncanonical. The existing explicit Chapter acceptance
continues to own promotion of the draft.

The post-draft primary actions are phrased in author language:

```text
Keep this draft
Revise
```

## Vocabulary compression

The primary navigation now favors:

- Direction
- Story core
- Story shape
- Chapter 1

Technical state remains available but is moved behind optional disclosure where
possible:

- Story Map details
- Story insight internals
- mapping/provenance details
- whole-book reconciliation / owning-command state
- interpretation diagnostics
- component-level refinement

This is progressive disclosure, not removal of the underlying state.

## Escape hatches

Compression must never become loss of control.

The implementation therefore preserves:

- **Adjust what Auteur sees** for premise-interpretation corrections;
- **Explore the story insights** for deeper architecture inspection;
- **Customize story shape** for the existing Structure card path;
- **Plan step by step** for the existing outline/chapter/scene progression;
- advanced whole-book and state details;
- the existing explicit Chapter acceptance boundary.

## Mechanical evidence contract

Browser contract tests assert that:

1. direction choice uses one visible action while preserving both underlying commands;
2. recommended Structure has one default action and a customization escape hatch;
3. Chapter planning retains all seven existing continuation actions internally;
4. planning exposes one default **Plan Chapter 1** action plus step-by-step mode;
5. drafting invokes the existing draft action and then opens Chapter 1;
6. the candidate prose is rendered before keep/revise decisions;
7. internal/advanced vocabulary is progressively disclosed;
8. the uncomplicated default path exposes the eight intended author interactions.

## Claims this package can establish

Repository/browser evidence may establish:

- fewer mandatory visible interactions;
- retained internal command/artifact sequence;
- retained customization paths;
- direct prose visibility after drafting;
- reduced primary-surface terminology exposure.

It cannot establish from automated evidence alone:

- lower experienced cognitive load;
- increased joy or confidence;
- stronger author ownership;
- higher preference;
- greater desire to continue.

Those remain real-author validation questions.

## Follow-up human comparison

After the compressed Browser candidate is usable, compare:

```text
A — corrected pre-compression Beginner flow
B — compressed Beginner flow
```

Measure:

- time to first useful insight;
- time to first visible prose;
- APPROVE/ADMIN actions between creative payoffs;
- hesitation and backtracking;
- "why do I need to decide this?" moments;
- use of customization escape hatches;
- perceived ownership;
- desire to continue.

Only after that comparison should Creative Scratch / Riff be reconsidered.

## Post-draft creative discovery extension

The compression principle also applies after prose exists.

A beginner must not be forced to translate an unexpected creative discovery into
internal model-maintenance work. When prose introduces material that was not in
the accepted plan, the product should surface the story consequence first and
the authority machinery second.

The selected follow-up contract is defined in
`docs/design/2026-10-03-beginner-creative-divergence-reconciliation.md`,
implemented in the integrated candidate #309, and tracked by #306.

The primary post-draft flow is:

```text
Auteur noticed the story changed while you were writing
-> Keep draft & update story
-> Keep as intentional divergence
-> Revise to match plan
```

This preserves the same governing product rule as the premise-to-prose
compression:

```text
maximum author control over meaning
+
minimum author administration of machinery
```

Unexpected prose is therefore treated as discovery evidence before it is
treated as invalid state.

## Non-goals

This package does not:

- modify CI/CD;
- modify branch protection;
- execute or redefine formal L3 qualification;
- update `STATUS.md`;
- update `artifacts/strategic_reconciliation.md`;
- create a new semantic layer;
- implement Creative Scratch / Riff;
- remove explicit Chapter acceptance;
- collapse internal outline/chapter/scene artifacts;
- redefine the product thesis.
