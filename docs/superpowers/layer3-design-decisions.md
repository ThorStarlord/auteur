# Layer 3: Narrative Realization — Design Decisions

**Status:** READY FOR PLANNING (after Layer 2 dogfood verification)  
**Goal:** Convert chapter intentions into concrete dramatic units (scenes)

## Five Critical Semantic Boundaries

These decisions must be finalized before implementation. They determine whether Layer 3 becomes a robust realization system or another set of disconnected YAML files.

---

## 1. Scene Ownership Model

**Question:** Does the chapter own a list of scenes, or do scenes reference the chapter?

**Decision:**

```text
Scene owns chapter_id
Chapter scene list is derived
```

**Rationale:**
- Moving a scene between chapters requires changing only one field (scene.chapter_id)
- No two sources of truth (no sync required)
- Deletion is simple (delete scene file; chapter list auto-updates)
- Enables scenes to be authored independently

**Implementation:**

```yaml
# Scene file: scene_07_02.yaml
id: scene_07_02
chapter_id: chapter_07            # ← Scene owns this reference
narrative_position: 2

# Chapter file: chapter_07.yaml
# scene_ids: [] ← DERIVED from query: find all scenes where chapter_id == chapter_07
```

**Validation rule:** All scenes reference existing chapters; all chapters contain scenes (derive scene list).

---

## 2. Arc Beat Realization Model

**Question:** How do scenes relate to arc beats? Do they realize, reference, or defer them?

**Decision:**

```text
Arc owns beat definition (planned structural beat)
Scene references beat occurrence (realized in scene)
Arc realizes may be partial (degree of realization)
```

**Rationale:**
- Arc beat is single source of truth for what should happen
- Multiple scenes might partially realize one beat
- Scene can reference beat but only partially achieve it
- Enables diagnostics like "this beat was intended but didn't occur"

**Implementation:**

```yaml
# Arc file: character_arcs/clara_trust_arc.yaml
beats:
  - id: distrust_deepens
    intended_effect: "Clara's trust in Daniel decreases"
    phase_target: 4
    emotional_intensity: high

# Scene file: scene_07_02.yaml
realizes_arc_beats:
  - beat_id: distrust_deepens
    degree: full              # Alternative: partial, implied, deferred
    evidence:
      - Clara_conceals_discovery
      - Clara_avoids_Daniel
```

**Validation rule:**
- All referenced beats must exist in their arcs
- Beat realization degree must be one of: full, partial, implied, deferred
- At least one scene should fully realize each critical beat

**Future extension (not V1):**
- Track why beat was only partial (author choice vs. plot constraint)
- Compare intended vs. realized effect

---

## 3. Scene Position and Temporal Simultaneity

**Question:** Can two scenes have the same position? How do we represent events that occur simultaneously but are shown sequentially?

**Decision:**

```text
narrative_position must be unique (reading order)
temporal_relation tracks story-world simultaneity
```

**Rationale:**
- Narrative position is how reader encounters scenes (always linear)
- Story-world time can have simultaneous events
- Conflating them creates false constraints
- Enables validation of timeline consistency

**Implementation:**

```yaml
# Scene A (shown in narrative position 1)
id: scene_07_01
narrative_position: 1
story_time:
  starts_at: "day_3_evening"
  ends_at: "day_3_21_30"

# Scene B (shown in narrative position 2, but occurs at same time as A)
id: scene_07_02
narrative_position: 2
story_time:
  starts_at: "day_3_evening"
  ends_at: "day_3_21_20"
temporal_relation:
  parallel_with:
    - scene_07_01

# Scene C (shown in position 3, occurs after both)
id: scene_08_01
narrative_position: 3
story_time:
  starts_at: "day_3_22_00"
```

**Validation rule:**
- narrative_position values must be unique within chapter
- If temporal_relation.parallel_with references scene_X, scene_X must reference back (mutual)
- No circular parallel-with chains

**V1 Simplification:** May use text-based story_time initially:
```yaml
story_time: "day_3_evening"
temporal_relation:
  parallel_with:
    - scene_07_01
```

---

## 4. POV Character Knowledge Model

**Question:** What can a POV character know? How do we track entry knowledge vs. discovered knowledge?

**Decision:**

```text
entry_knowledge: what character knows entering scene
entry_means: how they know it (previous scene, briefing, inference)
perceived_in_scene: what character directly witnesses
learned_in_scene: what character concludes or discovers
exit_knowledge: what character knows after scene (derived)
```

**Rationale:**
- Absence of character ≠ ignorance (can learn through message, document, etc.)
- Critical for consistency validation (character shouldn't know before discovery)
- Enables tracking knowledge propagation across chapters
- Supports non-POV character knowledge (what protagonist knows about others)

**Implementation:**

```yaml
id: scene_07_02
pov_character_id: clara
participants:
  - clara
  - daniel

entry_knowledge:
  facts:
    - daniel_claims_innocence
  beliefs:
    - daniel_is_trustworthy
  emotions:
    - hope
    - uncertainty

perceived_in_scene:
  discoveries:
    - altered_access_record
  actions:
    - daniel_attempts_to_stop_her
  dialogue:
    - daniel_explains_he_was_researching_too

learned_in_scene:
  inferences:
    - someone_altered_archive (from discovery)
  emotional_shifts:
    - suspicion_deepens
  questions:
    - "Why does Daniel care if she finds the record?"

exit_knowledge:
  facts:
    - access_record_was_altered
    - daniel_noticed_her_discovery
  beliefs:
    - daniel_may_not_be_trustworthy
  emotions:
    - fear
    - determination
```

**Validation rule:**
- All exit_knowledge should be derivable from entry_knowledge + perceived_in_scene + learned_in_scene
- Knowledge doesn't retroactively disappear (once learned, known)
- Character-specific knowledge consistency (if Clara learns X, Daniel can't act as if X is unknown unless scenes are parallel)

---

## 5. Emotional State Representation

**Question:** Should emotional states be numeric, directional, or semantic? What precision is useful without false objectivity?

**Decision:**

```text
V1: Directional + semantic (not numeric)
Use state transitions and intensity, not scales
Allow semantic labels and brief rationale
```

**Rationale:**
- Numeric scales imply false precision (trust: 5.2?)
- Narrative emotions are qualitative, not quantitative
- State transitions are verifiable (from suspicious to paranoid)
- Intensity (low/moderate/high) captures arc without false objectivity
- Rationale field enables author intent to be visible

**Implementation:**

```yaml
# Entry emotional state
entry_emotional:
  trust:
    state: guarded
    intensity: moderate
  suspicion:
    state: active
    intensity: moderate
  hope:
    state: waning
    intensity: low

# Emotional changes during scene
emotional_arc_in_scene:
  - trigger: Daniel tries to stop her
    shift: trust → suspicion
    intensity_before: moderate
    intensity_after: high
  - trigger: Clara finds altered record
    shift: suspicion → certainty
    intensity_change: deepens

# Exit emotional state
exit_emotional:
  trust:
    state: suspicion
    intensity: high
    rationale: Daniel's interference proves he's hiding something
  suspicion:
    state: certainty
    intensity: high
  fear:
    state: emerging
    intensity: moderate
```

**Allowed emotional states (domain-specific examples):**
- trust ↔ suspicion ↔ certainty
- hope ↔ doubt ↔ despair
- safety ↔ unease ↔ fear ↔ terror
- accepted ↔ conflicted ↔ opposed

**Validation rule:**
- States should be linguistically plausible transitions (not arbitrary)
- Intensity should be consistent (can't go from high→low→high within single scene without justification)
- Rationale field is optional but recommended for non-obvious shifts

**Future extension (not V1):** If emotion patterns emerge, can formalize state machine per character arc.

---

## 6. Scene Completeness & Draft State

**Question:** Can incomplete scenes exist? What's the minimum viable scene?

**Decision:**

```text
Allow scenes in draft/incomplete states
Validation distinguishes draft vs. production-ready
Minimum viable: chapter_id + pov_character + goal + outcome
```

**Rationale:**
- Authors need scaffolding (scenes before they're detailed)
- Validation should not block work-in-progress
- Clear distinction between planning and finished structure
- Enable gradual scene refinement

**Implementation:**

```yaml
# Minimal/draft scene
id: scene_07_04
chapter_id: chapter_07
narrative_position: 4
status: draft         # draft | incomplete | ready

pov_character_id: clara
# (participants, entry_state optional)

goal:
  actor_id: clara
  objective: determine_daniel_role
  # (opposition, turn optional)

outcome:
  result: unresolved
  # (emotional_changes optional)

# Production-ready scene
id: scene_07_02
chapter_id: chapter_07
narrative_position: 2
status: ready

pov_character_id: clara
participants:
  - clara
  - daniel

entry_state: {...}
goal: {...}
opposition: {...}
turn: {...}
decision: {...}
outcome: {...}
exit_state: {...}
realizes_arc_beats: {...}
```

**Validation rule:**
- Status: draft → only basic references validated
- Status: ready → full validation (all fields required, consistency checked)
- Cannot mark scene "ready" if referenced arc beats don't exist

---

## Refined Layer 3 V1 SceneOutline

Based on the five decisions above:

```yaml
id: scene_07_02
chapter_id: chapter_07
narrative_position: 2
status: ready  # draft | incomplete | ready

# Participants
pov_character_id: clara
participants:
  - clara
  - daniel

# Temporal placement
story_time: "day_3_evening"
temporal_relation:
  parallel_with: []
  follows_scene: scene_07_01

# Entry state
entry_state:
  knowledge:
    - daniel_claims_innocence
  emotional:
    trust:
      state: guarded
      intensity: moderate
    suspicion:
      state: active
      intensity: moderate

# Dramatic action
goal:
  actor_id: clara
  objective: inspect_the_ledger
  rationale: "Prove or disprove Daniel's alibi"

opposition:
  source_id: daniel
  pressure: prevent_discovery_without_explanation
  rationale: "He realizes what she's looking for"

turn:
  type: discovery
  event: altered_access_record_found
  impact: "Clara can no longer believe his innocence"

decision:
  actor_id: clara
  choice: conceal_the_discovery
  rationale: "She needs time to understand implications"

outcome:
  result: partial_success
  knowledge_added:
    - access_record_was_altered
  knowledge_questioned:
    - daniel_alibi_validity
  consequences:
    - daniel_realizes_clara_found_evidence

# Exit state
exit_state:
  knowledge:
    - access_record_altered
    - daniel_noticed_her
  emotional:
    trust:
      state: suspicion
      intensity: high
      rationale: "Daniel's interference confirms guilt"
    fear:
      state: emerging
      intensity: moderate

# Structural references
realizes_arc_beats:
  - beat_id: clara_distrust_deepens
    degree: full
  - beat_id: false_alibi_discovered
    degree: full

setups_created:
  - altered_record_signature

payoffs_triggered:
  - plant_false_alibi
```

**This remains minimal but preserves:**
- Clear ownership (scene owns chapter_id)
- Arc realization semantics (degree of realization)
- Temporal model (position + story_time + parallel_with)
- POV knowledge (entry + learned + exit)
- Emotional semantics (directional + intensity + rationale)
- Draft state support (status field)

---

## Layer 3 V1 Scope

**Implement:**
- ✅ SceneOutline schema (as above)
- ✅ Scene-to-chapter validation
- ✅ Arc beat reference validation
- ✅ Knowledge consistency (no retroactive forgetting)
- ✅ Temporal relationship validation (no circular parallel-with)
- ✅ Scene loader (YAML serialization)
- ✅ CLI: auteur {genre} realization {seed|validate|inspect}

**Do NOT implement (later layers):**
- ❌ Dialogue planning or prose outline
- ❌ Beat libraries or automatic scene generation
- ❌ Emotional state machines or quantitative scales
- ❌ Shot-by-shot blocking or staging
- ❌ Detailed timeline with clock times

**Validation rules (Layer 3 V1):**
1. All scenes reference existing chapters
2. Scene narrative_position unique within chapter
3. All referenced arc beats exist in their arcs
4. temporal_relation.parallel_with mutual (if A parallel B, then B parallel A)
5. Knowledge consistency (can't forget, can't know before discovery)
6. Arc beat realization is full/partial/implied/deferred only
7. Draft scenes skip some fields; ready scenes require all fields

---

## Success Criteria for Layer 3 V1

- [ ] One chapter can be realized as multiple scenes
- [ ] Scenes can reference and partially realize arc beats
- [ ] Temporal relationships (parallel scenes) validate correctly
- [ ] Knowledge entry→exit consistency enforced
- [ ] Status field prevents invalid state transitions (draft → ready requires all fields)
- [ ] Graph shows scene sequence within chapter and cross-chapter arc beats
- [ ] Diagnostics are as clear as Layer 2 (reference, temporal, knowledge violations explained)
- [ ] Scenes from generated outline pass all validators

---

**Last Updated:** 2026-07-12  
**Status:** DESIGN DECISIONS FINALIZED  
**Prerequisite:** Layer 2 dogfood verification  
**Next Step:** Layer 3 implementation plan (after dogfood)
