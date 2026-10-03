# Quick Draft Spike — Low-Friction Entry Path

**Date:** 2026-10-03  
**Original spike:** `feat/quick-draft-spike`  
**Integrated candidate:** `feat/beginner-quick-draft-loop`  
**Scope:** isolated product-ergonomics prototype  
**Command:** `auteur quick-draft "<premise>" "<first scene intent>"`

## Goal

Test whether Auteur can move a beginner from a rough idea to first-scene prose
without requiring upfront Story Identity, Structure, outline, Chapter plan, or
scene-plan acceptance.

The spike accepts exactly two story inputs:

1. a 1–2 sentence premise or prompt;
2. what the author wants to happen in the very first scene.

Everything else is inferred locally and marked provisional.

## Example

```text
auteur quick-draft \
  "Detective Miller learns that every suspect remembers a murder differently." \
  "Miller interviews Vance, who describes Miller committing the murder."
```

The command prints the working scene directly to the terminal. The integrated Beginner Browser also exposes the same two-input path as **Start writing now** and stores the session under:

```text
.auteur/quick_draft/<session-id>/
├── scaffold.yaml
├── provisional_bible.json
└── scene_draft.md
```

It does **not** create:

```text
story_identity.yaml
blueprint.yaml
bible.json
chapters/01/final.md
```

at project root.

## Flow

```text
premise
+
first-scene intent
        ↓
deterministic provisional scaffolding
        ↓
one prose-generation call
        ↓
working scene draft
        ↓
author reads / edits / reacts
        ↓
later review, acceptance, and reconciliation
```

No critic pass, canon acceptance, Structure acceptance, or reconciliation runs
before the writer sees prose.

## Provisional scaffolding

The facade builds enough temporary context for the existing Bard prompt without
promoting any of it into normal story state.

Default lenses:

- Main Story Engine
- Emotional & Aesthetic Framing
- Common Tropes
- Structural Shape
- Reader Experience

All lens records use:

```yaml
status: inferred_provisional
```

The inferred Identity container and its target-experience, story-type, and
central-engine subcontainers also carry `status: inferred_provisional`.

The provisional scene plan is similarly marked.

## Authority state

The scaffold records:

```yaml
authority:
  story_setup: not_accepted
  structure: not_accepted
  scene_draft: working_only
  canon_acceptance: deferred_until_after_draft
  structural_reconciliation: deferred_until_after_draft
```

The spike therefore preserves the core rule:

> recommendations and inferred proposals are never silently converted into
> accepted story material.

The command does not call any normal acceptance owner.

## How the draft is produced

The facade:

1. constructs a temporary generic `StoryIdentity` in memory;
2. compiles it to an in-memory `StoryBlueprint` using the existing compiler;
3. narrows that blueprint to a one-scene / ~1400-word drafting target;
4. creates a one-scene outline from the author's second input;
5. reuses the existing Bard prompt renderer;
6. makes exactly one LLM request with an 1800-token ceiling;
7. writes and prints the resulting scene.

This keeps the prototype close to current Auteur generation behavior without
introducing a parallel narrative contract.

## Provider selection

The command takes no provider/model story inputs.

It uses existing environment configuration:

1. `AUTEUR_QUICK_DRAFT_PROVIDER` when set;
2. otherwise `OPENAI_API_KEY` when present;
3. otherwise `ANTHROPIC_API_KEY`.

`AUTEUR_QUICK_DRAFT_MODEL` may provide an environment-level model override.

Provider configuration is infrastructure context, not another creative decision
asked of the writer.

## Thirty-second target

The session records:

```yaml
draft:
  elapsed_seconds: ...
  thirty_second_target_met: true|false
```

The prototype minimizes pre-prose latency by using deterministic scaffolding,
one generation request, no critic pass, and no approval workflow.

The thirty-second measure is an ergonomics target rather than a guarantee about
external provider latency.

## Deferred decisions

After prose exists, the product can ask questions that now have concrete
evidence behind them:

- Does this feel like the right story?
- Which inferred story setup should be kept?
- Did the scene discover characters, places, or events Auteur should remember?
- Does the emerging scene imply a different Structure?
- Should the draft remain exploratory, be reconciled, or eventually be
  accepted?

Those are deliberately **post-draft** responsibilities.

## Integrated shaping handoff

The integrated Browser does not silently convert discovery hints into shaping
inputs.

After **What did we discover?**, each possible new element is opt-in:

~~~text
[ ] Carry this idea into story shaping
~~~

Nothing is checked by default.

When the author selects **Shape this story**, Auteur preserves a noncanonical
handoff receipt containing:

- the Quick Draft session ID;
- exact source-draft SHA;
- original premise;
- first-scene intent;
- destination workspace ID;
- only the discoveries explicitly selected by the author.

The normal workspace receives the author's premise, first-scene intent, and
selected discoveries as explicit shaping input. Unselected heuristic findings
remain behind in the provisional Quick Draft session.

If the draft has no detected discoveries, Auteur skips the empty confirmation
step.

## Contract preservation

The spike does not modify:

- `StoryIdentity`;
- `StoryBlueprint`;
- Chapter / Scene acceptance owners;
- provenance lifecycle models;
- reconciliation contracts;
- canonical artifact schemas.

It only composes existing models behind an isolated provisional facade.

## Mechanical prototype checks

`tests/test_quick_draft_spike.py` verifies:

- exactly two positional story inputs;
- an extra third decision is rejected;
- one LLM request produces the initial prose;
- all inferred scaffolding is `inferred_provisional`;
- no root accepted Identity, Blueprint, Bible, final Chapter, or validation
  artifact is created;
- draft acceptance is false;
- review is deferred;
- reconciliation is deferred;
- the fake-provider path reaches prose within the thirty-second target;
- the CLI prints the prose before any acceptance instruction.

## Product question this spike answers

The experiment is not:

> Can Auteur eliminate planning?

It is:

> Can Auteur infer enough reversible planning to let the writer experience the
> story first, and ask for commitment only after the writer has something
> concrete to react to?

That is the low-friction hypothesis this branch is designed to test.
