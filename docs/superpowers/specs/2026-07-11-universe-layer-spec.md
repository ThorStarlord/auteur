# Universe Layer Architecture Specification

## Overview

The Universe layer is the top of Auteur's Layered Story Architecture. It defines shared world-building decisions (setting, magic system, timeline, mythology, fundamental rules) that constrain all downstream Series and Books.

## Layer Hierarchy

```
Universe (defines world rules)
    ↓ (constraints flow down)
Series (establishes multi-book continuity)
    ↓ (inherits universe rules)
Book/Story Identity
    ↓ (genre contract)
Blueprint
    ↓ (structural skeleton)
Outline
    ↓ (scene sequence)
Draft
    ↓ (prose)
Editing
    ↓ (validation & refinement)
```

## UniverseIdentity Structure

Each universe is defined in `universe_identity.yaml`:

```yaml
name: Fantasy Realm
slug: fantasy-realm
description: A world where ancient magic awakens
setting_profile:
  setting_type: multi_world
  primary_location: The Realm of Light
  known_locations:
    - The Realm of Darkness
    - The Neutral Void
  worldbuilding_scope: wide
magic_system: Balance between elemental and divine magic
core_mythology: The eternal dance between creation and entropy
timeline:
  current_era: Age of Awakening
  era_description: Magic returns after centuries of dormancy
  years_of_history: 10000
forbidden_elements:
  - Absolute moral certainty
  - Technology beyond medieval
  - Complete resolution of the Light/Dark conflict
required_elements:
  - Moral ambiguity
  - Magic as transformative force
  - References to ancient lore
cross_story_constraints:
  - rule: No story should permanently resolve the Light/Dark conflict
    applies_to_all_stories: true
    severity: required
  - rule: Respect the established timeline; no time travel without justification
    applies_to_all_stories: true
    severity: warning
  - rule: Consider showing the cost of magic use
    applies_to_all_stories: true
    severity: info
```

## CLI Commands

```bash
auteur universe validate <universe_identity.yaml>
  # Validates the universe for completeness and coherence

auteur universe diagnose <universe_identity.yaml>
  # Generates a diagnostic report with warnings and suggestions
```

## Validation Rules

| Rule | Severity | Message |
|------|----------|---------|
| `universe.empty_forbidden_and_required` | warning | Define at least forbidden OR required elements |
| `universe.setting_and_mythology_coherence` | warning | Magic system should have mythology |
| `universe.constraint_severity_balance` | info | Consider mixing required/warning constraints |
| `universe.worldbuilding_scope_specificity` | info | Avoid vague scope; use specific values |

## Integration with Series

Series can reference a Universe:

```yaml
# series_identity.yaml
name: Chronicles of the Realm
slug: chronicles
universe_constraint_path: ../universe_identity.yaml
# ... book plans
```

Series diagnostics will validate against universe constraints.

## Design Rationale

1. **Top-down constraints:** Universe rules flow down; Series/Books inherit them
2. **Deterministic validation:** Same universe → same diagnostic output
3. **Non-breaking integration:** Existing Series can optionally reference a Universe
4. **Flexibility via severity:** Required/warning/info let authors balance constraint vs. creative freedom

## Future Expansion

- Universe inheritance (universes that extend other universes)
- Cross-universe validation for franchise/multiverse work
- Universe templates for common archetypes (fantasy, sci-fi, contemporary, horror)
- Universe version history and backwards compatibility
