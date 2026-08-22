# Phase H — H2 Frozen Coding-Agent Producer Packet

## Evidence status

**Producer-only evidence. Do not treat this document as an evaluation.**

This packet was produced for Phase H H2 and is intended to be frozen before the H3 context-reduced evaluator pass. It contains candidate generation, causal profiling, causal-distinctness classification, an intent-aware advisory recommendation when adjudicable, and F4-style craft/composition evidence.

It deliberately contains **no evaluator reaction**, no `convincing` / `defensible with concerns` / `failure` verdict, no numeric score, no success rate, and no judgment about whether the producer itself performed well.

### Provenance

- phase: `H2`
- producer role: coding-agent producer
- producer model family: `GPT-5.6 Sol`
- production-contract baseline: `dd17040d7fb828ed863823b131224d03ac0f4d81`
- benchmark corpus: `docs/research/story-discovery-phase-h-cases.yaml`
- benchmark corpus blob: `aadeca2daba68b5eb77b3f7d301d2a5f34c491e9`
- protocol update commit preceding this packet: `e63e6d6404866e82a0baea81bae32e258f231866`
- production contracts consulted:
  - `src/auteur/story_discovery_intent.py`
  - `src/auteur/story_discovery_recommend.py`
  - `src/auteur/story_discovery_causality.py`
  - `src/auteur/story_discovery_craft.py`
- canonical acceptance allowed: `false`
- automatic quality scoring allowed: `false`
- date produced: `2026-08-21` (America/Sao_Paulo)

Candidate labels in this packet are traceability labels only. Their order, label, title length, and amount of prose are not quality signals.

---

# H01 — Dead Channel

## Exact declared brief

```yaml
premise: A retired astronaut hears mission-control chatter in her empty apartment.
story_type:
  genre: sci_fi
  target_audience: adult
target_experience:
  primary_emotional_promise: haunted self-reckoning under impossible evidence
architecture_preferences:
  complexity: layered
  causal_distribution: layered
  engine_hierarchy: primary_with_layers
hard_constraints:
  - The protagonist is genuinely retired at the beginning.
  - The mission-control chatter must remain causally important rather than decorative atmosphere.
```

## Candidate A — Dead Channel

**Core answer:** The impossible chatter is a fragmented retransmission of the protagonist's final mission, but the fragments contradict the version of the disaster she has lived with for years. She investigates the signal to reconstruct what she chose, what she failed to hear, and why her memory protected her from it.

**Central engine**

- want: determine why the impossible mission-control traffic is reaching her apartment and what actually happened during her final mission;
- resistance: damaged recordings, contradictory memory, former colleagues who remember the event differently, and her own practiced explanation of the disaster;
- conflict: every recovered transmission gives her stronger factual evidence while destabilizing the identity built around surviving the mission;
- stakes: she can preserve the story that allowed her to live after retirement or recover a truth that may alter her responsibility for a crew member's death;
- change: she stops treating memory as a verdict and accepts responsibility for a choice whose meaning she had simplified.

**Causal profile**

- primary strategy: reconstruct the failed mission by correlating impossible transmissions with archived telemetry, witness memory, and her own recollections;
- causal owner: the retired astronaut's investigation, with the signal supplying bounded new evidence;
- external action pattern: record, decode, cross-check, interview, revisit archived decisions, test competing reconstructions;
- pressure system: each fragment closes off a comforting explanation while the source of the signal remains physically impossible;
- reversal mechanics:
  - a recovered transmission contradicts a remembered command sequence;
  - a former colleague's account shifts apparent responsibility;
  - a final fragment reveals that the protagonist heard enough to make a consequential choice at the time;
- climax mechanic: she reconstructs the complete final exchange and publicly or privately states what she actually chose rather than the version she has repeated for years;
- scene families: late-night signal captures, archive reconstruction, tense conversations with former crew/mission-control staff, memory-versus-record comparison, final reconstructed transmission;
- evidence gaps: the physical explanation for why the signal appears now remains an open speculative mechanism.

## Candidate B — One More Orbit

**Core answer:** The chatter comes from a survivor of the old mission caught in a relativistic/time-displaced communication window. The protagonist cannot return to active flight, but her knowledge of the mission makes her the only person capable of coordinating a rescue from Earth before the window closes.

**Central engine**

- want: identify the speaker and coordinate a viable rescue without returning to astronaut service;
- resistance: an unstable communication window, obsolete mission systems, agencies that regard the signal as impossible, and the protagonist's loss of formal authority after retirement;
- conflict: she must turn private impossible evidence into a coordinated technical rescue while persuading institutions to act on information only she can interpret;
- stakes: a stranded crewmate may remain unreachable forever, and the protagonist may discover that retirement cannot protect her from unfinished obligations;
- change: she learns that being retired ends her role but not her capacity to act responsibly with what she knows.

**Causal profile**

- primary strategy: convert intermittent future/past mission-control chatter into actionable rescue telemetry and coordinate present-day institutions around it;
- causal owner: the retired astronaut as technical coordinator, with agencies and the stranded survivor as dependent actors;
- external action pattern: decode, calculate, persuade, assemble specialists, stage tests, coordinate timed rescue actions;
- pressure system: shrinking communication windows, institutional disbelief, technical obsolescence, and the protagonist's lack of command authority;
- reversal mechanics:
  - the signal is proven to contain live responses rather than archival playback;
  - a rescue assumption based on old mission data fails;
  - the astronaut discovers the survivor has been transmitting under different temporal conditions than expected;
- climax mechanic: she coordinates a precisely timed present-day intervention that allows the survivor's signal/location to become reachable without personally returning to space;
- scene families: signal-response experiments, technical planning rooms, institutional persuasion, remote rescue rehearsals, final timed coordination;
- evidence gaps: exact speculative physics of the communication window.

## Candidate C — Ground Loop

**Core answer:** The chatter is an illicit rebroadcast assembled from mission-control channels that were removed from the official record. Someone is forcing the protagonist to hear evidence that mission leadership knowingly sacrificed part of her crew. She must reconstruct the institutional decision and decide what to do with the truth.

**Central engine**

- want: identify who is transmitting suppressed mission-control traffic and determine what the hidden channels prove;
- resistance: classified records, former officials protecting the institution, partial evidence, and the protagonist's emotional investment in the organization that defined her adult life;
- conflict: proving institutional wrongdoing requires her to attack the authority structure that made her career and shaped her account of the mission;
- stakes: exposing the truth may destroy reputations and her own legacy; silence preserves an official lie about the dead;
- change: she shifts from loyalty to the institution as identity toward loyalty to the people and facts the institution erased.

**Causal profile**

- primary strategy: trace suppressed communication records, identify the anonymous rebroadcaster, and assemble a public evidentiary case against mission leadership;
- causal owner: the protagonist's institutional investigation, opposed by surviving mission leadership;
- external action pattern: authenticate, trace, interview, obtain records, confront officials, prepare disclosure;
- pressure system: secrecy rules, institutional counterpressure, reputational risk, and uncertainty about the transmitter's motives;
- reversal mechanics:
  - a supposedly fabricated transmission authenticates against independent telemetry;
  - the anonymous source is revealed to have a personal stake in the failed mission;
  - evidence shows the sacrifice was a deliberate policy choice rather than one rogue decision;
- climax mechanic: the protagonist uses the reconstructed hidden channel sequence to force an institutional reckoning in a hearing, publication, or public confrontation;
- scene families: forensic audio authentication, classified-record pursuit, former-colleague confrontations, institutional pressure encounters, public evidence presentation;
- evidence gaps: identity and delivery mechanism of the initial rebroadcaster are open design choices.

## F3-style pairwise causal assessment

- A / B: `distinct` — A repeatedly reconstructs a past decision to confront personal responsibility; B repeatedly converts live impossible communication into rescue coordination. Their protagonist verbs, pressure, reversals, and climaxes differ materially.
- A / C: `distinct` — A's decisive causal contest is memory/evidence reconstruction centered on the protagonist's own choice; C's is institutional investigation and disclosure against organized resistance.
- B / C: `distinct` — B is a time-critical technical rescue system; C is an evidentiary exposure system.

**F3-style set status:** `qualified`

## Producer intent-aware recommendation

**Recommended:** Candidate A — Dead Channel.

**Rationale:** The declared primary promise is haunted self-reckoning under impossible evidence. Candidate A makes the signal simultaneously the speculative mechanism, investigative evidence, and pressure on the protagonist's self-understanding. It also satisfies the layered / primary-with-layers preference without requiring the institutional or rescue layer to own the climax.

**Why not B:** B preserves the impossible chatter and creates strong external action, but its governing objective becomes saving another person through technical coordination. The center of gravity moves toward urgency and rescue rather than self-reckoning.

**Why not C:** C preserves haunted evidence and can sustain moral pressure, but the decisive conflict becomes institutional wrongdoing. The protagonist's personal memory can remain important, yet the public conspiracy/exposure engine owns more of the major action and climax.

## F4-style craft impact: B relative to A

- craft layers changed: causal_strategy, causal_ownership, external_action, pressure_system, scene_families, reader_experience, theme;
- causal ownership shift: from the protagonist reconstructing her own past decision to the protagonist coordinating multiple present-day actors toward a rescue;
- external action shift: emphasize calculation, persuasion, logistics, timed intervention; de-emphasize archival reconstruction and self-incriminating memory comparison;
- scene-family shift: more technical planning/rescue scenes, fewer intimate evidence-versus-memory confrontations;
- pressure/texture shift: haunted uncertainty becomes deadline-driven technical urgency;
- reader-experience shift: self-reckoning is preserved only if rescue choices repeatedly reactivate the old mission; otherwise the primary promise is reweighted toward suspense and hope;
- thematic effect: agency after retirement rather than responsibility for the meaning of a past choice;
- gain: stronger forward momentum and an externally measurable objective;
- give up: some of the premise's intimacy and the direct coupling between impossible evidence and self-knowledge;
- composability: `requires_reframing`;
- composition note: a weak/partial rescue obligation could provide present pressure, but it must expose the old choice rather than become the governing win condition;
- primary risk: a full rescue countdown displaces the self-reckoning engine.

## F4-style craft impact: C relative to A

- craft layers changed: causal_ownership, external_action, pressure_system, scene_families, story_texture, theme;
- causal ownership shift: adds an institution as an active opposing causal owner;
- external action shift: add authentication, record pursuit, confrontation, disclosure; de-emphasize purely private reconstruction;
- scene-family shift: institutional interviews/hearings join the archive and memory scenes;
- pressure/texture shift: haunted ambiguity gains paranoia, secrecy, and public-risk pressure;
- reader-experience shift: the primary self-reckoning can remain governing if institutional suppression explains why her false memory endured rather than replacing her responsibility;
- thematic effect: adds the relationship between personal memory and institutional narrative control;
- gain: an external antagonist and layered source of resistance;
- give up: some solitude and ambiguity if institutional culpability becomes too explanatory;
- composability: `compatible_as_secondary`;
- composition note: institutional suppression can obstruct access to the truth while the climax still turns on what the protagonist did and how she understands it;
- primary risk: making mission leadership the true villain can absolve the protagonist and collapse the intended self-reckoning.

---

# H02 — Between Floors

## Exact declared brief

```yaml
premise: "A murder mystery in one elevator: six strangers, no supernatural explanation, and the killer never leaves the elevator."
story_type:
  genre: mystery
  target_audience: adult
target_experience:
  primary_emotional_promise: claustrophobic suspicion resolving into reconstructive relief
  secondary_palette:
    - dread
    - moral uncertainty
  avoided_experiences:
    - supernatural awe
architecture_preferences:
  complexity: maximalist
  causal_distribution: mixed
  engine_hierarchy: primary_with_layers
hard_constraints:
  - The killer never leaves the elevator.
  - The final solution is physically possible and retrospectively fair.
  - The sealed-space mechanics must materially matter to the solution.
```

## Candidate A — Hidden Seconds

**Core answer:** The killer stages an emergency stop that creates a short interval in which lights, body positions, door-control status, and passengers' assumptions about elapsed time diverge. The detective solves the case by reconstructing those hidden seconds from physical traces and conflicting perception.

**Central engine**

- want: reconstruct exactly how the murder occurred while all six people remained inside;
- resistance: darkness, compressed space, mistaken time estimates, overlapping movements, and mutually contaminating testimony;
- conflict: every suspect's account is locally plausible until the detective maps it against elevator mechanics and the limited positions available during the stop;
- stakes: if the impossible sequence cannot be reconstructed fairly, the killer leaves behind a perfect-room alibi;
- change: the detective learns to treat shared assumptions about what "could not have happened" as evidence rather than fact.

**Causal profile**

- primary strategy: reconstruct a physically exact second-by-second murder sequence from elevator mechanics, body positions, and testimony;
- causal owner: detective-led physical reconstruction opposed by the killer's staged timing illusion;
- external action pattern: measure, reenact, compare, test, eliminate positions, reconstruct sequence;
- pressure system: confinement, contradictory testimony, limited physical possibilities, and the expectation that everyone saw the same event;
- reversal mechanics: a timing assumption fails; load/door data disproves a claimed position; reenactment reveals a movement possible only during the blackout;
- climax mechanic: a live reconstruction demonstrates the fair-play sequence and identifies the killer's unique opportunity;
- scene families: testimony map, elevator-mechanism tests, body-position reenactments, clue reconciliation, final demonstration;
- evidence gaps: exact murder method/tool remains a later structure-level choice.

## Candidate B — Weight of an Alibi

**Core answer:** The killer manipulates where passengers stand and when they shift position so the elevator's load and leveling sensors create a false record of when the victim was alive and where everyone could have been. The detective solves a choreography puzzle in which social behavior and machine readings form one alibi system.

**Central engine**

- want: explain why objective elevator sensor data appears to exonerate everyone;
- resistance: passenger movement, misleading weight readings, deliberate crowd choreography, and motives that make innocent people hide where they stood;
- conflict: the detective must separate truthful machine data from the false inference the killer designed it to support;
- stakes: trusting the elevator's records at face value makes the murder mechanically impossible;
- change: the detective learns to distinguish a measurement from the story people tell about what the measurement means.

**Causal profile**

- primary strategy: reconstruct passenger choreography and sensor state to show how truthful machine readings were turned into a false timeline;
- causal owner: killer-designed choreography versus detective interpretation of objective system data;
- external action pattern: inspect sensor logs, weigh passengers/objects, reproduce standing positions, interrogate concealed movements, test alibi configurations;
- pressure system: apparently objective exculpatory data plus social reasons passengers obscure their exact positions;
- reversal mechanics: a sensor record proves true but its inferred meaning fails; a passenger admits a concealed movement; a recreated weight distribution reveals the killer's designed alibi;
- climax mechanic: the detective recreates the exact weight/position configuration that generated the misleading machine record and isolates the killer's move;
- scene families: sensor-log analysis, weight experiments, position diagrams, concealed-movement interrogation, final choreography reenactment;
- evidence gaps: exact sensor capabilities must be technically researched during structure design.

## Candidate C — All Doors Closed

**Core answer:** One passenger commits the murder during a mechanically possible stop, but several others independently conceal pieces of what they saw because each has a separate reason to protect the victim, themselves, or another passenger. The detective must solve both the physical act and the distributed concealment that makes the act appear impossible.

**Central engine**

- want: identify the killer while explaining why nearly every witness account contains a different omission;
- resistance: independent concealments, conflicting loyalties, cramped sightlines, and the killer exploiting the group's fragmented lies-by-omission;
- conflict: the detective cannot reconstruct the physical murder until the social reasons for each missing observation are separated from actual guilt;
- stakes: collective concealment can manufacture reasonable doubt even though only one person killed the victim;
- change: the detective shifts from searching for one coherent conspiracy to mapping several incompatible motives for concealment.

**Causal profile**

- primary strategy: decompose the group's testimony into independent concealments, then combine the recovered observations with elevator mechanics to reconstruct the murder;
- causal owner: detective-led social decomposition opposed by distributed witness concealment and the killer's exploitation of it;
- external action pattern: interrogate, cross-compare omissions, expose private motives, map sightlines, reenact the stop, reconstruct the act;
- pressure system: claustrophobic mistrust, multiple morally ambiguous secrets, and a physical sequence obscured by social concealment;
- reversal mechanics: one apparent accomplice is cleared as merely concealing an unrelated act; another omission changes the physical timeline; the final recovered observation makes the mechanical sequence possible;
- climax mechanic: the detective separates every witness's reason for silence and then reconstructs the one physical act only the killer performed;
- scene families: paired testimony contradictions, private secret reveals, sightline tests, group-pressure confrontations, final social-plus-physical reconstruction;
- evidence gaps: exact independent motives need downstream character design.

## F3-style pairwise causal assessment

- A / B: `distinct` — A's engine is hidden elapsed time and physical movement; B's is truthful sensor data deliberately arranged to produce a false inference. Tests, reversals, and decisive clues differ.
- A / C: `distinct` — A privileges physical reenactment of a compressed interval; C repeatedly decomposes social concealments before the physical act becomes reconstructable.
- B / C: `distinct` — B attacks an objective-data alibi through sensor/choreography experiments; C attacks distributed human omission through motive and testimony decomposition.

**F3-style set status:** `qualified`

## Producer intent-aware recommendation

**Recommended:** Candidate A — Hidden Seconds.

**Rationale:** The declared mystery promise emphasizes claustrophobic suspicion resolving into reconstructive relief, with a hard requirement that sealed-space mechanics materially matter. Candidate A makes the physical impossibility itself the governing engine and gives the climax the most direct reconstructive form. The other two candidates remain compatible with the maximalist/mixed preference as possible subordinate layers.

**Why not B:** B uses elevator mechanics rigorously, but the mystery center becomes interpretation of machine records and engineered sensor evidence. It is still fair-play, yet less directly about the shared lived impossibility of six people occupying one tiny space during the decisive seconds.

**Why not C:** C strongly uses the six-stranger social pressure and moral-uncertainty palette, but the repeated action pattern is testimony decomposition. The physical reconstruction risks becoming the final answer after a primarily social concealment story.

## F4-style craft impact: B relative to A

- craft layers changed: causal_strategy, external_action, scene_families, pressure_system, story_texture;
- causal ownership shift: from bodily timing illusion to killer-designed interpretation of machine data;
- external action shift: add sensor-log analysis, weighing and configuration tests; de-emphasize pure second-by-second movement reconstruction;
- scene-family shift: more forensic machine experiments, fewer perception/timing reenactments;
- pressure/texture shift: claustrophobic uncertainty gains technical-forensic texture;
- reader-experience shift: reconstructive relief is preserved, but the route becomes "the data were true, the inference was false" rather than "the impossible seconds were misperceived";
- thematic effect: measurement versus interpretation;
- gain: objective evidence that can be fairly planted and reinterpreted;
- give up: some immediate bodily claustrophobia of the murder interval;
- composability: `requires_reframing`;
- composition note: a limited sensor clue can strengthen A's reconstruction, but a full sensor-alibi system would become a competing primary puzzle;
- primary risk: the reader experiences the case as a sensor trick rather than a sealed-space timing puzzle.

## F4-style craft impact: C relative to A

- craft layers changed: causal_ownership, external_action, pressure_system, scene_families, reader_experience, theme;
- causal ownership shift: adds several witnesses as active sources of obstruction without making them co-killers;
- external action shift: add motive-specific interrogation and omission mapping while retaining mechanical reenactment;
- scene-family shift: more private secret reveals and group confrontations layered around the physical tests;
- pressure/texture shift: technical claustrophobia gains moral uncertainty and interpersonal suspicion;
- reader-experience shift: dread and moral uncertainty become stronger secondary colors while reconstructive relief can remain primary;
- thematic effect: people can collectively obscure truth without sharing one conspiracy;
- gain: richer use of six strangers and mixed causation;
- give up: some purity and economy of the physical puzzle;
- composability: `compatible_as_secondary`;
- composition note: individual omissions can hide specific observations needed for A's timing reconstruction while the physical sequence remains the governing solution;
- primary risk: too many secrets could make confession, not reconstruction, solve the murder.

---

# H03 — Nothing Missing

## Exact declared brief

```yaml
premise: A heist where nothing can be stolen, nobody may lie, and the crew must still defeat a corrupt museum director.
story_type:
  genre: thriller
  target_audience: adult
target_experience:
  primary_emotional_promise: delighted procedural cleverness under escalating institutional pressure
architecture_preferences:
  complexity: layered
  causal_distribution: mixed
  engine_hierarchy: primary_with_layers
hard_constraints:
  - No object may be stolen or secretly removed from the museum.
  - No crew member may knowingly state a lie.
  - The climax must still feel like an active coordinated operation rather than a paperwork-only exposé.
```

## Candidate A — Provenance Cascade

**Core answer:** The crew defeats the director by proving the true provenance of disputed objects through a timed chain of lawful access, live authentication, donor testimony, conservation evidence, and public claims. Nothing leaves the museum; what the operation steals is the director's ability to define legitimate ownership.

**Central engine**

- want: force the museum to publicly lose control of the false provenance stories that protect the director;
- resistance: compartmentalized records, donor pressure, controlled access, the director's ability to delay verification, and the crew's inability to lie or remove evidence;
- conflict: the crew must coordinate truthful disclosures so each one unlocks the next before the director can isolate or suppress them;
- stakes: failure leaves the artifacts physically untouched but institutionally trapped under fraudulent ownership claims;
- change: the crew shifts from treating possession as physical control to treating legitimacy and public knowledge as the contested asset.

**Causal profile**

- primary strategy: stage a synchronized public provenance verification that makes multiple independent truths mutually reinforcing and impossible to suppress;
- causal owner: crew coordination versus the director's institutional control of access and interpretation;
- external action pattern: authenticate, schedule, disclose, cross-verify, trigger lawful access, coordinate witnesses, stage public reveal;
- pressure system: timed access windows, institutional countermeasures, donor/legal pressure, and truthfulness constraints;
- reversal mechanics: one provenance chain is blocked; another truthful disclosure forces an unplanned access route; the director's attempted rebuttal authenticates a hidden dependency;
- climax mechanic: multiple crew roles execute a timed public verification sequence in which every statement is true and the director loses institutional control without any object leaving;
- scene families: access planning, conservation-lab verification, donor/witness coordination, public-event staging, cascading final reveal;
- evidence gaps: exact legal ownership outcomes depend on jurisdiction and should remain structural research.

## Candidate B — Open House

**Core answer:** The crew turns the museum's own lawful access rules, audit obligations, public-event logistics, insurance procedures, and donor restrictions into a heist architecture. They force the director to open systems he normally keeps separated, causing hidden evidence to become observable at one coordinated moment.

**Central engine**

- want: create a lawful operational state in which the director can no longer keep incriminating records and processes compartmentalized;
- resistance: bureaucracy, discretionary delays, security procedures, and the director's authority to cancel or reroute ordinary requests;
- conflict: every crew action must be a legitimate request or truthful statement, yet their combined sequence must produce an institutional condition the director never intended;
- stakes: if the director identifies the pattern early, he can close each procedural opening without ever needing to lie;
- change: the crew learns to treat rules as interacting mechanisms rather than obstacles to circumvent.

**Causal profile**

- primary strategy: chain lawful procedural triggers so ordinary museum systems expose one another under deadline;
- causal owner: crew manipulation of institutional process versus director-controlled discretion;
- external action pattern: request, schedule, file, attend, trigger audits, coordinate access, exploit rule dependencies;
- pressure system: bureaucratic timing, cancellation risk, compliance requirements, and limited windows in which multiple departments overlap;
- reversal mechanics: a procedure is lawfully denied; the denial triggers another required process; a security restriction creates a mandatory witness trail; the director's defensive cancellation opens a higher-level audit;
- climax mechanic: the crew synchronizes several legitimate institutional processes so the director must either allow the incriminating evidence into public view or openly violate rules in front of witnesses;
- scene families: procedural reconnaissance, role-specific lawful requests, timing rehearsals, bureaucratic reversals, multi-department final operation;
- evidence gaps: institution-specific policies need downstream research.

## Candidate C — The Honest Con

**Core answer:** The crew builds a temporary exhibition made entirely from true labels, authentic reproductions, public records, and carefully sequenced guided statements. Every component is literally accurate, but the arrangement makes the director's fraud legible to the audience before he can dismantle the exhibit.

**Central engine**

- want: make the public infer the director's corruption from a sequence of individually truthful statements and permitted materials;
- resistance: curatorial approval, the risk that truthful fragments remain innocuous in isolation, the director's power to interrupt the exhibition, and the no-lying rule forbidding deceptive claims;
- conflict: the crew must control order, context, and attention without making any false statement or removing any original object;
- stakes: if the audience does not reach the intended inference before shutdown, the director can dismiss each fact as harmless context;
- change: the crew shifts from concealment/deception toward truthful dramaturgy as the operative mechanism.

**Causal profile**

- primary strategy: engineer audience inference by sequencing verified truths in a live exhibition under hostile oversight;
- causal owner: crew control of truthful context/attention versus director control of curatorial interruption;
- external action pattern: research, design sequence, secure permissions, rehearse literal wording, route audience attention, defend exhibit in real time;
- pressure system: semantic precision, limited exhibit duration, curatorial monitoring, and the need for the audience to connect facts without a false assertion;
- reversal mechanics: a planned label is forbidden; the crew substitutes a different true artifact/context; the director's correction adds a fact that strengthens the inference; an audience question forces an unscripted but truthful answer;
- climax mechanic: a live guided sequence makes the corruption undeniable through cumulative truthful context as the director attempts to shut the event down;
- scene families: semantic rehearsal, exhibit assembly, permission games, audience-routing operation, live verbal duel during shutdown;
- evidence gaps: exact permissible reproductions/labels depend on museum policy.

## F3-style pairwise causal assessment

- A / B: `distinct` — A's decisive machinery is proof of disputed provenance through cascading authentication; B's is interaction among institutional procedures and lawful access triggers.
- A / C: `distinct` — A wins by establishing ownership/provenance facts; C wins by controlling the order/context in which already-true facts are perceived.
- B / C: `distinct` — B repeatedly manipulates procedures and departmental dependencies; C repeatedly engineers truthful communication and audience inference.

**F3-style set status:** `qualified`

## Producer intent-aware recommendation

**Recommended:** Candidate A — Provenance Cascade.

**Rationale:** The brief asks for procedural cleverness under institutional pressure while making both prohibitions productive. Candidate A preserves heist coordination and gives the museum's contested objects/provenance a causal role rather than merely using the institution as a bureaucracy or stage. Its layered structure can also absorb procedural and exhibition mechanisms without changing the governing objective.

**Why not B:** B delivers strong procedural cleverness and active coordination, but the objects themselves can become incidental; the victory risks reading as an audit trap whose museum setting is substitutable.

**Why not C:** C makes the no-lying restriction unusually active and theatrical, but the operation centers on audience inference. Without careful grounding it can feel like a semantic loophole rather than a heist whose objective is structurally tied to museum ownership.

## F4-style craft impact: B relative to A

- craft layers changed: causal_strategy, external_action, pressure_system, scene_families, story_texture;
- causal ownership shift: from evidentiary provenance chains to interlocking institutional procedures;
- external action shift: add filings, appointments, audits, compliance triggers; de-emphasize object-specific authentication;
- scene-family shift: more bureaucracy-as-machinery scenes, fewer provenance/research confrontations;
- pressure/texture shift: the story becomes more procedural/legal and less object-centered;
- reader-experience shift: delighted cleverness is preserved, with more pleasure coming from rule interaction than evidence revelation;
- thematic effect: institutions can be defeated by the consistency of their own rules;
- gain: strong clockwork heist logistics without theft or lies;
- give up: some of the museum-specific moral argument about who owns cultural objects;
- composability: `compatible_as_secondary`;
- composition note: procedural triggers can create the access windows that allow A's provenance evidence to be authenticated and revealed;
- primary risk: procedural obstacles become the actual objective and demote provenance to payload.

## F4-style craft impact: C relative to A

- craft layers changed: causal_strategy, external_action, scene_families, story_texture, reader_experience, theme;
- causal ownership shift: adds audience interpretation as an active part of the causal chain;
- external action shift: add wording rehearsal, exhibit sequencing, attention routing, live questioning;
- scene-family shift: more performance/social-engineering scenes layered onto evidence gathering;
- pressure/texture shift: procedural thriller gains theatrical wit and semantic tension;
- reader-experience shift: delighted cleverness can be strengthened if truthful staging is one operation layer rather than the sole trick;
- thematic effect: truth can be strategically arranged without becoming falsehood;
- gain: makes the no-lying constraint visible at scene level;
- give up: some directness of proving provenance if the audience-inference trick becomes the point;
- composability: `compatible_as_secondary`;
- composition note: use the honest exhibition as A's public delivery mechanism after the crew has established the provenance chain;
- primary risk: the story collapses into a word-game con where material museum evidence is secondary.

---

# H04 — The Missing Room

## Exact declared brief

```yaml
premise: A family inherits a house that becomes one room smaller every night.
story_type:
  genre: horror
  target_audience: adult
target_experience:
  primary_emotional_promise: intimate dread as physical compression forces avoided family truths into the open
architecture_preferences:
  complexity: layered
  causal_distribution: layered
  engine_hierarchy: primary_with_layers
hard_constraints:
  - The shrinking house must remain an active causal mechanism throughout the story.
  - The family conflict must not become merely backstory for an unrelated monster or containment plot.
```

## Candidate A — Rooms of Avoidance

**Core answer:** The house removes spaces the family uses to keep specific conflicts compartmentalized. Each disappearance eliminates a physical strategy of avoidance—locked bedroom, separate dining routine, private study—until the family has nowhere left to store incompatible versions of its past.

**Central engine**

- want: understand the rule governing the disappearing rooms and stop the house from erasing their remaining living space;
- resistance: each family member depends on a different room/ritual to avoid a painful truth, and admitting the connection threatens relationships before it appears to help;
- conflict: preserving the house requires abandoning the very patterns of separation the family uses to remain functional;
- stakes: continued avoidance literally compresses them toward one final room while emotional confrontation may destroy the family before the house does;
- change: family members learn to hold shared painful truth without needing architecture to keep their versions apart.

**Causal profile**

- primary strategy: infer which avoidance pattern each vanished room embodied and deliberately confront the corresponding family truth before the next loss;
- causal owner: family choices/avoidance patterns interacting with the supernatural house;
- external action pattern: map, compare, occupy forbidden spaces, recover objects, confront, test the house's rule, change household behavior;
- pressure system: nightly irreversible spatial loss plus relational escalation when a room's emotional function is named;
- reversal mechanics: confronting the obvious secret fails to save a room; an apparently neutral room disappears because of a subtler avoidance pattern; a truthful confrontation changes the order/rule of disappearance without restoring lost space;
- climax mechanic: in the final shared space the family addresses the central buried harm without retreating into separate rooms/roles, determining whether the last room remains;
- scene families: morning floor-plan shock, room/object recovery, family argument tied to space, rule-testing overnight vigil, final compressed confrontation;
- evidence gaps: exact supernatural ontology remains intentionally unexplained unless downstream design chooses otherwise.

## Candidate B — The Erased Inheritance

**Core answer:** Every vanished room corresponds to a relative deliberately removed from the family's inheritance story. The current heirs must reconstruct excluded branches of the family and restore their claims/names before the house deletes the physical space built from those exclusions.

**Central engine**

- want: identify why rooms vanish in a specific sequence and what each missing space says about the inheritance;
- resistance: falsified family records, living relatives who benefited from exclusions, shame around past acts, and the house destroying evidence as rooms disappear;
- conflict: solving the supernatural pattern forces the current family to decide whether preserving their inheritance is worth restoring people the family intentionally erased;
- stakes: the house and inheritance contract toward nothing while the family may lose property/status by correcting the record;
- change: the heirs move from treating inheritance as possession to treating it as an account of whom the family chose to recognize.

**Causal profile**

- primary strategy: connect vanished architecture to erased relatives through records, objects, interviews, and restitution decisions;
- causal owner: heirs' historical investigation opposed by inherited secrecy and present beneficiaries of exclusion;
- external action pattern: inventory, research, interview, trace ownership, contact estranged relatives, restore names/claims, test correlations with room loss;
- pressure system: nightly loss destroys evidence and living relatives resist reopening ownership/moral claims;
- reversal mechanics: a room linked to an apparently honored ancestor vanishes; records reveal a beneficiary helped erase someone else; restoring a name changes but does not stop the next disappearance because material restitution is also required;
- climax mechanic: the heirs publicly/legalistically restore the central excluded relative's place in the inheritance at direct cost to themselves as the last threatened room begins to vanish;
- scene families: architectural genealogy mapping, document discovery, estranged-relative visits, inheritance disputes, restitution climax;
- evidence gaps: legal effect of restitution and exact house genealogy need structure research.

## Candidate C — Borrowed Rooms

**Core answer:** The rooms do not cease to exist; each appears overnight inside the home of an estranged family member connected to the conflict that room once contained. The heirs must physically follow the migrating architecture through the family's fractured network and decide whether to reconnect relationships the house is forcing into contact.

**Central engine**

- want: find where the missing rooms are going and prevent the inherited house from becoming uninhabitable;
- resistance: estranged relatives refuse access, each transplanted room exposes a different unresolved relationship, and moving rooms destabilize both houses;
- conflict: recovering or stabilizing space requires entering other people's homes and conflicts rather than controlling the inheritance from one location;
- stakes: the central house shrinks while the family network is physically invaded by rooms carrying old objects/secrets;
- change: the heirs stop imagining family conflict as something safely contained in one inherited house and accept that unresolved relationships already span multiple homes/lives.

**Causal profile**

- primary strategy: trace transplanted rooms across estranged relatives and resolve the relationship each transfer makes materially unavoidable;
- causal owner: the house's spatial transfers plus the extended family's choices about access/reconciliation;
- external action pattern: track, travel, negotiate entry, inspect transplanted rooms, recover/share objects, confront estranged relatives, test transfer conditions;
- pressure system: continued shrinkage at home, invasive room arrivals elsewhere, and escalating relational boundaries around entering other households;
- reversal mechanics: a missing room is found intact elsewhere; attempting to move its contents triggers another transfer; a relative thought unrelated receives the room that contains the core family secret;
- climax mechanic: the final room spans/joins two estranged households, forcing a collective decision about whether the inherited home can remain a single family's exclusive possession;
- scene families: impossible room discovery in another house, tense home-entry negotiations, object/secret confrontations, spatial-transfer tests, multi-house climax;
- evidence gaps: physical rules for room transplantation require later specification.

## F3-style pairwise causal assessment

- A / B: `distinct` — A repeatedly tests present avoidance patterns through domestic confrontation; B repeatedly performs historical/genealogical investigation and restitution.
- A / C: `distinct` — A compresses one household toward direct confrontation; C expands action across estranged households through migrating architecture and negotiation/access scenes.
- B / C: `distinct` — B's decisive machinery is erased lineage/property recognition; C's is spatial transfer across living family relationships.

**F3-style set status:** `qualified`

## Producer intent-aware recommendation

**Recommended:** Candidate A — Rooms of Avoidance.

**Rationale:** The declared promise explicitly centers intimate dread as physical compression forces avoided family truths into the open. Candidate A makes the shrinking mechanism and avoidance behavior one causal engine, preserving one governing center while allowing historical or extended-family layers as subordinate complications.

**Why not B:** B keeps family conflict and the house causally linked, but the repeated action pattern becomes historical investigation and restitution. The emotional center shifts from present avoidance under compression toward inherited injustice and discovery.

**Why not C:** C makes disappearing rooms highly active and relational, but it externalizes the pressure into travel, access, and a network of households. The original single-house compression becomes less dominant as the story spatially expands.

## F4-style craft impact: B relative to A

- craft layers changed: causal_strategy, causal_ownership, external_action, scene_families, story_texture, reader_experience, theme;
- causal ownership shift: from present household avoidance to historical family exclusions and living beneficiaries;
- external action shift: add genealogy, documents, estranged-relative contact, restitution decisions; de-emphasize repeated rule-testing through present household behavior;
- scene-family shift: more investigative/historical scenes, fewer compressed domestic confrontations;
- pressure/texture shift: intimate dread gains inheritance mystery and moral history;
- reader-experience shift: dread remains, but reconstructive discovery competes with the immediate feeling of being physically cornered into truth;
- thematic effect: who counts as family and who gets erased from property/history;
- gain: deeper intergenerational stakes and material consequences for truth-telling;
- give up: some immediacy of present-tense relational compression;
- composability: `compatible_as_secondary`;
- composition note: an erased relative can be the buried harm represented by one or two key rooms while A's governing rule remains present avoidance;
- primary risk: genealogy becomes the puzzle that explains every disappearance, displacing the behavior-based engine.

## F4-style craft impact: C relative to A

- craft layers changed: causal_strategy, external_action, pressure_system, scene_families, story_texture;
- causal ownership shift: extends causal ownership from one household to an estranged family network;
- external action shift: add tracking, travel, access negotiation, multi-house confrontation; de-emphasize staying trapped together in shrinking space;
- scene-family shift: impossible-room discoveries in other houses replace some single-location compression scenes;
- pressure/texture shift: claustrophobic domestic horror becomes uncanny relational invasion with wider spatial movement;
- reader-experience shift: intimate dread is threatened if leaving the house repeatedly provides relief from compression;
- thematic effect: unresolved family conflict cannot be contained by property boundaries;
- gain: vivid spatial escalation and use of estranged relatives as active causal participants;
- give up: concentration and literal claustrophobia;
- composability: `requires_reframing`;
- composition note: one disappeared room appearing briefly with an estranged relative could reveal a relational dependency, but repeated migration would become a second primary supernatural rule;
- primary risk: the story stops feeling like one house becoming inescapably smaller.

---

# H05 — What She Saves

## Exact declared brief

```yaml
premise: The protagonist must never learn that her brother caused the disaster; the reader knows by the midpoint, and her external goal still resolves.
story_type:
  genre: literary
  target_audience: adult
target_experience:
  primary_emotional_promise: painful dramatic irony that resolves into earned but incomplete agency
  secondary_palette:
    - dread
    - compassion
    - bittersweet relief
architecture_preferences:
  complexity: maximalist
  causal_distribution: mixed
  engine_hierarchy: primary_with_layers
hard_constraints:
  - The brother caused the disaster.
  - The protagonist never learns that her brother caused the disaster.
  - The reader knows the brother's responsibility by the midpoint.
  - The protagonist's external goal resolves through her own consequential choices.
```

## Candidate A — What She Saves

**Core answer:** The protagonist spends the story repairing the disaster's continuing consequences while working from an incomplete but actionable account of its cause. Her competence and ethical choices genuinely resolve the external crisis; the reader simultaneously knows that the private story she carries about the disaster will never become complete.

**Central engine**

- want: repair the disaster's ongoing damage and protect the people still affected by it;
- resistance: cascading consequences, limited resources, community distrust, and incorrect assumptions about the original cause that are useful enough to act on but emotionally misleading;
- conflict: she must become capable enough to solve the present problem without receiving the revelation that would normally reorganize her family history;
- stakes: failure harms people now, while success may cement a personally incomplete explanation of the past;
- change: she develops earned agency and responsibility based on what she can know, not on a final revelation about her brother.

**Causal profile**

- primary strategy: solve the disaster's present consequences through investigation, repair, coalition-building, and consequential choices available within the protagonist's knowledge;
- causal owner: protagonist-led repair effort, with the hidden truth altering reader interpretation but not controlling her decisions;
- external action pattern: assess damage, choose priorities, coordinate people, repair systems/relationships, confront consequences, make irreversible tradeoffs;
- pressure system: worsening external consequences plus reader-known dramatic irony around the brother's hidden responsibility;
- reversal mechanics: a repair exposes deeper damage; an apparent clue about the cause leads to a useful but incomplete model; the brother's hidden action changes reader interpretation of a success without changing the protagonist's chosen goal;
- climax mechanic: the protagonist makes the decisive repair/sacrifice/coordination choice that resolves the external goal on the basis of her own values and knowledge;
- scene families: consequence triage, practical repair, community conflict, sibling scenes with double meaning for reader, final external resolution;
- evidence gaps: disaster domain and external repair mechanics remain premise-level unspecified.

## Candidate B — His Quiet Repair

**Core answer:** The brother, known by the reader to have caused the disaster, covertly repairs secondary harms and creates openings that the protagonist interprets as luck, community help, or the result of her own plan. Her external objective still resolves through her decisions, but the reader watches his concealed atonement run beneath her visible agency.

**Central engine**

- want: protagonist seeks to resolve the external damage; brother separately seeks to reduce the harm he caused without confessing;
- resistance: their efforts interfere, the brother cannot explain his knowledge without exposing himself, and his hidden interventions can distort the protagonist's understanding of what is possible;
- conflict: the protagonist must retain genuine causal ownership while the brother tries to atone without taking over the solution or revealing the truth;
- stakes: if his covert help becomes decisive, her agency is counterfeit; if he does nothing, preventable harms continue;
- change: the protagonist grows through her own choices while the brother confronts the moral limits of repair without confession.

**Causal profile**

- primary strategy: run two asymmetric action streams—visible protagonist-led resolution and covert brother-led mitigation—whose intersections create dramatic irony;
- causal owner: formally the protagonist for the external goal, with the brother as a concealed secondary causal actor;
- external action pattern: protagonist investigates/repairs/coordinates; brother covertly redirects resources, removes obstacles, and absorbs consequences;
- pressure system: the brother's need to help without revealing why, plus the risk his interventions displace the protagonist's causal ownership;
- reversal mechanics: a helpful intervention is misattributed; the protagonist rejects or undoes a covert shortcut; the brother must choose not to make the final decisive intervention even though he could;
- climax mechanic: the protagonist completes the external resolution herself while the brother's last meaningful act is to accept a subordinate/supporting role rather than secretly solve it;
- scene families: visible repair scenes, covert parallel-action scenes, sibling encounters with reader-only meaning, near-discovery moments, protagonist-owned climax;
- evidence gaps: exact boundaries of acceptable covert help require downstream structure calibration.

## Candidate C — The Official Cause

**Core answer:** An institution supplies the protagonist with a false but operationally useful explanation of the disaster while protecting her brother. She uses the partial model to solve the external crisis, while the reader knows both the brother's guilt and the institutional decision to preserve her ignorance.

**Central engine**

- want: solve the external problem using the best explanation and resources available to her;
- resistance: institutional secrecy, gaps in the official account, practical consequences that do not perfectly match the model, and officials who need her competent but not fully informed;
- conflict: she must decide how much to trust an explanation that works operationally even as inconsistencies accumulate that she can never trace to her brother's guilt;
- stakes: rejecting the official model entirely can jeopardize the repair; accepting it uncritically leaves other institutional harms unchallenged;
- change: she becomes capable of acting under epistemic uncertainty and demanding accountable process even without learning the private truth withheld from her.

**Causal profile**

- primary strategy: use and stress-test an incomplete official causal model to resolve present consequences while challenging institutional decisions that remain visible to her;
- causal owner: protagonist-led problem solving opposed/conditioned by institutional information control;
- external action pattern: analyze reports, test predictions, negotiate access/resources, identify model failures, force procedural concessions, execute repair plan;
- pressure system: a model that is useful enough to trust but incomplete enough to mislead, plus institutional incentives to preserve the cover story;
- reversal mechanics: the official model correctly predicts one failure; another consequence exposes a gap; an institutional obstruction is revealed as deliberate even though the brother's role remains hidden;
- climax mechanic: the protagonist resolves the external goal by adapting beyond the official model and forces an institutional change she can justify without discovering her brother's responsibility;
- scene families: report/model analysis, practical tests, institutional negotiation, unexplained sibling subtext, adaptive final operation;
- evidence gaps: institutional identity and exact false explanation need later design.

## F3-style pairwise causal assessment

- A / B: `distinct` — A keeps the brother causally secondary to a single protagonist repair engine; B deliberately runs a second covert action stream whose intersections generate much of the dramatic mechanism.
- A / C: `distinct` — A's opposition is consequences and incomplete personal understanding; C repeatedly contests an institutionally controlled but operational causal model.
- B / C: `distinct` — B's secondary causal actor is the brother's covert atonement; C's is institutional information management/procedure.

**F3-style set status:** `qualified`

## Producer intent-aware recommendation

**Recommended:** Candidate A — What She Saves.

**Rationale:** The brief's unusual hard constraint is that the protagonist must achieve meaningful external resolution without the truth that would conventionally anchor the emotional climax. Candidate A makes that absence the governing architecture: her agency is real, the reader's knowledge changes interpretation, and the brother's guilt never becomes the causal prerequisite for her success.

**Why not B:** B strongly exploits the reader-only knowledge and the maximalist/mixed preference, but a second covert action stream gives the brother more causal gravity. It requires careful subordination to avoid making her success depend on invisible assistance.

**Why not C:** C gives the incomplete knowledge a concrete mechanism and creates institutional pressure, but the story can shift toward information-control politics. The sibling asymmetry risks becoming merely the secret protected by a larger institutional plot.

## F4-style craft impact: B relative to A

- craft layers changed: causal_ownership, external_action, scene_families, pressure_system, reader_experience, theme;
- causal ownership shift: adds the brother as a persistent secondary causal actor beneath the protagonist's visible engine;
- external action shift: add covert mitigation, hidden resource movement, obstacle removal, and parallel consequences;
- scene-family shift: more reader-only parallel scenes and near-intersections with the protagonist's work;
- pressure/texture shift: dramatic irony becomes more active and suspenseful because the brother's choices can affect her path;
- reader-experience shift: dread/compassion intensify; earned agency is threatened if his contributions become necessary to her final success;
- thematic effect: whether atonement without confession can be morally meaningful;
- gain: richer mixed causation and a more active brother arc;
- give up: causal simplicity and some certainty that the protagonist fully owns her success;
- composability: `compatible_as_secondary`;
- composition note: the brother may quietly mitigate collateral harm or remove one non-decisive obstacle, but he must not provide the plan, key insight, indispensable resource, or final action that resolves her goal;
- primary risk: invisible assistance retroactively cheapens the protagonist's earned agency.

## F4-style craft impact: C relative to A

- craft layers changed: causal_ownership, external_action, pressure_system, scene_families, story_texture, theme;
- causal ownership shift: adds an institution as the active controller of the protagonist's causal model;
- external action shift: add report testing, access negotiation, procedural confrontation, model revision;
- scene-family shift: more institutional/process scenes around the practical repair engine;
- pressure/texture shift: intimate dramatic irony gains epistemic and political pressure;
- reader-experience shift: agency can remain earned, but compassion/dread may diffuse if the institution becomes a more salient antagonist than the brother's hidden guilt;
- thematic effect: action and responsibility under incomplete but useful knowledge;
- gain: a robust reason the protagonist never discovers the truth and a second causal layer compatible with mixed architecture;
- give up: some intimacy of a family secret existing without a formal concealment machine;
- composability: `compatible_as_secondary`;
- composition note: an institution may provide the incomplete working model and create obstacles, while the protagonist's own repair choices remain the primary engine and the brother remains the reader-known source of the original disaster;
- primary risk: the cover-up becomes the real plot and shifts the climax toward exposing the institution.

---

# H06 — Fixed Point

## Exact declared brief

```yaml
premise: History cannot be changed; a time traveler can only change what the trip means to people who remember it.
story_type:
  genre: sci_fi
  target_audience: adult
target_experience:
  primary_emotional_promise: grief transformed into consequential responsibility without undoing loss
architecture_preferences:
  complexity: layered
  causal_distribution: layered
  engine_hierarchy: primary_with_layers
hard_constraints:
  - No trip changes any historical event or outcome.
  - The protagonist must still make consequential choices in the present.
  - Time travel must remain necessary to the story rather than replaceable by ordinary archival research.
```

## Candidate A — Witness Chain

**Core answer:** The traveler repeatedly witnesses an unchangeable public tragedy to recover testimony that was never preserved. She cannot alter what happens, but she can carry firsthand context into the present and decide what obligations institutions and descendants inherit from finally knowing it.

**Central engine**

- want: recover testimony/context from the fixed tragedy that the present lacks and decide what to do with it;
- resistance: the event cannot be changed, witnesses do not all understand what is happening, present institutions dispute the meaning of recovered testimony, and each trip deepens the traveler's grief;
- conflict: she must abandon intervention as the measure of agency and build consequential present action from knowledge that arrives too late to save anyone in the past;
- stakes: the dead remain dead either way, but the present may continue policies, relationships, or injustices built on a false understanding of what happened;
- change: she redefines agency as faithful witness plus present responsibility rather than control over outcomes.

**Causal profile**

- primary strategy: use time travel to collect irrecoverable firsthand testimony/context, then translate it into present-day decisions and accountability;
- causal owner: traveler-led witnessing and present advocacy, opposed by fixed history and present institutions/people invested in existing interpretations;
- external action pattern: travel, observe, interview within fixed events, compare accounts, preserve testimony, persuade, organize present action;
- pressure system: inability to intervene, incomplete witness perspectives, emotional repetition of tragedy, and present resistance to new meaning;
- reversal mechanics: a witness contradicts the canonical account; a later trip recontextualizes an earlier testimony without changing it; present actors weaponize or reject the recovered evidence;
- climax mechanic: the traveler makes a consequential present-day choice—release, restitution, memorial action, institutional challenge—based on testimony she could obtain only by being there;
- scene families: fixed-event witness encounters, repeated-location recontextualization, archive comparison, present debate, consequential present action;
- evidence gaps: exact tragedy and time-travel access rules remain unspecified.

## Candidate B — The Same Goodbye

**Core answer:** The traveler returns to the fixed final days of one loved person. Every visit has always happened and nothing about the death changes. What changes in the present is how surviving people understand remembered conversations once the traveler can supply context from different moments around the same goodbye.

**Central engine**

- want: understand the loved person's final choices and help surviving relationships live with an unchangeable death;
- resistance: fixed outcomes, emotionally contradictory memories, the temptation to treat one more visit as a chance to intervene, and survivors who need different meanings from the same facts;
- conflict: the traveler must use repeated fixed encounters to understand rather than rewrite the goodbye, then decide what she owes living people with that understanding;
- stakes: she cannot save the dead person, but she can either perpetuate a damaging family interpretation or help survivors carry the loss differently;
- change: she relinquishes the fantasy that love is proven by prevention and learns to act through attention, interpretation, and present relationship repair.

**Causal profile**

- primary strategy: revisit fixed conversations around one death to gather context, then mediate present relationships through a more complete understanding;
- causal owner: traveler-led interpretation and present relational action;
- external action pattern: revisit, listen, ask bounded questions, compare remembered conversations, speak with survivors, repair/renegotiate relationships;
- pressure system: emotional recurrence, fixed death, incompatible survivor memories, and the traveler's temptation to seek one final intervention loophole;
- reversal mechanics: a familiar conversation means something different in context; another survivor remembers the same words differently; the traveler discovers that a painful statement was protecting someone rather than rejecting them;
- climax mechanic: she chooses a consequential present relational action—reconciliation, truth-telling, boundary, memorial commitment—without changing the death;
- scene families: repeated goodbye scenes, memory comparison, survivor conversations, grief-triggered return trips, present relational climax;
- evidence gaps: time-travel mechanism and degree of interaction permitted within fixed history.

## Candidate C — Annotations

**Core answer:** The traveler builds a public archive from details only direct temporal observation can recover: context around disputed decisions, voices omitted from surviving records, and physical facts no document preserved. The past never changes; the present's official history does, creating fights over education, restitution, and policy.

**Central engine**

- want: create an evidentiary archive that corrects what the present believes about fixed historical events;
- resistance: fragmentary access windows, the need to authenticate observations that have no surviving source, institutional gatekeepers, and communities with conflicting stakes in the historical narrative;
- conflict: she must turn unrepeatable temporal witnessing into a trustworthy public record without claiming the authority to rewrite the past itself;
- stakes: false history continues shaping present institutions if the archive fails; mishandled evidence can convert witness into another form of narrative domination;
- change: she moves from possessing privileged knowledge to building accountable systems for how that knowledge is preserved and used.

**Causal profile**

- primary strategy: collect otherwise unavailable temporal observations, authenticate/corroborate them where possible, and build a contested present-day archive that drives policy/public decisions;
- causal owner: traveler plus archival collaborators opposed by institutional/historical gatekeepers;
- external action pattern: travel, document, corroborate, catalog, authenticate, publish, defend archive, negotiate institutional response;
- pressure system: unverifiable firsthand evidence, incomplete access, public controversy, and the ethical power of controlling historical context;
- reversal mechanics: a temporal observation invalidates a famous document's interpretation; authentication fails for a true observation; an omitted voice changes the meaning of an accepted event without changing the event itself;
- climax mechanic: the archive is used in a consequential present institution/policy/restitution decision while the traveler accepts limits on her own interpretive authority;
- scene families: observational trips, evidence-corroboration labs/archives, editorial disputes, public challenges, institutional decision climax;
- evidence gaps: authentication method for time-travel observation and exact institutional stakes.

## F3-style pairwise causal assessment

- A / B: `distinct` — A gathers distributed testimony around a public tragedy and converts it into institutional/social responsibility; B repeatedly revisits one intimate death and converts context into relationship repair.
- A / C: `distinct` — A is witness/testimony plus advocacy; C is evidence collection, authentication, archival publication and institutional historical contest.
- B / C: `distinct` — B's governing action is intimate relational interpretation; C's is public knowledge-system construction and institutional response.

**F3-style set status:** `qualified`

## Producer intent-aware recommendation

**Recommended:** Candidate A — Witness Chain.

**Rationale:** The target promise asks for grief transformed into consequential responsibility without undoing loss. Candidate A makes the fixed-history constraint active in every trip while giving the protagonist a clear present-day action chain: witness what cannot be recovered otherwise, carry it forward, and accept obligations created by knowing. The witness engine can hold intimate and institutional layers without either replacing the primary rule.

**Why not B:** B realizes grief most directly and preserves the fixed death, but it narrows the premise toward one relationship. Consequential responsibility can become primarily emotional/relational rather than a broader answer to what agency means when history cannot change.

**Why not C:** C gives the protagonist substantial present-day action and makes time travel indispensable to evidence collection, but the dominant texture becomes archival authentication and public-history contest. Grief risks becoming motivation/background for an epistemic institution story.

## F4-style craft impact: B relative to A

- craft layers changed: causal_strategy, causal_ownership, external_action, scene_families, story_texture, reader_experience, theme;
- causal ownership shift: from distributed witnesses/present institutions to the traveler and a small survivor relationship network;
- external action shift: emphasize repeated conversations, memory comparison, reconciliation/boundary choices; de-emphasize public testimony transfer and institutional action;
- scene-family shift: more recurring intimate goodbye scenes, fewer public witness/accountability scenes;
- pressure/texture shift: philosophical/history pressure becomes concentrated grief and relational recurrence;
- reader-experience shift: grief is intensified; consequential responsibility becomes more intimate and may feel smaller in scale without careful present consequences;
- thematic effect: love and agency after irreversible loss;
- gain: emotional concentration and recurring scene resonance;
- give up: breadth of the premise's implications for history, witness, and collective responsibility;
- composability: `compatible_as_secondary`;
- composition note: one key witness relationship or repeated goodbye can personalize A's broader testimony mission while the governing objective remains carrying irrecoverable testimony into consequential present action;
- primary risk: the loved one's death becomes the only real reason for time travel and converts the story into a private grief loop.

## F4-style craft impact: C relative to A

- craft layers changed: causal_ownership, external_action, pressure_system, scene_families, story_texture, theme;
- causal ownership shift: adds archival collaborators and institutions as persistent causal actors;
- external action shift: add documentation standards, corroboration, authentication, publication, policy dispute;
- scene-family shift: more archive/lab/editorial/public-contest scenes layered after or between witness trips;
- pressure/texture shift: grief/witness texture gains procedural epistemic pressure;
- reader-experience shift: responsibility becomes more concrete and public, but grief can be weakened if evidence mechanics dominate;
- thematic effect: who has authority to preserve and interpret fixed history;
- gain: a strong mechanism connecting time travel to present institutional consequence;
- give up: some immediacy of human witness and moral encounter;
- composability: `compatible_as_secondary`;
- composition note: A's recovered testimony can require a bounded authentication/archive layer before it can responsibly drive present action;
- primary risk: the archive becomes the governing engine and turns witness scenes into raw-data acquisition.

---

# Producer freeze boundary

This document ends the H2 producer role.

H3 must not revise these candidate directions, causal profiles, pairwise classifications, recommendations, rejected reasons, or craft/composition notes in place. If a factual/contract defect is discovered before adjudication, create a separately versioned corrected producer packet and record why the first packet was invalid rather than silently editing reviewed evidence.

No canonical StoryIdentity was accepted or created by this producer pass.
