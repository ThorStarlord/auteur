# Layer 2.5: Structural Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task without human pauses between tasks. Continuous execution mode.

**Goal:** Transform Layer 2 from disconnected schemas into one coherent narrative structure system. Answer: "How do the different outlines cooperate to form one authoritative story structure?"

**Architecture:** Layer 2.5 is the composition, integration, and workflow portion of Layer 2. It defines ownership, references, validation, and orchestration across Book, Sequence, Chapter, and Arc outlines.

**Tech Stack:**
- Existing Layer 2 outline schemas (Book, Chapter, Sequence, Series, arcs)
- Pydantic for composition validation
- Graph-based reference validation
- CLI commands for workflow orchestration

## Global Constraints

- Backward compatible: all Layer 2 schemas unchanged
- No breaking changes to existing validators
- Composition must handle optional structural depth (sequences optional)
- One real complete outline validates everything
- All orchestration commands work identically across all 3 genres

---

## File Structure

### New Directory: `src/auteur/narrative_orchestration/`

```
src/auteur/narrative_orchestration/
├── __init__.py                          # Public API exports
├── schema/
│   ├── __init__.py
│   ├── ownership.py                     # Ownership rules (which artifact owns what)
│   ├── references.py                    # Reference definitions (arc→chapter, etc.)
│   └── composition_rules.py             # Composition constraints (ordering, consistency)
├── validator/
│   ├── __init__.py
│   ├── reference_validator.py           # Validate all IDs resolve
│   ├── chronological_validator.py       # Payoff after setup, etc.
│   ├── contradiction_validator.py       # Detect conflicts between artifacts
│   └── composition_validator.py         # Validate complete structure
├── orchestrator/
│   ├── __init__.py
│   ├── outline_builder.py               # Seed: create template outlines from StoryIdentity
│   ├── outline_inspector.py             # Status: show outline structure
│   ├── outline_grapher.py               # Graph: visualize relationships
│   └── outline_workflow.py              # Workflow: seed → inspect → validate
└── cli_orchestration.py                 # CLI: auteur blueprint commands

data/
└── composition/
    ├── ownership_rules.yaml             # Canonical ownership mapping
    └── composition_constraints.yaml     # Ordering, optionality rules

tests/auteur/narrative_orchestration/
├── test_ownership.py
├── test_references.py
├── test_reference_validator.py
├── test_chronological_validator.py
├── test_contradiction_validator.py
├── test_composition_validator.py
├── test_outline_builder.py
├── test_outline_inspector.py
├── test_outline_grapher.py
├── test_orchestration_workflow.py
└── test_real_outline_integration.py      # Real StoryIdentity → complete outline
```

---

## Task Breakdown

### Phase 1: Ownership & Reference Framework (4 tasks)

**Task 1: Ownership Rules Definition**
- Define canonical owners for each structural fact
- YAML ownership mapping:
  - Books in series → Series Outline
  - Sequences in book → Book Outline
  - Chapters in sequence → Sequence Outline
  - Chapter purpose → Chapter Outline
  - Character transformation → Character Arc
  - Plot progression → Story Arc
  - Arc beat locations → Arc references chapter
  - Derived state → Computed (not separately authored)
- Pydantic models for ownership declarations
- Tests: 8+ validating ownership schema

**Task 2: Reference System Definition**
- Define reference types: book→sequence, sequence→chapter, arc→beat→chapter, setup→payoff
- ID format: {artifact_type}_{unique_id} (e.g., chapter_07, clara_distrust_deepens)
- Reference integrity: all references must resolve
- Tests: 10+ validating reference structure and resolution

**Task 3: Composition Constraints**
- Optionality: which artifacts are optional (sequences can be omitted)
- Chronological ordering: payoff after setup, crisis before resolution
- State validity: character state progression must be consistent
- Arc coverage: which books/chapters must have character arcs
- Tests: 12+ validating constraints

**Task 4: Composition Rules YAML**
- ownership_rules.yaml — canonical ownership mapping
- composition_constraints.yaml — ordering, optionality, state rules
- Load and validate rules structure
- Tests: 8+ validating rules loading

### Phase 2: Validators (3 tasks)

**Task 5: Reference Validator**
- Validate all IDs resolve correctly
- Check: book→sequence, sequence→chapter, arc→chapter, setup→payoff
- Detect: missing IDs, broken references, orphaned artifacts
- Tests: 14+ covering resolution scenarios

**Task 6: Chronological Validator**
- Validate payoff occurs after setup (unless intentional prelude)
- Check: character arc beats in chapter order
- Validate: Book 3 reveals not referenced in Book 1
- Detect: contradictory orderings
- Tests: 12+ covering chronology scenarios

**Task 7: Contradiction Validator**
- Detect conflicts between artifacts
- Examples: Chapter says "trust increases" while CharacterArc says "distrust deepens"
- Check: Story Arc progress matches Chapter outcomes
- Validate: Book ending matches Book Outline climax
- Tests: 14+ covering contradiction scenarios

### Phase 3: Orchestration (4 tasks)

**Task 8: Outline Builder (Seed)**
- Create template outlines from StoryIdentity
- Generate: Book Outline (1), Sequence Outlines (3-4), Chapter Outlines (12-16), Character Arc (1), Story Arc (1)
- Use genre-informed defaults (netorara has specific beats, etc.)
- Validate generated outline passes all validators
- Tests: 8+ covering seed workflows for all genres

**Task 9: Outline Inspector (Status)**
- Show complete outline structure in readable format
- Display: Series → Book → Sequence → Chapter hierarchy
- Show: Character Arc beats and their chapter references
- Show: Story Arc progression and chapter coverage
- Identify: missing elements, optional unimplemented sections
- Tests: 6+ covering inspection scenarios

**Task 10: Outline Grapher (Graph)**
- Visualize outline relationships as text/ASCII
- Show: container hierarchy (tree)
- Show: arc references (cross-cutting connections)
- Show: setup→payoff flows
- Output: can be used for documentation
- Tests: 5+ covering graph scenarios

**Task 11: Orchestration Workflow**
- CLI commands: seed, validate, graph, status
- Integration with existing blueprint CLI
- Full workflow: create → inspect → validate → iterate
- Genre-aware defaults for all 3 genres
- Tests: 8+ covering complete workflows

### Phase 4: Integration & Verification (2 tasks)

**Task 12: Composition Validator (Full)**
- Orchestrate all validators (reference, chronological, contradiction)
- Provide coherent error reporting
- Validate complete outline coherence
- Tests: 12+ validating complete scenarios

**Task 13: Real Outline Integration Test**
- Build one complete, real outline from actual StoryIdentity
- Use netorara genre with 2 books, 6 sequences, 20 chapters
- Implement: 1 Character Arc (protagonist), 1 Story Arc (cuckoldry progression)
- Validate: all references, chronology, no contradictions
- Test: orchestration workflow from seed to final validated outline
- Tests: 15+ covering real-world scenario

---

## Success Criteria

✅ Ownership rules clearly defined and validated
✅ Reference system working across all artifact types
✅ All validators detecting their specific issues
✅ Orchestration commands (seed, validate, graph, status) fully functional
✅ Optional structural depth supported (sequences can be omitted)
✅ All 3 genres working identically with no special-casing
✅ One real, complete, coherent outline builds and validates
✅ All 100+ composition tests passing
✅ Zero breaking changes to Layer 1-2 functionality

---

**Last Updated:** 2026-07-12  
**Status:** Ready for implementation  
**Estimated Scope:** 13 tasks, ~1200+ test cases  
**Continuous Execution:** Yes (no human pauses between tasks)
