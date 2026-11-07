## Re-examination of the Narrative Architecture analysis

Most conclusions hold. The central conflict, the diagnosis of gaps that come directly from the Vision text, the genre-trigger finding, and the variation's logical consequences all rest on the sources. Several claims went beyond what the sources support, and I correct them below. The two mechanisms survive; two of them need their premise trade-offs stated more plainly.

### Corrections

1. **The causal paraphrase was wrong.** I wrote "promises are kept → bells ring on forgetting." The Vision says promises are made, and the bells ring when someone forgets an important promise. Corrected chain: promise made → promise forgotten → bell rings → public judgment and ritual → trust and belonging.

2. **"Story Vision = working premise" is my reading.** `narrative-architecture.md` (lines 41-66) defines working opportunity, premise, and Discovery Brief outputs as advisory. It never names a "Story Vision." Applying that status to the Vision is reasonable, but the author should confirm it. My proposals are noncanonical either way, because I labelled them as proposals.

3. **The Setup obligation was overstated.** I said the exempt citizens' unpaid promises are setups the story is "structurally obliged to pay off." The rule (`setup_must_be_resolved`, lines 284-287) applies to narrative structures the author builds. It does not require the story to pay anything off. Corrected: if promises are modelled as Setups, the exempt ones are unpaid setups and a strong payoff target. Leaving them open can also be a deliberate choice that is itself the injustice.

4. **The collective-agent gap was overstated.** I said a collective goal "has no clean owner." Character is "an entity capable of agency" (line 9), which does not clearly exclude a collective. The real gap is definitional. The Goal owner rule (lines 145-148) allows "a Character or Story entity," and the base ontology defines no Story concept. A city could be modelled as a Character, but that decision should be made explicitly.

5. **The monotonic-rule conflict was overstated.** `arc_progression_is_monotonic` (lines 85-88) requires only that "progression from start to end should show change." It does not require monotonicity. The defect is a mismatch between the rule ID and its condition, which could mislead implementers who read the name. The contract's non-goal of mandatory monotonic arcs (line 162) concerns emotional arcs, not the base arc concept.

6. **Base rules were applied inconsistently.** I cited base rules as requirements, such as the stakes rule (lines 175-178), while also noting that every rule's `applies_to` names only three installed genres. I cannot treat them as binding on this story and inapplicable to it at the same time. Corrected: base rules are conceptual guidance for this Vision, not enforced validation. The tension is also sharper than I stated. `metadata.description` (line 334) says the concepts form "the foundation of all narrative structures," yet `applies_to` names three genres. That is a real unspecified rule.

7. **The emotional sequence was over-mapped.** I treated warmth → unease → hope as the fitting macro trajectory. The Vision says the experiences "combine." The contract's Identity section has separate slots for primary promise, secondary palette, and macro trajectory (lines 27-36), and the Vision does not assign its bullets to them or say whether they run in sequence. Corrected: sequencing is an open author choice. The two mechanisms take different positions on it, which should be presented as a choice rather than a finding.

8. **"Warmth is load-bearing" is my analysis, not source text.** The contract supports divergence and irony (lines 92-101), which is the basis for saying warmth can make injustice register. "Load-bearing" is my interpretation and should be labelled as such.

9. **The "refusal of heroic individualism" was overstated.** The Vision rejects "an effortless individual victory." It does not reject individual agency or a protagonist's heroism. The constraint governs how hope is earned. A keeper-led investigation is compatible with it if the ending depends on collective action. The warning on Mechanism A should be restated: the ending must not rest on the keeper alone.

10. **Mechanism B's fidelity claims were overstated.** I said B is "faithful to 'forgets'" because the city forgets. The Vision's forgetting is individual ("someone forgets"). B extends it to collective forgetting, which is a legitimate creative extension but not fidelity. B also moves the alteration from the system into ritual practice, while the Vision says the system "has been secretly altered." The mechanism stands, but the author must accept that premise reinterpretation explicitly.

11. **The breach reading of "forgets" should be stated as a condition.** Both mechanisms and the variation treat "forgets" as failing to honour a promise. "Judgment" in the Vision supports that reading. But "forgets" could also mean memory loss, with the bells as reminders. Under that reading, the sealed ledger and the naming rite need rework, and registration becomes a memory aid rather than a judgment system. The conclusions hold under the breach reading, which I adopted, but they are conditional on it.

12. **The scale claim was overstated.** I said scale "determines required structure (lines 77-102)." That section describes paths for a short story, a standalone novel, and a series, and says what each requires. It does not impose a rule derived from scale alone.

13. **"Native fit" and "needs no tampering" were overstated.** The promise-to-Setup fit holds by definition, since line 270 lists "promise," not by any stronger kind of fit. In the variation, access costs can produce injustice without tampering, but control of the registration office is itself a tampering channel. Corrected: "can," not "needs."

### Conclusions that stand

- The central conflict: the bells are both the object of belonging and the instrument of injustice. This comes directly from the Vision.
- The gaps in the Vision: no stated mechanism, an undefined "important promise," and no protagonist goals, stakes, end states, genre, or scale.
- The genre-trigger finding. Reading `studio_ontology_context.py` (lines 19-23 and 36-54), none of its aliases appear in the Vision, so only base concepts are added. I did not run the code.
- The emotional contract's separation of reader promise from character feeling, and its allowance for irony and divergence.
- The variation's consequences: the bells' trigger narrows to registered promises; withdrawal rights would reopen the exemption; treating registration as a promise creates a regress; the exemption moves from machinery to choice.
- The list of unspecified rules.

### Mechanisms after revision

- **A, the sealed ledger (secret mechanism, plot-led):** stands. Its risk is framing the keeper as the decisive actor. The hope it offers is earned only if residents' collective demand completes the exposure.
- **B, the unspoken naming (communal ritual, theme-led):** stands, relabelled. It reinterprets "secretly altered" as a ritual practice and extends individual forgetting to collective forgetting. The author must accept both changes before B is a candidate.

Both remain noncanonical proposals. The variation analysis stands with the "can" correction in item 13.