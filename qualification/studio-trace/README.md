# Consequential interpretation traceability — authentic Studio qualification

**Date:** 2026-11-17
**Baseline:** `main@7a34ec8a`
**Disposition: NO CHANGE WARRANTED.** Existing Studio behavior satisfied the bounded criterion.

## What ran

One frozen brief, one real Studio request, one genuine host-agent construction. No modification to `system.txt`, `user.json`, or any generation instruction. No added reminders about ambiguity, provenance, or interpretation disclosure.

Frozen brief: a fourteen-Book optimistic series about a guild of bridge-wards whose signature makes a span legal. Governing criterion: *"a bridge is sound only if a person who did not build it will cross it."* Book 12 must decide whether to close the Old Span, certified by a ward later shown to have been paid by its builder.

Request `49a58bf066cf6389…`, model `deepseek-v4.1-flash` via `opencode-general-subagent`.

## Attempt 1 — rejected on a mechanical error

The candidate recorded **7 interpretations** and was rejected:

> `interpretation 'interp-use-completes-the-certificate' affects unknown nodes: phase-public-underwrites, phase-old-span`

`affects` resolves against **node** ids; the model referenced **phase** ids. The repair removed phase ids from `affects` and changed nothing else. Preserved at `attempt-1-rejected/`.

This is a real, narrow representational finding: the model naturally reached for phase-level dependencies that `affects` cannot express. The existing validation caught it correctly. **No semantic content was altered by the repair.**

## Attempt 2 — admitted

47 nodes, 43 links, 9 phases, 10 open questions, 2 opportunities. Status `ready`. No canonical writes.

## The consequential interpretation

`interp-use-completes-the-certificate`, flagged `author_decision_required: true`:

> "The governing criterion is treated as a structural law rather than a motto: a bridge is sound only when someone who did not build it crosses. Read this way the certificate is not completed at the signing but at a strange…"

- **Recorded on the existing surface** — `working_interpretations`, authority `agent_interpretation`, 7 items, 2 needing an author decision.
- **`affects` accurate** — `engine-crossing-public`, `structure-criterion-test`, `trope-crowd-crosses`, `structure-book-12-crucible`, `theme-use-is-the-test`.
- **Consequences stated conditionally**, not as necessity: *"if use has always been the completing act, the forty-year crossing public is already a party to the certificate and can be addressed as one."*
- **The distant consequence is explicitly tied to it**: Book 12's node carries conditional/reading language rather than asserting the closure follows.

## Counterfactual check

Replace the reading with the other credible one — soundness requires *willingness* to cross, not actual crossing — and Book 12's outcome changes materially: forty years of daily use would discharge the doubt rather than make the public a party. The architecture makes that dependency intelligible through the interpretation record rather than burying it.

## What this establishes

**Observed product behaviour.** The unmodified workflow selected a consequential interpretation of an underspecified author criterion, recorded it on the existing surface, named the elements it determines, stated its consequences conditionally, and extended it to a distant Book without presenting it as entailed.

**This is the fifth uncoached success and the first in authentic Studio construction.** The VLS-01 failure did not reproduce here.

## What remains unqualified

One run, one model, one scenario. No fresh-context reader was separately exercised — the interpretation record was inspected directly, which is weaker evidence for author-facing usefulness than a reader test. No human author. No comparative claim against an ordinary LLM workflow.

## Not done, deliberately

No intervention was tested, because no consequential omission occurred. The prior research proposed three diagnoses for the VLS-01 failure and withdrew two; this run provides no support for a fourth.

## The one finding worth carrying forward

`affects` is node-only. Phase-level dependencies are not representable, and a capable agent reached for them unprompted. That is a bounded, testable representational question — worth more than another prompt experiment, and it is a schema question rather than a reasoning one.

## T10

Unchanged and open. This is not a comparative evaluation.
