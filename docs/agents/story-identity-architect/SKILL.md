# Story Identity Architect Skill

An agentic creative architect skill designed to refine chaotic creative ideas, execute a structured "grilling workflow" for conceptual alignment, and output a validated `story_identity.yaml` ready to seed a structural `blueprint.yaml` skeleton.

## Meta
- **Name**: Story Identity Architect
- **Goal**: Transition a raw, unstructured story idea into a clear, high-level creative contract without losing authorial intent.
- **Output**: Validated `story_identity.yaml` and a seeded `blueprint.yaml` skeleton.

---

## 1. The Grilling Workflow

When executing this skill, the agent must **never** make all decisions silently. The agent must use a disciplined **grilling workflow**:

1. **Ask One Question at a Time**: Never overwhelm the author with a giant questionnaire. Focus on one core element of the story identity at a time.
2. **Provide a Recommended Answer**: When asking a question, provide a high-fidelity recommended answer based on their previous inputs.
3. **Lock Decisions Explicitly**: Wait for the author to approve, adjust, or reject the recommendation before moving to the next question.

### Grilling Sequence
- **Phase 1: The Core Answer**: What is this story really about? What is the singular premise?
- **Phase 2: The Emotional Experience**: What is the target emotional promise? What feeling should we avoid?
- **Phase 3: Classification & Bounds**: Genre, Mode, Medium, and crucially—**What This Is Not** (defining creative boundaries).
- **Phase 4: The Central Engine**: The high-level structural forces (Want, Resistance, Conflict, Stakes, Change).
- **Phase 5: Open Questions**: Identifying the crucial narrative and thematic questions left unresolved.

---

## 2. Story Identity Brief Format

Once the grilling sequence is completed and all decisions are explicitly approved, the agent generates a markdown brief in the following standard format and saves it to `docs/story_identity_brief.md`:

```markdown
# Story Identity Brief

## Core Answer
[What the story is becoming / the singular creative compass]

## Reader Experience
- **Primary Emotional Promise**: [e.g., dread, wonder, tension]
- **Emotional Progression**: [e.g., unease -> dread -> catharsis]
- **Avoided Outcomes**: [List of emotions or tones to avoid]

## Story Type
- **Medium**: [e.g., novel, short_story]
- **Mode**: [e.g., tragic, heroic, open]
- **Genre**: [e.g., grimdark_fantasy, thriller, sci_fi]
- **Subgenres**: [List of subgenres]
- **Audience Promise / Target Audience**: [e.g., adult, young_adult]

## Central Story Engine
[A summary of the core conflict mechanism]

## High-Level Structural Forces
- **Want**: [The primary protagonist ambition]
- **Resistance**: [The core opposition blocking resolution]
- **Conflict**: [The collision of want and internal cost]
- **Stakes**: [The compounding cost of success or failure]
- **Change**: [How the protagonist or world is altered irrevocably]

## What This Is Not
- [Boundary 1]
- [Boundary 2]

## Coherence Risks
- [Risk 1: Potential plot-holes or thematic clashes]

## Next Authorial Questions
- [Question 1]
- [Question 2]
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
