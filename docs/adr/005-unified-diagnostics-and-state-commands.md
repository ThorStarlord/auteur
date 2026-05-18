# ADR 005: Unified Diagnostics and State Commands

## Status

Accepted

## Context

Auteur is a whole-story structure engine first and a chapter drafting engine second. To scale this philosophy, we are adapting highly successful software engineering "Sensemaking" and "Interface Specification" patterns to long-form fiction:
- **`problem-framer` & `unknowns-mapper`** $\rightarrow$ `story-framer` & `story-unknowns-mapper`
- **`ui-visual-calibration` & `ui-system`** $\rightarrow$ `experience-calibration` & `story-bible-tokens`
- **`ui-blueprint` & `ui-screen-spec`** $\rightarrow$ `cartographer-outline` & `scene-spec`
- **`ui-inspector` & `ui-redline`** $\rightarrow$ `prose-critic` & `narrative-redline`
- **`ui-spec-reconcile`** $\rightarrow$ `story-canon-reconciler`

To support these cognitive skills programmatically, we require a unified, schema-safe CLI command family (`auteur state`) to inspect, transactionalize, and audit the story spine across all 9 engine layers. 

## Decision

We will implement a unified **Narrative Engineering Lifecycle** supported by a programmatic `auteur state` CLI command family and a unified diagnostic adapter bridge.

### 1. The 4-Phase Narrative Engineering Lifecycle

The adapted skills will compose into a continuous, high-integrity feedback loop:
1.  **Phase 0: Ideation & Recovery**: `story-framer` structures creative fog into a `StoryIdentity` brief, while `story-unknowns-mapper` isolates speculative lore elements.
2.  **Phase 1: Seed & Constraint Calibration**: `experience-calibration` establishes emotional wave thresholds, and `story-bible-tokens` generates base schema ledgers.
3.  **Phase 2: Execution & Inspection**: `prose-critic` checks active chapter tone and pacing, while `narrative-redline` detects **Narrative Drift** by comparing chapter drafts against outlines and bible states.
4.  **Phase 3: Revision & Reconciliation**: `story-canon-reconciler` cascades structural mutations across all ledgers when the author updates structural parameters mid-novel.

### 2. The `auteur state` Command Family

A new command namespace `auteur state` will manage mutations and audits across Auteur's physical ledgers (`blueprint.yaml`, `bible.json`, `outline.yaml`, and `structure/proposals/`):
-   `check`: Unified validation pass running both the deterministic structure analyzer (Layers 1-5, 9) and the carrier transition auditor (Layer 6).
-   `update <file> --key <key> --val <val>`: Transactional, schema-safe field mutation with automatic Pydantic validation and rollback on failure.
-   `prepare <phase> --scope <scope>`: Generates standard Markdown handoff packets for downstream drafting or revision agent chains.
-   `canon`: Compiles a clean, high-fidelity reference report of world entities and lore.
-   `confirm <recovery.yaml>`: Safely merges confirmed recovery layers into the active blueprint.

### 3. The Adapter Bridge

To enable a single, unified proposal generator (`propose_repairs_from_diagnostics`) to write unified YAML Decision Packets for **any** layer violation, we adopt the **Adapter Pattern**. 

All diagnostic checkers—regardless of layer—must return or be adapted into the canonical `StructureDiagnostic` format containing a `repair_options` payload:

```python
class DiagnosticLayer(str, Enum):
    TARGET_EXPERIENCE = "Layer 1"
    CONSTRAINTS = "Layer 2"
    SCOPE = "Layer 3"
    STRUCTURAL_FORCES = "Layer 4"
    THREADS = "Layer 5"
    CARRIERS = "Layer 6"
    REPRESENTATION = "Layer 7"
    MODULATION = "Layer 8"
    RESONANCE = "Layer 9"

class StructureDiagnostic(BaseModel):
    severity: str  # "error" | "warning"
    layer: DiagnosticLayer
    rule: str
    evidence: str
    repair_options: RepairOptions = Field(default_factory=RepairOptions)
    affected_blueprint_fields: list[str] = Field(default_factory=list)
```

Bible-layer location anomalies (`BibleAuditDiagnostic` from Layer 6) will be converted programmatically via `as_structure_diagnostic()` before being passed downstream to the proposal engine.

### 4. Implementation Sequencing (Infrastructure-First)

We will sequence the development sequentially to preserve the **"Brain vs. Worker"** boundary:
1.  **Phase 1: Core Harness**: Build the programmatic `auteur state check` unified validation harness, then wire up the **`prose-critic & narrative-redline`** cognitive skill on top of it.
2.  **Phase 2: Transactions**: Build transactional `update` mutations and `prepare` context compilers.
3.  **Phase 3: Canon & Recovery**: Build canon reports and `confirm` recovery merges.

## Consequences

-   **High Handoff Fidelity**: AI agents use deterministic CLI tool calls (`auteur state check`) to diagnose projects, reducing hallucination risks.
-   **Zero Narrative Drift**: Discrepancies between drafted prose, scene cards, and bible entities are caught early and reported in a unified manner.
-   **Simplified Proposal Codebase**: The proposal generation and application pipelines (`auteur structure apply`) now process a single, unified type stream.
-   **Controlled Mutation**: Authors maintain absolute sovereignty; all structural proposals must be explicitly resolved in the proposal ledger before merging.
