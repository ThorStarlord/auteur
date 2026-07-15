# Auteur Bounded Pilot Report

Date: 2026-07-15

This pilot used the repository's realistic `examples/sample_blueprint.yaml`
project fixture and a bounded setup/payoff input. It was an execution pilot of
the current product surface, not a claim that the fixture replaces an author's
long-form project.

## Workflow trace

Executed path:

```text
Blueprint
    → deterministic Structure diagnosis
    → registered critics
    → Reasoning Reports
    → synthesis review
    → author-facing review commands
```

The available fixture did not contain a complete accepted Scene Realization,
accepted prose, external manuscript edit, or reconciliation publication. Those
stages therefore remain unproven by this pilot and were not simulated as if
they had occurred.

Commands and artifacts:

| Step | Evidence |
|---|---|
| Structure diagnosis | `python -m auteur.cli structure diagnose examples/sample_blueprint.yaml --output <derived report>` |
| Structure result | 3 diagnostics: 0 errors, 1 warning, 2 info |
| Critic execution | `structure.blueprint` and `structure.setup_payoff` both returned `success` |
| Derived reports | One JSON Reasoning Report per critic |
| Synthesis | One derived `reasoning_review` with 4 groups |
| Author review | `auteur reasoning review <review.json>` and `auteur reasoning inspect <review.json> <group-id>` |

The Structure diagnosis found a missing motif representation warning and two
theme/target-experience information findings. The setup/payoff input contained
an unresolved `hidden_key` setup, producing competing explanations and
alternative recommendations.

## Friction log

### Freshness envelope mismatch

```yaml
intent: Run synthesis freshness validation over both critic reports
classification: transformation_gap
severity: medium
affected_scope: reasoning_and_provenance
friction: Built-in critics consume raw artifact objects, while the runtime source snapshot requires revision-bearing input envelopes. The pilot could execute both critics, but could not express their live artifact revisions through the same input shape without an adapter.
smallest_reproduction: pass a StoryBlueprint object to structure.blueprint and compare its report against a revision-bearing current_inputs mapping
```

This is a real integration finding, not a failed narrative operation. The safe
behavior was observed: the mismatched synthesis was marked stale rather than
being presented as fresh.

### Incomplete product path

```yaml
intent: Complete Identity → Structure → Realization → Expression → reconciliation
classification: missing capability
severity: high
affected_scope: pilot_boundary
friction: The repository fixture did not provide one bounded accepted project containing all requested authored stages, so the complete real-project path could not be evaluated.
smallest_reproduction: sample_blueprint.yaml has no accepted Scene Realization and external manuscript pair
```

This is a pilot-input limitation as well as a product-dogfood limitation. No
implementation was added to hide the missing evidence.

## Capability-matrix corrections

No existing matrix labels were changed. The pilot provided direct evidence for
deterministic Blueprint reasoning, multi-critic execution, synthesis, and
author-facing inspection. It did not provide evidence to upgrade Scene
Realization, Chapter Expression, or reconciliation labels because those stages
were not traversed by the available project.

## Author-facing review evaluation

The review surface answers the following for the exercised reports:

- what matters first: ranked groups are shown in order;
- why it matters: each group includes its summary and overlap basis;
- affected artifact: exposed when a finding declares an artifact or rule;
- agreement/disagreement: conflicts are marked and source claim references are retained;
- freshness: fresh/stale status is shown;
- next action: each group exposes a review/decision prompt;
- raw JSON avoidance: concise output is available before `--json` detail.

The setup/payoff review remained understandable without opening JSON. The
fixture did not provide enough prose or multiple authored chapters to evaluate
whether the review helps a real drafting decision.

## Evidence-selected next goal

The single next implementation goal selected from this pilot is:

> Add a read-only artifact revision/freshness adapter between built-in critics
> and the Reasoning Runtime so raw accepted artifacts and their provenance
> snapshots travel together without changing critic input APIs.

Why this goal: it is the only reproducible integration friction found during
the executed reasoning path, and stale safety is an authority invariant. The
pilot did not justify implementing structural revision propagation yet because
the required accepted Realization/Expression project path was not available.

## Pilot status

The bounded reasoning pilot is complete. The full end-to-end authoring pilot is
not complete; its next prerequisite is a genuinely authored bounded project
with 3–5 Scene Realizations, accepted prose, one external edit, and a
reconciliation cycle.

