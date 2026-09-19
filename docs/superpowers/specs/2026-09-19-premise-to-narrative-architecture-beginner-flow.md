# Premise-to-Narrative-Architecture Beginner Flow

Status: **draft for user review**

Date: 2026-09-19

## Related authorities

This specification must remain consistent with:

- `docs/narrative-architecture.md` — canonical semantic layers and authority placement;
- `docs/opinionated-narrative-engine.md` — creative-beginner product promise, opinionated recommendation, and explicit ratification;
- `docs/research/product-design-research.md` — premise-to-Identity onboarding, progressive disclosure, and architecture-value research;
- the Working Composition / Mapping Planner contracts implemented in draft PR #237, which remain noncanonical substrate rather than the desired final beginner ordering.

Where this specification changes the current Beginner Workspace journey, it changes **product workflow and projection**, not the canonical five-layer semantic architecture.

## Purpose

This specification redesigns the Beginner Workspace entry flow around a product finding from direct human use:

> Auteur currently asks the author to configure narrative components before it has first shown a coherent interpretation of the story already implied by the premise.

The corrected product order is:

```text
raw premise
  ↓
Narrative Architecture Analysis
  ↓
Story Navigator shows "what Auteur sees"
  ↓
optional architecture refinement / composition
  ↓
Discovery
  ↓
Story Identity
  ↓
Structure
```

The goal is not to create another canonical semantic layer. The goal is to give the creative beginner an explicit, inspectable, derived interpretation of the premise before asking them to make story-development decisions.

This specification builds on the existing canonical architecture:

```text
Ontology → Identity → Structure → Realization → Expression
```

and preserves the central authority rule:

> **Advice, inference, analysis, and working composition are not authority.**

Only explicit existing acceptance boundaries can create canonical Story Identity or Structure.

---

## Human finding that triggered the redesign

During qualification of the Working Composition candidate, the Beginner Workspace showed:

- a Mystery Decision Card;
- a proposed Mystery primary engine;
- a proposed superhero world dimension;
- a proposed relationship-betrayal dimension;
- controls such as "Use this lens";
- internal category labels such as `PRIMARY_ENGINE`, `SETTING_WORLD`, and `RELATIONSHIP_THEMATIC`.

The user could not tell what the new section was for.

The deeper problem was not only terminology.

The interface implicitly asked the author to reconstruct the story's architecture manually:

```text
premise
  ↓
Auteur detects fragments
  ↓
author confirms/assembles fragments
  ↓
Auteur can reason with them
```

The desired product relationship is the reverse:

```text
premise
  ↓
Auteur interprets the premise as a coherent narrative architecture
  ↓
author sees and understands that interpretation
  ↓
author optionally corrects/refines/composes it
  ↓
Auteur uses the resulting working architecture for Discovery and later guidance
```

This is a workflow and product-architecture correction, not merely a copy or labeling change.

---

## Product thesis

For a creative beginner, the first question after entering a premise should be:

> **"What story do I currently have?"**

Auteur should answer that question before asking:

> "What should you choose next?"

The Beginner Workspace therefore separates four activities that were previously partially collapsed:

1. **Interpretation** — What narrative architecture is already implied by the premise?
2. **Discovery** — What coherent story directions could that architecture become?
3. **Identity** — Which commitments define the story the author actually chooses?
4. **Structure** — How should that accepted story be planned and organized?

The author may refine the inferred architecture, but refinement is optional by default.

The author should not need to understand Auteur's internal ontology merely to obtain intelligent guidance.

---

## Approved default interpretation policy

Auteur presents **one best coherent interpretation of the premise by default**.

It does **not** show two or three competing whole-premise architectures as the normal beginner experience.

Alternatives are surfaced only when a **specific component is materially ambiguous**.

Examples:

```text
Genre constellation:
  Mystery — strong
  Superhero fiction — strong

Aesthetic framing:
  Best fit: erotic psychological melodrama
  Also plausible: campy erotic melodrama
  Why ambiguous: the premise supports betrayal spectacle but does not yet
  specify whether the emotional treatment should be psychologically serious
  or theatrically heightened.
```

This preserves the product posture:

```text
understanding first
choice second
```

rather than forcing a beginner to compare multiple large interpretations before they can orient themselves.

---

## Terminology

### Narrative Architecture Analysis

A derived interpretation of the story implied by the current raw premise and any explicit author context.

It is:

- noncanonical;
- inspectable;
- revisable;
- evidence-linked;
- provenance-bearing;
- allowed to contain uncertainty;
- allowed to use model reasoning;
- never silently promoted into Story Identity or Structure.

### Narrative architecture

In this product-facing context, "narrative architecture" means the explicit model Auteur uses to understand the story across useful narrative dimensions.

It does **not** mean a sixth semantic layer.

The analysis may describe material that, if later accepted, would belong to different canonical layers or remain reusable craft/guidance knowledge.

### Extraction versus inference

Some premise information can be directly extracted:

- "superhero";
- "investigates";
- "wife";
- "betrayal";
- "secret identity".

Other information is interpretive:

- jealous uncertainty;
- erotic melodrama;
- dramatic irony;
- a rival narrative function;
- a revelation architecture;
- a power-shift relationship dynamic.

The product may use the friendly language:

> **"Here is what Auteur sees in your story."**

Internally the operation should be treated as **premise interpretation / narrative architecture inference**, not as a claim that every element was literally stated in the premise.

---

## Analysis facets

The first implementation should support the following author-facing facets.

### 1. Genre constellation

The set of materially relevant genres/subgenres or genre-like traditions implied by the premise.

Examples:

- Mystery;
- superhero fiction;
- erotic psychological drama;
- relationship melodrama;
- romance;
- horror;
- thriller.

A genre constellation is not automatically a single canonical `story_type.genre`.

It is a derived interpretation used to understand the story before Identity acceptance.

The analysis must distinguish:

- strongest/primary genre engine where inferable;
- major supporting genres;
- minor flavor/background genres;
- ambiguous alternatives.

### 2. Narrative engines and structural tendencies

The causal or experiential machinery likely to drive the story.

Examples:

- investigation → clue → reinterpretation → revelation;
- escalating suspicion;
- relationship trust erosion;
- forbidden desire and resistance;
- public/private identity pressure;
- corruption/escalation;
- rivalry → displacement → confrontation.

These are **architectural tendencies**, not accepted Structure plans.

They must not be represented as if Act structure, chapter order, or exact beats already exist.

### 3. Character narrative functions

The roles characters appear likely to perform in the narrative machinery.

Examples:

- protagonist / investigator;
- intimate partner / source of uncertainty;
- rival / disruptive third party;
- confidant;
- witness;
- clue carrier;
- public antagonist;
- false suspect;
- temptation figure.

These functions are derived interpretations, not immutable character identities.

One character may serve multiple functions.

### 4. Aesthetic framing

How the premise appears to invite the material to be framed or experienced.

Examples:

- campy melodrama;
- erotic tension;
- psychological intimacy;
- dread;
- noir fatalism;
- heroic spectacle;
- comic exaggeration;
- tragic seriousness;
- unsettling voyeuristic uncertainty.

Aesthetic framing must remain distinct from prose-level Expression.

The analysis describes the likely high-level treatment; exact voice, diction, sentence form, and prose rendering remain Expression concerns.

### 5. Trope families

Recognizable recurring narrative patterns implied by the premise.

Examples:

- secret identity;
- suspicious behavior;
- forbidden intimacy;
- hidden relationship;
- rival intrusion;
- dramatic irony;
- double life;
- evidence of betrayal;
- corruption;
- revelation/confrontation.

Trope inference is guidance context, not canon.

Auteur should avoid treating trope labels as obligations unless the author later chooses commitments that require them.

### 6. Emotional and relationship dynamics

Important emotional or relational machinery implied by the premise.

Examples:

- jealousy;
- mistrust;
- longing;
- humiliation;
- intimacy versus autonomy;
- control versus surrender;
- erosion of trust;
- emotional dependency;
- betrayal;
- power renegotiation.

This facet is especially important for stories whose emotional architecture cannot be represented adequately by plot genre alone.

### 7. Setting and world logic

Narratively meaningful world features that affect how the story works.

Examples:

- superhero public identity;
- powers and asymmetry;
- institutional investigation;
- celebrity/reputation;
- magical social rules;
- technological constraints;
- class/faction structures.

World context should be included only when it materially changes narrative reasoning.

### 8. Themes and motifs, when supported

Auteur may surface likely thematic tensions or recurring motifs only when they are meaningfully supported by the premise.

Examples:

- public persona versus private truth;
- desire versus self-image;
- trust versus certainty;
- power and vulnerability.

Weakly supported themes should be presented as uncertain possibilities, not asserted as facts.

---

## Analysis component contract

Each surfaced component should preserve enough information to explain itself.

Conceptually:

```text
ArchitectureComponent
  component_id
  facet
  author_label
  normalized_concept?
  role / emphasis
  evidence[]
  rationale
  confidence / certainty band
  provenance[]
  alternatives[]
  lifecycle
  author_adjustment?
```

The exact schema may reuse existing contracts where possible.

The design requirement is semantic, not a mandate to create a new production model for every field above.

### Evidence

Evidence should identify why Auteur inferred the component.

For premise-derived analysis this may include:

- exact premise phrases;
- normalized semantic matches;
- genre-pack/profile evidence;
- Story Design Pack evidence;
- prior accepted upstream state when applicable.

### Certainty

Beginner UI should prefer human-readable certainty:

- **clear**;
- **likely**;
- **uncertain**.

The implementation may retain more precise internal confidence if an existing reasoning contract requires it.

Confidence must not be presented as objective truth.

### Alternatives

Alternatives should be component-scoped.

An alternative is shown when choosing between interpretations would materially change later guidance.

Do not generate alternatives merely to look sophisticated.

---

## Story Navigator responsibility

The Story Navigator is not primarily a wizard progress indicator.

Its core product responsibility is:

> **Help the author understand the current story model and where they are in developing it.**

The Navigator should answer:

- What kind of story does Auteur currently think this is?
- What major narrative machinery is present?
- What is inferred versus author-confirmed versus canonical?
- What direction has been chosen?
- What has been accepted?
- What remains unresolved?
- What stage is the author working in now?
- What is the next useful decision?

The workflow stages remain useful, but they become one part of a larger story model.

### Target Navigator shape

Before any accepted milestones:

```text
STORY NAVIGATOR

Your story
├── Narrative architecture
│   ├── Genre constellation
│   ├── Narrative engines
│   ├── Character functions
│   ├── Aesthetic framing
│   ├── Tropes
│   ├── Emotional / relationship dynamics
│   └── World context
│
├── Discovery
│   └── Direction not chosen yet
│
├── Story Identity
│   └── Not accepted yet
│
├── Structure
│   └── Not planned yet
│
├── Realization
│   └── Later
│
└── Expression
    └── Later
```

The current `Discover 1/3 → Story Identity 0/4 → Structure 0/3` progress sequence may remain as secondary stage progress, but it must no longer define the Navigator's entire meaning.

---

## Default first screen

After entering a premise, the beginner should first see a concise summary such as:

```text
HERE IS WHAT AUTEUR SEES

This looks primarily like a relationship-centered superhero mystery.

Genre constellation
  Mystery
  Superhero fiction
  Erotic / relationship melodrama

Main narrative machinery
  Investigation and accumulating evidence
  Erosion of relationship trust
  Public/private identity pressure

Character functions
  Protagonist / investigator
  Intimate partner / source of uncertainty
  Rival or disruptive third party

Aesthetic framing
  Erotic tension
  Heightened melodrama
  Suspicious intimacy

Common trope families
  Secret identity
  Suspicious behavior
  Rival intrusion
  Hidden intimacy
  Revelation / confrontation

[Looks right — continue]
[Refine this interpretation]
[Why does Auteur see this?]
```

The author should **not** be forced to inspect or approve every item before continuing.

The architecture is working interpretation, not canon.

---

## Working Composition: corrected role

The Working Composition and Mapping Planner machinery is retained, but its product role changes.

### Previous placement

```text
premise
  ↓
proposed dimensions
  ↓
author must activate dimensions
  ↓
composed guidance
```

### Corrected placement

```text
premise
  ↓
Narrative Architecture Analysis
  ↓
best-fit architecture becomes active working interpretation
  ↓
optional author refinement
  ↓
Working Composition records active/refined guidance dimensions
  ↓
Discovery / Identity guidance consumes the composition
```

Working Composition therefore becomes:

> **the editable working representation of the architectural dimensions that materially influence guidance and promotion planning.**

It should not be required to contain every displayed architecture component.

For example:

- a trope may remain analysis/provenance context without becoming a mapping dimension;
- a character narrative function may inform Discovery without mapping directly to Story Identity;
- a confirmed primary engine may participate in canonical mapping later;
- aesthetic framing may remain guidance-only if current Story Identity cannot represent it.

### Default activation

Components inferred by the current validated analysis may participate in working guidance by default.

The author does **not** need to click "Use this lens" for every component before Auteur can reason with the premise.

The interface must make clear:

```text
inferred working interpretation ≠ canonical commitment
```

### Activation versus author confirmation

Guidance activation, author confirmation, and canonical authority are separate concepts.

An inferred component may be **active for working guidance by default** even when the author has not explicitly confirmed it. This is what allows Auteur to reason from the premise immediately instead of requiring the author to activate every detected dimension.

The system must preserve at least these distinctions:

```text
inferred component
  ├─ active/suppressed for working guidance
  ├─ unreviewed/author-confirmed/author-modified as working interpretation
  └─ noncanonical until an existing Story Identity or Structure authority boundary accepts a mapped commitment
```

Do not overload one lifecycle/status field to mean all three things.

The exact schema may reuse existing fields or introduce a narrow separate activation/review axis, but it must support these invariants:

- inferred does not mean author-confirmed;
- active for guidance does not mean canonical;
- author confirmation of an interpretation does not itself promote canon;
- suppressing a component removes it from working guidance without rewriting accepted canon;
- canonical acceptance remains a separate later action.

### Refinement

"Refine this interpretation" may allow the author to:

- strengthen emphasis;
- reduce emphasis;
- remove a component;
- replace an ambiguous component;
- add a missing component;
- rename an author-facing component;
- add rationale in the author's own words.

Refinement changes working interpretation only.

It never silently creates canonical Identity or Structure.

---

## Relationship between analysis and existing WorkingComposition categories

Current WorkingComposition categories include:

- `PRIMARY_ENGINE`;
- `GENRE_SUBGENRE`;
- `EMOTIONAL_AESTHETIC`;
- `RELATIONSHIP_THEMATIC`;
- `SETTING_WORLD`.

These remain useful for **guidance composition and mapping**, but they are not sufficient to represent the entire author-facing architecture analysis.

Do not force every extracted facet into those five categories.

Instead:

```text
Narrative Architecture Analysis
  broader derived interpretation
        ↓
material guidance dimensions selected/projected
        ↓
WorkingComposition
        ↓
Mapping Planner
```

This keeps the Mapping Planner bounded and avoids turning it into a universal story ontology.

---

## Discovery: corrected purpose

Discovery answers:

> **"Given what this premise already contains, what coherent story should it become?"**

Discovery does not primarily extract the architecture already present in the premise.

It searches the story-design space opened by that architecture.

### Discovery input

Discovery receives:

- raw premise;
- current Narrative Architecture Analysis;
- author refinements;
- active working composition;
- relevant genre/design knowledge;
- accepted upstream state when revising.

### Discovery output

Opinionated mode should produce:

- one strongest recommended story direction;
- why it best fits the current premise and architecture;
- meaningful rejected alternatives;
- trade-offs;
- unresolved choices that materially affect direction.

Example:

```text
Recommended direction:
Investigative betrayal mystery

Primary engine:
Investigation of intimate betrayal

Supporting architecture:
Superhero secret/public identity
Erotic relationship melodrama

Why this direction:
The premise's strongest causal motion comes from suspicion becoming evidence,
while the superhero context raises the cost of discovery and the relationship
framing makes every clue emotionally consequential.
```

Alternatives might include:

- psychological relationship tragedy;
- campy erotic superhero melodrama.

Discovery alternatives are **story directions**, not competing premise analyses.

---

## Current Discovery cards must be reclassified

The existing fixed Mystery qualification inventory should not be treated as sacred product architecture.

Every current card must be audited against this rule:

### Belongs before Discovery when it asks:

> "What is already present in this premise?"

Examples may include:

- genre/lens identification;
- high-level aesthetic mode;
- obvious relationship dynamic;
- obvious world context.

These should become analysis/refinement rather than required Discovery choices.

### Belongs in Discovery when it asks:

> "Which coherent direction should this premise take?"

Examples:

- which engine should dominate;
- what form of uncertainty drives the story;
- which major payoff/revelation shape is strongest;
- which of two plausible architectures should become the chosen direction.

### Belongs in Story Identity when it asks:

> "What commitment should define the chosen story?"

Examples:

- target reader experience;
- accepted genre/subgenre promise;
- emotional core;
- central engine;
- theme;
- broad ending contract.

### Belongs in Structure when it asks:

> "How should the accepted story unfold?"

Examples:

- escalation pattern;
- revelation placement;
- investigation progression;
- act/thread organization;
- setup/payoff plan;
- causal ordering.

The redesign may reduce, replace, or dynamically select cards.

The product must not preserve a ten-card sequence merely because it already exists.

### Adaptive decision inventory

The beginner flow should not treat fixed card counts such as `Discover 3 / Identity 4 / Structure 3` as product requirements.

A Decision Card exists because there is a material unresolved author decision, not because a stage has a predetermined quota.

Therefore:

- if the architecture analysis already establishes a premise trait strongly enough for current guidance, do not ask the author to restate it;
- if Discovery has one clear recommended direction and only one material ambiguity, ask about that ambiguity rather than filling a three-card quota;
- if the selected direction already determines most Story Identity fields, present a coherent candidate Identity and ask only about genuinely unresolved commitments;
- if Structure has no reason to ask a particular planning question yet, defer it rather than manufacturing a choice;
- dynamic selection must remain bounded, explainable, and testable.

This does not require free-form unbounded questioning. The application may still select from curated Decision Card families and deterministic eligibility rules.

---

## Story Identity: corrected purpose

Story Identity answers:

> **"What are we now committing this story to?"**

It converts the selected Discovery direction into explicit Layer 1 commitments.

Identity review should expose:

- genre/subgenre commitments;
- target reader experience;
- emotional core;
- theme where applicable;
- core narrative engine;
- central conflict;
- protagonist want/resistance/stakes/change where required by current contract;
- broad resolution/ending contract where supported;
- author overrides;
- important architectural material that remains guidance-only because the current canonical vocabulary cannot represent it.

The author may revise these commitments before acceptance.

Only explicit acceptance mutates canonical Story Identity.

### Identity should not force loss

If the derived architecture contains meaningful material that the current Story Identity cannot represent, the acceptance preview must visibly distinguish:

```text
becomes canonical
continues as downstream guidance
preserved as provenance
still unresolved
```

This preserves the prior rule:

> **Promotion is lossy only when the author can see the loss.**

---

## Structure: corrected purpose

Structure answers:

> **"Given the accepted Story Identity, how should the story unfold?"**

Structure consumes accepted Identity plus relevant working architecture and builds plans for:

- causal progression;
- threads and arcs;
- escalation;
- reversals;
- setup/payoff;
- revelation timing;
- chapter/beat planning where appropriate;
- thematic progression;
- structural use of character functions;
- structural use of emotional/relationship dynamics.

Structure must not be used to decide basic genre identity that should already have been resolved upstream.

Derived architecture may continue to inform Structure, but accepted Identity is authoritative.

---

## Relationship to canonical semantic layers

The corrected Beginner flow is a product workflow over the canonical architecture, not a replacement for it.

```text
RAW PREMISE
  ↓
Narrative Architecture Analysis
  DERIVED interpretation across useful concepts
  ↓
Discovery
  DERIVED story-direction search
  ↓
Story Identity
  Layer 1 candidate → explicit acceptance → canon
  ↓
Structure
  Layer 2 candidate/plan → explicit acceptance → canon
  ↓
Realization
  Layer 3
  ↓
Expression
  Layer 4
```

Narrative Architecture Analysis may refer to concepts whose later canonical homes differ.

It must never be called "Layer 0.5", "Pre-Identity Layer", or another new semantic layer.

---

## Analysis engine and authority

Rich premise interpretation is allowed to use model reasoning.

This is necessary for subtle inferences such as:

- aesthetic framing;
- trope families;
- character narrative functions;
- emotional relationship dynamics;
- ambiguous genre combinations.

However:

```text
model inference
  ≠ canon
  ≠ mapping authority
  ≠ validation authority
```

### Recommended responsibility split

```text
Provider/model reasoning
  → proposes architecture analysis

Deterministic application layer
  → normalizes IDs
  → binds evidence/provenance
  → validates schema
  → reconciles author refinements
  → manages currentness/staleness

Working Composition
  → projects material active dimensions

Mapping Planner
  → proposes existing canonical mappings

Existing domain authority
  → validates and promotes accepted Identity/Structure
```

The Mapping Planner remains deterministic with respect to canonical destinations.

The model may propose an interpretation; it does not invent canonical fields or mutate authority.

---

## Provider availability and fallback

The product should distinguish:

### Rich analysis available

A configured reasoning provider can produce the full Narrative Architecture Analysis.

### Rich analysis unavailable

Auteur may still:

- reflect explicit premise terms;
- use deterministic pack/profile matches;
- show known genre/design evidence;
- explain that deeper narrative interpretation is unavailable in the current environment.

The fallback must not fabricate rich analysis.

A provider failure must not silently degrade into confident unsupported interpretation.

---

## Provenance and currentness

Every analysis snapshot must be bound to the premise and relevant source knowledge used to produce it.

At minimum preserve:

- premise fingerprint;
- analyzer/version identity;
- model/provider identity where policy permits;
- genre/design-pack identifiers, versions, and hashes used;
- generation time/run identity if existing reasoning contracts require it;
- author refinements;
- upstream accepted milestone references when revising.

If the premise or material source knowledge changes, analysis becomes stale.

Stale analysis may remain inspectable but should not be silently presented as current guidance context.

---

## Premise editing

Before Story Identity acceptance, editing the premise should:

1. preserve the previous analysis for comparison/history where current session contracts permit;
2. mark the previous analysis stale;
3. request/recompute a new analysis;
4. attempt to preserve explicit author refinements only when their target meaning still exists;
5. surface conflicts rather than silently rebasing incompatible author adjustments.

After Story Identity acceptance, premise edits should not silently rewrite accepted Identity.

They become revision input.

---

## Author corrections and learning

A correction should teach Auteur about this story without becoming canon automatically.

Examples:

```text
Auteur inferred:
  psychological erotic drama

Author correction:
  make the tone campy melodrama instead

Result:
  working architecture updates
  Discovery/guidance recomputes
  Story Identity remains unchanged until later acceptance
```

Author corrections should preserve:

- what Auteur originally inferred;
- what the author changed;
- the author's rationale when supplied;
- which downstream recommendations changed.

---

## Beginner-facing vocabulary

Do not expose internal enum labels by default.

Examples:

| Internal | Beginner-facing |
| --- | --- |
| `PRIMARY_ENGINE` | Main story engine |
| `GENRE_SUBGENRE` | Genre / story tradition |
| `EMOTIONAL_AESTHETIC` | Emotional & aesthetic framing |
| `RELATIONSHIP_THEMATIC` | Relationship & thematic dynamic |
| `SETTING_WORLD` | World & setting logic |
| `PROPOSED` | Inferred by Auteur |
| `CONFIRMED` | Adjusted/confirmed for this working interpretation |
| `REJECTED` | Removed from working interpretation |

Advanced inspection may expose exact internal types.

The beginner-facing surface should lead with ordinary language.

---

## Story Map, Global Map, and Navigator

The Narrative Architecture Analysis is compatible with Auteur's existing long-horizon thesis:

```text
Explicit Narrative Architecture
  → Global Map
  → Decision Map
  → Focus
```

For a new premise, the initial Story Navigator can be treated as the beginner-facing orientation projection of a derived architecture before much accepted history exists.

Do not create a second canonical map database.

Reuse existing projection/orientation concepts where possible.

The first implementation does not need to solve the complete long-horizon Global Map problem.

### Story Navigator versus Story Map

The Navigator and Story Map must not become competing representations of the same story.

Use one underlying derived architecture projection with two presentation depths:

```text
Story Navigator
  concise orientation + status + next action

Story Map
  expanded read-only inspection of the same current architecture,
  evidence, relationships, ambiguity, and accepted milestones
```

The Story Map may show more detail, but it must not own a second persistence model or silently diverge from the Navigator.

---

## Suggested beginner interaction sequence

### Step 1 — Enter premise

The author gives a raw premise, character impulse, or desired reader experience.

### Step 2 — Auteur interprets

Show a short progress state:

> "Auteur is identifying the story's genre signals, narrative machinery, character functions, emotional dynamics, and framing."

### Step 3 — Show architecture summary

Present one coherent best-fit interpretation.

Default actions:

- **Looks right — continue**
- **Refine this interpretation**
- **Why does Auteur see this?**

"Looks right" is not canonical acceptance.

It simply continues using the analysis as working context.

### Step 4 — Optional refinement

Only if requested, expose component controls.

The author can change emphasis, remove, replace, or add material.

### Step 5 — Discovery

Show one recommended story direction plus meaningful alternatives.

Discovery guidance should visibly use multiple relevant architecture facets.

### Step 6 — Story Identity

Translate the chosen direction into explicit commitments.

Show exactly what would become canonical and what remains guidance/provenance.

### Step 7 — Explicit Identity acceptance

Existing authority boundary.

### Step 8 — Structure

Develop the accepted story into plans.

### Step 9 — Explicit Structure acceptance

Existing authority boundary.

---

## Differential guidance requirement

The redesign is successful only if architecture materially changes reasoning.

For the approved hybrid qualification case:

```text
Primary:
  Mystery investigation

Supporting:
  Superhero public identity

Relationship/aesthetic:
  Relationship betrayal
  Erotic tension / betrayal framing
```

the same Mystery decision must not receive effectively generic Mystery-only guidance.

A valid composed explanation should connect relevant dimensions, for example:

```text
A detective-procedural approach strengthens the investigation engine, but in
this story the evidence should also pressure the protagonist's private/public
superhero identity and change the meaning of intimacy and trust. A clue that
would be merely informational in a generic mystery may here simultaneously
threaten reputation, romantic security, and the protagonist's interpretation
of the partner's behavior.
```

The exact recommendation may differ.

The acceptance criterion is that supporting architecture produces observable, provenance-traceable reasoning differences while the primary engine remains legible.

---

## Approved sanitized qualification case

The human qualification case remains:

```text
Primary narrative engine:
  Mystery investigation

Supporting world:
  Superhero identity / public-hero context

Supporting relationship/aesthetic:
  Relationship betrayal with erotic-betrayal framing
```

The revised qualification must begin at premise interpretation rather than manually activating the three dimensions.

Human evaluation should answer:

1. Does Auteur's initial architecture summary accurately reflect the premise?
2. Is the distinction between "what Auteur sees" and "what the author has accepted" clear?
3. Does the author understand that refinement is optional?
4. Are genre, narrative machinery, character functions, aesthetic framing, tropes, relationship dynamics, and world context understandable?
5. Are ambiguous components surfaced without overwhelming the author?
6. Does Discovery feel like exploration of what the story could become rather than extraction of what is already present?
7. Does Story Identity feel like commitment rather than another brainstorming pass?
8. Does Structure feel downstream of accepted Identity?
9. Does composed guidance materially use the superhero and relationship/erotic-betrayal dimensions?
10. Can the author explain the resulting story direction and the next useful decision?

---

## Current PR #237 disposition

PR #237 remains:

- open;
- draft;
- unmerged.

Its human qualification is **stopped** because the test exposed a product-ordering defect.

Do not merge it in its current product presentation.

The implementation is not discarded.

The following work remains valuable substrate:

- WorkingComposition persistence;
- dimension lifecycle;
- Mapping Planner;
- promotion preview;
- canonical authority integration;
- provenance;
- revision isolation;
- crash recovery;
- semantic-only staleness;
- HTTP/application/browser command paths.

The redesign should reuse these capabilities where they still fit.

The main superseded assumption is:

> the author should manually activate detected composition dimensions before Auteur has presented a coherent narrative interpretation.

---

## Migration strategy

The redesign should prefer **reprojection and reordering** over tearing out qualified infrastructure.

Expected reuse:

```text
WorkingComposition
Mapping Planner
PromotionPreview
authority integration
revision overlays
receipt recovery
browser command plumbing
  → retained
```

Expected redesign:

```text
premise intake
analysis/inference projection
Navigator information architecture
default activation semantics
Discovery card inventory
guidance composition entry point
qualification flow
  → changed
```

Potential new production objects must be justified by information that cannot be cleanly represented through existing reasoning reports, session projections, WorkingComposition, or domain models.

---

## Non-goals

This package does not:

- create a sixth canonical semantic layer;
- make inferred narrative architecture canonical;
- require every trope or character function to become a persistent domain object;
- automatically accept Story Identity;
- automatically accept Structure;
- replace the existing Mapping Planner with LLM mapping;
- make prose generation part of first-session value;
- solve the full Global Map/Series architecture;
- perform existing-manuscript reverse engineering;
- require users to edit YAML or internal enums;
- create a universal taxonomy of every genre or trope before product use.

---

## Design invariants

1. **Premise interpretation precedes creative configuration.**
2. **One best coherent interpretation is the beginner default.**
3. **Alternatives appear only for materially ambiguous components.**
4. **Architecture analysis is derived, not canon.**
5. **The author can continue without individually confirming every inferred component.**
6. **Composition is optional refinement, not an admission gate.**
7. **Discovery searches possible directions from the architecture.**
8. **Story Identity owns explicit narrative commitments.**
9. **Structure owns plans, not basic genre extraction.**
10. **WorkingComposition remains noncanonical.**
11. **Mapping Planner remains non-authoritative.**
12. **Only existing authority services promote canon.**
13. **Supporting architecture must materially affect guidance when relevant.**
14. **Unrepresentable architectural meaning remains visible rather than disappearing.**
15. **Beginner UI uses narrative language before implementation vocabulary.**
16. **No product concept is added merely because it can be represented.**

---

## Acceptance criteria for implementation planning

The implementation plan may be written only if this specification is accepted.

The subsequent implementation must prove at minimum:

### Analysis

- a fresh premise produces one coherent Narrative Architecture Analysis;
- the hybrid fixture surfaces Mystery, superhero, and relationship/erotic-betrayal material without manual activation;
- character functions, framing, trope families, and relationship/world context can be surfaced where supported;
- evidence/provenance is inspectable;
- ambiguous component alternatives are bounded;
- analysis remains noncanonical.

### Navigator

- the first meaningful screen explains "what Auteur sees";
- stage progress remains visible but subordinate to story orientation;
- internal enum names are hidden from the beginner default;
- the author can continue without confirming every component;
- refinement is discoverable but optional.

### Composition

- analysis projects material guidance dimensions into WorkingComposition;
- author refinements update working guidance without canonical mutation;
- removing/reducing a component changes relevant downstream guidance;
- custom author additions preserve wording and provenance.

### Discovery

- Discovery operates on the current architecture;
- it presents a coherent recommended story direction rather than merely asking the author to identify existing premise traits;
- meaningful alternatives differ in story direction, not just wording;
- current cards are reclassified or replaced according to stage ownership.

### Identity

- selected direction produces a candidate Story Identity;
- promotion preview distinguishes canonical mappings, guidance-only meaning, provenance-only meaning, and unresolved meaning;
- explicit acceptance remains required;
- unsupported narrative material does not silently disappear.

### Structure

- Structure begins from accepted Identity;
- structure guidance uses relevant accepted/working architecture;
- Structure does not re-ask basic premise-classification questions.

### Authority and reliability

- analysis/refinement never mutates canon;
- crash recovery and idempotency remain correct;
- revision isolation remains correct;
- metadata-only changes do not create semantic staleness;
- semantic Identity changes do create appropriate downstream staleness.

### Human qualification

The human operator can:

- explain what Auteur inferred;
- distinguish inference from canon;
- optionally refine the interpretation;
- understand the purpose of Discovery, Identity, and Structure;
- observe multi-dimensional guidance;
- reach an explicit Identity acceptance without needing internal architecture vocabulary.

---

## Sequencing recommendation

The implementation should be staged around product behavior rather than infrastructure novelty:

```text
1. premise analysis contract + projection
2. Navigator "what Auteur sees" surface
3. automatic projection into WorkingComposition
4. optional refinement controls
5. Discovery reclassification
6. Story Identity handoff
7. Structure handoff
8. end-to-end qualification
```

Do not begin by adding a broad new ontology or generic narrative database.

Reuse the current Working Composition candidate wherever possible.

---

## Success definition

This redesign succeeds when a creative beginner can enter a premise and say:

> "Auteur understands the kind of story I mean. I can see what it inferred, correct it if necessary, explore what the story could become, choose the direction I want, and understand when I am actually committing something."

The author should not need to manually reconstruct the premise's narrative architecture before Auteur can begin helping them.