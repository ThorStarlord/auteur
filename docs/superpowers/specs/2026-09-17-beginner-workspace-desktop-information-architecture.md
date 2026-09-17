# Beginner Workspace desktop information architecture

Status: **draft for human review**

## Purpose

This specification defines the next desktop browser experience for the
Beginner Workspace. It responds to the final independent-gate finding that
the core journey works, but the current desktop information architecture does
not give the current decision enough visual priority and does not teach the
decision deeply enough through Auteur's narrative vocabulary.

This is a presentation and guidance-composition design. It does not change
the Beginner Workspace authority model, the ten-card qualification inventory,
canonical persistence, validation, provenance, revision isolation, or
milestone commands.

## Current diagnosis

The current browser correctly provides a left Navigator, a central Decision
Card, expandable Tutor sections, a read-only Story Map, and milestone review.
The main desktop problem is hierarchy:

- the current question is visually similar in weight to supporting Tutor
  material;
- Recommendation, Why this matters, Narrative principle, Trade-offs and
  impact, and Evidence occupy the primary card even when the author has not
  asked for deeper explanation;
- the guidance sections expose labels, but their relationship to Auteur's
  ontology is not sufficiently explicit;
- the author must mentally combine stage, decision, guidance, working state,
  and canonical state to understand what is happening;
- the current card can feel like a panel of fields rather than one bounded
  narrative decision with a clear consequence surface.

This is not a functional defect. Selection, autosave, Continue, review,
acceptance, and revision commands remain the existing application contract.

## Product principles

The desktop workspace follows these principles:

1. **One place to decide; many places to understand.** The Decision Card is
   the place where an author chooses. Tutor detail, Story Map, Navigator, and
   review evidence explain the surrounding state.
2. **Focus before depth.** The current decision and its immediate consequence
   are visible first. Teaching and provenance are available without competing
   for the same visual priority.
3. **Derived guidance is not canon.** Tutor content is explicitly derived
   advice. A working choice is durable exploration state. An accepted
   milestone is canonical narrative truth.
4. **Narrative ontology before implementation vocabulary.** Beginner-facing
   copy should speak in terms of concepts, commitments, and plans. Internal
   IDs, phase numbers, storage terms, and command names belong only in
   advanced inspection.
5. **Contextual teaching, not a textbook sidebar.** Every explanation should
   connect the craft concept to the current story, current stage, and current
   choice.
6. **Progressive disclosure without concealment.** Supporting depth is
   collapsed by default. Blocking contradictions, materially stale
   assumptions, and revision risk remain visible at the point where they
   affect the author's decision.

## Ontology and authority alignment

The desktop surface is a projection and command client over existing domain
services. It must preserve the canonical architecture:

```text
Ontology concepts and vocabulary
        ↓
derived Tutor guidance for one decision
        ↓
working choice in the Beginner session envelope
        ↓
milestone proposal and domain validation
        ↓
explicit authority-boundary promotion
        ↓
canonical Identity commitment or Structure plan
```

The UI must not imply that the ten beginner cards are a new semantic layer.
They are an orchestration inventory that projects selected domain knowledge
into a manageable learning sequence.

The semantic distinctions shown in the UI are:

| UI state | Meaning | Authority |
| --- | --- | --- |
| Tutor guidance | Recommendation, explanation, alternatives, and predicted consequences | Derived / not canon |
| Working choice | The author's current exploratory selection, autosaved and revisable | Session exploration state |
| Review available | All required decisions have answers and the whole can be evaluated | Not canon |
| Ready to accept | Review validation found no blocking contradiction or materially stale assumption | Proposed milestone |
| Accepted milestone | Explicitly promoted Story Direction, Story Identity, or Whole-Story Structure | Existing domain authority |
| Revision proposal | Isolated exploratory replacement of an accepted milestone | Noncanonical until accepted |

Story Direction is an accepted Discovery commitment and an upstream input to
Identity development. It is not a replacement for `StoryIdentity`. Story
Identity remains the canonical Layer 1 commitment; Structure remains the
canonical planning layer.

## Desktop layout

The default desktop composition is a three-zone workspace with a deliberately
unequal hierarchy:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Workspace identity · current stage · Working / Revision / Canonical state │
├───────────────┬───────────────────────────────────────┬──────────────────┤
│ Story         │ Decision Card                         │ Tutor detail     │
│ Navigator     │                                       │ drawer / rail    │
│ orientation   │  stage eyebrow                       │  closed by        │
│               │  decision question                    │  default         │
│ Discover      │  why now                              │                  │
│ Identity      │  recommendation                       │  Teach me        │
│ Structure     │  choices                              │  Compare options  │
│               │  working-state feedback               │  Preview impact   │
│               │  active warning                       │  Evidence         │
│               │  Continue / Review                    │                  │
├───────────────┴───────────────────────────────────────┴──────────────────┤
│ Review or Story Map: secondary inspection surface, below or on demand     │
└──────────────────────────────────────────────────────────────────────────┘
```

The exact CSS grid may vary, but the proportions must communicate that the
Decision Card is the primary work surface. The Tutor rail is not a second
equal column of permanent content. It is a closed-by-default detail surface
that may open inline or as a right-side drawer without moving the author's
place in the journey.

### Header

The header contains only orientation and durable-state signals:

- workspace name or ID in subdued metadata;
- current stage: Discover, Story Identity, or Structure;
- current lifecycle label: Working, Review available, Ready to accept, or
  Accepted;
- revision indicator when active, including the target milestone;
- a compact link to the read-only Story Map.

Do not show internal enum names, raw stage slugs, session versions, or command
IDs in the beginner header. Those remain available through advanced
inspection.

### Story Navigator

The Navigator remains persistent on desktop and subordinate to the Decision
Card. Each stage row shows:

- human-readable stage name;
- answered count;
- one lifecycle label;
- accepted or not-yet-accepted status;
- a compact stale or at-risk signal only when applicable.

The Navigator must not show future locked stages as active errors. A locked
stage is simply a later stage. Selecting a completed stage is an intentional
orientation action and must not mutate canonical state.

Within the current stage, the Navigator may show card names as a compact
outline. The current card is prominent; completed cards are visually quiet;
future cards remain visible but do not compete with the current question.

### Decision Card

The Decision Card owns the desktop visual hierarchy. Its default content is:

1. stage and decision position;
2. one plain-language question;
3. one short **Why this matters now** paragraph;
4. one recommendation block labelled as advice, not truth;
5. the available choices;
6. an immediate option-specific consequence preview for the selected choice;
7. working-state feedback and the next action;
8. only active blocking or stale warnings that affect this card.

The question should be the largest text in the card. The recommendation
should support the question, not precede it. Choices should be visually
stronger than the recommendation so disagreement feels normal and supported.

Selecting an option still autosaves immediately and does not advance. The
card stays in place, confirms **Working choice saved**, updates the selected
choice's consequence preview, and exposes **Continue →**. On a final answered
card, the primary action becomes **Review Discovery →**, **Review Story
Identity →**, or **Review Structure →**.

The UI must not use a generic Save button or imply that selecting Auteur's
recommendation is required. A valid alternative is a deliberate authorial
choice, not an error.

### Guidance detail

The following content belongs in the on-demand Tutor detail surface:

- **Teach me** — the relevant craft concept in plain language, followed by
  how it operates in this story;
- **Why Auteur recommends this** — the recommendation's reasoning and the
  assumptions it uses;
- **Compare choices** — a compact comparison of audience experience,
  framing, conventions, structural effect, and trade-offs;
- **Preview impact** — likely downstream changes, clearly labelled as a
  prediction rather than a mutation;
- **Story evidence** — human-readable source concepts and relevant accepted
  commitments, with technical provenance available only after further
  expansion.

Each section should answer a different author question. Do not repeat the
same paragraph under multiple headings. The selected option's impact may be
visible as one compact summary below the choices because it answers the
immediate question, while the complete comparison remains on demand.

The guidance contract should continue to provide stable fields for decision,
orientation, craft concept, recommendation, rationale, alternatives,
trade-offs, consequences, evidence, and authority status. This design changes
composition and presentation, not the meaning or authority of those fields.

### Warnings and tensions

Warnings are classified before presentation:

- **Blocking contradiction** — red, concise, card-local summary with an
  explanation affordance;
- **Materially stale assumption** — amber, concise statement naming the
  assumption that needs reassessment;
- **Authorial tension** — neutral or muted note that invites interpretation;
- **Guidance divergence** — neutral comparison language such as “Different
  from Auteur's recommendation,” never “conflict” or “thread.”

Card-local guidance must not be repeated as a global warning on every later
card. The author should see the issue where it matters and find the full
explanation in the detail surface or milestone review.

### Review and Story Map

Review is a whole-first surface. Its primary order is:

1. synthesized proposed milestone;
2. why the proposal coheres with upstream commitments;
3. blocking issues and stale assumptions;
4. acknowledged authorial tensions;
5. impact if accepted;
6. explicit milestone action;
7. expandable supporting decisions.

The review must distinguish **Review available** from **Ready to accept**.
Locked future reviews are not rendered as blocked review panels. The Story Map
is read-only and shows current canonical milestones once each; historical
revisions remain in provenance, not in the current-canon list.

After Whole-Story Structure is accepted, the workspace shows a completion
summary such as **Story foundation accepted** and names the three accepted
milestones. It does not leave a stale review CTA as the apparent next step.

## Interaction states

The desktop design preserves this state transition model:

```text
Working
  ├─ answer card → autosaved working choice
  ├─ inspect guidance → remain Working
  ├─ Continue → next card or Review available
  └─ revise choice → replace current working projection

Review available
  ├─ open review → validate whole milestone
  ├─ revise supporting decision → Working / recomputed review
  └─ valid review → Ready to accept

Ready to accept
  └─ explicit milestone action → Canonical

Canonical
  └─ Open revision → isolated revision workspace
```

An active revision adds an overlay to the same presentation:

- the header identifies the target milestone and says **Exploring revision**;
- choices are labelled exploratory and remain noncanonical;
- downstream artifacts say **At risk if this revision is accepted** only after
  actual divergence;
- Cancel Revision discards the overlay;
- acceptance delegates to the existing authority boundary and then shows the
  resulting downstream stale state.

## Data and API implications

No new canonical schema is proposed. The existing combined workspace
projection remains the source for all desktop surfaces so Navigator, Decision
Card, review, warnings, canonical references, and revision state cannot drift.

The browser may need presentation-only view-model additions, such as:

- a compact `current_focus` summary;
- a structured `guidance_sections` ordering;
- explicit beginner labels for lifecycle and ontology concepts;
- an `issue_presentation` severity/category;
- a selected-option impact summary;
- and a `next_action` label distinct from command identity.

These are projections of existing domain/application data. They must not
duplicate validation rules, determine readiness, infer canon, or decide which
authority service to call. If a projection field cannot be derived from the
combined application projection, the application layer—not browser
JavaScript—must define it.

## Accessibility and responsive behavior

- The question is the first meaningful heading inside the main region.
- Keyboard focus follows the current card and does not jump into hidden Tutor
  detail when a choice is selected.
- Radio choices expose selected, recommended, and exploratory state without
  relying on color alone.
- Warnings use role and text appropriate to severity; authorial tension must
  not be announced as an alert.
- On narrow screens, the Navigator and Tutor detail become drawers. The header
  keeps current-stage orientation visible and the Decision Card remains the
  primary surface.
- The Story Map remains read-only at every size.

## Acceptance criteria for implementation

The implementation phase should be considered successful only when:

1. A new author can identify the current question before reading any Tutor
   detail.
2. Recommendation, explanation, alternatives, and consequences are clearly
   distinct content types.
3. The default desktop card is compact enough that choices and Continue are
   visible without scrolling in the normal viewport.
4. The selected option's consequence is specific to that option and clearly
   derived/predictive.
5. A valid non-recommended choice reads as supported authorial agency, not a
   blocking error.
6. Working, review available, ready to accept, accepted, and revision states
   are distinguishable without knowing internal implementation terms.
7. No global guidance divergence leaks onto unrelated cards.
8. Review presents the synthesized whole before supporting evidence.
9. The final accepted state has one clear completion summary and no obsolete
   primary review CTA.
10. The existing automated authority, persistence, concurrency, revision,
    and promotion tests remain unchanged in meaning and continue to pass.

## Scope boundary

This spec does not authorize implementation yet. The next phase begins only
after human review of this document and should produce a separate TDD
implementation plan. Until then:

- no browser or application code changes;
- no new workspaces or qualification runs;
- no changes to canonical artifacts;
- no PR merge or ready-for-review transition;
- no L3 or release qualification.

