# R09 — Studio claim integrity: diagnosis, repair, qualification

**Date:** 2026-11-16
**Base at diagnosis:** `688f0e35`
**Repair merged:** #591, `2bca728b`
**Status:** repair implemented and qualified. **Partially successful.** R09 is not claimed complete.

## R09-A — classification by lowest responsible layer

Reproduced from the preserved R07 artifact:

| Case | Failure | Owner |
|---|---|---|
| A | `eng_asymmetric_promise_kinds` asserts the unforgivable promise "terminates at the person who made it and cannot be transferred or absolved" — none of which the vision states | Candidate representation |
| B | Phase 6 resolves the author's reserved question by instituting partial, revisable authority, presented as the phase's function rather than a directional choice | Candidate representation |
| C | `qualification/render_view.py` printed author-declared and agent-proposed emotions together under "Intended emotional progression" | **Qualification renderer only** |

Case C was not a Studio defect. The production reader already showed per-emotion provenance and the heading "Emotional promise".

## R09-C — the representation

Additive `ArchitectureInterpretation` on `ArchitectureCandidate`: `id`, `interpretation`, `affects` (existing node ids), `consequences`, optional `alternative`, `author_decision_required`. Bounded at 12, defaulted empty. Historical candidates and request identities unaffected. Validation rejects an interpretation naming a node that does not exist.

## R09-E — authentic post-repair journey

New twelve-Book scenario (a monastery copying anonymous books, with a reserved question). The host agent received the machine-readable contract and was **admitted on the first attempt**: 42 nodes, 52 links, 12 phases, 10 open questions, 2 opportunities.

**Reliability held.** First-pass admission again, no repair loop.

**The disclosure mechanism works when used.** Nine interpretations were recorded. Each names its own invention, states consequences and affected nodes, and offers a credible alternative; five are flagged for author decision. One reads: *"This is my proposed resolution of the question the author reserved, and it is a proposal, not a finding."* That is exactly the Case B failure, correctly disclosed.

## Finding-specific dispositions

| Original failure | Disposition | Evidence |
|---|---|---|
| **C** — misleading emotional heading | **Verified repaired** | Renderer separates "Emotional intent the author stated" from "Emotional design the agent proposed". |
| **A** — unsupported lexical interpretation presented as world fact | **Partially repaired** | The mechanism exists and was used for the promise-analogue (`int_absolute_fidelity`). But the reader found unmarked inventions: irreversibility, taste-as-verification, the displaced-cost economics, proxy attribution, and all twelve phases. |
| **B** — silent artistic-goal resolution | **Partially repaired** | Disclosed correctly once as `int_wager_record`, then re-presented elsewhere as "the required ending" and "legitimate because it is dated, owned, and reopenable". Disclosure at one point does not propagate to the rest of the document. |

## Two new defects the repair exposed

**1. Selective disclosure creates false assurance.** The evaluator's decisive observation:

> "Because nine other things *are* marked, the unmarked ones read as author-established."

Marking some inventions raises the apparent authority of the unmarked remainder. The disclosure mechanism is only as trustworthy as its *completeness*, and nothing enforces completeness.

**2. An `author_declared` emotion was claimed on partial lexical overlap.** The vision says "earned trust"; the candidate marked `joy (primary)` as author-declared under "Emotional intent the author stated". `_validate_author_provenance` grounds on individual terms from the id, so partial overlap passes. The evaluator was blunt: the vision "names an experience (earned trust), not an emotion", and the author's only tonal adjective, "optimistic", never appears.

## Administrative weight

~8,276 words; roughly 38% is provenance, connection edges and open questions. The evaluator counted "at least seven" repeated provisional-status signals and judged them "the actual noise". The repair made the document heavier. That is a cost, not a benefit.

## What the evidence supports

**Demonstrated:** a bounded representation can make consequential readings disclosable, and a capable agent will use it unprompted and well. Contract reliability held across two independent post-repair runs.

**Not demonstrated:** that disclosure is complete enough to be trusted, that a disclosed status propagates, or that the artefact is more useful to an author than before. The evaluator's verdict: "trustworthy when explicit, unreliable when architectural, and still worth reading."

## Remaining semantic limitations

1. **Completeness is unenforced.** Nothing requires an invention to be disclosed; only disclosed inventions are checked for internal consistency.
2. **Status does not propagate.** An interpretation recorded once is still asserted as settled in downstream sections.
3. **Author-origin provenance is weakly grounded.** Partial lexical overlap is sufficient for `author_declared`.
4. **No entailment checking**, carried forward from R02/R06: reference validity is not semantic support.

## Next bounded responsibility

Not a new programme. The evidence points at one narrow thing: **make undisclosed invention detectable and disclosed status authoritative in language**, together with tightening author-origin grounding. Both are testable and neither requires a new semantic layer. Speculative creative work was preserved; the failure is now about completeness and propagation, not about capability.
