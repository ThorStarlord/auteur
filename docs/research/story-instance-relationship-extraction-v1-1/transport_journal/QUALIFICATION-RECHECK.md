# V1.1 Transport Journal Clean Requalification Report

## Frozen anchors

- Protocol: `a6f7ded7d01cfdd149c526a71e0c751af517e0b1`
- Qualified harness: `11c6f32ccca7dd9911b4646edfdcb3f2428cdce9`
- Journal implementation: `1093409554ddfe45771e9a19acd148b1978a3ea1`
- Prior non-qualifying report: `5d019217388ef0776955647702b3c6afa23d7449`

## Implementation immutability

Both `transport_journal.py` and `test_transport_journal.py` are byte-identical to implementation commit `1093409…`. No implementation or test edits were made during this requalification.

## Inference accounting

- Model calls: 0
- Agent/provider/inference calls: 0

The previous qualification remains non-qualifying because its two canaries used model workers. This is a fresh qualification execution and does not reclassify that historical evidence.

## Qualification

- J1 lifecycle: PASS
- J2 binding overwrite refusal: PASS
- J3 response overwrite refusal: PASS
- J4 derived-ledger failure safety: PASS
- J5 hash mismatch detection without mutation: PASS
- J6 derived-ledger rebuild: PASS
- J7 missing-event refusal: PASS
- J8 duplicate-agent refusal: PASS
- J9 duplicate-opaque-ID refusal: PASS
- J10 synthetic 78-observation journal: PASS
- Crash recovery: PASS
- Derived-ledger failure safety: PASS

All inputs were locally constructed synthetic data in fresh temporary directories. No prior canary, Attempt 4, or empirical artifacts were reused.

## Synthetic reconciliation

- Complete event chains: 78
- Unique opaque IDs: 78
- Unique agent IDs: 78
- Matching response hashes: 78
- Hash mismatches: 0
- Missing/incomplete chains: 0
- Conflicting bindings: 0
- Authoritative overwrites accepted: 0

## Tests

- Transport-journal tests: 10 passed
- Combined frozen-harness/journal tests: 24 passed
- Failures: 0
- Transport implementation coverage: 92%

## Git

- Branch: `research/story-instance-relationship-extraction-v1-1-transport-journal`
- Requalification commit: this additive clean-requalification commit

## Empirical status

ATTEMPT 5 NOT STARTED

0/78

## Conclusion

TRANSPORT JOURNAL:
QUALIFIED — ATTEMPT 5 MAY BEGIN
