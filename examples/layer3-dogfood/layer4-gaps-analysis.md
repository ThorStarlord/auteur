# Layer 4 Gap Analysis: SceneOutline → Prose

**Date:** 2026-07-13  
**Analysis Method:** Examined 3 realistic Layer 3 dogfood scenes, analyzed what prose generation must invent beyond Layer 3 structure  
**Status:** Layer 4 scope clearly defined

---

## Executive Summary

Layer 3 (SceneOutline) successfully captures **narrative structure and dramatic action**, providing all information needed for story coherence. However, prose generation must invent substantial information about **voice, pacing, style, and presentation** that Layer 3 deliberately does not specify.

Layer 4 should own:
- **Prose voice & POV interiority** (how the character thinks, not just what they know)
- **Dialogue generation** (character speech, with knowledge/emotion constraints)
- **Pacing & rhythm** (how fast/slow the scene unfolds)
- **Sensory details** (what the POV character notices)
- **Prose style** (metaphor, literary devices, sentence structure)
- **Exposition method** (how entry-state knowledge becomes visible to reader)

---

## Scene Structure Provided (Layer 3)

### Dogfood Scenes Analyzed

| Scene | Chapter | Position | POV | Goal | Turn Type |
|-------|---------|----------|-----|------|-----------|
| scene_07_01 | 7 (Rising Action) | 1 | elena | enjoy evening, support Daniel | discovery |
| scene_13_02 | 13 (Midpoint) | 2 | elena | force Daniel to admit truth | revelation |
| scene_21_01 | 21 (Climax) | 1 | elena | verify Daniel's promise | reversal |

### What SceneOutline Reliably Provides

1. **POV character** (first-person perspective anchor)
2. **Goal** (what character wants to accomplish)
3. **Opposition** (what blocks the goal)
4. **Turn** (the pivotal discovery/reversal/decision)
5. **Decision** (character's choice in response)
6. **Outcome** (result: success/partial/failure)
7. **Entry state** (knowledge and emotions at scene start)
8. **Exit state** (knowledge and emotions at scene end)
9. **Participants** (who's present in scene)
10. **Story time** (when the scene occurs)
11. **Arc beat realization** (which narrative beats advance)
12. **Narrative continuity** (setups created, payoffs triggered)

**Assessment:** Layer 3 is comprehensive for structural integrity. All scenes passed validation; no information critical to narrative coherence is missing.

---

## What Prose Generation Invented (Should Be Layer 4)

### Pattern 1: Dialogue

**Layer 3 constraint:** None - only dramatic action structure  
**What prose generated:**
- Scene 1: No dialogue (pure internal observation)
- Scene 2: Full naturalistic dialogue with 4 exchange cycles
- Scene 3: Internal monologue only (no dialogue)

**Risk Level:** MEDIUM

**Why it matters:**
- Prose can invent dialogue that violates POV knowledge (character shouldn't speak facts they don't know yet)
- Dialogue must respect emotional state (angry Elena speaks differently than resigned Elena)
- Topic matter must align with narrative coherence (what can Daniel say? What must he never admit?)

**Example from analysis:**
```
Daniel: "Nothing physical has happened, Elena."
```
This specific phrase was invented by prose generation. Layer 3 says:
- Opposition: "daniel... refuses to cut contact"
- Outcome: "consequences: [daniel_realizes_discovery]"

But Layer 3 doesn't constrain *what words* Daniel uses to deny/defend himself.

**Layer 4 needs:**
- Dialogue tone rules per character (Daniel: deferent vs. defiant vs. negotiating)
- Knowledge boundary rules (character cannot speak facts they don't possess)
- Emotional constraints (angry character speaks shorter sentences, uses "I" more, etc.)
- Topic restrictions (some subjects must never be addressed in dialogue)

---

### Pattern 2: Descriptive Details

**Layer 3 constraint:** Only abstract location ("gallery," "apartment")  
**What prose generated:**
- "white walls" (gallery setting)
- "the black dress Daniel liked" (visual detail)
- "her fingers lingering longer than necessary" (body language)
- "across from Sylvia's apartment building" (external observation)

**Risk Level:** LOW

**Why it matters:**
- Sensory details add texture and emotional resonance
- Details should match the POV character's noticing pattern (analytical Elena vs. dreamy Elena)
- Excessive detail slows pacing; sparse detail can feel cold

**Example:** Scene 1 begins with gallery details. Layer 3 provides:
- story_time: "week_2_evening"
- pov_character_id: "elena"
- goal: "enjoy the evening and support daniel"

But NOT:
- What the gallery looks like
- What Elena is wearing
- How the crowd moves

Prose generated all three, making the scene vivid without violating structure.

**Layer 4 needs:**
- Visual focus guidance (what should the POV character notice?)
- Sensory emphasis (sight-heavy vs. sound-heavy vs. feeling-heavy?)
- Descriptive depth (sparse vs. lush)
- Character-specific noticing patterns (Elena is perceptive of body language, not architecture)

---

### Pattern 3: Pacing & Rhythm

**Layer 3 constraint:** Only narrative_position (ordering within chapter)  
**What prose generated:**
- Scene 1: Slow pacing - observation of facial expressions, internal realization
- Scene 2: Escalating pacing - dialogue exchange with building intensity
- Scene 3: Contemplative pacing - extended reflection on realization

**Risk Level:** MEDIUM

**Why it matters:**
- Slow pacing can defang dramatic tension
- Fast pacing can feel rushed without emotional landing
- Scene duration (30 seconds vs. 30 minutes) affects how readers experience time

**Example:** Scene 2 (confrontation) contains:
- Layer 3 goal: "force daniel to admit the truth"
- Layer 3 turn: "elena produces evidence (messages)"
- Layer 3 decision: "accept daniel's promise to end contact"

Prose compressed this into a single emotional climax (~5 minutes of dialogue). But what if the author intended:
- A longer argument with multiple reconciliations and ruptures?
- A quick confrontation followed by hours of processing?
- Back-and-forth negotiation with pauses?

Layer 3 doesn't specify temporal pacing.

**Layer 4 needs:**
- Compression/expansion guidance ("quick discovery" vs. "slow dawning")
- Scene duration target (moment vs. minutes vs. hours)
- Rhythm specification (fast dialogue, slow description, etc.)
- Pacing curve (does intensity build, spike, or plateau?)

---

### Pattern 4: Character Voice & Interiority

**Layer 3 constraint:** Only emotional_state labels (uncertain, devastation, acceptance)  
**What prose generated:**
- Scene 1: Analytical observation ("Elena felt something shift in her chest, something cold and small")
- Scene 2: Emotional reaction ("Elena's voice was steady now")
- Scene 3: Philosophical reflection ("suddenly, that became the liberation")

**Risk Level:** MEDIUM

**Why it matters:**
- Elena's voice must be consistent across scenes (should sound like the same person)
- Character voice shapes how readers interpret events (analytical Elena vs. emotional Elena)
- Interiority pattern (linear thoughts vs. spiral vs. metaphor-based) should match emotional core

**Example:** Scene 3 exit state includes:
```
emotional:
  acceptance: "liberated through surrender"
```

Prose interpreted this as philosophical epiphany:
```
"And suddenly, that became the liberation... she could accept what he was 
and decide who she would become."
```

But could also be interpreted as:
- Dull resignation ("It didn't matter anymore")
- Bitter clarity ("At least I know the truth")
- Relief ("Finally I can stop pretending")

Each interpretation is valid for "acceptance" but creates different emotional tone.

**Layer 4 needs:**
- POV voice archetype (analytical vs. emotional vs. sardonic vs. poetic)
- Thought pattern (linear introspection vs. spiral vs. image-based vs. dialogue)
- Vocabulary register (formal vs. colloquial vs. internal vs. external)
- Metaphor style (extended vs. sparse vs. specific vs. abstract)

---

### Pattern 5: Emotional Expression

**Layer 3 provides:** Abstract semantic labels ("uncertain," "devastation," "acceptance")  
**Prose must literalize:** Concrete experience showing that emotion

**Risk Level:** MEDIUM

**Example - "Uncertain" (Scene 1 exit):**

Layer 3 specifies:
```yaml
exit_state:
  emotional:
    trust: 
      state: "uncertain"
      intensity: "moderate"
```

Prose literalized this as:
```
"She felt something shift in her chest, something cold and small that hadn't 
been there before."
```

The metaphor ("cold and small") concretizes abstract uncertainty into physical sensation. But the metaphor could be wrong:
- Too purple prose for genre?
- Disconnected from Elena's character?
- Not matching the turn event (observation, not revelation)?

**Example - "Devastation" (Scene 2 exit):**

Layer 3 specifies:
```yaml
exit_state:
  emotional:
    devastation:
      state: "heartbroken"
      intensity: "high"
```

Prose literalized this as:
```
"Elena wanted to believe him. God, how she wanted to believe him... She stayed. 
In that moment, she chose to stay."
```

The passage shows devastation through yearning and capitulation, not through despair or anger.

**Layer 4 needs:**
- Guidance for literalizing emotional states (what concrete experience shows this state?)
- Metaphor constraints (abstract vs. specific, extended vs. brief)
- Intensity modulation (how does "low" uncertainty show vs. "high"?)
- Emotional consistency (same state should feel consistent across scenes)

---

### Pattern 6: Exposition & Knowledge Revelation

**Layer 3 provides:** Entry/exit knowledge structured with how_known and degree  
**Prose must decide:** How does reader learn these facts?

**Risk Level:** MEDIUM

**Example - Scene 1:**

Entry state (what Elena knows):
```yaml
knowledge:
  - "daniel and elena have been together for 5 years"
  - "elena has no reason to suspect daniel"
```

Exit state (what Elena learned):
```yaml
knowledge:
  - "daniel responds positively to sylvia's attention"
  - "daniel does not maintain physical boundaries with sylvia"
```

Prose could reveal entry knowledge:
- Through narration: "Elena had been with Daniel for five years. She trusted him completely."
- Through dialogue: (if other character present)
- Through action: (showing her confidence in the dress choice, etc.)
- Implicitly: (reader infers from her initial comfort at gallery)

Prose chose implicit revelation through action:
```
"She wore the black dress Daniel liked, the one that made her feel confident."
```

This shows trust implicitly. Good choice. But Layer 3 doesn't constrain it.

**Layer 4 needs:**
- Rules for revelation method (implicit vs. explicit, dialogue vs. narration)
- Exposition constraints (no front-loading, show through action)
- Knowledge chronology (when does reader learn fact?)
- POV respect (reader only knows what Elena knows, when Elena knows it)

---

### Pattern 7: Minor Actions & Blocking

**Layer 3 constraint:** Only major dramatic action (goal/opposition/turn/decision)  
**What prose generated:**
- "stepped into the gallery" (opening movement)
- "reached for her" (intimacy gesture)
- "pulled out her phone" (evidence access)
- "started the car and drove away first" (symbolic action)

**Risk Level:** LOW

**Why it works:**
- Minor actions reinforce major beats (reaching for her shows Daniel's initial denial instinct)
- Actions feel natural within prose context
- No contradiction to Layer 3 structure

**Layer 4 needs:**
- Guidance on action density (sparse vs. detailed blocking)
- Symbolic action constraints (what actions carry thematic weight?)
- Character movement patterns (does Elena pace, sit still, hide, approach?)

---

## Information Layer 4 Must Add

### 1. Prose Style Guide

**What Layer 3 leaves unspecified:**
- Literary device preferences (metaphor, simile, symbolism, etc.)
- Sentence structure variety (long/short, simple/complex)
- Dialogue attribution (he said, she asked, dialogue tags vs. action)
- POV depth (shallow observation vs. deep interiority)

**Layer 4 should define:**
- Genre-appropriate prose tone (netorare: escalating tension and humiliation)
- Archetype-specific voice (Elena: analytical, restrained, introspective)
- Metaphor constraints ("something cold and small" is this acceptable or too abstract?)
- Sentence rhythm (matches emotional state? matches pacing?)

**Why it matters:** Without these constraints, prose could sound:
- Overwrought (too many metaphors, purple prose)
- Detached (clinical, no emotional resonance)
- Inconsistent (Elena sounds different in each scene)
- Wrong-toned (cozy mystery voice doesn't fit netorare)

---

### 2. Dialogue Constraints

**What Layer 3 leaves unspecified:**
- Who should have dialogue (protagonist only? secondary characters?)
- Dialogue topics (what can be discussed, what's forbidden?)
- Dialogue tone (formal, intimate, defensive, etc.)
- Character-specific speech patterns

**Layer 4 should define:**
- POV character dialogue rules (sparse vs. frequent, revelatory vs. defensive)
- Opposition dialogue rules (how does opponent respond? what are their speech patterns?)
- Knowledge boundaries (character cannot say facts they don't possess)
- Emotional state effects (angry speech is shorter, uses "I" more, etc.)

**Example:** Scene 2 confrontation. Layer 3 says:
```yaml
opposition:
  source_id: "daniel"
  pressure: "denies involvement initially, then minimizes"
```

Daniel's dialogue was invented entirely by prose. Layer 4 should constrain it:
- Can Daniel deny knowing Sylvia well? (No, entry_state says he's been texting her)
- What tone should his denial use? (Defensive, guilty, negotiating?)
- What can he admit? (Entry state allows: "emotional involvement")
- What must he deny? (Entry state says: "claims no physical involvement")

---

### 3. Pacing Guidance

**What Layer 3 leaves unspecified:**
- Scene duration (moment vs. minutes vs. hours)
- Pacing curve (building, spiking, plateauing, falling)
- Action speed (quick succession of events vs. lingering moments)

**Layer 4 should define:**
- Intended scene duration ("this confrontation should feel like it takes 20 minutes")
- Compression/expansion guidance ("slow down at the turn, speed up after")
- Rhythm curve ("builds from observation to realization")
- Time markers (does action occur in real-time or compressed time?)

**Example:** Scene 2 could be:
- **Fast:** Confrontation happens in 2 minutes, quick exchanges, climax and decision
- **Slow:** Argument spans 30 minutes with pauses, reconciliation attempts, emotional processing
- **Episodic:** Multiple attempts and failures before final decision

Layer 3 doesn't distinguish. Layer 4 should specify which version matches intended effect.

---

### 4. POV Voice & Interiority Pattern

**What Layer 3 leaves unspecified:**
- How does Elena think? (Logical analysis vs. emotional reaction vs. metaphor-based)
- Thought structure (linear narrative vs. spiral vs. stream-of-consciousness)
- Vocabulary register (formal/literary vs. colloquial)
- Narrative distance (close to thoughts vs. observational)

**Layer 4 should define:**
- Elena's voice archetype (analytical observer, emotional reactor, philosophical reflector)
- Interiority method (direct thought vs. observation → inference)
- Consistency rules (same voice across all scenes)
- Emotional state modulation (how does Elena's voice shift with emotion?)

**Example:** Scene 1 entry emotion is "secure," exit emotion is "uncertain."

How should this shift Elena's voice?
- **Secure Elena:** Clear observations, confident judgments, smooth prose
- **Uncertain Elena:** Questioning, hesitation, fragmented thoughts

Layer 4 should guide this shift explicitly.

---

### 5. Descriptive Focus & Sensory Emphasis

**What Layer 3 leaves unspecified:**
- What should the POV character notice? (people, places, objects, sensations?)
- Sensory preference (sight-dominant, sound, touch, feeling?)
- Descriptive depth (sparse vs. lush)
- Character-specific noticing pattern

**Layer 4 should define:**
- Elena's observational focus (body language? dialogue? environment?)
- Sensory emphasis in each scene (Scene 1: visual observation; Scene 2: emotional feeling; Scene 3: internal reflection)
- Descriptive budget (what proportion of prose is description vs. action vs. interiority?)
- Skip rules (what should NOT be described? Irrelevant details that would distract?)

**Example:** Scene 3 occurs in Elena's car watching Sylvia's building.

Layer 3 specifies:
- story_time: "week_11_afternoon"
- goal: "verify whether daniel kept his promise"
- turn: "elena sees daniel leaving sylvia's apartment"

But not:
- What does the building look like?
- What does Sylvia's apartment reveal through its exterior?
- What does Elena see when Daniel emerges (clothes, expression, body language)?
- Does Elena focus on environment or on Daniel?

Layer 4 should guide: "Focus narrowly on Daniel's appearance and demeanor; external details blur."

---

### 6. Stylistic Constraints

**What Layer 3 leaves unspecified:**
- Metaphor style (extended vs. brief, abstract vs. concrete)
- Literary devices (which are appropriate? Which to avoid?)
- Sentence structure patterns (varied, consistent, rhythmic?)
- Genre-specific tone (netorare should feel like escalating humiliation, not cozy mystery)

**Layer 4 should define:**
- Acceptable metaphors for this story (Elena's internal state shown through what imagery?)
- Forbidden devices (avoid direct addresses to reader? stream of consciousness ok?)
- Sentence rhythm (matches pacing, emotional state, POV voice)
- Genre tone (netorare requires specific emotional calibration)

**Example:** Scene 1 prose used metaphor:
```
"something cold and small that hadn't been there before"
```

Is this:
- Perfect literalization of "uncertainty"? (YES)
- Acceptable metaphor depth? (YES)
- Right emotional tone for netorare? (YES - suggests growing dread)

But Layer 3 doesn't constrain these choices. Layer 4 should.

---

### 7. Exposition Method Rules

**What Layer 3 leaves unspecified:**
- How should entry_state knowledge become visible to reader?
- Should exposition be implicit or explicit?
- When should facts be revealed (opening, middle, end)?
- What narrative methods are acceptable? (Narration, dialogue, action, inference?)

**Layer 4 should define:**
- Rules for naturalness (no info-dumping about background)
- Rules for POV respect (reader only learns what Elena knows)
- Rules for integration (entry_state weaves into scene, not stated as facts)
- Rules for precision (does reader need to know exact timeline? Or just "they've been together"?)

**Example:** Scene 13 entry_state includes:
```yaml
knowledge:
  - "elena has doubts about daniel's sincerity"
  - "daniel has been texting sylvia regularly"
```

Prose could reveal these as:
- **Narration:** "Elena had discovered Daniel's texts two days ago"
- **Dialogue:** "Your texts to her... I found them"
- **Action:** Elena pulls out her phone (reader infers she has evidence)
- **Observation:** "She knew the signs. He was lying"

Prose chose action → dialogue (most dramatic). Layer 4 should guide whether this choice is consistent with desired style.

---

## Information Layer 3 Provided But Could Be More Precise

### 1. Emotional State Labels

**Current precision:** Semantic labels ("uncertain," "devastation," "acceptance") with intensity

**Could be enhanced with:**
- Example internal experience (what does this emotion feel like in body? in thought?)
- Behavioral markers (how does this emotion show externally?)
- Thought pattern shifts (does devastation make thoughts spiral or freeze?)

**Impact on Layer 4:** More precise emotion definitions would constrain prose generation better.

**Example:** Current Layer 3:
```yaml
emotional:
  trust:
    state: "uncertain"
    intensity: "moderate"
```

Could be enhanced:
```yaml
emotional:
  trust:
    state: "uncertain"
    intensity: "moderate"
    internal_experience: "persistent doubt despite wanting to believe"
    behavioral_marker: "avoids eye contact, changes subject"
    thought_pattern: "circular - keeps returning to contradictory evidence"
```

This would guide prose toward specific characterization.

---

### 2. Knowledge Entry/Exit Transitions

**Current precision:** Structured knowledge with how_known and degree

**Could be enhanced with:**
- Impact on character (does this knowledge shift goals? decisions?)
- Integration method (how does character incorporate new knowledge?)
- Certainty shift (does knowledge go from "suspected" to "certain"?)

**Impact on Layer 4:** Better understanding of knowledge's emotional weight.

**Example:** Current Layer 3:
```yaml
knowledge_questioned:
  - "daniel's fidelity"
```

Could be enhanced:
```yaml
knowledge_questioned:
  - fact: "daniel's fidelity"
    was_degree: "certain"
    now_degree: "probable"
    emotional_weight: "catastrophic"
    goal_shift: "from preserve-relationship to verify-truth"
```

---

## Verdict: Layer 4 Scope is Clear

### Layer 3 Successfully Owns

- Narrative structure (goal/opposition/turn/decision/outcome)
- Dramatic coherence (what happens and why)
- Character knowledge tracking (what they know and how they know it)
- Emotional state transitions (entry → exit)
- Arc beat realization (which beats advance)
- Story continuity (setups/payoffs)

**Confidence:** Layer 3 foundation is solid. No critical story information is missing.

---

### Layer 4 Must Own

| Responsibility | Scope |
|----------------|-------|
| **Prose voice & POV interiority** | How the character thinks, their internal monologue style, voice consistency |
| **Dialogue generation** | Character speech with knowledge/emotion/tone constraints |
| **Pacing & rhythm** | Scene duration, pacing curve, action speed |
| **Sensory details** | What POV character notices, visual focus, sensory emphasis |
| **Prose style** | Literary devices, metaphor, sentence structure, genre tone |
| **Exposition method** | How entry_state knowledge becomes visible to reader |
| **Minor actions & blocking** | Movement, gesture, symbolic action |
| **Emotional literalization** | Converting semantic emotional states to concrete prose experience |

**Confidence:** Layer 4 scope is well-defined and doesn't overlap with Layer 3.

---

### No Significant Layer 3 Gaps Found

The 3 dogfood scenes demonstrate that SceneOutline is sufficient for prose generation to proceed. No critical information is missing that would prevent prose generation.

However, Layer 3 could be enhanced (optional, not required):
- More detailed emotion definitions (internal experience, behavioral markers)
- Knowledge transitions explained (why each fact matters)
- Exposition guidance (when should reader learn facts?)

---

## Recommendations

### For Immediate Layer 4 Implementation

1. **Define prose style guide** with genre tone (netorare: escalating humiliation, emotional intensification), metaphor constraints, sentence structure patterns

2. **Specify dialogue rules** with knowledge boundaries (character cannot say facts they don't possess), emotional state effects on speech, tone per character

3. **Create pacing schema** that specifies scene duration, compression/expansion guidance, and rhythm patterns

4. **Define POV voice archetype** with thought patterns, vocabulary register, and consistency rules

5. **Establish exposition method rules** to integrate entry_state knowledge naturally without info-dumping

### For Future Layer 3 Enhancement

1. Add optional `prose_guidance` field to SceneOutline:
   ```yaml
   prose_guidance:
     voice_archetype: "analytical_observer"
     sensory_emphasis: "body_language_and_facial_expression"
     pacing: "slow_dawning_realization"
     metaphor_style: "concrete_physical_sensations"
   ```

2. Enhance emotional states with:
   ```yaml
   emotional:
     uncertainty:
       internal_experience: "persistent doubt despite wanting to believe"
       behavioral_marker: "avoids_eye_contact"
       thought_pattern: "circular"
   ```

3. Add exposition method to knowledge facts:
   ```yaml
   knowledge:
     - what: "daniel has been texting sylvia"
       how_known: "learned"
       expose_method: "show_phone_screen"  # vs. dialogue, narration, inference
   ```

---

## Conclusion

**SceneOutline (Layer 3) provides complete dramatic structure.** All 3 dogfood scenes validated successfully. Prose generation can proceed with Layer 3 as foundation.

**Layer 4 should focus on voice, style, and presentation.** The scope is clear and distinct from Layer 3:
- Layer 3: WHAT happens (structure, action, knowledge, emotion states)
- Layer 4: HOW it's told (voice, pacing, style, exposition, dialogue)

**No critical gaps found.** Layer 3 is ready for Layer 4 implementation.

**Success metric for Layer 4:** Generated prose should:
1. Respect all Layer 3 constraints (POV, goal, opposition, turn, decision, outcome, entry/exit states)
2. Sound like a coherent character with consistent voice
3. Maintain genre tone (netorare: escalating emotional intensity)
4. Feel like literary prose, not stage directions
5. Preserve knowledge boundaries (only know what entry_state allows)
6. Show emotional transitions realistically

---

**Analysis completed:** 2026-07-13  
**Confidence level:** HIGH  
**Ready for Layer 4 spec:** YES

