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

## Flagged ambiguities

- "audit" could mean checking blueprint coherence (structure diagnostics) or
  checking Bible/chapter consistency (Bible audit). Resolved: structure
  diagnostics check within-blueprint coherence; Bible audit checks
  cross-chapter carrier state consistency.
