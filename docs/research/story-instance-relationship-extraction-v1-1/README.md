# Auteur — Story-Instance Relationship Extraction Experiment V1.1

**Status:** PREREGISTERED — NOT EXECUTED

**Amendment base:** frozen V1 protocol at
`dfa51910a6ec7cf9fc8a5f173d2de56cb6f6d00b`

This is a minimal execution-contract amendment. The frozen V1 protocol remains
immutable and controls every question not explicitly amended here. V1.1 closes
one operational gap: how to handle an extractor response that cannot be
mechanically rendered into the frozen `R-DERIVED` downstream schema.

## 1. Aborted V1 attempt

The previous V1 attempt is recorded only as an invalidated, incomplete
execution attempt:

| stage | completed |
|---|---:|
| extractor | 3/3 |
| downstream generator | 0/36 |
| extraction evaluator | 0/3 |
| downstream evaluator | 0/36 |
| total | 3/78 |

All three extractor responses were structurally incompatible with the frozen
downstream projection. Continuing would have required an unregistered
semantic repair rule, so execution stopped before downstream calls. The
attempt is not classified as CASE A, B, C, or D and does not contribute
observations to V1.1.

The exact tool-return responses remain only in the original execution
transcript. Local compacted transcriptions are not exact raw empirical
evidence and are not incorporated into this preregistration.

## 2. Unchanged experiment

V1.1 does not reconsider or redesign:

- the research question;
- the Archive of Lies fixture;
- `B0`, `R-GOLD`, and `R-DERIVED`;
- `GOLD-R01` and `GOLD-R02`;
- `CAUSAL_SUPPORT` and `PRESSURE_GROUP`;
- probes `P02`, `P03`, `P04`, and `P05`;
- three repetitions and the 78-call empirical budget;
- authority classes, evaluation rubric, or claim ceiling; or
- the meanings of CASE A/B/C/D.

V1.1 adds no ontology, Global Map, production code, or production schema.

## 3. Tightened extractor envelope

The extractor packet must state these mechanical output requirements:

1. Return exactly one JSON object.
2. Do not use Markdown fences or prose before or after the object.
3. Use only the frozen fields:
   `relations`, `abstentions`, `relation_type`, `source_fact_refs`,
   `target_ref`, `member_roles`, `fact_ref`, `role`, `authority_class`,
   `evidence_refs`, `rationale`, `support`, `candidate_area`, and `reason`.
4. `relation_type` must be `CAUSAL_SUPPORT` or `PRESSURE_GROUP`.
5. Emit at most two relation entries.
6. Emit at most three members in any `PRESSURE_GROUP` entry.
7. Use only the frozen authority values:
   `ACCEPTED`, `DETERMINISTIC_DERIVATION`, and `INTERPRETIVE`.
8. Use only the frozen support values: `strong`, `moderate`, and `weak`.
9. Use only valid source/member references from the supplied source boundary.
10. Use the frozen abstention shape only: `candidate_area` plus `reason`.

The limits are representational constraints, not hints about the expected
answer. Zero or one relation remains valid when supported by the source.
These requirements do not expose the gold reference, gold IDs, expected
endpoints, expected member count, or evaluator targets.

## 4. Mechanical structural validator

Before canonical rendering, apply a deterministic research-local validator to
each raw extractor response. The validator returns either
`STRUCTURE_VALID` or `FORMAT_INVALID` and machine-readable violation reasons.

It may check only:

- JSON parseability and one-object shape;
- allowed top-level and nested fields;
- required fields and JSON value types;
- allowed enum values;
- relation count no greater than two;
- pressure-group member count no greater than three;
- source-reference syntax and membership in the supplied source identities;
- relation-specific structural shape;
- duplicate relation or member structures; and
- abstention object shape.

For mechanical relation shape, `CAUSAL_SUPPORT` has one source reference and
one target reference. `PRESSURE_GROUP` has at least two and no more than three
member/source references, one target reference, and member roles for its
members. The validator does not decide whether any relation is narratively
correct or gold-equivalent.

The validator must not judge:

- causal truth or direction as a narrative claim;
- whether a pressure group is semantically good;
- whether a relation matches `GOLD-R01` or `GOLD-R02`;
- which relation should be preferred; or
- whether an abstention was substantively wise.

Those remain extraction-evaluation questions.

## 5. Frozen behavior for invalid output

For `STRUCTURE_VALID`:

- retain the exact raw response;
- retain the validator result and reasons;
- canonically render it exactly as specified by V1; and
- use that projection for the paired `R-DERIVED` repetition.

For `FORMAT_INVALID`:

- retain the exact raw response;
- retain the validator failure reasons;
- do not truncate, select a subset, repair, coerce, retry, synthesize, or
  call another model; and
- set the downstream `R-DERIVED` overlay to `EMPTY` for that repetition.

For a `FORMAT_INVALID` repetition, the model-visible downstream packet must
contain no relationship-overlay block, placeholder, empty object or list,
header, status, or metadata. Apart from opaque bookkeeping that is not shown
to the model, it must be byte-identical to the paired `B0` packet for the same
probe and repetition. The generator is not told why the overlay is empty.
This is intentional: operational format failure becomes part of
extraction-fidelity evidence instead of making the experiment unexecutable.

No invalid response may be converted into a valid relation by interpretation
of what the model probably meant.

## 6. Evaluation of invalid output

The extraction evaluator still receives the exact raw extractor response,
alongside the frozen source and gold reference through the blinded evaluation
packet.

For `FORMAT_INVALID` observations, the normalized evaluation must record:

- schema/format adherence: failure;
- projection usability: failure;
- unsupported invention: assessable when the raw content permits;
- semantic claims: assessable only when unambiguously recoverable from the
  raw response; and
- no relation recovery credit based on reconstruction or semantic repair.

Malformed structure itself remains part of extraction-fidelity evidence.

## 7. Decision gate preservation

The original gate remains unchanged:

- CASE A requires that `R-GOLD` improves over `B0` on the primary family and
  `R-DERIVED` recovers most of that value with acceptable fidelity.
- CASE B requires that `R-GOLD` improves over `B0` but extraction does not
  reliably recover usable/value-preserving relations. A `FORMAT_INVALID`
  observation may contribute evidence toward CASE B, but cannot establish CASE
  B without the independent downstream `R-GOLD` versus `B0` finding.
- CASE C and CASE D retain their frozen V1 definitions.

The aborted V1 attempt is excluded from all V1.1 comparisons and gate counts.

## 8. New-run boundary

V1.1 empirical execution starts at **0/78**. The three aborted V1 extractor
observations are not reused, evaluated, or counted. Backend-qualification
canaries are not empirical observations.

The previously qualified `multi_agent_v1` / `gpt-5.6-sol` backend may be
reused only if its runtime properties remain unchanged; otherwise it must be
requalified before execution.

## 9. Adversarial review checklist

Before V1.1 publication, verify that:

- empty-overlay fallback requires no semantic repair;
- information parity is preserved;
- validation is mechanical rather than semantic scoring;
- failure status cannot leak into the downstream prompt;
- the stricter envelope does not reveal the gold answer;
- `R-GOLD` versus `B0` remains measurable if all derived outputs fail;
- CASE B remains reachable without post-hoc rescue; and
- old observations are clearly excluded.

## 10. Scope and status

This amendment changes no production code, tests, ontology, Global Map, or
frozen V1 file. It authorizes no empirical calls until V1.1 is reviewed and
the separate execution task begins.

**STORY-INSTANCE RELATIONSHIP EXTRACTION V1.1:**

**PREREGISTERED — NOT EXECUTED — AWAITING HUMAN REVIEW**
