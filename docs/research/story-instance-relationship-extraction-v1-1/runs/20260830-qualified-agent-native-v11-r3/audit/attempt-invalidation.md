# Attempt 3 Invalidation

Status: INVALIDATED — execution attempt failure, not an experimental result.

Run: 20260830-qualified-agent-native-v11-r3
Protocol SHA: a6f7ded7d01cfdd149c526a71e0c751af517e0b1
Harness SHA: 11c6f32ccca7dd9911b4646edfdcb3f2428cdce9

## Boundary

- Extractor calls captured: 3/78.
- Generator calls completed before abort: 6/78.
- Total calls attempted/completed before abort: 9/78.
- Extraction evaluators: 0.
- Downstream evaluators: 0.
- Unblinding: not performed.
- Empirical result: none.

## Invalidation reason

The concurrent generator launch exceeded the available multi-agent thread limit. The resulting completion notifications did not include a reliable mapping from completed agent IDs to the opaque schedule IDs. The returned responses therefore cannot be reconciled to exact blinded positions. The notifications also contain duplicate P02-shaped responses even though the first six schedule positions contain only one P02 position, which is an additional traceability warning.

Because exact schedule-to-response identity is required, these generator outputs must not be scored, reused, or used to infer any condition effect. No further calls were made after the traceability failure.

## Disposition

This run is invalidated as an execution-attempt failure. The frozen protocol and qualified harness remain unchanged. A future attempt must start from a fresh run ID and fresh workers, with bounded concurrency and durable opaque-ID-to-agent-ID capture before launching subsequent calls.

