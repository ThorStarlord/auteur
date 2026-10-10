# Living Story Studio — Post-construction Adversarial Review Charter

**Frozen target:** \`bd2ba539d2f300941681fa7c7b80ab4765354b79\` (opt-in Studio branch, PRs #346–#359 plus #361)
**Main comparator:** \`85374e705115ec4884b8e0c85f3f69b6fe1c342a\`
**Date:** 2026-10-10
**Owner choice:** conduct separate Product, UX, Architecture challenges and one reconciled decision.
**Status:** source-based review; not a runtime, human-UX, merge, or release qualification.

## Decision to be made

Does the implemented graph-first Beginner experience earn its product value, interaction overhead, and architectural complexity compared with plausible alternatives?

The intended value has **two** independent parts:
1. Spatial story creation from the first session, including unstructured ideas and optional connections.
2. Relationship visualization and source-backed narrative intelligence.

A prose-only first-draft speed metric cannot determine the value of (1) and (2). Visual novelty or interface preference alone cannot prove value either.

**Comparison candidates:** A — graph-first Studio; B — graph/manuscript hybrid; C — current prose/decision-card Beginner with contextual relationship inspection. Evaluate each against both objectives, not a hypothetical generic author.

## Review separation

| Pass | Challenge | Excluded substitution |
| --- | --- | --- |
| Adversarial Product | Why should graph-first remain the primary product direction? | Code correctness is not proof of market/user value |
| Adversarial UX | Assuming spatial creation has value, is this interaction model usable and coherent? | Predicted friction is not measured human difficulty |
| Adversarial Architecture | Assuming the interaction is warranted, are ownership, persistence, evidence, and complexity proportionate? | Technical elegance alone cannot invalidate product value |
| Synthesis | Which decision, minimal repairs, and evidence are warranted? | More findings or passing static tests do not establish release readiness |

These are independently **scoped analytical passes by the current agent**, not independent human reviewers or separate agent instances. Do not imply stronger isolation.

## Authority and evidence baseline

- [Selected Studio contract](../../design/2026-10-09-living-story-studio.md) and the existing [UX product requirements](../../product/auteur-ux-product-requirements.md) express intent.
- \`src/auteur/beginner/browser/index.html\` and \`app.js\` express the existing home, two-input Quick Draft, decision cards, and book-orientation baseline.
- \`src/auteur/beginner/browser/studio.html\`, \`studio.js\`, \`studio.css\`, \`studio_store.py\`, \`studio_projection.py\`, \`studio_impact.py\`, and server routes express the candidate.
- \`src/auteur/quick_draft.py\`, \`relations/*\`, \`impact/*\`, \`beginner/book_progress.py\` are existing semantic/data owners.
- [#360](https://github.com/ThorStarlord/auteur/issues/360) is the **existing** local-execution qualification owner. [#318](https://github.com/ThorStarlord/auteur/issues/318) and [#310](https://github.com/ThorStarlord/auteur/issues/310) independently own F2/X3 and host-agent dogfood.

Reviewers must link exact source lines and, where executable, record the reproducer and observed result.

## Shared test scenarios

| ID | Scenario | Relevant properties |
| --- | --- | --- |
| S1 | Start with vague premise or **no premise**, create one free-form idea | Entry cost, freedom, persistence |
| S2 | Edit note A, switch to B, return to A, reload | Work preservation, context switching |
| S3 | Write a first scene before defining Story Identity | Writing tempo, host-agent contract |
| S4 | Add unplanned Sister Beatrice and a convent during prose | Discovery, optional typing, no duplicate authoring |
| S5 | Explore two ambiguous relationships, then reverse one | Spatial reasoning, uncertainty, relation authority |
| S6 | Navigate 12 characters, three plot threads, many edge labels | Focus, scalability, value vs manipulation |
| S7 | Revise an accepted scene and preview downstream change | Read-only implications, freshness, consent |
| S8 | Return to a six-Chapter Book after interruption | Re-entry, primary next action, source identity |
| S9 | Operate entirely by keyboard on a narrow screen | Accessibility and focus |
| S10 | Rapid edits, two tabs, interrupted save, remove/restart/restore | Durability, concurrency, failure truth |
| S11 | Change relationships after Chapter 3 | Time-aware evidence vs false historical snapshots |
| S12 | Repeated autosaves and long editing history | Resource growth, robustness |

Run equal-intent matched comparisons. Do not require a full alternate implementation when a cheaper source/flow comparison answers the specific question.

## Claim levels

- **Confirmed source defect:** behavior follows deterministically from exact code / a narrowly isolated execution. State that it is *not a live browser reproducer* if that is true.
- **Source-supported risk:** a concrete mechanism exists, but effect/severity needs runtime observations.
- **Product/UX hypothesis:** prediction to test, not a finding about actual authors.
- **Intentional trade-off:** an acknowledged limitation with a cost, rather than necessarily a bug.
- **Unsupported:** no credible evidence for the claim; retire rather than repeat.
- **External evidence missing:** requires local app, host-agent workflow, assistive technology, or real writers.

Do not use numerical weighted scores that conflate incomparable qualities.

## Execution controls

- Initial review is **read-only to product code and story authority**. Create review documents and a tracking issue only.
- No GitHub Actions, new paid provider, secret, irreversible data mutation, automatic acceptance, or default-interface change.
- GitHub connector provides source/PR evidence. Current container cannot resolve github.com; this is **an execution-environment limitation**, not a failed test.
- Where a stable runnable checkout is unavailable, finish source-based reasoning and list exact blocked commands, scenarios, and claim ceilings.
- Distinguish a confirmed implementation defect from a fatal product hypothesis failure.
- A finding cannot create its own repair authority: reconcile first, then select narrowly warranted repair work in a separate follow-on responsibility.

## Review dispositions

**Product:** KEEP GRAPH-FIRST / REFINE / INVESTIGATE HYBRID / RECONSIDER / NOT YET DECIDABLE.
**UX:** RETAIN / REFINE INTERACTION / REDESIGN WORKFLOW / NOT YET DECIDABLE.
**Architecture:** RETAIN / TARGETED SIMPLIFICATION / STRUCTURAL CHANGE WARRANTED / NOT YET DECIDABLE.
**Combined:** CONTINUE OPT-IN / REPAIR BLOCKING GAPS / RUN FOCUSED EVIDENCE / CONSIDER DEFAULT / RECONSIDER DIRECTION.

**Stop:** each material failure class has been challenged; new probes only repeat evidence; next decision would require unavailable runtime or human observation; or review no longer changes the next action.

**Promotion law:** documented != source-inspected != executed != human-beneficial != merged != release-qualified.
