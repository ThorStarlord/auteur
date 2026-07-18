# Auteur v1 Architecture Completion Report

**Date:** 2026-07-18
**Status:** Final

This report marks the transition from **building the foundation** to **building on top of it**. The Book reconciliation subsystem is architecturally mature. The remaining gaps are breadth, UX, and cross-cutting infrastructure — not missing architectural layers.

---

## Implemented Capabilities

### Narrative Engine (Five Semantic Layers)

| Layer | Scope | Status | Key Modules |
|-------|-------|--------|-------------|
| Layer 0 — Ontology | Concepts & types | **Experimental** | `narrative_ontology` (CLI exists, core stubs) |
| Layer 1 — Identity | Story contracts | **Complete** | `identity.py`, `blueprint.py`, `genres/`, `mediums/` |
| Layer 2 — Structure | Plans & forces | **Complete** | `structure/` (analyzer, generator, proposals, audits) |
| Layer 3 — Realization | Events & state | **Partial** | `narrative_realization` (CLI exists, backends stubs); `cartographer` (plan → outline) is complete |
| Layer 4 — Expression | Prose & manuscript | **Complete** | `expression/` (pilot, composition, book, reconciliation, book_reconciliation) |

### Cross-Cutting Systems

| System | Status | Key Modules |
|--------|--------|-------------|
| Provenance | **Complete** | `provenance/` (ArtifactStore, lifecycle, freshness) |
| Reasoning | **Complete** | `reasoning/` (runtime, synthesis, setup_payoff) |
| Critics | **Complete** | `critic/` (5 critics: contract, arc, tension, slop, theme) |
| Pipeline | **Complete** | `pipeline/` (runner, draft orchestration) |
| LLM Abstraction | **Complete** | `llm/` (provider abstraction, retrying, fake for tests) |

### Completed Workflows

| Workflow | Steps | Layer |
|----------|-------|-------|
| **Genre Pipeline** | Session → choices → validation → StoryIdentity compilation | Identity |
| **Structure Diagnosis** | Blueprint → 9-layer analysis → diagnostics → proposals → application | Structure |
| **Cartographer Planning** | PlanningCall → LLM → outline → validation | Realization |
| **Chapter Drafting** | Cartographer → Bard → 5 critics → accept/iterate → final | Expression |
| **Chapter Reconciliation** | Inspect → propose → plan → publish → decide → recompose → accept | Expression |
| **Book Reconciliation** | Inspect → route → plan → publish → decide → recompose → compare → accept → complete | Expression |
| **Editing** | Review → accept/reject/apply patches | Expression |
| **Round-trip** | Export chapter → external edit → import chapter → promote | Expression |
| **Series Management** | Validate → compile → diagnose → graph → bible | Series |
| **Universe Management** | Validate → diagnose → build | Universe |
| **Character Analysis** | Categorize → diagnose | Character |
| **Relations Tracking** | Track → graph → diagnose | Character |

### CLI Surface Summary

- **27 top-level commands** → ~100+ leaf commands
- Book reconciliation: 14 subcommands (inspect → route → plan → publish → decide → recompose → compare → accept → complete + 5 companion inspect/show)
- Chapter reconciliation: 12 subcommands
- Genre pipelines: 3 genre-specific CLIs + 1 generic

---

## Architectural Layers

### Authority Model

```
canonical       author-declared, accepted identity/blueprint/structure/realization
derived         computed artifacts (reports, proposals, plans, comparisons, completions)
decision        immutable decision records (accept/reject/defer + acceptance records)
candidate       proposed changes awaiting decision
pointer         current accepted-source reference (only mutable tier)
```

### Provenance Model

```
Artifact metadata: authority, lifecycle, revision, content_hash, source references
Freshness: direct dependencies only, health ≠ staleness, staleness ≠ invalidity
Hash policy: YAML/JSON normalized → NFC → sorted keys → SHA-256
Acceptance: creates immutable revision + moves pointer (compare-and-swap, last)
```

### Transformation Families

| Family | Examples |
|--------|----------|
| Knowledge Creation | `realization.generate_expression` |
| Knowledge Evaluation | critics, reasoning, comparison |
| Knowledge Evolution | acceptance, pointer moves |
| Boundary Crossing | composition (Projection), publication |

---

## Architectural Invariants (Confirmed by Audit)

1. ✅ Authority owned by target artifact's lifecycle
2. ✅ Expression does not silently change upstream layers
3. ✅ Publication ≠ acceptance (durable unaccepted candidates)
4. ✅ Candidate decisions are independent unless explicit dependency contract
5. ✅ Chapter recomposition uses accepted sources only (never unpublished candidates)
6. ✅ Chapter/Book recomposition ≠ acceptance (no pointer movement)
7. ✅ Chapter/Book acceptance ≠ reconciliation completion (completion is purely administrative)
8. ✅ Reasoning reports and critic outputs are derived, read-only
9. ✅ Evidence identifies source artifact/revision/hash
10. ✅ Stale inputs block unsafe promotion; no silent substitution
11. ✅ Transformations are explicit, provenance-rich, freshness-validated, failure-atomic
12. ✅ Failed workflows leave no partial canonical mutation
13. ✅ Prior revisions and decisions remain inspectable
14. ✅ Derived artifacts may not silently replace or canonize sources

---

## Remaining Product Gaps (Prioritized)

### Priority 1: Author Workflow / Workspace UX

**Missing capability:** Coherent, guided CLI workflow for end-to-end novel authoring.

**Evidence:** 100+ leaf commands in a flat namespace. Book reconciliation has 14 subcommands. Genre pipelines have 3 near-duplicate CLIs. No `auteur help` command. No "getting started" or "common workflows" output. Error messages are inconsistent (3+ patterns). Some errors silently swallowed. No tab-completion.

**Why the architecture needs it:** The engine is complete but undiscoverable. A new user cannot know what order to run commands. The reconciliation workflow (14 steps) needs a wizard or guided mode.

**Foundational:** Yes — without it, the product cannot be used without the implementation documentation open.

**Dependencies:** All completed subsystems (identity, structure, expression, reconciliation).

**Implementation estimate:** Medium (2-4 weeks). Refactor CLI to use command groups with workflow descriptions. Add `auteur guide` or `auteur workflow` commands. Standardize error patterns. Add tab-completion generation.

**Maintenance burden:** Low (cosmetic/structural changes to cli.py).

### Priority 2: Export / Publishing Pipeline

**Missing capability:** Convert accepted Book manuscript to standard publishing formats (EPUB, PDF, HTML, DOCX).

**Evidence:** Book expression exists (`book/expression/book_v001.md`) and the full reconciliation pipeline is complete. But no command produces a publishable artifact. The roundtrip module handles chapter-level markdown only. No format conversion exists.

**Why the architecture needs it:** The primary product of Auteur is a novel manuscript. An author must be able to produce something readable outside Auteur.

**Foundational:** Yes — this is the end deliverable of the entire pipeline.

**Dependencies:** Book expression (complete), Book reconciliation (complete).

**Implementation estimate:** Medium (2-3 weeks). Markdown → EPUB via `pandoc` or pure-Python libraries. Add `auteur publish` command. Handle cover page, TOC, metadata.

**Maintenance burden:** Low-medium (format libraries change, but thin wrapper).

### Priority 3: Schema Migration

**Missing capability:** Versioned project schemas with migration support.

**Evidence:** `blueprint.yaml` and `bible.json` have no `schema_version` field. The `provenance` module tracks artifact freshness but doesn't handle schema evolution. If the blueprint format changes, old projects cannot be upgraded. The `project-format.md` doc describes the current format with no versioning.

**Why the architecture needs it:** Any format change between v1 and v2 will orphan existing user projects. Schema versioning is the minimum requirement for production use.

**Foundational:** Yes — without it, the project cannot evolve.

**Dependencies:** `project.py`, `blueprint.py`, `bible.py`, `provenance/`.

**Implementation estimate:** Small (1-2 weeks). Add `schema_version` to project files, create migration framework, write v1→v2 migration if needed.

**Maintenance burden:** Low (once framework exists, each migration is additive).

### Priority 4: Remove Stale / Duplicated Code

**Missing capability:** Clean codebase without dead paths.

**Evidence:**
- Three genre-specific CLI adapters (`cli_netorare.py`, `cli_mystery.py`, `cli_gentlefemdom.py`) — these are legacy compatibility wrappers. The generic `get_genre_pipeline()` path exists but the old branches remain as dead code (~100 lines).
- Tests in `src/` directory (`narrative_realization/*/test_*.py` and `test_cli_realization.py`) — pytest doesn't discover these.
- Narrative blueprint package (~15 files with mostly empty stubs).
- Narrative ontology, realization, orchestration packages — large CLIs but the backends are stub/empty.

**Why the architecture needs it:** Dead code increases maintenance cost, confuses navigation, and creates a false sense of completeness. Tests in `src/` give a false sense of coverage.

**Foundational:** No — but it's low-cost cleanup with high signal-to-noise improvement.

**Dependencies:** None (safe deletions).

**Implementation estimate:** Small (1 week). Delete stale genre CLI branches, move tests from `src/` to `tests/`, decide on experimental package fate (complete or formally archive).

**Maintenance burden:** Negative (less code to maintain).

### Priority 5: Code Quality Infrastructure

**Missing capability:** Automated linting, type-checking, and coverage. 

**Evidence:** No mypy/pyright, no ruff/flake8, no pre-commit hooks, no coverage reporting in CI. CI runs only on ubuntu-latest with Python 3.11. No nightly builds. No benchmarks.

**Why the architecture needs it:** Without type-checking, refactoring is risky. Without linting, code style drifts. Without coverage, test gaps are invisible.

**Foundational:** No — but the project is large enough (50k+ lines) that these are necessary for maintenance velocity.

**Dependencies:** None.

**Implementation estimate:** Small (1 week). Add ruff config, mypy config, pre-commit hooks, coverage reporting, matrix testing in CI.

**Maintenance burden:** Low (config once, maintain per language upgrade).

### Priority 6: Visualization / Graph Output

**Missing capability:** Interactive or rendered graphs of narrative structure, provenance, and reconciliation status.

**Evidence:** Series graph exists as DOT output (requires external Graphviz). Relation graph exists as terminal-only ASCII. No SVG/PNG/HTML output. No provenance visualization. No reconciliation status dashboard.

**Why the architecture needs it:** Authors need to see the structural health of their story. A graph showing "which chapters are stale," "what was accepted," or "thread relationships" is more useful than a JSON report.

**Foundational:** No — but high user value.

**Dependencies:** Structure analyzer, series, relations, reconciliation.

**Implementation estimate:** Medium (2-4 weeks). Add Mermaid.js or Graphviz output to existing graph commands. HTML dashboard for reconciliation status.

**Maintenance burden:** Low (formatting only, no logic changes).

### Priority 7: Performance / Incremental Computation

**Missing capability:** Caching, lazy loading, and incremental recomposition for large works.

**Evidence:** Session-scoped bootstrap cache in conftest is the only caching. No incremental recomposition (full recomposition on every change). No lazy loading for large blueprints. No LLM result caching.

**Why the architecture needs it:** For a multi-chapter novel (50+ chapters, 100k+ words), full recomposition on every change would be slow.

**Foundational:** No — v1 proves correctness; v2 optimizes for scale.

**Dependencies:** Expression, reconciliation, provenance.

**Implementation estimate:** Large (4-8 weeks). Add content-addressable cache, dirty-bit tracking, incremental recomposition.

**Maintenance burden:** Medium (caching invalidation complexity).

### Priority 8: Complete Experimental Packages

**Missing capability:** Fully implement or formally archive Layer 0 (Ontology), Layer 3 (Realization), and overlay systems (Orchestration, Blueprint).

**Evidence:** `narrative_ontology`, `narrative_realization`, `narrative_orchestration`, `narrative_blueprint` all have substantial CLI scaffolding but stub/empty backends. These represent unfinished architectural layers.

**Why the architecture needs it:** These are referenced by the narrative architecture specification. Their incompleteness creates a gap in the architecture story.

**Foundational:** No — the current complete layers (1, 2, 4) already support the full authoring pipeline. These layers would add depth but don't block any current workflow.

**Dependencies:** Each other (lower layers must be done first).

**Implementation estimate:** Large (8-16 weeks per package). Ontology alone is a foundational type system. Realization is a deep layer.

**Maintenance burden:** High (these are large packages with complex interdependencies).

---

## Explicit Non-Goals (v1)

The following are intentionally excluded from v1:

1. **Multi-user collaboration** — no merge queues, branch reconciliation, or shared projects
2. **Generic workflow engine** — no event-sourcing, workflow DSL, or visual editor
3. **Automatic semantic rewriting** — no AI-driven prose repair without author consent
4. **Database storage** — file-based project format only
5. **Model-inferred canonical edges** — all provenance explicitly tracked
6. **Open-Ended Mode** — hidden from default help; Opinionated Mode is the default product
7. **Scrivener/Ulysses/Google Docs import** — markdown round-trip only
8. **Universe / Series / Book assembly beyond expression** — the expression layers handle multi-chapter/book/assembly; higher-level universe/series orchestration is v2 territory

---

## Roadmap for v2

### Phase 1: UX & Publishing (4-6 weeks)
1. **CLI overhaul** — command groups, guided workflows, standard errors, tab-completion
2. **Export pipeline** — `auteur publish` for EPUB/PDF/HTML
3. **Schema migration** — versioned project format

### Phase 2: Cleanup & Quality (2-3 weeks)
4. **Dead code removal** — stale genre adapters, misplaced tests, experimental packages
5. **CI quality gates** — linting, type-checking, coverage, matrix testing

### Phase 3: Visualization & Performance (6-10 weeks)
6. **Visualization** — rendered graphs, HTML reconciliation dashboard
7. **Incremental computation** — caching, dirty-bit tracking

### Phase 4: Depth (8-16 weeks)
8. **Ontology (Layer 0)** — complete the foundational type system
9. **Realization (Layer 3)** — complete scene-level state tracking
10. **Orchestration** — cross-layer validation and workflow automation

---

## Conclusion

Auteur v1 has achieved **architectural maturity** across its core pipeline:

- Five semantic layers: Identity (complete) → Structure (complete) → Expression (complete), with Ontology (experimental) and Realization (partial) remaining
- Provenance: immutable artifacts, pointer-based authority, deterministic derived outputs
- Transformation: explicit contracts, freshness validation, atomic publication, rollback
- Reasoning: deterministic runtime, 5 critics, synthesis, author-facing review
- Reconciliation: full Chapter and Book workflows from inspection through completion

The product is no longer missing foundational architecture. The next phase is not another reconciliation phase — it is **building on top of the foundation** with UX polish, publishing output, code quality infrastructure, and incremental depth where the author workflow demands it.
