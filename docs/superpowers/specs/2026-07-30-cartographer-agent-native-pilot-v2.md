# Auteur — Cartographer Agent-Native Pilot v2

## Status and boundary

Design and operational kit only. No generation, narrative output, reviewer
rating, unblinding, executor implementation, commit, or push is authorized by
this specification. The pinned prior-pilot SHA is
`d3d12b8dfb501a5e553c3b366df2f349d4438e59`.

## Purpose

Measure whether `profile_emotional_targets` creates repeatable, structurally
useful differences beyond ordinary run-to-run generation variance, with two
independent blinded reviewers. Canonical executor promotion is out of scope.

## Prior evidence and rationale

Pilot v1 demonstrated deterministic artifact validity (8/8 after replacement),
protocol viability after remediation, and a narrow directional promise signal.
It did not establish behavioral usefulness: treatment and control each won 2/4
pairs, only one reviewer participated, and run variance was not measured.

The v2 kit maps every major incident to a control:

| v1 incident or ambiguity | v2 mitigation |
| --- | --- |
| one execution per condition | three fresh executions per condition |
| malformed execution records and one replacement | canonical schema, parse/validate/hash before eligibility, one record repair maximum |
| false-positive repository-change report | expected, attributable, and pre-existing changes are separate path-level fields |
| leaked `authored_emotional_target` | reviewer packages contain neutral context only; automated leakage scan |
| contaminated v1 review set | two isolated reviewer directories and pre-handoff lock/audit gate |
| review-lock path transport mismatch | lock-relative paths plus export/import transport dry run |
| one-reviewer limitation | two independent reviewers and predefined agreement measures |
| coordinator/operator overhead | checklists, manifests, synthetic fixtures, and intervention threshold |

## Fixed design

Four v1 cases and their profiles are retained unchanged. Each case has three
control and three treatment executions: 4 × 2 × 3 = 24. Every execution uses a
fresh session, one opaque packet, the pinned SHA, the existing deterministic
validator, and no provider or `compile_outline()` call.

Review uses Option A: three randomized matched control/treatment pairs per
case, twelve blinded pairs per reviewer. Each reviewer independently rates
both outputs before pairwise judgment. A/B order and package order are
reviewer-specific and randomized.

## Preregistered hypotheses

- **H1 validity:** at least 22/24 outputs validate, and no condition has fewer
  than 5/6 eligible executions. Failure means the validity threshold is not met.
- **H2 repeatability:** within-condition spread is measurable and the treatment
  effect exceeds within-condition variance on at least 3 of 6 primary
  dimensions in at least 3/4 cases. Failure means separation is not shown.
- **H3 target alignment:** treatment direction is target-aligned in at least
  3/4 cases under both reviewers' median classifications. Failure means no
  target-specific conclusion.
- **H4 structural usefulness:** any treatment advantage is positive on
  structural integration or progression in at least 3/4 cases and is not only
  surface intensity. Failure means surface-only or mixed evidence.
- **H5 reviewer agreement:** reviewers agree on pairwise winner in at least
  9/12 matched comparisons and are within one scale point on at least 80% of
  primary dimension ratings. Failure means reviewer direction is unstable.
- **H6 operational reliability:** at least 22/24 records are canonical with no
  unresolved integrity incident and all required review locks/manifests pass.
  Failure means operational reliability is not established.

Null interpretation for every hypothesis is descriptive failure to meet the
threshold, not evidence that the treatment has no effect.

## Cases

| Case | Authored intent | Treatment profile | v1 reason to retain |
| --- | --- | --- | --- |
| A1 | mounting dread | dread 0.7; fascination 0.4 | treatment strongly preferred |
| A2 | grief shaped by delayed recognition | grief 0.5 | control strongly preferred; replication is necessary |
| A3 | restrained sorrow | tenderness 0.6; awe 0.3 | narrow treatment preference with tradeoffs |
| A4 | tense curiosity | dread 0.2; tenderness 0.9 | narrow control preference; tests adverse tradeoff |

No case or profile is changed. This preserves v1 comparability and measures
replication plus variance rather than selecting for positive results.

## Eligibility, repairs, and replacement

Output-format/schema repairs are limited to two and record syntax/schema repairs
to one. Neither may change narrative content. An execution is eligible only
when packet, SHA, output, validator result, hashes, canonical record,
isolation, and change audit all pass. A quarantined execution is preserved;
its replacement receives a new opaque ID, equivalent input, and coordinator-only
lineage, and does not add an observation. At most two replacement attempts are
allowed per case-condition; failure to obtain 3 eligible replicates stops that
condition and the pilot cannot enter behavioral synthesis.

## Primary analysis

The unit is case → condition → replicate → reviewer rating. Report
within-condition spread, matched treatment-control differences, reviewer
variance, and cross-case reversals separately. For each case report median
effect by dimension, wins/control wins/ties, spread, target alignment,
structural usefulness, and adverse tradeoffs. Do not claim weight calibration.

Primary dimensions are emotional progression, structural integration, coherence,
authored-constraint preservation, clarity, and narrative usefulness. Pairwise
preference and confidence are secondary; intensity alone is never primary.

## Gates and stop rules

Operational viability requires: ≥22/24 eligible outputs; 100% deterministic
validation among eligible outputs; ≥22/24 canonical records; ≤2 replacements;
zero unauthorized execution-attributable changes; zero isolation violations;
100% pair-equality, leakage, fidelity, reviewer completion, lock integrity, and
transport checks; ≤2 coordinator interventions; and no provider calls.

Behavioral promise requires operational viability, treatment positive median on
primary dimensions in ≥3/4 cases, treatment preferred in ≥3/4 cases by each
reviewer, ≥9/12 reviewer pairwise agreement, treatment effect exceeding
within-condition spread on ≥3 primary dimensions in ≥3 cases, target alignment
in ≥3 cases, and no recurring severe coherence or constraint regression.

A narrow prototype additionally requires the promise gate, ≥2/3 replicate
directional consistency in ≥3 cases, ≥10/12 pairwise agreement, ≤1 replacement,
≤1 coordinator intervention, no unresolved evidence incident, and a concrete
runtime contract with expected value exceeding protocol complexity. Canonical
promotion is not a v2 conclusion.

Pilot-wide stop triggers are repeated record failure (≥3), repeated isolation
failure (≥2), any provider/network use, any hidden-condition leakage, failure
to obtain three eligible replicates in a condition, reviewer contamination,
lock mismatch, fidelity failure, hypothesis-changing protocol drift, or
replacement rate above the fixed limit.

## Evidence and transport

All local evidence lives under
`.local/evaluations/cartographer-agent-pilot/profile-emotions-v2/`, already
Git-excluded. Lock paths are relative to the lock file directory and the
transport bundle preserves that structure. Pre-import resolution, source/export/
import hashes, leakage scans, and source-output fidelity checks are mandatory.

## Readiness conclusion

The protocol is designed to begin 24 isolated executions only after the kit's
synthetic dry runs pass. This document does not authorize those executions.
