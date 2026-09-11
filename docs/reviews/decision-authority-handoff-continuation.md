# Decision-to-Authority Handoff — Continuation Evidence

**Date:** 2026-09-11  
**Baseline:** Decision-to-Authority Handoff merged via PR #196.  
**Scope:** hermetic continuation check over the shipped Structure handoff route.  
**Authority:** evidence only; no story mutation is authorized here.

## Question

After Auteur identifies the existing Structure authority workflow, can a beginner actually prepare that workflow from the Tutor choice using current product surfaces?

## Exercised continuation

`tests/test_handoff_continuation_evidence.py` creates a current resolved Tutor choice, derives its handoff, and follows the route to the first required preparation input:

```text
resolved Tutor choice
→ Decision-to-Authority Handoff
→ Structure revision workflow identified
→ `structure revision plan --proposal <proposal.yaml>`
→ ?
```

The handoff itself works as designed: it identifies `structure_revision`, distinguishes read-only/derived/authority-bearing steps, remains `DERIVED / NOT CANON`, and leaves accepted files unchanged.

## Observed friction

The first preparation step requires a **concrete `StructureProposal`**. Current Story Design Pack/Tutor advice does not contain one:

- `DecisionCard` carries recommendation, alternatives, trade-offs, evidence, and pack provenance;
- `DesignOption` carries craft meaning plus broad `architecture_targets`;
- `StructureProposal` requires an explicit selected option whose `data` can become concrete revision operations;
- the revision planner derives operations from that concrete proposal data;
- the handoff intentionally does not invent or generate the proposal.

Therefore the route is correct but still discontinuous for a beginner:

```text
Tutor choice
→ correct authority route
→ missing concrete proposal representation
→ Structure revision plan
```

This gap appears **before** Narrative Change Preview. Auteur already has read-only impact-preview machinery for concrete decision candidates, but there is not yet a concrete Structure candidate corresponding to this Tutor choice to preview.

## Classification

**Primary gap: creative-planning translation at the workflow boundary.**

This is not evidence for another authority system or new narrative ontology. The existing `StructureProposal` and revision-plan contracts should be reused.

The mission already assigns creative planning to LLM calls while deterministic code owns schemas, project files, validation, artifacts, and retry rails. A safe bridge should follow that split: creative proposal content may be generated, but deterministic code must validate and persist only a noncanonical candidate.

## Selected bounded capability

Promote **Tutor-to-Structure Proposal Bridge** as the next implementation package.

Minimum behavior:

```text
current resolved Structure-routed Tutor choice
+ current blueprint
→ creative proposal generation
→ deterministic `StructureProposal` validation
→ project-local noncanonical proposal artifact
→ existing `structure revision plan --proposal ...`
```

Required guardrails:

- proposal generation does not apply or accept the proposal;
- generated output must validate against the existing `StructureProposal` schema;
- source fingerprints/currentness must be checked again before proposal generation;
- the proposal must retain the Tutor session/card/selected-value provenance;
- accepted `story_identity.yaml` and `blueprint.yaml` remain byte-identical;
- invalid model output fails without leaving a partial proposal;
- no generic deterministic mapping from craft labels to blueprint patches may be invented;
- the existing Structure revision lifecycle remains the only route to canonical mutation.

## Not justified yet

Narrative Change Preview, Decision Reassessment, Unified Project Orientation, serial expansion, and long-horizon architecture remain unselected. Change Preview should be reconsidered only after a concrete proposal exists and the author faces a real need to understand its downstream impact before applying it.

## Conclusion

Decision-to-Authority Handoff successfully answers **where the change belongs**. The smallest remaining gap is now **how the chosen creative intent becomes a validated noncanonical Structure proposal that the existing revision workflow can inspect and plan**.
