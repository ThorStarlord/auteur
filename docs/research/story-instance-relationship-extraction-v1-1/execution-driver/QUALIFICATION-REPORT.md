# V1.1 Execution Driver Qualification Evidence

Source qualification candidate: `d25dc7584abafab64d64f0d910ae4e22760f82d0`

This report is additive evidence for the reusable execution driver. It does
not start Attempt 9 and does not contain empirical observations.

## Composite transaction

The executor-facing path is:

`begin_observation` → `bind_observation` → `finish_observation` →
`record_close_and_release`.

`finish_observation` performs capture, completion, cumulative reconciliation,
schedule reload verification, and atomic schedule persistence before closure.

## Full synthetic qualification

- Phase accounting: `3 / 36 / 3 / 36 = 78`
- Incremental reconciliation gates: `78/78 PASS`
- Transport complete chains: `78/78`
- Unique opaque IDs: `78`
- Unique synthetic agent IDs: `78`
- Matching hashes: `78`
- Worker closures: `78`
- Schedule reload persistence checks: `78/78`
- Generator preflight: `36/36`
- P02 parity: `PASS` for all three repetitions
- Book-4 routing: `9/9 exact`
- Evaluator packet integrity: `3/3 + 36/36 exact`
- Pre-unblind readiness: `PASS`

The phase gates are chronological: generator packets are compiled only after
the three extractor observations; evaluator packets are compiled only after
the 36 generator observations at cumulative N=39; evaluator observations then
consume those compiled packets.

## Research tests

Command:

```text
python -m pytest run_tools/test_v11_empirical_driver.py docs/research/story-instance-relationship-extraction-v1-1/harness/test_execution_harness.py -q
```

Result: `24 passed`.

## Full-suite baseline comparison

Command used for the relevant previously failing test areas:

```text
python -m pytest -q tests/test_author_decisions_cli.py tests/test_story_discovery_recommendation_basis.py tests/test_story_discovery_review.py
```

Parent `a6a3b77018d877ac0f8e93b658adf1d117b6a334`: `4 failed, 39 passed`.

Candidate `d25dc7584abafab64d64f0d910ae4e22760f82d0` plus the qualification
changes: `4 failed, 39 passed`.

The four failures are identical on both sides:

- `tests/test_author_decisions_cli.py::test_import_path_is_feature_worktree`
- `tests/test_story_discovery_recommendation_basis.py::test_qualified_comparative_non_adjudicable_is_a_valid_project_state`
- `tests/test_story_discovery_review.py::test_recommendation_review_reconstructs_writer_facing_evidence`
- `tests/test_story_discovery_review.py::test_composed_review_explains_borrows_and_preserved_primary`

No new failure was introduced by the execution-driver changes. These tests are
outside the touched research boundary and were not modified.

## Inference accounting

- Model calls: `0`
- Agent calls: `0`
- Provider calls: `0`
- Attempt 9: `NOT STARTED`, `0/78`

## Status

`EXECUTION DRIVER: FULLY QUALIFIED — ATTEMPT 9 MAY BEGIN`

This status authorizes the next boundary only; it does not execute it.
