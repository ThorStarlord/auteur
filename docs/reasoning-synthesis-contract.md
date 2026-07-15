# Auteur Reasoning Report Synthesis Contract

The Synthesis Contract defines how multiple derived Reasoning Reports become a
single author-facing review. Synthesis organizes and compares reasoning; it
does not replace the reports or make a diagnosis canonical.

```text
Reasoning Reports
    ↓
normalize references
    ↓
detect overlap and conflict
    ↓
group related claims
    ↓
rank and summarize
    ↓
Derived Narrative Review
```

## Input contract

A synthesis request names complete, provenance-valid Reasoning Reports and a
review scope. Each report retains its report ID, critic identity/version,
source revisions/hashes, confidence method, claims, evidence, and
recommendations. Missing or stale reports are recorded as unavailable; they
are never silently treated as agreement.

## Output contract

The derived review contains:

```yaml
review_id:
artifact_type: reasoning_review
source_reports:
  - report_id:
    critic_id:
    report_revision:
groups:
  - group_id:
    claim_refs: []
    overlap_basis:
    summary:
conflicts:
  - conflict_id:
    claim_refs: []
    conflict_type:
    explanation:
priorities:
  - group_id:
    rank_basis:
    rank:
recommendations:
  - recommendation_ref:
    supporting_claim_refs: []
    alternatives: []
confidence:
  method:
  explanation:
provenance:
  source_reports: []
  created_at:
status: derived
```

Every group and conflict points back to its source claims. A summary may be
shorter than its sources, but it must not erase contradictory claims,
alternative recommendations, or incompatible confidence methods.

## Overlap and conflict

Overlap is an explicit relation supported by declared evidence such as shared
artifact targets, rules, source spans, or normalized terms. Similar wording
alone is not proof of identical meaning.

Conflict is preserved when reports disagree about interpretation, severity,
scope, confidence, or recommended action. The review identifies the conflict
and its evidence; it does not choose a winner merely because one critic ran
first or has a higher uncalibrated score.

## Ranking and recommendations

Priorities are derived from declared inputs such as severity, evidence count,
scope impact, freshness, and a documented ranking method. Confidence scores
from different methods are not numerically combined without a calibration
contract. Unknown confidence remains unknown.

Recommendations remain alternatives linked to their claims. Synthesis may
highlight common or conflicting recommendations, but it cannot create a
proposal, publish a candidate, accept a revision, or mutate narrative state.

## Provenance and freshness

The review records every source report and the report revisions/hashes used.
If any source report becomes stale, the review is stale or must be recomputed.
Recomputation creates a new derived review and does not overwrite the source
reports or prior review history.

## Invariants

1. Synthesis is read-only and produces only a derived review.
2. Every group, conflict, priority, and recommendation retains source refs.
3. Overlap and conflict are distinct and explicitly explained.
4. Disagreement is preserved; synthesis never silently canonizes a conclusion.
5. Confidence methods are not combined without declared calibration.
6. Stale or missing inputs are visible and cannot appear as agreement.
7. Synthesis cannot create proposals, publish candidates, or change authority.
8. Repeated synthesis over identical reports is deterministic.
9. Source reports and prior reviews remain append-only/versioned.

## Deferred concerns

Natural-language rewriting, model-based semantic similarity, author UI,
workflow completion, collaborative review, and automatic proposal generation
are deferred. A first implementation may use deterministic references and
normalized rule/target keys before adding richer comparison.

