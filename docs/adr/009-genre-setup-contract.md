# ADR 009: Setup Contract and Emotional Runway in Genre Contracts

## Status

Accepted

## Context

Auteur is becoming a whole-story structure engine first and a chapter drafting engine second.
For a story to satisfy genre expectations, it must meet specific **genre contract expectations**, particularly the concept of **Emotional Runway**—the amount of setup (ordinary status quo, bond development, and world establishment) required before the central genre disruption, transformation, or payoff can feel earned rather than mechanically correct or unearned.

For example, relationship-destabilizing genres like *Netorare* and *Netori* require a `long` emotional runway and `required` baseline relationship establishment to make subsequent erosion or intervention emotionally legible and satisfying to the audience.

## Decision

Introduce the `SetupContract` model and integrate it into the `GenreContract` registry schema, all fallback definitions, and all existing genre YAML files.

1. **SetupContract Pydantic Model**:
   - `emotional_runway`: A `NarrativeRunway` enum (e.g., `short`, `medium`, `long`, `very_long`).
   - `relationship_establishment`: A `RequirementLevel` enum defining the burden of relationship setup before payoff.
   - `baseline_world_establishment`: A `RequirementLevel` enum defining the burden of normalcy setup.
   - `minimum_setup_beats`: List of required story establishment beats.
   - `forbidden_shortcuts`: Traps/shortcuts that are forbidden in structural setup (e.g., stating bonds purely through exposition).
   - `compression_strategies`: Strategies to deliver the setup within compact formats.

2. **Registry Changes**:
   - Add `setup_contract` to `GenreContract`.
   - Update `_create_fallback_contract` in registry to provide robust defaults.
   - Update `romance.yaml`, `horror.yaml`, `mystery.yaml`, `thriller.yaml`, and `grimdark_fantasy.yaml` to define specific setup contracts.
   - Introduce `netorare.yaml` and `netori.yaml` as first-class, built-in genre contracts.

3. **Structural Diagnostic Rule**:
   - Add the `genre.setup_contract.insufficient_runway` diagnostic check under the `SCOPE` layer in `analyze_structure()`.
   - The diagnostic warns authors if the chosen story container length (e.g., `short_story`, `novella`) is too short to support the genre's required emotional runway.

## Consequences

- The structure engine is now explicitly aware of the scene-budget and setup burden required to satisfy distinct genre contracts.
- Warnings are automatically raised during structural diagnostics if a writer attempts to squeeze a high-setup genre (like Netorare/Netori) into an overly compressed container (like a short story), helping them select the correct length class or apply compression strategies early.
- Registry integrity is fully preserved with robust fallbacks and complete YAML files.
