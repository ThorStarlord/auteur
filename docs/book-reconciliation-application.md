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
| Candidate decision | decision | decided | no |
| Accepted Book-owned source | accepted | accepted | no (immutable recomposition input, not the Book pointer) |
| Current accepted-source pointer | pointer | current | no (names the current accepted revision per element) |

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

## Candidate decisions (decision lifecycle) — Model A (append-only)

Once candidates are published, the author decides each one independently:
**approve**, **reject**, or **defer**. Terminology is deliberate:

- **Approve** = "use this candidate in the next recomposition." A *workflow*
  decision. Approving materializes a durable **accepted Book-owned source** (see
  below) that a future recomposition reads.
- **Reject** = "do not use this candidate."
- **Defer** = "not deciding yet." **Defer is nonterminal**: a deferred candidate
  can later be approved or rejected.

The word **accept** is reserved for a later, separate step — accepting a
*recomposed Book* as canonical (out of scope in this slice). Candidate decisions
never use "accept".

Each decision is a durable, immutable record, but a candidate may be decided
more than once. Decisions form an **append-only history**; the **latest**
decision (highest `decision_sequence`) is the active one and supersedes all
priors. A decision does **not** recompose the Book, does **not** accept a
candidate as canonical, and does **not** move the accepted Book pointer.

Path: `book/expression/reconciliation/decisions/<decision_id>.yaml`

```yaml
decision_id: book_candidate_decision_...
artifact_type: book_candidate_decision
authority: decision            # distinct from candidate / accepted / derived
lifecycle: decided
candidate_id: book_candidate_fce60cdf...
book_expression_id: book_01:expression_v001
candidate_type: book_separator_candidate
decision:
  status: approved             # approved | rejected | deferred
  reason: Author approved separator
  decided_at: 2026-07-16T14:30:00+00:00
decision_sequence: 2           # append-only ordinal; latest wins
supersedes: book_candidate_decision_...   # prior active decision, or null
source_candidate_id: book_candidate_fce60cdf...
source_candidate_revision: 1
source_candidate_hash: sha256:...   # snapshot of the decided candidate
source_book_revision: 1             # Book snapshot; recomposition compares this
source_book_hash: sha256:...
accepted_source_id: book_accepted_separator_v001_...   # only on approval
accepted_source_path: .../accepted-sources/book_accepted_separator_v001_....yaml
transformation:
  id: expression.decide_book_candidate
  version: 1
freshness:
  status: fresh
  reasons: []
```

### Append-only history and superseding

A candidate may be decided any number of times: the natural workflow is
`pending → deferred → approved`. Each `decide_candidate` call appends a new
immutable record carrying an incrementing `decision_sequence` and a `supersedes`
pointer to the prior active decision. Only the **latest** decision counts for the
preview and for recomposition; prior records are preserved as the audit trail and
are never deleted. The `decision_id` is deterministic
(`SHA256(candidate_id + status + reason + sequence)`).

`book_candidate_decision_history(candidate_id)` returns the ordered history plus
the `active_status` / `active_decision_id`. The CLI exposes this as
`book-candidate-history`.

### Accepted Book-owned sources (produced on approval)

Approving a candidate is not itself narrative acceptance, but it *does* produce a
durable, accepted Book-owned **source** artifact — distinct from the candidate —
that recomposition reads. Recomposition reads accepted sources, **not** decisions.

Path: `book/expression/reconciliation/accepted-sources/<accepted_source_id>.yaml`

| Candidate type | `owned_kind` | Revises |
|----------------|--------------|---------|
| `book_separator_candidate` | `separator` | Book separator |
| `book_order_candidate` | `order` | Chapter assembly order |
| `book_title_rendering_candidate` | `title` | Title rendering |
| `book_inserted_material_candidate` | `material` | Inserted material |

```yaml
accepted_source_id: book_accepted_separator_v001_...
artifact_type: accepted_book_owned_source
owned_kind: separator
authority: accepted            # distinct from candidate/derived/decision
lifecycle: accepted
book_expression_id: book_01:expression_v001
target_id: separator_01
revision: 1                    # bumps per (book, target, kind) on re-approval
source_decision_id: book_candidate_decision_...
source_candidate_id: book_candidate_fce60cdf...
original: "---"
proposed: "***"
transformation:
  id: expression.accept_book_owned_source
  version: 1
```

### Accepted-source authority: three decoupled tiers

Decision history, accepted revisions, and the current pointer are three distinct
things. The earlier model derived all three from "latest decision", which let a
later defer or reject silently revoke a previously accepted revision. They are now
decoupled:

1. **Decision history (Tier 1 — immutable, append-only).** Every approve, reject,
   and defer is recorded with a `decision_sequence` and a `supersedes` pointer.
   The latest decision is current author *intent*; prior records are the audit
   trail and are never deleted.

2. **Accepted Book-owned revisions (Tier 2 — immutable once written).** Each
   *approval* mints a new revision (`revision: 1`, `2`, …) at
   `accepted-sources/<accepted_source_id>.yaml`. A revision is never modified or
   deleted; re-approval writes a *new* revision beside the old one.

3. **Current accepted-source pointer (Tier 3 — the only mutable tier).** One
   pointer per Book-owned element, keyed by `(owned_kind, element_id)`, at
   `accepted-sources/pointers/<pointer_id>.yaml`. It names the revision that is
   *currently* accepted and carries an append-only `history` of every move.

```yaml
pointer_id: book_pointer_separator_...
artifact_type: current_accepted_source_pointer
authority: pointer
lifecycle: current
owned_kind: separator
element_id: separator_01
current_revision: 2
current_accepted_source_id: book_accepted_separator_v002_...
active_decision_id: book_candidate_decision_...
history:                          # append-only; one entry per approval
  - revision: 1
    accepted_source_id: book_accepted_separator_v001_...
    decision_id: book_candidate_decision_...aaa
  - revision: 2
    accepted_source_id: book_accepted_separator_v002_...
    decision_id: book_candidate_decision_...bbb
```

**Semantics by decision:**

- **Approve** — mints a new immutable revision (Tier 2) and moves the pointer
  (Tier 3) to it. The decision records `pointer_moved: true`.
- **Defer** — records intent (Tier 1) only. `pointer_moved: false`; no revision,
  no pointer move. Deferral means "take no new action", not "revoke".
- **Reject** — records intent (Tier 1) only. `pointer_moved: false`; the
  previously accepted revision remains current. Rejection prevents the preview
  from being interpreted as an *undecided* candidate but does **not** revoke
  accepted authority — an explicit revert operation (future work) would be
  required to move the pointer back.

**Consumption.** `current_accepted_source_pointer(element_id, owned_kind)` returns
the pointer (or `None` if the element was never approved).
`current_accepted_source(element_id, owned_kind)` resolves the pointer to its
immutable revision — this is what recomposition reads. It reads pointers, **not**
decisions. `current_accepted_sources(publication_id)` (aliased by the legacy name
`active_accepted_sources`) returns the exact set a recomposition of that
publication would consume. `accepted_source_history(element_id, owned_kind)`
returns every revision ever written (Tier 2); `pointer_history(element_id,
owned_kind)` returns only the authority-boundary crossings (approvals), so it is
strictly shorter than the decision history whenever defers/rejects occurred.

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

### Pointer-based preview (not recomposition)

Creating a decision regenerates the publication's preview from the **current
accepted-source pointers**, not from raw decisions. A candidate is applied when
its element's pointer names a revision that originated from this publication's
candidate. Because the preview and recomposition both read pointers, the preview
faithfully mirrors what a recomposition would produce:

- An *approved* candidate is applied.
- A candidate that was approved and then *deferred* or *rejected* stays applied —
  the pointer was never moved, so accepted authority persists.
- A candidate that was only ever deferred/rejected (or is still undecided) has no
  pointer and is excluded.

The regenerated preview is rebuilt from accepted Chapter sources plus
pointer-current Book-owned candidates and remains `authority=derived`,
`lifecycle=proposed`, `role=application_preview`, `canonical=false`. It records
`decision_aware: true`, `pointer_based: true`, an `applied_decisions` list (each
entry carries the latest `status` and a `pointer_current` flag), and a
`current_pointers` summary. No Book Expression is modified or accepted.

### Book-change freshness gate for recomposition

Approving a candidate snapshots the Book revision/hash it was decided against.
`assess_recomposition_freshness(publication_id)` is the read-only gate a future
recomposition MUST pass:

- **Scenario A (Book revision changes after approval):** if the accepted Book
  advances after an approval, the snapshot no longer matches the current Book.
  The gate returns `status=blocked_stale_book` with structured reasons
  (`BOOK_REVISION_CHANGED`, `BOOK_HASH_CHANGED`, or
  `BOOK_OR_CHAPTER_REVISION_CHANGED`) and
  `recommended_action: "Book changed since decision. Re-approve or create a new
  decision."` Recomposition is **rejected** until the author re-decides for the
  new Book.
- **Scenario B (a source separator/order the candidate captured changes):**
  candidates capture the source element's state at publication time; the
  decision-time freshness gate already rejects a decision whose target moved.
  Recomposition remains read-only and deterministic over the captured snapshot.

The gate is **pointer-based**: it checks every accepted source the publication's
pointers currently name (the exact set recomposition would consume), comparing
each source's captured Book revision/hash against the live Book. A publication
whose elements have no pointer — never approved, or only ever deferred/rejected —
is always `ready` (there is nothing current to be stale). Because a defer/reject
never moves a pointer, an approve-then-reject element is still checked here: its
revision is still current, so a later Book change still blocks recomposition.

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

auteur expression approve-book-candidate <candidate> --reason "text" --project PROJECT
auteur expression reject-book-candidate  <candidate> --reason "text" --project PROJECT
auteur expression defer-book-candidate   <candidate> --reason "text" --project PROJECT
auteur expression show-book-candidate-decision <decision> --project PROJECT
auteur expression book-candidate-history <candidate> --project PROJECT
```

`approve-book-candidate` replaces the former `accept-book-candidate`: "accept" is
reserved for accepting a recomposed Book. Normal output names the source Book,
selected proposals, readiness, published candidates, the preview status,
`Acceptance status: none`, `Accepted Book pointer changed: no`, and a recommended
next action. Decision output names the candidate, the decision, reason, and
`decision_sequence`, any superseded decision, the accepted Book-owned source (on
approval), `Preview updated: yes`, and `Book pointer changed: no`. Hashes and full
metadata are shown only behind `--json` and `--verbose`.

The decision commands record approve/reject/defer only. There are still
intentionally **no** `apply-book-proposal`, `recompose-book-reconciliation`, or
`complete-book-reconciliation` commands: candidate *acceptance into canonical
Book content*, Book recomposition, and reconciliation completion remain out of
scope.

## Book Comparison (Phase C2)

Comparison is a read-only, deterministic evaluation of whether a pointer-based
recomposition (Phase C1) matches its external manuscript. The result is:

```yaml
authority: derived
lifecycle: evaluated
role: reconciliation_comparison
canonical: false
```

It never accepts, mutates, or changes any source. It moves no pointer, completes
no reconciliation, and generates no automatic proposals.

Path: `book/expression/reconciliation/comparisons/<comparison_id>.yaml`

```yaml
authority: derived
lifecycle: evaluated
role: reconciliation_comparison
canonical: false
comparison_id: book_comparison_<sha256[:32]>
source_recomposition_id: book_recomposition_<publication_id>
source_recomposition_hash: sha256:...
source_publication_id: book_publication_...
external_manuscript:
  path: /abs/path/to/manuscript.md
  content_hash: sha256:...          # captured at comparison time
  marker_contract_version: 1
source_book_revision: 1
source_book_hash: sha256:...
chapter_sources:
  - chapter_id: chapter_01
    accepted_expression_id: chapter_01:expression_v001
    revision: 1
    content_hash: sha256:...
book_owned_sources:
  - pointer_id: book_pointer_separator_...
    accepted_revision_id: book_accepted_separator_v001_...
    owned_kind: separator
    content_hash: sha256:...
summary:
  exact_match: false
  ready_for_book_acceptance: true
  residual_counts: {exact_match: 3, book_owned_residual: 1, chapter_owned_residual: 0,
                    structural_residual: 0, marker_residual: 0, unresolved_residual: 0}
findings:
  - finding_id: finding_<sha256[:32]>
    category: book_owned_residual
    external_span: {start_line: 5, end_line: 7}
    recomposed_span: {start_line: 0, end_line: 0}
    ownership_analysis: {marker: separator, routing_target: separator, confidence: certain}
    reason: separator differs from recomposition
    recommended_action: accept the Book if this Book-owned difference is intended, ...
transformation: {id: expression.compare_book_recomposition, version: 1}
```

### Residual classification

Differences are classified using the marker contract and routing rules from
Phase A. The recomposition is the source of truth; each divergence is one of:

| Category | Meaning |
|----------|---------|
| `exact_match` | Recomposition and external agree (identical prose/title/separator/order) |
| `book_owned_residual` | Belongs to separator, order, title, or inserted material |
| `chapter_owned_residual` | Difference inside Chapter prose |
| `structural_residual` | Missing / extra / reordered / malformed Chapter boundary |
| `marker_residual` | Marker contract violation (duplicate/malformed marker, unsupported contract) |
| `unresolved_residual` | Ownership cannot be determined safely (markerless, cross-Chapter movement) |

Ownership routing uses `MarkerContract`: an invalid marker is a `marker_residual`;
a valid Chapter marker routes to its Chapter (or, when the accepted Book does not
know it, to a `structural` extra-Chapter problem); a valid separator marker routes
to the Book. Multiple Chapters changed with the Chapter order unchanged is treated
as cross-boundary movement and collapses to a single `unresolved_residual` rather
than being mis-attributed to individual Chapters.

### Readiness criteria

A comparison is *ready for Book acceptance* when:

- no unresolved residuals
- no Chapter-owned residuals
- no structural residuals
- no marker residuals

Book-owned residuals may remain nonzero if the Book-owned difference is intended.

### Freshness validation (12-point gate)

Comparison is gated by a 12-point freshness check; any failure blocks atomically
(no report, partial or otherwise, is written) with a structured
`ComparisonBlockedError`:

1. Recomposition exists on disk
2. Recomposition is `authority: derived`
3. Recomposition is `lifecycle: proposed`
4. Recomposition hash matches its stored body (not tampered)
5. Phase C1 recomposition freshness gate passes
6. Source publication still exists
7. All accepted Chapter pointers unchanged
8. All Book-owned pointers unchanged
9. Pointer targets still exist on disk
10. Accepted Book revision matches the recomposition snapshot
11. External manuscript exists at the resolved path
12. External manuscript hash is captured at comparison time

Checks 7, 8, and 10 are enforced by re-assembling the recomposition from the
current accepted pointers and Book state and comparing the deterministic content
hash: any drift (a Chapter pointer advanced, a Book-owned pointer moved to
different content, the Book revision changed) blocks with
`blocked_pointer_moved` / `blocked_stale_recomposition`. A Chapter accepted after
recomposition is caught by the Phase C1 gate as `blocked_stale_chapter`.

### Determinism

The comparison id is `SHA256(recomposition_id + external_hash + marker_version +
sorted_finding_ids)` and each finding id is
`SHA256(category + external_span + recomposed_span + routing_target + reason)`. No
timestamp enters the artifact, so a repeated comparison over identical state
overwrites the report with byte-identical content and an identical
`comparison_id`.

### CLI

```bash
auteur expression compare-book-recomposition <recomposition_id> \
  --project PROJECT [--external-manuscript PATH] [--json] [--verbose]
auteur expression inspect-book-comparison <comparison_id> \
  --project PROJECT [--json]
```

When `--external-manuscript` is omitted the source inspection's manuscript is the
default. Normal output names the exact-match count, the readiness flag, each
residual count with the Book-owned types, `Accepted pointers changed: no`, and a
recommended next action (`accept Book` / `re-examine residuals` /
`re-approve sources`). A blocked comparison prints the block status, each
structured reason, `No comparison report was created.`, and the recommended
action. Full metadata and per-finding ownership reasoning are shown behind
`--json` / `--verbose`.

## Non-goals

This slice implements read-only Book comparison but does **not** implement
acceptance of a recomposed Book, accepted Book-owned pointer movement driven by
comparison, reconciliation completion, source mutation, or automatic proposal
generation. Comparison evaluates and classifies; it never accepts, mutates, moves
a pointer, or completes anything. Decisions record author intent, produce accepted
Book-owned sources on approval, and regenerate a derived preview; they never
mutate any accepted or canonical artifact and never move the accepted Book
pointer.
