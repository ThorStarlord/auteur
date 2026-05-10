# Auteur

A narrative engineering toolkit for long-form fiction. Auteur is a whole-story
structure engine first and a chapter drafting engine second.

## Language

**Narrative Drift**:
The accumulation of lore inconsistencies across multiple drafted chapters,
where the Bible state and chapter prose contradict each other.
_Avoid_: Lore rot, continuity error, plot hole (these are symptoms, not the condition).

**Bible Audit**:
A deterministic diagnostic pass that reads the StoryBible event log and
character state to detect impossible state transitions.
_Avoid_: Lore check, consistency scan.

**Location Teleportation**:
A character appears at location A in one Bible event, then location B in
the next consecutive event, with no intermediate event explaining the move.
_Avoid_: Spatial inconsistency, position jump.

**Diagnostic Slice**:
A minimal, independently shippable unit of diagnostic functionality — one
detection rule, its data model, and its CLI wiring.
_Avoid_: Feature, check, validator.

**Character State Change**:
A structured record from the Cartographer outline: `{character, field, before, after}`,
tracking what changed for a character per scene.
_Avoid_: Delta, mutation, update.

**Layer 6 / Carriers**:
Characters, setting, situation, institutions, and world systems that carry or
instantiate structural forces. The Bible tracks carrier state (location,
physical, emotional, inventory, relationships, secrets_known, arc percentage).

**Layer 7 / Representation**:
Plot, events, scenes, reveals, turns, and sequences — visible evidence that
the deeper structure is working. Chapter drafts and final.md live here.

## Relationships

- The **Cartographer** outline produces **Character State Changes** per scene.
- The **Bible** records **Character State Changes** in its event `deltas` during chapter accept.
- A **Bible Audit** reads Bible events, traces **Character State Changes**, and emits
  **Diagnostics** for impossible transitions (e.g., **Location Teleportation**).
- **Narrative Drift** occurs when **Layer 7** (chapter drafts) contradicts **Layer 6**
  (Bible carrier state) across multiple chapters.

## Example dialogue

> **Author:** "My character Aldric was in the Throne Room in chapter 3, but in
> chapter 5 he's suddenly in the Dungeon with no scene showing how he got there."
>
> **Dev:** "That's a **Location Teleportation** — a **Narrative Drift** between
> **Layer 6** Bible state and **Layer 7** chapter representation. A **Bible Audit**
> would catch it by tracing the event log and flagging the missing transition."

**Decision Packet**:
A structured artifact presenting one unresolved contradiction and 2-3 author-facing
options (preserve intent / challenge intent) for resolving it. Stored as a
`StructureProposal` YAML file in `structure/proposals/`.
_Avoid_: Conflict report, resolution prompt, fix suggestion.

**Story State Manager**:
The unified multi-layer audit system that coordinates diagnostics across all 9
structure layers. Extends the existing `auteur audit` command to detect
contradictions at every layer and produce Decision Packets.
_Avoid_: Lore manager, consistency engine.

**Proposal Resolution**:
The act of an author selecting and locking an option in a Decision Packet,
persisting the choice in the proposal YAML's `selection` and `decision` fields.
_Avoid_: Accept, fix, apply.

## Relationships

- The **Cartographer** outline produces **Character State Changes** per scene.
- The **Bible** records **Character State Changes** in its event `deltas` during chapter accept.
- A **Bible Audit** reads Bible events, traces **Character State Changes**, and emits
  **Diagnostics** for impossible transitions (e.g., **Location Teleportation**).
- **Narrative Drift** occurs when **Layer 7** (chapter drafts) contradicts **Layer 6**
  (Bible carrier state) across multiple chapters.
- A **Diagnostic** from any layer can be promoted to a **Decision Packet**
  (a `StructureProposal` YAML) when it has `repair_options`.
- The **Story State Manager** runs all diagnostic rules across all layers and
  emits **Decision Packets** for unresolved contradictions.
- The author performs **Proposal Resolution** by editing the YAML or via
  `auteur audit --accept <id> --option <id>`.

## Example dialogue

> **Author:** "My character Aldric was in the Throne Room in chapter 3, but in
> chapter 5 he's suddenly in the Dungeon with no scene showing how he got there."
>
> **Dev:** "That's a **Location Teleportation** — a **Narrative Drift** between
> **Layer 6** Bible state and **Layer 7** chapter representation. A **Bible Audit**
> would catch it by tracing the event log and flagging the missing transition."
>
> **Author:** "I ran `auteur audit` and it gave me a **Decision Packet** with two options.
> I chose 'preserve_1' to add a transition scene. How do I lock that in?"
>
> **Dev:** "Either edit the `repair_1_carriers_location_teleportation.yaml` in
> `structure/proposals/` and set `selection.selected_option_id` to `preserve_1`,
> or run `auteur audit --accept repair_1_carriers_location_teleportation --option preserve_1`.
> Either way, the **Proposal Resolution** is stored in the YAML and `auteur audit`
> will skip it next time."

## Flagged ambiguities

- "audit" could mean checking blueprint coherence (structure diagnostics) or
  checking Bible/chapter consistency (Bible audit). Resolved: structure
  diagnostics check within-blueprint coherence; Bible audit checks
  cross-chapter carrier state consistency.
