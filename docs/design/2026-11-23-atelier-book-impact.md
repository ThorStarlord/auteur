# Atelier: what Architecture changes mean for the working Books

Status: implemented on `feat/atelier-book-impact` (builds on #631–#634). Opt-in Atelier only.

## The author's question

"I changed my working Architecture. Which of my working Books does that touch, how exactly, and how do I
bring one back in line, without losing my place?"

On `main` before this change the author could open each Book in the Series and Book context and read its
owner freshness. For the impact study records (`scripts/seed_book_impact_study.py`):

- Book 24 said only "A concept it refers to is no longer in the working Architecture", and named the
  removed concept by its raw id (`inst_gate_table · no longer recorded`).
- The changed *Ledger engine* was not mentioned. The owner's single `semantic_impact` flag stops at the
  first removed node, so the change was hidden.
- Book 26 (out of date, every cited concept unchanged) read the same as any other out-of-date Book.
- There was no view across Books, and nothing led from the Architecture revision to the Books.

## What each case means and how it is established

Every fact comes from the Working Book owner's own record. The owner compares the node fingerprints that
`current.json` kept in `series_nodes` with the current working Architecture. A reference exists only where
the Book records one: a typed `series_node` ref, an agent's `name_source`, or a typed edge target.

| Case | How it is established | What the Atelier says | What it does not claim |
|---|---|---|---|
| A. Architecture revised, every cited concept unchanged | the Book's `series_request_sha256` differs from the current request, and every fingerprint matches | "every concept it cites is unchanged. That shows its recorded references did not change, not that the Book is unaffected." | that the Book is unaffected |
| B. Cited concept changed | the fingerprint differs | the concept's wording when the Book was written, and now, marked word by word; the citing elements | that the story no longer works |
| C. Cited concept removed | the node is absent | the concept as the Book recorded it, and the citing elements; it is never shown in the atlas | that the concept is still current |
| D. Book source changed | the owner's `source_changed` | "a change to the Book's source, not to the Architecture" | an Architecture-origin impact |
| E. No recorded reference | there is no ref | "That does not show that no Book depends on it." | independence |
| F. Unreadable record | reading the Book record raises | "whether it is affected cannot be told"; no Reconcile is offered | "unaffected" |
| Not recorded | there is a ref but no kept fingerprint | "the version it was written against is not recorded, so whether it changed cannot be told" | unchanged |

**The recorded version of a changed or removed concept.** It is used only when a kept record holds a node
whose digest equals the recorded fingerprint. The owner looks first in the Book's own request packets (a
develop request carries the whole Architecture it was prepared on), then along the working Architecture's
applied revision chain (`studio_architecture.architecture_versions`). Nothing is reconstructed. If no record
matches, no version is shown.

Books the canvas keeps source items for, but that have no working Book (including one with only a prepared
develop request), are listed as such: nothing they might depend on is recorded.

## Decisions

1. **Extend the existing read, not a second freshness system.** The owner's `book_series_references` gains
   a per-reference `status`, `recorded`, `current` and `fields_changed`. The #633 Series-context projection
   that the Atelier already reads gains:
   - `architecture_revisions_since` for each Book;
   - the canvas's Books without a working record.

   The owner's `_freshness` is unchanged.
2. **One currentness rule, enforced by the owner, for every entry point.**
   - **The flaw on `main`:** `book_apply_review` recorded any applied revision against the request's
     Architecture and source. A targeted revision of an already out-of-date Book therefore marked the whole
     Book current.
   - **#634's guard:** it closed this only in the Studio, with prepare and apply checks. The owner's CLI kept
     the old behaviour.
   - **The owner rule now:** a non-holistic revision of a Book that was out of date when it was prepared is
     applied, but the Book keeps its earlier `series_request_sha256`, `source_sha256` and every kept fingerprint.
     A concept the revision newly cites is recorded as it is now. The apply result, the lineage entry and
     `applied_review` say `currentness: kept_baseline`.
   - **Compatibility:** older workflows still run. A CLI targeted revision still prepares, completes and
     applies; only what the Book claims to be current changed.
   - **The adapter:** the Studio's own apply refusal is removed, because the owner now holds the rule. The
     review explains that the Book stays out of date.
3. **Reconciliation is the existing whole-Book revision.** The Studio already asks the owner for a whole-Book
   revision when a Book is out of date (`RevisionExpectation(current_only=True)`), because only that can bring
   it up to date. "Reconcile Book N" opens that composer, seeded with the recorded evidence in editable words.
   The draft:
   - names the changed and removed concepts and the ids of the elements that cite them;
   - asks the agent to keep what still holds and leave author decisions open;
   - leaves whether the story still works to the author.

   A partial reconciliation is not offered. It cannot make the Book current, and offering it as reconciliation
   would advertise something it does not do.
4. **The atlas stays the orientation surface.** Nothing is added to the atlas. Three places lead to the
   overview:
   - the applied-revision summary;
   - the atlas reading's Series section;
   - each concept's existing Book references.

   The overview lives in the existing Series and Book context leaf, so Back and Escape return to the same
   concept, trail and camera.
5. **Investigation stays a question.** For a changed concept, "Ask your coding agent what this may mean"
   drafts a hypothesis question in the existing #632 inquiry panel. It is never sent for the author.

## Alternatives not taken

- **A cross-Book dependency engine, or inference from wording.** It would assert relationships no record
  holds.
- **Per-reference reconciliation, recording a single concept as reconciled.** It would need a new freshness
  model at reference granularity. A whole-Book revision is the only operation the owner can honestly record
  as current.
- **Refusing CLI targeted revisions of out-of-date Books.** That is safe, but it would break a legitimate
  workflow (fixing the elements that cite a removed concept) that keeping the baseline supports honestly.
- **Badges on atlas concepts.** They would add clutter and imply severity. The evidence is one action away
  instead.

## Owner behaviour this surfaced

While a Book still cites a removed concept, the owner refuses any revision that leaves a citation to it in
place: "series_node reference does not resolve". So a Book in case C cannot be revised at all until the
citing elements are in scope. The Studio's whole-Book reconciliation handles this. A CLI targeted revision
must name the citing elements.

## Limits

- **No real author:** the walkthroughs were run by agents. This is not human usability evidence.
- **Mechanical evidence only:** the overview shows what each Book records. It cannot say whether a Book's
  story still works, and a Book can depend on a concept it never recorded.
- **No reverse direction:** a Book revision does not propose Architecture changes. That is the next product
  opportunity, not built here.
- **A long chain stops early:** the Architecture chain walk stops after 40 revisions or at the first
  unreadable version. An older recorded version is then reported as not kept.

## Independent review and dispositions

Three independent reviewers worked on disposable projects: authority and freshness, interaction, and
adversarial workflow.

**Authority (no blockers).**
- **Fixed:** a partial revision of an out-of-date Book gave the current fingerprint to a concept the Book
  already cited without one. Such a concept is now carried forward unrecorded; only a newly cited concept is
  recorded as it is now.
- **Fixed:** a damaged or truncated Architecture history was reported as "not on the current revision
  chain". The chain is now walked by request identity, and says whether it was read whole; when it was not,
  the Atelier says how far behind the Book is "cannot be told".
- **Fixed:** with no working Architecture, every cited concept read "removed". It now reports
  `architecture_unavailable`, and nothing is said about any concept.
- **Fixed:** a damaged Architecture `current.json` made the whole Working Books section unreadable. That
  unguarded read was removed.
- **Fixed:** a record without fingerprints raised in `_freshness`. It is now read, with its references
  unrecorded.
- **Fixed:** older applied revisions claimed `currentness: current` by default. They now report `None`
  (not recorded).

**Interaction.**
- **Fixed:** the applied-revision card counted concepts with changed relationships, while the evidence called
  them unchanged. The evidence now says what a Book's fingerprint covers: name, kind and description, not
  relationships.
- **Fixed:** the atlas reading showed a sentence about "this concept" when no concept was selected.
- **Fixed:** the entry line sat below the fold. It now comes first in the applied-revision card, or directly
  under the atlas summary.
- **Fixed:** opening one Book made the overview long and moved the page. The other Books now shrink to one
  line, and only the folio scrolls.
- **Fixed:** Escape closed the whole view. It now steps back one level, and a concept opened from the impact
  view leads back to it.
- **Fixed:** parser errors were shown to the author. They are now behind "Technical detail".
- **Fixed:** Book 26's evidence and draft named nothing. They now name the Architecture concepts that
  changed since the Book was written but that it does not cite, from the exact version it records; the draft
  asks only to check them.
- **Fixed:** the seeded draft opened at its end. It now opens at its start, in a taller box.
- **Fixed:** repeated caveats are now said once.

**Adversarial (no blockers).**
- **Fixed:** after Apply from the overview, the confirmation was hidden in a closed record. The record now
  stays open, its note is focused, and the announcement says when the Book stays out of date.
- **Fixed:** a waiting partial request on an out-of-date Book gave no warning. It now explains why it cannot
  bring the Book up to date, and why no answer can pass while elements outside it cite a removed concept. It
  offers a whole-Book reconciliation that replaces it.
- **Fixed:** a Book whose own source changed was worded as an Architecture change. Its line, button and draft
  now name the source.
- **Fixed:** an unreadable Architecture chain was reported as "not on the chain" (the same finding as the
  authority review's).
- **Recorded, unchanged:** a damaged Architecture `current.json` reads as "No working Architecture yet" in
  the Atelier. This predates this change.

**Recorded for later:**
- **Long Series:** for very long Series, a compact table would scale better than rows. The overview already
  folds after 8 Books per group, and says "cited by N Books" past four.
- **Source changes:** a Book's changed source items are not named individually, because the owner keeps only
  a digest.
- **Element ids in the draft:** the reconcile draft keeps element ids, for the coding agent's precision.
