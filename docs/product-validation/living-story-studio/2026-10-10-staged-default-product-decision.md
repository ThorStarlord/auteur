# Living Story Studio — Staged Default and Fair-Baseline Product Decision

**Date:** 2026-10-10  
**Status:** OWNER-SELECTED PRODUCT DIRECTION / IMPLEMENTATION EVIDENCE-GATED  
**Scope:** Auteur Beginner browser UX; no changes to narrative authority, data acceptance, GitHub merge policy, or public release authorization.  
**Supersedes:** the specific *keep opt-in pending comparative human superiority* promotion recommendation in [the 2026-10-10 adversarial synthesis](adversarial-synthesis.md); historical source findings and unexecuted qualification remain valid.

## 1. Decision

**Living Story Studio / graph-first creation is Auteur's selected target default experience.**

Adopt it in stages: after real basic safety qualification, make it the **development default**; after reliable everyday qualification, make it the **early-user beta default**; retain the existing Beginner interface as a reachable fallback. Broad promotion and retirement of the old UI remain later decisions.

This product-owner decision is sufficient to select design direction. It does **not** establish that all writers prefer graph-first, that the implementation passes tests, or that a protected merge/release is authorized.

The historical Beginner Home remains a **technical/operational comparator, not a UX gold standard**. Its existing regression coverage, integration and longer history cannot substitute for evidence of experienced creative usefulness. Recorded owner feedback describes it as clunky; this is direct owner-observed evidence, not representative user research.

The selected graph-first direction has two substantive goals: **spatial story creation from the first session** and **relationship visualization**. Tests that measure only speed to first prose are incomplete; tests that measure only visual appeal are also incomplete.

## 2. Four distinct questions

| Question | What is established | Decision owner / evidence |
| --- | --- | --- |
| Which product direction is desired? | Graph-first is selected as target default | Product owner selection; no comparative population study needed to **select** a direction |
| Is the candidate safe for routine author work? | Not yet established by live Browser/local suite at this date | Executable checks for preservation, recovery, authority, failure truth |
| Should development/early users use it by default? | Conditional on proportional safety/utility requirements below | Reversible rollout decision after relevant checks |
| Should the broad product retire old Beginner? | Not yet decided | Real reliability, accessibility, migration cost, author feedback and publication authority |

**Symmetric product evidence, risk-specific safety:** old and new interfaces are evaluated fairly for value and friction. Actual operational switching/migration risk can justify additional safeguards, but an incumbent has no presumed UX superiority merely because it ships.

## 3. Progressive adoption contracts

### Stage A — Selected development direction (now)

- Invest in graph-first Studio as the preferred future interface; preserve the working canvas and scene-first entry.
- Treat the old Beginner UI as **fallback and comparison baseline**, not a UX design to reproduce mechanically.
- Do not require a cohort preference study or exhaustive UX equivalence to *choose this direction*.
- Preserve existing Story Identity/Structure/Realization/Expression/relations/Book owners and their explicit author acceptance guarantees.

### Stage B — Development default (after essential safety checks)

- On a runnable local app, demonstrate create/edit/switch/reopen; working text/links/layout survive reload; scene editing and Quick Draft handoff behave truthfully; save conflicts/failures preserve recoverability; derived graph never accepts canon.
- Execute the exact changed Browser → HTTP → persistent-owner route; simulated DOM or static substring tests alone are not enough.
- Ensure an obvious fallback, rollback and recoverable user work. No hidden migration or destructive conversion.
- At this stage the **developer's normal entry route may become Studio**, while previous Beginner remains accessible. This is not production release or a claim of universal preference.
- If an external host-agent provider gate is unavailable, distinguish which safe subset was actually exercised; do not pretend full Quick Draft generation passed or expose unavailable actions as working.

### Stage C — Early-user beta default

- Qualify everyday flows end to end, initial accessibility/keyboard access, failure handling and rollback for users' real work.
- Clearly label unfinished capabilities; collect concise task-linked feedback during actual writing.
- Comparative studies can be targeted to questions that could change the decision; they are **not an unconditional gate** demanding proof that most people prefer the graph.

### Stage D — Broad default and legacy retirement (separate)

- Requires stronger experience/reliability/accessibility and migration evidence appropriate to affected users, with proper merge/release authority.
- No requirement that *every* user prefer graph-first, but no inference that owner's preference represents the population.
- Retire legacy only once needed capabilities/guarantees, migration/recovery and fallback-policy decisions are addressed.

These stages describe **product intent and evidence thresholds**, not permission to bypass repository governance, automatically merge PRs, or deploy.

## 4. Preserve guarantees, not historical interface conventions

**Hard invariants:** explicit author control over story meaning; durable working notes; honest failure/conflict reporting and recovery; no shadow canon; accepted history and provenance preserved; accessible essential paths; exact source and user-intent identity.

**Replaceable choices:** card layouts, form sequencing, node/edge presentation, navigation hierarchy, prominence of panels, whether the graph or prose editor is the initial focus. They must earn their place through author value, not tenure.

Fix implementation failures at the lowest owning layer. Do not restart strategic divergent exploration after an ordinary editor or persistence defect.

## 5. Blame the process, preserve responsibility

### What went wrong in the decision process

- **Proxy substitution:** "already implemented" was treated as "product/UX mature."
- **Unequal burden:** new Studio needed unusually strong proof to displace a baseline with no equivalent demonstrated UX superiority.
- **Conflated gates:** product owner selection, local safety, beta usability, and broad release were treated as one default-promotion question.
- **Omission cost ignored:** delayed use also delays learning and retained product value, especially where reversal is cheap.

These are **decision-system defects**, not grounds for personal fault-finding. The corrective move is to change the review prompts and adoption rules, not label a reviewer or developer incompetent.

Blameless does not mean accountability-free: report which decision changed, what evidence was available, who owns the next repair/verification, and how to detect the failure mode next time. Deliberate safety violations remain separately subject to normal repository policy.

### Lightweight fair-baseline check for major UX replacement choices

1. What does the incumbent **actually** prove about usability, distinct from code existence?
2. Are comparable evidence standards applied to both designs' product benefits and weaknesses?
3. What are the real safety invariants and migration risks, separate from interface taste?
4. What is the cheapest reversible adoption stage that both creates author value and yields new evidence?
5. What is the cost of **not** adopting and learning? What direct owner feedback is available, and what claim cannot be generalized?

This is a **thinking aid, not a mandatory score, committee or release approval form**. Record only decision-changing answers.

## 6. Active execution and evidence handoff

- [#360](https://github.com/ThorStarlord/auteur/issues/360): exact-head local/browser safety qualification, including inspector editing, save/restart, re-entry, conflict recovery and authority boundaries. This is the **near-term gating responsibility** for Stage B.
- [#369](https://github.com/ThorStarlord/auteur/issues/369): compare product value and investigate hybrid alternatives **when real outcomes could change a meaningful design decision**. It is no longer a blanket precondition for Stage B.
- [#318](https://github.com/ThorStarlord/auteur/issues/318), [#310](https://github.com/ThorStarlord/auteur/issues/310): separate six-Chapter Book and host-agent Quick Draft gates remain; do not claim they passed from Studio code review.
- Original reviewed SHA: \`bd2ba539d2f300941681fa7c7b80ab4765354b79\`; inspected repair candidate SHA: \`a864ea42f230a948b33809553c2f4accfee4859b\`. No real running-app safety PASS has been established in this decision.

## 7. Revisit triggers

- **Concrete work loss or authority breach:** bounded engineering repair → focused verification; block unsafe author work.
- **Graph useful but clunky:** UX iteration rather than fundamental product restart.
- **Prose/graph integration incomplete:** architecture or interaction seam repair.
- **Persistent observed lack of spatial/relational value:** reconsider hybrid/prose-first, then reopen product discovery as warranted.
- **Safety verified and normal use informative:** progress to development default with visible fallback and feedback, not another speculative adversarial review.

**Compact law:** *Preserve proven guarantees, not unproven interfaces. Hold existing and new UX to fair value standards; size safety checks to consequence and reversibility; improve the decision process rather than blaming individuals.*
