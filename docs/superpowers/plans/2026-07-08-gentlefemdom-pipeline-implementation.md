# Gentle Femdom Genre Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Implement the Gentle Femdom genre pipeline (sensual dominance, tender surrender, romantic authority cores) with decision trees, validation rules, and identity generation, proving the architecture scales to third genre.

**Architecture:** Three gentle femdom emotional cores each with 9-phase decision tree. Templates and validation are genre-specific; Session, Server, UI, and CLI are reused from netorare without modification.

**Tech Stack:** Python 3.11+, Pydantic (StoryIdentity), YAML serialization, pytest for testing.

## Global Constraints

- Exact file paths: Create under `src/auteur/gentlefemdom/` (parallel to netorare, mystery)
- Template API matches netorare/mystery exactly: `phases` dict, `get_options(phase)`, `get_constraints(phase)`, `validate_choices(choices)`
- Validation API matches netorare/mystery: `ValidationRule` class, `RuleSet` dispatcher, `validate_choices(template, choices)` returning `(is_valid, errors, warnings)`
- Identity Generator routing: `from_choices(core_id="sensual_dominance"|"tender_surrender"|"romantic_authority", choices)` → `StoryIdentity` with `Genre.GENTLEFEMDOM`
- All generated YAML must pass `auteur identity validate story_identity.yaml`
- Three cores independently testable, working with shared infrastructure
- Test count target: 40-50 total (15 Task 1 + 20 Task 2 + 12 Task 3)

---

## Task 1: Gentle Femdom Core Templates

**Files:**
- Create: `src/auteur/gentlefemdom/__init__.py`
- Create: `src/auteur/gentlefemdom/core_templates.py`
- Create: `tests/gentlefemdom/__init__.py`
- Create: `tests/gentlefemdom/test_core_templates.py`

**Interfaces:**
- Produces: `SensualDominanceTemplate`, `TenderSurrenderTemplate`, `RomanticAuthorityTemplate` classes
- Each with 9-phase `.phases` dict, `.get_options(phase)`, `.get_constraints(phase)`, `.validate_choices(choices)`
- `get_template(core_id)` factory function

**Implementation Notes:**
- SensualDominanceTemplate: core_id="sensual_dominance", primary_emotion="playful_control"
  - Phase 1: emotional_core (returns sensual_dominance)
  - Phase 2: genre_contract (sadistic, dom_leadership, playful_power, intimate_control)
  - Phase 3: scope (intimate_pair, expanding_circle, community_dynamic)
  - Phase 4: structural_forces (want, resistance, conflict, stakes, change)
  - Phases 5-9: metadata (boundary_clarity, tone_playfulness, care_expression, power_balance, connection_confidence)

- TenderSurrenderTemplate: core_id="tender_surrender", primary_emotion="safe_vulnerability"
  - Similar 9-phase structure with surrender-specific options

- RomanticAuthorityTemplate: core_id="romantic_authority", primary_emotion="cherished_leadership"
  - Similar 9-phase structure with romantic authority-specific options

**Test Requirements:**
- 15 tests total covering all three templates
- Verify instantiation, phases, options for all cores
- Validate valid and invalid choices

---

## Task 2: Gentle Femdom Validation Rules

**Files:**
- Create: `src/auteur/gentlefemdom/validation.py`
- Create: `tests/gentlefemdom/test_validation.py`

**Validation Rules:**

**Sensual Dominance:**
- consent_enthusiastic: Power exchange must be enthusiastically consensual
- boundaries_explicit: Boundaries clearly stated and respected
- playfulness_present: Tone is playful, not cruel
- care_central: Dominant's care for submissive evident

**Tender Surrender:**
- surrender_voluntary: Never coerced or manipulated
- vulnerability_honored: Submissive's vulnerability is valued and protected
- trust_earned: Dominant demonstrates trustworthiness
- growth_emotional: Emotional development alongside physical

**Romantic Authority:**
- authority_rooted_in_care: Leadership serves both partners
- partner_cherished: Submissive genuinely valued and celebrated
- respect_bidirectional: Respect flows both directions
- interdependence_balanced: Neither partner wholly dependent

**Test Requirements:**
- 20 tests covering all rules and cores
- Verify valid cases pass, invalid cases fail with clear messages

---

## Task 3: Identity Generator Extension & CLI

**Files:**
- Modify: `src/auteur/netorare/identity_generator.py` (add gentlefemdom routing)
- Create: `src/auteur/cli_gentlefemdom.py` (CLI handler)
- Create: `tests/gentlefemdom/test_identity_generator.py`

**Implementation Notes:**
- Extend IdentityGenerator to accept core_ids: sensual_dominance, tender_surrender, romantic_authority
- Route all three to Genre.GENTLEFEMDOM
- CLI handler: `handle_gentlefemdom_init(project_path, core_id="sensual_dominance", ...)`
- Port: 8767 (distinct from netorare's 8765, mystery's 8766)

**Test Requirements:**
- 12 tests covering identity generation, YAML serialization, CLI workflow
- Verify all three cores generate valid identity files
- Verify no regressions

---

## Summary Checklist

- [ ] All 15 Task 1 (templates) tests passing
- [ ] All 20 Task 2 (validation) tests passing
- [ ] All 12 Task 3 (identity) tests passing
- [ ] Total: 47 tests passing
- [ ] Generated YAML passes `auteur identity validate`
- [ ] No regressions (mystery + netorare tests still pass)
- [ ] Three clean commits (one per task)

