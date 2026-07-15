# Auteur Architecture Constitution

This document records the principles that govern Auteur's foundations and
should change only through an explicit architectural decision. Product
capabilities may expand around these principles without weakening them.

## Fundamental questions

| Question | Governing architecture |
|---|---|
| What exists and what does it mean? | Narrative Architecture |
| Which revision is authoritative? | Provenance Architecture |
| How may knowledge move or change form? | Transformation Architecture |
| Why is a change recommended? | Reasoning Architecture |

## Architecture and artifacts

Architecture defines rules; narrative artifacts embody the author's story.
Identity, Structure, Realization, Expression, manuscripts, and future Book or
Series artifacts are governed instances, not architectural layers themselves.

## Authority vocabulary

- **Canonical**: the current accepted revision owned at a defined scope.
- **Derived**: an explanatory, analyzed, or assembled artifact that is not a
  competing source of truth.
- **Candidate**: durable proposed work awaiting an explicit decision.
- **Publication**: transactional persistence of proposed candidates; it is not
  acceptance.
- **Acceptance**: an explicit lifecycle operation that changes authority at the
  owning artifact scope.

## Core invariants

1. Authority is always owned by the lifecycle of the target artifact.
2. Expression does not silently change Realization, Structure, Identity, or
   Bible/state.
3. Publication never implies acceptance.
4. Candidate decisions are independent unless an explicit dependency contract
   requires a transaction.
5. Chapter recomposition uses accepted source revisions only.
6. Chapter recomposition is not Chapter acceptance.
7. Chapter acceptance is not reconciliation completion.
8. Reasoning reports and critic outputs are derived and read-only with respect
   to narrative authority.
9. Evidence identifies its source artifact, revision, and content hash when
   the source is revisioned.
10. Stale inputs block unsafe promotion or make dependent derived output stale;
    newer revisions are never substituted silently.
11. Transformations are explicit, provenance-rich, freshness-validated, and
    failure-atomic at their declared boundary.
12. Failed workflows leave no partial canonical mutation.
13. Prior revisions and decisions remain inspectable; new work does not erase
    author history.
14. Derived artifacts may organize, compare, or explain source artifacts, but
    may not silently replace or canonize them.

## Extension test

Every new capability should answer these questions before implementation:

- Which narrative artifact does it own or govern?
- Is its output canonical, derived, or a candidate?
- Which existing acceptance boundary changes authority?
- What provenance and freshness dependencies does it record?
- What happens on stale input or partial failure?
- How does it prove zero mutation outside its declared scope?

If a capability cannot answer these questions, it is not ready to cross a
canonical boundary.

## Product direction

The constitution does not prescribe which product capability comes next. That
choice is evidence-driven:

```text
run the canonical reference → observe author friction → choose one bounded gap
→ implement → verify against the constitution and the reference
```

Book-level workflow, Series workflows, export, additional critics, author UX,
collaboration, and plugins are extensions built on these foundations. They do
not require another foundational architecture unless implementation evidence
proves otherwise.
