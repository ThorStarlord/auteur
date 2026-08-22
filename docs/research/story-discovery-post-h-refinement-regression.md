# Story Discovery post-H refinement regression

## Status

**Integrated post-H regression evidence. This is not Phase I research.**

Repository revision under regression: `00754a781339f27512fa1a85e781389cd933227e`.

This pass evaluates whether the two product defects isolated by Phase H were converted into usable production contracts without reopening the already-qualified Story Discovery architecture:

1. close-call recommendations must distinguish declared-intent fit from Auteur's own advisory artistic preference and may decline false certainty;
2. composition must preserve both causal ownership and reader-experience ownership, with every borrow bounded by a subordinate job and forbidden ownership.

The pass reuses the frozen six-case Phase H corpus and its already-committed H2/H3/H4 evidence. It does **not** execute live Anthropic/OpenAI providers, recruit human writers, create a numeric quality score, or mutate canonical `story_identity.yaml` state.

Evidence inputs:

- `docs/research/story-discovery-phase-h-cases.yaml`;
- `docs/research/story-discovery-phase-h-agent-producer.md`;
- `docs/research/story-discovery-phase-h-evaluator-findings.md`;
- `docs/research/story-discovery-phase-h-composition-dogfood.md`;
- `docs/research/story-discovery-phase-h-synthesis.md`;
- production contracts and regression tests at the exact revision above.

The fixed question is:

> Did #125 and #126 remove the two failure modes that justified them, while preserving causally distinct search, useful craft comparison, candidate-only composition, and explicit author authority?

---

# Contract state after hardening

## Recommendation

A qualified causal set no longer implies that Auteur must present one candidate as objectively better aligned with author intent.

The production contract now distinguishes:

- `explicit_intent_fit` — a declared author commitment actually distinguishes the alternatives;
- `advisory_artistic_preference` — multiple directions satisfy the brief, but Auteur has a defensible craft preference that is not an additional author requirement;
- `not_adjudicable` — even a bounded craft preference would require inventing an unstated criterion.

The persisted state and review surface distinguish those outcomes. A comparative `not_adjudicable` result does not invalidate already-qualified candidates, and no automatic primary-relative F4/F5 path is created when there is no recommendation.

## Composition

New composition reports are schema v2 and contain independent causal and experiential hierarchy assessments. Aggregate classification is derived deterministically in code:

- either dimension `primary_displaced` -> overall `primary_displaced`;
- otherwise either dimension `uncertain` -> overall `uncertain`;
- otherwise -> `primary_preserved`.

A composed candidate is emitted only when **both** dimensions are `primary_preserved`.

Every v2 borrow also carries a deterministic subordinate `job` and `forbidden_ownership` boundary covering the governing external objective, decisive reversal chain, climax, and governing reader-experience promise. The writer still names only what they want to borrow; Auteur handles the hierarchy machinery internally.

Legacy v1 composition reports remain readable.

---

# Six-case controlled regression

## H01 — Dead Channel

### Recommendation

The original preference for the personal mission reconstruction remains a clear **explicit-intent** case.

The declared primary promise is `haunted self-reckoning under impossible evidence`. The personal reconstruction direction makes the impossible chatter directly pressure the protagonist's self-account and consequential past choice. The rescue direction makes saving another person the governing objective; the institutional direction makes exposure of organized wrongdoing the governing contest.

**Post-hardening basis:** `explicit_intent_fit` is proportionate here because the declared reader-experience promise materially distinguishes the engines.

The refinement does not make a previously clear case artificially hesitant.

### Composition

The H4 borrow—mission leadership suppressing records—has a bounded job: obstruct and contextualize evidence access while the protagonist reconstructs her own choice.

- causal ownership: preserved if reconstruction of her choice still owns decisive reversals and climax;
- experiential ownership: preserved if haunted self-reckoning remains the emotional center rather than conspiracy exposure;
- forbidden ownership: the institutional layer may not become the governing objective, moral answer, decisive reversal chain, or climax.

This remains a clean positive control under the dual hierarchy contract.

### Authority

Recommendation and composition remain advisory. Nothing in the refined path changes canon before explicit acceptance.

---

## H02 — Between Floors

### Recommendation

This remains the clearest close-call calibration case.

The frozen H2 producer preferred **Hidden Seconds**, while the context-reduced H3 evaluator preferred **Weight of an Alibi**. H3 found both strongly compatible with the declared elevator-mystery brief and identified the difference as a choice between two legitimate governing pleasures:

- bodily/timing reconstruction of hidden seconds;
- elevator-specific sensor/choreography reconstruction where truthful machine readings support a false inference.

The brief requires sealed-space mechanics to matter, but it does not declare that shared subjective impossibility should outrank elevator-specific machine mechanics.

**Post-hardening basis:** a preference for either direction may be returned as `advisory_artistic_preference`; it should not be labeled `explicit_intent_fit` unless additional declared intent actually distinguishes those pleasures. `not_adjudicable` remains available if the judge cannot state a craft preference without adding a new criterion.

This directly removes the Phase H defect: the system can still be opinionated without converting its taste into a fabricated author requirement.

### Composition

H4 borrowed independent witness concealment under the hidden-seconds primary. Its job is to obscure observations required for the physical reconstruction.

- causal ownership: preserved only if the physically demonstrable reconstruction still identifies the killer;
- experiential ownership: preserved only if reconstructive relief from the sealed-space puzzle remains governing while dread/moral uncertainty remain supporting palette;
- forbidden ownership: confession, motive revelation, or social decomposition may not solve the physical sequence or become the practical center of anticipation.

The post-H composition contract makes the second condition inspectable rather than relying on a generic hierarchy warning.

### Authority

The H2/H3 disagreement remains a legitimate artistic choice. Successful subordination of a secondary does not retroactively prove that the frozen H2 primary was objectively better.

---

## H03 — Nothing Missing

### Recommendation

The provenance-authentication direction remains a clear positive control. It uniquely couples disputed museum objects, truthful action, active coordination, and institutional resistance into one museum-specific objective. The alternatives produce different dominant procedural pleasures.

**Post-hardening basis:** `explicit_intent_fit` remains defensible where the declared museum/object constraints actually distinguish provenance ownership from a more replaceable bureaucracy or dramaturgy engine.

### Composition

The truthful-exhibition borrow has a narrow delivery job: make already-established provenance evidence publicly legible under hostile oversight.

- causal ownership: provenance authentication still owns the evidentiary burden and success condition;
- experiential ownership: the pleasure should remain coordinated proof/authentication rather than a word-game or audience-manipulation puzzle;
- forbidden ownership: truthful dramaturgy cannot create the proof or independently defeat the director.

This remains a clean dual-hierarchy positive control.

---

## H04 — The Missing Room

### Recommendation

The present-tense family-avoidance/compression engine remains a clear fit because the declared target experience explicitly says physical compression forces avoided family truths into the open.

**Post-hardening basis:** `explicit_intent_fit` remains proportionate. The recommendation does not need to weaken merely because other directions are viable stories.

### Composition

The erased-relative/inheritance layer has the job of supplying historical content and material stakes for one major avoidance pattern.

- causal ownership: present family behavior under physical compression must still govern the disappearing-room rule and climax;
- experiential ownership: present relational confrontation and loss of avoidance space must remain what the horror emotionally organizes around;
- forbidden ownership: genealogy may not become a master puzzle, universal supernatural explanation, or independent restitution win condition.

The dual hierarchy therefore preserves the useful H4 lesson while catching a version in which ancestry technically remains secondary but absorbs the reader's real attention.

---

## H05 — What She Saves

### Recommendation

The protagonist-owned repair direction remains strongly supported by the hard constraint that her external goal resolves through **her own consequential choices**. H3's concern was not that the recommendation selected the wrong engine; it was that the brother's reader-known guilt could become too passive if the primary were kept too pure.

**Post-hardening basis:** the protagonist-owned direction can still be an `explicit_intent_fit` recommendation because the hard agency constraint distinguishes it from a version where covert help owns indispensable success conditions.

### Composition

This is the first decisive dual-hierarchy regression.

H4 proposed borrowing the brother's covert atonement as non-decisive mitigation. The frozen evidence already separated two judgments:

- **causally:** the borrow can remain subordinate if the protagonist retains the plan, indispensable choices, key insight/resources, and final action;
- **experientially:** the brother can nevertheless become emotionally magnetic because the reader knows his responsibility and repeatedly watches his attempts to atone.

Under the old causal-only model, a composition could plausibly pass while suspense, compassion, and thematic attention migrated toward whether the brother confesses, is discovered, or redeems himself.

Under the post-H contract, that result cannot silently pass. The experiential assessor must independently establish that the protagonist's intended reader-experience center still governs. If the evidence is `uncertain`, the aggregate is `uncertain`; if the brother has become the emotional primary, the aggregate is `primary_displaced`. In either case no composed candidate is written.

The borrow boundary is also explicit:

- job: increase dramatic irony through bounded, non-decisive mitigation;
- forbidden ownership: protagonist objective, decisive reversal chain, climax, and governing reader-experience promise.

**Regression result:** the exact failure mode identified by H4 is now represented as a fail-closed production state rather than hidden inside prose risk.

---

## H06 — Fixed Point

### Recommendation

This remains the second decisive close-call calibration case.

H2 preferred a distributed public-witness/responsibility engine. H3 preferred the repeated intimate goodbye plus consequential present relationship choice. H3's objection was specific: the brief does not declare **breadth or collective scale** to be better than intimate relational responsibility.

Both can satisfy `grief transformed into consequential responsibility without undoing loss`.

**Post-hardening basis:** if Auteur prefers the collective direction because of its broader social architecture, that preference belongs under `advisory_artistic_preference`, not `explicit_intent_fit`. A preference for the intimate direction can likewise be advisory unless the author declares scale, public consequence, or relational intimacy as a priority.

The refinement therefore preserves Auteur's ability to recommend while preventing “broader” from silently becoming an invented author criterion.

### Composition

H4 borrowed one repeated goodbye/key-witness relationship under the distributed witness primary.

Causal subordination is possible if the broader witness chain remains necessary for the present action. But the borrowed mechanism is emotionally complete enough to become the story the reader actually experiences as primary.

The new contract must separately ask:

- does the wider witness mission still own the decisive present action and causal reversals?
- does grief-to-responsibility still organize around the distributed witness promise, or have the repeated goodbye and one relationship become the audience's practical emotional center?

If most anticipation/reversals attach to the intimate relationship, or the final present choice becomes primarily about that relationship, experiential displacement is no longer a soft warning. It rejects composition unless the author first changes the intended primary.

**Regression result:** the H4 divergence between formal plot hierarchy and experienced story hierarchy is now a first-class production distinction.

### Authority

The fact that Candidate B can be a compatible borrow under Candidate A does not settle the H3 primary-choice dispute. Composition cannot be used to smuggle an undeclared primary preference back into the recommendation layer.

---

# Cross-case findings

## Recommendation basis survives the difficult cases

The six-case corpus still contains both kinds of recommendation the product needs:

- clear declared-intent/hard-constraint cases such as H01, H03, H04, and H05;
- genuine artistic margins such as H02 and H06 where the deciding value is not fully declared.

The new contract can express those differences without forcing every good candidate set into one epistemic category. Close calls remain actionable because `advisory_artistic_preference` preserves Auteur's opinionated role; they are simply labeled honestly.

## Experiential hierarchy closes the composition gap

H01-H04 remain useful clean controls: their borrowed layers have obvious subordinate jobs and can preserve both plot and intended experience.

H05 and H06 are the important adversarial controls. They show why causal ownership alone was insufficient. The v2 contract cannot call a composition fully preserved unless both causal and experiential assessments independently preserve the primary, and aggregate classification is not delegated to model discretion.

## Job + forbidden ownership remains operational

The H4 formulation survives hardening well because it turns “keep the primary primary” into a concrete boundary:

- what useful work the borrow is allowed to do;
- which governing functions it may not seize.

The writer does not need to supply this ontology manually. Guided composition still asks for the mechanism in ordinary language and production attaches/enforces the boundary internally.

## Existing positive paths remain intact

The refinements do not reopen candidate search, F3 causal qualification, or F4 craft comparison. Single/zero-survivor semantics remain outside the recommendation-basis change, legacy persisted recommendation/composition evidence remains readable under explicit compatibility rules, and composition remains candidate-only until explicit acceptance.

## Author authority remains intact

Across recommendation, non-adjudicability, review, guided composition, and direct composition:

- no recommendation is canonical by itself;
- comparative non-adjudicability does not manufacture a primary;
- no F4/F5 path runs automatically without a selected recommendation;
- no composition report creates `story_identity.yaml`;
- `story-discovery accept` remains the explicit authority-bearing transition.

The refinement therefore improves semantic honesty without increasing automation authority.

---

# Conditional causal-profile specificity check

Phase H did not find causal-profile specificity to be a blocker, but H3 describes it as a **recurring** calibration risk rather than a single isolated example. Profiles sometimes move from an implied class of reversal to a particular illustrative reversal event more specifically than the candidate evidence warrants.

Examples in the frozen findings include reversal details in Dead Channel and The Missing Room that are consistent with the engine but more specific than the core answer strictly entails.

This does **not** invalidate the post-H refinement campaign: no reviewed case changed governing causal ownership because of the extra specificity, and H3/H5 explicitly treated it as known debt rather than a producer-contract failure.

Because the pattern is repeated, it should be tracked separately and narrowly rather than silently expanded into this campaign. The follow-up rule is:

> Causal profiles describe mechanically implied classes of action/reversal. Candidate-specific events not supported by evidence must be labeled hypothetical or placed in `evidence_gaps`.

No implementation of that debt is included in this regression slice.

---

# Defects found by this regression

No new consequential Story Discovery boundary was found in the frozen corpus beyond the already-known causal-profile specificity debt above.

The regression does not justify a new recommendation ontology, automatic author-preference inference, automatic acceptance, a new primary-selection workflow, or another composition feature family.

---

# Supported post-hardening claim

The strongest claim supported by this regression is:

> **Against the existing six-case Phase H evidence, the post-H Story Discovery contracts can distinguish recommendations grounded in declared author intent from Auteur's own advisory craft preferences, can decline fabricated certainty, and can reject secondary composition when either causal ownership or reader-experience ownership displaces the intended primary. The writer-facing path preserves explicit author acceptance as the only canonical transition.**

This is a contract/regression claim. It is not a population-level creative-quality claim.

---

# Unsupported claims

This regression does **not** establish:

- that live Anthropic or OpenAI outputs reliably obey the refined contracts;
- that one provider/model is superior;
- that recommendations are objectively or uniquely correct;
- that human writers prefer, understand, or trust the refined wording;
- that the experiential classifier matches human perception in all stories;
- that six frozen cases imply a success rate;
- that provider/model behavior will remain stable over time;
- that the known causal-profile specificity debt is solved.

Those remain future evidence questions only when a product decision actually depends on them.

---

# Regression decision

**The two Phase H follow-up defects are sufficiently hardened for this refinement campaign to close, subject to final repository qualification of this evidence revision.**

Recommendation calibration no longer needs another umbrella research cycle. Composition now treats causal and reader-experience hierarchy as independent preservation obligations and exposes the boundary to writers without making them manage internal ownership terminology.

The remaining causal-profile specificity issue is narrow debt and should not hold this campaign open.

If final repository qualification passes on the exact evidence head and no base/review drift appears, the appropriate campaign record is:

> **Story Discovery post-H refinement is complete. Further development is demand-driven rather than campaign-driven.**
