# Series Vertical Slice V1 Synthetic Repeated Map/Focus Probe

Status: synthetic product-design evidence only.

This probe is not participant evidence, usability validation, or real-user
approval. It does not establish that creative beginners will prefer the
proposed Map density, grouping, or decision cadence. No production code,
Domain Model V1 decision, or frozen V1 interaction contract was changed.

## Goal and baseline

The goal was to test the smallest product-design requirements needed for
Map -> Focus to remain coherent as accepted narrative history accumulates
through Books 1 to 4.

The baseline was the exact qualified product candidate:

```text
candidate: d3bb1eb37d065b34c132771cf19a0856e60d0cea
checkout:  H:/GithubRepositories/auteur/.worktrees/series-vertical-slice-v1-qualification-wording
```

The checkout's `src` and `tests` bytes matched that candidate. The existing
vertical-slice end-to-end and service matrix passed 97/97. The prior
[qualification report](../engineering/series-vertical-slice-v1-focus-authority-clarification-qualification.md)
records the complete source and artifact gates.

Observed baseline behavior relevant to this probe:

- `BookPlanningContext` can contain only `series_commitment` and
  `state_change` items.
- Each context item has a summary, a why-now explanation, and accepted source
  references, but no status, currentness, supersession, resolution,
  reactivation, grouping, or relevance score.
- Context derivation carries commitments explicitly named by the immediately
  preceding accepted Book Direction.
- State carry-forward uses a hard-coded Archive of Lies / Book 2 transition
  rule.
- `NextDecisionProposal` is validated only for the exact two Book 2 context
  items and contains a hard-coded Book 2 question, options, rationale, and
  tradeoff.
- Map lists every derived context item. It has no compression or grouping
  operation.
- Accepted sources are validated. Unaccepted realization candidates do not
  enter Canonical State or the derived context.
- Derived context can be deleted and rebuilt without changing authority or
  Canonical State.

The exact implementation therefore cannot execute a generalized custom
Books 2-4 scenario without production changes. That is an observed V1
boundary, not a workaround used by this probe. The repeated scenario below
is a product-design test ledger, not a claim that the current service persisted
these custom artifacts.

## Adversarial accepted-history ledger

The synthetic story was deliberately constructed so that recency, simple
current-state projection, and an ungrouped history dump would each fail at
least one checkpoint.

| Reference | Accepted or status | Meaning |
|---|---|---|
| `series-direction@1` | accepted | Series pressure: official history must answer to lived memory. |
| `series-direction@1 / commitment-falsifier` | accepted, unresolved at Book 1 | The person who falsified the founding record must be identified. |
| `book-1-direction@1` | accepted | Book 1 carries the Series pressure and the falsifier question. |
| `book-1-realization@1 / founding-record` | accepted | The founding record is confirmed forged. |
| `book-1-realization@1 / monastery-testimony` | accepted | A sealed witness testimony exists at a remote monastery; initially dormant. |
| `book-1-realization@1 / broken-lantern` | accepted | A recent personal detail with no Series or next-decision relevance. |
| `book-2-direction@1` | accepted | Book 2 continues the pressure and investigates the falsifier. |
| `book-2-realization@1 / named-falsifier` | accepted | The falsifier is identified; the falsifier question is resolved. |
| `book-2-realization@1 / public-admission` | accepted | The council publicly admits the founding record was false. |
| `book-2-burn-archive` | proposed, not accepted | An abandoned/unaccepted proposal to burn the archive. |
| `book-3-direction@1` | accepted | Book 3 continues the pressure while responding to political reversal. |
| `book-3-realization@1 / admission-retracted` | accepted | The council retracts its admission; the prior public-admission state is superseded. |
| `book-3-realization@1 / archive-protected` | accepted | A treaty protects the archive because it contains the only evidentiary chain. |
| `book-3-realization@1 / repaired-lantern` | accepted | Recent but irrelevant information. |
| `book-3-ally-militia` | proposed, not accepted | A tempting alternative that was abandoned before acceptance. |
| `book-4-direction@1` | accepted | The dormant monastery testimony is now the intended route back to lived memory. |

The synthetic planning points are:

- Book 2: the founding fraud is newly active; the falsifier question is still
  open.
- Book 3: the falsifier question is resolved; the council's current retraction
  is active; the monastery testimony remains dormant.
- Book 4: the monastery testimony becomes relevant again; the treaty-protected
  archive makes an apparently dramatic "burn the archive" option incompatible
  with accepted state.

## Probe procedure

Books 2, 3, and 4 were evaluated independently from their own accepted
history snapshot. The probe asked, at each checkpoint:

1. What should Map surface?
2. What should it omit?
3. What should be summarized rather than listed?
4. Why is each surfaced item relevant now?
5. Which accepted sources support it?
6. What single bounded creative decision should Focus present?
7. Can the recommendation be explained specifically from accepted context?

The synthetic run compared four relevance approaches:

1. recency-first;
2. all accepted history;
3. current commitments and current state only; and
4. accepted, typed, causal relevance with lifecycle filtering and pressure
   grouping.

This is a structured synthetic design probe, not a blind participant
comprehension study. Its outputs are scenario-analysis evidence. No scores are
reported as user comprehension results.

## Checkpoint results

### Book 2

| Probe question | Synthetic result |
|---|---|
| Surface | The active Series pressure; the newly confirmed forged founding record; and the still-open falsifier question. The Map should stay short and distinguish the pressure from the concrete Book 1 consequence. |
| Omit | The broken lantern, the unaccepted burn-archive proposal, and any future Book 3/4 material. |
| Summarize | The founding fraud and the witness problem may be one compact continuity cluster, with the concrete forged-record state shown as the evidence item. The unresolved falsifier question remains a decision driver, not a second history dump. |
| Why now | The accepted Book 1 realization changes what official history can claim, and the accepted Book 1 Direction carries the Series pressure into Book 2. The falsifier question is still open and can now be pursued against a concrete record. |
| Accepted sources | `series-direction@1`, `book-1-direction@1`, `book-1-realization@1 / founding-record`, and, if the witness is surfaced, `book-1-realization@1 / monastery-testimony`. |
| Focus decision | “How should Book 2 make the exposed fraud matter to lived memory?” This is one bounded Book 2 exploration decision, not Book 2 canon. |
| Recommendation test | Yes, if the rationale cites the active Series pressure plus the accepted forged-record state and names a specific tradeoff between centering testimony and tracing institutional cover-up. |

Classification: the qualified Archive of Lies Book 1 -> Book 2 behavior
generalizes cleanly in shape. The custom multi-factor ledger is not executable
by the current implementation, so the richer result is a missing capability,
not observed V1 behavior.

### Book 3

| Probe question | Synthetic result |
|---|---|
| Surface | The active Series pressure; the current council retraction; and the causal consequence that official recognition has been withdrawn. The resolved falsifier question may appear as a one-line completed-history marker only if it explains why the retraction matters. |
| Omit | The broken/repaired lantern; the unaccepted militia proposal; the old public-admission state as if it were current; and the dormant monastery testimony as an active item. |
| Summarize | Group the forged record, public admission, and retraction into one “official history is unstable” pressure cluster. List the current retraction as the present state and keep the prior admission in expandable history, not as a peer item. |
| Why now | The retraction changes the immediate conditions under which the accepted Series pressure can be pursued. It is current accepted state, not merely a recent event. The falsifier question is no longer a next decision because it was resolved in Book 2. |
| Accepted sources | `series-direction@1`, `book-2-direction@1`, `book-2-realization@1 / named-falsifier`, `book-2-realization@1 / public-admission`, `book-3-direction@1`, and `book-3-realization@1 / admission-retracted`. |
| Focus decision | “How should Book 3 respond to the council's retraction while preserving the witness's authority?” |
| Recommendation test | It can be specific only if the current retraction and the resolved falsifier outcome are both available as accepted inputs. A recommendation based only on the latest Book 2 event would lose the causal chain; a recommendation based on all history would overload Focus. |

Classification: repeated Map requires a lifecycle-aware distinction between
active, resolved, current, and superseded material. Repeated Focus requires a
new per-Book proposal capability. The current V1 does neither.

### Book 4

| Probe question | Synthetic result |
|---|---|
| Surface | The active Series pressure; the treaty-protected current archive state; and the monastery testimony as a reactivated historical fact. The reactivation should be explicit: Book 4's accepted Direction makes the old testimony relevant again. |
| Omit | The resolved falsifier question; the superseded public-admission state as current; the irrelevant lantern; and both unaccepted proposals. |
| Summarize | Compress the founding fraud, council admission, retraction, and treaty protection into a single history-of-the-archive cluster. Show the treaty protection as the current constraint and the monastery testimony as the newly reactivated evidence. |
| Why now | The accepted Book 4 Direction points back to the monastery testimony, and the accepted treaty state makes the choice consequential: burning the archive would destroy the only evidentiary chain. Relevance comes from the present Book 4 direction plus accepted historical support, not from age or recency. |
| Accepted sources | `series-direction@1`, `book-3-direction@1`, `book-3-realization@1 / admission-retracted`, `book-3-realization@1 / archive-protected`, `book-1-realization@1 / monastery-testimony`, and `book-4-direction@1`. |
| Focus decision | “How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?” |
| Recommendation test | A recommendation to burn the archive must be rejected, marked incompatible, or recomputed. It contradicts accepted `archive-protected` state. A valid recommendation must explain why recovery/publication preserves both lived memory and the evidence chain, and must state the tradeoff against a more confrontational option. |

Classification: dormant-fact reactivation and recommendation/state
compatibility are new requirements. They are not solved by a larger recency
window or by listing more history.

## Relevance approach comparison

| Adversarial condition | Recency-first | All accepted history | Current-only | Typed causal + grouped |
|---|---|---|---|---|
| Active consequence across several Books | May drop it when newer detail arrives. | Retains it but repeats it. | Retains current state, but may lose its originating evidence. | Retains one active continuity item with stable supporting sources. |
| Fully resolved question | Keeps stale work visible. | Keeps it as noise. | Can omit it, but loses useful resolution context. | Excludes it from active Map; optionally summarizes it as resolved history. |
| Dormant fact becomes relevant again | May surface accidentally or miss it. | Always lists it, causing clutter. | Misses it because it is not current state. | Reactivates it when the current Book direction or decision depends on it. |
| Superseded state | Can show stale state as recent. | Lists both competing states. | Shows current state but not why it changed. | Shows current state; retains superseded lineage only when it explains now. |
| Several consequences instantiate one pressure | Produces duplicate cards. | Produces duplicate cards plus old history. | May hide the pressure's causal evidence. | Groups by Series pressure and shows representative current evidence. |
| Irrelevant recent information | Incorrectly promotes it. | Includes it. | May include it if current but unrelated. | Excludes it because it supports neither active continuity nor the next decision. |
| Abandoned/unaccepted proposals | May include them if recent. | Includes them unless filtered. | Usually excludes them, but without explicit provenance. | Excludes them by accepted-authority boundary; optional abandonment history remains separate. |
| Apparent option contradicts accepted state | Cannot detect the contradiction. | Cannot detect the contradiction. | Can expose the state but has no proposal gate. | Requires compatibility validation or proposal invalidation before recommendation. |

The evidence supports the fourth approach, but only at the level of a product
rule. It does not justify a universal relevance engine, a numerical relevance
score, or a generalized event graph yet.

## Baseline comparison and classifications

| Finding | Classification |
|---|---|
| Sparse Series Direction, separate Series/Book ownership, explicit acceptance, and accepted-only authority boundaries remain coherent. | **existing V1 behavior generalizes** |
| Source-linked why-now explanations and deletion/rebuild semantics remain necessary and conceptually reusable. | **existing V1 behavior generalizes** |
| Repeated per-Book Focus proposals do not exist; current validation is exact Book 2 behavior. | **missing capability** |
| Carry-forward selection is tied to the immediately previous Book and a hard-coded Archive of Lies transition. | **missing capability** |
| Map has no lifecycle, currentness, supersession, reactivation, or pressure-group representation. | **missing capability** |
| Map density will become misleading if every accepted consequence is listed or if every old item is retained as active. | **product-design pressure** |
| A dormant fact needs a present trigger to become relevant again; recency is not a sufficient trigger. | **possible relevance/compression rule** |
| Several facts that instantiate one Series pressure should normally be one compact Map cluster with representative evidence. | **possible relevance/compression rule** |
| A proposal or recommendation that contradicts current accepted state cannot remain a valid recommendation. | **possible relevance/compression rule**; future invariant |
| No contradiction was found in the Direction / State / Continuity separation itself. | **no product-design contradiction observed** |
| If a future generic Focus surface still labels every decision “Book 2,” that would be a presentation contradiction created by generalization, not a current V1 defect. | **product-design pressure** |
| Maximum Map density, preferred grouping, acceptable history disclosure, and whether one bounded decision feels sufficient require human evidence. | **requires human evidence** |

The proposed contradictory Book 4 recommendation is especially important. The
probe does not classify the current V1 as defective because V1 does not claim to
support that Book 4 proposal. It establishes a requirement for any future
repeated capability: recommendation generation must be evaluated against the
current accepted state at the same freshness boundary as its source context.

## Smallest generalized repeated-Map/Focus capability contract

The smallest contract supported by this probe is conceptual and deliberately
narrow:

### Repeated planning context

For an explicitly entered planning point for Book `N > 1`, Auteur may derive a
non-authoritative context from accepted sources through Book `N - 1`.

The context must:

- include active Series commitments that still govern the next Book;
- include current accepted state changes that constrain or enable the next
  decision;
- reactivate an older accepted fact only when the current Book Direction or
  proposed decision supplies a present relevance trigger;
- represent resolved and superseded material as history, not as current peer
  items, unless it explains the present condition;
- group multiple consequences that instantiate the same Series pressure;
- exclude unaccepted, abandoned, or merely recent irrelevant material;
- give every surfaced group or item a specific why-now explanation and exact
  accepted source references; and
- be rebuildable from accepted authority and the derivation version.

### Repeated Focus proposal

For each planning point, Auteur may derive one bounded `NextDecisionProposal`
for that Book. It must:

- be non-authoritative until a separate author acceptance boundary;
- cite the accepted context that supports the question and recommendation;
- offer a small bounded set of options with specific tradeoffs;
- explain the recommendation from the active pressure, current state, and
  present relevance trigger;
- validate each recommended option against current accepted state, or mark the
  proposal stale and recompute it when that state changes; and
- use the current Book number in its presentation and non-canonical status
  language.

This contract does not yet include finite Series extent, universal Direction
inheritance, a general event graph, free-form Book Direction authoring, a
numerical relevance score, or an author-facing history browser.

## Human uncertainty

This synthetic probe cannot answer:

- how many Map groups a beginner can usefully hold at once;
- whether a resolved item should be hidden, collapsed, or shown as a visible
  milestone;
- whether a reactivated old fact feels like helpful continuity or a surprising
  interruption;
- whether grouping by Series pressure matches a writer's own mental model;
- how much source/history detail a writer wants before trusting a
  recommendation;
- whether a state-compatibility warning feels protective or obstructive; or
- whether one bounded Focus decision remains useful after several Books.

These require a real creative participant. They must not be inferred from this
synthetic probe.

## Bounded conclusion

Map -> Focus generalizes cleanly at the authority and provenance seam, but not
as a repeated workflow. The smallest evidence-supported generalized idea is
not “carry more history.” It is:

> **Derive a compact, accepted-source-backed continuity view for the current
> Book, with lifecycle-aware relevance, pressure grouping, explicit
> why-now explanations, and one state-compatible bounded next decision.**

That is a candidate product capability contract, not an approved V2 and not an
implementation plan. No production code or Domain Model V1 decision was
changed by this probe.
