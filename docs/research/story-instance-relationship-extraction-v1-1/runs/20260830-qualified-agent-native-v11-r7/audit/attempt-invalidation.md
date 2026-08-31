# Attempt 7 Invalidation Audit

Status: INVALIDATED — REMAINS BLINDED — NO PRODUCT INFERENCE

Attempt 7 was invalidated before the first generator response. The first
generator allocation at schedule position `2` was durably published, but the
worker launch was blocked by the agent-thread limit after completed canary and
extractor workers had not yet been closed. No generator worker was launched,
and no generator response was captured.

The three extractor observations were complete and preserved:

- schedule position `56`, opaque ID `O_YPMBRWY1CEQIJA`;
- schedule position `55`, opaque ID `O_JKMHBAASQQOY1A`; and
- schedule position `10`, opaque ID `O_PWBWKYBMOIFLUA`.

The incomplete allocation was:

- schedule position `2`, opaque ID `O_XNIVXFT3HX1H8A`.

The cumulative progress gate reported:

```text
expected_positions       = {2, 10, 55, 56}
allocated_positions      = {2, 10, 55, 56}
malformed_allocations    = 0
complete_chains          = 3
unique_opaque_ids        = 3
unique_agent_ids         = 3
hash_mismatches          = 0
incomplete_chains        = 1
conflicting_bindings     = 0
ready                    = false
```

No incomplete event was repaired, overwritten, bound, captured, or completed.
No extractor response was scored or interpreted for research conclusions. No
generator or evaluator calls were made after the three extractor calls. No
unblinding, case classification, result inference, or production work was
performed.

Attempt 7 remains excluded from empirical conclusions. A future attempt must
start from a fresh run and must close completed worker threads before any new
worker launch.
