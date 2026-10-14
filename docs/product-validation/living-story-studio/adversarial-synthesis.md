# Living Story Studio — Adversarial Synthesis and Decision

**Source target:** \`bd2ba539d2f300941681fa7c7b80ab4765354b79\`  
**Reviews:** [Product](adversarial-product-review.md), [UX](adversarial-ux-review.md), [Architecture](adversarial-architecture-review.md)  
**Date:** 2026-10-10  
**Status:** source-evidence synthesis with a narrow logic-only DOM-stub reproducer; not end-to-end or human validation.

## Executive verdict

**CONTINUE GRAPH-FIRST AS OPT-IN; REPAIR CONFIRMED WORK-PRESERVATION FAILURES; RUN EXACT-HEAD QUALIFICATION; DO NOT PROMOTE DEFAULT.**

- **Product:** a legitimate spatial creation objective and working graph candidate exist, but integrated relationships-to-canon value is not demonstrated. Current graph-first default is unearned.
- **UX:** inspector switching drops uncommitted author prose in an extracted-handler reproduction. Re-entering from Home without the original URL creates a new canvas. Core author trust and longitudinal re-entry must be repaired.
- **Architecture:** separate working store and derived projections are justified in principle. Full-document saves plus unbounded receipt/tombstone history and incomplete source/working identity warrant focused qualification/simplification, not a new graph database.
- **Qualification:** [#360](https://github.com/ThorStarlord/auteur/issues/360), [#318](https://github.com/ThorStarlord/auteur/issues/318), and [#310](https://github.com/ThorStarlord/auteur/issues/310) remain open. No real browser, full-suite or human-value PASS evidence has been produced by this review.

## 1. Consolidated finding register (stable IDs)

| ID | Class / confidence | Material consequence | Earliest correct next move |
| --- | --- | --- | --- |
| LSS-R01 | **Source behavior reproduced in isolated original JS handler**, UX U-01 | Unsaved inspector text disappears when changing selected node | **Repair**, then Browser S2 verify |
| LSS-R02 | **Source-established navigation path**, UX U-02 | Returning through Home starts fresh canvas, making prior work hard to recover | **Repair** with local canvas entry, then S8 verify |
| LSS-R03 | **Product/architecture gap**, P-01 / A-03 | Working graph and read-only source graph share screen but lack evidence-backed author-facing relationship/acceptance roundtrip | **Investigate** S4/S5/S7; no shadow canon |
| LSS-R04 | **Source-supported longitudinal risk**, A-01/A-02 | Persistent command fingerprints/tombstones and whole-document rewrites can grow resource costs | **Measure** edit-history latency/size; choose bounded retention if warranted |
| LSS-R05 | **Source-supported authority ambiguity**, A-04/U-05 | Chapter change files may be shown as "changed" without proving accepted Chapter history | **Verify** relation-change lifecycle with accepted/unaccepted fixture |
| LSS-R06 | **Product/UX hypothesis**, P-03/U-03 | Graph manipulation, dual scene intents, and returning to guided Quick Draft may cost more than spatial discovery creates | **Compare** S1/S3/S4/S5 with baseline/hybrid |
| LSS-R07 | **Intentional prototype constraint**, A-06/U-04 | 1400×1040 positions, 200 notes, 500 links; literal infinite-canvas claim cannot be made | **Describe bounds** and test S6; defer graph engine |
| LSS-R08 | **Review-limit evidence gap**, all passes | Runnable/browser/host-agent/human value claims remain unavailable | **Follow #360/#318/#310**; no unsupported PASS |
| LSS-R09 | **Source-backed interpretation boundary**, A-05 | Workflow dependency paths should not be described as certain narrative consequences | **Preserve disclaimer**; test author comprehension S7 |

These findings are not equally urgent. R01 is actual work preservation; R02 affects everyday re-entry. R03/R06 determine product value but require experience evidence. R04/R05 warrant bounded probes before any large refactor.

## 2. Adversarial disagreement reconciliation

**Graph-first vs prose-first:** the product review cannot show the graph's additional spatial/relationship value is realized end-to-end; the UX review shows two avoidable blockers. This supports *fixing author trust while retaining an opt-in graph*, not concluding the product direction is false.

**Explicit Save vs autosave:** an explicit Save button is not intrinsically wrong, but Studio elsewhere saves scene input on change and says work is saved locally. The extracted handler execution showed that a user can type, switch, and lose work. Repair the information model, not merely add warning text.

**Separate working store vs duplication:** keeping provisional notes outside accepted story authority is essential to the no-premise goal. Removing the working store purely to reduce code is unsound. Simplification should focus on redundant replay/serialization costs when actual longevity tests justify it.

**Chapter change vs historical snapshot:** the Browser already warns that filtered current relations are not historical snapshots. That is positive. Validate acceptance provenance separately; do not build a costly historical reconstruction system from speculation alone.

## 3. Minimal repair decisions inside the user's delegated scope

**Authorize ordinary, reversible repository work only after this synthesis**, separate from the review PRs:
1. R01: capture/commit inspector changes before selection, view change, deletion, export, or other destructive navigation. Preserve pending state on failed save and show truthful feedback. Include minimal model/DOM regression.
2. R02: add an existing-canvas reopening path using the current local CanvasStore directory, with safe IDs; do not add a new library/database. Keep direct \`?canvas=\` links valid.
3. R05: only after confirming source lifecycle, label chapter changes accurately and show acceptance status if supported.
4. R04: only after measurement, bound command receipts if it can be done without breaking retry identity and crash recovery. Leave as risk until then.

**Do not automatically implement R03/R06**: these are product/UX investments that need comparative value evidence first.

## 4. Empirical discriminators

| Decision | Evidence likely to change it |
| --- | --- |
| Promote graph-first to default | S1/S4/S5/S6/S8 matched real author tasks show meaningful added spatial/relationship value at acceptable effort |
| Choose hybrid | Repeated prose momentum/focus loss in graph-first, while users still obtain clear gains from spatial relationship exploration |
| Keep current Beginner primarily prose-first | Author outcomes and preference show graph manipulation offers insufficient additional discovery value |
| Refactor working persistence | Exact-head stress test demonstrates unacceptable growth or failures; focused simpler design preserves replay/recovery |
| Change canonical story workflow | Provenance/authority error reproduced in actual accepted source; never based on UI desire alone |

**No numeric weighted product score.** Measure task completion/creative alternatives discovered, avoided duplicate work, author control, accuracy of canon understanding, recoverability, and direct observation/interpretation separately.

## 5. Qualification, promotion and stop boundaries

**Integration owner:** [#360](https://github.com/ThorStarlord/auteur/issues/360) should run the real control -> HTTP -> store and Browser scenarios against the exact candidate head, including R01/R02 repairs on their own documented SHAs.

**Story owners:** six-Chapter re-entry [#318](https://github.com/ThorStarlord/auteur/issues/318) and host-agent dogfood [#310](https://github.com/ThorStarlord/auteur/issues/310) are independent. This review cannot close them.

**Human UX:** only actual observed authors can justify broad preference or default-interface benefit. Synthesized agents and source inspection may select probes but cannot claim human usefulness.

**No merge/default/release:** the reviews are advisory and author-level product findings, not code qualification. Protected factory policy and publication authority still apply.

**Stop further theorizing now** where an actual browser, local checkout, or author observation is the nearest meaningful evidence. After repairing concrete R01/R02 mechanisms, rerun them under #360; avoid additional speculative graph features.

## 6. Final disposition

- **Product:** KEEP AS OPT-IN / DEFAULT NOT YET JUSTIFIED
- **UX:** REPAIR AUTHOR-WORK PRESERVATION AND RE-ENTRY
- **Architecture:** RETAIN CURRENT OWNERSHIP; TARGETED MEASUREMENT AND SIMPLIFICATION
- **Overall:** **REPAIR THE NARROW VERIFIED BOUNDARY, THEN VERIFY AND COMPARE**.

It is not proof that graph-first is wrong; it is proof that graph-first is not yet earned as the default. It is not a longer backlog; it is a bounded next decision.


## Post-synthesis execution addendum — 2026-10-10

Review decisions were executed within the bounded non-protected repository envelope **after** separate review reports and synthesis were committed.

- **LSS-R01:** [PR #367](https://github.com/ThorStarlord/auteur/pull/367), SHA \`1c77477226556f78fdd29d3b4536e5017a982889\`: inspector input/change captures note text, title, type, and working group before the user navigates. Extracted original handlers exercised under a minimal stub now retain the typed content; no live Browser pass claimed.
- **LSS-R02:** [PR #368](https://github.com/ThorStarlord/auteur/pull/368), SHA \`a864ea42f230a948b33809553c2f4accfee4859b\`: explicit local canvas list/selector/New action; bare Studio link uses most recent available canvas; switches await pending saves. An isolated startup-function test with stubbed fetch chose the existing \`saved-1\` canvas and minted zero IDs. No real HTTP/Browser pass claimed.
- **Qualification handoff:** [#360](https://github.com/ThorStarlord/auteur/issues/360) now contains an exact-repair-head comment and needs an actual runnable checkout. [#369](https://github.com/ThorStarlord/auteur/issues/369) separately owns comparative graph-first/hybrid/Beginner author-value evidence.

**Reconciled outcome:** R01/R02 have **source-level repairs with narrow simulated control-path evidence**, not verified closure. R03–R09 remain under their stated product or architecture evidence ceilings. Keep the full Studio + review + repair stack as **draft PRs**; no main merge, default promotion, or release is claimed.


## Superseding owner product decision — 2026-10-10

**Historical review verdict above remains an evidence record, not current product selection.** The owner later identified an unfair incumbent burden: existing Beginner was treated as presumptively good UX because implemented first. See [Staged Default and Fair-Baseline Decision](2026-10-10-staged-default-product-decision.md).

**Current selected direction:** graph-first Studio is the **target default**. Once essential real-browser/local work-preservation and authority-safety paths are verified, favor a reversible **development default** with legacy fallback; require appropriate everyday reliability for early-user beta and stronger evidence/authority for broad release. Comparative human validation remains valuable but is not a blanket Stage-B veto. This does **not** change the current missing runtime qualification or authorize protected merge/release.

Learning is assigned to the **decision process** — incumbent proxy, asymmetric evidence requirements, conflation of selection/safety/release, and omitted value of reversible learning — rather than to individual blame. Preserve provenance of the previous verdict and its unresolved technical findings.
