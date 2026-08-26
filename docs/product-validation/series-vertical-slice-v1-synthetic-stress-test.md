# Series Vertical Slice V1 Synthetic Stress-Test Report

Status: synthetic product-design stress evidence only.

This report is not participant evidence, usability validation, or a release
qualification. No real participant was involved. No production code or frozen
V1 product decision was changed during the campaign.

## Baseline and method

The campaign used the exact qualified implementation candidate:

```text
candidate: e5236763949107424cb71f7102f5c800c1347bea
checkout:  H:/GithubRepositories/auteur/.worktrees/series-vertical-slice-v1-qualification-final
import:    that checkout's src/auteur
```

The probes created fresh temporary projects and exercised the existing service
and CLI-facing models. The repository checkout remained unchanged apart from
the generated qualification evidence already present in that checkout. The
campaign did not add fixtures, alter production code, or implement a fallback
for unsupported finite Series behavior.

The campaign separated four evidence classes:

1. **Observed program behavior:** validation results, persisted artifacts,
   context contents, rebuild comparisons, and thrown errors.
2. **Synthetic-agent statements:** answers from three fresh blind contexts that
   received only the writer scenario, beginner-facing outputs, and existing
   comprehension questions.
3. **Interpretation:** what those observations mean for the frozen V1 model.
4. **Proposed product implication:** a possible future capability or research
   question, not an approved change.

## Baseline representation boundary

Before testing finite scenarios, the exact model was inspected and exercised.

Observed program behavior:

- `SeriesDirection` has fields for title, promise, pressure, open question,
  commitments, and `series_type`.
- `series_type` is `Literal["ongoing"]`; validating `"finite"` fails.
- An `intended_book_count` or equivalent extent field is rejected as an extra
  input.
- `DirectionCommitment` has `scope`, but no target Book number or terminal
  extent field.
- `NextDecisionProposal` and its store identity validation are explicitly
  Book-2-specific.
- The deterministic carry-forward state-selection rule is explicitly keyed to
  the Archive of Lies Book 2 transition.

Classification: **missing V1 capability**. This is an explicit boundary of the
qualified slice, not an implementation defect in that slice.

## Scenario results

### D2 — exactly two Books intended

Observed program behavior:

- The exact “two Books” intention cannot be represented as finite extent.
- If represented using the existing `ongoing` value, Book 1 → Book 2 works:
  two context items are surfaced, each has a non-empty why-now explanation
  and source references, the unaccepted alternative realization is absent,
  derived context rebuilds semantically identically, and the Book 2 decision
  is available with three accepted input references.
- Nothing in the resulting state records that Book 2 is intended to be the
  final Book.

Classification:

- finite extent: **missing V1 capability**;
- bounded Book 1 → Book 2 journey: **no consequential issue**;
- inability to express “this is the last Book”: **product-design
  pressure/scaling issue**.

### T3 — exactly three Books intended

Observed program behavior:

- The exact finite trilogy intention cannot be represented.
- Book 1 → Book 2 behaves like the qualified journey.
- Book 2 → Book 3 can accept a local Book Direction and a realization, enter
  Book 3 planning, derive context, and rebuild it successfully.
- Book 3 context contains only the carried Series commitment. The accepted
  Book 2 state change is not surfaced, even though it is recent and accepted.
- A Book 3 next-decision proposal fails with:

  ```text
  ValueError: The bounded Book 2 decision requires its two accepted
  carry-forward context items
  ```

- Therefore the second Map → Focus cycle cannot be completed through the
  existing decision surface.

Classification: **missing V1 capability** with **product-design
pressure/scaling issue**. The behavior is coherent for a Book-2 vertical slice,
but not for a repeated trilogy workflow.

### T3-END — known Book 3/end outcome, unknown Book 2

Observed program behavior:

- A statement such as “By Book 3, the archive must lose its power to define
  lived memory” can be stored as an untyped Series commitment.
- `DirectionCommitment` has no Book target, terminal-outcome role, or distance
  metadata.
- If Book 1 does not explicitly reference that commitment, it is not surfaced
  in Book 2 context.
- If Book 1 explicitly references it, it is surfaced in Book 2 alongside the
  ordinary commitment and state item, with a generic “Book 1 explicitly
  carried this Series commitment” why-now explanation.
- The system cannot distinguish “important distant Book 3 outcome” from any
  other Series commitment when selecting or explaining context.

Classification: **product-design pressure/scaling issue**. The sparse model can
hold the statement, but it cannot represent or explain distant planned
consequences as a distinct planning kind. No contradiction was observed in the
authority model.

### Q4 — exactly four Books intended

Observed program behavior:

- The exact finite quadrilogy intention cannot be represented.
- Book 1 → Book 2 completes the qualified Map → Focus cycle.
- Book 2 → Book 3 and Book 3 → Book 4 can persist accepted local directions,
  accepted state transitions, planning entries, and rebuildable contexts.
- Both later contexts contain only the Series commitment; accepted state
  changes from the preceding Book are not surfaced.
- Neither later transition has a usable Focus decision. The same bounded Book 2
  validation error occurs for Book 3 and Book 4.

Classification: **missing V1 capability** with **product-design
pressure/scaling issue**. Map remains technically small, but partly because
the relevance rule stops carrying later state rather than because a general
multi-Book relevance model has been demonstrated.

### U3/4 — uncertain extent

Observed program behavior:

- An ongoing Series can remain open-ended, which is compatible with not knowing
  whether the work will stop at Book 3 or continue to Book 4.
- The model cannot record “currently expect three, may require four” as an
  extent range, confidence, forecast, or provisional horizon.
- Adding an extent field is rejected by the strict model.

Classification: **missing V1 capability**. The existing `ongoing` value is a
workable absence of a terminal commitment, but it does not express uncertain
finite intent. This is also a **product-design pressure/scaling issue** for
future horizon-aware planning.

### R3→2 — contraction

Observed program behavior:

- There is no expected trilogy extent to revise and no contraction operation.
- A second accepted Series Direction can change the commitment statement and
  creates ArtifactStore revision 2 while preserving artifact revision history
  `[1, 2]`.
- Both generated Series Direction proposals report revision 1; the change is
  not represented as an explicit extent revision, contraction, or successor
  decision.

Classification: **missing V1 capability**. The existing authority boundary does
not become incoherent because finite extent is absent, but the product cannot
explain a change from “trilogy” to “end at Book 2” as a first-class planning
change.

### R3→4 — expansion

Observed program behavior:

- There is no expected trilogy extent to revise and no expansion operation.
- A second accepted Series Direction can change the commitment statement and
  creates ArtifactStore revision 2 while preserving artifact revision history
  `[1, 2]`.
- The change is not represented as an explicit expansion to Book 4, and no
  future Book 4 planning obligation is created.

Classification: **missing V1 capability**. As with contraction, no current
authority contradiction was exposed; the missing concept is explicit extent
evolution and its effect on planning.

## Cross-cutting findings

| Question | Observed behavior | Classification |
|---|---|---|
| Sparse Series Direction without complete future planning | Works for the ongoing V1 path and remains sparse. | **no consequential issue** |
| Planned extent versus planned Book content | Extent is absent, so the two concepts cannot be confused by the implementation; finite intent is simply unavailable. | **missing V1 capability** |
| Series-vs-Book Direction ownership | Accepted Book Directions remain local and reference accepted Series commitments; repeated acceptance does not rewrite Series Direction. | **no consequential issue** |
| Explicit authority boundaries | Proposals and decision actions remain non-authoritative; accepted realization bundles change Canonical State. | **no consequential issue** |
| Carry-forward accumulation | Accepted realization history accumulates and rebuilds; later context selection does not generalize the Book 2 state rule. | **product-design pressure/scaling issue** |
| Relevance and recent irrelevant information | Unaccepted alternatives and the unrelated Book 1 datum do not enter context merely by existing or being recent. | **no consequential issue** |
| Why-now explanations | Every surfaced item in the tested contexts has a non-empty explanation. Later explanations remain generic when distant commitments are carried. | **product-design pressure/scaling issue** |
| Map compactness | Book 2 has two items; later Books have one. Compactness holds, but later-state omission contributes to the small size. | **product-design pressure/scaling issue** |
| Focus source dependence | The Book 2 recommendation names the accepted Series, Book 1, and realization sources and gives a specific rationale/tradeoff. No later Focus is available. | **no consequential issue** at V1 scope; **missing V1 capability** beyond Book 2 |
| Unaccepted proposal contamination | Unaccepted realization alternatives do not appear in later context or Canonical State. | **no consequential issue** |
| Abandoned proposal contamination | V1 has no explicit abandonment operation. Leaving a proposal unused is enough for the tested context path, but abandonment provenance is not represented. | **missing V1 capability** only if abandonment history becomes a user requirement |
| Derived rebuildability | Every tested context, including later-Book contexts, rebuilt semantically identically after deletion. | **no consequential issue** |
| Expected extent changes | No extent invariant exists to become inconsistent. Direction artifact revisions preserve history, but do not encode contraction or expansion semantics. | **missing V1 capability** |

## Blind synthetic comprehension

Three independent fresh synthetic contexts received only:

1. the short Archive of Lies writer scenario;
2. the beginner-facing acceptance, Map, and Focus outputs; and
3. the existing seven comprehension questions.

They did not receive ADRs, Domain Model V1, source code, implementation
documentation, expected answers, or authority terminology. A separate fresh
synthetic evaluator received only the pre-registered scoring rubric and the
three answer sets.

These are **synthetic comprehension evidence**, not participant evidence.

### Evaluator result

| Synthetic context | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 useful action | Authority inversion | Primary criterion |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| A | 2 | 2 | 2 | 2 | 2 | 0 | 1 | Yes | Fail |
| B | 2 | 2 | 2 | 2 | 2 | 0 | 1 | Yes | Fail |
| C | 2 | 2 | 2 | 2 | 2 | 0 | 1 | Yes | Fail |

Aggregate score: 30/36 across Q1–Q6, with 3/3 useful unaided next actions,
but 0/3 contexts pass the primary criterion because all three invert the Q6
authority boundary.

Representative synthetic-agent statements:

- “Choosing the recommendation would make the living witness central to Book
  2.”
- “Choosing the recommendation would make the living witness central to Book
  2.”
- “Choosing the recommendation establishes the living witness as Book 2’s
  direction.”

Interpretation: **synthetic comprehension failure** and **product-design
pressure/scaling issue**. The repetition across three independent contexts
indicates a systematic presentation ambiguity rather than one anomalous answer.
The wording “Your choices” and the absence of an explicit plain-language
statement that these actions do not establish Book 2 canon appear insufficient
for blind comprehension.

This does not prove that real beginners will fail in the same way. It identifies
the exact question a human session must test.

## Answers to the stress-test questions

### Which parts generalized cleanly?

The following generalized from the single journey through the tested ongoing
multi-Book paths:

- sparse Series Direction without exhaustive future planning;
- separate Series and local Book Direction ownership;
- explicit acceptance as the authority boundary;
- accepted realization as the source of Canonical State change;
- exclusion of unaccepted alternatives from state and context;
- source-linked why-now explanations for surfaced items;
- deterministic deletion and rebuild of derived context;
- a compact Book 2 Map with source-backed Focus rationale and tradeoff.

### Which assumptions failed under finite or repeated pressure?

- V1 assumes an ongoing Series rather than modeling finite or uncertain extent.
- V1 assumes the next useful decision is a Book 2 decision, not a repeated
  per-Book capability.
- V1's state carry-forward selection is specific to the Archive of Lies Book 2
  case; later accepted state is not surfaced.
- Distant commitments can be stored only as untyped statements, without target
  Book or terminal-outcome semantics.
- Extent contraction and expansion have no first-class representation.
- The beginner-facing Focus output does not make non-canonical decision status
  explicit enough for blind comprehension.

### Did Map/Focus remain coherent through duology, trilogy, and quadrilogy scale?

Only partially.

- **Duology:** coherent for the one required Book 1 → Book 2 cycle, except that
  finite “Book 2 is the end” intent cannot be recorded.
- **Trilogy:** Map/context mechanics can continue to Book 3, but the second
  Focus decision is unavailable and later state is omitted.
- **Quadrilogy:** the same limitation appears at Book 3 and Book 4; repeated
  Map → Focus does not remain a complete workflow.

The model therefore generalizes as a sparse accepted-history and context
projection seam, not as a Series-scale repeated planning loop.

### Is finite Series extent a metadata/capability gap or a deeper contradiction?

It is currently a metadata/capability gap, not a deeper contradiction.

The existing Direction–State–Continuity separation remains coherent when extent
is absent. However, a long-horizon product that intentionally supports finite,
uncertain, expandable, and contractive Series will eventually need explicit
extent semantics and a rule for how extent changes affect future planning. The
stress campaign supplies pressure for that work but does not settle its design.

### Did any scenario justify reopening a frozen V1 design decision?

No authority or storage decision should be reopened from this campaign. The
synthetic Q6 failure does justify opening a narrowly scoped UX clarification
question: should Focus and decision-result presentation explicitly say, in
beginner language, “This records a planning choice; it does not make Book 2
canon”?

That is a research-backed candidate question, not an approved V1 change. It
requires real-human testing before changing the frozen interaction contract.

### Smallest evidence-supported V2 candidate

The smallest candidate suggested by this campaign is:

> Add an explicit, plain-language non-canonical status explanation at the Focus
> choice boundary and after each choice/defer action.

This is not implemented or approved. It is supported by 3/3 synthetic
comprehension failures on the same authority distinction. A larger follow-on
candidate—generalized later-Book context and Focus cycles, with finite/uncertain
extent—is not yet small enough to choose without product design and human
evidence.

### What still fundamentally requires a real human participant?

Synthetic runs cannot establish:

- whether actual creative beginners interpret “choice” as canon in the same
  way;
- whether the current Map density and why-now explanations feel useful or
  burdensome;
- whether participants want finite extent recorded or are satisfied with an
  ongoing/open Series;
- whether bounded alternatives feel empowering or restrictive;
- whether repeated later-Book context should include more state, less state, or
  a different grouping;
- whether the facilitator-mediated CLI hides interaction friction that a real
  interface would expose;
- what participants would actually choose as their next creative action.

## Bounded conclusion

Series Vertical Slice V1 survives this campaign as a coherent, technically
qualified Book 1 → Book 2 capability with clean authority and provenance
boundaries. It does not yet demonstrate a generalized finite or repeated
multi-Book product loop.

The campaign found no implementation defect requiring an immediate fix and no
contradiction in the frozen Direction–State–Continuity model. It found explicit
missing capabilities and scaling pressure around Series extent, distant
commitments, repeated later-Book decisions, and the beginner-facing statement
of non-canonical choice status.

The next legitimate step remains a real human validation session using the
[user-validation package](series-vertical-slice-v1-user-validation.md). Do not
report this campaign as participant evidence or usability validation, and do
not implement V2 until the evidence and product decision are separately
accepted.
