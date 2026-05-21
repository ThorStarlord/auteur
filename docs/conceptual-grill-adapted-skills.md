# Conceptual Grill Session: Adapted Sensemaking & Interface Skills

**Date**: 2026-05-18  
**Mode**: Autonomous Q/A (no user pauses, approved per instruction)  
**Source Context**: [CONTEXT.md](file:///h:/GithubRepositories/auteur/CONTEXT.md), [AGENTS.md](file:///h:/GithubRepositories/auteur/AGENTS.md), [docs/adr/005-unified-diagnostics-and-state-commands.md](file:///h:/GithubRepositories/auteur/docs/adr/005-unified-diagnostics-and-state-commands.md), [docs/prd-adapted-sensemaking-skills.md](file:///h:/GithubRepositories/auteur/docs/prd-adapted-sensemaking-skills.md)

---

## 1. Goal Extraction & Mandate

### Primary Goal
Stress-test the conceptual plan to adapt developer-grade tools from the `sensemaking-skills` and `interface-skills` ecosystems to narrative engineering in Auteur.

### Core Constraint (Sovereignty)
Ensure that all adapted skills respect creative authorial sovereignty. AI-assisted elements must function as the **Brain (Cognitive Orchestrator)** guiding interactive choices, while the Auteur CLI operates as the **Worker (Deterministic Executor)**.

---

## 2. Fully Resolved Question Chain

### Question 1: How should we treat a "mismatch" detected by adapted diagnostic/redline skills?
*   **Recommended Answer**: All diagnostic mismatches from adapted skills are formulated as Decision Packets (`StructureProposal` YAML artifacts) presenting a dual-choice path: **Preserve Creative Intent** (challenge and update the contract/Bible) or **Preserve Constraint** (align the draft). Under no circumstances will the agent perform silent refactors or direct, non-consensual rewrites.
*   **Status**: **Approved & Locked**
*   **Evidence**: [AGENTS.md:L14-L15](file:///h:/GithubRepositories/auteur/AGENTS.md#L14-L15), [CONTEXT.md:L81-L85](file:///h:/GithubRepositories/auteur/CONTEXT.md#L81-L85).

### Question 2: How do we cleanly split labor between deterministic code and generative LLM assistance during the `blueprint-to-cartographer` (outline compiler) phase?
*   **Recommended Answer**: Enforce a strict **Two-Step Structural Compilation Pipeline**. 
    *   *Step 1: Deterministic Skeleton Compilation (Worker)* compiles structural constraints (acts, subplots, location logs, POV) programmatically via Python CLI commands with zero LLM calls, producing a valid Pydantic model (`CartographerOutline`).
    *   *Step 2: Interactive Generative Enrichment (Brain)* uses the LLM Brain and author to layer on creative details (want/resistance, thematic questions, clue beats) within the deterministic skeleton container.
*   **Status**: **Approved & Locked**
*   **Evidence**: [AGENTS.md:L35](file:///h:/GithubRepositories/auteur/AGENTS.md#L35), [AGENTS.md:L23-L25](file:///h:/GithubRepositories/auteur/AGENTS.md#L23-L25).

### Question 3: How should we execute and report on semantic assertions in the `chapter-acceptance-testing` (TDD) skill without creating "flaky" non-deterministic gates?
*   **Recommended Answer**: Enforce a strict separation between **Hard Gates (Deterministic Constraints)** and **Soft Gates (Semantic Evaluations)**:
    *   *Hard Gates*: Absolute requirements checked programmatically by Python (word count, POV syntax, spatial location logs). Failure returns a strict exit code `1`, blocking the process.
    *   *Soft Gates*: Qualitative evaluations run by the LLM `prose-critic` (tone shifts, clue reveals). These *never* cause a CLI exit failure. Instead, they output a **Semantic Feedback Report** with heuristic confidence scores. The author holds final sovereignty to sign off on these or trigger an interactive rewrite.
*   **Status**: **Approved & Locked**
*   **Evidence**: [AGENTS.md:L35-L37](file:///h:/GithubRepositories/auteur/AGENTS.md#L35-L37), [docs/prd-story-grill-skill.md:L86-L88](file:///h:/GithubRepositories/auteur/docs/prd-story-grill-skill.md#L86-L88).

### Question 4: How should `story-thread-flow` (the tapestry visualizer adapted from `ui-flow`) visualize subplots and want/resistance collisions without introducing heavy graphical rendering dependencies?
*   **Recommended Answer**: Leverage **Mermaid Markdown** and **ANSI Terminal Plots**.
    *   The planned CLI command `auteur thread flow` should compile the structural forces of all active threads into a standard **Mermaid diagram** (natively renderable in markdown environments like VS Code, GitHub, and agent UI packages).
    *   The terminal output uses ANSI color-blocked rows to represent subplot density per act, flagging "orphaned subplots" (unresolved arcs) in high-contrast red.
*   **Status**: **Approved & Locked**
*   **Evidence**: [docs/prd-adapted-sensemaking-skills.md:L68-L70](file:///h:/GithubRepositories/auteur/docs/prd-adapted-sensemaking-skills.md#L68-L70), [CONTEXT.md:L38-L41](file:///h:/GithubRepositories/auteur/CONTEXT.md#L38-L41).

### Question 5: How should `prose-critic-redline` (the style critic adapted from `ui-redline`) format its output to be highly usable for both humans and downstream AI agents?
*   **Recommended Answer**: Produce a two-part output:
    1.  **Human Representation**: A colored ANSI terminal diff (using green/red blocks) showing vocabulary bans, POV slips, and pacing anomalies inline with prose lines.
    2.  **Machine Representation**: A structured `StructureProposal` YAML file written to `structure/proposals/` under `source_domain = "prose_redline"`. This enables downstream editing agents to call programmatic tools to parse and fix structural style issues systematically.
*   **Status**: **Approved & Locked**
*   **Evidence**: [docs/adr/005-unified-diagnostics-and-state-commands.md:L41-L44](file:///h:/GithubRepositories/auteur/docs/adr/005-unified-diagnostics-and-state-commands.md#L41-L44).

### Question 6: How do we structure the `story-canon-reconciler` (adapted from `ui-spec-reconcile`) to safely cascade structural changes without corrupting historical chapter events?
*   **Recommended Answer**: Implement an **Event-Sourced Canon Migration Ledger**:
    *   Historical drafted chapters and their accepted event logs are **immutable**.
    *   If an author updates structural blueprint properties mid-novel (e.g., renaming a location, character, or editing a backstory event), the reconciler writes a **Canon Migration Event** to a local migrations ledger.
    *   Future bible audits replay the ledger to reconstruct the "current view" of world states. This maintains high historical auditability without corrupting previously accepted chapter state deltas.
*   **Status**: **Approved & Locked**
*   **Evidence**: [docs/adr/005-unified-diagnostics-and-state-commands.md:L28-L29](file:///h:/GithubRepositories/auteur/docs/adr/005-unified-diagnostics-and-state-commands.md#L28-L29).

### Question 7: How do we package these adapted skills to make them highly discoverable and testable?
*   **Recommended Answer**: Mirror the existing `skills/` design structure. Each adapted skill contains:
    1.  A standard `SKILL.md` file detailing Brain behaviors and prompt contracts.
    2.  Wiring into Auteur's test suite (`tests/`) where the programmatic commands (e.g., `auteur state check` and `auteur audit --repair`) are verified with unit and integration tests.
*   **Status**: **Approved & Locked**
*   **Evidence**: [AGENTS.md:L32-L34](file:///h:/GithubRepositories/auteur/AGENTS.md#L32-L34)

### Question 8: When a user gets a "failed" diagnostic report on their blueprint.yaml, how does Auteur distinguish between a structural mistake and a deliberate creative choice?
*   **Recommended Answer**: Auteur distinguishes between them by classifying violations into schema errors and coherence errors, then checking for explicit author overrides:
    *   *Syntactic/Schema errors* (e.g. malformed YAML, invalid types) are always structural mistakes, validated via Pydantic; they cannot be bypassed and halt compilation.
    *   *Coherence & Genre contract errors* (e.g. romance ending in a tragedy) are treated as structural mistakes *only if no override is declared*.
    *   *If an override is declared* in the blueprint's `genre_overrides` mapping under `ProjectIdentity` (classified as `safe_variation`, `compression`, `subversion`, or `reclassification`), Auteur treats the violation as a deliberate creative choice. It suppresses the error/warning and emits tailored creative advice.
*   **Status**: **Approved & Locked**
*   **Evidence**: [docs/adr/010-genre-overrides-classification.md](file:///h:/GithubRepositories/auteur/docs/adr/010-genre-overrides-classification.md), [tests/test_genre_overrides.py](file:///h:/GithubRepositories/auteur/tests/test_genre_overrides.py)

### Question 9: How does Auteur dynamically adapt its structural validation rules for a given story blueprint without hardcoding a massive, fragile mapping of specific genre rules in the Python code?
*   **Recommended Answer**: Auteur decouples rule enforcement from rule definitions by storing genre and medium contracts declaratively in YAML registry files (e.g., `mystery.yaml`, `romance.yaml`). The python structure diagnostics engine (`auteur.structure.analyzer`) contains only generic, reusable validation checks that evaluate attributes of the loaded contract object (e.g., set containment, trope intersection, and ordinal runway-to-container math). This allows adding or changing genres without mutating code.
*   **Status**: **Approved & Locked**
*   **Evidence**: [src/auteur/genres/data/](file:///h:/GithubRepositories/auteur/src/auteur/genres/data/), [src/auteur/structure/analyzer.py](file:///h:/GithubRepositories/auteur/src/auteur/structure/analyzer.py)

### Question 10: How does Auteur map a writer's fluid, creative, and qualitative intent (e.g., target experience feelings, themes, and emotional promises) into a rigid, parseable StoryBlueprint without over-constraining the writer or forcing formulaic structures?
*   **Recommended Answer**: Auteur achieves this through:
    *   *Layered Separation*: Segmenting qualitative creative fields (Layers 1 and 9) from the quantitative structure fields (Layers 2-7). Qualitative fields are typed and parsed for schema completeness, but their internal creative content is not audited for semantic "goodness".
    *   *Deterministic Relational Heuristics*: Using vocabulary intersections (e.g., checking if thesis terms echo in thread thematic functions) and basic checks (e.g., ensuring wants don't duplicate transformation changes) to verify coherence without subjective bias.
    *   *Hard vs. Soft Gates*: Restricting hard failures to logical inconsistencies (e.g. subplot budget, teleportation), while deferring qualitative reviews to interactive downstream critic checks that generate soft reports rather than blocking compilation.
*   **Status**: **Approved & Locked**
*   **Evidence**: [docs/opinionated-narrative-engine.md](file:///h:/GithubRepositories/auteur/docs/opinionated-narrative-engine.md), [src/auteur/structure/analyzer.py](file:///h:/GithubRepositories/auteur/src/auteur/structure/analyzer.py)

---

## 3. Execution Plan

Having completed the conceptual grilling phase and obtained full strategic alignment, we will execute the following steps:
1.  Verify that all new documentation files compile cleanly and match Auteur's strict domain grammar (using no banned words like *plot hole* or *consistency scan*).
2.  Provide a comprehensive walkthrough of the adapted skill catalog to ensure future developers and agents can immediately utilize these structural tools.
