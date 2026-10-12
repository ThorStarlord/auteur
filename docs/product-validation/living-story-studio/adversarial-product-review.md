# Adversarial Product Review — Is Graph-First Worth Keeping?

**Frozen candidate:** \`bd2ba539d2f300941681fa7c7b80ab4765354b79\`
**Review method:** independent product-question pass over the cumulative Studio source and established Beginner product baseline; not a human study.
**Disposition:** **KEEP AS OPT-IN EXPLORATORY DIRECTION / DO NOT PROMOTE AS DEFAULT YET**. Comparative product value is not established.

## Decision under attack

Does a graph-first workspace create enough additional writing and relationship-reasoning value that it should displace the existing prose/decision-card Beginner Home?

The owner has explicitly prioritized **both spatial story creation and relationship visualization** and prefers the graph from session one. This is a legitimate direction for an exploratory candidate, not evidence that all future users will prefer it.

Do not evaluate only time-to-first-draft or only visual novelty.

## 1. What the candidate genuinely adds

- The Studio can open before a formal premise; the working canvas supports free notes, characters, scenes, places, questions, working connections, layout and export. See [Studio UI](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.html) and [working schema](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_store.py#L22-L85).
- A writer can open an expanded scene scratch editor; an explicit existing Quick Draft request preserves provisional premise and first-scene intent. The candidate does not silently accept these as canon ([Studio script](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L453-L537)).
- Relation and Story Lens inspection is intentionally derived from existing data, not from canvas edge drawing; impact and Book overview use separate read-only owner projections ([graph](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_projection.py), [impact](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_impact.py)).

These establish **capability presence in code**, not experienced value.

## 2. Strongest arguments against graph-first as default

### P-01: The promised *unity* is not yet realized (source-established product gap)

Working nodes/edges are maintained in \`state.items/state.connections\`; accepted/derived nodes and edges are kept separately in \`state.derived\`. The Browser renders different layers, but there is no integrated author-facing transition from a working idea/connection to its source-backed narrative counterpart ([rendering and projections](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L310-L442)). There is a guided Quick Draft handoff, not a demonstrated comprehensive acceptance roundtrip.

**Consequential assumption:** one spatial workspace makes source-backed narrative intelligence useful *during* creation, not merely available as an adjacent tab/view.

**Counterargument:** preserving separation is essential to avoid shadow canon; an opt-in first-stage prototype may deliberately postpone promotion. That is reasonable for a prototype, not enough for default-interface substitution.

**Next evidence:** S4/S5/S7 complete working idea -> draft discovery -> reviewed acceptance -> refreshed relationship/impact -> return to the same canvas focus. Require exact source binding, not a new canonical graph owner.

### P-02: The first-session default is still the existing prose/card Home (intentional boundary)

[Current index](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/index.html#L15-L56) presents a premise-first and two-input Quick Draft experience, with an opt-in Studio link. A source-authored prototype cannot establish that the graph is a successful replacement for this baseline.

**Counterargument:** opt-in is correctly reversible under evidence gates. Avoid treating this as a regression; it is a maturity limitation.

### P-03: Graph-as-admin-work is plausible, not demonstrated (product/UX hypothesis)

An author must choose note type (optional), possibly place nodes, draw or select working connections, inspect a separate evidence view, and supply an existing workspace ID to load Story Lenses. None of these actions necessarily yields useful prose.

**Hypothesis to falsify:** graphs help writers see novel relational or causal possibilities sufficiently often to repay visual manipulation and terminology overhead.

**Counterargument:** a spatially oriented writer may discover ideas by connecting notes that would not emerge in linear prose. Human comparison should preserve this benefit.

### P-04: There is significant duplication of navigational capability (trade-off)

The existing Home already supports a short Quick Draft path, discovery/reconciliation, story decision cards and Book orientation ([Beginner Home](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/index.html)). Studio also offers scene writing, derived story views, impact and Book orientation. Maintaining two UI paths can be a justified experimental cost, not necessarily a sustainable permanent architecture.

**Counterargument:** the Studio can become the eventual primary shell once value is earned; replacing the old path prematurely would be riskier.

### P-05: The strongest unique value is spatial exploration, not merely viewing source graphs (interpretation)

Character relationships and Book progress could be shown in a list, inspector, or timeline. The product needs to demonstrate more than displaying them in a node-link diagram. What is hard to replicate in prose is creating and reorganizing *possible* relationships and then seeing their story implications.

**Test:** Does arranging provisional characters/conflicts/questions reveal valuable story alternatives that a simpler contextual view does not?

## 3. Credible alternatives (no strawman)

| Candidate | Strongest merit | Lost value / cost | Decision relevance |
| --- | --- | --- | --- |
| A. Graph-first + large scene editor | Supports spatial ideation and relational exploration on one main surface | Visual overhead, multiple layers and canvas persistence complexity | Preferred experimental direction; default unsupported |
| B. Hybrid graph/manuscript dual workspace | Preserves spatial creativity without making prose navigation graph-dependent | Mode switching, divided mental model, layout complexity | Genuine rival; prototype only if real friction persists |
| C. Current prose/decision-card entry + contextual relation panel | Short direct writing path and existing guidance/acceptance continuity | Weak for free-form spatial idea generation and cross-connection discovery | Strong comparator, not automatically a substitute |

Do not score these with a single weighted number. Evaluate S1/S3/S5/S6/S8 for quality of ideas generated, ability to discover story consequences, admin effort, and confidence about what is established.

## 4. Opportunity-cost challenge

The active [F2/X3 Book mission #318](https://github.com/ThorStarlord/auteur/issues/318) and [Quick Draft host-agent dogfood #310](https://github.com/ThorStarlord/auteur/issues/310) can produce direct end-to-end author value. If Studio consumes disproportionate effort before those are qualified, it may delay user-relevant continuity. Do not use this argument to cancel spatial creation without comparing its benefits; it only raises the evidence threshold for default promotion.

## 5. Provisional verdict and falsifiers

**Verdict:** The rationale for **continuing opt-in graph-first exploration** is warranted because spatial creation is a real selected user goal and the candidate adds an authoring affordance the baseline lacks. The rationale for **making graph-first the default** is NOT established, and the current separation between working canvas and source projections remains a meaningful product gap.

I would change the verdict toward **hybrid/prose-first** if comparable real author tasks show graph actions consistently delay writing, obscure canon, or fail to uncover useful story structure. I would strengthen **graph-first** if users repeatedly derive and act on useful relationship insights more naturally than through the current interface.

**Immediate next decision:** retain the opt-in candidate, do not invest in wide new graph features, fix hard author-work loss if confirmed, and run only the matched author-task probes that discriminate A/B/C.

**Claim ceiling:** source-grounded product critique and viable hypothesis set; neither cohort preference nor superior author outcomes demonstrated.
