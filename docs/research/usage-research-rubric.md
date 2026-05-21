# Usage Research Scoring Rubric

This rubric is used to semantically evaluate the quality of artifacts produced by the sensemaking pipeline. It moves beyond structural YAML validity to assess the **semantic usefulness** and **handoff readiness** of the research outputs.

## Scoring Scale
- **0 (Absent)**: Required information is missing or completely irrelevant.
- **1 (Vague)**: Information is present but too abstract to guide action (e.g., "improve the repo").
- **2 (Partially Useful)**: Information is grounded but lacks specific search seeds or measurable boundaries.
- **3 (Concrete & Handoff-Ready)**: Information is precisely grounded in repository state with clear search targets and verifiable stopping rules.

---

## 1. Problem Frame Evaluation

### Object Under Pressure
- **1**: Vague target like "the project" or "the codebase."
- **2**: General area like "the documentation" or "the scripts."
- **3**: Specific file or registry (e.g., `workflow-registry.yaml`, `SKILL.md` boundary).

### Failure Mode
- **1**: Emotional description ("it's confusing").
- **2**: Functional description ("it fails to route").
- **3**: Technical causality ("hallucinated continuity due to missing initial_inputs validation").

### What Must Be True
- **1**: Generic assumptions ("the code must work").
- **2**: Operational assumptions ("the skill must be registered").
- **3**: Contractual invariants ("Step 3 must receive a grounded Object Under Pressure to avoid blind scanning").

---

## 2. Unknowns Map Evaluation

### Critical Unknowns
- **1**: General curiosity ("how does it work?").
- **2**: Specific questions about logic or data.
- **3**: High-leverage unknowns that block a specific search path.

### Research Paths
- **1**: Broad intent ("research the repo").
- **2**: Specific intent ("check the validator logic").
- **3**: Executable search strategy ("Verify the `subset_run` regex in `validate-plan.py` against non-contiguous cases").

### Stopping Rule
- **1**: Time-based or vague ("Stop when done").
- **2**: Outcome-based but subjective ("Stop when it feels stable").
- **3**: Verifiable & grounded ("Stop when all negative fixtures in `examples/negative/` fail and the current research run passes").

---

## 3. Orchestration & Handoff Evaluation

### Routing Quality
- **1**: Incorrect workflow or skill chosen.
- **2**: Correct workflow but suboptimal configuration.
- **3**: Precision routing that matches the Object Under Pressure.

### Handoff Readiness
- **1**: Blind handoff requiring downstream re-discovery.
- **2**: Context provided but requires manual cleanup.
- **3**: Seeded handoff; downstream skill knows exactly where to start scanning.
