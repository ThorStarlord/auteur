# Problem Frame

## 1. Raw Fog
The user wants to transition the Auteur codebase to be a "whole-story structure engine first and a chapter drafting engine second." We need to perform Full Fog Path diagnostics to understand the codebase boundaries, knowns/unknowns, and recommend downstream implementation workflows.

## 2. Problem Under the Problem
Auteur is designed to engineer long-form fiction. A common issue with long-form story generation is "narrative drift"—lore inconsistencies, character location teleportations, and plot holes—which accumulate when generating chapter-by-chapter without a global structural constraint engine.
To solve this, Auteur defines a 9-Layer Engine where higher layers (Target Experience, Promise, Scope, Structural Forces) cleanly cascade and dictate the lower layers (Carriers, Representation, Modulation, Resonance).
However, the codebase currently contains a mix of drafting critics, cartographer outlines, and structural analyzers. The problem under the problem is that we need to:
1. Identify the current implementation status of each of the 9 layers.
2. Determine how tightly coupled the drafting engine (Layer 8) is to the structural layers (Layers 1-7).
3. Evaluate the completeness of the `StoryStateManager` and proposal lifecycles which manage this state.
4. Establish a clean transition path where structural validation must pass before drafting begins.

## 3. Object Under Pressure
The objects under pressure in this transition are:
- `src/auteur/structure/state.py` (`StoryStateManager` implementation)
- `src/auteur/cli.py` (specifically `auteur identity`, `auteur structure`, and `auteur audit` CLI commands)
- The relationship between `StoryBlueprint` schemas, the analyzer, and the drafting pipeline
- The roadmap for `auteur state` commands described in `docs/prd-story-state-commands.md`

## 4. Failure Mode
If the transition is not framed and executed correctly:
- The structural validation layer will remain a passive checker rather than a gatekeeper for chapter drafting.
- Chapter drafting will continue to drift from the Story Bible, causing lore rot.
- The system will allow "author override cheats" where the LLM inserts fake overrides to bypass validation instead of correcting the story spine.
- We will end up with high-complexity code that authors cannot easily control or debug.

## 5. Success Condition
The success condition is a comprehensive diagnostic brief and an actionable implementation plan that:
1. Audits the 9 layers of the codebase to identify what exists, what is stubbed, and what is missing.
2. Explains how the `StoryStateManager` orchestrates state validation and proposal lifecycles.
3. Specifies the next concrete development steps (e.g. implementing the missing `auteur state` CLI commands or decoupling drafting from outline generation).
4. Outlines a verification plan using the existing test suite and new integration tests.

## 6. What Must Be True
- The existing tests (which currently all pass) must remain green and act as our regression safety net.
- We must not introduce complex LLM calls into what should be deterministic, schema-based, or analyzer-based validation checks.
- We must align our design with Auteur's domain terminology (e.g. Narrative Drift, Location Teleportation, Scope Contract, Proposal Lifecycle).

## 7. Next Artifact
The next artifact in the Full Fog Path workflow is the `unknowns_map` (`artifacts/unknowns_map.md`), which will map out the codebase gaps, boundary uncertainties, and technical unknowns.
