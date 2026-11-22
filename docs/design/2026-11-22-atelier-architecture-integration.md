# Atelier ↔ Architecture workflow integration (2026-11-22)

**Status:** implemented inside the opt-in Atelier (`?atelier`). The ordinary Studio is unchanged.
Default promotion of the Atelier remains an owner decision.
**Base:** `main@21a4506c` (PR #631). **Evidence:**
[`docs/qualification-evidence/atelier-architecture-integration-20261122/`](../qualification-evidence/atelier-architecture-integration-20261122/).

## The question

Can an author understand a narrative concept in the Living Atlas, investigate or revise it with
the Studio's existing coding-agent workflow, and come back to a consistent working Architecture
without rebuilding their context?

## What already existed (not rebuilt)

- Ontology meanings in every Architecture request (`studio_ontology_context.py`), marked as
  derived guidance, not story intent.
- Source-qualified projections: the explanation packet, the Atelier model, and the
  `trope_function_refs` contract (#625), which joins a contextual function to a shared trope only
  by a recorded reference.
- The graph-grounded coding-agent panel ("Explore graph with coding agent"): typed source anchors
  resolved on the server, read-only inquiries (explain, challenge, explore, compare), and
  holistic revision through review and an explicit Apply.
- Progressive Revelation and Focused Constellation in the Atelier, and the story-structure
  comparison (#631).

## Findings on `main` (measured in the served Studio, `baseline.json`)

| Step of the author journey | On `main` | Cause |
|---|---|---|
| Select one contextual trope function and investigate it | Only "Read the full explanation" is offered. No route to inquiry or revision. | Creative workflow gap |
| Select a shared trope and investigate it | "Open in Studio inspector" silently anchors the coding-agent panel, which opens 1,153 px down a 900 px window with no cue | Navigation gap |
| Prepare a revision request | The atlas clears the selection and announces "The working Architecture changed" although its request SHA is unchanged | Continuity defect; the announcement has the wrong authority |
| Apply the reviewed revision | Selection cleared; all 156 positions move although the revision added only references; the atlas ends 2,020 px above the window; the announcement says "Nothing was saved" | Continuity and authority defects |
| Read what changed | Only the Studio's text diff of record kinds and ids | Presentation gap |
| Hand one function to the agent | The finest anchor is the whole `trope_functions` list | Semantic projection gap (identity widened at the interface) |
| Read a genre's payoff expectations | Joined text without sources; "Reader payoffs" without proposal status | Authority and provenance gap |
| Read a shared trope in the dense specimen | Nine local phrases repeat "the first crosser"; no record joins them (the specimen predates #625), and the folio did not say so | Presentation gap; the record itself is historical, not a reasoning defect |
| Engine's agent interpretations | Shown only with the story-structure switch on | Presentation gap |

## Responsibility chosen

**Atlas → existing coding-agent workflow → atlas, with source identity and place preserved.**
The alternatives were weaker:

- A new Atelier-native inquiry panel would duplicate the existing panel and its server contracts.
- More facets or nodes for ontology concepts would add display without improving any task.
- A setup→payoff representation is a real gap, but its owner is Series/Book structure, which the
  Studio does not expose (see "Boundary" below). That is a product decision, not a UI fix.

## What changed

```text
Atelier folio (selected concept)
  Develop with your coding agent                         new
    exact source: "Trope function 1 of the Craft and structural thriller contract"
                  "the first crosser" · genre_contracts/genre-craft-thriller/trope_functions/0
    Challenge this design · Explore possibilities · Request a revision
      → studio.js developFromAtelier: graphSelectionController.select(anchor),
        creativePanel.setOperation(op), scroll to the panel, focus the question field
  Changed by the revision you applied                    new (after an applied revision)
  Proposed reader payoffs, each with its source          was: joined text, no source
  Recorded contextual functions / Same words, not recorded as this trope   new (trope nodes)
  Agent interpretations naming it                        was: only with Story structure on
  Relationships to local phrases name where each is recorded

Atelier update()
  same request SHA (re-read while a request is prepared) → keep everything, announce nothing
  applied revision of the version on screen (studio.js revision context) →
    revisionDelta by recorded identity and every recorded field, dashed ring on touched concepts,
    keep the selected concept, constellation, trail and zoom if it is still recorded,
    keep every position if story order, scopes and each concept's place of belonging are
    unchanged (author can "Lay out the atlas again"), else lay out again and say so

Studio (only with ?atelier)
  "↑ Back to the atlas · <concept>" beside the coding-agent panel and the review
  a working-state line in the folio: request waiting · revision ready to review · answer ready

Graph intent (backward compatible)
  GraphAnchor.index: optional, only with a list field; resolves to entryValue and entrySourceRef
  carried by the JS resolvers, agent bridge, revision intent builder and the CLI (@field#index)
```

### The one model extension, and why

`GraphAnchor.index` was added after the following were inspected: the anchor contract
(`field` names a whole schema property, and `reference` addresses only `parent_id`,
`emotion_target_ids`, `complex_emotion_ids`, `genre_activations` and `parallel_with`), the
explanation packet's function keys, and the trope-function reference contract. A contract's
trope functions are one list field, so the narrowest existing anchor for one function was the
whole list, and the agent was told the author was asking about every function of that genre.
The index is optional, valid only with a recorded list field, fails closed when the entry is
absent, and leaves every existing intent and persisted receipt valid. It adds nothing to the
Architecture schema or the ontology. Phase-local functions keep their existing activation-level
anchor (`reference` to the genre activation); when a genre is activated twice in one phase the
folio says that the request is anchored on all of the phase's activations.

## Boundary: setup, payoff and Series context

- **Ontology** defines Setup, Payoff, Revelation, Reversal and Arc, their direction and rules
  (`data/ontology/base_ontology.yaml`), and supplies them to every Architecture request as derived
  guidance.
- **A working Architecture** records payoffs only as a genre contract's `payoff_expectations`
  (prose) and in free-text link functions, phase functions and interpretations. It has no typed
  setup→payoff relation.
- **Series/Book structure** owns typed setups, payoffs and their order across Books
  (`src/auteur/series/models.py`, `graph.py`, `SetupPayoffValidator`). The served Studio has no
  route to it.
- **The UI can legitimately** list each payoff expectation with its own source and as a proposal
  (done here), and quote link text verbatim.
- **Only the agent can hypothesise** which recorded element prepares which payoff, and that belongs
  in an inquiry answer or an interpretation, never as a typed dependency drawn by the atlas.

So "which documented plans prepare this payoff?" cannot be answered from the Studio today, and
this change does not pretend to: the folio calls them "payoffs the proposal hopes for, not
recorded setups or commitments of a Series or Book plan."

## Integrity

- One concept, one address: every one of the 156 dense and 68 small concepts maps to an anchor the
  Studio's own resolver accepts (model test). A contract function is one entry; a phase-local
  phrase is its recorded activation; a trope node is the node. Equal wording never maps one onto
  another.
- A revision delta compares recorded identities (node ids, contract positions, source references
  and endpoints), never titles; the same records under a new request SHA are no change.
- Nothing in the Atelier calls an agent or writes a record. Preparing changes nothing; the only
  writes in the journeys are the two revisions the author applied (canvas revision 1 → 3), and the
  author's story items are unchanged.
- The revision marks are labelled as a comparison with the previous working version, not a record.

## Independent review

A read-only reviewer that did not build the change reproduced eight problems at `9cb278b5` in
the served Studio. All are fixed in `8ea9b22a` with regressions:

| Finding | Disposition |
|---|---|
| A reordered list was reported as rewording of the same entry; my first fix inferred "moved" from equal words | Reverted the inference; the folio and announcement describe the entry at the position and say identity is positional |
| A kept layout could contradict a changed phase order; record fields beyond the title were not compared | Layout kept only when its inputs are unchanged; every recorded field is compared; "0 changed" is never claimed when nothing drawn changed |
| The working line could name the wrong concept or another canvas | Named only for the request actually sent with that anchor; follows inquiry history; reset on canvas switch |
| An unsent draft was cleared after a failed send | Recorded as sent only after the request exists |
| "Back to the atlas" stayed visible with the atlas off screen | Hidden unless the atlas is on screen |
| Applying a revision reset constellation, zoom and trail | Kept when the concept is still recorded |
| "Challenge" offered where the Studio offers only "Explain" | Only the operations the Studio offers for that source kind |
| Index validation mismatches | Same integer check everywhere; the CLI rejects a malformed `#index` with a message |

It judged the entry-index extension warranted, and the hand-off itself a real improvement.

## Limits

- No author has used it. The journeys were run by an agent playing both author and coding agent.
- The coding agent's revisions in the journeys were written by this agent (Claude Opus 5.5) in a
  disposable project, as the Studio's host-agent design expects; they are working proposals.
- Positional identity: a contract function is identified by its list position, as its source
  reference is. After a revision, the folio reports what the entry at that position reads now and
  says it may be a different entry; it never infers which entry moved from equal words.
- A kept layout keeps positions after new relationships are recorded, so a concept may sit away from
  the phases it newly relates to until the author lays the atlas out again.
- The Studio's coding-agent panel itself (raw ids in its anchor chips, a manual response paste) is
  unchanged.
- Setup→payoff relationships and Series planning are not reachable from the Studio.
