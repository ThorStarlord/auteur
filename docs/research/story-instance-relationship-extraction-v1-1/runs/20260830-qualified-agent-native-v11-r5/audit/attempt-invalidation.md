# Attempt 5 Invalidation

Status: INVALIDATED — non-empirical transport preflight failure.

Frozen protocol: a6f7ded7d01cfdd149c526a71e0c751af517e0b1
Qualified harness: 11c6f32ccca7dd9911b4646edfdcb3f2428cdce9
Qualified transport journal: 1093409554ddfe45771e9a19acd148b1978a3ea1
Clean journal qualification: 177f0a8886dd24babd0e22d1e9c13ddb53633620

## Preflight

Two unrelated synthetic canary workers returned CANARY:

- 01a05541-ee1f-7e31-9b43-926b5c7c3d96
- 01a05542-03c7-7db1-9c11-c904d204d346

However, the required append-only canary journal reconciliation reported:

- complete chains: 0/2
- incomplete chains: 2
- unique opaque IDs: 0
- unique agent IDs: 0
- result: FAIL

The canary event directories were not created, so the required ALLOCATED → AGENT_BOUND → RESPONSE_CAPTURED → COMPLETE evidence chain cannot be certified.

## Disposition

Attempt 5 stopped at empirical 0/78. No empirical extractor, generator, or evaluator calls were made. No empirical observations exist. No unblinding, scoring, CASE classification, result PR, or product inference was performed.

The failure is recorded without modifying the protocol, semantic harness, or transport-journal implementation. A future attempt requires diagnosing the canary journal invocation before any empirical call.

