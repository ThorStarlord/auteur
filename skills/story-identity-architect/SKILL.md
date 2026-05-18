---
name: story-identity-architect
description: "An agentic creative brief builder designed to refine raw ideas, execute a structured grilling workflow, and compile a validated story_identity.yaml."
---

# Story Identity Architect Skill

An agentic creative architect skill designed to refine chaotic creative ideas, execute a structured "grilling workflow" for conceptual alignment, and output a validated `story_identity.yaml` ready to seed a structural `blueprint.yaml` skeleton.

## Meta
- **Name**: story-identity-architect
- **Goal**: Transition a raw, unstructured story idea into a clear, high-level creative contract without losing authorial intent.
- **Output**: Validated `story_identity.yaml` and a seeded `blueprint.yaml` skeleton.

---

## 1. The Grilling Workflow

When executing this skill, the agent must **never** make all decisions silently. The agent must use a disciplined **grilling workflow**:

1. **Ask One Question at a Time**: Never overwhelm the author with a giant questionnaire. Focus on one core element of the story identity at a time.
2. **Provide a Recommended Answer**: When asking a question, provide a high-fidelity recommended answer based on their previous inputs.
3. **Lock Decisions Explicitly**: Wait for the author to approve, adjust, or reject the recommendation before moving to the next question.

### Grilling Sequence

The grilling workflow focuses strictly on the high-level conceptual brief (`StoryIdentity`):

- **Phase 1: Target Experience & Core Answer (Layer 1)**: What is this story really about? What is the singular creative premise (core answer)? What is the target emotional promise, emotional progression, and what emotional states or tropes must be avoided?
- **Phase 2: Story Type & Promise Constraints (Layer 2)**: Medium (novel, novella, short story), Mode (tragic, heroic, open), Genre, subgenres, Target Audience, and boundaries—**What This Is Not** (defining creative boundaries).
- **Phase 3: Central Engine Forces (Layer 4)**: The high-level dramatic forces of the central story engine: Want (protagonist ambition), Resistance (core opposition), Conflict (collision of want and internal cost), Stakes (compounding cost of success/failure), and Change (how the protagonist/world is altered).
- **Phase 4: Alternatives, Open Questions & Confidence**: Open questions, narrative alternatives, and the author's confidence score.

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
- **Mode**: [e.g., tragic, heroic, open]
- **Genre**: [e.g., grimdark_fantasy, thriller, sci_fi]
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
- **Workflow**: The agent initiates the step-by-step grilling sequence (Section 1).
- **Execution**: The agent asks exactly one question at a time, recommends an answer, and waits for explicit approval before proceeding.
- **Output**: Resolves creative fog, resulting in a compiled `story_identity.yaml`.

### B. Direct Seeding Mode (`--seed`)
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
