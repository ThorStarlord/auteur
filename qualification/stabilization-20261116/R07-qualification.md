# Post-repair qualification — R07

**Date:** 2026-11-16
**Base:** `41b37fa5` (R02/R05 in #588, R03/R04 in #589)
**Scenario:** held-out. A thirty-Book series about a court of translators rendering a treaty between two languages that cannot express the same obligations. Not the desert archive, not the fraudulent founder.
**Status:** executed. One model (`deepseek-v4.1-flash` via a fresh `opencode` general subagent), one independent AI reader, no human author.

## Reliability — the question this run was built to answer

| | Historical run (`b6c37e52`) | Post-repair (`41b37fa5`) |
|---|---|---|
| Model calls for one architecture | 7 | **1** |
| First-pass admission | no | **yes** |
| Rejections | 5 | **0** |
| Repair loops | 2 | **0** |
| Delivered contract | prose only | `output_contract` in the request, sha-bound |

The host agent received `system.txt`, `user.json` and `output_contract.json`. It produced 39 nodes, 43 links, 8 phases, 9 open questions and 2 opportunities, and the validator admitted it immediately.

**This measures contract usability, not creative intelligence.** The rejection count fell to zero on a scenario it had never seen, which is the specific claim the repair was designed to support.

## Boundaries

No `story_identity.yaml`, no `blueprint.yaml`. The candidate remains noncanonical.

## Independent evaluation — again mixed

A fresh reader received only the vision and a rendered view.

**Strong.** Purpose fidelity held "on the hardest point": both forbidden endings became structural constraints, and "the asymmetry cannot be dissolved by discovering a hidden equivalent". Two mechanisms were judged genuinely generative — *Obligation Drift* ("meaning therefore moves every time the text is used correctly") and *Glossarial Accumulation* ("an interpretation can be destroyed by being well documented").

**Weak, and familiar.**

- **Provenance slipped again, at a different layer.** Three invented meanings were presented in the register of settled fact: what "cannot be forgiven" means; the main thread's Change; and an "Intended emotional progression" section listing seven invented emotions as recovered intent.
- **Causal plurality was overstated.** "Five of six layers are stages of one claim's life; the sixth … has no causal edge to the engine, yet is counted among the six."
- **The horizon restates.** Phase 2 is deletable; Phase 7's only new idea gets a subordinate clause.
- **The same `engine` confusion returned**: "everything is a `(engine)` while being called a 'Layer', so seven engines include six layers, one of which is also a counterweight."

## What this changes

**The contract repair worked.** First-pass conformance went from 0/1 to 1/1 with no operator hints and no repair loop. That is the administrative-burden finding from the 2026-11-16 comparison addressed directly.

**The provenance repair did not transfer to the Studio layer.** R02 governs `inherited` claims in a Working Book artifact. A Studio `ArchitectureCandidate` has no inherited collection and only `emotion_targets` carries provenance, so the same failure class — invention presented as given — remains representable there. This is not an R02 regression; it is a boundary R02 never covered, now demonstrated by authentic execution rather than assumed.

## Limits

One scenario, one model, one AI reader, no human author. A single first-pass admission does not establish reliable conformance in general. The evaluator's provenance judgement is interpretive, not a validation result.
