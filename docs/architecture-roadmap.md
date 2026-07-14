# Auteur Architecture Roadmap

This document connects the project’s foundational architecture documents and
records the next architectural domain. It is a navigation and integrity review,
not a generic workflow design.

## The three completed foundations

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
| Why should a change be recommended? | Not yet formalized |

The main terminology risk is using “validation,” “diagnosis,” “proposal,” and
“acceptance” interchangeably. Validation should report evidence; diagnosis
should explain a problem; proposals should suggest an author-decidable change;
acceptance should change authority.

## The next architectural pillar: Reasoning Architecture

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
3. Adapt existing critic/analyzer findings into that contract without mutation.
4. Connect reasoning recommendations to existing proposal generation.
5. Dogfood author-facing explanations and confidence boundaries.
6. Revisit grouped decisions only when explicit dependencies recur in real use.

## Review conclusion

Auteur has three stable foundational architectures: Narrative, Provenance, and
Transformation. The next major investment should be Reasoning Architecture,
because the remaining core question is no longer how information moves, but why
the system recommends that it move.
