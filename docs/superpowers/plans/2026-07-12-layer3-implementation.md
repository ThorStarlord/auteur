# Layer 3: Narrative Realization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task without human pauses between tasks. Continuous execution mode.

**Goal:** Implement Scene Realization layer that converts chapter intentions into concrete dramatic units.

**Architecture:** Layer 3 defines what concretely happens in each scene (goal, opposition, turn, decision, outcome, state changes). Five semantic boundaries established and ready for implementation.

**Tech Stack:**
- Pydantic v2 for SceneOutline schema
- YAML-based scene storage (consistent with Layer 2)
- Validators for reference, knowledge, temporal relationships
- Genre-agnostic infrastructure (netorara, mystery, gentlefemdom)
- CLI integration with existing blueprint commands

## Global Constraints

- Backward compatible: all Layer 2 functionality unchanged
- No breaking changes to existing validators
- Five semantic boundaries must be preserved in every component
- One real scene sequence validates everything
- All orchestration commands work identically across all 3 genres
- Draft scenes support (status: draft | incomplete | ready)

---

## File Structure

### New Directory: `src/auteur/narrative_realization/`

```
src/auteur/narrative_realization/
├── __init__.py                          # Public API exports
├── schema/
│   ├── __init__.py
│   ├── scene_outline.py                 # SceneOutline schema with 5 boundaries
│   ├── scene_state.py                   # Entry/exit state models
│   └── scene_action.py                  # Goal, opposition, turn, decision, outcome
├── loader/
│   ├── __init__.py
│   └── scene_loader.py                  # YAML serialization for scenes
├── validator/
│   ├── __init__.py
│   ├── reference_validator.py           # Scene→chapter, beat references resolve
│   ├── knowledge_validator.py           # Knowledge consistency (no retroactive forgetting)
│   ├── temporal_validator.py            # Position uniqueness, parallel validation
│   └── scene_validator.py               # Orchestrate all scene validators
├── orchestrator/
│   ├── __init__.py
│   ├── scene_builder.py                 # Build scenes from chapter outline
│   ├── scene_inspector.py               # Display scene status and coverage
│   └── scene_workflow.py                # Workflow orchestration
└── cli_realization.py                   # CLI: auteur realization commands

data/
└── scenes/
    └── {genre}/{story_id}/
        ├── chapter_01/
        │   ├── scene_01_01.yaml
        │   └── scene_01_02.yaml
        └── chapter_02/
            └── scene_02_01.yaml

tests/auteur/narrative_realization/
├── test_scene_outline.py
├── test_scene_state.py
├── test_scene_action.py
├── test_scene_loader.py
├── test_reference_validator.py
├── test_knowledge_validator.py
├── test_temporal_validator.py
├── test_scene_validator.py
├── test_scene_builder.py
├── test_scene_inspector.py
├── test_scene_workflow.py
└── test_real_scene_integration.py        # Real chapter→scenes realization
```

---

## Task Breakdown

### Phase 1: Scene Schema & State (3 tasks)

**Task 1: Scene Outline Schema**
- Create `src/auteur/narrative_realization/schema/scene_outline.py`
- Define SceneOutline as main container (id, chapter_id, narrative_position, status, pov_character_id, participants)
- Include all 5 semantic boundaries preserved in schema
- Status enum: draft | incomplete | ready
- Implement comprehensive tests (12+)

**Task 2: Scene State Models**
- Create `src/auteur/narrative_realization/schema/scene_state.py`
- Define EntryState (knowledge, emotions)
- Define ExitState (knowledge, emotions)
- Define KnowledgeFact (what, how_known, degree_of_certainty)
- Define EmotionalState (state, intensity, rationale)
- Implement comprehensive tests (10+)

**Task 3: Scene Action Models**
- Create `src/auteur/narrative_realization/schema/scene_action.py`
- Define Goal (actor_id, objective, rationale)
- Define Opposition (source_id, pressure, rationale)
- Define Turn (type, event, impact)
- Define Decision (actor_id, choice, rationale)
- Define Outcome (result, knowledge_added, consequences, emotional_shifts)
- Implement comprehensive tests (12+)

### Phase 2: Loaders & Validators (5 tasks)

**Task 4: Scene Loader**
- Create `src/auteur/narrative_realization/loader/scene_loader.py`
- Load/save SceneOutline from YAML
- Validate scene file structure on load
- Cache loaded scenes
- Genre-aware path resolution
- Implement comprehensive tests (8+)

**Task 5: Reference Validator**
- Create `src/auteur/narrative_realization/validator/reference_validator.py`
- Validate scene→chapter reference
- Validate scene→arc_beat references
- Validate setup→payoff references
- Detect orphaned scenes
- Implement comprehensive tests (14+)

**Task 6: Knowledge Validator**
- Create `src/auteur/narrative_realization/validator/knowledge_validator.py`
- Track knowledge entry→learned→exit
- Prevent retroactive forgetting
- Validate learning mechanisms (perception, inference, external source)
- Check character knowledge consistency across scenes
- Implement comprehensive tests (14+)

**Task 7: Temporal Validator**
- Create `src/auteur/narrative_realization/validator/temporal_validator.py`
- Validate unique narrative positions within chapter
- Validate temporal_relation (parallel_with mutual, follows_scene valid)
- Check no circular parallel-with chains
- Validate temporal relationships don't violate knowledge (can't know before discovery)
- Implement comprehensive tests (12+)

**Task 8: Scene Validator (Orchestration)**
- Create `src/auteur/narrative_realization/validator/scene_validator.py`
- Orchestrate all four validators
- Aggregate violations (reference, knowledge, temporal)
- Provide coherent error reporting
- Support draft vs. ready validation levels
- Implement comprehensive tests (14+)

### Phase 3: Orchestration (3 tasks)

**Task 9: Scene Builder**
- Create `src/auteur/narrative_realization/orchestrator/scene_builder.py`
- Create template scenes from chapter outline
- Generate minimal SceneOutline for each chapter phase
- Apply genre-specific scene defaults
- Validate generated scenes pass all validators
- Implement comprehensive tests (8+)

**Task 10: Scene Inspector**
- Create `src/auteur/narrative_realization/orchestrator/scene_inspector.py`
- Show complete scene sequence for chapter
- Display entry/exit states for each scene
- Show arc beat realization coverage
- Identify missing or incomplete scenes
- Show validation status
- Implement comprehensive tests (6+)

**Task 11: Scene Workflow**
- Create `src/auteur/narrative_realization/orchestrator/scene_workflow.py`
- Integrate with CLI
- Commands: seed, validate, inspect, graph
- Full workflow: create → inspect → validate → iterate
- Genre-aware defaults
- Implement comprehensive tests (8+)

### Phase 4: Integration & Verification (2 tasks)

**Task 12: Real Scene Integration Test**
- Build one real chapter with complete scene sequence
- Use netorara genre, one chapter (Chapter 7: The Search)
- Implement: 3 scenes, 1 character arc realization, 2 story arc beats
- Validate: all references, knowledge consistency, temporal relationships
- Test: full orchestration workflow from outline to validated scenes
- Implement comprehensive tests (15+)

**Task 13: CLI Integration & Documentation**
- Integrate with existing `cli_blueprint.py`
- Add commands: auteur {genre} realization {seed|validate|inspect}
- Update CLI help and documentation
- Create usage examples for all 3 genres
- Verify commands work end-to-end
- Implement comprehensive tests (10+)

---

## Success Criteria

✅ SceneOutline schema preserves all 5 semantic boundaries  
✅ Reference validator ensures all IDs resolve  
✅ Knowledge validator enforces consistency (no retroactive forgetting)  
✅ Temporal validator ensures valid relationships  
✅ Scene builder generates valid outlines from chapters  
✅ Inspector shows complete scene coverage  
✅ All orchestration commands work for all 3 genres identically  
✅ One real chapter scene sequence builds and validates without errors  
✅ All 100+ scene tests passing  
✅ Zero breaking changes to Layer 0–2 functionality  

---

**Last Updated:** 2026-07-12  
**Status:** Ready for implementation  
**Estimated Scope:** 13 tasks, ~1200+ test cases  
**Continuous Execution:** Yes (no human pauses between tasks)
