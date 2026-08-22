# Phase H — H3 Context-Reduced Evaluator Packet

## Evidence status

This is the H3 evaluator input derived from the frozen H2 producer packet at `docs/research/story-discovery-phase-h-agent-producer.md` on baseline `67246a9f2919fd3c545410a2f244ece42800ef55`.

The reduction is intentionally asymmetric:

- preserve each exact declared brief;
- preserve candidate core-answer content and causal-profile evidence;
- remove original candidate letters, titles, order significance, producer provenance, recommendation, rejected-candidate reasons, F3 pairwise classifications, F3 set status, and F4 craft/composability judgments from the **initial selection pass**;
- reorder candidates and replace traceability labels with opaque per-case aliases;
- do not use alias, position, length, or amount of prose as a quality signal.

After the evaluator records an independent preference and causal/profile assessment for a case, the frozen H2 recommendation, rejected reasons, and F4 notes may be revealed for the second-stage recommendation/fairness/craft-teaching review. They must not retroactively change the first-stage preference.

This is **context-reduced, not blind**. The same model family produced H2 and performs H3, and the broader conversation may contain earlier Phase H context. Artifact-level cue removal reduces obvious self-confirmation pressure but does not establish statistical or human independence.

---

## E01

### Declared brief

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

### direction_v5

Core answer: The chatter is an illicit rebroadcast assembled from mission-control channels removed from the official record. Someone is forcing the protagonist to hear evidence that mission leadership knowingly sacrificed part of her crew. She reconstructs the institutional decision and decides what to do with the truth.

Causal profile:
- primary strategy: trace suppressed communication records, identify the anonymous rebroadcaster, and assemble a public evidentiary case against mission leadership;
- causal owner: the protagonist's institutional investigation, opposed by surviving mission leadership;
- external action pattern: authenticate, trace, interview, obtain records, confront officials, prepare disclosure;
- pressure system: secrecy rules, institutional counterpressure, reputational risk, and uncertainty about the transmitter's motives;
- reversals: supposedly fabricated traffic authenticates; the source has a personal stake; evidence expands responsibility from one actor to an institutional policy;
- climax: use the reconstructed hidden-channel sequence to force an institutional reckoning;
- scene families: audio authentication, classified-record pursuit, former-colleague confrontation, institutional pressure, public evidence presentation;
- evidence gap: the initial rebroadcaster's identity/delivery mechanism remains open.

### direction_q7

Core answer: The impossible chatter is a fragmented retransmission of the protagonist's final mission, but the fragments contradict the version of the disaster she has lived with for years. She investigates to reconstruct what she chose, what she failed to hear, and why memory protected her from it.

Causal profile:
- primary strategy: reconstruct the failed mission by correlating impossible transmissions with archived telemetry, witness memory, and her own recollections;
- causal owner: the retired astronaut's investigation, with the signal supplying bounded new evidence;
- external action pattern: record, decode, cross-check, interview, revisit archived decisions, test competing reconstructions;
- pressure system: each fragment closes off a comforting explanation while the source remains physically impossible;
- reversals: a transmission contradicts remembered commands; another witness shifts apparent responsibility; the final sequence shows she heard enough to make a consequential choice;
- climax: reconstruct the complete final exchange and state what she actually chose rather than the version repeated for years;
- scene families: signal captures, archive reconstruction, former-crew conversations, memory-versus-record comparisons, final reconstruction;
- evidence gap: why the signal appears now remains open speculative physics.

### direction_m2

Core answer: The chatter comes from a survivor of the old mission caught in a relativistic/time-displaced communication window. The protagonist cannot return to flight, but her knowledge makes her the only person capable of coordinating a rescue from Earth before the window closes.

Causal profile:
- primary strategy: convert intermittent mission-control chatter into actionable rescue telemetry and coordinate present institutions around it;
- causal owner: the retired astronaut as technical coordinator, with agencies and the stranded survivor dependent on her interpretation;
- external action pattern: decode, calculate, persuade, assemble specialists, stage tests, coordinate timed rescue actions;
- pressure system: shrinking communication windows, institutional disbelief, technical obsolescence, and lack of command authority;
- reversals: the signal proves live; an old-data assumption fails; temporal conditions differ from what the rescue model assumed;
- climax: coordinate a precisely timed present intervention that makes the survivor reachable without the protagonist returning to space;
- scene families: signal-response experiments, technical planning, institutional persuasion, rescue rehearsal, timed coordination;
- evidence gap: exact communication-window physics.

---

## E02

### Declared brief

```yaml
premise: "A murder mystery in one elevator: six strangers, no supernatural explanation, and the killer never leaves the elevator."
story_type:
  genre: mystery
  target_audience: adult
target_experience:
  primary_emotional_promise: claustrophobic suspicion resolving into reconstructive relief
  secondary_palette: [dread, moral uncertainty]
  avoided_experiences: [supernatural awe]
architecture_preferences:
  complexity: maximalist
  causal_distribution: mixed
  engine_hierarchy: primary_with_layers
hard_constraints:
  - The killer never leaves the elevator.
  - The final solution is physically possible and retrospectively fair.
  - The sealed-space mechanics must materially matter to the solution.
```

### direction_t8

Core answer: The killer manipulates where passengers stand and when they shift position so the elevator's load and leveling sensors create a false record of when the victim was alive and where everyone could have been. The detective solves a choreography puzzle in which social behavior and machine readings form one alibi system.

Causal profile:
- primary strategy: reconstruct passenger choreography and sensor state to show how truthful machine readings were turned into a false timeline;
- causal owner: killer-designed choreography versus detective interpretation of objective system data;
- external action pattern: inspect sensor logs, weigh passengers/objects, reproduce positions, interrogate concealed movement, test configurations;
- pressure system: apparently objective exculpatory data plus social reasons passengers obscure exact positions;
- reversals: a record is true but its inferred meaning fails; a concealed movement is admitted; recreated weight distribution reveals the designed alibi;
- climax: recreate the exact configuration that generated the misleading machine record and isolate the killer's move;
- scene families: sensor analysis, weight experiments, position diagrams, concealed-movement interrogation, final choreography reenactment;
- evidence gap: exact sensor capabilities require technical research.

### direction_k3

Core answer: One passenger commits the murder during a mechanically possible stop, but several others independently conceal pieces of what they saw for separate reasons. The detective must solve both the physical act and the distributed concealment that makes it appear impossible.

Causal profile:
- primary strategy: decompose testimony into independent concealments, then combine recovered observations with elevator mechanics;
- causal owner: detective-led social decomposition opposed by distributed witness concealment and the killer's exploitation of it;
- external action pattern: interrogate, cross-compare omissions, expose private motives, map sightlines, reenact, reconstruct;
- pressure system: claustrophobic mistrust, morally ambiguous secrets, and a physical sequence obscured by social concealment;
- reversals: an apparent accomplice is merely hiding an unrelated act; another omission changes the timeline; a recovered observation makes the physical sequence possible;
- climax: separate every witness's reason for silence, then reconstruct the one physical act only the killer performed;
- scene families: testimony contradictions, private-secret reveals, sightline tests, group pressure, final social-plus-physical reconstruction;
- evidence gap: exact independent motives need downstream character design.

### direction_r4

Core answer: The killer stages an emergency stop that creates a short interval in which lights, body positions, door-control status, and passengers' assumptions about elapsed time diverge. The detective solves the case by reconstructing those hidden seconds from physical traces and conflicting perception.

Causal profile:
- primary strategy: reconstruct a physically exact second-by-second murder sequence from elevator mechanics, body positions, and testimony;
- causal owner: detective-led physical reconstruction opposed by the killer's staged timing illusion;
- external action pattern: measure, reenact, compare, test, eliminate positions, reconstruct sequence;
- pressure system: confinement, contradictory testimony, limited physical possibilities, and the assumption everyone saw the same event;
- reversals: a timing assumption fails; load/door data disproves a claimed position; reenactment reveals movement possible only during blackout;
- climax: a live reconstruction demonstrates the fair-play sequence and identifies the killer's unique opportunity;
- scene families: testimony map, elevator-mechanism tests, body-position reenactments, clue reconciliation, final demonstration;
- evidence gap: exact murder method/tool remains a later structural choice.

---

## E03

### Declared brief

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

### direction_f2

Core answer: The crew builds a temporary exhibition made entirely from true labels, authentic reproductions, public records, and carefully sequenced guided statements. Every component is literally accurate, but the arrangement makes the director's fraud legible before he can dismantle the exhibit.

Causal profile:
- primary strategy: engineer audience inference by sequencing verified truths in a live exhibition under hostile oversight;
- causal owner: crew control of truthful context/attention versus director control of curatorial interruption;
- external action pattern: research, design sequence, secure permissions, rehearse literal wording, route attention, defend exhibit in real time;
- pressure system: semantic precision, limited exhibit duration, curatorial monitoring, and need for the audience to connect facts without false assertion;
- reversals: a label is forbidden and replaced with another true context; the director's correction strengthens the inference; an audience question forces an unscripted truthful answer;
- climax: a live guided sequence makes corruption undeniable through cumulative truthful context as the director tries to shut it down;
- scene families: semantic rehearsal, exhibit assembly, permission games, audience routing, live verbal duel;
- evidence gap: exact permissible reproductions/labels depend on policy.

### direction_n6

Core answer: The crew defeats the director by proving the true provenance of disputed objects through a timed chain of lawful access, live authentication, donor testimony, conservation evidence, and public claims. Nothing leaves the museum; the operation removes the director's ability to define legitimate ownership.

Causal profile:
- primary strategy: stage synchronized public provenance verification so multiple independent truths become mutually reinforcing and difficult to suppress;
- causal owner: crew coordination versus director control of access and interpretation;
- external action pattern: authenticate, schedule, disclose, cross-verify, trigger lawful access, coordinate witnesses, stage public reveal;
- pressure system: timed access windows, institutional countermeasures, donor/legal pressure, and truthfulness constraints;
- reversals: one provenance chain is blocked; another truthful disclosure forces an unplanned route; the director's rebuttal authenticates a hidden dependency;
- climax: multiple crew roles execute a timed public verification sequence in which every statement is true and the director loses institutional control without any object leaving;
- scene families: access planning, conservation verification, donor/witness coordination, public-event staging, cascading final reveal;
- evidence gap: exact legal ownership outcome depends on jurisdiction.

### direction_c9

Core answer: The crew turns lawful access rules, audit obligations, public-event logistics, insurance procedures, and donor restrictions into a heist architecture. They force the director to open systems he normally keeps separated, causing hidden evidence to become observable at one coordinated moment.

Causal profile:
- primary strategy: chain lawful procedural triggers so ordinary museum systems expose one another under deadline;
- causal owner: crew manipulation of institutional process versus director-controlled discretion;
- external action pattern: request, schedule, file, attend, trigger audits, coordinate access, exploit rule dependencies;
- pressure system: bureaucratic timing, cancellation risk, compliance requirements, and limited windows of departmental overlap;
- reversals: a process is lawfully denied and triggers another; a security restriction creates a witness trail; defensive cancellation opens a higher-level audit;
- climax: synchronize legitimate processes so the director must allow incriminating evidence into view or openly violate rules in front of witnesses;
- scene families: procedural reconnaissance, lawful requests, timing rehearsals, bureaucratic reversals, multi-department final operation;
- evidence gap: institution-specific policies require research.

---

## E04

### Declared brief

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

### direction_s1

Core answer: Rooms do not cease to exist; each appears overnight inside the home of an estranged family member connected to the conflict that room contained. The heirs must follow migrating architecture through the fractured family network and decide whether to reconnect relationships the house forces into contact.

Causal profile:
- primary strategy: trace transplanted rooms across estranged relatives and resolve the relationship each transfer makes materially unavoidable;
- causal owner: spatial transfers plus extended-family choices about access/reconciliation;
- external action pattern: track, travel, negotiate entry, inspect transplanted rooms, recover/share objects, confront relatives, test transfer conditions;
- pressure system: continued shrinkage at home, invasive room arrivals elsewhere, and escalating relational boundaries;
- reversals: a missing room is found intact elsewhere; moving contents triggers another transfer; a seemingly unrelated relative receives the room containing the central secret;
- climax: the final room spans two estranged households, forcing a decision about whether the inherited home can remain exclusive property;
- scene families: impossible-room discoveries elsewhere, home-entry negotiation, object/secret confrontation, transfer tests, multi-house climax;
- evidence gap: physical transplantation rules require specification.

### direction_h8

Core answer: Every vanished room corresponds to a relative deliberately removed from the family's inheritance story. The heirs reconstruct excluded branches and restore claims/names before the house deletes the physical space built from those exclusions.

Causal profile:
- primary strategy: connect vanished architecture to erased relatives through records, objects, interviews, and restitution decisions;
- causal owner: heirs' historical investigation opposed by inherited secrecy and present beneficiaries;
- external action pattern: inventory, research, interview, trace ownership, contact estranged relatives, restore names/claims, test correlations;
- pressure system: nightly loss destroys evidence and living relatives resist reopening ownership/moral claims;
- reversals: a room linked to an apparently honored ancestor vanishes; a beneficiary helped erase someone else; restoring a name is insufficient without material restitution;
- climax: restore the central excluded relative's place in the inheritance at direct cost as the last threatened room begins to vanish;
- scene families: architectural-genealogy mapping, document discovery, estranged-relative visits, inheritance disputes, restitution climax;
- evidence gaps: legal effect of restitution and exact genealogy need research.

### direction_p5

Core answer: The house removes spaces the family uses to keep specific conflicts compartmentalized. Each disappearance eliminates a physical strategy of avoidance until the family has nowhere left to store incompatible versions of its past.

Causal profile:
- primary strategy: infer which avoidance pattern each vanished room embodied and deliberately confront the corresponding family truth before the next loss;
- causal owner: family choices/avoidance patterns interacting with the supernatural house;
- external action pattern: map, compare, occupy forbidden spaces, recover objects, confront, test the house's rule, change household behavior;
- pressure system: nightly irreversible spatial loss plus relational escalation when a room's emotional function is named;
- reversals: confronting the obvious secret fails; a neutral-looking room proves tied to subtler avoidance; truthful confrontation changes the disappearance pattern without restoring lost space;
- climax: in the final shared space, address the central buried harm without retreating into separate rooms/roles, determining whether the last room remains;
- scene families: floor-plan shock, room/object recovery, space-tied argument, overnight rule test, final compressed confrontation;
- evidence gap: supernatural ontology can remain unexplained.

---

## E05

### Declared brief

```yaml
premise: The protagonist must never learn that her brother caused the disaster; the reader knows by the midpoint, and her external goal still resolves.
story_type:
  genre: literary
  target_audience: adult
target_experience:
  primary_emotional_promise: painful dramatic irony that resolves into earned but incomplete agency
  secondary_palette: [dread, compassion, bittersweet relief]
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

### direction_j7

Core answer: The brother covertly repairs secondary harms and creates openings that the protagonist interprets as luck, community help, or the result of her own plan. Her objective still resolves through her decisions, but the reader watches his concealed atonement beneath her visible agency.

Causal profile:
- primary strategy: run two asymmetric action streams—visible protagonist-led resolution and covert brother-led mitigation—whose intersections create dramatic irony;
- causal owner: formally the protagonist for the external goal, with the brother as concealed secondary causal actor;
- external action pattern: protagonist investigates/repairs/coordinates; brother covertly redirects resources, removes obstacles, absorbs consequences;
- pressure system: the brother must help without revealing why, while his interventions risk displacing protagonist ownership;
- reversals: helpful intervention is misattributed; protagonist rejects or undoes a covert shortcut; brother must choose not to make the final decisive intervention;
- climax: protagonist completes the resolution herself while brother accepts a subordinate role rather than secretly solving it;
- scene families: visible repair, covert parallel action, sibling double-meaning, near-discovery, protagonist-owned climax;
- evidence gap: acceptable covert-help boundaries require careful calibration.

### direction_d2

Core answer: An institution supplies the protagonist a false but operationally useful explanation of the disaster while protecting her brother. She uses the partial model to solve the external crisis, while the reader knows both the brother's guilt and the institutional decision to preserve her ignorance.

Causal profile:
- primary strategy: use and stress-test an incomplete official causal model to resolve present consequences while challenging visible institutional decisions;
- causal owner: protagonist-led problem solving conditioned/opposed by institutional information control;
- external action pattern: analyze reports, test predictions, negotiate access/resources, identify model failures, force procedural concessions, execute repair plan;
- pressure system: a model useful enough to trust but incomplete enough to mislead, plus institutional incentives to preserve the cover story;
- reversals: the official model correctly predicts one failure; another consequence exposes a gap; an obstruction is revealed as deliberate without exposing the brother;
- climax: adapt beyond the official model, resolve the external goal, and force an institutional change justified without learning the private truth;
- scene families: report analysis, practical tests, institutional negotiation, sibling subtext, adaptive final operation;
- evidence gap: institutional identity and exact false explanation remain open.

### direction_w4

Core answer: The protagonist repairs the disaster's continuing consequences while working from an incomplete but actionable account of its cause. Her competence and ethical choices genuinely resolve the external crisis; the reader knows the private story she carries about the disaster will never become complete.

Causal profile:
- primary strategy: solve present consequences through investigation, repair, coalition-building, and consequential choices available within her knowledge;
- causal owner: protagonist-led repair effort, with hidden truth altering reader interpretation but not controlling her decisions;
- external action pattern: assess damage, choose priorities, coordinate people, repair systems/relationships, confront consequences, make irreversible tradeoffs;
- pressure system: worsening external consequences plus reader-known dramatic irony around the brother's hidden responsibility;
- reversals: a repair exposes deeper damage; an apparent cause clue yields a useful but incomplete model; the brother's hidden action changes reader interpretation of success without changing the protagonist's goal;
- climax: make the decisive repair/sacrifice/coordination choice on the basis of her own values and knowledge;
- scene families: consequence triage, practical repair, community conflict, sibling scenes with double meaning, final external resolution;
- evidence gap: disaster domain and repair mechanics remain unspecified.

---

## E06

### Declared brief

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

### direction_x6

Core answer: The traveler builds a public archive from details only direct temporal observation can recover: context around disputed decisions, omitted voices, and physical facts no document preserved. The past never changes; the present's official history does, creating fights over education, restitution, and policy.

Causal profile:
- primary strategy: collect otherwise unavailable temporal observations, authenticate/corroborate them where possible, and build a contested present-day archive that drives decisions;
- causal owner: traveler plus archival collaborators opposed by institutional/historical gatekeepers;
- external action pattern: travel, document, corroborate, catalog, authenticate, publish, defend archive, negotiate response;
- pressure system: unverifiable firsthand evidence, incomplete access, public controversy, and ethical power over historical context;
- reversals: an observation invalidates a famous document's interpretation; authentication fails for a true observation; an omitted voice changes meaning without changing events;
- climax: the archive is used in a consequential present policy/restitution decision while the traveler accepts limits on interpretive authority;
- scene families: observational trips, corroboration labs/archives, editorial disputes, public challenges, institutional decision climax;
- evidence gap: authentication method and exact institutional stakes.

### direction_l9

Core answer: The traveler repeatedly witnesses an unchangeable public tragedy to recover testimony that was never preserved. She cannot alter what happens, but carries firsthand context into the present and decides what obligations institutions and descendants inherit from finally knowing it.

Causal profile:
- primary strategy: use time travel to collect irrecoverable firsthand testimony/context, then translate it into present decisions and accountability;
- causal owner: traveler-led witnessing and present advocacy, opposed by fixed history and present actors invested in existing interpretations;
- external action pattern: travel, observe, interview within fixed events, compare accounts, preserve testimony, persuade, organize present action;
- pressure system: inability to intervene, incomplete perspectives, emotional repetition of tragedy, and present resistance to new meaning;
- reversals: a witness contradicts the canonical account; a later trip recontextualizes earlier testimony without changing it; present actors weaponize or reject evidence;
- climax: make a consequential present choice—release, restitution, memorial action, institutional challenge—based on testimony obtainable only by being there;
- scene families: fixed-event witness encounters, repeated-location recontextualization, archive comparison, present debate, consequential action;
- evidence gap: exact tragedy and access rules remain unspecified.

### direction_b4

Core answer: The traveler returns to the fixed final days of one loved person. Every visit has always happened and nothing about the death changes. What changes is how surviving people understand remembered conversations once the traveler supplies context from different moments around the same goodbye.

Causal profile:
- primary strategy: revisit fixed conversations around one death to gather context, then mediate present relationships through a more complete understanding;
- causal owner: traveler-led interpretation and present relational action;
- external action pattern: revisit, listen, ask bounded questions, compare remembered conversations, speak with survivors, repair/renegotiate relationships;
- pressure system: emotional recurrence, fixed death, incompatible memories, and temptation to seek an intervention loophole;
- reversals: a familiar conversation means something different in context; another survivor remembers the same words differently; a painful statement is re-understood as protection rather than rejection;
- climax: choose a consequential present relational action—reconciliation, truth-telling, boundary, memorial commitment—without changing the death;
- scene families: repeated goodbye scenes, memory comparison, survivor conversations, grief-triggered return trips, present relational climax;
- evidence gap: time-travel mechanism and degree of interaction permitted within fixed history.

---

## Initial-pass evaluator instruction

For each case, before consulting the frozen H2 recommendation/F4 material:

1. decide whether the three directions are causally distinct enough to compare;
2. check each causal profile against the direction as written and flag unsupported invention or missing mechanics;
3. identify the direction most defensible against the exact declared intent, or mark the case not adjudicable;
4. explain the strongest alternative fairly;
5. record uncertainties without converting them into numeric scores.

Only after those choices are fixed should the evaluator inspect the original H2 recommendation/rejected reasons/F4 notes and assess recommendation defensibility, craft-teaching usefulness, alternative fairness, authority semantics, and creative usefulness.