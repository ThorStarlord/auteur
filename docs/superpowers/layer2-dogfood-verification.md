# Layer 2 Dogfood Verification Plan

**Status:** REQUIRED BEFORE Layer 3 implementation  
**Goal:** Validate that Layer 2 (Narrative Structure 2A–2D) supports real authorial workflows, not just generated fixtures  
**Duration:** One complete project cycle (seed → revise → validate → repair → iterate)

## Success Criterion

**An author can understand and repair structural problems without reading source code or validator implementation.**

Specifically:
- Diagnostics are actionable (not cryptic)
- Ownership is clear (easy to identify who owns each decision)
- Changes are predictable (moving a chapter doesn't require understanding architecture)
- Validation helps, not obstructs
- Graph answers real questions

## Workflow Loop

```
1. SEED
   auteur netorare blueprint seed ./project story_identity.yaml
   
2. INSPECT
   auteur netorare blueprint status ./project
   → Check completeness, review generated structure
   
3. MANUALLY REVISE
   Edit outlines to match author intent
   → Add details to chapter goals
   → Adjust sequence boundaries
   → Refine character arc beats
   
4. INTRODUCE REALISTIC ERRORS
   Deliberately create inconsistencies (see below)
   
5. VALIDATE
   auteur netorare blueprint validate ./project
   → Record which errors detected
   → Record which errors missed
   → Rate diagnostic clarity
   
6. UNDERSTAND & REPAIR
   Without reading code: understand what went wrong, fix it
   → Rate ease of understanding
   → Record confusion points
   
7. GRAPH
   auteur netorare blueprint graph ./project
   → Can you answer the graph questions? (see below)
   
8. ITERATE
   Repeat cycle 2–7 until structure is stable
```

## Realistic Error Scenarios to Introduce

### A. Ownership Violations

**Move a chapter to another sequence:**
```yaml
# Originally: sequence_01 owns chapters 1–4
# Move: chapter_04 into sequence_02
```
Expected: Validator detects sequence boundary violation.  
Test: Can author understand why it's wrong?

**Duplicate chapter number:**
```yaml
# Two chapters claim to be chapter_05
```
Expected: Reference validator finds conflict.  
Test: Diagnostic clearly identifies both?

**Chapter references non-existent sequence:**
```yaml
chapter_07:
  parent_sequence: sequence_99  # Does not exist
```
Expected: Reference validator catches this.  
Test: Error message names the missing sequence?

### B. Chronological Violations

**Payoff before setup:**
```yaml
chapter_05:
  realizes_arc_beats:
    - reveal_false_alibi    # Payoff

chapter_03:
  realizes_arc_beats:
    - plant_false_alibi     # Setup (happens AFTER payoff)
```
Expected: Chronological validator flags this.  
Test: Diagnostic explains temporal reversal clearly?

**Crisis before escalation:**
```yaml
# Character arc: trust → suspicion → confrontation → revelation
# But chapter 4 (confrontation) comes before chapter 3 (suspicion)
```
Expected: Chronological validator catches arc beat out of order.  
Test: Can author see the progression is reversed?

**Arc climax in wrong book:**
```yaml
# Book 1 ends, Book 2 begins
# Character arc reaches climax in Book 2 Chapter 1
# But all preceding beats are in Book 1
# And Book 1 Outline says arc should resolve by end
```
Expected: Contradiction validator flags outcome mismatch.  
Test: Clear diagnostic about book-level arc resolution?

### C. Contradiction Scenarios

**Emotional state conflict (hard error):**
```yaml
chapter_07:
  outcome: trust_increases

character_arc:
  beat: clara_distrust_deepens  # Trust DECREASES
```
Expected: Contradiction validator catches this.  
Test: Diagnostic explains both states and asks for clarification?

**Intentional dramatic irony (NOT an error):**
```yaml
chapter_07:
  surface_outcome: "Clara believes Daniel is honest"
  
character_arc:
  internal_state: "Clara's suspicion deepens"
  # Both true: she consciously trusts, subconsciously doubts
```
Expected: Validator should NOT flag as error.  
Test: Does validator distinguish hard contradictions from semantic tension?

**Story arc progress mismatch:**
```yaml
mystery_arc:
  phase: "investigation progressing"
  latest_beat: "find_clue_03"
  
chapter_summary:
  outcome: "Clara confirms alibi is valid; mystery resolved"
```
Expected: Contradiction validator flags misalignment.  
Test: Diagnostic clearly explains why outcome contradicts arc phase?

### D. Optionality & Structure Variance

**Minimal structure (Book → Chapters, no Sequences):**
```yaml
book_01:
  chapters:
    - chapter_01
    - chapter_02
    # No sequence_01, sequence_02
```
Expected: Validator accepts; sequences are optional.  
Test: Status command shows structure as valid?

**Standalone book (no Series Outline):**
```yaml
book_01:
  # No parent_series
  chapters: [...]
```
Expected: Validator accepts; series is optional.  
Test: Can author work without series-level structure?

**Single character arc (protagonist only):**
```yaml
# story has 5 characters
# Only clara_trust_arc exists
# No secondary character arcs
```
Expected: Validator accepts; secondary arcs are optional.  
Test: Status shows coverage accurately?

**Unresolved setup (intentional carry-over):**
```yaml
book_01:
  setups:
    - altered_record_signature
    # No payoff in Book 1
    
book_02:
  payoffs:
    - altered_record_discovered  # Resolved in Book 2
```
Expected: Validator accepts cross-book setup→payoff.  
Test: Graph shows cross-book dependency?

### E. Real Authorial Changes

**Chapter split (one chapter becomes two):**
```yaml
# Before: chapter_07 (too long, covers phases 4–5)
# After:
#   chapter_07a (phase 4)
#   chapter_07b (phase 5)
```
Expected: Arc beats need redistributing.  
Test: Can author understand which beats move to 07b?

**Sequence reordering (swap two sequences):**
```yaml
# Before: sequence_01 → sequence_02 → sequence_03
# After:  sequence_01 → sequence_03 → sequence_02
```
Expected: Chronological validator checks arc beat order.  
Test: Validator detects beats now out of sequence order?

**Character arc addition mid-project:**
```yaml
# Discover: need secondary romance arc (not just cuckoldry arc)
# Add: elena_romantic_hope_arc
```
Expected: Validator accepts new arc.  
Test: Can author place beats and references without conflict?

## Diagnostic Quality Checklist

For each validation error, rate the diagnostic:

### Reference Error Example
```
❌ REFERENCE_BROKEN: arc beat not found
✓ REFERENCE_BROKEN: 
  Type: Arc Beat Reference
  Arc: clara_trust_arc
  Missing Beat: distrust_deepens_phase_4
  Location: chapter_07.yaml, line 12
  Suggestion: Add beat to character arc, or reference existing beat
```

### Chronological Error Example
```
❌ CHRONOLOGICAL_VIOLATION: beat order wrong
✓ CHRONOLOGICAL_VIOLATION:
  Type: Setup before Payoff
  Arc: mystery_false_alibi
  Setup: plant_false_alibi (chapter_03)
  Payoff: reveal_false_alibi (chapter_05)
  Issue: Payoff occurs 2 chapters AFTER setup
  Expected: Setup should come after payoff
  Suggestion: Move payoff to chapter 06+, or move setup to chapter 02 or earlier
```

### Contradiction Error Example
```
❌ CONTRADICTION: conflicting states
✓ CONTRADICTION:
  Type: Emotional State Conflict
  Artifact A: Chapter 07 Outline
    Outcome: "Clara's trust increases"
  Artifact B: Character Arc - clara_trust_arc
    Beat: distrust_deepens (trust DECREASES)
  Conflict: Both cannot be true
  Resolution Options:
    1. Revise chapter outcome to show trust decreasing
    2. Revise arc beat definition
    3. If intentional (drama irony), mark as semantic tension
```

Record for each error during dogfood:
- [ ] Diagnostic was clear
- [ ] Author understood problem without code reading
- [ ] Author knew how to fix it
- [ ] Graph or status command reinforced the issue

## Graph Utility Checklist

Can the graph answer these questions?

- [ ] Where does this character arc turn? (visualize beat sequence)
- [ ] Which chapters advance the central mystery? (show mystery arc)
- [ ] Which setups have no payoff? (orphaned setup detection)
- [ ] Which chapter is overloaded? (show chapter with 3+ arc beats)
- [ ] Which books depend on cross-book revelation? (show cross-book links)
- [ ] Where are long gaps in the arc? (show chapter gaps between beats)
- [ ] How do sequences divide the book? (show chapter→sequence→book)
- [ ] What is the complete arc path? (narrative flow visualization)

Record: Which questions the graph answered clearly? Which were confusing?

## Ownership Clarity Checklist

For each structural fact, author should know:

- [ ] Who owns books (Series Outline)
- [ ] Who owns sequences (Book Outline)
- [ ] Who owns chapters (Sequence Outline)
- [ ] Who owns chapter purpose (Chapter Outline)
- [ ] Who owns character transformation (Character Arc)
- [ ] Who owns arc beats (Arc definition)
- [ ] Who owns chapter-to-arc references (Chapter Outline)
- [ ] Which facts are derived (not independently authored)

Record: Any ambiguity about ownership? Cases where two files seemed to own the same decision?

## Workflow Friction Checklist

- [ ] Creating a new chapter is straightforward
- [ ] Moving a chapter between sequences requires one field change
- [ ] Adding an arc beat to an arc is intuitive
- [ ] Referencing an arc beat from a chapter is clear
- [ ] Inspecting what an error means takes <30 seconds
- [ ] Fixing an error doesn't require rebuilding other files
- [ ] Graph output is readable in terminal
- [ ] Status output shows completeness without overwhelming detail

Record: Pain points in manual editing workflow?

## Sample Real Project

Use netorara genre, 2-book structure:

**StoryIdentity:**
```
Title: The Betrayal Cycle
Genre: netorara
Emotional Core: classic humiliation
Books: 2
Tone: exploration of consent, transformation
```

**Seed:** Generate 2 books × 3 sequences each × ~10 chapters per book

**Manual Refinement:**
- Adjust chapter goals to match story themes
- Define Clara's character arc beats
- Define false-alibi discovery story arc

**Error Introduction Sequence:**
1. Move chapter 04 to wrong sequence (test ownership)
2. Create chronological reversal in arc beats (test chronology)
3. Make chapter outcome contradict character arc (test contradiction)
4. Try optional structure (Book → Chapters, no sequences)
5. Add new secondary arc mid-project

**Evaluation:**
- Record time to understand each error
- Rate diagnostic clarity (1–5 scale)
- Rate ease of repair (1–5 scale)
- Identify repeated confusion patterns

## Deliverable

After completing dogfood loop, produce:

**Layer 2 Dogfood Report** with:
- Workflow observations (what felt smooth, what felt awkward)
- Diagnostic quality assessment (clear vs. confusing errors)
- Ownership clarity assessment (any ambiguous decisions)
- Graph utility (which questions it answered well)
- Missing or excessive features (too strict validation, missing checks)
- Recommended pre-Layer 3 improvements

**Expected outcome:** Layer 2 is solid enough for Layer 3 to depend on it confidently.

---

**Last Updated:** 2026-07-12  
**Status:** PLAN READY FOR EXECUTION  
**Prerequisite for:** Layer 3 implementation start
