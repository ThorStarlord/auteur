# Beginner Decision Golden Path — Product Integration Evidence

**Date:** 2026-09-11  
**Baseline:** Decision-Oriented Tutor M1 complete on `main` via PRs #187, #191, #192, and #193.  
**Scope:** hermetic product-integration verification of already-shipped capability; no external-provider or subjective production claim.  
**Authority:** evidence/review document; it does not authorize narrative mutation.

## Question

Can a beginner move through the current Auteur surfaces from a raw premise to one understood and recorded creative choice **without manually reconstructing where the product boundary is**, and can Auteur tell them what authoritative workflow owns the story change implied by that choice?

## Exercised path

The new integration test `tests/test_beginner_decision_golden_path.py` exercises one coherent project through:

```text
raw premise
→ Story Discovery candidate generation
→ explicit StoryIdentity acceptance
→ blueprint seed
→ root Tutor Decision Card
→ Tutor explanation
→ author `choose`
→ resolved local Tutor session
```

The Story Discovery step uses the real CLI and deterministic in-process LLM fixtures, so the integration crosses the same command/parser/serializer boundaries without paid or live model calls. The accepted StoryIdentity and derived blueprint are then used as real source-fingerprint inputs to the root Tutor session.

## What works

1. **The beginner can reach accepted story direction through an explicit boundary.** Story Discovery writes candidates first; `story-discovery accept` is still the operation that creates the accepted `story_identity.yaml`.
2. **Structure can be seeded from that accepted identity.** The same project then has a real `blueprint.yaml` for downstream context.
3. **Root Tutor can bind to real current project artifacts.** `auteur tutor next` persists a source-aware local session over `story_identity.yaml` and `blueprint.yaml`.
4. **The same semantic decision can be explained without changing its identity.** `tutor explain` preserves the card ID while changing presentation depth.
5. **The author can record a choice safely.** `tutor choose ... choose --value ...` resolves the local session.
6. **The authority boundary remains intact.** The accepted StoryIdentity and blueprint remain byte-identical after the Tutor choice.

This is meaningful product progress: the route from story direction to one bounded advisory decision is now coherent and safe.

## Observed friction

The first material integration gap appears **immediately after the Tutor choice**.

The resolved Tutor session contains:

- `status: resolved`;
- `response_action: choose`;
- the selected `response_value`;
- the original Decision Card;
- `LOCAL / NONCANONICAL` session authority;
- `DERIVED / NOT CANON` decision authority.

It does **not** contain a structured handoff telling the author:

- which accepted artifact or semantic layer the choice would affect;
- which existing authority-bearing workflow owns that change;
- whether the next step is Identity revision, Structure proposal/revision, Realization revision, or another existing path;
- what command or bounded operation the author should inspect next;
- why that path is the correct authority boundary.

The current CLI therefore ends at a semantically correct but product-incomplete state:

```text
"I chose the recommendation."
        ↓
Tutor: "Recorded. Still noncanonical."
        ↓
???
        ↓
existing authoritative story workflow
```

A knowledgeable Auteur developer can infer the next action from architecture targets, source artifacts, the workflow engine, and existing revision commands. A beginner should not need to reconstruct that routing manually.

## Classification

**Primary gap:** workflow / product integration.

This is not evidence for a new semantic layer or universal narrative ontology. The repository already has:

- explicit authority levels and `WorkflowAction`;
- Story Discovery acceptance;
- Structure diagnose/propose/apply and scoped revision workflows;
- Realization/reconciliation paths;
- provenance and impact machinery;
- Decision Cards and Tutor sessions.

The missing capability is a **derived bridge between a resolved advisory decision and the already-existing authority-bearing workflow**.

## Recommended bounded capability

Promote **Decision-to-Authority Handoff** as the next implementation package.

Minimal contract:

```text
resolved Tutor choice
→ derived Decision Handoff
→ affected layer/artifact candidates
→ one existing authority-bearing workflow recommendation
→ human-readable rationale
→ explicit statement that the handoff itself does not mutate canon
```

The handoff should be inspectable in human and JSON output and should be deterministic from evidence already present in the Decision Card/session plus current project state where possible.

### Required guardrails

- Handoff authority is derived/noncanonical.
- Generating or inspecting a handoff must not change StoryIdentity, blueprint, accepted Realization, or other canonical state.
- The handoff must point to an **existing** authority path; it must not invent a second acceptance system.
- When evidence is insufficient to route confidently, return an explicit unresolved/inspect state rather than guessing.
- A stale Tutor session must not produce an actionable handoff from obsolete source state.
- `tutor choose` remains a local response operation; it does not become canonical mutation.

## What this evidence does not justify yet

This verification does **not** yet justify:

- automatic execution of the authoritative action;
- Narrative Change Preview;
- automatic causal impact claims;
- Decision Reassessment;
- Unified Project Orientation or a dashboard;
- new Series ontology or long-horizon expansion;
- adaptive writer profiling.

Those remain later candidates and should be promoted only from subsequent observed friction.

## Conclusion

The Golden Path succeeds through the point of **understanding and recording one choice**. It fails to provide a beginner-facing continuation from that safe local choice to the existing authority-bearing story workflow.

That makes **Decision-to-Authority Handoff** the smallest evidenced next product intervention.
