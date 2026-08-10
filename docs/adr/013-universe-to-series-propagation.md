# ADR 013: Universe-to-Series Constraint Propagation

**Date:** 2026-07-11  
**Status:** Accepted  
**Context:** Genre pipeline completion and Series Engine integration require a binding contract for how Universe-level constraints propagate to Series and Book narratives.

## Problem Statement

The layered narrative architecture (Universe → Series → Book → Story Identity) promises that Universe-level decisions constrain downstream narratives. However:

1. Current Universe-to-Series validator returns no diagnostics.
2. Series Builder lacks thematic consistency checking.
3. No clear ownership between `SeriesIdentity` and `SeriesBible`.
4. Natural-language principles are indistinguishable from mechanically-enforceable constraints.
5. Unclear whether LLM assistance is required for constraint validation.

This ADR establishes a deterministic, testable contract that scales to future genres.

## Decisions

### 1. Canonical Ownership

**Decision:** `SeriesIdentity` is the canonical author-edited Series contract. `SeriesBible` is a compiled operational artifact derived from identity, book plans, and continuity state.

**Rationale:** Authorial intent must live in authored files. The Bible is a convenience reference and implementation artifact, not a competing source of truth.

**Implication:** Authors edit `series_identity.yaml`; tools generate `series_bible.json`.

---

### 2. Constraint Classification

**Decision:** Universe constraints are classified as:

1. **Structured Constraints** (deterministic, blocking)
   - Finite-domain values (genres, character states, thematic arcs)
   - Boolean conditions (e.g., "no character resurrection")
   - Enumerated relationships (faction membership, alliance rules)

2. **Natural-Language Principles** (advisory, non-blocking)
   - Free-text guidance (e.g., "stories should explore intimacy within power dynamics")
   - Thematic directions without computational enforcement
   - Narrative values that inform but do not mechanically block

3. **LLM-Assisted Interpretation** (optional, V1 non-blocking)
   - Semantic similarity checks (e.g., "tone consistency across books")
   - Intent alignment (e.g., "character growth arcs follow the series theme")
   - Explicitly marked as "uncertain" and never blocking

**Rationale:** Determinism requires clear boundaries. Natural language requires human judgment. LLM insights are valuable but not mandatory for V1.

---

### 3. Constraint Inheritance

**Decision:** Constraints inherit down the narrative hierarchy:

```
Universe
  ├→ Series (inherits all Universe constraints)
  │   ├→ Book 1 (inherits Series + Universe constraints)
  │   ├→ Book 2 (inherits Series + Universe constraints)
  │   └→ Book 3 (inherits Series + Universe constraints)
```

**Corollary:** Series may **strengthen but not weaken** Universe constraints.

**Example:**
- Universe rule: "Magic is possible."
- Series strengthens: "Magic requires sacrifice and has a cost."
- Invalid series rule: "Magic is impossible." ← **Violation**

**Rationale:** Constraints cascade downward. A Series that violates Universe rules is fundamentally incoherent. Authors may add constraints but not remove them.

---

### 4. Diagnostic Generation

**Decision:** Every Universe-to-Series or Series-to-Book diagnostic must include:

1. **Originating Constraint** (the Universe or Series rule)
2. **Conflicting Field** (the Series or Book value that violates it)
3. **Severity Level:**
   - `ERROR`: Structured constraint violation (blocks compilation)
   - `WARNING`: Natural-language principle mismatch (advisory only)
   - `INFO`: LLM-assisted suggestion (non-blocking, marked as uncertain)
4. **Actionable Explanation** (what the author should do)
5. **Diagnostic ID** (for tracking and filtering)

**Format:**
```json
{
  "id": "UNIVERSE_CONSTRAINT_VIOLATION",
  "severity": "ERROR",
  "constraint": "Magic can never resurrect the dead.",
  "source": "universe_identity.yaml:thematic_rules[0]",
  "conflict": "Series Book 2 resurrects protagonist.",
  "conflict_source": "series_identity.yaml:books[1].plot_summary",
  "explanation": "Book 2 contradicts Universe constraint on resurrection. Consider: (1) Redefine resurrection mechanics to allow limited resurrection within cost framework, (2) Remove resurrection from Book 2 plot, (3) Modify Universe constraint if series-wide resurrection is essential.",
  "lsm_context": null
}
```

**Rationale:** Authors need to understand *why* a constraint was violated and *what* they can do about it.

---

### 5. Structured Constraint Schema (Minimum V1)

**Decision:** Universe constraints are defined as:

```python
@dataclass
class StructuredConstraint:
    id: str  # Unique identifier
    type: Literal["genre_rule", "thematic_invariant", "character_state", "relationship_rule"]
    description: str  # Natural-language summary
    enforcement: Literal["deterministic", "advisory"]  # How the constraint is checked
    schema: dict  # Machine-readable constraint
    # For genre_rule: schema = {"allowed_values": [...]}
    # For thematic_invariant: schema = {"thematic_arc": str, "must_appear_in": ["book_1", "book_2"]}
    # For character_state: schema = {"character": str, "must_be": str}
    # For relationship_rule: schema = {"party_a": str, "party_b": str, "must_be": str}
```

**Rationale:** Enables validation to be data-driven rather than hard-coded.

---

### 6. Compilation Determinism

**Decision:** Compilation of `SeriesIdentity` into `SeriesBible` must be deterministic and complete even when:

- LLM services are unavailable
- User declines LLM-assisted diagnostics
- Constraint schema is minimal

**Constraint:** All structural compilation (gathering books, resolving character states, reconciling timelines) proceeds without LLM calls. LLM diagnostics are **added after**, not required for completion.

**Rationale:** Authors must be able to work offline. Builds trust. Reduces latency.

---

### 7. Thematic Consistency

**Decision:** Thematic consistency is tracked as:

```python
@dataclass
class ThematicArc:
    theme: str  # e.g., "Power without accountability destroys intimacy"
    books: list[int]  # Which books develop this theme
    progression: dict[int, str]  # Book 1: "introduces", Book 2: "deepens", Book 3: "resolves"
```

**Validation Rules:**
- If a theme is introduced in Book 1, it must appear (or be resolved) in Book 2+.
- If a theme is dropped without resolution, warn.
- If Book N contradicts the thematic arc, warn.

**Rationale:** Thematic continuity is a higher-level concept than character or lore continuity. Explicit tracking prevents thematic drift.

---

### 8. Backwards Compatibility and Migration

**Decision:** Existing Series without explicit Universe constraints do not break. Universe-to-Series validation is opt-in via:

```yaml
# series_identity.yaml
series_metadata:
  universe_contract: "universe_identity.yaml"  # Opt-in validation
  universe_contract_version: 1
```

If `universe_contract` is absent, Series Builder skips Universe diagnostics. If present, validation is mandatory.

**Rationale:** No surprise breaking changes. Authors choose whether to enforce Universe constraints.

---

## Out of Scope for V1

The following are explicitly deferred:

- Session history and archive behavior
- Warning acknowledgment UI
- Dedicated `/health` endpoint
- Standalone Universe Builder
- Standalone Book Builder
- Graph visualization beyond the series command
- Automatic constraint inference from prose
- Cross-universe Series (all books must belong to the same Universe)
- Constraint versioning (constraints are immutable once committed)

---

## Implementation Consequences

1. **New file:** `src/auteur/universe/constraints.py` (StructuredConstraint dataclass, schema validation)
2. **New validator:** `src/auteur/series/universe_integration.py` must produce diagnostics, not return silently
3. **New data model:** `SeriesIdentity` gains optional `universe_contract` and `thematic_arcs` fields
4. **Series Bible:** Must include thematic progression and constraint satisfaction evidence
5. **Tests:** Universe-to-Series validation must have regression tests for all constraint types

---

## Validation Checklist

Before implementing Series diagnostics (Group 3), confirm:

- [ ] StructuredConstraint schema can represent all genres' rules
- [ ] Structured vs. advisory constraint distinction is clear to implementers
- [ ] Backwards-compatible Series files load without errors
- [ ] Constraint inheritance is tested for at least 3 layers deep
- [ ] LLM-assisted diagnostics are explicitly optional and non-blocking
- [ ] SeriesBible and SeriesIdentity can be round-tripped without data loss
- [ ] All 8 binding decisions can be verified by code review

---

**Next Step:** Decompose Group 3 (Series completion) into precise requirements per the constraint model defined here. Each requirement must map to at least one diagnostic.
