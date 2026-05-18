# PRD: Story Grill Narrative Stress-Testing Skill

**Status:** Approved (Conceptual Design Phase)  
**Date:** 2026-05-18  
**Source:** Conceptual Adaptation of Sensemaking & Interface Skills to Auteur  

---

## 1. Problem Statement

Long-form fiction is highly vulnerable to **Narrative Drift**—the accumulation of lore inconsistencies, character contradictions, and spatial anomalies across drafted chapters. 
While Auteur provides deterministic validators (e.g., `auteur structure diagnose` for Layer 1–5 blueprint coherence, and `auteur audit` to flag Layer 6 Location Teleportation in the event log), there is no dedicated, agent-guided workflow to **stress-test proposed chapter outlines, scene beats, and character trajectories before drafting**.

Without a structured, cognitive mechanism for stress-testing narrative plans against existing world rules and story facts:
1. **Lore rot goes undetected**: Authors accidentally introduce world-rule or genre violations that are not caught until deep into drafting.
2. **State contradictions bypass outlines**: Characters act with knowledge they do not have, carry items they did not retrieve, or appear in places without travel events.
3. **Drafting is inefficient**: AI drafting critics are forced to review raw, inconsistent outlines, leading to wasted generation costs and high rework rates.

---

## 2. Solution Overview

Introduce the **Story Grill** (`story-grill`) skill—a dedicated narrative stress-testing tool that acts as the interactive gatekeeper between structural planning (Layers 1-5) and prose execution (Layers 7-8). 

The Story Grill skill:
- **Interrogates** a proposed chapter outline, scene card, or character arc against the existing `StoryBible` (Layer 6) and project constraints (Layer 2).
- **Surfaces** contradictions as structured **Decision Packets** (proposals).
- **Grills** the author on how to resolve the drift, recommending solutions that preserve creative intent.
- **Applies** the selected resolution by programmatically updating the outline or Story Bible records.

---

## 3. User Stories

### Author Experience
1. **As an author**, I want to stress-test my chapter outlines against my world rules before drafting, so that I can catch lore inconsistencies early before writing prose.
2. **As an author**, I want the agent to present logical or lore contradictions as clear, explicit Decision Packets, rather than simple error tracebacks.
3. **As an author**, I want the agent to recommend a specific resolution option and explain *why* it aligns with my established `story_identity.yaml` constraints.
4. **As an author**, I want resolved grilling decisions (e.g., adding an intermediate travel scene) to be merged back into the Story Bible or outline files automatically without manual edits.

### Agent & Tooling Experience
5. **As an agent**, I want a structured cognitive sequence to guide my grilling, ensuring that I hydrate context, check for drift categories, and present options systematically.
6. **As an agent**, I want standard, machine-readable command contracts (`auteur audit --repair` and `auteur audit --accept`) to execute my structural/lore resolutions on disk.
7. **As a developer**, I want a clear separation between the initial creative fog reduction (`story-identity-architect`) and execution-time narrative stress-testing (`story-grill`), so that my agent-level prompts remain clean and focused.

---

## 4. Key Implementation Decisions

### Target Scope & Layers
The Story Grill skill operates primarily on the intersection of three key layers in the 9-Layer Engine:
- **Layer 2 (Promise/Constraints)**: Stress-tests against medium, mode, genre boundaries (*What This Is Not*).
- **Layer 6 (Carriers)**: Stress-tests against active character states, location logs, item inventories, and faction relationships in the `StoryBible`.
- **Layer 7 (Representation)**: Validates that the proposed scene cards, outline cards, or raw chapter beats execute the structural forces declared in the blueprint.

### Standard Drift Categories
The skill systematically checks for four categories of narrative drift:

| Drift Category | Check | Example Contradiction |
|---|---|---|
| **Lore Drift** | Verifies adherence to the world laws and constraints in Layer 2. | A character casts an active spell in a low-magic zone defined in "What This Is Not". |
| **Spatial / Spatial Drift** | Traces carrier location transitions (detects **Location Teleportation**). | Aldric enters the dungeon in Chapter 5, but the Bible states he is currently in the Throne Room. |
| **Inventory Drift** | Verifies ownership and access to world items or keys. | Lira uses the Shattered Crown, which is currently recorded as locked in the tyrant's treasury. |
| **Motivation Drift** | Checks character choices against core structural forces (Layer 4). | The protagonist surrenders their want without a matching resistance scene or stakes collision. |

### CLI Command Integration
The Story Grill skill orchestrates Auteur's CLI audit command family to transition from diagnostic to resolution:
```bash
# 1. Hydrate and run diagnostic sweep to generate Decision Packets
auteur audit --repair <project_directory>

# 2. Apply the author-approved resolution option to update the Bible/outlines
auteur audit --accept <proposal_id> --option <option_id>
```

---

## 5. Testing & Verification

1. **Diagnostic Heuristics Tests**: Unit tests must assert that `auteur audit --repair` correctly generates `StructureProposal` YAML files with `source_domain = "bible_audit"` when spatial or inventory inconsistencies are simulated.
2. **Mock Interactive Session Tests**: Verification scripts must simulate an agent-author grilling loop, showing that when an option is selected, `auteur audit --accept` successfully stamps the resolution on disk without corrupting the main `blueprint.yaml`.

---

## 6. Out of Scope

- **Automated Prose Modulation**: The Story Grill is not a prose editor or style critic (which belongs to Layer 8 Prose Critics). It focuses entirely on narrative consistency, world logic, and outline alignment.
- **Automatic Story Rewriting**: The skill must *never* silently rewrite the story spine or inject plot events without explicit, interactive author approval.
