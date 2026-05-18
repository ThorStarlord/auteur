# Story Grill Skill

An agentic narrative stress-testing skill designed to interrogate proposed chapter drafts, scene cards, or character arcs against the `StoryBible` state and target constraints. This skill identifies **Narrative Drift** (lore inconsistencies, spatial anomalies, or motivational clashes) and guides the author through an interactive "grill and resolution loop" to update story states inline before drafting begins.

## Meta
- **Name**: Story Grill
- **Goal**: Stress-test proposed narrative outlines/drafts against story facts and rules to achieve 100% lore and continuity consistency.
- **Output**: Resolved scene outlines, updated `StoryBible` state records, and inlined lore corrections.

---

## 1. Cognitive Architecture: Brain vs. Worker

When executing this skill, the agent functions as the **Brain (Cognitive Orchestrator)** while the Auteur CLI operates as the **Worker (Deterministic Executor)**.

- **The Brain (You)**: Hydrates the creative context, maps character trajectories, categorizes lore contradictions, prioritizes narrative drift issues, recommends resolutions based on established creative intent, and interactively grills the author.
- **The Worker (CLI)**: Handles state-transition analysis, event log calculations, backward-compatible proposal generation, and non-destructive metadata updates. You must **never** silently write new events or force characters' locations without routing it through the CLI audit commands.

---

## 2. The Interactive Narrative Grill Loop

The agent must walk the author through a disciplined, step-by-step **4-Phase Sequence** to identify and resolve drift:

### Phase 1: Context Hydration
Before executing any audits, the agent must load and understand the existing narrative structure from the project directory:
1. Parse the target experience and constraints from `story_identity.yaml` or Layer 2 `blueprint.yaml` parameters.
2. Read the active events, character coordinates, and item assignments in the `StoryBible`.
3. Load the proposed chapter outline, scene card, or raw draft beats (Layer 7–8 representation) that the author wants to stress-test.

### Phase 2: Diagnostic & Drift Sweeps
Run the Auteur CLI audit repair engine to compile logical, spatial, and lore contradictions:
```bash
auteur audit --repair <project_directory>
```
- Capture the output diagnostics. If no findings are produced and the command exits with `0` (Zero Drift), skip to Phase 4.
- Parse the output proposal YAML files generated under `structure/proposals/` to identify the specific drift items.

### Phase 3: Priority Grilling & Selection
Do not present findings as a flat, overwhelming questionnaire. Present the unresolved Decision Packets one at a time, ordered by **Drift Priority Tiers**:

1. **Tier 1: Lore Drift** (Layer 2 Constraint violations) - Violations of defined magic systems, history, technology limits, or genre rules.
2. **Tier 2: Spatial Drift** (Layer 6 Location transitions) - Missing travel events or **Location Teleportation** findings.
3. **Tier 3: Inventory Drift** (Layer 6 World items/keys) - A character using or wielding an item they do not carry or that is located elsewhere.
4. **Tier 4: Motivation Drift** (Layer 4 Structural forces) - Sudden character choices that contradict their core wants/resistance without supporting beats.

For each prioritized Decision Packet:
1. **Ask One Question**: Describe the contradiction, cite the exact file-level evidence, and list the 2-3 options.
2. **Provide a Recommendation**: Recommend one option, explaining *why* it aligns with the creative boundaries established in the target experience or identity.
3. **Wait for Approval**: Explicitly wait for the author to select, refine, or reject the recommendation.

---

## 3. Narrative Decision Packet Format (`StructureProposal` YAML)

Decision Packets for narrative stress-testing are stored as `StructureProposal` YAML files with the `source_domain` field set to `"bible_audit"`. This format ensures backward-compatibility and clear command routing:

```yaml
proposal_id: "repair_carriers_location_teleportation_aldric"
source_domain: "bible_audit"
layer: 6
finding: "Location Teleportation"
description: "Aldric enters the dungeon treasury in Chapter 5 scene 2, but the last recorded location in the Bible was the Throne Room (Chapter 3)."
affected_carriers:
  - character: "Aldric"
    field: "location"
repair_options:
  - option_id: "add_travel_scene"
    summary: "Add a transition scene in Chapter 5 scene 1 where Aldric sneaks down the dungeon stair."
    data:
      delta_type: "cartographer_outline"
      action: "insert_scene"
      index: "5.1"
      content: "Aldric sneaks past the guards at the dungeon stair."
  - option_id: "retroactive_travel"
    summary: "Record Aldric's travel to the dungeon in Chapter 4's end-of-scene bible delta."
    data:
      delta_type: "bible_delta"
      action: "update_carrier_state"
      character: "Aldric"
      field: "location"
      value: "Dungeon Treasury"
selection:
  selected_option_id: null
decision:
  resolved_at: null
  author_notes: null
```

---

## 4. Resolution & Verification Commands

Once the author selects a resolution option, the agent executes the change programmatically using the CLI:

### A. Lock & Apply the Resolution
Update the selected option in the proposal YAML file, then run:
```bash
# Accept and execute the option without mutating the structural blueprint.yaml
auteur audit --accept <proposal_id> --option <selected_option_id>
```

### B. Re-Verify Alignment
Run a final audit sweep to ensure the drift is completely resolved:
```bash
auteur audit --repair <project_directory>
```
Once this command returns `0` (Zero violations), compile a brief success summary for the author, highlighting:
*   The resolved lore/continuity gaps.
*   The updated bible events or outline scenes.
*   Confirmation that Layer 6 carriers and Layer 7 representations are 100% aligned and ready for drafting.
