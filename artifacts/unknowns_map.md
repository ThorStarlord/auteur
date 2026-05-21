# Unknowns Map

## 1. Knowns
- **CLI and State Commands**: The CLI commands for `state check`, `state update`, `state prepare`, `state canon`, and `state confirm` are implemented in `src/auteur/structure/state.py` and mapped to `src/auteur/cli.py`.
- **Bible Model Schema**: `src/auteur/structure/state.py` contains Pydantic models for `CharacterState`, `LocationState`, `ItemState`, `FactionState`, `EventState`, and `StoryBibleModel`, providing schema-enforced validation.
- **Diagnostics Coverage**: `state_check` defines layers 1 through 7 (`TARGET_EXPERIENCE`, `CONSTRAINTS`, `SCOPE`, `STRUCTURAL_FORCES`, `THREADS`, `CARRIERS`, `THEME`) matching the structural audit layers.
- **Green Test Suite**: The codebase has 253 passing tests, verifying existing draft, retry, audit, structure, and init functions.
- **Goal Shift**: The primary objective is to make the codebase a whole-story structure engine first, drafting chapter by chapter second.

## 2. Unknowns
- **Coverage of Layers 8 and 9**: The 9-layer engine model includes Modulation (Layer 8) and Resonance (Layer 9), but `state_check` only lists layers 1 to 7 in its `_LAYER_ORDER`. How are Layers 8 and 9 validated and integrated into the story state?
- **State Integration in Drafting Loop**: Does the drafting pipeline (`src/auteur/pipeline.py`) programmatically enforce or invoke `state check` before starting to write prose?
- **Author Overrides**: How does the validation engine prevent "author override cheats" where the drafting agent inserts fake overrides to bypass structural check failures instead of correcting the story blueprint or bible?
- **Decoupling Cartographer Outlines**: To what extent are outline generation and drafting coupled in the codebase, and can they be run completely independently?

## 3. Assumptions
- **Constraint Cascading**: We assume that higher layers (L1-L4) in the blueprint must deterministically validate/constrain the lower layers (L5-L7) before drafting can be executed.
- **CLI Preference**: We assume the current `auteur state` subcommand design is the desired API for authors to manage narrative transactions.
- **Existing Test Coverage**: We assume the tests under `tests/` contain mock projects we can use to verify structural check behaviors.

## 4. Risks
- **Drafting Loop Non-Convergence**: If structural constraint validation is too rigid, the LLM drafting loop might fail to converge, hitting the iteration limit and wasting tokens.
- **Bypassing Gaps**: If validation blocks all drafting, authors might be unable to write text unless all structural warnings are cleared, causing friction.
- **State Rot**: If transaction rollbacks in `state_update` fail or are not atomic, the project files could end up corrupted or partially updated.

## 5. Research Paths
- **State Check Execution**: Run `auteur state check` manually on the existing test projects (e.g. under `tests/fixtures/`) to see its diagnostic output.
- **Drafting Pipeline Analysis**: Inspect `src/auteur/pipeline.py` and `src/auteur/critic.py` to see where/how structural checks or `StoryStateManager` are invoked.
- **Test Coverage Inspection**: Locate tests covering state commands in the `tests/` directory to see how they mock transactions.

## 6. Stopping Rule
Stop research when:
1. We have run `state check` and verified how the drafting pipeline integrates with it.
2. The boundaries of the 9 layers implemented in the code vs. documented in `CONTEXT.md` are fully mapped.
3. The schema contract for `repository_sensemaking_brief` is ready to be written.

## 7. Machine-readable routing

```yaml
# Routing metadata for dynamic orchestration and artifact handling
clarity_assessment: "high"
unknowns_count: 4
assumptions_count: 3
research_needed: true
```
