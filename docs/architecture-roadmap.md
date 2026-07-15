# Auteur Architecture Roadmap

This document connects the project’s foundational architecture documents and
records the next architectural domain. It is a navigation and integrity review,
not a generic workflow design.

The stable principles governing all future extensions are recorded in
[Architecture Constitution](architecture-constitution.md).

## Meta-architecture: rules and artifacts

Auteur consists of two orthogonal systems:

1. Architectural capabilities that govern behavior.
2. Narrative artifacts that represent the author's work.

Architecture defines the rules; artifacts embody the story. Every architectural
capability exists to govern, analyze, or evolve artifacts, but none of those
capabilities is itself part of the narrative.

### Architectural capabilities

```text
Narrative Ontology
        ↓
Narrative Architecture
        ↓
Provenance Architecture
        ↓
Transformation Architecture
        ↓
Reasoning Architecture
        ↓
Critic Integration Contract
        ↓
Critic Registry
        ↓
Reasoning Runtime
        ↓
Author Workflow
```

### Narrative artifacts

```text
Ontology
        ↓
Story Identity
        ↓
Blueprint
        ↓
Chapter Structure
        ↓
Scene Realization
        ↓
Scene Expression
        ↓
Chapter Expression
        ↓
Manuscript
```

Narrative artifacts are not architectural layers. They are concrete instances
of the Narrative Architecture, just as records are instances of a data model.
The governing capabilities operate on those artifacts without becoming story
content.

| Capability | Governs |
|---|---|
| Narrative Ontology | Entities, relationships, types, and semantic definitions |
| Narrative Architecture | Semantic ownership and constraints |
| Provenance Architecture | Revision history and authority |
| Transformation Architecture | Legal movement between artifacts |
| Reasoning Architecture | Explainable recommendations about artifacts |
| Critic Integration Contract | How implementations produce reasoning reports |
| Critic Registry | Critic identity, discovery, compatibility, and dependencies |
| Reasoning Runtime | Selection and execution of critics |
| Author Workflow | Human interaction with artifacts and decisions |

## The four completed foundations

### Narrative Architecture — what knowledge exists

The canonical semantic model is:

```text
Ontology → Identity → Structure → Realization → Expression
```

Canonical narrative facts are owned at their semantic scope. Expression renders
realized facts but does not silently redefine upstream meaning.

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
accepted source → candidate → proposal → plan → publication
→ independent decision → accepted-source recomposition
→ comparison → Chapter acceptance → reconciliation completion
```

No stage silently changes authority.

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

## Conceptual integrity review

The foundations are coherent because each answers a different question:

| Question | Owning architecture |
|---|---|
| What exists and what does it mean? | Narrative Architecture |
| Which revision is authoritative? | Provenance Architecture |
| How may knowledge move or change form? | Transformation Architecture |
| Why should a change be recommended? | Reasoning Architecture |

The main terminology risk is using “validation,” “diagnosis,” “proposal,” and
“acceptance” interchangeably. Validation should report evidence; diagnosis
should explain a problem; proposals should suggest an author-decidable change;
acceptance should change authority.

### Reasoning Architecture — why change is justified

Reasoning is distinct from transformation. A transformation answers how an
approved change moves between artifacts. Reasoning answers why a change is
recommended and what evidence supports it.

Recommended conceptual chain:

```text
observation → evidence → claim → confidence → recommendation → proposal
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

This should begin as a deterministic contract around existing critic and
analyzer findings, not as a generic AI workflow engine.

## Intentionally deferred capabilities

- grouped candidate decisions and dependency transactions;
- markerless manual mapping;
- paragraph movement across ownership boundaries;
- Scene merge and split;
- advanced round-trip manuscript reconciliation;
- broad normalization of every cross-domain transformation;
- collaboration, voting, merge queues, and generic workflow engines.

These are extension points, not violations of the V1 foundations.

## Recommended sequence

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

## Review conclusion

Auteur has four stable foundational architectures: Narrative, Provenance,
Transformation, and Reasoning. The Critic Integration Contract, Critic Registry,
and Reasoning Runtime operationalize those foundations. The remaining work is
vertical author workflow and capability refinement, not another foundational
architecture.

## Product coverage and pilot

The architecture suite is mostly complete for V1, but product completeness is
uneven across artifact scopes. The detailed coverage matrix and bounded pilot
protocol are in `docs/capability-coverage.md`. Use that inventory and a real
five-to-ten-chapter project to select the next implementation from author
friction, with structural revision propagation as the leading candidate only
if the pilot confirms it.
