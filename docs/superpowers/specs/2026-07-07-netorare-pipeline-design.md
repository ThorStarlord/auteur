# Netorare Genre Pipeline Design

**Date:** 2026-07-07  
**Status:** Design Approved  
**Scope:** Interactive 9-layer decision tree for authoring opinionated netorare stories

---

## 1. Executive Summary

The netorare pipeline is a **guided discovery workbench** that teaches authors about story machinery through interactive choice-and-consequence exploration. It is not a recommendation engine; it is a **deterministic 9-layer decision interface** that guides authors through the full narrative structure, showing how each choice cascades through all downstream layers.

The pipeline supports three distinct emotional cores (Classic Humiliation, Horror, Mystery), each with its own structural template. Authors select one core and progress through 8 phases (Layers 1-9), making decisions at each phase while seeing real-time updates to the full 9-layer structure. Each phase includes a pause-for-review checkpoint where authors can see the consequences of their choice before moving forward.

Output is a deterministically-validated `story_identity.yaml` file that feeds into existing auteur commands (`blueprint seed`, `structure diagnose`, etc.).

---

## 2. User Intent & Problem

**User Need:** Authors want to write netorare stories but don't understand the structural differences between netorare subtypes or how emotional core decisions cascade through narrative structure.

**Learning Goal:** Authors should learn "the machinery of writing and of the genre" by making explicit structural choices and seeing their consequences.

**Opinionated Philosophy:** The pipeline enforces one clear path per emotional core, but supports intentional blending via the override system (not arbitrary mixing).

---

## 3. Architecture

### 3.1 Three Emotional Cores

Each core is a distinct **9-layer template** with its own:
- Target experience (Layer 1)
- Genre contract (Layer 2)
- Scope defaults (Layer 3)
- Structural forces skeleton (Layer 4)
- Thread/module patterns (Layer 5)
- Character role requirements (Layer 6)
- Scene structure patterns (Layer 7)
- Modulation guidelines (Layer 8)
- Thematic coherence constraints (Layer 9)

**Core 1: Classic Humiliation**
- Primary emotion: Shame, powerlessness, degradation
- Emotional progression: Confidence → Suspicion → Exposure → Acceptance/Reclamation
- Want/Change Arc: MC wants dignity/proof but must accept powerlessness (tragic) or reclaim through reckoning (cathartic)
- Escalation pattern: Humiliation spiral (discoveries stack against MC's position)
- Valid endings: Tragic acceptance OR cathartic reckoning (via override)

**Core 2: Horror**
- Primary emotion: Dread, psychological terror, ontological wrongness
- Emotional progression: Unease → Escalating Horror → Body/Mind Transgression → Transformation
- Want/Change Arc: MC wants to escape/prevent/understand but must transform or accept new reality
- Escalation pattern: Reality-breaking (rules of world shift, no escape)
- Valid endings: Transform into new form OR accept new order (both valid, no tragic/cathartic distinction)

**Core 3: Mystery**
- Primary emotion: Voyeurism, curiosity, unwilling complicity
- Emotional progression: Suspicion → Investigation → Revelation → Unwilling Complicity
- Want/Change Arc: MC wants truth/confirmation but becomes knowing witness or active participant
- Escalation pattern: Investigation acceleration (clue density increases, misdirection deploys)
- Valid endings: Unwilling witness OR active participant (both valid)

### 3.2 9-Phase Decision Flow

```
Phase 1: Emotional Core Selection (Layer 1)
  → User selects: Humiliation | Horror | Mystery
  → Auto-transition after approval

Phase 2: Genre Contract & Scope (Layers 2-3)
  → Options pre-populated based on Core
  → Auto-transition after approval

Phase 3: Structural Forces (Layer 4) - PAUSE FOR REVIEW
  → User selects: Want, Resistance, Conflict, Stakes, Change
  → Review checkpoint: Show cascaded consequences
  → Explicit approval required to proceed

Phase 4: Threads & Subgenre Modifiers (Layer 5) - PAUSE FOR REVIEW
  → Main thread locked to Core
  → User selects: Subplot options
  → User can declare subgenre modifiers (locked_room, hardboiled, cozy, etc.)
  → Review checkpoint
  → Explicit approval

Phase 5: Carriers (Layer 6) - PAUSE FOR REVIEW
  → Required character roles pre-populated by Core
  → User customizes: POV count, additional characters
  → Relationship structure options
  → Review checkpoint

Phase 6: Representation (Layer 7) - PAUSE FOR REVIEW
  → Act structure (locked to Core pattern)
  → User selects: Pacing strategy, reveal timing
  → Scene structure options
  → Review checkpoint

Phase 7: Modulation (Layer 8) - PAUSE FOR REVIEW
  → User selects: POV flavor, tone, voice
  → Pacing dynamics
  → Stylistic choices
  → Review checkpoint

Phase 8: Resonance Check (Layer 9) - PAUSE FOR REVIEW
  → Theme options presented (filtered by all prior choices)
  → User selects: Core theme, motifs
  → Coherence validation runs
  → Final approval
```

### 3.3 Cascade & Real-Time Visualization

**Left Panel:** Decision interface (one phase at a time)  
**Right Panel:** Live 9-layer structure preview (always visible)

When user makes a choice:
1. **Immediate highlight:** Current layer highlights in bold
2. **Cascade visualization:** Affected downstream layers (N+1 to 9) show updated content in muted color with label "calculated from your choices"
3. **Color coding:** Each layer has distinct background color for visual separation
4. **Smart highlighting:** Only the most affected layers glow; others remain visible for context

Example: User selects "Want: Regain dignity" (Layer 4)
- Layer 4 glows with the full want/resistance/conflict/change skeleton
- Layer 5 shows which threads can support this want
- Layer 6 dims but shows carrier roles must align
- Layer 7 shows which scene structures work for this want
- Layer 8-9 remain visible but dimmed

### 3.4 Pause-for-Review Checkpoints

After each major decision, display:

```
✓ You selected: [CHOICE SUMMARY]

This shapes your story:
  [CONSEQUENCE 1]
  [CONSEQUENCE 2]
  [CONSEQUENCE 3]

Downstream impacts:
  • Layer N+1: [constraint]
  • Layer N+2: [constraint]

[Approve - Continue] [Choose Different Option]
```

Only after explicit [Approve] does pipeline auto-transition to next phase.

### 3.5 Validation & Constraint Enforcement

Each phase validates against deterministic rules:

**Layer 4 validation:**
- Want ≠ Change (core dramatic engine rule)
- Resistance must create genuine obstacle to Want
- Stakes must align with emotional core

**Layer 5 validation:**
- Selected threads must support the want
- Subplot budget respects scope contract
- Subgenre modifiers must be compatible with core

**Layer 6 validation:**
- Required character roles present (MC, Partner, Rival)
- POV count respects scope contract
- No character roles violate core constraints (e.g., "innocent MC" forbidden in Humiliation)

**Layer 7 validation:**
- Act structure matches core pattern
- Scene pacing supports emotional progression
- Forbidden endpoints are blocked (e.g., "MC wins" impossible in Humiliation tragic path)

**Layer 8 validation:**
- POV choice supports emotional core
- Tone consistency across acts

**Layer 9 validation:**
- Theme resonates with all prior layers
- Motifs support core emotional message
- Full coherence check across all 9 layers

**On validation failure:** Pipeline shows:
```
⚠️ This choice creates structural incoherence.
Reason: [RULE NAME]: [EXPLANATION]

Valid alternatives for this choice:
  • [Option A] → consequence
  • [Option B] → consequence
  • [Option C] → consequence
```

---

## 4. Genre Blending & Overrides

### 4.1 Default: Single-Path Opinionated

Author picks ONE emotional core. Pipeline enforces that core's template throughout Layers 1-9. All validation rules tied to that core apply.

### 4.2 Advanced: Intentional Genre Shift

Author can declare a `genre_shift` override to create two distinct contract zones:

```yaml
story_identity:
  target_experience: mystery
  
  genre_shift_override:
    phase_1:
      core: mystery
      layers: 1-5
      description: "Act 1-2: MC investigates the relationship"
    
    phase_2:
      core: horror
      layers: 6-9
      description: "Act 3: MC discovers what they've become complicit in"
    
    transition_point:
      act: "End of Act 2"
      narrative_function: "Revelation recontextualizes all prior investigation as complicity"
    
    justification: "Audience undergoes same recontextualization as MC"
```

### 4.3 Blending Validation

A genre shift is classified as a `subversion` override. Validation checks:

1. **Phase 1 template:** Is mystery coherent through Layer 5?
2. **Phase 2 template:** Is horror coherent through Layers 6-9?
3. **Transition function:** Does the shift point have explicit narrative purpose?
4. **Theme continuity:** Do both cores' themes support the same underlying argument?

If blending fails validation:
```
⚠️ Genre shift is narratively valid but structurally incoherent.
Problem: Mystery core requires [X] theme, but Horror core requires [Y].
These cannot coexist without one being muted.

Options:
  1. Keep Mystery → Change Horror theme to [Z]
  2. Keep Horror → Change Mystery theme to [Z]
  3. Choose different genre for phase 2
```

---

## 5. Decision Trees per Core

### 5.1 Classic Humiliation

**Layer 4 Branches:**

Want options:
- Regain dignity / prove their worth
- Prove their love was genuine all along
- Expose the other person's deception
- Escape or flee the situation

Each want cascades to specific resistance:
- "Regain dignity" → Resistance: [Own inadequacy] or [Rival's genuine superiority]
- "Prove love" → Resistance: [Contradiction in evidence] or [Partner's authentic choice]
- "Expose" → Resistance: [No one believes MC] or [Exposure implicates MC too]
- "Escape" → Resistance: [Social bonds trap MC] or [MC's own identity is entangled]

Change options (after Layer 4 completion):
- Accept powerlessness / loss (tragic path)
- Reclaim through reckoning / confrontation (cathartic path via override)

**Layer 5 Branches:**

Main thread (locked): Humiliation spiral

Subplot options:
- Rival's perspective (show their side)
- Witness observer (confidant's POV, secondary)
- Partner's hidden motivation (reveal vs. withhold)

**Layer 6 Branches:**

Required roles:
- MC (powerless protagonist)
- Partner (choosing other person)
- Rival (superior alternative)

Optional roles:
- Confidant (MC's trusted listener)
- Witness (external observer)
- Authority figure (social pressure enforcer)

Constraint: No "innocent MC" character arcs. MC must have some inadequacy (real or perceived) that explains the situation.

**Layer 7 Branches:**

Act structure (locked to humiliation pattern):
- Act 1: Setup false confidence / secure relationship
- Act 2: Escalating discovery (clues stack against MC's position)
- Act 3: Confrontation & resolution

Scene pacing (user selects):
- Accelerating reveals (clue density increases)
- Slow burn (long period of suspicion before acceleration)
- Delayed discovery (most info withheld until final act)

Forbidden: "Dramatic reversal where MC wins" or "Rival revealed as villain" (violates humiliation contract)

**Layer 8 Branches:**

POV options:
- Limited to MC's shame-spiral perception (recommended)
- Alternating MC + Rival (shows contrast)
- MC only, with unreliable narrator techniques

Tone options:
- Suffocating intimacy (everything happens close/personal)
- Social observation (watching from outside perspective)
- Psychological fragmentation (MC's mind breaking apart)

**Layer 9 Branches:**

Theme options (filtered by all prior choices):
- "The limits of love vs. adequacy"
- "Powerlessness in witnessing what you cannot change"
- "The cost of self-deception"
- "Social bonds as traps"

---

### 5.2 Horror

**Layer 4 Branches:**

Want options:
- Escape / get away from the transgression
- Prevent the transformation from happening
- Understand what is happening to reality
- Restore things to how they were

Each cascades to: Inescapability resistance (the situation is ontologically inescapable)

Change options:
- Transform into something new (both valid, not tragic/cathartic split)
- Accept the new order of reality

**Layer 5 Branches:**

Main thread (locked): Reality-breaking escalation

Subplot options:
- Sanity fragmentation (MC's mind breaks)
- Partner's unknowability (other person becomes alien)
- Cosmic scale (something vast is revealed)

**Layer 6 Branches:**

Required roles:
- MC (witnessing the horror)
- Partner (becoming other / transformed)
- Transgressor (inhuman force / entity)

Constraint: Partner must become increasingly alien, not sympathetic. (If sympathetic, story collapses into humiliation.)

**Layer 7 Branches:**

Act structure (locked):
- Act 1: Normal world, small wrongness
- Act 2: Reality destabilizes (rules shift)
- Act 3: New reality crystallizes (no return)

Scene pacing:
- Mounting dread (tension builds)
- Sudden vertigo (stable world breaks all at once)
- Slow wrongness (wrongness accumulates gradually)

Forbidden: "Everything returns to normal" endings

**Layer 8 Branches:**

POV:
- Fragmenting perspective as sanity breaks (recommended)
- Detached observation (MC becoming inhuman)

Tone:
- Wrongness and violation
- Cosmic indifference
- Body horror intimacy

**Layer 9 Branches:**

Theme options:
- "The horror of seeing loved ones become unknowable"
- "The price of knowledge"
- "Bodily/existential corruption"
- "The impossibility of consent to transformation"

---

### 5.3 Mystery

**Layer 4 Branches:**

Want options:
- Understand the truth about the relationship
- Confirm suspicions without being seen
- Expose what's been hidden
- Figure out the other person's motivations

Change options:
- Become unwilling witness (knew it, did nothing)
- Active participant (knew it, became involved)

**Layer 5 Branches:**

Main thread (locked): Investigation / unveiling

Subplot options:
- Red herrings (false leads, misdirection)
- Slow realization of complicity (each clue implicates MC more)
- Secondary investigation (parallel mystery)

**Layer 6 Branches:**

Required roles:
- MC (detective / investigator)
- Partner (enigma / target of investigation)
- Rival (hidden agent / revelation)

Constraint: None can be one-dimensional. All must have hidden depths revealed.

**Layer 7 Branches:**

Act structure (locked):
- Act 1: Suspicion planted
- Act 2: Investigation accelerates (clue density increases)
- Act 3: Truth reveals MC's complicity

Scene pacing:
- Clue density increases progressively
- Information withheld then dumped
- Steady accumulation with false explanations

Forbidden: "MC remains innocent observer" endings (violates mystery contract)

**Layer 8 Branches:**

POV:
- Gradually unreliable as knowledge reveals (recommended)
- Detective prose style
- Voyeuristic perspective

Tone:
- Voyeuristic unease
- Noir investigation
- Psychological puzzle-solving

**Layer 9 Branches:**

Theme options:
- "The impossibility of remaining innocent once you know"
- "The complicity of observation"
- "Watching and being watched"
- "Knowledge as transgression"

---

## 6. Output Artifacts

### 6.1 Story Identity YAML

```yaml
story_identity:
  version: "1.0"
  
  # Layer 1
  target_experience:
    primary_emotion: "humiliation"
    emotional_progression:
      - "confidence"
      - "suspicion"
      - "exposure"
      - "acceptance"
    secondary_palette:
      - "shame"
      - "powerlessness"
  
  # Layer 2
  genre_contract:
    genre: "netorare"
    subgenre: "classic_humiliation"
    mode: "tragedy"  # or "conquest" via override
    medium: "novel"
  
  # Layer 3
  scope_contract:
    story_length: "novel"
    pov_budget: 1
    subplot_budget: 1
  
  # Layer 4
  structural_forces:
    want: "regain_dignity"
    resistance: "own_inadequacy"
    conflict: "evidence_accumulates_against_position"
    stakes: "loss_of_relationship_and_identity"
    change: "accept_powerlessness"
  
  # Layer 5
  threads:
    - name: "humiliation_spiral"
      role: "main"
      support_function: "escalates_mc_exposure"
    - name: "rival_perspective"
      role: "subplot"
      support_function: "shows_contrast"
  
  # Layer 6
  carriers:
    characters:
      - role: "mc"
        name: "[author-defined]"
        inadequacy: "emotional_unavailability"
      - role: "partner"
        name: "[author-defined]"
      - role: "rival"
        name: "[author-defined]"
  
  # Layer 7
  representation:
    act_structure: "setup_escalation_confrontation"
    scene_pacing: "accelerating_reveals"
  
  # Layer 8
  modulation:
    pov: "limited_mc"
    tone: "suffocating_intimacy"
    voice: "[author-defined]"
  
  # Layer 9
  thematic_core:
    theme: "limits_of_love_vs_adequacy"
    motifs:
      - "powerlessness"
      - "proximity"
  
  # Author reflection
  rationale: "[Generated description of why each choice cascades]"
  decision_log: "[Record of all phases and choices]"
  
  genre_shift_override: null  # or blending definition if declared
```

### 6.2 Integration with Auteur CLI

```bash
# Step 1: Run netorare pipeline (outputs story_identity.yaml)
auteur netorare init ./my_story --provider anthropic

# Step 2: Seed blueprint from identity
auteur blueprint seed ./my_story/story_identity.yaml \
  --output ./my_story/blueprint.yaml

# Step 3: Run diagnostics
auteur structure diagnose ./my_story/blueprint.yaml
```

---

## 7. Validation Rules Summary

### Deterministic Checks (Enforced by Pipeline)

| Check | Trigger | Action |
|-------|---------|--------|
| Want ≠ Change | Layer 4 | Reject, show alternatives |
| Resistance blocks Want | Layer 4 | Reject, explain how |
| Thread supports Want | Layer 5 | Reject, filter options |
| Character roles present | Layer 6 | Reject, require selection |
| Act structure matches core | Layer 7 | Enforce (no choice) |
| Theme resonates with all layers | Layer 9 | Reject + show mismatches |
| Genre shift has narrative function | Override | Reject if arbitrary |

### Non-Blocking Warnings

- Subgenre modifiers unknown or rarely used with this core → WARN, allow override
- Theme is unconventional for this core → WARN, allow if author approves
- POV choice is uncommon for emotional core → WARN, allow

---

## 8. Implementation Scope

### In Scope
- ✅ Interactive browser UI (9-phase decision tree)
- ✅ Real-time 9-layer visualization
- ✅ Deterministic validation (20+ rules)
- ✅ Story identity YAML output
- ✅ Three distinct emotional core templates
- ✅ Pause-for-review checkpoints
- ✅ Genre shift override system
- ✅ CLI integration (`auteur netorare init`)

### Out of Scope
- Recommendation engine (this is guided discovery, not recommendation)
- LLM prose generation (pipeline output feeds existing auteur commands)
- Cartographer outline generation (separate downstream step)
- Blueprint editing UI (authors edit YAML or use existing CLI)

---

## 9. Success Criteria

1. ✅ Authors can select one emotional core and progress through all 9 layers without getting stuck
2. ✅ Each phase shows real-time cascade of prior choices into downstream layers
3. ✅ Validation rejects incoherent choices with clear explanations
4. ✅ Output story_identity.yaml passes deterministic validation
5. ✅ Authors understand why each choice matters (learning goal met)
6. ✅ Genre blending via override works correctly (rare, intentional, validated)

---

## 10. Open Questions / Future Exploration

- Should the pipeline support "undo" to go back and change prior decisions?
- Should pipeline track "confidence scores" on each decision (how locked-in is this choice)?
- Should there be a "playback" mode where authors can see alternate decision chains?
- Should the pipeline generate a "rejected directions" list showing what was ruled out?

---

**Design approved:** 2026-07-07  
**Next step:** Implementation plan via writing-plans skill
