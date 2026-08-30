# Attempt 4 Invalidation

Run: 20260830-qualified-agent-native-v11-r4

Status: INVALIDATED — transport-ledger integrity failure; no experimental result.

Frozen protocol: a6f7ded7d01cfdd149c526a71e0c751af517e0b1
Qualified harness: 11c6f32ccca7dd9911b4646edfdcb3f2428cdce9

## Evidence boundary

- Transport canaries: 2/2 passed, unrelated to the experiment.
- Extractor raw responses preserved: 3.
- Generator raw responses preserved: 36.
- Evaluator raw responses preserved: 39.
- Raw empirical responses preserved: 78.
- Unblinding: not performed.
- CASE classification: none.
- Product inference: none.

## Invalidation reason

All 78 empirical calls were executed sequentially and their raw response files were written. During the required mechanical correction of the transport ledger's response hashes, the correction command failed and its Python traceback was written into the ledger file. The ledger was therefore replaced with an explicit invalidation record.

The raw response files and blinded schedule remain preserved, but the authoritative durable mapping required by the protocol cannot be certified from the damaged ledger. No identity may be reconstructed from notification order, response content, or timestamps.

## Disposition

Attempt 4 is invalidated and remains blinded. No evaluator outputs are scored, no condition map is revealed, and no result PR or CASE classification is created. A future attempt requires a new run ID, fresh workers, and safer transactional ledger writes with validation before replacing the prior ledger.

