# Attempt 8 Invalidation Audit

Status: INVALIDATED — REMAINS BLINDED — NO PRODUCT INFERENCE

Attempt 8 was invalidated at `3/78`, before any generator call. The two
runtime canaries and all three extractor observations completed through the
RuntimeAdapter, passed cumulative reconciliation, were explicitly closed with
`multi_agent_v1__close_agent`, and received durable closure evidence.

The first generator packet construction then failed in the run-specific
orchestration helper. Its prompt path attempted to parse the already-raw
`raw-response.txt` bytes as though they were a JSON envelope object. This is a
run-specific packet-helper defect, not a journal, adapter, progress-gate, or
worker-lifecycle failure.

The protocol requires stopping on any tooling defect discovered after live
execution begins. No patch-and-continue, generator launch, response capture,
repair, retry, unblinding, scoring, CASE classification, or product inference
was performed.

## Authoritative state

- Completed empirical chains: `3`
- Allocated empirical observations: `3`
- Unique opaque IDs: `3`
- Unique agent IDs: `3`
- Hash mismatches: `0`
- Incomplete chains: `0`
- Conflicting bindings: `0`
- Malformed allocations: `0`
- Worker closure records: `3`
- Unclosed completed workers: `0`
- Cumulative reconciliation: `ready=true`

The three extractor responses remain raw blinded evidence only and are
excluded from all research conclusions because Attempt 8 is invalidated.
