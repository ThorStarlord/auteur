# Story-Instance Relationship Extraction — Research Disposition

Status: suspended after architecture and deterministic vertical-slice proof, 2026-08-31.

## Decision

Do not start Attempt 10, V1.2/V2, another model-output campaign, another
empirical harness, or production relationship extraction by default.

Detailed Narrative Architecture V1 has now been reviewed, and its deterministic
P0 vertical slice has been implemented and merged without requiring automatic
story-instance relationship extraction. Extraction is therefore **not a
prerequisite for the current implementation-expansion path**.

Further extraction work requires a new, concrete empirical question that crosses
the reopening gate below.

## Established enough to proceed

- Direction and realization should compose through accepted history, current
  state, dependency, and relevance projections;
- causal/supporting-history trace and pressure grouping have qualifying positive
  evidence in V3;
- currentness and relevance are separate;
- richer structure should be selectively projected into current decisions;
- the narrow repeated Map/Focus mechanism is useful, while V3 shows incremental
  value from preserving explicit grouping/relationship structure beyond it; and
- the deterministic P0 architecture slice can represent causal-support and
  pressure-group relations through declared and deterministic sources without
  automatic extraction.

## Post-architecture implementation update — 2026-08-31

[Detailed Narrative Architecture V1](../architecture/detailed-narrative-architecture-v1.md)
and its merged [deterministic vertical slice](../architecture/detailed-narrative-architecture-v1-vertical-slice.md)
proved a bounded path through revisioned accepted history, current-state
projection, story-instance relations, Global Map, Focus, retroactive revision
impact, and derived-state rebuild.

The vertical slice used explicit accepted structure plus narrow deterministic
derivation for its first causal/supporting-history and pressure-group behavior.
It did not require an LLM relationship extractor.

This changes the default sequencing decision: implementation expansion should
continue from concrete product/architecture gaps. Automatic extraction should
not be built merely to make the relationship index more complete or to resume
the earlier experiment.

See [Global Map Architecture and Extraction — Research Retrospective](global-map-architecture-and-extraction-retrospective.md)
for the cross-campaign methodological synthesis.

## Not established

Universal relationship ontology, reliable open-world extraction, arbitrary
pressure inference, promotion of LLM confidence to authority, cross-story
generalization, human usability, and the need for a graph database are not
established.

The merged deterministic vertical slice also does not establish that every
important story relationship can be declared or deterministically derived. It
only demonstrates that automatic extraction is unnecessary for the current P0
implementation boundary.

## Evidence boundary

The V1 ledger is explicitly research-only. The qualifying V3 result reports
A=6/6/3, B=6/6/3, C=13/2/0 and paired P03/P05 C=4/2/0 versus B=0/3/3.
It identifies explicit pressure grouping and causal/supporting-history trace
as the strongest C-over-B mechanism. V1 and V1.1 separately test extraction
reliability; invalidated runs remain excluded from product inference.

The architecture and vertical-slice implementation establish engineering
coherence for a bounded deterministic path. They do not retroactively validate
or score any invalidated extraction attempt.

## Extraction reopening gate

Further extraction execution remains suspended. Reopen automatic
story-instance relationship extraction only when a concrete user/product
capability requires a relationship that satisfies all three conditions:

1. it cannot reasonably be declared in an accepted owning artifact;
2. it cannot be deterministically derived from accepted structure/history; and
3. it materially affects a user-facing decision strongly enough to justify
   interpretive inference.

If all three conditions are met, the proposed empirical question must also state
its concrete capability, target relationship mechanism, authority boundary,
acceptance criteria, and claim ceiling before execution.

The following are **not** sufficient reopening reasons by themselves:

- wanting more graph/index coverage;
- making the architecture feel complete;
- increasing the number of inferred relation types;
- improving elegance or symmetry of the Global Map;
- resuming Attempt 10 because earlier attempts were invalidated; or
- testing extraction before any product capability actually depends on it.

## Next empirical question

No extraction question is currently authorized.

A future question should arise from an observed implementation or user-facing
capability gap that crosses the reopening gate. Until then, continue with
architecture/product implementation work and deterministic tests rather than a
new extraction campaign.
