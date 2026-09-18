# Beginner Workspace desktop information architecture

Status: **amended draft for human review**

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

### Authoritative repository sources

These sources have different authority roles and should not be described as
equivalent.

**Canonical architecture**

- `docs/narrative-architecture.md` — Auteur's canonical architecture
  specification; defines Layers 0–4 as Ontology, Identity, Structure,
  Realization, and Expression.

**Authoritative product and design contracts**

- `docs/design/decision-oriented-tutor.md` — Decision Card, Tutor authority,
  presentation depth, and the advice-is-not-canon boundary.
- `docs/product/creative-writing-tutor.md` — learning-by-doing Tutor loop and
  derived-guidance boundary.

**Current implementation authorities and evidence**

- `src/auteur/identity.py` — current `StoryIdentity` commitment model.
- `src/auteur/story_design_packs/models.py` — current `TutorGuidance`,
  `DecisionCard`, Tutor-depth, and provenance contracts.
- `src/auteur/beginner/guidance.py` — current Beginner guidance and flat
  `OptionImpact` projection.
- `src/auteur/beginner/projections.py` — current combined workspace projection
  for Navigator, Decision Card, reviews, canon, and revision state.
- `src/auteur/beginner/mystery_adapter.py` — current Mystery card/evidence
  inventory and the concrete source of the present shallow option-impact
  copy.

Documentation defines semantic meaning; implementation files show the current
contracts and constraints that the design must adapt.

## Story semantics versus Auteur reasoning

The Inspector must make two different information families visually and
conceptually distinct.

**Story-facing consequences** describe what the author's choice does to the
story:

- **Story Identity** — commitments about what kind of narrative this is,
  including genre, target experience, emotional core, theme, and central
  engine;
- **Structure** — plans for sequencing, causality, escalation, setup/payoff,
  reversals, and whole-story organization;
- **Realization** — later events and state changes the story must embody,
  including character knowledge, relationships, locations, and outcomes;
- **Expression** — how POV, voice, detail, rhythm, dialogue, and other
  language/rendering choices may carry the commitment.

Only relevant semantic areas appear for a given Decision Card. These are
predicted consequences, not mutations of the corresponding artifact.

**Auteur reasoning** explains why Auteur is presenting the advice:

- recommendation and recommendation rationale;
- craft principle and contextual teaching;
- alternatives and trade-offs;
- failure modes, risks, and compensating requirements;
- evidence, source binding, and provenance;
- freshness and authority status.

Recommendation, evidence, and provenance explain Auteur's reasoning. They must
not be presented as if they were story facts or canonical commitments.

## Layout alternatives and decision

The redesign considered three primary desktop arrangements:

| Approach | Author focus | Guidance depth | Desktop use | Mobile mapping | Decision |
| --- | --- | --- | --- | --- | --- |
| Persistent three-panel Inspector | Good, but risks equal visual weight | Excellent | Excellent on wide screens | Maps to stacked/drawer regions | Rejected as the default because the Inspector can become a second hero |
| Two-panel workspace with on-demand Inspector | Excellent | Excellent when opened | Good | Maps cleanly to a drawer | **Chosen** |
| Bottom analysis region | Weaker because analysis competes below the decision | Good | Poor for comparison while deciding | Moderate | Rejected because it separates consequences from the choice and weakens focus |

The chosen behavior is a hybrid two-panel workspace: persistent Navigator on
the left, dominant Decision Card in the center, and a right-side Inspector
that is present as a compact **Explore guidance** affordance but closed by
default. Opening it overlays or docks over the right side without resizing or
displacing the Decision Card. The author can close it without losing the
current choice or scroll position.

When open, the Inspector uses collapsed semantic sections and independent
scrolling. It is not an always-visible three-column wall of content. On narrow
screens it becomes a drawer; the Decision Card remains in place.

## Desktop layout

The default desktop composition is a two-panel workspace with a deliberately
unequal hierarchy: the persistent Navigator and dominant Decision Card are
always present; the Inspector is an on-demand overlay or docked detail
surface:

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
Decision Card is the primary work surface. The Tutor Inspector is not a
second equal column of permanent content. It opens as a right-side overlay or
docked panel without moving, resizing, or reflowing the Decision Card.

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
4. one compact recommendation line labelled as advice, not truth;
5. the available choices;
6. an immediate option-specific consequence preview for the selected choice;
7. working-state feedback and the next action;
8. only active blocking or stale warnings that affect this card.

The question should be the largest text in the card. The center recommendation
is intentionally compact: **Auteur suggests: Logical deduction · Why?** The
full rationale belongs in the Inspector. Choices should be visually
stronger than the recommendation so disagreement feels normal and supported.

Selecting an option still autosaves immediately and does not advance. The
card stays in place, confirms **Working choice saved**, updates the selected
choice's consequence preview, and exposes **Continue →**. On a final answered
card, the primary action becomes **Review Discovery →**, **Review Story
Identity →**, or **Review Structure →**.

The UI must not use a generic Save button or imply that selecting Auteur's
recommendation is required. A valid alternative is a deliberate authorial
choice, not an error.

### Guidance detail and semantic consequence contract

The following content belongs in the on-demand Tutor Inspector:

- **Teach me** — the relevant craft concept in plain language, followed by
  how it operates in this story;
- **Why Auteur recommends this** — the recommendation's reasoning and the
  assumptions it uses;
- **Compare choices** — a compact comparison of relevant dimensions and
  trade-offs;
- **Preview impact** — likely downstream changes, clearly labelled as a
  prediction rather than a mutation;
- **Story evidence** — human-readable source concepts and relevant accepted
  commitments, with technical provenance available only after further
  expansion.

Each meaningful option may expose a relevance-driven subset of these guidance
dimensions:

- reader experience;
- aesthetic or experiential framing;
- narrative promise;
- genre conventions;
- Story Identity consequence;
- Structure consequence;
- Realization consequence;
- Expression consequence;
- what becomes easier;
- what becomes harder;
- failure mode or risk;
- compensating requirement;
- craft principle;
- evidence and provenance.

The conceptual derived contract is:

```text
GuidanceInspectorProjection
  recommendation
  recommendation_rationale
  selected_choice_relationship
  narrative_consequences[]
    semantic_area: Identity | Structure | Realization | Expression
    summary
    implications[]
    what_becomes_easier[]
    what_becomes_harder[]
    risks[]
    compensating_requirements[]
  alternatives[]
  tradeoffs[]
  craft_principles[]
  evidence[]
  authority_status: DERIVED / NOT CANON
```

All fields inside a consequence are optional. Irrelevant semantic areas and
empty sections are omitted. Absence is preferable to boilerplate. The
implementation must not satisfy the shape with copy such as “this emphasizes
a different approach”; each populated field must make a concrete, contextual
claim about the current story and choice.

The current flat `OptionImpact` fields—audience experience, framing,
expected tropes, narrative structure, and trade-offs—are therefore enriched
as a derived projection. This does not change their authority, persistence,
or the canonical Story Identity/Structure artifacts.

Each section should answer a different author question. Do not repeat the
same paragraph under multiple headings. The selected option's most useful
immediate consequence may appear as one compact summary below the choices;
the complete semantic comparison remains on demand.

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

## Conceptual projection contract

No new canonical schema is proposed. The existing combined `WorkspaceProjection`
remains the single source for all desktop surfaces so Navigator, Decision Card,
review, warnings, canonical references, and revision state cannot drift.

The desktop contract is composed into two conceptual projections over that
same source:

```text
DecisionWorkspaceProjection
  current_focus
    stage
    position
    question
    why_this_matters_now
  options[]
    label
    selected
    recommended
  immediate_consequence
  working_state
  active_issue_summary
  next_action
  authority_status

GuidanceInspectorProjection
  recommendation
  recommendation_rationale
  selected_choice_relationship
  narrative_consequences[]
    semantic_area
    summary
    implications[]
    what_becomes_easier[]
    what_becomes_harder[]
    risks[]
    compensating_requirements[]
  alternatives[]
  tradeoffs[]
  craft_principles[]
  evidence[]
  freshness
  authority_status
```

Exact class names and serialization can be chosen during implementation
planning. The conceptual boundary is not optional: the workspace projection
answers what the author must decide now, while the Inspector projection
answers what Auteur knows and explains about that decision.

These remain projections of existing domain/application data. They must not
duplicate validation rules, determine readiness, infer canon, or decide which
authority service to call. If a field cannot be derived from the combined
projection, the application layer—not browser JavaScript—must define it.

## Testing strategy

The implementation plan must establish these tests without asserting brittle
exact prose:

- **Projection tests** verify relevant semantic consequence areas, omission of
  irrelevant areas, distinction between story consequences and Auteur
  reasoning, option-specific content, freshness, and authority status.
- **Browser rendering tests** verify the Decision Card hero, closed/open
  Inspector behavior, disclosure placement, warning severity, recommendation
  subordination, and absence of internal terminology in the beginner view.
- **Boundary tests** verify that JavaScript consumes projection fields and
  sends commands but does not infer semantic state, readiness, canon, or
  authority routing.
- **Regression tests** verify that persistence, concurrency, provenance,
  revision isolation, cancellation, promotion, and staleness semantics remain
  unchanged.
- **Human desktop walkthrough** verifies decision prominence, useful
  ontology-aware guidance, no normal-viewport scroll barrier, understandable
  state vocabulary, and clear next action across the Mystery journey and a
  transfer premise.

Tests should assert semantic categories and required distinctions, not exact
sentences or visual pixel coordinates.

## Migration strategy

Migration is additive and presentation-first:

1. Keep current API commands, persistence, and authority behavior unchanged.
2. Introduce the richer derived projection fields alongside existing fields
   while preserving compatibility for current consumers.
3. Compose the new desktop Decision Workspace and Inspector from the combined
   projection.
4. Remove the old center-column guidance accordions only after equivalent
   Inspector content is present and covered by projection/browser tests.
5. Do not migrate or rewrite persisted session envelopes or canonical story
   artifacts. No persistence migration is required.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Richer guidance becomes verbose | Relevance-driven semantic sections, compact summaries, collapsed Inspector, and independent scrolling |
| UI vocabulary drifts from ontology | Derive semantic-area labels from canonical mappings and review repository sources before implementation |
| Inspector becomes the new visual hero | Keep it closed by default, subordinate typography, bounded width, and no Decision Card resizing |
| JavaScript starts composing story semantics | Require structured application projections and boundary tests; browser only renders and sends commands |
| Semantic categories become boilerplate slots | Make every field optional and omit irrelevant sections; test for concrete option-specific content |
| Existing guidance consumers break | Additive projection fields and compatibility-preserving API rollout |

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
