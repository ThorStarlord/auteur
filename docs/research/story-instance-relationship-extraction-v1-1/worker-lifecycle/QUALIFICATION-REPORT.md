# V1.1 Worker Lifecycle Qualification Report

## Frozen anchors

The qualification started from cumulative-gate commit
`2ab1c83e8b8e3ac41749a56f0caf14d773932e1e`. The protocol, semantic harness,
transport journal, runtime adapter, and cumulative reconciliation gate were
not modified.

## Runtime close capability

The actual runtime operation was `multi_agent_v1__close_agent`. Each call used
the exact agent ID returned by `multi_agent_v1__spawn_agent`. Every call
returned an acknowledgment with the worker's completed response, and each
acknowledgment was persisted as `05-worker-closed.json`.

## Local lifecycle gate

Added and qualified:

- `transport_journal/worker_lifecycle.py`
- `transport_journal/test_worker_lifecycle.py`

L1–L6 all passed. The gate rejects missing, premature, duplicate, or
wrong-agent closure evidence and blocks the next launch when any prior
allocated observation lacks closure evidence.

## Live canaries

| canary | opaque ID | agent ID | journal | reconcile | close | closure evidence |
|---|---|---|---|---|---|---|
| C1 | `C_R7_LIFE_01` | `01a055cc-37e3-7413-8602-49784d0e0bf9` | PASS | PASS | PASS | PASS |
| C2 | `C_R7_LIFE_02` | `01a055cc-5860-7d23-8c1e-e28b721f8615` | PASS | PASS | PASS | PASS |
| C3 | `C_R7_LIFE_03` | `01a055cc-7ed4-7c90-a356-e8cf4ee750fc` | PASS | PASS | PASS | PASS |
| C4 | `C_R7_LIFE_04` | `01a055cc-9a6b-7e51-a722-587138153ba4` | PASS | PASS | PASS | PASS |
| C5 | `C_R7_LIFE_05` | `01a055cd-1f77-74e2-8498-67405df0623f` | PASS | PASS | PASS | PASS |
| C6 | `C_R7_LIFE_06` | `01a055cd-44fb-7131-8349-6ba1f042051f` | PASS | PASS | PASS | PASS |
| C7 | `C_R7_LIFE_07` | `01a055cd-6fc0-7dc2-8cbd-f5723063b2c8` | PASS | PASS | PASS | PASS |
| C8 | `C_R7_LIFE_08` | `01a055cd-94f9-78d2-8923-d771740c5d39` | PASS | PASS | PASS | PASS |

## Slot reuse

- C1–C8 launches: `8/8 PASS`
- C6–C8 after prior explicit closures: `3/3 PASS`
- Maximum running concurrency: `1`
- Unclosed completed workers: `0`

## Reconciliation

- Complete chains: `8`
- Unique opaque IDs: `8`
- Unique agent IDs: `8`
- Matching raw hashes: `8`
- Hash mismatches: `0`
- Incomplete chains: `0`
- Conflicting bindings: `0`
- Malformed allocations: `0`
- Closure records: `8`

## Inference accounting

- Empirical calls: `0/78`
- Qualification canaries: `8`
- Attempt 8: not started

## Git

- Pre-canary logic commit: `9609b7a024ce855d89d61f5bbd51d66e4fb6ff8e`
- Branch: `research/story-instance-relationship-extraction-v1-1-worker-lifecycle`

## Conclusion

**WORKER LIFECYCLE: QUALIFIED — ATTEMPT 8 MAY BEGIN**

Attempt 8 was not started.
