---
name: Prose Critic Redline
description: "An agentic style-auditing skill designed to compare chapter drafts directly against style contracts and generate redline reports."
---

# Prose Critic Redline Skill

An agentic style-auditing skill designed to compare completed chapter draft prose directly against its `chapter_contract.yaml` (Layer 8) constraints (vocabulary bans, active voice ratio, POV violations), generating highlighted redline mismatch reports to guide rapid revisions.

## Meta
- **Name**: Prose Critic Redline
- **Goal**: Audit draft prose against style contracts, highlighting exact lines that drift from creative constraints.
- **Output**: A detailed Redline Mismatch Report with highlighted text segments and actionable revision prompts.

---

## 1. Cognitive Architecture: Brain vs. Worker

When executing this skill, the agent functions as the **Brain (Cognitive Orchestrator)** while the Auteur CLI operates as the **Worker (Deterministic Executor)**.

- **The Brain (You)**: Analyzes the artistic flow of the prose, identifies stylistic friction (passive transitions, character voice slips), designs contextual revision instructions for the writing engine, and guides the author through a step-by-step resolution loop.
- **The Worker (CLI)**: Compiles metrics (word count, sentence structures), executes deterministic pattern scanners (regex/NLP for banned words or passive constructions), checks for required clue occurrences, and highlights exact line numbers.

---

## 2. The Interactive Redline Resolution Loop

The agent must walk the author through a strict **5-Phase Sequence** to audit and fix prose drift:

### Phase 1: Context Hydration
Before executing any style audits, load the creative contracts:
1. Parse the target chapter's contract from `chapter_contract.yaml` (metrics, transitions, reveals, style limits).
2. Hydrate the raw chapter draft text (Layer 8 representation).

### Phase 2: Budget & Transition Verification (Layer 6 & 7)
Verify basic outline compliance:
1. Check the draft's total word count against the contract's min/max limits.
2. Confirm that the required state transitions (characters in locations, item handoffs) are explicitly described in the text.
3. If basic compliance fails, report these structural failures before running style checks.

### Phase 3: Vocabulary & Clue Scanning (Layer 8 Content)
Scan for semantic matches and forbidden terms:
1. Run pattern scanners to locate any occurrences of banned vocabulary (e.g., filter words like "suddenly", "realized").
2. Run semantic search checks to verify the required thematic clues are represented in the prose.
3. Highlight matching line numbers and sentences in the drift database.

### Phase 4: POV & Voice Auditing (Layer 8 Style)
Audit grammatical boundaries:
1. Scan the text for pronouns or tense changes that violate the Point-of-View contract (e.g., detecting "I" or "my" in a Third-Person Limited chapter).
2. Calculate the active-to-passive verb ratio, flagging paragraphs with excessive passive voice constructions.
3. **Ask One Question**: *"In Chapter 4 paragraph 12, Kael is described using passive construction ('the sound was heard by Kael'). We recommend revising this to active voice ('Kael caught the click of the latch') to align with your 70% active verb contract. Shall we apply this revision?"*
4. **Wait for Approval** before locking in changes.

### Phase 5: Redline Audit Reporting
Once the sweep is complete, compile the visual highlighted redline report:
```bash
auteur draft audit-style chapter_04_draft.txt --contract structure/contracts/chapter_04.yaml --output docs/reports/chapter_04_redline.md
```

---

## 3. Highlighted Redline Mismatch Report Schema

The skill outputs a highly readable redline report showing exact file line references, violating text blocks, and direct revision instructions:

```markdown
# Prose Critic Redline Report: Chapter 4

## 1. Chapter Contract Status: **FAILED (3 Violations)**

| Metric | Target | Actual | Status |
|---|---|---|---|
| Word Count | 2200 - 2600 | 2450 | **Passed** |
| Active Verb Ratio | > 70% | 62% | **Failed (Excessive Passive)** |
| POV Constraints | Third-Person Limited (Kael) | Third-Person Limited | **Passed** |

## 2. Highlighted Mismatches & Redlines

### A. Banned Vocabulary Violations
- **Line 45**: `He suddenly realized that the guards had already left the post.`
  - *Mismatch*: Banned filter words `suddenly` and `realized` detected.
  - *Revision Recommendation*:
    ```diff
    - He suddenly realized that the guards had already left the post.
    + The empty benches in the guard post confirmed his suspicion: they were gone.
    ```

### B. Passive Voice Damping
- **Line 112**: `The latch of the iron grate was slowly turned by Kael's fingers, and the hinge was oiled by him to stifle the creak.`
  - *Mismatch*: Passive constructions `was slowly turned by` and `was oiled by` detected (Active ratio: 62%).
  - *Revision Recommendation*:
    ```diff
    - The latch of the iron grate was slowly turned by Kael's fingers, and the hinge was oiled by him to stifle the creak.
    + Kael slowly turned the latch of the iron grate, oiling the hinge to stifle its creak.
    ```

### C. Missing Semantic Clues
- **Contract Requirement**: "Lira tipped off the garrison"
  - *Mismatch*: No semantic match or reference to Lira's tip-off was detected in Kael's discoveries.
  - *Revision Recommendation*: Insert a physical letter or overheard dialogue in Chapter 4 Scene 3 where the scouts reference the tip-off.
```

---

## 4. CLI Style Auditing Commands

The agent uses these commands to run the worker style and pattern auditing engines:

```bash
# Deterministically audit active/passive verbs, vocabulary, and POV pronouns
auteur draft audit-style chapter_04_draft.txt --contract structure/contracts/chapter_04.yaml --output docs/reports/chapter_04_redline.md
```
