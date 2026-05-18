---
name: Chapter Acceptance Testing (TDD)
description: "An agentic creative QA skill designed to construct and verify chapter contracts (TDD specs) for draft acceptance."
---

# Chapter Acceptance Testing (TDD) Skill

An agentic creative QA skill designed to construct explicit, machine-verifiable "chapter contracts" (TDD specs) from scene outlines *before* drafting begins, and verify completed drafts against these contracts before accepting them into the project database.

## Meta
- **Name**: Chapter Acceptance Testing (TDD)
- **Goal**: Implement Test-Driven Development (TDD) gates for chapter drafts, guaranteeing absolute alignment with story outlines, metrics, and voice guides.
- **Output**: Validated `chapter_contract.yaml` specs and automated critic validation reports.

---

## 1. Cognitive Architecture: Brain vs. Worker

When executing this skill, the agent functions as the **Brain (Cognitive Orchestrator)** while the Auteur CLI operates as the **Worker (Deterministic Executor)**.

- **The Brain (You)**: Evaluates structural scene targets, establishes realistic word-count and description metrics, details specific carrier state transitions (Layer 6 coordinates), defines semantic targets for world clues or theme reveals, and interactively grills the author to approve the contract limits.
- **The Worker (CLI)**: Validates draft files against the contract schema, compiles text statistics, runs structural critics, checks location logs, and prints standard pass/fail reports.

---

## 2. The Interactive Contract Builder Sequence

The agent must walk the author through a strict **5-Phase Sequence** to generate the chapter contract:

### Phase 1: Context Hydration
Before writing the contract, extract the scene specifications:
1. Parse the target chapter's scene card from `cartographer_outline.yaml` (index, POV, location, threads, and want/resistance/conflict forces).
2. Read the active carrier coordinates in the `StoryBible` to determine preconditions.

### Phase 2: Metric & Budget Limits (Pacing)
Establish word count and pacing constraints:
1. Recommend a word count bracket and description density target based on scene intensity (e.g., action scenes are fast/lean; mystery scenes are slow/dense).
2. **Ask One Question**: *"For Chapter 4, your scene outline specifies a tense stealth passage in the dungeon. We recommend a tight budget of 2,200–2,600 words, a 'slow' pacing speed, and an active verb ratio above 70%. Does this align with your targets?"*
3. **Wait for Approval** before locking in metrics.

### Phase 3: State Dynamic Assertions (Continuity)
Define exactly what must change in Layer 6 (Carriers) during this chapter:
1. Identify which characters or items are involved.
2. **Ask One Question**: *"In this chapter, Kael enters the scouts' room and retrieves the Spies Guild insignia. We must assert Kael's coordinate shifts to 'Dungeon Outpost' and the 'Spies Crest' is added to Kael's active inventory. Do you approve these transition assertions?"*
3. **Wait for Approval** before locking in transitions.

### Phase 4: Required Clues & Reveals (Resonance)
Define the semantic check targets for world lore or thematic progression:
1. Retrieve the threads active in the scene outline.
2. **Ask One Question**: *"To advance the main thread and Spies Guild subplot, this chapter must reveal that the scouts were tipped off by Lira. We recommend asserting a semantic check for the clue: 'Lira tipped off the garrison'. What specific dialogue or revelation constraints should we add?"*
3. **Wait for Approval** before locking in reveals.

### Phase 5: Modulation & Style Bounds (Critics Gate)
Establish point-of-view limits and vocabulary restrictions:
1. Recommend strict filters to ban common "slop" words or passive verbs.
2. **Ask One Question**: *"This chapter is restricted to Kael's Third-Person Limited POV. We will write automated checks banning first-person pronouns, as well as the filter-words 'realized', 'suddenly', and 'watched'. Shall we finalize this style contract?"*
3. **Wait for Approval** before compiling the final contract.

Once approved, the agent runs the CLI worker to compile the contract:
```bash
auteur draft compile-contract cartographer_outline.yaml --chapter 4 --output structure/contracts/chapter_04.yaml
```

---

## 3. Chapter Contract Schema (`chapter_04_contract.yaml`)

The compiler outputs a fully-structured TDD contract YAML file:

```yaml
chapter_index: 4
title: "Whispers in the Dark"
metrics:
  word_count_min: 2200
  word_count_max: 2600
  target_pacing: "slow"
  min_active_verb_ratio: 0.70
state_transitions:
  - character: "Kael"
    field: "location"
    assert_before: "Dungeon Passages"
    assert_after: "Dungeon Outpost"
  - character: "Kael"
    field: "inventory"
    action: "add"
    item: "Spies Crest"
required_elements:
  semantic_clues:
    - "scout armor bears the Spies Guild crest"
    - "Lira tipped off the garrison"
modulation:
  point_of_view: "third_person_limited"
  active_pov_character: "Kael"
  banned_vocabulary:
    - "suddenly"
    - "realized"
    - "watched"
```

---

## 4. Verification & Critics Commands

Once the author (or draft engine) completes the chapter draft, the agent runs the CLI verification test suite:

```bash
# 1. Compile the contract spec from the outline card
auteur draft compile-contract cartographer_outline.yaml --chapter 4 --output structure/contracts/chapter_04.yaml

# 2. Run the deterministic and semantic critics to verify draft compliance
auteur draft verify chapter_04_draft.txt --contract structure/contracts/chapter_04.yaml
```
If the test suite exits with `0` (Green), the chapter is approved. If it fails, the CLI outputs a detailed redline error trace for the revision loop.
