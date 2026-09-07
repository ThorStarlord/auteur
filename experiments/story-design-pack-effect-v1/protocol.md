# Preregistration: Pack Effect v1

## Question

For bounded superhero-applicable creative decisions, does supplying Auteur's
V1 `superhero` Story Design Pack improve the usefulness of the generated story
design artifact and its accompanying guidance compared with the exact same
workflow without a pack?

## Conditions

- **Control:** the frozen V1 workflow, with no Story Design Pack context.
- **Treatment:** the frozen V1 workflow, with only the built-in `superhero`
  pack, version `0.1.0`, supplied as derived context.
- Premise, decision prompt, system instructions, model, provider, sampling,
  candidate count, post-processing, and evaluator rubric are identical.
- The pack is context, not canon. It must not directly mutate a blueprint or
  author-owned state.

## Unit and sample

The unit is one condition-by-case generation. The frozen corpus has six cases
in `cases.json`. If the selected runtime has no meaningful deterministic seed,
two independent replicates per condition per case are required; otherwise the
seed is recorded and one replicate is permitted.

## Primary outcomes

Blinded evaluators score two predeclared composites on a 1–5 scale:

1. **Story artifact usefulness:** intent alignment, specificity, causal
   integration, stakes, actionability, and avoidance of unsupported narrowing.
2. **Reasoning/guidance usefulness:** why, tradeoffs, craft principle, story
   connection, author agency, and avoidance of pack parroting.

Failure flags are recorded independently and never silently converted into a
numeric score.

## Claim ceiling

This experiment can support only a bounded observation about these cases,
these conditions, this runtime, and this rubric. It cannot establish general
story quality, learning effectiveness, transfer, long-horizon value,
composition superiority, Tutor V2 value, ontology admission, or promotion of
the future-roadmap prototype. It cannot authorize Experiment 2.

## Analysis

Before unblinding, evaluator packets are randomized per case and contain no
condition labels. The condition key remains private. After scores are frozen,
the custodian may compute per-condition means, paired differences by case, and
failure-flag counts. Missing or invalid generations make the result
`INCOMPLETE_EXPERIMENT`; they are not imputed.

## Stopping rules

Stop with `EXPERIMENT_RUNTIME_UNAVAILABLE` when no approved real model runtime
is available. Stop with `READY_FOR_BLIND_EVALUATION` after valid raw outputs
are packeted and no fresh evaluator is available. Do not self-score.
