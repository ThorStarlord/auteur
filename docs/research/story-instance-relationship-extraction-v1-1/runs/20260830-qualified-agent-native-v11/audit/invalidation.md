# V1.1 Execution Invalidation Audit

## Status

This run is **NON-QUALIFYING / INVALIDATED BEFORE UNBLINDING**.

The run completed 78 model calls:

- extractor: 3/3
- downstream generator: 36/36
- extraction evaluator: 3/3
- downstream evaluator: 36/36

No prior V1 observation was reused. No production code or protocol file was
changed. No unblind or decision-gate classification was performed.

## Defect

The three extraction-evaluator prompts did not contain the exact captured raw
extractor responses. They contained shortened reconstructions. Because the
frozen protocol requires the extraction evaluator to receive the exact raw
response, those three extraction judgments are non-qualifying evidence.

The evaluator calls are retained as raw runtime evidence, but must not be
treated as valid extraction-evaluation observations. No evaluator retry was
made, because doing so would exceed the preregistered 78-call budget.

The downstream evaluator prompts did contain the exact captured generator
responses, but downstream judgments cannot repair the invalid extraction
evaluation stage or establish the preregistered gate.

## Boundary

The run remains sealed and unblinded. It must not be reported as CASE A, B, C,
or D, and it must not authorize product work or a follow-on implementation.
