# Phase H — Story Discovery Agent Semantic Dogfood Synthesis

## Status

**H5 synthesis and closure recommendation.**

This document synthesizes the already-frozen H2 producer evidence, H3 context-reduced evaluator evidence, and H4 bounded composition dogfood for Phase H issue #119.

Repository baseline at H5 start: `095f777d42332a45e485379b4c17c8ff3a2b1ed3`.

Evidence inputs:

- `docs/research/story-discovery-phase-h-agent-producer.md` — H2 producer-only evidence;
- `docs/research/story-discovery-phase-h-evaluator-packet.md` — H3 reduced evaluator input;
- `docs/research/story-discovery-phase-h-evaluator-findings.md` — H3 qualitative adjudication;
- `docs/research/story-discovery-phase-h-composition-dogfood.md` — H4 bounded composition evidence.

This is a **semantic plausibility** synthesis. It does not test live Anthropic/OpenAI production behavior, human-writer preference, experienced-writer usefulness, cross-provider reliability, or live F5 composition quality.

No aggregate numeric score, pseudo-success rate, or weighted leaderboard is used.

---

## Phase H question

Phase H was intentionally weakened from a live-provider quality gate to the following bounded question:

> On a small representative benchmark, does a separated coding-agent dogfood pass find Story Discovery's candidate search, causal analysis, recommendation, craft teaching, and bounded composition semantically coherent, plausibly useful, and internally defensible?

The evidence is sufficient to answer **yes, with important limits**.

The useful result is not that every recommendation was uniquely correct. The useful result is that the Story Discovery contracts repeatedly supported concrete, causally different story directions, grounded discussion of their downstream craft consequences, and bounded composition under explicit author authority — while also exposing two specific product boundaries where the current semantics are too coarse.

---

# Evidence synthesis

## 1. Candidate search / causal distinctness

The strongest recurring result is that the candidate search concept is semantically plausible.

Across the six frozen briefs, the producer directions generally differed in the things that should matter if two interpretations are actually different stories:

- protagonist recurring verbs;
- causal ownership;
- pressure systems;
- reversal sources;
- scene families;
- decisive climax mechanics;
- reader-experience emphasis.

The H3 reduced evaluator did not encounter a benchmark case where the candidate set collapsed into mere rhetorical variants or became impossible to adjudicate because all candidates expressed the same causal engine.

This supports the existing F3 design choice that **causal architecture, not titles, prose density, provenance, or confidence, is the relevant comparison layer**.

It does not establish that every future provider/model will generate equally distinct candidates.

## 2. Causal profiles

The derived causal-profile concept is useful enough to retain.

Profiles consistently made implicit story commitments inspectable: what the protagonist repeatedly does, who owns the causal contest, what creates pressure, where reversals come from, and what kind of climax the premise implies under a given engine.

The recurring calibration risk is **beat invention**. Some profiles moved from describing an engine into supplying a concrete illustrative reversal that the candidate itself did not strictly entail.

That risk did not make the benchmark unusable, but future prompting/contract work should keep a clearer distinction between:

- mechanics implied by the candidate;
- illustrative/hypothetical downstream beats;
- unresolved evidence gaps.

This is retained as known semantic debt, not elevated to a Phase H blocking defect.

## 3. Comparative recommendation

Recommendation was **plausible but not uniquely reliable**.

Where a brief strongly privileged one governing engine, H2 and H3 generally converged. Where two directions satisfied the declared brief through different legitimate artistic pleasures or scales, the H3 evaluator sometimes preferred a different direction while still finding H2's recommendation defensible.

The important failure mode is therefore not arbitrary recommendation. It is **false decisiveness at the margin**.

Two recurring patterns exposed it:

- treating one flavor of claustrophobic reconstruction as more aligned even though the brief also strongly supported elevator-specific sensor mechanics;
- treating broader collective/institutional responsibility as a stronger fit when the brief did not declare breadth or scale as a preference over intimate relational responsibility.

The current production recommendation prompt explicitly tells the judge to "Choose one advisory winner" and supplies a default priority stack. That is useful for convergence, but it can encourage the judge to convert an undeclared taste preference into an apparently objective stronger-fit claim.

The semantic distinction Phase H supports is:

> **Explicit author preference or hard contract evidence may justify a stronger-fit claim.**
>
> **When multiple candidates are comparably compatible with the declared brief, Auteur should label the choice as an advisory artistic preference and expose the tradeoff rather than manufacture certainty.**

This is a concrete product-contract follow-up, not a reason to invalidate Story Discovery recommendation as a whole.

## 4. F4 craft teaching

F4 craft teaching was one of the strongest semantic surfaces in the benchmark.

The evidence repeatedly connected high-level narrative choices to downstream craft consequences:

- causal strategy and ownership;
- protagonist action patterns;
- scene-family changes;
- pressure and texture;
- reader experience;
- thematic consequences;
- gains and sacrifices;
- composition boundaries.

The strongest F4 notes did more than say an alternative was "compatible." They stated **how much of the alternative could be borrowed and what would cause displacement**.

This is valuable because it converts abstract story preference into actionable writing guidance.

The main caution is asymmetry: after one candidate becomes the advisory primary, explaining every alternative relative to that primary can make the chosen hierarchy feel more inevitable than the original author brief actually warrants. Recommendation calibration therefore matters upstream of craft teaching.

## 5. Bounded composition

H4 supports the semantic plausibility of bounded composition, with a newly identified hierarchy boundary.

The most stable compositions gave every borrowed mechanism:

1. a **bounded job** it was allowed to perform; and
2. a **forbidden ownership** it was not allowed to seize.

Examples included:

- institutional suppression may obstruct evidence access but may not own moral responsibility or the climax;
- witness concealment may corrupt reconstruction inputs but may not solve the murder through confession;
- truthful exhibition may deliver proven provenance but may not substitute for proving provenance;
- genealogy may supply buried historical harm but may not become the supernatural rule explaining every disappearing room.

This is more operational than a generic instruction to "keep the primary primary."

The H4 evidence also exposed an important distinction that the current production hierarchy assessor does not explicitly model:

> **Causal-primary preservation is necessary but not always sufficient.**

A borrowed mechanism can remain formally subordinate in causal ownership and still become the story's **reader-experience or emotional primary**.

The hidden-attempt-to-atone and repeated-goodbye examples are the clearest cases: the primary can still own the external objective and climax while the secondary attracts most dread, grief, compassion, anticipation, or thematic attention.

The current F5 hierarchy prompt primarily evaluates action patterns, recurring pressure, reversals, and the climax. Phase H therefore identifies a concrete follow-up boundary: composition hierarchy should explicitly reason about both **causal ownership** and **experiential/emotional ownership**, or otherwise fail closed when those layers diverge materially.

This does not establish a live F5 defect because H4 did not execute live F5 provider behavior. It establishes that the existing semantic model is incomplete at this boundary.

## 6. Author authority

The explicit authority boundary remained intact throughout H2–H4.

No dogfood action accepted a `StoryIdentity`, candidate labels/order/provenance were not treated as creative-quality signals, and recommendation/composition remained advisory.

This supports the narrow claim that the Story Discovery semantic design can preserve explicit author authority under the tested research procedure.

It does **not** establish how human writers subjectively experience that authority surface. A recommendation can remain noncanonical in the data model while still feeling overly authoritative to a user; that question requires human-writer evidence.

---

# Recurring risks and defects

## Product-contract follow-up A — recommendation calibration

**Observed boundary:** close artistic calls can be presented as stronger brief fit even when the decisive preference is undeclared.

Current production surface: `src/auteur/story_discovery_recommend.py`.

The existing prompt correctly rejects contract-fit/provenance/confidence as artistic quality signals and preserves explicit constraints, but it also requires one advisory winner. The follow-up should preserve convergence while distinguishing at least:

- preference grounded in explicit declared author intent / hard constraints;
- advisory artistic preference among multiple comparably brief-compatible engines;
- genuinely non-adjudicable cases if evidence is insufficient.

A solution should not introduce numeric scoring or make the judge less useful merely to avoid committing.

## Product-contract follow-up B — composition hierarchy

**Observed boundary:** a secondary can preserve the primary's external causal ownership while becoming the story's emotional/experiential center.

Current production surface: `src/auteur/story_discovery_compose.py`.

The existing hierarchy assessor is deliberately causal and checks major action patterns, recurring pressure, reversals, and climax ownership. The follow-up should preserve those hard causal checks while also making reader-experience/emotional displacement inspectable.

The H4 "job + forbidden ownership" formulation is a promising operational guardrail and should be tested against production composition semantics.

## Known debt not opened as a separate blocker — causal-profile specificity

Causal-profile generation sometimes states illustrative reversal beats more concretely than the candidate commitments warrant.

This should be addressed opportunistically in prompting/contract refinement by labeling illustrative examples or pushing unsupported specifics into evidence gaps. Phase H did not find this severe enough to justify its own blocking follow-up issue.

---

# Evidence limitations

Phase H deliberately stops well below production-quality or human-validation claims.

The following remain untested:

- production Anthropic Story Discovery quality;
- production OpenAI Story Discovery quality;
- cross-provider consistency;
- provider/model prompt reliability over time;
- live F5 semantic quality;
- automatic hierarchy-classifier reliability under real provider outputs;
- experienced-writer creative persuasiveness;
- human-writer usability or preference;
- population-level usefulness;
- independence equivalent to a separate human evaluator.

H2 and H3 used the same model family. The frozen/reduced evaluator packet removed major producer cues and forced recommendation reveal after the initial choice, but the procedure cannot prove memory isolation equivalent to a separate model or human reviewer.

These limitations are claim ceilings, not reasons to keep Phase H open indefinitely.

---

# Is a later live-provider or human-writer phase worth the cost?

**Not required immediately for the current engineering boundary.**

Phase H answered the cheaper question it was revised to answer: the semantic contracts are coherent enough to justify continued use and targeted refinement rather than broad redesign.

A later evidence phase becomes worthwhile when one of these decisions depends on it:

- choosing or comparing production providers/models for Story Discovery;
- claiming creative-quality reliability rather than semantic plausibility;
- deciding whether recommendation calibration works across unconstrained real outputs;
- deciding whether writers actually find the recommendation/craft surfaces useful and appropriately advisory;
- validating whether the extended composition hierarchy model predicts human perception of what the story is "really about."

Until such a product decision is pending, live-provider/human evaluation would create stronger evidence but would not currently unlock a clearly necessary implementation decision.

---

# Closure decision

**Close Phase H as completed.**

The semantic-plausibility uncertainty has been reduced enough to move forward without pretending the system is creatively validated in production.

The evidence supports continuing with the current Story Discovery architecture rather than reopening candidate search, F3, F4, authority semantics, or composition from first principles.

Two narrow product-contract debts should move to follow-up issues rather than keeping the umbrella phase open:

1. calibrate recommendation language/decision basis for close artistic calls;
2. extend composition hierarchy reasoning beyond causal ownership to include experiential/emotional displacement and explicit secondary ownership boundaries.

---

# Final supported Phase H claim

The strongest claim supported by the actual evidence is:

> **On six representative frozen briefs, a separated coding-agent producer/evaluator dogfood pass found the Story Discovery candidate, causal-profile, craft, and bounded-composition contracts capable of expressing materially different and generally useful intent-aware narrative directions while preserving explicit author authority. Comparative recommendations were plausible rather than uniquely reliable at close artistic margins, and bounded composition exposed a remaining need to distinguish causal-primary preservation from emotional/reader-experience displacement.**

This is intentionally weaker and more precise than claiming provider quality, writer validation, or uniquely correct recommendations.

# Claims Phase H must not be cited to support

Phase H does **not** establish:

- that Anthropic or OpenAI production outputs meet a creative-quality bar;
- that one provider/model is better than another;
- that the recommendation is objectively or uniquely correct;
- that human writers prefer or trust the outputs;
- that live F5 will always preserve hierarchy;
- that six cases imply a population success rate;
- that same-model context reduction equals independent human adjudication.

# H5 boundary

H5 is synthesis/closure only. It does not implement either follow-up product change, execute live providers, or create/accept canonical StoryIdentity state.
