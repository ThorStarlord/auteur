# Atelier narrative-structure study

**Status:** opt-in experiment inside the opt-in Atelier (`?atelier&narrative`, or the *Story
structure* switch in the Atelier toolbar). It is not a production default; promoting it is an
owner decision.

**Question.** Can the Living Atlas make recorded narrative structure easier to recognise and to
explore, without moving the stable atlas, inferring meaning the records do not hold, or adding
another spatial system?

*A is the world. B is the magnifying glass.* This study changes neither. It changes what the
world gives weight to at rest, and what a selection says about story time.

**Recommendation:** adopt only the narrative-first hierarchy inside the experiment, with the
useful temporal cues folded into Progressive Revelation. A separate story-time trace was built,
measured and independently reviewed, then removed: it restated what selection already shows,
apart from one fact that now appears in selection itself.

## What the records establish

The study reads two recorded agent proposals: a 68-concept coastal literary mystery and a
156-concept fourteen-Book series. Neither is author-owned or accepted story.

| Recorded fact | Where it lives | Status |
|---|---|---|
| A genre's role (governing, supporting, tertiary, local) | `genre_contracts/<id>/role` | agent proposal |
| A genre's role *in a phase* (governing, supporting, locally dominant, background) | `phases/<id>/genres/<n>` | agent proposal; may differ from the contract role |
| A genre is activated in a phase, with local functions | `phases/<id>/genre_activations/<genre>` | agent proposal |
| Two phases run in parallel | `phases/<id>/parallel_with/<n>` | agent proposal |
| A node is placed under another node | `nodes/<id>/parent_id` | agent proposal |
| Agent interpretations, and what they affect | `interpretations/<id>` | never author-established |

Four facts shaped the design:

- **Connectivity is not importance.** Only genres carry a recorded role. The baseline atlas sizes
  every mark by its count of documented relationships, so in the dense specimen the tertiary
  *Structural disaster* (18 relationships) is drawn as large as the supporting *Civic daily-life*
  and *Craft and structural thriller* (18 each). In both real specimens the governing genre also
  happens to be the most connected; a constructed counterexample separates the two.
- **Only genres have direct phase participation.** A phase names a genre in its `genres` list or
  its activations. No phase record refers to an engine, structure, trope node, theme or emotion
  node. The Signature Burden Engine, the dense specimen's central mechanism, has 8 recorded parts
  and no phase record. A phase "pathway" for it could come only from chains of other
  relationships, which the study refuses to show as participation.
- **Equal wording is not a reference.** Contract trope functions recur word for word in phase
  functions (for example *The incomplete archive* in phases 1, 3 and 4), but no phase records a
  `trope_function_refs` link to them. The Studio already treats equal wording as distinct ideas;
  this study keeps that rule and reports the recurrence instead.
- **The proposal's own words go beyond its fields.** The dense summary says the signature-burden
  engine "owns the series", and an interpretation says every genre contract is "a working framing
  … none of them is presented as an author commitment". The candidate shows both rather than
  overriding either.

## The candidate

### 1. Narrative-first resting hierarchy

```text
Story structure off (baseline)          Story structure on (candidate)
genre mark size = 0.8 + 0.55·√(rel/max)  genre mark size = contract role: governing 1.6,
every mark sized by relationships        supporting 1.12, tertiary/local 0.9; others 1
label priority + 60·√(rel/max)           label priority + recorded role or parenthood only
—                                        governing genre: halo + "GOVERNING · PROPOSED"
—                                        recorded parent: square frame + "CONTAINS n",
                                         no extra size
folio: "Landmarks · most documented"     folio: "Recorded story structure" (roles with their
                                         sources, every recorded parent, the proposal's own
                                         interpretation about its genre roles), then "Most
                                         connected", which says it measures connectivity
```

Positions, camera, bands, categories and every relationship thread are unchanged. Parent links
are drawn slightly stronger at rest. The folio says that the atlas frames a parent but does not
size or rank it as governing, and that what a parent link means for the story is in the
proposal's own words.

### 2. Story time inside Progressive Revelation

```diff
 select a concept (Progressive Revelation, unchanged: threads to its recorded relatives)
+  Story structure on:
+    activated phase pill      "PHASE ROLE · BACKGROUND" … "PHASE ROLE · GOVERNING"
+    phase listing the genre   marked in place (dotted pill, role named), no thread
+      without activating it
+    other phases              unchanged (faded, as in the baseline)
+    folio · In story time     every phase in recorded order: phase role or "not recorded",
+                              "listed, no activation", recorded parallels, every source;
+                              the contract role named beside the phase roles
+    no phase record refers    "No phase record refers to this concept … not evidence that
+      to the concept          it is absent"; recurring equal wording reported, not linked
+    recorded in one phase     one line: "recorded in phase 5 of 9"
```

No thread is added, nothing moves, and leaving the selection (Esc) clears every mark.

### What was tried and removed: a separate story-time trace

An author-initiated *Trace through story time* entered a state that faded everything but the
phases and labelled each one with what it records. It worked as specified: every mark resolved to
its source, no line joined the phases, and Esc restored the exact view (synchronous cost 30–37 ms,
no animation). Measurement and the independent review then showed:

- Only genres qualified: 3 of 27 named concepts in the small specimen, 7 of 67 in the dense one.
- Progressive Revelation already joins a genre to every phase that activates it. Beyond that, the
  trace added the role each phase records (all 10 genres) and, for 2 genres, 2 phases each that
  list the genre without activating it. The folio already listed both.
- As a mode it added an Esc layer, sent keyboard and hover to concepts it had faded, and at phone
  width showed 3 of 9 roles for *Civic daily-life*.

The new information fits inside selection, so the control was removed and those cues were added
to the selection itself (section 2).

## What the comparison shows

Measured in the served Studio at 1440×900 (`comparison.json`); judgements are marked as such.

**At rest, the hierarchy separates recorded roles that the baseline flattens.**

| Specimen | Baseline genre mark sizes | Candidate | Resting names | Overlaps | Moved |
|---|---|---|---|---|---|
| Small, 68 concepts | 1.35 · 1.26 · 1.26 | 1.6 governing · 1.12 · 0.9 tertiary | 31 of 31 both | 0 both | nothing |
| Dense, 156 concepts | 1.18 to 1.35 (seven genres) | 1.6 · 1.12 ×4 · 0.9 tertiary and local | 66 of 76 both | 0 both | nothing |
| Counterexample | governing Fantasy 1.26 < supporting 1.35 | governing Fantasy 1.6 > supporting 1.12 | 31 of 31 both | 0 both | nothing |

The candidate draws the tertiary *Structural disaster* smaller than the supporting genres it
matched in the baseline. In the counterexample the baseline draws the governing genre smaller
than a supporting one; the candidate does not. Where the governing genre is also the most
connected (both real specimens), the baseline already looked roughly right; there the gain is
the clear role scale, the role named in words, and the five recorded parents framed.

In the dense specimen the governing genre's role line does not fit at rest without covering a
neighbour's mark, so its name is set larger instead; the call-out on hover, the folio and the
spoken label state the role. On the small specimen and the counterexample the role line shows.

**On selection, the cues add the phase roles without costing the neighbourhood.**

| Concept (dense unless noted) | Relationships | Phases joined (both arms) | Pills naming a phase role | Phases listed, no thread | Neighbours named, baseline → candidate |
|---|---|---|---|---|---|
| Institutional certification procedural (governing) | 32 | 8 | 8 | 0 | 22 → 21 of 24 |
| Tribunal drama without an overlord (supporting) | 20 | 3 | 3 | 0 | 17 → 17 of 17 |
| Civic daily-life (supporting) | 18 | 4 | 4 | 2 | 16 → 16 of 16 |
| Structural disaster (tertiary) | 18 | 3 | 3 | 0 | 16 → 16 of 16 |
| Evidence inquiry (local) | 15 | 2 | 2 | 2 | 14 → 14 of 14 |
| The Signature Burden Engine (central mechanism) | 16 | 0 | 0 | 0 | 8 → 8 of 10 |
| A phase-local structural function | 1 | 1 | 1 | 0 | 1 → 1 of 1 |
| Literary mystery (small, governing) | 20 | 4 | 4 | 0 | 14 → 14 of 15 |
| Fantasy (counterexample, governing) | 14 | 4 | 4 | 0 | 11 → 11 of 11 |

Cameras, positions and the number of threads drawn are identical between the arms for every
case, and no label overlaps another.

What the cues let an author read, and the baseline does not (judgement, from the records):

- *Civic daily-life* is recorded as background in phases 1, 2 and 4, locally dominant in 5,
  supporting in 8 and governing in 9: a supporting genre that ends the story governing.
- *Horror* is tertiary in its contract but locally dominant in phase 2 and supporting in 3 and 4;
  both records are shown, neither overrides the other.
- *Tribunal drama* is the second most connected genre (20 relationships) but recorded in only
  3 of 9 phases (4, 7, 8). Connectivity says nothing about presence across story time.
- The central mechanism has recorded structure and no phase record; the folio says that plainly.

## Integrity

| Constraint | How the candidate meets it | Checked by |
|---|---|---|
| Importance only from a recorded role, never from degree | Mark size and label priority use `genre_contracts/<id>/role`; no relationship count enters either | counterexample and dense role tests |
| Agent roles are not author-accepted | "PROPOSED" on the role line; folio: "the agent proposal's, not author decisions"; the proposal's own interpretation about its roles is shown | folio text tests |
| Parenthood is not governing importance | Frame and count, size unchanged; folio says the atlas does not size or rank a parent as governing | parent tests |
| Every marked phase resolves to a source | Each phase cue comes from a relation, a `genres` entry or the concept's own record; every source is listed and resolved | model and served tests resolve each reference |
| No multi-hop reachability as participation | Only direct phase records count; chains are never followed | model test: the engine has none |
| No causality from order; no path between occurrences | No line is drawn between phases; the folio says order is not recorded causation and shows recorded parallels | thread-count equality test |
| Unrecorded is not absent | "Not recorded" and "a gap in the records, not absence from the story" | folio text tests |
| No writes | Presentation only; nothing is persisted | canvas revision unchanged in every test and capture |

## Evidence

Produced at `2d1c4b31` (clean tree, based on `main@e48a3ecc`); see
[the evidence folder](../qualification-evidence/atelier-narrative-structure-20261121/README.md).

```text
tests/test_beginner_studio_atelier_narrative_browser.py   5 served-browser tests
  switch off by default; on: role sizes, every parent framed, folio
    statements; nothing moves; off restores the baseline           dense
  governing genre with fewer relationships is the governing mark  counterexample
  selection: phase roles on pills, listed phases marked, same
    view and threads as baseline, every source resolves, Esc clears dense
  no cue without a phase record: engine, single-phase function,
    contract function with recurring words, baseline silent        dense, small
  keyboard focus on a story-time row emphasises the phase; phone:
    same view as baseline, no clipped label, no overlap            dense
tests/test_studio_atelier_model.mjs                13/13 (roles not degree, sources, parallels)
Atelier Python + browser                           19/19
Studio page and browser slice (66 files)           348 passed (studio.js reads one more parameter)
capture (comparison.json)                          positions, cameras, threads identical; revision 1 → 1
```

```text
live, windowed Chromium, dense, 3 rounds
                         synchronous ms, baseline → candidate        worst frame ms, baseline → candidate
  select Civic          73.3 / 26.7 / 29.4 → 70.5 / 30.3 / 31.9     133 / 17 / 17 → 83 / 33 / 17
  select Procedural     51.7 / 29.2 / 30.2 → 45.7 / 30.4 / 31.2     33 / 33 / 17 → 33 / 33 / 33
  return (Esc)          26.5–29.6 → 28.6–35.6                        17–33 → 17–33
  switch at rest        candidate only: 18.7–22.0                    16.8
  switch while selected candidate only: 22.0–24.8                    16.8–17.0
  (the first select of a session is slower in both arms; mean frame 16.7–20.6 ms throughout)
```

## Independent review

A read-only reviewer (an agent that did not build the candidate) examined the trace version at
`aceddfb8` in the served Studio, including main's files injected into the page for a baseline
check. It found nothing blocking. Its findings, each reproduced before it was addressed:

| Finding | Severity | Disposition |
|---|---|---|
| "No phase record names this concept" is false for contract trope functions whose words recur in phases | consequential | Reworded to "refers to"; recurring equal wording is reported, not treated as identity |
| "Structure records containment, not importance or influence" contradicts the dense summary ("owns the series"); the interpretation about genre roles is computed but never shown | consequential | The folio now states what the atlas does, not what the link means; interpretations naming a concept, and the one about the genre roles, are shown with their status |
| During a trace, keyboard and hover land on faded concepts | consequential | The trace was removed |
| At phone width the trace shows 3 of 9 roles | consequential | The trace was removed; selection cues checked at 390 px (no clipped label, no overlap) |
| Only top-level parents are framed | minor | Every recorded parent is framed and listed |
| Recorded parallel phases are hidden | minor | Listed with each phase |
| Contract and phase role words collide | minor | "PHASE ROLE ·" on the pill; the folio names the contract role beside the phase roles |
| The switch appears in the baseline arm | minor | Kept: a reversible comparison switch inside the Atelier is the study's design; the ordinary Studio is unchanged |

Its judgement on the central question was the same as the measurement's: adopt the hierarchy,
fold the useful temporal cues into Progressive Revelation, and do not keep a separate mode.

## Limitations

- No author has used the candidate. Every judgement here is the builder's or one agent
  reviewer's; none is author acceptance.
- Roles, phase roles and parent links are all agent proposals. The candidate gives weight to what
  the proposal records; a wrong role in the proposal would be drawn with the same confidence,
  labelled as proposed.
- A phase names a genre by id or by its recorded title; a phase that misspells a genre's title
  is not matched, and that phase shows "not recorded".
- In these specimens only genres have direct phase records, so story-time cues appear only for
  genres and phase-local functions. Richer phase records would extend them without code changes.
- At rest the dense governing genre's role line does not fit; its name is set larger instead.
- Touch was emulated at phone width, not tested on a phone.

## Recommendation

**Adopt only the narrative-first hierarchy, incorporating the useful temporal cues into the
existing Progressive Revelation** (as implemented here, inside the opt-in Atelier).

The hierarchy is a small, source-grounded change that moves nothing, keeps every resting name,
costs nothing measurable, and stops the atlas from implying that connectivity is importance,
which the counterexample shows the baseline does. The temporal cues carry the one new fact the
trace offered, the role each phase records, inside the selection authors already use. A separate
trace mode would add a control for 10 concepts across both specimens.

Making either the Atelier or this comparison the default Studio view remains an owner decision.
