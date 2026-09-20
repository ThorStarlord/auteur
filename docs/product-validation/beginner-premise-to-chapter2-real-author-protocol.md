# Beginner Premise-to-Chapter-2 Real-Author Dogfood Protocol

**Status:** READY FOR HUMAN EXECUTION  
**Tracking issue:** #249  
**Evidence type:** human product evidence; do not substitute agent simulation.

## Purpose

Exercise the current Beginner author journey end to end and identify the first
material product friction after the post-draft / Chapter N -> N+1 continuation
merge.

This protocol does not authorize a new subsystem. Its output is an observation
record used to select the smallest warranted intervention.

## Journey

Run one fresh story through:

```text
new premise
-> narrative architecture
-> story direction / Identity
-> explicit accepted foundation
-> whole-story outline
-> Chapter 1 plan
-> scene plan
-> Chapter 1 draft
-> post-draft review
-> revise or explicitly accept
-> accepted Chapter 1 outcome
-> contextual Chapter 2 plan
```

Do not coach around product friction unless the author is blocked. Preserve the
author's own wording when recording confusion or unmet need.

## Observation record

Create a dated copy of this section under `docs/product-validation/`.

- Date:
- Repository SHA:
- Workspace/project ID:
- Author role/context:
- Journey endpoint reached:
- First material friction:
- Author's wording:
- What the author expected:
- What Auteur presented:
- Whether the author could recover without outside explanation:
- Authority/canon confusion observed:
- Data loss or unsafe mutation observed:
- Additional later frictions (secondary only):

## Classification

Classify the **first material friction** before proposing a change:

- `UX / presentation` — capability exists but is hard to discover or understand;
- `workflow` — existing capabilities do not connect into a coherent author action;
- `craft knowledge` — the author understands the decision but lacks useful narrative guidance;
- `domain model` — current accepted/candidate/derived state cannot express the recurring need;
- `infrastructure` — reliability, performance, packaging, or qualification blocks use.

## Candidate mapping

Only after classification, compare the observed friction with preserved
candidate families:

- Unified Decision Inbox / broader attention sources;
- Current Author Intent;
- demand-driven Story Design Pack growth;
- Existing-Manuscript Reverse Engineering;
- Book-Level Reasoning and Editing;
- bounded Episode 1 Direction when the author is explicitly working serially.

The candidate list is not a menu that must be used. A smaller UX/workflow fix
takes precedence when it solves the observed problem.

## Evidence boundaries

- Human use is first-class product evidence but is not deterministic test evidence.
- One author does not establish population-level usability or universal craft truth.
- A green automated suite does not override a material human workflow failure.
- An agent/browser automation run may verify mechanics but may not be relabeled human evidence.
- Recommendations remain advisory until explicitly selected through the normal repository process.
- Do not broaden ontology, authority, or scope to make the evidence look more consequential.

## Selection output

Record exactly one of:

1. `NO_MATERIAL_FRICTION` — do not invent work merely to continue the roadmap;
2. `BOUNDED_INTERVENTION` — name the smallest change, owning layer, and evidence;
3. `OWNER_DECISION_REQUIRED` — the next step depends on a creative/product choice not delegated by existing authority;
4. `EXTERNAL_BLOCKER` — execution cannot continue for a reason outside the repository.

If a bounded intervention is selected, link the raw observation record from the
new issue/plan rather than paraphrasing it into stronger claims.
