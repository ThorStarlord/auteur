# Blueprint to Cartographer Outline Compiler Skill

An agentic outline compiler skill designed to ingest the high-level structural constraints, story engine, and subplots in a finalized `blueprint.yaml` (Layer 5) and compile it into a concrete, chapter-by-chapter `cartographer_outline.yaml` (Layer 7) ready for drafting.

## Meta
- **Name**: Blueprint to Cartographer Outline Compiler
- **Goal**: Translate whole-story structural planning into a balanced, character-aligned scene outline.
- **Output**: Validated `cartographer_outline.yaml` containing want, resistance, conflict, POV, and location coordinates per chapter.

---

## 1. Cognitive Architecture: Brain vs. Worker

When executing this skill, the agent functions as the **Brain (Cognitive Orchestrator)** while the Auteur CLI operates as the **Worker (Deterministic Executor)**.

- **The Brain (You)**: Manages act budgets, distributes subplots strategically to avoid pacing dead-zones, assigns POV characters to scenes to maximize thematic conflict, and interactively grills the author to approve act boundaries and scene engines.
- **The Worker (CLI)**: Validates input schemas, parses structural constants, enforces subplot budgets, and programmatically compiles and validates outline YAML files.

---

## 2. The Interactive Outlining Loop

The agent must walk the author through a strict **5-Phase Sequence**, grilling on one structural boundary at a time to build the complete chapter skeleton:

### Phase 1: Context Hydration
Before executing any outlining, load the core project blueprint:
1. Parse the structural constants (Act counts, Subplot budgets, Max POV characters) in `blueprint.yaml`.
2. Extract the Want, Resistance, Conflict, Stakes, and Change of the Main Thread and all Subplots (Layer 4 & 5).

### Phase 2: Act & Chapter Division (Pacing)
Interactively divide the story scale into act boundaries:
1. Propose an act-to-chapter allocation based on standard pacing guidelines (e.g., 25% Act I, 50% Act II, 25% Act III).
2. **Ask One Question**: *"Your blueprint specifies 24 chapters. We recommend Act I (Chapters 1-6), Act II (Chapters 7-18), and Act III (Chapters 19-24). Does this pacing allocation align with your vision?"*
3. **Wait for Approval**: Adjust act blocks based on the author's input.

### Phase 3: Subplot Webbing & Distribution (Tapestry)
Weave subordinate threads (character arcs, subplots) across the chapters:
1. Locate the subplot list in the blueprint, noting each subplot's scene budget.
2. Interactively propose where to insert subplot beats to maintain momentum.
3. **Ask One Question**: *"Your subplot 'The Spies Guild' has a budget of 3 scenes. We recommend placing these beats in Chapter 4 (introduction), Chapter 11 (midpoint stakes raise), and Chapter 17 (pre-climax reveal). Shall we lock in this distribution?"*
4. **Wait for Approval** before locking in thread placements.

### Phase 4: Carrier & POV Coordinate Alignment (Modulation)
Assign POVs and location coordinates (Layer 6) to each chapter:
1. Parse the character roster and settings list from the blueprint.
2. For each chapter, determine the most impactful POV character and location.
3. **Ask One Question**: *"For Chapter 18 (the climax of Act II), Kael and Lira are in the Dungeon Treasury. We recommend making Lira the POV character here to dramatize Kael's descent into corruption. Do you approve?"*
4. **Wait for Approval** before finalizing chapter coordinates.

### Phase 5: Outline Compilation
Once all coordinates are locked, run the CLI worker to compile the outline skeleton:
```bash
auteur cartographer compile blueprint.yaml --output cartographer_outline.yaml
```

---

## 3. Cartographer Outline Schema (`cartographer_outline.yaml`)

The compiler outputs a fully-structured outline schema conforming to Layer 7 requirements:

```yaml
title: "The Shattered Crown - Scene Outline"
total_chapters: 24
chapters:
  - index: 1
    act: "Act I"
    title: "The Ruined Hearth"
    pov_character: "Kael"
    location: "Ruined Keep"
    threads:
      - "main_thread"
    scene_engine:
      want: "Kael wants to find shelter in the ruins while escaping the winter storm."
      resistance: "The storm has blocked the main gate, forcing him to climb the outer wall."
      conflict: "Kael must risk a dangerous climb in freezing wind or stay exposed in the pass."
      stakes: "If he falls, he dies; if he waits, the cold will kill him."
      change: "Kael reaches the courtyard but is spotted by scouts, losing his mount."
  - index: 4
    act: "Act I"
    title: "Whispers in the Dark"
    pov_character: "Kael"
    location: "Dungeon Passages"
    threads:
      - "main_thread"
      - "spies_guild_subplot"
    scene_engine:
      want: "Kael wants to follow the scouts to locate their outpost."
      resistance: "The passages are rigged with ancient trapdoors and sound alarms."
      conflict: "Kael must advance quickly without triggering mechanisms."
      stakes: "Triggering an alarm alerts the entire garrison, blocking his escape."
      change: "Kael finds the scouts' room and discovers they are wearing Spies Guild crests."
```

---

## 4. CLI Outline & Seeding Commands

The agent uses these CLI tools to execute the worker operations:

```bash
# 1. Compile the blueprint into the scene outline yaml
auteur cartographer compile blueprint.yaml --output cartographer_outline.yaml

# 2. Validate the compiled outline schema and continuity transitions
auteur cartographer validate cartographer_outline.yaml
```
