# Auteur Architecture Roadmap

This document connects the project's foundational architecture documents and
records architecture-specific extension history and integrity rules. It is a
navigation and integrity review, not the current generic product roadmap.

For current product/repository evolution candidates, use
[Product Evolution Roadmap](product-evolution-roadmap.md). For currently selected
work and exact repository state, use [Repository Status](../STATUS.md).

The stable principles governing all future extensions are recorded in
[Architecture Constitution](architecture-constitution.md).

## Current Role

The foundational architecture sequence described below is substantially
established. The historical Reasoning Architecture -> Critic Integration ->
Registry -> Runtime sequence records how the current platform reached that state;
it should not be interpreted as the present implementation queue.

The current architectural conclusion remains:

> Auteur does not need another foundational architecture by default. New domain
> concepts should be admitted only when real author/product friction cannot be
> solved cleanly through existing architecture, workflow, presentation, or
> reusable craft knowledge.

Narrative Ontology V2 follows this rule: it reconciles and consolidates the
existing Layer-0 contract; it is not a fifth foundational architecture or a new
research campaign.

Selection among product directions belongs in
[product-evolution-roadmap.md](product-evolution-roadmap.md). Exact active work
belongs in `STATUS.md` and bounded issues/plans.

## Meta-architecture: rules and artifacts

Auteur consists of two orthogonal systems:

1. Architectural capabilities that govern behavior.
2. Narrative artifacts that represent the author's work.

Architecture defines the rules; artifacts embody the story. Every architectural
capability exists to govern, analyze, or evolve artifacts, but none of those
capabilities is itself part of the narrative.

### Architectural capabilities

```text
Narrative Architecture
  includes Layer-0 Narrative Ontology semantics
        |
        v
Provenance Architecture
        |
        v
Transformation Architecture
        |
        v
Reasoning Architecture
        |
        v
Critic Integration Contract
        |
        v
Critic Registry
        |
        v
Reasoning Runtime
        |
        v
Author Workflow
```

Narrative Ontology is the semantic substrate of Narrative Architecture: concepts,
relation vocabulary, and deterministic semantic invariants. Keeping it inside
the Narrative Architecture foundation avoids implying that Ontology is a fifth
foundational architecture beside Narrative/Provenance/Transformation/Reasoning.

### Narrative artifacts

```text
Story Identity
        |
        v
Blueprint / Structure
        |
        v
Scene Realization
        |
        v
Scene Expression
        |
        v
Chapter/Segment Expression
        |
        v
Manuscript
```

Ontology is deliberately absent from this artifact chain. Ontology supplies
vocabulary to every semantic layer; it is not normally a story-instance artifact
that is transformed into Story Identity.

Narrative artifacts are concrete instances governed by the Narrative
Architecture, just as records are instances of a data model. The governing
capabilities operate on those artifacts without becoming story content.

| Capability | Governs |
|---|---|
| Narrative Ontology (inside Narrative Architecture) | Reusable concepts, relation types, semantic vocabulary, deterministic semantic invariants |
| Narrative Architecture | Semantic ownership, scope independence, and constraints |
| Provenance Architecture | Revision history and authority |
| Transformation Architecture | Legal movement between artifacts |
| Reasoning Architecture | Explainable recommendations about artifacts |
| Critic Integration Contract | How implementations produce reasoning reports |
| Critic Registry | Critic identity, discovery, compatibility, and dependencies |
| Reasoning Runtime | Selection and execution of critics |
| Author Workflow | Human interaction with artifacts and decisions |

## The four completed foundations

### Narrative Architecture — what narrative knowledge exists and who owns it

The canonical semantic model remains five layers:

```text
Ontology -> Identity -> Structure -> Realization -> Expression
```

The arrow from Ontology means "supplies vocabulary" rather than "a project
ontology artifact is transformed into Identity". Identity, Structure,
Realization, and Expression own story-instance knowledge of their respective
kinds.

Canonical narrative facts are owned at their semantic scope. Expression renders
realized facts but does not silently redefine upstream meaning.

Narrative artifacts are additionally classified by independent scope, authority,
and revision/temporal coordinates. See `docs/narrative-architecture.md`.

### Provenance Architecture — how authority evolves

Artifacts carry lifecycle, authority, revision, dependency, freshness, and
accepted-pointer information. Acceptance creates a new canonical revision while
preserving prior history. Staleness blocks unsafe promotion rather than hiding
drift.

### Transformation Architecture — how knowledge moves

Transformations declare inputs, outputs, authority change, provenance,
validation, staleness, acceptance, and failure atomicity. The proven Expression
path is:

```text
accepted source -> candidate -> proposal -> plan -> publication
-> independent decision -> accepted-source recomposition
-> comparison -> Chapter acceptance -> reconciliation completion
```

No stage silently changes authority.

### Reasoning Architecture — why change is justified

Reasoning is distinct from transformation. A transformation answers how an
approved change moves between artifacts. Reasoning answers why a change is
recommended and what evidence supports it.

Recommended conceptual chain:

```text
observation -> evidence -> claim -> confidence -> recommendation -> proposal
```

Reasoning outputs remain derived. They must not mutate canonical artifacts or
implicitly create accepted candidates. Transformation consumes a recommendation
only after explicit proposal and author decision boundaries.

Minimum reasoning vocabulary:

```yaml
observation:
evidence:
claim:
confidence:
recommendation:
candidate_transformations:
```

This began as a deterministic contract around existing critic and analyzer
findings rather than as a generic AI workflow engine. That architectural choice
remains valid even though the implementation sequence below is now historical.

## Unified authority constitution

- Canonical means the current accepted revision at the owning scope.
- Derived means explanatory or assembled output that is not a new source of truth.
- Candidate means durable proposed work awaiting an explicit decision.
- Publication is not acceptance.
- Recomposition is not Chapter acceptance.
- Chapter acceptance is not reconciliation completion.
- Canonical Chapter composition uses accepted Chapter Structure, accepted Scene
  Expressions, and accepted transitions only.
- Expression workflows do not mutate Realization, Structure, Identity, or Bible/state.
- Ontology vocabulary cannot accept, promote, or mutate story-instance authority.

## Conceptual integrity review

The foundations are coherent because each answers a different question:

| Question | Owning architecture |
|---|---|
| What narrative knowledge exists, what does it mean, and which semantic layer owns it? | Narrative Architecture (including Narrative Ontology) |
| Which revision is authoritative? | Provenance Architecture |
| How may knowledge move or change form? | Transformation Architecture |
| Why should a change be recommended? | Reasoning Architecture |

The main terminology risk is using "validation," "diagnosis," "proposal," and
"acceptance" interchangeably. Validation should report evidence; diagnosis
should explain a problem; proposals should suggest an author-decidable change;
acceptance should change authority.

Narrative Ontology V2 further divides ontology rules into schema constraints,
semantic invariants, craft heuristics, and interpretive criteria so subjective
craft advice cannot masquerade as deterministic validity.

## Intentionally deferred capabilities

- grouped candidate decisions and dependency transactions;
- markerless manual mapping;
- paragraph movement across ownership boundaries;
- Scene merge and split;
- advanced round-trip manuscript reconciliation;
- broad normalization of every cross-domain transformation;
- collaboration, voting, merge queues, and generic workflow engines;
- broad Book/Chapter persistence migration to Entry/Segment terminology.

These are extension points, not violations of the V1 foundations. Their current
product priority, if any, belongs in the Product Evolution Roadmap rather than
being inferred from this list.

## Historical implementation sequence — largely completed

The sequence below records the architecture program that established the current
Reasoning/critic/runtime foundation. It is retained for historical orientation,
not as the present work queue.

1. Define the Reasoning Architecture vocabulary, evidence contract, and
   evaluation/acyclicity rules. See `docs/reasoning-architecture.md`.
2. Standardize analyzer-to-report adapters through
   `docs/critic-integration-contract.md`.
3. Define critic discovery and compatibility through `docs/critic-registry.md`.
4. Define runtime selection, dependency, freshness, and outcome boundaries in
   `docs/reasoning-runtime.md`.
5. Implement a minimal deterministic Reasoning Runtime slice.
6. Adapt existing critic/analyzer findings into that contract without mutation.
7. Aggregate reasoning reports and dogfood author-facing explanations.
8. Define derived multi-report review through
   `docs/reasoning-synthesis-contract.md`.
9. Connect reasoning recommendations to existing proposal generation.
10. Revisit grouped decisions only when explicit dependencies recur in real use.

Future work should not restart these steps merely because they remain listed
here. Inspect current implementation, `STATUS.md`, and contemporary product
evidence first.

## Review conclusion

Auteur has four stable foundational architectures: Narrative, Provenance,
Transformation, and Reasoning. Narrative Ontology is the Layer-0 semantic
substrate inside the Narrative Architecture foundation. The Critic Integration
Contract, Critic Registry, and Reasoning Runtime operationalize those
foundations. The remaining work is primarily vertical author workflow and
capability refinement, not another foundational architecture.

## Product coverage and evidence-driven selection

Architecture completeness and product completeness are different questions.
When a real author workflow exposes a gap, classify it before expanding the
architecture:

```text
run real workflow
-> observe friction
-> classify UX / workflow / craft knowledge / domain / infrastructure
-> choose the smallest correct intervention
-> implement
-> verify
```

Use [product-evolution-roadmap.md](product-evolution-roadmap.md) to preserve and
compare candidate directions, and [../STATUS.md](../STATUS.md) for the currently
selected implementation frontier. Historical coverage matrices, pilots, and
product-validation records remain evidence rather than a perpetual work queue.
