# Beginner Decision Golden Path — Product Integration Evidence

**Date:** 2026-09-11  
**Baseline:** Decision-Oriented Tutor M1 complete via PRs #187, #191, #192, and #193.  
**Scope:** hermetic integration verification of shipped capability; no live-provider or subjective production claim.  
**Authority:** evidence only; no narrative mutation is authorized here.

## Question

Can a beginner move from a raw premise to one understood and recorded creative choice, and can Auteur then identify the existing authoritative workflow that owns the implied story change?

## Exercised path

`tests/test_beginner_decision_golden_path.py` runs:

```text
raw premise
→ Story Discovery candidates
→ explicit StoryIdentity acceptance
→ blueprint seed
→ root Tutor Decision Card
→ Tutor explanation
→ author choose
→ resolved local Tutor session
```

Story Discovery uses the real CLI with deterministic in-process LLM fixtures. The accepted `story_identity.yaml` and derived `blueprint.yaml` become real source-fingerprint inputs to the root Tutor session.

## What works

- Story Discovery keeps candidate generation separate from explicit `story-discovery accept`.
- Structure seeds successfully from accepted StoryIdentity.
- Root Tutor binds to current project artifacts.
- `tutor explain` preserves semantic card identity while changing presentation depth.
- `tutor choose` resolves the local advisory session.
- Accepted StoryIdentity and blueprint remain byte-identical after the Tutor choice.

The route from story direction to one bounded advisory decision is therefore coherent and safe.

## Observed friction

The first material gap appears **immediately after the Tutor choice**. The resolved session records status, selected action/value, original Decision Card, and the two noncanonical authority statuses, but provides no structured answer to:

- which accepted artifact or semantic layer the choice would affect;
- which existing authority-bearing workflow owns the change;
- what command/operation should be inspected next;
- why that route is the correct authority boundary.

Current product flow:

```text
"I chose the recommendation."
→ Tutor records a safe noncanonical response
→ ???
→ existing authoritative story workflow
```

A repository expert can infer the route from architecture targets, project artifacts, workflow rules, and revision commands. A beginner should not have to reconstruct that routing manually.

## Classification

**Primary gap: workflow / product integration.**

This is not evidence for a new semantic layer or universal ontology. Auteur already has explicit authority levels, `WorkflowAction`, Story Discovery acceptance, Structure revision paths, Realization/reconciliation paths, provenance/impact machinery, Decision Cards, and Tutor sessions.

The missing capability is a **derived bridge from a resolved advisory choice to an existing authority-bearing workflow**.

## Recommended bounded capability

Promote **Decision-to-Authority Handoff**:

```text
resolved Tutor choice
→ derived Decision Handoff
→ affected layer/artifact candidates
→ one existing authority workflow recommendation
→ rationale
→ explicit no-mutation status
```

Guardrails:

- handoff remains derived/noncanonical;
- generation/inspection cannot change accepted story state;
- it points to an existing authority path rather than creating a second acceptance system;
- insufficient evidence returns an unresolved/inspection result instead of guessing;
- stale Tutor sessions cannot produce an actionable handoff;
- `tutor choose` remains local advisory state.

## Not justified yet

This evidence does not yet justify automatic authoritative execution, Narrative Change Preview, Decision Reassessment, Unified Project Orientation, new long-horizon ontology/scale work, or adaptive writer profiling. Those remain evidence-gated candidates.

## Conclusion

The Golden Path succeeds through **understanding and recording one choice** but does not provide the beginner-facing continuation to the owning authority workflow. **Decision-to-Authority Handoff is the smallest evidenced next intervention.**
