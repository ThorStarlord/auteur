# VLS-01 — Very-Long-Series Architectural Judgment Pilot

**Date:** 2026-11-16
**Baseline:** `main@20a5737ee06e29dad82565596b29341cb7e354e7`
**Status:** Executed stages 0–3. Stage 4 (independent evaluation) **not executed**. Terminal disposition: **PARTIALLY QUALIFIED**.

## A representation finding before generation

The output contract caps `nodes` at **80**. A 100-Book horizon therefore cannot be represented as 100 Book nodes under any circumstance — the pilot's "macro periods plus six focal Books" shape is forced by the schema, not chosen for convenience. This is a real product representation limit and it belongs to the pilot's own distinction between *planning* a long horizon and *managing* accumulated history.

## Stage 0 — frozen inputs

Author brief: a hundred-Book series about a profession of witnesses who reconstruct unseen events from physical traces; testimony admissible only if the witness can be shown to have been wrong at least once. Three commitments, one intentional ambiguity ("shown to have been wrong"), one forbidden trivial resolution. Request `bdde76cf…`.

## Stage 1 — original architecture

Admitted **first-pass**, no repair loop.

| | |
|---|---|
| Structure | 51 nodes, 62 links, 5 macro phases, 4 open questions |
| Focal Books | `bk_01`, `bk_02`, `bk_24`, `bk_50`, `bk_76`, `bk_100` |
| Interpretations | 10, of which 4 flagged `author_decision_required` |

The distant dependency is real and specific: **Book 2** adopts a certification instrument whose first receipt becomes *permanently valid* — it cannot be re-opened without invalidating the instrument. **Book 76** turns on a claim admissible only through that unre-testable receipt. That is a dependency, not a callback.

The builder also challenged its own horizon and recorded the engine-organization choice as a consequential interpretation rather than as settled fact.

## Stage 2 — Book 24 counterfactual

Counterfactual chosen **after** the original was frozen, and deliberately load-bearing: Book 24 does *not* impose demonstrated defects on auditors; the profession grants a constitutional exemption that certification authority cannot itself be certified.

Result: 53 nodes; 2 nodes added, 16 changed, 4 of 5 macro phases rewritten. Selectivity is plausible at face value — neither inert nor wholesale.

**Evidence loss, recorded rather than concealed:** the review record from this step was consumed by the apply and not preserved separately. My completion script also misreported the apply as `null` because I assumed the Studio apply function returned `{"result": …}` like the Working Book one. The applied state was verified afterwards at 53 nodes / `ready`. The apply is real; the review artifact is missing.

## Stage 3 — fresh-context Book 76 decision

A genuinely fresh agent received only the frozen author brief and a rendered view of the revised architecture. It produced a 2,705-word decision brief.

It did the hardest thing the pilot asked for: it **contradicted the architecture**.

> "Book 76 as specified has no decision in it. The node pre-commits the outcome … That is a dilemma on paper and a non-choice in a story."

It then separated conduct from doctrine — "Doctrine is already settled by the constitution; conduct is not settled by anything, and conduct is what a Book can dramatize" — and restated the stakes more sharply than the architecture did: "Can the profession's authority survive being used?"

It identified the author's intentional ambiguity as arriving "at the top of the institution for the first time", distinguishing author commitment from agent proposal from its own reading.

## Stage 4 — not executed

No independent evaluation was commissioned. This is the pilot's **decisive** stage and its absence bounds every conclusion below. No claim about creative quality is made.

## Hypothesis dispositions

| Hypothesis | Disposition |
|---|---|
| H1 Renewable creative causality | **Inconclusive** — mechanisms are causally linked, but renewal across 100 Books was not tested |
| H2 Cross-horizon coordination | **Partially supported** — Book 2 → Book 76 dependency is genuine and load-bearing |
| H3 Consequential revision | **Partially supported** — revision changed state selectively; whether the changes were *justified* is unevaluated |
| H4 Context-independent reconstruction | **Supported within the pilot** — a fresh agent reconstructed the relevant context from the persisted architecture alone |
| H5 Decision usefulness | **Partially supported, with a negative finding** — the fresh agent produced a decisive, well-argued brief, and did so by identifying that the architecture had pre-committed its own decision |
| H6 Calibrated horizon judgment | **Not exercised** — no independent check of whether 100 Books was justified |

## What the evidence supports

A capable host agent can construct a causally differentiated long-horizon architecture with a genuine distant dependency, disclose its consequential inventions unprompted, and survive a major counterfactual revision selectively. A fresh agent can then recover enough to make a consequential later-Book recommendation — and can tell the difference between the author's commitments, the agent's proposals and its own reading.

## What it does not support

Nothing about **accumulated history over 100 realized Books**. This pilot planned a horizon; it did not maintain one. It also does not support any claim about creative quality, because the decisive evaluator never ran.

## Negative findings worth carrying forward

1. **The architecture pre-committed a decision it claimed to leave open.** A fresh reader caught it; the constructor did not. That is a creative-reasoning finding, not a provenance one.
2. **80-node cap forbids per-Book representation at this horizon.**
3. **Stage 2's review artifact was lost** to a reporting assumption of mine.

## Next warranted responsibility

Not a larger pilot. The one thing the evidence points at is **whether an architecture can keep a decision genuinely open**, since the pilot's decisive stage found the constructor closing a choice it had declared open. That is narrower than "more long-horizon capability" and it is testable without scale.

Stage 4 should be run before any of this is acted on.
