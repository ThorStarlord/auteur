## Scope and sources

I read the four named files from the snapshot. I did not read the contracts they reference (realization-state, theme-and-motif, character-and-relationship, story-opportunity-discovery), so nothing below relies on them.

- `C:\Users\Admin\AppData\Local\Temp\claude\e91f3203f308aeba\b058a91a-026a-436c-9148-0051d73610e9\scratchpad\worker-snapshot-6e886a0d\data\ontology\base_ontology.yaml`
- `C:\Users\Admin\AppData\Local\Temp\claude\e91f3203f308aeba\b058a91a-026a-436c-9148-0051d73610e9\scratchpad\worker-snapshot-6e886a0d\docs\narrative-architecture.md`
- `C:\Users\Admin\AppData\Local\Temp\claude\e91f3203f308aeba\b058a91a-026a-436c-9148-0051d73610e9\scratchpad\worker-snapshot-6e886a0d\docs\emotional-trajectory-contract.md`
- `C:\Users\Admin\AppData\Local\Temp\claude\e91f3203f308aeba\b058a91a-026a-436c-9148-0051d73610e9\scratchpad\worker-snapshot-6e886a0d\src\auteur\beginner\studio_ontology_context.py`

The Story Vision is a pre-Identity working premise. Under the architecture doc, it stays noncanonical until it passes Story Discovery and explicit acceptance. Everything below is advisory.

## 1. Diagnosis of the current architecture

**Layer placement.** The Vision mostly supplies Identity material: theme (belonging, communal responsibility, public trust), target experience (a three-part reader promise), and a core engine (the bells as a judgment system). It also implies Structure material (a discovery arc), but no scope, medium, or genre is set.

**Central conflict.** The bell keeper's discovery is set against an unnamed party who altered the system. The base ontology defines Conflict as opposition between forces with incompatible goals and stakes. The Vision states the stakes (trust, belonging) but not either party's goal, so the Goal-must-have-owner rule is not yet satisfied.

**Causal structure.** The chain is: promise made, promise forgotten, bell rings, (unstated) response, trust and belonging sustained. The alteration breaks the link for powerful citizens. The discovery is a Revelation in ontology terms: it discloses hidden information and changes how the community is understood. The biggest gap is that the Vision never says what a ring produces.

**Emotional potential.** The reader promise is warmth and belonging, then unease, then hope earned collectively. Per the emotional-trajectory contract, this is a macro reader promise, not a sequence of character moods. Its strongest feature is that the warmth is the material the injustice violates, so the unease reads as betrayed intimacy. The contract explicitly permits irony and false resolution, so the opening warmth can stay warm on the surface while carrying the unease underneath.

**Strengths**
- The device embodies the theme (promises and bells literalize trust), so the theme can be dramatized rather than stated.
- The bells have built-in reversal potential. The ontology's Symbol rule allows meaning to evolve, and a Reversal inverts a trajectory unexpectedly. Here the bells can shift from an instrument of accountability to an instrument of privilege.
- Because the bells are communal, the hope arc is structurally collective, which matches the "not an effortless individual victory" requirement.

**Weaknesses**
- The bell mechanism is undefined: how forgetting is detected, what ringing causes, and who can hear.
- Neither protagonist nor antagonist has a stated goal.
- The alteration is unspecified: who made it, when, and what "exempt" means operationally (silent, ringing but ignored, or rerouted). "Secretly" implies a concealment mechanism that the Vision does not supply.
- "Collective action" has no organizer, form, or cost yet.
- The keeper maintains the system, so the discovery implicates the protagonist's own role. This is unresolved.
- Warmth risks becoming decorative unless the community is shown under pressure.

**Unresolved questions, in priority order**
1. What does a ring cause?
2. Does the community know about the alteration?
3. What makes a promise "important," and who decides?
4. Who benefits from the exemption, and who pays for it?

**Source notes that affect this reading**
- The studio module only adds genre extensions when a genre is explicitly named, using aliases such as "mystery" or "detective." The Vision names none, so the context would carry only the 12 base concepts and leave genre unknown. The premise has mystery-shaped features (concealed alteration, discovery), but the module treats genre as something an author must declare.
- Setup to Payoff is declared one-to-one, while Payoff to Setup is declared many-to-many. If the silenced bells are one Setup with several payoffs, the ontology contradicts itself on this point, which needs a modeling decision.
- The theme-resolution rule's condition says themes may stay unresolved, but its error message says "Theme must resolve." This looks like a metadata slip and does not change the reading above.
- Every validation rule's `applies_to` lists only the three existing genres. Applying them to this premise is an inference, not something the file states.

## 2. Two candidate mechanisms

**Mechanism A: The Ledger Beneath the Bells (record-based)**
- **How it works.** The bells ring from a registry of promises kept in the tower. The exemption is an administrative category: promises of "standing" citizens are excluded from comparison, so their bells never ring. The keeper finds a second class of entries.
- **Pressures.** The keeper's access is limited, the council controls the ledger, and the ledger can be corrected or destroyed. Exposure carries a cost: if the ledger is shown to be rigged, the bells lose authority, and the shared ritual that binds the city may collapse with them.
- **Collective action.** Because the ledger is controlled, verification must come from elsewhere. Residents testify about their own promises and whether their bells rang. The hope comes from distributed memory rather than a single heroic reconstruction.
- **Reader experience.** Unease builds from small discrepancies in ordinary records, with warm ritual serving as cover. Hope comes from testimony. This fits the warmth-unease-hope promise.
- **Risk.** It drifts toward procedural investigation. If pursued, the author would need to declare a genre.

**Mechanism B: Answering the Bells (social-response-based)**
- **How it works.** A ringing bell obliges neighbors to go to the forgetful person and help them make it right, so judgment is social before it is formal. The alteration muffles the bells of exempt households, so no one hears them or is obliged to help or judge.
- **Pressures.** Answering is local and visible, and visiting someone's home is a social act with costs. Neighbors who answer for the powerful become complicit, and those who refuse to answer others are judged. The powerful retaliate through standing rather than secrecy.
- **Collective action.** Residents begin answering the muffled bells themselves. This is risky because it means confronting a household with standing. The hope is chosen, costly participation.
- **Reader experience.** The warmth is the mechanism itself. Belonging becomes the instrument of injustice when applied selectively, which is the irony the contract allows: warm surface, unease beneath. A false resolution is also available, where ordinary answering resumes while exempt households stay silent.
- **Risk.** It is less plot-driven. It needs a clear antagonist and concrete scenes of answering, and mass social behavior is harder to sustain across a long narrative.

**How they differ.** The sources of injustice differ (record versus response). So do the collective acts (testimony versus answering), the dominant pressures (exposure cost versus social cost), and where the reader feels unease (discrepancy versus silence). Both need the Section 1 gaps closed first, especially what a ring causes.

## 3. Voluntary registration variant

**Bell operation.** The bells can only judge what is registered, so their domain becomes the registry rather than the community's promises. "Ring whenever someone forgets" becomes "ring when a registered promise lapses." This is a textual change to the premise and should be an explicit authorial decision. Detection also becomes an administrative comparison against fulfillment status, which makes the bells less mysterious and more bureaucratic.

**Forgetting.** Forgetting is redefined as lapse against a record. Forgetting an unregistered promise becomes invisible to the bells, so its moral weight shifts from a social failing to a documentation issue. New forms appear: forgetting to register, forgetting which promises were registered, and "I promise to register," a meta-promise that can itself lapse. If the registry remembers, citizens may remember less, which connects to the premise's idea of a community holding promises in its own memory.

**Effect on the alteration.** The exemption no longer requires secretly altering bell judgment. Powerful citizens can simply stay unregistered and go unreached in plain sight, so the injustice becomes lawful and deniable. This challenges the premise's word "secretly." The author must choose: keep a secret (about who was allowed to register, or how the registry is edited), or make the injustice open.

**Conflicts**
- Access inequality: registration costs time, literacy, distance, and trust in the registrar. The unregistered may be disproportionately poor or marginal, so the bells fail the people they were meant to protect. The injustice becomes multi-layered.
- Definitional power: whoever defines "promise" and "important" for registration holds the exemption, so registrar categories become a new site of power.
- The keeper's role shifts from listener to registrar, which creates new complicity.
- Theme: voluntary registration makes belonging elective. If only some register, shared responsibility becomes partial. Opt-in may strengthen warmth through chosen membership, but it weakens the premise's universality.

**Hope.** Mass public registration could be a collective act, with citizens openly registering their promises so exemptions become visible. This is a proposal, not a fact of the premise.

## 4. Assumptions and unspecified rules

**Assumptions this analysis relies on**
1. The bells' detection and ringing are taken as given. The Vision does not say whether they are supernatural, institutional, or ritual.
2. "Powerful citizens" is a class, but its basis (office, wealth, lineage) is unspecified.
3. The alteration is secret from citizens, and the keeper is the first to know.
4. The reader ordering (warmth, unease, hope) is a macro shape, not a required monotonic path, per the contract.
5. The city is a closed polity with no outside authority.
6. Collective action can be dramatized without a named antagonist.
7. The base ontology's rules apply to this premise, though their `applies_to` lists name only existing genres.
8. The Vision is a working premise, so Identity fields (genre, scope, medium, length, POV) are not set.
9. The snapshot's `data/ontology` file matches the packaged copy that the studio module loads. I did not verify this.

**Story rules the Vision leaves unspecified**
- What a ring causes: judgment, shame, penalty, or nothing.
- Who can hear a bell: everyone, keepers only, or the forgetful person.
- What "important" means, who decides it, and whether promises made to oneself count.
- What "exempt" means operationally.
- Who has authority to alter the bells, when the alteration happened, and whether it can be reversed.
- Whether keepers are hereditary, appointed, or elected, and whether keepers are subject to the bells themselves.
- Whether a repaired promise clears a ring, and whether bells can be wrong.
- Whether other institutions (courts, council) exist and how they relate to the bells.
- Scope, length, medium, and POV.

The highest-leverage decisions before Identity are: define the ring's consequence, decide whether the alteration is secret, choose between the record-based and response-based mechanisms (or a hybrid), and decide whether the registration variant is in or out.