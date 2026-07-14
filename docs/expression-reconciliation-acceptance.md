# Reconciliation acceptance orchestration

Acceptance is a provenance decision, not merely an editorial preference: it
selects the canonical source revision for future transformations. Publication
creates durable proposed candidates; acceptance is explicit and independent.

## Scope

V1 supports independent `accept`, `reject`, and `defer` decisions for published
Scene Expression and Chapter transition candidates. Preview Chapters,
unresolved findings, Structure, Realization, markerless material, and manual
mapping remain inspectable but are not decidable here.

Each decision is recorded under the publication directory:

```text
publications/<publication-id>/decisions/decision_<id>.yaml
```

Decision records preserve candidate snapshots, target snapshots, author,
rationale, result, and source plan/inspection/proposal provenance. Decisions
are append-only; changing a decision is not supported in V1.

## Candidate decisions

Scene acceptance reuses `ExpressionStore.accept()` after live freshness checks.
It changes only the Scene accepted pointer and preserves the previous accepted
revision. Scene rejection reuses `reject()`. Deferral is orchestration metadata
and does not alter the underlying candidate lifecycle.

Transition decisions use the transition-candidate adapter. Acceptance validates
ID, revision, hash, and boundary, preserves the previous transition revision,
and updates only the accepted transition pointer. Adjacent Scenes and
Realizations are never modified.

Stale candidates cannot be ordinarily accepted. They may be revalidated or have
intentional divergence acknowledged using existing Scene lifecycle semantics.
Rejection and deferral preserve stale candidates and record stale context.

## Independence and review states

Candidates are independently reviewable unless explicit publication metadata
declares a dependency. Undeclared model-suspected dependencies are advisory.
Explicitly linked candidates are blocked for independent acceptance until a
future grouped-decision workflow exists.

Publication review is derived, not canonical state:

```text
published → under_review → partially_decided → all_candidates_decided
                         ↘ blocked
```

`all_candidates_decided` does not mean reconciled. Deferred candidates count as
decided but are not accepted. The preview remains `derived`, `proposed`,
`noncanonical`, and `application_preview`; no preview can become canonical.

Recomposition and Chapter acceptance are intentionally outside this slice.
Canonical Chapter Expression may only be recomposed later from accepted Scene
and transition revisions.

## CLI

```bash
auteur expression reconcile review <publication> --project PROJECT
auteur expression reconcile decide <candidate> --accept --by author --project PROJECT
auteur expression reconcile decide <candidate> --reject --by author --reason "..." --project PROJECT
auteur expression reconcile decide <candidate> --defer --by author --reason "..." --project PROJECT
auteur expression reconcile decisions <publication> --project PROJECT
```

`--json` and `--verbose` expose technical provenance. There is no publication-
wide accept command, recomposition command, Chapter acceptance command, or
completion command in V1.
