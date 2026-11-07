## Narrative Architecture exercise: Bell Keepers

I read only the four named files and wrote nothing. The Vision maps well onto the ontology's Setup, Revelation, and Symbol concepts and onto the emotional contract's split between reader promise and character feeling. Its main gaps are an undefined bell mechanism, no collective agent in the ontology, and no declared genre, scale, or ending state. Under `docs/narrative-architecture.md` (lines 41-66), a Story Vision is a working premise, not accepted Identity, so everything below is advisory.

### 1. Diagnosis

**Central conflict.** The bells are both the object of the community's belonging and the instrument of its injustice. The conflict has two layers: external (keeper against exempt powerful citizens) and internal (the community's attachment to rituals it would have to question). The Vision states both but develops only the external one.

**Causal structure as stated.** Promises are kept → bells ring on forgetting → public accountability and ritual → trust and belonging. The alteration exempts some promises → unequal accountability. Discovery → the keeper holds knowledge → a choice. The endpoints are present, but the rules between them are not: what triggers a ring, what a ring does, how the exemption works, and who knows.

**Ontology fit** (`data/ontology/base_ontology.yaml`):
- A promise maps naturally to **Setup**, defined as "an element, promise, or mystery that requires later resolution" (line 270). Under `setup_must_be_resolved` (lines 284-287), the exempt citizens' unrung promises are unpaid setups the story is structurally obliged to pay off. That is a strong hook for the ending.
- The discovery is a **Revelation** that must change understanding (lines 305-308). The exemption reframes the bells from neutral arbiter to instrument.
- The bells' drift from belonging to complicity fits **Symbol**, whose meaning "can evolve" (lines 217-220).
- "Hope through collective action" has no clean base concept. **Character** is "an entity capable of agency" (line 9), and a Goal must belong to "a Character or Story entity" (lines 145-148). The base ontology defines no Story or collective concept, so a collective goal has no clean owner.

**Emotional potential** (`docs/emotional-trajectory-contract.md`):
- The three reader-facing bullets are a reader promise. They fit a macro trajectory of warmth → unease → hope (Identity, lines 25-36). The Vision says the experiences "combine" but does not say whether they are sequential or concurrent.
- Warmth is load-bearing. Injustice registers against a warm baseline, and the contract's allowances for irony and intentional divergence (lines 92-101) let readers feel unease while residents feel belonging.
- "Rather than effortless individual victory" is a candidate for an avoided experience (Identity lists these, line 34).
- Whether hope is "earned" is an authorial judgment. The contract says validation must not judge artistic quality (lines 116-117), so the structure has to carry the earnedness.

**Strengths:** the double-edged symbol; a built-in refusal of heroic individualism; native fit between promises and setup/payoff; a clear inciting discovery.

**Weaknesses:**
- The core mechanism is unspecified.
- "Important promise" is undefined, and it is the judgment criterion of the whole system. The injustice can be dismissed as "not important."
- The protagonist's goal, the antagonists' goals, stakes (required by `conflict_must_have_stakes`, lines 175-178), and arc end states are all missing.
- Theme and emotion are blended. "Belonging" appears as both a theme and a reader experience, and the contract keeps them separate (lines 138-144).
- No genre, scale, or scope is declared. `studio_ontology_context.py` adds genre concepts only when a genre is named (lines 36-54, 138-142). None of its aliases appear in the Vision, so the story receives base concepts only, and "an unnamed genre stays unknown." Its "foundational" list (lines 15-18) is all twelve base concepts, so it selects nothing. I inferred this from reading the code, not by running it.
- Ontology issues that touch this story:
  - `theme_may_not_require_resolution` has the error message "Theme must resolve" (lines 111-114).
  - `arc_progression_is_monotonic` (lines 85-88) conflicts in name with the contract's non-goal of mandatory monotonic arcs (line 162).
  - Every base rule's `applies_to` names only the three installed genres, so the snapshot does not show how a genre-less story is validated.

### 2. Two mechanisms

**Mechanism A: the sealed ledger (secret mechanism, plot-led).**
- *How it works:* Bells still ring for everyone, but when an exempt citizen forgets, the ring is logged to a sealed book the keeper maintains as routine. The keeper has been, unknowingly, the clerk of the exemption.
- *Pressures:* She is the only reader of the evidence. The bells can be turned on her: if she is seen as a forgetter, the bell rings for her. Exposure risks the ritual the whole city depends on.
- *Engine and reader experience:* Escalating revelation runs from a silent anomaly to the sealed book, then to exempt names including the council and her mentor. Warmth fills the early rituals, and unease builds as mundane ledger entries accumulate. Dramatic irony is available if the reader sees entries before the keeper understands them.
- *Hope:* Exposure fails on its own (a Reversal, lines 310-329: the council dismisses the book as a clerical error). Hope comes when residents collectively demand a public reading of the ring log. That preserves the Vision's rule.
- *Risks:* Thriller shape, drift toward individual heroism, and a forced genre decision.

**Mechanism B: the unspoken naming (communal ritual, theme-led).**
- *How it works:* Bells still ring for every forgotten promise, but a ring becomes social judgment only when someone names it aloud at the morning rite. Over generations, naming was delegated to officials, who never name the exempt households. The alteration lives in ritual, not in the metal.
- *Pressures:* Stability versus justice: exempt households argue that naming would fracture the town. The community's comfort in the rite makes it complicit. Collective action is structurally necessary because naming requires many voices. The author must decide that rule.
- *Engine and reader experience:* Warmth lasts longer and becomes the vehicle of complicity. The reader sees the beauty of the rituals while detecting their omissions. Unease builds through small silences rather than discovery events.
- *Hope:* Ordinary residents perform a communal naming. It works only because the story spent time on the rituals.
- *Risks:* Low external tension, which needs a clock (a festival, a death, a failing bell). Also a risk of abstraction and didactic speeches.

**Trade-off.** A is faithful to "secretly altered" and centres the injustice in a record. B is faithful to "forgets," since the city forgets, and centres it in a silence. A's hope risk is heroism; B's is passivity.

### 3. Voluntary registration variation (hypothetical)

**Core shift.** The exemption stops being a secret alteration and becomes a property of who registers. The bells judge only registered promises, so exemption by design becomes exemption by choice.

**Operation of the bells.**
- The trigger changes from "whenever someone forgets" to "whenever a registered promise is forgotten." Unregistered forgetting is silent.
- Three rules must be decided. Can registration be withdrawn? If so, the powerful can register and withdraw at will, and the exemption returns through a legal-looking door. Who maintains the register and who may read it? Is registering itself a promise? If yes, forgetting to register rings and the system is universal again. If no, opt-out is built in.
- In ontology terms, the broad "promise" narrows to registered Setups, and the bells enforce setup/payoff only on those.

**The possibility of forgetting.**
- Forgetting gains a second layer. Forgetting to register is invisible to the bells; forgetting a registered promise rings. Some forgetting becomes administrative.
- Forgetting may become strategic: "I did not register, so I cannot be rung."
- The bells stop representing universal memory and start representing a subscribed service. That may weaken "belonging to something larger" unless registration is itself communal.

**Story conflicts.**
- The conflict moves from "is the bell altered?" to "who decides what counts as a promise, and who can afford to register?" Access costs (time, literacy, distance to the register) become a new channel for injustice that needs no tampering.
- Evidence changes. The exemption becomes an absence, which is harder to prove and less dramatic. The story needs new evidence forms, such as patterns in the register or silence where a registered powerful name should ring.
- Apparent fairness can serve as a false resolution (contract lines 100-101), followed by a regression as the asymmetry surfaces. That supports the warm-to-unease-to-hope trajectory.
- Registration can be a collective act: residents register together or refuse together. That may carry the Vision's hope better than the keeper's exposure.
- The keeper may be asked to enforce or administer the register, which creates a complicity conflict.
- A readable public register is a list of promises. That may add a new source of unease, though this is my inference, not something the Vision states.
- Thematic cost: registration may turn ritual into filing, weakening "connect everyday rituals." The author must decide whether registration is a ritual or an administrative act.

**Interaction with A and B.** In A, the sealed ledger becomes the register, so the hidden record becomes the legitimate one, which is a stronger reversal. In B, naming becomes a public registration rite, which can preserve belonging if done communally.

### 4. Assumptions and unspecified rules

**Assumptions my analysis relies on:**
1. "Combines" means the reader experiences coexist, with warmth as baseline. The sequence is unknown.
2. "Forgets" means failing to honour a promise, not losing memory of making it. If it means memory loss, A and B change.
3. Bell rings are publicly perceptible, which communal judgment requires.
4. The keeper is a POV character and the "powerful citizens" form a distinguishable group.
5. The story is novel-scale or larger. No scope is declared, and scale determines required structure (lines 77-102).
6. No genre is accepted, and I inferred none.
7. The emotional contract applies as a lens before Identity. Its concepts are not accepted commitments.
8. I read the code but did not run `studio_ontology_context.py`.
9. I did not follow the other contracts referenced in `narrative-architecture.md` (theme-and-motif, character-and-relationship, revision-staleness, story-opportunity-discovery, premise-fitness). They could refine Sections 1-3.

**Unspecified story rules:**
- What counts as a promise, and what "important" means.
- How the bells detect forgetting; whether rings are continuous or single; whether they can be silenced.
- What a ring does (social, legal, or personal consequence).
- How the alteration works, who can make or reverse it, and how old it is.
- Whether the exempt citizens form one faction and whether all of them know.
- Who maintains the bells, and whether the keeper has authority over them.
- Whether the city has a governance route for collective decisions (assembly, vote, rite). Without one, "collective action" has no carrier.
- Stakes and end states for the keeper, the exempt citizens, and the city, and whether hope is stated or implied.
- Whether the reader knows about the exemption before the keeper.
- Whether warmth decays or persists.
- Genre, scale, and scope, including whether bell rules are Universe-level world constraints and the plot is Book-level.
- How base validation rules apply to a genre-less story.