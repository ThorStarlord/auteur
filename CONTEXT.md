# Genre Pipeline Architecture Context

This document describes the proven architecture for extending auteur with new genres and provides architectural context for navigating the codebase.

## The 9-Layer Genre Pipeline

Auteur's genre pipeline is a deterministic narrative engine with 9 decision layers that guide authors through emotional coherence. Each genre implements the same 9-layer structure with genre-specific content and validation.

### The 9 Layers

1. **Emotional Core** (Layer 1)
   - User selects primary emotional arc (e.g., Humiliation, Horror, Mystery for Netorare)
   - This gates all downstream choices
   - Example: `core_id="humiliation"` routes to HumiliationTemplate

2. **Genre Contract** (Layer 2)
   - Author commits to genre-specific narrative promises
   - Examples: "Netorare: protagonist loses control", "Mystery: killer is revealed", "Gentle Femdom: consent is explicit"
   - Sets narrative boundaries

3. **Scope** (Layer 3)
   - Define the story's reach and scale
   - Examples: intimate pair, expanding circle, community dynamic, world-affecting

4. **Structural Forces** (Layer 4)
   - Five core narrative forces: Want, Resistance, Conflict, Stakes, Change
   - Genre-specific meanings (e.g., Humiliation wants != Mystery wants)

5-9. **Metadata Layers** (Layers 5-9)
   - Layer 5: Tone / Atmosphere / Emotional texture
   - Layer 6: Pacing / Narrative structure
   - Layer 7: Perspective / Point of view
   - Layer 8: Intimacy / Scope refinement
   - Layer 9: Ratification / Final validation

### Implementation Pattern

Each genre implements three class hierarchies:

**1. Templates** (`src/auteur/{genre}/core_templates.py`)
Each template class provides:
- core_id: Unique identifier
- primary_emotion: Core feeling
- phases: dict with 9-phase decision tree
- get_options(phase): List of selectable options
- get_constraints(phase): Validation constraints
- validate_choices(choices): Genre-specific validation

Three template classes per genre, one per emotional core.

**2. Validation Rules** (`src/auteur/{genre}/validation.py`)
- ValidationRule: Enforces one constraint
- RuleSet: Dispatcher collecting all rules
- 12-15 rules per genre (4 per emotional core)
- Each rule validates specific narrative integrity requirements

**3. Identity Generation** (`src/auteur/netorare/identity_generator.py`)
- IdentityGenerator.from_choices(): Transform choices to StoryIdentity
- IdentityGenerator.to_yaml(): Serialize to YAML
- Routing tables map all cores to their genres
- Generated YAML passes `auteur identity validate`

### Shared Infrastructure (Reused Across All Genres)

These components are genre-agnostic and shared:

**Session Management** (`src/auteur/netorare/session.py`)
- SessionManager: File-based JSON session state with atomic writes
- Tracks phase progression, choices, validation results
- All genres use same SessionManager

**Browser HTTP Server** (`src/auteur/netorare/browser/server.py`)
- NetorareServer: Reused for all genres (no modifications)
- Serves /session, /session/update, /session/complete, /session/validate
- Provides endpoints for browser UI

**Browser UI** (`src/auteur/netorare/browser/index.html`)
- Vanilla JavaScript decision tree interface
- Generic phase/option/constraint rendering
- All genres reuse same UI (no modifications)

**CLI Dispatcher** (`src/auteur/cli.py`)
- Routes `auteur {genre} init --core {core_id}` to genre-specific handlers
- Each genre provides its own handler class

### Port Allocation

Each genre gets a unique port to avoid collisions:
- Netorare: 8765
- Mystery: 8766
- Gentle Femdom: 8767

## The "No Special Cases" Principle

**Infrastructure must remain genre-agnostic.** If you need to add an `if genre == "netorare"` statement to SessionManager or NetorareServer, the architecture is breaking.

This principle ensures:
- Adding genre N+1 requires only template/validation/identity code (3 files)
- No infrastructure changes needed
- Each genre scales independently

**Validation:** Three genres implemented with zero infrastructure changes = pattern is production-ready.

## File Organization

```
src/auteur/
├── cli.py                                    Main dispatcher
├── cli_netorare.py                           Netorare handler
├── cli_mystery.py                            Mystery handler
├── cli_gentlefemdom.py                       Gentle Femdom handler
│
├── netorare/                                 Shared infrastructure
│   ├── session.py                            SessionManager
│   ├── identity_generator.py                 IdentityGenerator + routing
│   ├── core_templates.py                     Netorare: 3 cores
│   ├── validation.py                         Netorare: 15 rules
│   └── browser/
│       ├── server.py                         NetorareServer (shared)
│       └── index.html                        UI (shared)
│
├── mystery/                                  Genre-specific
│   ├── core_templates.py                     Mystery: 3 cores
│   └── validation.py                         Mystery: 12 rules
│
└── gentlefemdom/                             Genre-specific
    ├── core_templates.py                     Gentle Femdom: 3 cores
    └── validation.py                         Gentle Femdom: 12 rules
```

## Adding a New Genre (Pattern)

To add Genre N+1:

1. **Design** - Define 3 emotional cores and validation rules
2. **Implement Templates** - Create `src/auteur/{genre}/core_templates.py`
3. **Implement Validation** - Create `src/auteur/{genre}/validation.py`
4. **Extend Identity Generator** - Add core_id routing to `src/auteur/netorare/identity_generator.py`
5. **Create CLI Handler** - Create `src/auteur/cli_{genre}.py` with {Genre}Command
6. **Update Main CLI** - Add genre subparser to `src/auteur/cli.py`
7. **Test** - Write 40-50 tests (TDD throughout)

No infrastructure changes needed.

## The 3-Genre Threshold

Three different genres implemented with zero infrastructure modifications = the architecture is proven production-ready. Auteur has reached this threshold:

- Netorare (Humiliation, Horror, Mystery cores)
- Mystery (Howdunit, Paranoia, Cozy cores)
- Gentle Femdom (Sensual Dominance, Tender Surrender, Romantic Authority cores)

## API Contracts

### Template Contract

Every template must implement:
- phases: dict (9-phase decision tree)
- get_options(phase): List of options
- get_constraints(phase): Validation constraints
- validate_choices(choices): Genre-specific validation

### Validation Rule Contract

Every rule must implement:
- validate(template, choices): Returns (is_valid, errors)

### Identity Contract

Generated YAML must:
- Pass `auteur identity validate {file}.yaml`
- Contain Genre field
- Include selected choices and core_id
- Be consumable by `auteur blueprint seed {file}.yaml`

---

Last Updated: 2026-07-08
Validated Through: Three complete genre pipelines with proven reusability
