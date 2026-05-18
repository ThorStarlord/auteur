---
name: structure-coherence-auditor
description: "An agentic structure auditor skill designed to take a seeded blueprint, execute deterministic diagnostics, and guide structural repairs."
---

# Structure Coherence Auditor Skill

An agentic structure auditor skill designed to take a seeded structural blueprint, execute deterministic diagnostics, and guide the author through an inside-out "grilling and resolution sequence" to achieve 100% architectural coherence.

## Meta
- **Name**: structure-coherence-auditor
- **Goal**: Transition a raw seeded `blueprint.yaml` into a green, fully-validated `StoryBlueprint` ready for drafting.
- **Output**: Fully-resolved `blueprint.yaml` and a durable `docs/structure_coherence_report.md` audit trail.

---

## 1. Cognitive Architecture: Brain vs. Worker

When executing this skill, the agent functions as the **Brain (Cognitive Orchestrator)** while the Auteur CLI operates as the **Worker (Deterministic Executor)**.

- **The Brain (You)**: Manages author pacing, intent, vocabulary, prioritizes diagnostic findings, and interactively grills the author to select resolutions.
- **The Worker (CLI)**: Performs hard calculations, schema validation, non-destructive file merging, and serves as the safety rails. You must **never** manually edit blueprint fields unless guided by the CLI proposal application tools.

---

## 2. The Interactive Resolution Sequence

The agent must walk the author through a strict **4-Phase Sequence**, prioritizing core narrative forces before minor details.

### Phase 1: Structural Diagnostics Audit
Run the deterministic diagnostic tool to fetch the current gaps:
```bash
auteur structure diagnose blueprint.yaml
```
- Capture the output diagnostics. If the command exits with `0` (Zero Gaps), skip to Phase 4.

### Phase 2: Decision Packet Generation
Generate the structured proposals:
```bash
auteur structure propose-repairs blueprint.yaml
```
- This writes files to `structure/proposals/` (e.g. `structure/proposals/proposal_01_engine_want.yaml`).
- Parse the proposal files to extract options, rules, and affected fields.

### Phase 3: Priority-Ordered Grilling & Selection
Present unresolved proposals one at a time to the author. Do not present them as a flat, overwhelming list. Walk through them in **Inside-Out Narrative Priority (the 5-Tier Narrative Priority Matrix)**:

1. **Tier 1: Intent & Boundaries** (Layers 1-2: Target Experience, Promise/Constraints) - Higher-level core premise conflicts and genre/constraint clashes.
2. **Tier 2: Blueprint Canvas & Forces** (Layers 3-5: Scope/Scale, Structural Forces, Threads/Modules) - Central story engine forces, subplot budgets, and thread configurations.
3. **Tier 3: Carriers & Factions** (Layer 6: Carriers) - World entities, characters, and relationships (e.g. missing character wants or relationships).
4. **Tier 4: Representation & Modulation** (Layers 7-8: Representation, Modulation) - Outline, scenes, POV assignments, and pacing dynamics (checked during drift audits).
5. **Tier 5: Resonance & Coherence** (Layer 9: Resonance/Coherence) - Thematic coherence (e.g. ensuring threads support the thematic thesis).

For each prioritized proposal:
1. **Ask One Question**: Describe the gap, cite the exact evidence, and list the 2-3 options.
2. **Provide a Recommendation**: Recommend one option, explaining *why* it aligns with the creative intent established in `story_identity.yaml`.
3. **Wait for Approval**: Explicitly wait for the author to select or refine the option.

Once an option is selected:
- Update the proposal file on disk by setting the `selection.selected_option_id` field.
- Invoke the deterministic worker to merge the choice:
  ```bash
  auteur structure apply structure/proposals/<proposal_file>.yaml blueprint.yaml
  ```
- Re-run diagnostics to confirm the gap is resolved:
  ```bash
  auteur structure diagnose blueprint.yaml
  ```

### Phase 4: Final Verification & Report Compilation
Once `auteur structure diagnose blueprint.yaml` exits with `0` (No violations):
1. Compile the complete history of initial gaps and resolutions into a durable report and save it to `docs/structure_coherence_report.md`.
2. Present the final success report to the author.

---

## 3. Structure Coherence Report Format

The agent must output the final report in this exact format to `docs/structure_coherence_report.md`:

```markdown
# Structure Coherence Report

## 1. Executive Summary
- **Blueprint Title**: [Blueprint Title]
- **Final Coherence Status**: PASS (Zero structural violations remaining)
- **Audit Execution Date**: [Timestamp]

## 2. Initial Structural Gap Log
[A list of the original diagnostics produced by `auteur structure diagnose` at the start of the session, including severity, layer, and description.]

## 3. Resolution Trail
| Proposal ID | Layer | Selected Option | Narrative Design Decision |
|---|---|---|---|
| [Proposal ID] | [Layer] | [Selected Option] | [Conceptual impact and creative intent] |

## 4. Solidified Whole-Story Engine
- **Main Thread**: [Core dramatic want, resistance, stakes, and irreversible change]
- **Subplots**: [List of subordinate threads, their core conflicts, and their exact thematic functions]
- **Primary Core Constraints**: [Confirmed Genre, Mode, Medium, and Scale]

## 5. Next Authorial Steps
- Structural blueprint is verified and green. Ready to transition to the `auteur draft` pipeline.
```
