# Global Map Architecture and Extraction — Research Retrospective

Status: `RESEARCH AND PROCESS RETROSPECTIVE — ARCHITECTURE VALUE CLOSED ENOUGH TO BUILD; EXTRACTION SUSPENDED`

This document records cross-campaign learning from the Global Map architecture-value work, Story-Instance Relationship Extraction V1/V1.1, Detailed Narrative Architecture V1, and the deterministic V1 vertical slice. It is a process synthesis, not a new semantic architecture, product definition, or authorization for automatic relationship extraction.

The individual protocols, run records, qualifying results, architecture documents, ADRs, tests, and pull requests remain the source of truth for their own claims. This retrospective records what the sequence taught us about **which question to ask next, when an experiment has stopped reducing product uncertainty, and when architecture plus deterministic implementation is the better investigative method**.

## Evidence sequence

### 1. Architecture Value V3 established a bounded representation-value result

[Global Map Architecture Value V3](global-map-architecture-value-v3/README.md) compared a prompt/context baseline, the shipped repeated Map/Focus representation, and a richer architecture condition.

The qualifying result was:

- A: `6 PASS / 6 MIXED / 3 FAIL`;
- B: `6 PASS / 6 MIXED / 3 FAIL`;
- C: `13 PASS / 2 MIXED / 0 FAIL`; and
- paired P03/P05: C `4 PASS / 2 MIXED / 0 FAIL` versus B `0 PASS / 3 MIXED / 3 FAIL`.

The strongest C-over-B mechanisms were explicit pressure grouping and causal/supporting-history trace. The result did **not** establish that every item in the richer research ledger was useful, that a universal relationship ontology was needed, or that relationships could be extracted automatically.

The important decision was narrower: **some persistent relationship/group structure beyond the shipped repeated Map/Focus representation had earned further architectural consideration**.

### 2. Extraction V1/V1.1 asked a different question

Story-Instance Relationship Extraction V1/V1.1 moved from representation value to automatic population:

> Can Auteur derive source-backed story-instance `CAUSAL_SUPPORT` and `PRESSURE_GROUP` relationships reliably enough to preserve the demonstrated reasoning advantage?

That was a legitimate but narrower question. It was not the same as:

- whether explicit architecture has value;
- what the production architecture should be; or
- whether the first production architecture requires automatic extraction.

The distinction became important as the campaign progressed.

### 3. Invalidated extraction attempts increasingly tested the research apparatus

Repeated V1/V1.1 attempts were invalidated by execution-boundary problems such as transport identity, lifecycle, journaling, packet construction, run identity, projection, and orchestration. Those failures were real evidence about the **experiment and its execution system**.

They were not negative evidence about whether causal history, pressure grouping, Global Map, or Focus are useful product concepts.

The campaign therefore reached a point where improving the measurement/execution apparatus was consuming more effort than reducing the remaining product uncertainty.

See [Story-Instance Relationship Extraction — Research Disposition](story-instance-relationship-extraction-disposition.md) for the current stop decision.

### 4. Architecture synthesis changed the question productively

Detailed Narrative Architecture V1 treated architecture as an investigative instrument rather than merely a documentation deliverable.

The synthesis forced explicit answers about:

- accepted narrative history versus current canonical state;
- narrative order versus artifact revision order;
- ontology relationship vocabulary versus story-instance assertions;
- story-instance relationships versus canonical character relationship state;
- declared, deterministic, and interpretive relation origins;
- n-ary pressure groups rather than forcing every relation into a binary edge;
- derived Global Map and Focus versus authoritative narrative truth;
- independent health, freshness, and semantic-impact dimensions;
- revision propagation without silent downstream canonical mutation;
- rebuildability and provenance; and
- currentness versus relevance.

These were production-design questions that another recommendation-quality experiment was poorly positioned to answer.

See [Detailed Narrative Architecture V1](../architecture/detailed-narrative-architecture-v1.md) and [ADR 019](../adr/019-derived-global-map-and-story-instance-relation-authority.md).

### 5. The deterministic vertical slice exposed concrete engineering failures

The [Detailed Narrative Architecture V1 vertical slice](../architecture/detailed-narrative-architecture-v1-vertical-slice.md) then exercised the architecture through deterministic death tests rather than model-output scoring.

Implementation and review exposed concrete problems including:

- stable realization identity versus revision lineage;
- historical payload preservation;
- legacy revision-1 compatibility;
- a Focus path that initially bypassed Global Map;
- currentness/relevance conflation;
- story-fact identity collisions when local fact IDs repeat;
- historical dependency-hash validation;
- overly broad semantic-impact propagation; and
- whether the exact long-horizon Book-2-to-Book-6 cases were actually exercised.

Those findings were directly actionable engineering evidence. The merged vertical slice closes the bounded P0 death-test set without requiring automatic relationship extraction.

## Three questions that must remain separate

The sequence clarified three distinct questions:

1. **Does richer explicit narrative structure improve long-horizon reasoning?**  
   V3 provides qualifying positive evidence for a bounded mechanism family, especially pressure grouping and causal/supporting-history trace.

2. **Can those ideas compose into a coherent, maintainable production architecture?**  
   Detailed Narrative Architecture V1 plus the deterministic vertical slice provide a bounded positive answer for the P0 architecture contract.

3. **Can an LLM automatically infer/populate relationships reliably?**  
   This remains open and is not a prerequisite for the current implementation-expansion path.

Treating these as one question caused unnecessary coupling between architecture progress and extraction reliability.

## Methodological lessons

### Invalid execution is evidence about execution, not the product hypothesis

If a run violates its frozen packet, transport, isolation, accounting, or blind-evaluation contract, preserve the evidence and invalidate the run. Do not convert an execution failure into a semantic product conclusion.

### Architecture can be an investigative method

When the uncertainty concerns ownership, authority, lifecycle, provenance, revision semantics, state projection, or rebuildability, a detailed architecture plus adversarial death tests can reveal contradictions faster and more directly than another model-output benchmark.

A design document alone does not prove runtime behavior. The useful pair is:

`architecture synthesis -> deterministic vertical slice`

### Deterministic death tests are preferable when the claim is architectural

A question such as “does retroactively revising Book 2 preserve Book 6 acceptance while making its dependency stale?” is primarily an engineering-semantic question. It should first be answered through deterministic state, provenance, revision, and rebuild tests.

Use an empirical model experiment only when the remaining uncertainty is genuinely about model judgment or human response.

### Verify the artifact, not only the completion report

Agent reports are evidence pointers, not substitutes for repository inspection. During this work, direct branch/code review found stale provenance, a Global Map/Focus bypass, legacy-compatibility problems, death-test mismatches, identity collisions, and weakened historical-hash validation after intermediate reports described the slice as complete.

Completion claims should therefore be checked against the exact repository head, source code, tests, and qualification evidence relevant to the claimed invariant.

### Current-main provenance is part of reasoning correctness

The first architecture synthesis was based on an older repository line and therefore inherited a superseded interpretation of the architecture-value evidence. Reconciliation against actual current `main` materially changed the evidence story.

For repository synthesis work, “start from current main” is not only publication hygiene; stale provenance can change the conclusion.

### Stop when the remaining uncertainty changes category

Research should not continue merely because more observations are possible.

If an empirical campaign has established enough evidence for a mechanism to deserve architectural treatment, but further runs are mostly testing how to measure or automatically populate an undefined production representation, the uncertainty has changed category. The next method should change with it.

## Preferred work loop

For this class of Auteur problem, the preferred sequence is now:

```text
existing evidence
    -> identify the highest-leverage remaining unknown
    -> architecture synthesis when the unknown is structural
    -> architecture death tests
    -> smallest deterministic vertical slice
    -> inspect concrete implementation failures
    -> targeted empirical experiment only if a remaining unknown genuinely
       requires model or human evidence
```

This is not a rule that experiments must always follow architecture. Early experiments remain useful when they are the cheapest way to test whether a mechanism is worth architectural attention. The rule is to **match the method to the current uncertainty**.

## Diminishing-return and stop decision

The Story-Instance Relationship Extraction campaign remains suspended. Do not start Attempt 10, V1.2/V2, another extraction harness, or another transport-qualification campaign by default.

The architecture and merged deterministic vertical slice show that the current P0 implementation path can use declared and deterministically derived story-instance relations without automatic extraction.

A desire to populate more graph edges, make the architecture feel complete, or resume the previous experiment is not a sufficient reopening reason.

## Extraction reopening gate

Reopen automatic relationship-extraction research only when a concrete user/product capability requires a relationship that meets all of these conditions:

1. it cannot reasonably be declared in an accepted owning artifact;
2. it cannot be deterministically derived from accepted structure/history; and
3. it materially affects a user-facing decision strongly enough that interpretive inference would create real product value.

A reopened experiment must state the concrete capability, relationship mechanism, authority boundary, acceptance criteria, and claim ceiling before execution.

## What remains unestablished

This sequence does not establish:

- a universal story relationship ontology;
- reliable open-world relationship extraction;
- automatic arbitrary pressure inference;
- cross-story generalization;
- a need for a graph database;
- a complete commitment-lifecycle implementation;
- scalable 50/100+ entry context selection;
- human comprehension or usability of Global Map/Focus; or
- that interpretive relations should become authoritative.

Those remain separate questions and should be addressed only when they materially affect the next product capability.

## Repository decision

Keep historical experiment protocols, run evidence, invalidation records, and qualifying results append-only. Do not rewrite invalidated attempts into product evidence.

Use this retrospective as the cross-campaign process synthesis. Do not create another general research-governance layer from this work unless a genuinely new recurring governance problem appears.

Current decision:

`ARCHITECTURE VALUE ESTABLISHED ENOUGH TO BUILD; DETERMINISTIC P0 SLICE PROVEN; EXTRACTION RESEARCH SUSPENDED UNTIL A CONCRETE PRODUCT NEED CROSSES THE REOPENING GATE.`
