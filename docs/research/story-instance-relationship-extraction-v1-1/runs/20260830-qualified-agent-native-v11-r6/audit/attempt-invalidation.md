# Attempt 6 Invalidation

Status: INVALIDATED — executor reconciliation-gate defect.

Frozen protocol: a6f7ded7d01cfdd149c526a71e0c751af517e0b1
Harness: 11c6f32ccca7dd9911b4646edfdcb3f2428cdce9
Transport journal: 1093409554ddfe45771e9a19acd148b1978a3ea1
Runtime adapter: d36989aa8a4e7d5ccd15bfdc6acf0b0a0b68e7f2
Live integration qualification: 1c945713bf4241e2588437aefe3c0f919275a4f4

## Boundary

- Runtime canaries: 2/2 PASS.
- Extractor calls: 2/78, both complete authoritative chains.
- Generator calls: 0.
- Evaluator calls: 0.
- Unblinding: not performed.
- Product inference: none.

## Invalidation reason

After the second extractor chain completed, the executor called journal reconciliation with only the current schedule position as the expected set. Because the first completed chain was already present, the frozen journal correctly reported the aggregate journal as not ready for that one-element expected set. The executor treated this expected-set mismatch as a failure and stopped.

This is an executor-level reconciliation-gate defect discovered after empirical inference began. The qualified journal and adapter were not modified, and the second extractor response was not retried or reassigned.

## Disposition

Attempt 6 is invalidated at 2/78. Completed raw responses and authoritative journal chains are preserved. No further empirical calls, evaluator calls, scoring, unblinding, CASE classification, or result PR will occur. A future attempt requires a fresh run and a pre-tested aggregate reconciliation gate.

