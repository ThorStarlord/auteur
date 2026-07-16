# Book Reconciliation Application (Phase B)

Phase A inspects an externally edited Book manuscript and routes ownership:
Chapter-local wording delegates to Chapter reconciliation, while Book-owned
separator, title, insertion, and order edits become derived, noncanonical Book
proposals. Phase B adds two capabilities on top of those proposals:

1. A derived **application plan** describing a chosen set of Book-owned
   proposals.
2. An **atomic publication** that materializes durable, unaccepted Book
   candidates plus a noncanonical preview and a publication manifest.

Publication is **not** acceptance. No accepted Book pointer, Chapter Expression,
Structure, Identity, Blueprint, Realization, or Scene is ever mutated.

## Authority model

| Artifact | Authority | Lifecycle | Canonical? |
|----------|-----------|-----------|------------|
| Book proposal (Phase A) | derived | proposed | no |
| Application plan | derived | planned | no |
| Book candidate | candidate | proposed | no |
| Application preview | derived | proposed (`role=application_preview`) | no |
| Publication manifest | derived | published | no (published ≠ accepted) |

A candidate is durable and unaccepted: it records what an application *would*
change without changing any accepted Book state. A candidate-backed preview can
never become canonical.

## Application plan

Path: `book/expression/reconciliation/plans/<plan_id>.yaml`

```yaml
plan_id: book_application_set_998cbfc7ca38c7d3
artifact_type: book_reconciliation_plan
authority: derived
lifecycle: planned
source_inspection_id: inspection_20260716051223724129
source_book_expression: book_01:expression_v001
source_book_revision: 1
source_book_hash: sha256:...
external_manuscript_hash: sha256:...
selected_proposals:
  - proposal_inspection_20260716051223724129_001
planned_outputs:
  - output_type: book_separator_candidate
    target_id: separator_01
    source_proposal_id: proposal_inspection_20260716051223724129_001
    planned_candidate_id: book_candidate_fce60cdf...   # SHA256(plan_id + proposal_id)
    original: "---"
    proposed: "***"
conflicts: []
freshness_results:
  - proposal_id: proposal_..._001
    classification: fresh
    reasons: []
readiness:
  status: ready
  reasons: []
transformation:
  id: expression.publish_book_application
  version: 1
```

Planning is deterministic and read-only: the same inspection and proposal
selection always produce the same `plan_id` and the same `planned_candidate_id`
(`candidate_id = SHA256(plan_id + proposal_id)`). Planning creates **no**
candidate, **no** preview, and changes **no** pointer.

A plan is rejected (readiness other than `ready`) when a selected proposal is
stale, unsupported, unresolved/invalid, or when the selection has duplicate
targets or conflicting Chapter-order proposals. Source and hash mismatches
against the inspection, and transformation-version mismatches, mark the proposal
stale or unsupported.

## Candidate model

Path: `book/expression/reconciliation/candidates/<candidate_id>.yaml`

Types: `book_separator_candidate`, `book_order_candidate`,
`book_title_rendering_candidate`, `book_inserted_material_candidate`.

```yaml
candidate_id: book_candidate_fce60cdf...
artifact_type: book_separator_candidate
authority: candidate
lifecycle: proposed
book_expression_id: book_01:expression_v001
target_id: separator_01
source_book_revision: 1
source_book_hash: sha256:...
original: "---"
proposed: "***"
source_inspection_id: inspection_...
source_proposal_id: proposal_..._001
source_plan_id: book_application_set_...
publication_id: book_publication_...
transformation:
  id: expression.publish_book_application
  version: 1
created_at: 2026-07-16T05:12:23+00:00
freshness:
  status: fresh
  reasons: []
```

Candidates are durable, unaccepted, and noncanonical. Publishing them does not
update any accepted Book state.

## Noncanonical preview

Path: `book/expression/reconciliation/previews/<publication_id>.yaml`

The preview describes the Book *as if* the selected candidates were applied,
drawing only on accepted Chapter Expressions, the accepted Book order (unless an
order candidate overrides it), and published Book-owned candidates. It records
`candidate_sources`, `accepted_chapter_sources`, `applied_proposals`, a
deterministic `content_hash` over the effective title/separator/order/chapters,
and `authority=derived`, `lifecycle=proposed`, `role=application_preview`,
`canonical=false`. The preview is not a Book Expression and blocks normal
acceptance.

## Live freshness gate

Immediately before staging, `publish` revalidates every live dependency from
disk (persisted readiness is never trusted): the plan exists and is `ready`, the
plan transformation, the absence of a prior publication, the inspection and its
transformation and marker contract, the accepted Book revision/hash and
freshness, every Chapter revision/hash and the Chapter order, the separator (and
title) still match each proposal's recorded original, the external manuscript
hash, every proposal's lifecycle/transformation/source, target IDs, and
duplicate targets. A stale plan yields a structured rejection:

```yaml
status: rejected_stale
reasons:
  - code: BOOK_OR_CHAPTER_REVISION_CHANGED
    recommended_action: create a new Book reconciliation plan
visible_outputs_created: false
```

## Atomic publication

Publication is all-or-nothing:

1. **Stage** every candidate, the preview, and the manifest under
   `book/expression/reconciliation/staging/<publication_id>/` (outside final
   paths).
2. **Validate** that all planned candidates are staged, that staged candidate
   IDs and targets match the plan, that the preview contains no Chapter-local
   proposals, and that no canonical/accepted state is touched.
3. **Publish** by moving every staged output into its final location.
4. **Roll back** on any failure: unlink each already-moved candidate, preview,
   and manifest, remove staging, and unlink the publication/preview if partially
   written.

The invariant is that all outputs are visible together or none are.

## Publication manifest

Path: `book/expression/reconciliation/publications/<publication_id>.yaml`

```yaml
publication_id: book_publication_998cbfc7ca38c7d3
artifact_type: book_reconciliation_publication
authority: derived
lifecycle: published
source_plan_id: book_application_set_998cbfc7ca38c7d3
source_inspection_id: inspection_...
source_book_expression: book_01:expression_v001
source_book_revision: 1
source_book_hash: sha256:...
external_manuscript_hash: sha256:...
published_candidates:
  - book_candidate_fce60cdf...
preview:
  book_expression_id: book_01:expression_v001:application_preview
  revision: 1
  content_hash: sha256:...
  authority: derived
  lifecycle: proposed
  role: application_preview
acceptance_status: none
accepted_book_pointer_changed: false
transformation:
  id: expression.publish_book_application
  version: 1
```

## Duplicate and stale handling

- **Duplicate**: a second publication of the same plan is rejected with
  `status=rejected_duplicate`, `visible_outputs_created=false`. No duplicate
  candidates are created and the original publication is preserved byte-for-byte.
- **Stale plan**: any change to the Book, a separator, the Chapter order, a
  Chapter revision, the external manuscript, or the transformation version
  blocks publication *before staging* — no candidate, preview, or manifest is
  created.
- **Post-publication**: candidates and previews that depend on a changed source
  become stale, while independent candidates remain fresh.

## Candidate decisions (decision lifecycle)

Once candidates are published, the author decides each one independently:
**accept**, **reject**, or **defer**. A decision is a durable, *immutable*
record — it does **not** recompose the Book, does **not** accept a candidate as
canonical, and does **not** move the accepted Book pointer.

Path: `book/expression/reconciliation/decisions/<decision_id>.yaml`

```yaml
decision_id: book_candidate_decision_...
artifact_type: book_candidate_decision
authority: decision            # distinct from candidate / accepted / derived
lifecycle: decided             # terminal
candidate_id: book_candidate_fce60cdf...
book_expression_id: book_01:expression_v001
candidate_type: book_separator_candidate
decision:
  status: accepted             # accepted | rejected | deferred
  reason: Author approved separator
  decided_at: 2026-07-16T14:30:00+00:00
source_candidate_id: book_candidate_fce60cdf...
source_candidate_revision: 1
source_candidate_hash: sha256:...   # snapshot of the decided candidate
transformation:
  id: expression.decide_book_candidate
  version: 1
freshness:
  status: fresh
  reasons: []
```

### Immutability

Decisions are terminal. There is exactly **one decision per candidate**; there
is no revocation and no amendment. The `decision_id` is deterministic
(`SHA256(candidate_id + status + reason)`), and a second decision on the same
candidate — with any status or reason — is rejected with a
`DuplicateDecisionError`. Prior decisions are preserved, never deleted.

### Live freshness gate at decision time

Before a decision is written, every dependency is revalidated from disk
(persisted candidate freshness is never trusted): the candidate is still a
proposed, unaccepted candidate; its source plan, publication, inspection, and
proposal still exist and are unchanged (plan/inspection transformations match);
the accepted Book revision and hash still match the candidate's recorded source;
and the candidate's target still exists. If anything changed, the decision is
refused with a structured rejection and **no** decision record is written:

```yaml
status: rejected_stale
reasons:
  - code: BOOK_OR_CHAPTER_REVISION_CHANGED
    expected: fresh
    current: stale
    recommended_action: publish a fresh Book candidate and decide again
visible_outputs_created: false
```

### Decision-aware preview (not recomposition)

Creating a decision regenerates the publication's preview from its decisions:
**accepted** candidates are applied, while **rejected**, **deferred**, and
still-**undecided** candidates are excluded. The regenerated preview is rebuilt
from accepted Chapter sources plus accepted Book-owned candidates and remains
`authority=derived`, `lifecycle=proposed`, `role=application_preview`,
`canonical=false`. This is a *preview* of what recomposition would produce — no
Book Expression is modified or accepted. The preview records `decision_aware:
true` and an `applied_decisions` list.

### Explicit preview-acceptance blocking

`BookExpressionStore._validate_acceptable_artifact` blocks preview acceptance by
**metadata**, not by path. An acceptable artifact must be `authority=accepted`,
must not carry `role=application_preview`, and must be `lifecycle=accepted`. A
derived, proposed preview fails all three and raises
`BookPreviewNotAcceptableError` ("Previews are derived and proposed; they cannot
become canonical accepted Book content."), replacing the previous incidental
`FileNotFoundError`.

## CLI

```bash
auteur expression plan-book-reconciliation <inspection> \
  --proposal <proposal-id> --proposal <proposal-id> --project PROJECT
auteur expression show-book-plan <plan> --project PROJECT
auteur expression publish-book-reconciliation <plan> --project PROJECT
auteur expression inspect-book-publication <publication> --project PROJECT

auteur expression accept-book-candidate <candidate> --reason "text" --project PROJECT
auteur expression reject-book-candidate <candidate> --reason "text" --project PROJECT
auteur expression defer-book-candidate  <candidate> --reason "text" --project PROJECT
auteur expression show-book-candidate-decision <decision> --project PROJECT
```

Normal output names the source Book, selected proposals, readiness, published
candidates, the preview status, `Acceptance status: none`, `Accepted Book
pointer changed: no`, and a recommended next action. Decision output names the
candidate, the decision and reason, `Preview updated: yes`, and `Book pointer
changed: no`. Hashes and full metadata are shown only behind `--json` and
`--verbose`.

The decision commands record accept/reject/defer only. There are still
intentionally **no** `apply-book-proposal`, `recompose-book-reconciliation`, or
`complete-book-reconciliation` commands: candidate *acceptance into canonical
Book content*, Book recomposition, and reconciliation completion remain out of
scope.

## Non-goals

This slice does not implement Book recomposition from accepted candidates,
acceptance of a recomposed Book, or reconciliation completion. Decisions record
author intent and regenerate a derived preview; they never mutate any accepted
or canonical artifact.
