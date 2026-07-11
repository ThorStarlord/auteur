# Auteur Development Guidelines

Developer guidelines for the auteur narrative engineering toolkit.

## Core Philosophy

**Blame processes, not people.** Build systems and patterns that scale, not heroic individual efforts.

## Architecture Patterns & Reusability

### Layered Story Architecture (NOW COMPLETE)

Auteur implements the complete 8-layer narrative hierarchy:

1. **Universe** ✅ (defines world rules, constraints for all descendant layers)
2. **Series** ✅ (establishes multi-book continuity, character arcs, thematic throughlines)
3. **Book/Story Identity** ✅ (establishes genre contract and emotional core)
4. **Blueprint** ✅ (story beats aligned to 9-phase genre structure)
5. **Outline** ✅ (scene-by-scene breakdown via Cartographer)
6. **Draft** ✅ (actual prose generation and management)
7. **Editing** ✅ (refinement, review, drift validation)

Each layer:
- Owns a different scale of narrative decision
- Inherits constraints from all higher layers
- Produces durable YAML/JSON/Markdown artifacts
- Can produce diagnostics when coherence is violated
- Validates independently without special-casing in shared code

The Universe layer (implemented 2026-07-11) completes the hierarchy. See
`docs/superpowers/specs/2026-07-11-universe-layer-spec.md` for the full specification.

### The 9-Layer Genre Pipeline Pattern

Auteur's genre pipelines (netorare, mystery, gentle femdom) share a proven architecture:

1. **Generic Infrastructure** (built once, reused for all genres):
   - Session State Management (file-based JSON, atomic writes)
   - HTTP Browser Server (subprocess with cleanup, port management)
   - Browser UI (9-phase decision tree visualization)
   - Identity Generator (genre-routing by core_id to Genre enum)
   - CLI Entry Point (subcommand pattern)

2. **Genre-Specific Components** (implement per genre):
   - Core Templates (3 emotional cores, 9-phase options each)
   - Validation Rules (10-15 rules enforcing genre integrity)
   - Identity Transformation (genre-specific metadata generation)

### Designing Extensible Pipelines

When building opinionated pipelines (genre templates, validation engines, identity generators):

1. **Design the core abstraction first** — phases dict, option enumerations, `validate_choices()` signature
2. **Build generic infrastructure once** — no assumptions about specific genres
3. **Prove it generalizes** — implement 2+ distinct examples to validate the pattern
4. **Never special-case in infrastructure** — if a third genre needs a variant, the pattern is wrong

**Validation threshold:** If you can implement the same architecture for three different genres (netorare, mystery, gentle femdom) with zero infrastructure changes, the pattern is production-ready for additional genres.

### Current Genre Pipelines

| Genre | Emotional Cores | Templates | Validation Rules | CLI Port | Tests |
|-------|-----------------|-----------|------------------|----------|-------|
| Netorare | Classic Humiliation, Horror, Mystery | 3 × 9-phase | 15 rules | 8765 | 154 |
| Mystery | Howdunit, Paranoia, Cozy | 3 × 9-phase | 12 rules | 8766 | 75 |
| Gentle Femdom | Sensual Dominance, Tender Surrender, Romantic Authority | 3 × 9-phase | 12 rules | 8767 | 101 |

## Development Velocity & Subagent-Driven Development

### Continuous Execution Mode

When implementing multi-task work with subagent-driven-development:

1. **Dispatch Task 1** implementer → review → mark complete
2. **Immediately dispatch Task 2** (don't wait for summary or recap)
3. **Proceed through all tasks** without human-in-loop pauses

This approach:
- Avoids context waste on recapping
- Maintains flow state and momentum
- Scales to 3+ tasks efficiently
- Use only when tasks are genuinely independent

### Design Documents Are Force Multipliers

Clear design specs and implementation plans allow subagents to execute in isolation without round-trip questions:

- **Design Spec** (500+ words): Architecture, emotional cores, validation constraints, rationale
- **Implementation Plan** (1500+ words): Exact code to write, test structure, integration points

These documents let implementers work independently and enable high-velocity parallel task execution.

### Catching Issues Early

- Review between tasks (not after all tasks)
- If Task 1 review finds issues, fix before Task 2 starts
- Rework on early tasks is cheaper than discovering the pattern is wrong in Task 3

## Debugging & Verification

### Distinguishing Code Defects from Environment Issues

Python development involves multiple sources of truth that can disagree:
- **Git commits** — what's tracked in the repository
- **Python import paths** — what `import auteur` loads from disk
- **Shell executables** — which `auteur` command the shell resolves

These can diverge when:
- A stale package installation predates recent code changes
- Multiple Python versions coexist on the same machine
- Editable installs (`pip install -e .`) haven't been refreshed
- PATH environment contains multiple script locations

**Diagnostic process before declaring a code defect:**

1. **Verify the symptom is reproducible** — does it happen consistently, or only under certain conditions?
2. **Check multiple execution paths:**
   ```bash
   python -c "import auteur; print(auteur.__file__)"     # Shows which module Python loads
   which auteur                                           # Shows which executable shell resolves
   python -m auteur.cli gentlefemdom init ./test          # Bypasses shell executable resolution
   ```
3. **Test with corrected environment:**
   - Update PATH to prioritize current installation
   - Reinstall editable package: `pip install -e .`
   - Re-run the failing test
4. **Investigate *before* rewriting** — if tests pass but manual workflow fails, the code is likely correct
5. **Add regression coverage on invariants** — not to prevent environment issues (which tests can't), but to enforce the repository's contractual behavior

**Example:** Session storage moved from genre-specific paths to neutral `.auteur/genre_sessions/<genre>/`.
- Manual test showed old path being used
- Tests showed new path was correct
- Investigation revealed: shell was using Python312's `auteur` command (stale package) while tests used Python314 (current worktree)
- Fix: reinstall package, update PATH
- Regression test added: all 3 genres must use neutral path (prevents future code changes from silently reverting the invariant)

The lesson: **blame the process (PATH management, package installation), not the code.**

## Code Quality Standards

### Test-Driven Development

- Write failing tests first
- Implement minimal code to pass
- Self-review for completeness
- Task review validates spec compliance and code quality
- Target: 40-50 tests per 3-task genre pipeline

### Template API Consistency

All genre templates must implement the same interface:

```python
class CoreTemplate:
    phases: Dict[int, str]  # 1-9 mapping to layer names
    core_id: str
    primary_emotion: str
    
    def get_options(self, phase: int) -> List[TemplateOption]
    def get_constraints(self, phase: int) -> str
    def validate_choices(self, choices: Dict) -> Tuple[bool, List[str], List[str]]
```

### Validation Rule Structure

Each genre has a RuleSet with 10-15 domain-specific rules:

```python
class RuleSet:
    def __init__(self, core_id: str):
        self.rules: List[ValidationRule] = []
        self._build_rules()  # Dispatcher pattern
    
    def _build_core1_rules(self): ...  # Per-core implementation
    def _build_core2_rules(self): ...
    def _build_core3_rules(self): ...
```

Rules encode:
- Genre emotional integrity constraints
- Consent and safety requirements
- Narrative coherence checks
- Validation must be deterministic (same input → same output)

## Integration & CLI

### Naming Conventions

- Genre directories: lowercase (netorare, mystery, gentlefemdom)
- Module exports via `__init__.py`
- CLI commands: `auteur {genre} init ./project --core {core_id}`
- Port allocation: netorare=8765, mystery=8766, gentlefemdom=8767, +1 per new genre

### Reusing Session/Server/UI Infrastructure

The generic infrastructure in netorare is reusable without modification:

```python
from auteur.netorare.session import SessionManager
from auteur.netorare.browser.server import NetorareServer
# Browser UI in browser/index.html works for all genres
```

Just create new:
- `src/auteur/{genre}/cli_{genre}.py` → `handle_{genre}_init()`
- `src/auteur/{genre}/core_templates.py` → Genre-specific templates
- `src/auteur/{genre}/validation.py` → Genre-specific rules

## Documentation

- Design specs: `docs/superpowers/specs/YYYY-MM-DD-{genre}-design.md`
- Implementation plans: `docs/superpowers/plans/YYYY-MM-DD-{genre}-implementation.md`
- Reports: `.superpowers/sdd/{genre}-progress.md` (implementation tracking)

## No Special Cases in Infrastructure

If you find yourself adding `if genre == "new_genre"` to shared code, stop. The pattern needs rework:
- Either the infrastructure should handle it generically
- Or the new genre needs its own implementation of that component

The architecture succeeds when a new genre needs only templates + validation + identity transformation, never infrastructure changes.

---

**Last Updated:** 2026-07-11  
**Validated By:** Three complete genre pipelines (netorare, mystery, gentle femdom) with zero infrastructure modifications across 1090+ tests; genre-neutral runtime consolidation verified with regression coverage for session storage invariants
