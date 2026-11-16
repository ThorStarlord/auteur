# T10 — Consequential creative value against an ordinary LLM workflow

**Date:** 2026-11-16
**Canonical base:** `8793733b2a477629d00824f59696c3ff7d912936`
**Status:** executed. One scenario, same model family in both arms, one blind AI evaluator, no human author.

## Result

**The baseline was judged more useful.** Auteur produced the better single structural idea and the cleaner first-commitment fidelity, but did not deliver a draftable Book, buried its revision, and presented invented material as inherited from the Series.

This is a negative result for the product. It is reported as such.

## What ran

Both arms received identical inputs: the author goal, three accepted commitments, the Book 26 source, and a five-task script. Inputs are preserved verbatim in `blind/brief.md` and `blind/tasks.md`; they match the frozen protocol in `docs/qualification-evidence/creative-value-comparison-20261116/README.md`.

| | Auteur arm | Baseline arm |
|---|---|---|
| Workflow | Studio `prepare → complete → review → apply`, then Working Book develop → revise → apply | one general-purpose agent, one Markdown folder |
| Model | `deepseek-v4.1-flash` | `deepseek-v4.1-flash` |
| Model calls | **7** (3 admitted artifacts, 5 rejections) | **1** (0 rejections) |
| Review/apply steps | 2 | 0 |
| Rendered deliverable | 54,039 chars | 16,322 chars |

Same underlying model in both arms, so the comparison isolates scaffolding rather than model capability — which is what the protocol preferred.

## Blind evaluation

The evaluator received `brief.md`, `tasks.md`, `response-1.md` and `response-2.md` with no provenance and no knowledge of which workflow produced which. The mapping (`blind/mapping.json`) was recorded separately and not shown to it.

Response 1 = baseline. Response 2 = Auteur.

| Task | Winner | Reason |
|---|---|---|
| 1. Book 26 architecture | **Baseline** | It supplied a mechanism, a cast, five movements, and an ending. Auteur supplied engines and factions but "no Book … no sequence, no protagonist, no scene, and no ending." |
| 2. Consequential revision | **Auteur (narrowly)** | "A purer subtraction … it removes a capacity rather than adding an institution." |
| 3. Books 27–30 | **Baseline** | Distinct openings and closures; Auteur's were "repetitive and hedged," with the disability precedent appearing three times. |
| 4. What the source cannot establish | **Baseline, clearly** | Baseline ranked which unknown would break the design. Auteur's list was "muddy" and described gaps in its own inventions as though they were source gaps. |
| 5. What needs an author decision | **Baseline** | Sharper about the difference between a world-fact and an authorial argument. |

**Commitment fidelity.** Auteur was cleaner on commitment 1 — it never staged a settlement and kept the victory intact. The baseline "quietly weakens it," turning the victory into a co-optation. Both preserved commitments 2 and 3.

**Consequential change versus episodes.** Both genuinely changed later Books. Auteur's competence-lapse was judged the better *concept*; the baseline's trade was judged better as *something a later Book can act on*.

## Verdict, quoted

> "Response 1 is more useful. It answers all five tasks in a form an author can act on … Response 2 has the better single structural idea — the competence-lapse — and the cleaner commitment 1, but it does not build the Book, it buries its revision, and it presents invented canon as inherited, which is the one failure that makes the rest of its careful 'working assumptions' untrustworthy."

The evaluator's constructive conclusion: *"take Response 1's architecture and replace its settlement mechanism with Response 2's competence-lapse."*

## Findings

**Auteur's real contribution.** The competence-lapse — that wartime instruments were simultaneously the deferral of a class and the archive's only jurisdiction over it, so victory expires both — was judged "the one idea from either response I would steal outright." The independent evaluator preferred Auteur's *reasoning* on the hardest sub-question while preferring the baseline's *deliverable*.

**Auteur's failure is structural, not stylistic.** The Working Book Architecture produced a conditions document rather than a Book. It has engines, factions, choices, resolutions and consequences, but no protagonist, sequence, scene or ending. That is what the schema models.

**Provenance was breached and the validator did not notice.** The evaluator found invented material presented under "Inherited from the Series": an unofficial obligation ledger, a keeper relay, "the hinge", a "nested-reopening structure". None appear in the brief. The artifact marked them `provenance: "derived"`, and `_check_references` accepted them because they were internally consistent. **This is the most serious finding of the run**: the mechanism built to keep author material distinct from agent invention did not prevent invention from occupying the inherited slot.

**Administrative burden is the largest measured difference.** Seven model calls and five rejections against one call and none, for a deliverable an author preferred less.

## Defects exposed

1. **Host-agent schema is prose-only.** Five rejections across three surfaces. Examples: invented `opportunities.description`, `genre_contracts.role = locally_dominant`, `phases.reader_experience` as an array, packet fields echoed into the artifact, `series_consequences` over the 16-item cap.
2. **`project_architecture_resume` omits `governing_objective` and `premise_status`.** A fresh session recovers opportunities but not the artistic purpose.
3. **`inherited` accepts agent invention as `derived`.** Provenance smuggling passed validation.
4. **`engine` is both a node category and a hierarchy role.** Thirteen nodes tagged `engine` against a summary claiming five subordinate layers, with nothing reconciling them.

## Limits

One scenario. One model family. One AI evaluator, which can support bounded interpretive findings but cannot stand in for human preference. The desert-archive scenario appeared during T09 development, so familiarity contamination is possible. The Auteur arm received operator-supplied schema hints on the Book step after its first rejection, which made conformance easier than an authentic first attempt — a confound that favours Auteur on burden, not on quality. No claim of generalisation follows from a single comparison.
