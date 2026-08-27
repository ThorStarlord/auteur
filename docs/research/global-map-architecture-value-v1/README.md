# Global Map Architecture Value V1 — README

**Experiment:** Does richer explicit narrative architecture materially improve long-horizon creative reasoning?

**Version:** `global-map-architecture-value-v1` — **FROZEN** on merge. Any material redesign requires V2.

**Source revision:** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge, `origin/main`).

**One-sentence thesis:** `Explicit Narrative Architecture → Global Map → relevance projection → Decision Map → Focus → author decision → accepted architecture/state` — but only if the architecture earns its complexity.

---

## Artifacts in this directory

| file | purpose | generator sees? | evaluator sees? |
|---|---|---|---|
| `source-manifest.md` | Frozen accepted sources, derived vs accepted distinction, provenance table | yes (via packets) | yes |
| `candidate-architecture-ledger.md` | Condition C golden ledger (33 items, 4 sections, Global Map projection) | **C only** | yes (after blinding) |
| `decision-probes.md` | 5 frozen probes P01–P05 (generator-visible: state, intent, question, options) | **yes** | yes |
| `condition-specification.md` | A/B/C packet specs, parity rule, extraction isolation, controls, repetition=3×3×5, blinding | yes (as packets) | no (hidden mapping) |
| `evaluation-rubric.md` | Global criteria (11), per-probe must-not-miss/forbidden, value definitions, concept trace, value/cost, invalidation, severe signals | **no** (hidden) | **yes** |
| `run-manifest-template.md` | Row template for 45 outputs + sealed mapping | n/a (filled at execution) | opaque IDs only |

Top-level `docs/research/global-map-architecture-value-experiment-v1.md` is the entry-point preregistration summary.

---

## How to run (without redesigning)

1. Checkout exact source revision `3cc4975...`.
2. Read `source-manifest.md` and `candidate-architecture-ledger.md`.
3. For each probe `P01`–`P05`, build 3 condition packets per `condition-specification.md` (A plain context, B real `select_repeated_continuity` via `repeated_map_focus.py` r1, C ledger slice).
4. Generate **3** independent outputs per condition per probe using same model/settings/prompt (45 outputs), fresh context each.
5. Export under opaque IDs per `run-manifest-template.md`; keep sealed mapping private.
6. Blind-evaluate with `evaluation-rubric.md` (per-probe must-not-miss/forbidden + global criteria, no single aggregate).
7. Unblind and do concept-level value trace; apply value/cost matrix; record invalidation/severe signals.

**No execution in this task** — protocol only.

---

## Quality check — 15 answers

1. **What is being tested?** Internal representational value: does golden explicit architecture (ledger) improve long-horizon decision quality over plain context and shipped Map/Focus.
2. **What falsifies richer-architecture hypothesis?** Consistently neutral or negative: C shows no must-not-miss advantage, or shows overconstraint/distraction/false precision outweighing gains across probes; severe negatives not averaged away.
3. **What does A receive?** Plain frozen story context + intent + question/options (same facts, no explicit dispositions/grouping).
4. **What does B receive?** Shipped `repeated-map-focus-v2-r1` derived Map (active/reactivated entries, rescinded superseded/irrelevant, groups, why-now) via neutral adapter + same prompt.
5. **What does C receive?** Same sources **plus** golden ledger → Global Map → Decision Map (relevance-selected) + same question.
6. **Does C have unfair facts?** No — information-parity rule: every ledger entry traces to frozen source; C gains *organization*, not new facts. Violation invalidates.
7. **Which statements are accepted vs derived?** Source-manifest + ledger `authority` column: `ACCEPTED` vs `DETERMINISTIC_DERIVATION` vs `INTERPRETIVE` vs `NON-AUTHORITATIVE` trigger.
8. **What exact questions?** 5 frozen questions in `decision-probes.md` (P01 fraud→memory, P02 retraction+ witness, P03 testimony without destroying chain, P04 burn variant, P05 grouping focus).
9. **How blinded?** Opaque IDs `X17/Q04`, sealed `hidden_condition_id`, evaluator never sees condition mapping or expected winner.
10. **How evaluated without arbitrary taste?** Must-not-miss / forbidden signals per probe; either option defensible if constraints respected; judge awareness of consequential relationships, not option choice (except P04 burn must be rejected).
11. **What counts as material value?** C uses source-backed relationship to produce better decision/explanation or prevent error that A/B miss (see rubric).
12. **What counts as harm?** False constraints, stale reasoning, unsupported certainty, irrelevant complexity, worse recommendation, authority confusion, rigidity (negative + severe signals).
13. **How is variance handled?** 3 independent generations per condition per probe (45); no single lucky response; deterministic-seed if available else recorded.
14. **Which concepts credited/blamed?** Per-ledger-item trace (available/surfaced/used/changed/improved/prevented/cost/redundant) → PROMISING/UNCLEAR/NEGATIVE per concept.
15. **What invalidates V1?** 9 conditions listed (extra facts, different questions, model changed, unblinding, edited outputs, B modified, unsupported ledger, settings drift, source changed mid-run) → record and require V2.

---

## Next step after merge

Execute frozen experiment without redesigning V1. Do not build production Global Map UI, schemas, or relevance engine until evidence shows architecture earns complexity.
