---
name: story-identity-architect
description: "agentic creative brief builder designed to refine raw ideas, execute a structured grilling workflow, and compile a validated story_identity.yaml."
---

# Story Identity Architect Skill

An opinionated story architect skill designed to refine chaotic creative ideas, recommend the strongest genre-aligned story engine implied by the premise, execute a structured "grilling workflow" for conceptual alignment, and output a validated `story_identity.yaml` ready to seed a structural `blueprint.yaml` skeleton.

## Meta
- **Name**: story-identity-architect
- **Goal**: Transition a raw, unstructured story idea into a recommended high-level story engine without losing authorial intent.
- **Output**: Validated `story_identity.yaml` and a seeded `blueprint.yaml` skeleton.

---

## 1. The Grilling Workflow

When executing this skill, the agent must **never** make all decisions silently. Its internal role is **Opinionated Story Architect**: recommend strongly, explain why, and preserve explicit author override.

The default optimization basis for "best" is `genre_aligned`: choose the engine that best fulfills the selected genre/subgenre promise while staying coherent and faithful enough to the author's raw input.

The agent must use a disciplined **grilling workflow**:

1. **Recommend One Primary Engine First**: Infer the strongest story engine and present it before alternatives.
2. **Explain Why It Is Best**: Tie the recommendation to genre promise, target experience, structural coherence, and author input.
3. **Show Two Alternatives**: Briefly name viable but weaker directions.
4. **Ask One Question at a Time**: Never overwhelm the author with a giant questionnaire. Focus on the highest-leverage correction.
5. **Lock Decisions Explicitly**: Ask whether the author accepts, modifies, or switches to open-ended exploration before moving to the next layer.

### Grilling Sequence

The grilling workflow focuses strictly on the high-level conceptual brief (`StoryIdentity`):

- **Phase 1: Target Experience & Core Answer (Layer 1)**: What is this story really about? What is the singular creative premise (core answer)? What is the target emotional promise, emotional progression, and what emotional states or tropes must be avoided?
- **Phase 2: Story Type & Promise Constraints (Layer 2)**: Medium (novel, novella, short story), Mode (tragic, mythic, adventure, noir, intimate, epic, other), Genre, subgenres, Target Audience, and boundaries—**What This Is Not** (defining creative boundaries).
- **Phase 3: Central Engine Forces (Layer 4)**: The high-level dramatic forces of the central story engine: Want (protagonist ambition), Resistance (core opposition), Conflict (collision of want and internal cost), Stakes (compounding cost of success/failure), and Change (how the protagonist/world is altered).
- **Phase 4: Alternatives, Open Questions & Confidence**: Open questions, narrative alternatives, and the author's confidence score.
- **Phase 5: Recommendation Rationale & Overrides**: Why the recommended engine is best, which directions were rejected, and which author overrides must be preserved.

> [!NOTE]
> Detailed structural constants (subplot budgets, chapter divisions, POV lists) and subplot tapestries are deferred to the structure coherence auditor and cartographer outline compiler stages to keep the initial design brief pure and lightweight.

---

## 2. Story Identity Brief Format

Once the grilling sequence is completed and all decisions are explicitly approved, the agent generates a markdown brief in the following standard format and saves it to `docs/story_identity_brief.md`:

```markdown
# Story Identity Brief

## Core Answer
[What the story is becoming / the singular creative compass]

## 1. Target Experience (Layer 1)
- **Primary Emotional Promise**: [e.g., dread, wonder, tension]
- **Emotional Progression**: [e.g., unease -> dread -> catharsis]
- **Avoided Outcomes**: [List of emotions or tones to avoid]

## 2. Promise / Constraints (Layer 2)
- **Medium**: [e.g., novel, short_story]
- **Mode**: [e.g., tragic, mythic, adventure]
- **Genre**: [e.g., grimdark_fantasy, epic_fantasy, thriller, sci_fi]
- **Subgenres**: [List of subgenres]
- **Audience Promise / Target Audience**: [e.g., adult, young_adult]
- **What This Is Not**:
  - [Boundary 1]
  - [Boundary 2]

## 3. Central Engine Forces (Layer 4)
- **Want**: [The primary protagonist ambition]
- **Resistance**: [The core opposition blocking resolution]
- **Conflict**: [The collision of want and internal cost]
- **Stakes**: [The compounding cost of success or failure]
- **Change**: [How the protagonist or world is altered irrevocably]

## 4. Alternatives & Open Questions
- **Open Questions**:
  - [Question 1]
- **Alternatives Considered**:
  - [Alternative 1]
- **Confidence Score**: [e.g., 0.9]

## 5. Recommendation Contract
- **Mode**: opinionated
- **Best Basis**: genre_aligned
- **Why This Is Best**: [Rationale for the recommended engine]
- **Rejected Directions**:
  - [Weaker direction 1]
- **Author Overrides**:
  - [Explicit override 1]

## Coherence Risks
- [Risk 1: Potential plot-holes or thematic clashes]
```

---

## 3. YAML Compilation & Seed Workflow

Once the brief is generated, the agent compiles it into `story_identity.yaml`.

### Schema Specification (`story_identity.yaml`)

```yaml
title: "The Shattered Crown"
core_answer: "A grimdark epic about a hero who succeeds at his quest by becoming the thing he hunted."
target_experience:
  primary: "dread"
  progression: "unease -> dread -> catharsis"
  avoid:
    - "triumphant power fantasy"
    - "cozy safety"
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "grimdark_fantasy"
  subgenres:
    - "grimdark"
    - "corruption_tragedy"
  target_audience: "adult"
central_engine:
  want: "Kael wants to end the war by destroying the tyrant who ruined his kingdom."
  resistance: "The tyrant's power is bound to the same cursed magic Kael is tempted to use."
  conflict: "Kael can win quickly by becoming ruthless, or preserve his humanity and risk losing the war."
  stakes: "Every victory bought saves people now while making Kael more dangerous later."
  change: "Kael changes from a wounded avenger into the new source of darkness."
not_this:
  - "a cozy standard fantasy"
open_questions:
  - "Will Lira betray Kael before the final gate?"
alternatives:
  - "A path where Kael sacrifices himself instead of choosing the dark throne."
confidence: 0.9
recommendation_mode: "opinionated"
best_basis: "genre_aligned"
why_this_is_best: "The grimdark premise is most genre-aligned when victory and corruption are fused: readers expect moral cost, compromised agency, and an ending that fulfills dread rather than clean triumph."
rejected_directions:
  - "A heroic chosen-one victory would break the grimdark corruption promise."
  - "A cozy rebellion adventure would undercut the target experience of dread."
author_overrides:
  - "Keep Kael's final transformation tragic rather than redemptive."
```

### Validation & Seeding Commands

The agent verifies the yaml file:
```bash
# 1. Validate the story identity schema
auteur identity validate story_identity.yaml

# 2. Compile/Seed into a standard blueprint skeleton
auteur blueprint seed story_identity.yaml --output blueprint.yaml

# 3. Diagnose the newly seeded blueprint to ensure compliance
auteur structure diagnose blueprint.yaml
```

---

## 4. Modes of Operation

The Story Identity Architect skill supports two distinct modes of execution depending on the author's starting point:

### A. The Grilling Mode (`--interactive` / `--grill`)
Use this mode when starting from high **creative fog** (vague premises, unrefined world ideas, chaotic character thoughts). 
- **Workflow**: The agent initiates the opinionated step-by-step grilling sequence (Section 1).
- **Execution**: The agent recommends the strongest engine, explains why, asks exactly one correction question at a time, and waits for explicit approval before proceeding.
- **Output**: Resolves creative fog, resulting in a compiled `story_identity.yaml`.

### B. Open-Ended Exploration Mode (`--explore`)
Use this mode when the author explicitly wants exploration rather than decisive direction.
- **Workflow**: The agent presents three viable engines and their tradeoffs.
- **Execution**: The agent waits for the author to choose, combine, or reject the options before compiling `story_identity.yaml`.
- **Output**: Locks the selected or edited engine as `recommendation_mode: open_ended`.

### C. Direct Seeding Mode (`--seed`)
Use this mode when the author already has a structured plan or structured parameters ready to be committed.
- **Workflow**: The agent bypasses the interactive grilling sequence and directly maps parameters into the schema.
- **Execution**: The agent validates the input against the Pydantic schema and seeds the target files without manual interrogation.
- **Output**: Directly generates `story_identity.yaml` and seeds the skeleton `blueprint.yaml`.

---

## 5. Architectural Boundaries & Contrasts

To maintain clear system boundaries, the Auteur engineering engine separates concept generation from structural diagnostics and execution-time lore auditing:

*   **Story Identity Architect** (Concept Seeding): Solves **creative fog** (Layer 1–4). Operates interactively to extract and lock the high-level intent, medium, and constraint bounds.
*   **Structure Coherence Auditor** (Blueprint Validation): Solves **blueprint incoherence** (Layer 1–9). Validates that the story engine flows correctly (want $\neq$ change, subplots fit within scope budgets) using deterministic diagnostics.
*   **Story Grill** (Narrative Stress-Testing): Solves **narrative and lore drift** (Layer 6–8). Stress-tests a specific proposed chapter outline or scene draft against the current world bible carrier states and core constraints to prevent continuity errors before chapters are finalized.
