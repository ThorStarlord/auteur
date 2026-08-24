# Series Vertical Slice V1 User-Validation Package

Status: research-ready; no participant evidence has been collected.

This package validates whether a creative beginner understands and can use the
qualified Series journey. It does not qualify code, simulate a participant, or
decide the next capability in advance.

## Study question

Can a creative beginner use the sparse Series → Book 1 → realized consequence
→ later-Book Map/Focus journey without believing that Auteur has planned the
whole Series, silently changed canon, or made the Book 2 recommendation
authoritative?

## Qualified basis

Use the exact qualified candidate recorded in
[the qualification report](../engineering/series-vertical-slice-qualification-v1.md):

```text
candidate: e5236763949107424cb71f7102f5c800c1347bea
fixture:   tests/fixtures/archive_of_lies_vertical_slice/
surface:   qualified CLI Map/Focus adapter
```

The CLI is operated by the facilitator. The participant should not need to
use a terminal. The throwaway HTML prototype may be used in a separate
presentation experiment, but this base protocol uses the qualified CLI so
that observed behavior remains tied to the real implementation.

## Participant and session

Target participant: a creative beginner who writes, plans stories, or wants to
write, but is not assumed to know Auteur's domain vocabulary or CLI.

Recommended session length: 30–45 minutes.

Use a fresh temporary project for every session. Do not use a participant's
private story or collect personally identifying story material for this first
study. Ask permission before recording audio, screen, or quotations. The
participant may stop or decline any step.

Facilitator rules:

- Show the default beginner-facing output first. Do not lead with revision
  IDs, proposal IDs, or internal artifact names.
- Ask the comprehension question before explaining the intended answer.
- Prefer “What do you think this means?” over correction or teaching.
- If the participant asks whether something is permanent, ask for their
  interpretation first, then record the question and answer neutrally.
- Do not describe an option as correct because Auteur recommends it.
- Do not turn a participant's request for an unsupported capability into a
  workaround. Record it as evidence about the V1 boundary.

## Scenario brief

Read only this brief before the task:

> You are beginning a series called *Archive of Lies*. A city archive may have
> falsified its own history. You want each Book to expose a consequential
> conflict between official history and lived memory, but you do not want to
> plan the entire Series yet. In Book 1, Mara investigates a missing ledger.

Do not explain the intended Series commitment, authority boundaries, or Book 2
recommendation before the participant encounters them.

## Participant task sequence

The facilitator performs the CLI operations in the run sheet below while the
participant reviews, accepts, interprets, and chooses. Pause after each stage
and record the participant's own words before continuing.

| Stage | Participant sees and does | Evidence to collect |
|---|---|---|
| 1. Series promise | Reviews the sparse Series proposal and says whether it is a useful starting promise; accepts it if willing. | Does the participant expect a complete Book roadmap? Can they state what the promise leaves open? |
| 2. Book 1 direction | Reviews the local Book 1 direction and its relation to the Series promise; accepts it if willing. | Can they distinguish the local Book problem from the Series-level promise? |
| 3. What became true | Reviews the Book 1 outcome candidate before acceptance. Says what they think would become true, then accepts it if willing. | Does the participant distinguish a proposed outcome from the accepted change to narrative reality? |
| 4. Plan the next Book | Facilitator asks whether they want to begin planning Book 2. Participant explicitly chooses to continue. | Do they understand this as exploratory planning rather than acceptance of Book 2 canon? Do they believe they must plan all later Books? |
| 5. Map | Reads the default Map. Identifies what is established, why the surfaced items matter now, and what decision is available. | Is the context compact and understandable? Does “why it matters now” explain the carry-forward selection? |
| 6. Focus | Reads the default Focus. States the recommendation, its reason, its principal tradeoff, and the alternatives. | Does the recommendation feel useful rather than authoritative, verbose, or arbitrary? |
| 7. Three decision branches | In isolated copies of the same Book 2 state, chooses the recommendation, chooses the other presented option, and defers. | After each action, what does the participant think changed, what remains open, and what would they do next? |

If the participant declines an acceptance or wants to stop, pause the journey
and record that as a result. Do not persuade them to complete the flow.

## Comprehension questions

Ask these as open questions, in this order, without supplying the expected
terms. The parenthetical answers are for scoring only.

1. **What did you just establish about the Series?**
   Expected: a sparse promise/commitment or direction, not a complete plan for
   every future Book.
2. **What was specific to Book 1?**
   Expected: the local direction and its bounded investigation, distinct from
   the Series commitment.
3. **What became true after accepting the outcome?**
   Expected: the founding record became confirmed fraudulent in canonical
   narrative state; merely proposing the outcome would not have done that.
4. **Why is Auteur showing you the commitment and the exposed founding fraud
   while you plan Book 2?**
   Expected: they remain relevant because the accepted promise governs Book 2
   and the accepted state change creates an active constraint or conflict.
5. **Why did Auteur recommend the living-witness option, and what is the
   tradeoff?**
   Expected: it directly tests official history against lived memory using the
   exposed record; the tradeoff is less direct examination of the institutions
   that protected the fraud.
6. **What changes if you choose the recommendation, choose the other option,
   or defer?**
   Expected: the workflow choice is recorded, but none of the three choices
   accepts Book 2 Direction or makes Book 2 Canonical State.
7. **What would you do next?**
   Expected: a useful creative next step such as developing the selected
   direction, exploring the witness or cover-up, or returning later after
   deferring. The participant need not use Auteur's internal vocabulary.

## Pre-registered success criteria

Score each of questions 1–6 before discussing the intended model:

```text
2 = correct in ordinary language without a leading prompt
1 = substantially correct after one neutral follow-up
0 = incorrect, or the participant attributes authority to a proposal,
    derived context, or Book 2 decision action
```

The session meets the primary comprehension criterion when the participant:

- scores at least 5/6; and
- has no authority inversion on questions 1, 3, or 6; and
- can name a useful next creative action in question 7 without being told one.

Record usability separately. A session can fail comprehension while still
revealing a valuable presentation insight, and a participant can comprehend
the model while finding the interaction too dense or restrictive.

Secondary signals to record:

- participant identifies at least one surfaced item's “why now” without
  facilitator interpretation;
- participant can distinguish the recommendation from a fact or command;
- participant can select or defer without needing to understand CLI syntax;
- participant asks for more context, less context, a different explanation,
  or free-form Book 2 authoring;
- participant's next action is clear within roughly 30 seconds after Focus.

## Facilitator run sheet

Run these commands from the isolated environment built from the qualified
candidate. Keep proposal IDs private unless the participant asks about the
deeper evidence view.

```powershell
$fixture = "H:\GithubRepositories\auteur\tests\fixtures\archive_of_lies_vertical_slice"
$project = "<fresh temporary project path>"

auteur series journey propose-series $project --input "$fixture\series_direction.yaml"
# Capture the printed Proposal ID as $seriesProposalId.
auteur series journey accept-series $project $seriesProposalId

auteur series journey propose-book $project --input "$fixture\book_1_direction.yaml"
# Capture the printed Proposal ID as $bookProposalId.
auteur series journey accept-book $project $bookProposalId

auteur series journey propose-outcome $project --input "$fixture\book_1_outcome.yaml"
# Before accepting, ask: “What do you think would become true if you accepted this?”
auteur series journey accept-outcome $project recovered-founding-ledger

auteur series journey plan-next-book $project --book 2
auteur series journey map $project --book 2
auteur series journey focus $project --book 2
```

The participant should see the default Map and Focus output. For the private
decision ID, run the detail view in a facilitator-only terminal or capture the
ID from the Focus output without showing the source identifiers:

```powershell
$focusDetail = auteur series journey focus $project --book 2 --detail
# Capture Proposal ID from $focusDetail as $decisionProposalId.
```

Create three isolated copies of the project before recording any decision
action. Use the same proposal ID in each copy:

```powershell
Copy-Item -Recurse $project "${project}-recommended"
Copy-Item -Recurse $project "${project}-other"
Copy-Item -Recurse $project "${project}-defer"

auteur series journey decide "${project}-recommended" $decisionProposalId --choice recommended
auteur series journey decide "${project}-other" $decisionProposalId --choice trace-institutional-cover-up
auteur series journey decide "${project}-defer" $decisionProposalId --choice defer
```

Before each branch, ask the participant to predict what will become true and
what will remain open. After each branch, ask them to explain what actually
changed. The option IDs are facilitator controls; show the participant the
labels “Center a living witness” and “Trace the cover-up,” not the IDs.

## Observation sheet

Copy this block once per session:

```text
Session ID:
Date:
Facilitator:
Participant description (non-identifying):
Surface used: qualified CLI / other:
Recording consent: yes / no

Stage | Observed fact | Exact participant words | Participant action | Prompt used | Severity
------+----------------+--------------------------+-------------------+-------------+---------
      |                |                          |                   |             |
      |                |                          |                   |             |
      |                |                          |                   |             |

Comprehension scores:
Q1:   Q2:   Q3:   Q4:   Q5:   Q6:
Q7 next action:
Primary criterion: pass / fail / indeterminate

Confusion or terminology:
Excessive explanation or density:
Missing context:
Authority misunderstanding:
Map → Focus transition issue:
Bounded-alternative reaction:
Unsupported capability requested:
Other notable behavior:
```

Classify each note before interpreting it:

- **Observed fact:** what the participant did or what appeared on screen.
- **Participant statement:** the participant's words, quoted or closely
  transcribed.
- **Facilitator interpretation:** a hypothesis about why it happened.
- **Product implication:** a proposed change, recorded only after the evidence
  is summarized.

Do not put facilitator interpretations in the participant-statement field.

## Results template

After the session, complete this section without rewriting observations to fit
the product model:

```markdown
# Series Vertical Slice V1 Participant Result

Session:
Participant profile:
Surface:

## Observed facts
-

## Participant statements
- “...”

## Comprehension scores
| Question | Score | Evidence |
|---|---:|---|
| Q1 Series promise vs complete plan | | |
| Q2 Book 1 locality | | |
| Q3 accepted outcome vs proposal | | |
| Q4 why-now context | | |
| Q5 recommendation and tradeoff | | |
| Q6 choose/other/defer authority | | |
| Q7 next useful action | | |

Primary criterion: pass / fail / indeterminate

## Friction themes
- comprehension:
- terminology:
- context selection/explanation:
- Map → Focus transition:
- recommendation/tradeoff:
- authority boundary:
- bounded alternatives:
- missing capability:

## Facilitator interpretations
-

## Candidate product implications
-

## Confidence and limits
- One participant is directional evidence, not general validation.
- Separate observed behavior from proposed product changes.
- Do not choose V2 from this template until recurring or consequential
  evidence is identified.
```

## V2 decision rule

Do not preselect the next implementation capability. After at least one
session, compare observed friction against the qualified contract:

```text
qualified V1
  → participant evidence
  → consequential comprehension or workflow friction
  → smallest product/design boundary that addresses it
  → explicit decision and implementation qualification
```

Possible findings include a need for free-form Book 2 Direction, clearer
why-now explanations, a more legible acceptance boundary, less or more
carry-forward context, or a guided presentation surface. These are hypotheses
until participant evidence supports one.
