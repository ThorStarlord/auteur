# DENSE TRILOGY V1 — SESSION B

## System facts

- Frozen protocol: `2ecb94b3eef3794f51063fe2761b111a7ad2ca05`
- Session-A frozen commit: `d6c722ff781a56447ca7c880f6c3e80351bbe52c`
- Session-B starting commit: `d6c722ff781a56447ca7c880f6c3e80351bbe52c`
- Experiment branch: `experiment/dense-trilogy-architecture-stress-test-v1`
- Experiment worktree: `H:/GithubRepositories/auteur-dense-trilogy-architecture-stress-test-v1`
- Persisted Auteur project: `experiments/dense-trilogy-architecture-stress-test-v1`
- Authorized runtime baseline: `588fb1ef88184be9246d406fd1c90737b7c09cf6`
- Runtime invocation used repository source directly with `PYTHONPATH=src` and
  `python -c "from auteur.cli import main; ..."`.
- The original checkout was not used for story operations.

The isolated worktree was clean at the Session-A starting commit. The first
pre-source probe accidentally used the worktree root instead of the persisted
project path. It returned only project-path/gating errors and opened no story
artifact. That immutable probe is preserved in
`session-b-initial-surface-output.txt`; the correction is documented in
`session-b-pre-source-correction.md`.

## Fresh-context control

This was a fresh Session-B context. No handwritten Session-A summary was used,
and `session-a-evidence.md` was not read. Before the corrected pre-source
snapshot, no raw Book-1 narrative artifact was opened. The corrected snapshot
and exact corrected surface output are:

- `session-b-pre-source-reconstruction-snapshot.md`
- `session-b-pre-source-correction.md`
- `session-b-corrected-initial-surface-output.txt`

The path correction was logged as an `EXPERIMENT` issue; it did not expose
narrative content or contaminate the fresh-context reconstruction.

## Intended surfaced context — category A

Commands, all run against the persisted project, included:

- `series journey accepted-facts <project> --book 2`
- `series journey map <project> --book 2`
- `series journey focus <project> --book 2`
- `series review <project> --book 2`
- after explicit planning intent, the same map/focus/review surfaces again;
  default output was captured before any detail output.

Before planning, accepted history surfaced twelve Book-1 facts: Mara's
accountable-dissident authority; the contested erased coast; divided Admiralty
legitimacy; Mara/Ion conditional alliance; Sela's archive duty; Tamsin's earned
ally status; Nera's active protection; Brann's low-salience reef anomaly; Lio's
copied anomaly; the Ferrymen's strike leverage; disputed winter-convoy safety;
and divided House of Names custodianship.

Before planning, map and Focus were gated. After planning, Continuity Review
and Series Focus surfaced the intent, all three active commitments, all twelve
accepted Book-1 facts, no revision warnings, and no long-range supporting
context. The bounded Map/Focus decision proposal still failed because the
validator requires the exact context items `series-commitment-contested-history`
and `state-change-founding-ledger-exposed`, while the derived context contained
the actual commitments and Book-1 transitions under different IDs.

## Pre-source understanding

The corrected surface established a witness-backed chart, a publicly contested
erased coast, divided Admiralty legitimacy, a conditional Mara/Ion alliance,
active protection for Nera, a dormant reef/deletion anomaly held by Brann and
Lio, and institutional/location pressure around passage and naming. It did not
establish the full cast, relationship paths, faction history, or causal detail
needed for responsible Book-2 architecture. That missing detail motivated the
logged authoritative lookups below.

## Targeted authoritative lookups — category B

1. `series_direction.yaml`: checked the accepted Series promise, pressure, open
   question, and active commitments needed to frame Book-2 intent.
2. `series_identity.yaml`: inspected only Series-level counts and the Book-2
   directional scaffold. It showed trilogy shape, Book-2 complication function,
   national scope, and the broad civic-authority pressure. The Series identity
   contains 16 character arcs, 4 relationship arcs, 4 faction arcs, 7 dependency
   edges, 2 mysteries, 4 setups, 1 thematic arc, and 3 recurring symbols.
3. `book_1_direction.yaml`: checked the Book-1 identity and its accepted
   commitment linkage to understand the prior directional contract.
4. `.auteur/.../workflow/book-planning-intent/book-2.yaml` and derived
   `book-2-context.yaml`: checked what the planning workflow persisted and why
   the bounded Map/Focus validator could not match its required context IDs.
5. `repeated-book-2-context.yaml`: inspected the derived pressure-group shape
   to distinguish accepted-history projection from the bounded decision seam.

These were narrow checks after the pre-source snapshot. They did not include
`session-a-evidence.md`.

## Broad manual reconstruction — category C

Broad reconstruction count: **1**.

The full `book_1_outcome.yaml` was inspected after all pre-source surfaces,
planning intent, and continuity observations were frozen, to ground-truth the
twelve accepted Book-1 transitions and assess whether the surfaced facts were
represented. This was substantial earlier-Book inspection and is deliberately
classified as category C, not disguised as a targeted lookup.

## Book-2 planning intent

“Force Mara's witness-backed chart into a national legitimacy crisis while
protecting Nera's testimony and testing whether Ion's conditional alliance can
survive the Admiralty's split.”

The intent was entered through `series journey plan-next-book`. Two relevance
triggers were used because the intent explicitly concerned Mara's authority and
Nera's protection: `B1-01~902166` and `B1-07~8AEB3D`. No relevance token was
selected merely to inflate Focus.

## Continuity Review / Focus assessment

The review correctly identified the planning intent, active commitments, and
twelve accepted consequences. It preserved accepted/canonical authority
boundaries and stated that accepted downstream material remains accepted. It
distinguished active commitments from resolved history (none resolved). It did
not surface long-range supporting context, and the bounded Map/Focus path could
not produce its required two-item decision because of the ID/derivation seam.

Important context surfaced correctly: Mara's authority change, the erased coast,
Admiralty legitimacy, Mara/Ion trust, Nera's protection, Brann/Lio anomaly
holders, and institutional/location pressures.

Important context omitted from the tested bounded decision: the required
`founding-ledger-exposed` state item and `contested-history` commitment item as
the exact expected context IDs; richer SeriesIdentity arcs and dependencies did
not appear in Continuity Review's long-range section.

Irrelevant overload: none materially observed. The twelve surfaced facts were
all plausibly relevant to the stated intent.

## Failure classification and representation distinction

- `INTEGRATION_PROJECTION` / `WORKFLOW`: the bounded Book-2 decision requires
  two exact derived context IDs that are not produced by the current accepted
  Book-1 projection. The meanings exist in accepted direction/outcome and in
  derived context under other IDs; this is not evidence of a missing narrative
  concept.
- `SELECTION`: not demonstrated. The relevant accepted facts were selected and
  surfaced by Continuity Review and Focus.
- `REPRESENTATION`: not demonstrated. Existing direction, transition,
  commitment, dependency, mystery, setup, and arc representations were
  sufficient to encode the Book-2 architecture.
- `CURRENT_STATE`, `IDENTITY`, `REASONING`, `AUTHORITY`, and `OVERLOAD`: no
  consequential failure demonstrated in this session.
- `EXPERIMENT`: the initial wrong project-root probe was logged and preserved;
  it did not expose story content.

## Book-2 architecture and narrative facts

Accepted Book-2 Direction: **The Returning Coast**, a national-scale
complication in which recognition of erased communities becomes a struggle over
citizenship, repair, and shared authority.

Accepted Book-2 Realization Bundle: twelve architecture-level transitions,
including:

- Mara changes from accountable dissident to contested civic witness.
- Ion becomes a suspended intermediary; Mara/Ion changes from conditional
  alliance to costly mutual reliance.
- Nera's protected obligation becomes a protected witness with a public claim.
- Sela releases contested names; the House of Names becomes plural
  custodianship.
- Admiralty legitimacy becomes publicly conditional; the Ferrymen become a
  recognized negotiating bloc.
- The erased coast becomes provisionally recognized communities and the winter
  convoy becomes jointly audited.
- Brann's low-salience bell report corroborates Lio's copied deletion mark;
  Brann and Lio's anomaly thread becomes endangered public evidence.

The Book materially evolves the Series through character authority, relationship
path, institutional legitimacy, location/community status, knowledge asymmetry,
delayed witness protection, dormant-anomaly reactivation, and cross-Book causal
consequences. The three Series commitments remain unresolved, preserving live
pressure for a later Book.

## Accepted and derived artifacts

Accepted through existing Auteur mechanisms:

- `.auteur/series/vertical-slice/accepted/book-2-direction.yaml`
- `.auteur/series/vertical-slice/accepted/realization/realization-bundle-book-2-returning-coast-outcome.yaml`

Working inputs/evidence:

- `session-b-book-2-direction.yaml`
- `session-b-book-2-outcome.yaml`
- `session-b-evidence.md`

Derived/rebuilt artifacts:

- `.auteur/series/vertical-slice/derived/canonical-state.yaml`
- `session-b-series-diagnostics.json`
- `session-b-dependency-graph.yaml`
- `session-b-dependency-graph.mmd`
- `session-b-series-bible.json`

## Validation and diagnostics

- `series validate`: passed.
- `series diagnose`: completed with 3 warnings and no errors: unresolved
  payoffs for `erased-coast` and `bell-reef`, plus `copied-anomaly` still
  unresolved past its Book-2 deadline. These are expected open-pressure
  evidence, not silently repaired.
- `series graph`: completed; YAML and Mermaid outputs written.
- `series bible`: completed.
- accepted facts through Book 3 horizon: correctly listed 24 facts through
  Book 2; no Book-3 planning was entered.
- `series impact`: completed; no affected downstream artifacts detected.

## Freeze assertions

- Production source code and schemas changed: **NONE**.
- Session-A frozen artifacts were not rewritten; new state was created through
  the existing accepted/proposal mechanisms and derived rebuilds.
- Chapter outlines: **NONE**.
- Scene outlines: **NONE**.
- Prose: **NONE**.
- Book-3 planning intent: **NONE**.
- Book-3 realization: **NOT STARTED**.
- Book-3 was not designed.

Session-B is frozen at the commit recorded after this evidence file is added.
No merge, implementation PR, Session C, or production repair is authorized by
this record.
