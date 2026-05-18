# ADR 008: Rich Target Experience As Layer 1 Master Emotional Promise

## Status

Accepted

## Context

Auteur's Layer 1 (`TargetExperience`) originally had a very basic schema, capturing only a single primary emotion, a progression string, and a list of avoided feelings.
This was too simple to represent complex stories, where genre emotion is not static. Stories may have dynamic emotional trajectories, multi-genre emotional stacks, or distinct, POV-specific emotional contracts.
However, attempting to model every scene-level emotion or POV micro-mood variation at Layer 1 would overcomplicate the engine, as that tone modulation belongs in downstream layers (like Layer 8: Modulation).

## Decision

Redesign and expand `TargetExperience` to capture the master emotional promise, allowed emotional palette, and macro emotional trajectory of the story without adding micro-modulation details.

The schema will support two representations:

1. **Full / Rich Representation**:
   - `primary_emotional_promise`: The dominant, governing emotional product sold.
   - `secondary_palette`: A list of supporting allowed/useful emotions.
   - `avoided_experiences`: Concepts and tones that must be avoided.
   - `emotional_trajectory`: The macro emotional transitions (`pattern`, `start`, `midpoint`, `ending`).
   - `genre_emotion_stack`: A mapping/registry of genre-emotion roles (e.g. primary, secondary, tertiary genre expectations).
   - `pov_experience_contracts`: Optional, role-specific audience feeling and thematic functions (e.g. for protagonist, antagonist).

2. **Simplified / Beginner Representation**:
   - `primary`: Standard main emotional promise.
   - `progression`: Macro emotional sequence/pattern.
   - `secondary`: Key supporting emotions.
   - `avoid`: List of avoided feelings.

The Pydantic schema will seamlessly coerce inputs and synchronize properties bidirectionally so that:
- Any blueprint/identity using either format parses successfully.
- Code accessing legacy fields like `.primary`, `.progression`, and `.avoid` continues to function with zero changes.

Two narrow validation rules are added to the structure analyzer:
- `target_experience.genre_emotion_stack.primary_mismatch`: Enforces that the primary genre-emotion in the stack aligns with the primary emotional promise.
- `target_experience.pov_contract.unknown_character`: Enforces that any POV-specific contract references a character that is declared in the blueprint characters list.

## Consequences

- Authors can express rich emotional structures in their creative briefs and story blueprints.
- Auteur remains easy to use for beginners, who can use a simplified, four-field format.
- Backward compatibility is fully preserved for all existing blueprints, tests, and CLI outputs.
