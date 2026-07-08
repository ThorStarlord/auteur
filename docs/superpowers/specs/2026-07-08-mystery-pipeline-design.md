# Mystery Genre Pipeline Design Specification

**Date:** 2026-07-08  
**Status:** Design Approved  
**Author:** Claude  
**Related:** [Netorare Pipeline Design](2026-07-07-netorare-pipeline-design.md)

## Executive Summary

The Mystery genre pipeline extends auteur's netorare framework to support three distinct mystery emotional cores: **Howdunit** (intellectual satisfaction), **Paranoia** (dread/uncertainty), and **Cozy** (comfort with resolution). All three cores use the same 9-layer decision tree interface, session management, browser UI, and CLI infrastructure as netorare, with only the genre-specific templates, validation rules, and identity generation requiring new implementation.

**Expected deliverables:** Three core template classes, genre-specific validation rules, identity generator (reuses netorare's shared infrastructure), ~1,500 LOC, 40-50 tests.

---

## Part 1: Genre Architecture & Emotional Cores

### Core 1: Howdunit (Classic Detective Mystery)

**Primary Emotional Arc:** Curiosity → Confusion → Accumulation of Clues → Breakthrough → Intellectual Satisfaction

**Narrative Intent:** Reader solves alongside detective. Every clue was pointing to the truth; the revelation feels earned and inevitable.

**Layer 4 Structural Forces:**

| Force | Definition | Example |
|-------|-----------|---------|
| **Want** | What the protagonist needs to discover/accomplish | Solve the puzzle, identify the culprit, restore order |
| **Resistance** | What makes discovery difficult | Misleading clues, false suspects, hidden motives, misdirection |
| **Conflict** | The core tension driving investigation | Deduction vs. misdirection; reader is in contest with author |
| **Stakes** | What happens if mystery isn't solved | Injustice remains, culprit escapes, order unrestored |
| **Change** | How protagonist's understanding transforms | From confusion to clarity, suspicion to certainty, chaos to coherence |

**Reader Experience at Completion:**
- "Ah! It all makes sense now."
- "I should have caught that clue."
- "The evidence was fair; I lost this puzzle, not the author."

**Validation Constraints:**
- Clue count proportionate to story length (mystery of 10k words should have 8-12 clues, not 3 or 50)
- Red herrings don't contradict central solution (a clue pointing to Suspect A must not directly prove Suspect B is guilty)
- Final solution must be derivable from clues present in text (reader could theoretically solve it)
- Want ≠ Change (protagonist can't "want to solve the puzzle" if protagonist ends in "solved the puzzle" state — must show journey)

**Genre Options by Phase:**

Phase 1 (Emotional Core): howdunit  
Phase 2 (Genre Contract): detective, procedural, locked-room, puzzle-box  
Phase 3 (Scope): focused (single crime, contained), standard (multi-faceted crime, wider cast), expanded (serial crimes, city-scale)  
Phase 4 (Structural Forces): want, resistance, conflict, stakes, change (user-specified)  
Phase 5-9 (Metadata): investigation style (logical, intuitive, procedural), pacing, risk tolerance, confidence, alternatives

---

### Core 2: Paranoia (Psychological Thriller / Unreliable Mystery)

**Primary Emotional Arc:** Trust → Doubt → Growing Dread → Paranoia Peak → Crisis/Revelation

**Narrative Intent:** Reality fractures. By the climax, reader cannot trust their own reading of events — something fundamental shifted. The truth may be ambiguous.

**Layer 4 Structural Forces:**

| Force | Definition | Example |
|-------|-----------|---------|
| **Want** | What protagonist thinks they need | Understand what's happening, escape the situation, prove they're sane |
| **Resistance** | What creates uncertainty | Unreliable narrator, gaslighting, hidden agendas, contradictory evidence |
| **Conflict** | The core tension | Reality vs. Perception; can't trust senses, allies, or memory |
| **Stakes** | What's at risk | Mental stability, safety, truth of reality, identity |
| **Change** | How understanding transforms | Shift in what protagonist (and reader) believe is real (not necessarily resolution) |

**Reader Experience at Completion:**
- "I don't know what's real anymore."
- "Wait... was that real?"
- "The unreliability was the point."

**Validation Constraints:**
- Unreliable narrator inconsistencies must be deliberate (not author error)
- Gaslighting has narrative purpose (not random cruelty for shock value)
- Paranoia escalates logically (each new revelation compounds doubt)
- Reader can theoretically catch the deception (breadcrumbs exist for second reads)
- Want ≠ Change (protagonist can't "want to understand reality" if ending is "understood reality" — ambiguity must remain possible)

**Genre Options by Phase:**

Phase 1 (Emotional Core): paranoia  
Phase 2 (Genre Contract): gaslight, conspiracy, psychological-horror, unreliable-narrator  
Phase 3 (Scope): intimate (1-2 characters, internal), contained (household/institution), sprawling (conspiracy reaches wider)  
Phase 4 (Structural Forces): want, resistance, conflict, stakes, change (user-specified)  
Phase 5-9 (Metadata): narrator reliability (how much they know/lie), truth ambiguity (is solution revealed or ambiguous?), pacing, risk tolerance, confidence, alternatives

---

### Core 3: Cozy Mystery

**Primary Emotional Arc:** Comfort Zone → Curiosity → Light Investigation → Gathering → Resolution & Restored Comfort

**Narrative Intent:** Investigation is a side quest in an inherently safe world. The murder is serious but the world around it is warm, funny, supportive. Resolution doesn't shatter the community.

**Layer 4 Structural Forces:**

| Force | Definition | Example |
|-------|-----------|---------|
| **Want** | What protagonist seeks (in safe context) | Solve the mystery within their small community |
| **Resistance** | What slows investigation (low-stakes) | Clues scattered, witnesses reluctant, community politics, daily life interrupts |
| **Conflict** | The core tension | Investigation vs. daily life, justice vs. community bonds |
| **Stakes** | What matters most | Justice and closure, maintaining community relationships, personal growth |
| **Change** | How world transforms | Community dynamics shift, mystery resolved, comfort restored with new understanding |

**Reader Experience at Completion:**
- "That was cozy and satisfying."
- "I want to live in this world."
- "Justice was served, and the community survived intact."

**Validation Constraints:**
- Violence is off-page or minimal (murder happened, but graphic horror doesn't belong)
- Tone remains light/warm despite serious subject matter
- Community relationships are nuanced (not simple good vs. evil villains)
- Culprit is often sympathetic (understandable motive, not evil for evil's sake)
- Resolution doesn't dismantle the community (no "villain was the beloved baker and everyone turns on them" → instead, "beloved baker made mistake for love, community finds path forward")

**Genre Options by Phase:**

Phase 1 (Emotional Core): cozy  
Phase 2 (Genre Contract): small-town, bookshop, village, domestic, culinary  
Phase 3 (Scope): micro (household, shop), village (tight community), regional (interconnected small towns)  
Phase 4 (Structural Forces): want, resistance, conflict, stakes, change (user-specified)  
Phase 5-9 (Metadata): humor level, relationship focus, violence budget (none/off-page/minimal), community importance, confidence, alternatives

---

## Part 2: Implementation Tasks

### Task 1: Mystery Core Templates

**Files:**
- Create: `src/auteur/mystery/core_templates.py` (parallel to netorare structure)
- Test: `tests/mystery/test_core_templates.py`

**What it produces:**
- `HowdunitTemplate` class with 9-phase decision tree
- `ParanoiaTemplate` class with 9-phase decision tree
- `CozyTemplate` class with 9-phase decision tree
- Each with `get_options(phase)`, `get_constraints(phase)`, `validate_choices(choices)` methods
- Factory function `get_template(core_id)` returning appropriate template instance

**Test count:** ~15 tests (similar to netorare's 5, but covering three templates)

**Interface to Task 2:**
- Templates return option IDs (e.g., "puzzle-box", "contained-scope", etc.)
- Validation rules accept template + choices dict for checking constraints

---

### Task 2: Mystery Validation Rules

**Files:**
- Create: `src/auteur/mystery/validation.py` (parallel structure to netorare)
- Test: `tests/mystery/test_validation.py`

**What it produces:**
- `ValidationRule` class (reuse netorare's pattern)
- `RuleSet` class building mystery-specific rules
- `validate_choices(template, choices)` returning `(is_valid, errors, warnings)`

**Howdunit-specific rules:**
1. `clue_count_proportional`: Story must have clue count matching length estimate
2. `red_herring_coherence`: Red herrings don't directly contradict solution
3. `solution_derivable`: All clues present; solution is theoretically discoverable
4. `want_not_equal_change`: Want (discover truth) ≠ Change (discovered it)

**Paranoia-specific rules:**
1. `narrator_inconsistency_deliberate`: Inconsistencies are flagged as intentional
2. `gaslighting_has_purpose`: Gaslighting moments serve narrative function
3. `paranoia_escalates`: Doubt escalates logically through acts
4. `want_not_equal_change`: Want (understand reality) ≠ Change (reality state)
5. `truth_ambiguity`: Solution has breadcrumbs for second readings

**Cozy-specific rules:**
1. `violence_budget_respected`: Violence stays within declared budget
2. `tone_consistency`: Warm tone maintained despite serious subject
3. `community_relationships_nuanced`: Relationships are complex, not binary
4. `culprit_sympathetic`: Culprit's motive is understandable
5. `community_intact_after_resolution`: Ending doesn't destroy community bonds

**Test count:** ~20 tests (mix of template-specific and general mystery rules)

**Interface to Task 3:**
- Validation runs before identity generation
- Returns errors + warnings; identity generator raises ValueError if errors present

---

### Task 3: Mystery Identity Generator

**Files:**
- Reuse: `src/auteur/identity_generator.py` (existing code is genre-agnostic)
- Add: `tests/mystery/test_identity_generator.py` (mystery-specific tests)

**What it does:**
- `IdentityGenerator.from_choices(core_id="howdunit"|"paranoia"|"cozy", choices)` → `StoryIdentity`
- Validates mystery choices using Task 2 validation
- Transforms 9 layers of mystery choices → StoryIdentity.yaml
- Routes core_id to appropriate Genre enum (e.g., MYSTERY)

**Mystery-specific transformations:**
- Layer 1 (Emotional Core) → `TargetExperience.primary` = "puzzle-solving" | "paranoia" | "comfort"
- Layer 2 (Genre Contract) → `StoryType.genre` = MYSTERY + subgenre metadata
- Layer 4 (Structural Forces) → `central_engine.want`, `.resistance`, `.change`, `.stakes`, `.conflict`
- Layers 5-9 → metadata fields (investigation_style, gaslighting_purpose, violence_budget, etc.)

**Test count:** ~12 tests verifying mystery choices → YAML with correct genre routing

**Integration:**
- No new code; existing IdentityGenerator handles all three mystery cores
- Uses netorare's factory pattern for template loading

---

## Part 3: Reuse Architecture (Tasks 4-7)

All existing infrastructure is genre-agnostic and reuses netorare:

### Task 4: Session State Management
- `src/auteur/mystery/session.py` → **No new file needed**, reuse netorare's SessionManager
- Session stores: `{id, core_id: "howdunit"|"paranoia"|"cozy", choices, status, timestamp}`

### Task 5: Browser HTTP Server
- `src/auteur/mystery/browser/server.py` → **No new file needed**, reuse netorare's NetorareServer
- Server routes: `/session`, `/session/update`, `/session/complete`, `/session/validate`
- Same validation pipeline, same CORS headers, same error handling

### Task 6: Browser UI
- `src/auteur/mystery/browser/index.html` → **No new file needed**, reuse netorare's UI
- Same 9-phase decision tree, real-time layer cascade preview
- Same pause-for-review checkpoints, auto-transition

### Task 7: CLI Entry Point
- CLI command: `auteur mystery init ./my_story --core howdunit|paranoia|cozy`
- Reuses netorare's orchestration: create session → start server → open browser → poll → generate identity → cleanup

---

## Part 4: Integration & Validation

### How CLI Routes to Mystery
```
auteur mystery init ./project --core howdunit
  ↓
cli_mystery.py (new, parallel to cli_netorare.py)
  ↓
SessionManager.create_session(project, core_id="howdunit")
  ↓
NetorareServer (no changes needed; genus-agnostic)
  ↓
Browser UI (no changes needed)
  ↓
IdentityGenerator.from_choices(core_id="howdunit", choices)
  ↓
Validation (mystery-specific rules)
  ↓
story_identity.yaml (Genre.MYSTERY with howdunit metadata)
```

### Cross-Genre Testing
Generated mystery YAML must:
1. Pass `auteur identity validate story_identity.yaml`
2. Integrate with existing `auteur blueprint` commands
3. Maintain backward compatibility with netorare pipeline
4. Generate deterministic output (same choices → same YAML)

---

## Part 5: Testing Strategy

**Unit Tests (per-task):**
- Task 1: Template instantiation, option retrieval, constraint validation
- Task 2: Individual rule validation, rule conflict detection, error message clarity
- Task 3: Choice transformation, YAML serialization, genre routing

**Integration Tests:**
- End-to-end: Create mystery session → select howdunit choices → generate YAML → pass auteur identity validate
- All three cores (howdunit, paranoia, cozy) tested
- Boundary cases: minimal choices, maximal choices, invalid cascades

**Regression Tests:**
- Netorare pipeline remains unaffected
- Existing auteur commands work with mystery-generated identity files

**Expected test count:** 40-50 total (15 Task 1 + 20 Task 2 + 12 Task 3)

---

## Part 6: Design Decisions & Rationale

### Q1: Why three cores instead of options?
**A:** Each core has fundamentally different validation constraints and emotional progression. Treating them as "mystery with style flags" would require conditional validation logic throughout. Separate template classes enforce coherence per core.

### Q2: Reuse all of Tasks 4-7?
**A:** Yes. Session management, HTTP server, UI, and CLI are genre-agnostic. The only genre-specific code is templates (Layer 1-3 options), validation (Layer 4 constraints), and identity routing. This validates the netorare architecture's generalizability.

### Q3: Why validate paranoia stories if truth is ambiguous?
**A:** Ambiguity is a feature, not a cop-out. Validation ensures ambiguity is *intentional* — gaslighting serves a purpose, unreliability has breadcrumbs for second reads, paranoia escalates logically. Unvalidated ambiguity is just confused writing.

### Q4: Why separate cozy violence budget from paranoia threat intensity?
**A:** Cozy readers expect safety; paranoia readers expect escalating threat. A "violence budget" in cozy (off-page, minimal) is the right constraint; paranoia needs "threat intensity" (escalating, justified). Different narratives, different controls.

---

## Part 7: Deliverables Checklist

- [ ] `src/auteur/mystery/core_templates.py` — HowdunitTemplate, ParanoiaTemplate, CozyTemplate classes
- [ ] `src/auteur/mystery/validation.py` — Mystery-specific validation rules + RuleSet
- [ ] `tests/mystery/test_core_templates.py` — 15 unit tests for templates
- [ ] `tests/mystery/test_validation.py` — 20 unit tests for validation
- [ ] `tests/mystery/test_identity_generator.py` — 12 integration tests for identity generation
- [ ] `src/auteur/cli_mystery.py` — CLI entry point (can reuse most of cli_netorare.py)
- [ ] End-to-end test: `auteur mystery init ./test_mystery --core howdunit` succeeds
- [ ] Verification: Generated YAML passes `auteur identity validate`

---

## Part 8: Success Criteria

**Spec Compliance:**
- ✅ Three distinct emotional cores with separate validation rules
- ✅ All mystery choices generate valid story_identity.yaml
- ✅ Generated identity routes to Genre.MYSTERY
- ✅ Netorare pipeline unaffected

**Code Quality:**
- ✅ Mirrors netorare architecture (same patterns)
- ✅ Comprehensive test coverage (40-50 tests)
- ✅ Type hints throughout
- ✅ Clear error messages from validation

**Integration:**
- ✅ Downstream auteur commands accept mystery-generated identity
- ✅ CLI provides identical UX to netorare (same command pattern)
- ✅ Browser UI renders mystery templates without modification

---

## Next Steps

1. **Write Implementation Plan** — Tasks 1-3 with detailed steps, test code, validation examples
2. **Subagent-Driven Execution** — Fresh implementer per task, task review after each
3. **End-to-End Verification** — Run `auteur mystery init ./test_story --core howdunit` and validate full pipeline
4. **Code Review** — Broad architectural review ensuring generalizability

