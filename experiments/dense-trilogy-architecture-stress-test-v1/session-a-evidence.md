# Dense Trilogy Narrative Architecture Stress Test V1 — Session A Evidence

## System facts

- Frozen protocol commit: `2ecb94b3eef3794f51063fe2761b111a7ad2ca05`.
- Frozen protocol ref: `origin/docs/dense-trilogy-architecture-stress-test-v1`.
- Authorized runtime baseline: `588fb1ef88184be9246d406fd1c90737b7c09cf6`.
- Original checkout: `H:/GithubRepositories/auteur`, branch `main`, HEAD
  `5f6247d633f6699a773033d37904cb2ff019cc79`; dirty before work began with
  pre-existing untracked `.codex/`, `.reasonix/`, qualification evidence,
  `reasonix.toml`, and evaluation scripts. It was not modified.
- Experiment worktree: `H:/GithubRepositories/auteur-dense-trilogy-architecture-stress-test-v1`.
- Experiment branch: `experiment/dense-trilogy-architecture-stress-test-v1`.
- Starting experiment HEAD: `588fb1ef88184be9246d406fd1c90737b7c09cf6`.
- Parallel story sub-agents: none.
- Scope adopted: architecture only; no Books 2/3 realization, chapters, scenes,
  prose, production changes, schema changes, ontology, extraction, or scale work.

## Representation-plane audit

| Information family | Canonical / authoritative owner | Accepted-history owner | Derived / consuming surface | Session-A observation |
| --- | --- | --- | --- | --- |
| Universe constraints | `UniverseIdentity` | none | series validation/diagnostics | Existing plane confirmed; unused because fixture needed no universe contract. |
| Whole-series architecture | `SeriesIdentity` | none | validate, diagnose, graph, bible | Rich canonical path stores trilogy plans, arcs, mysteries, dependencies, setups, and themes. |
| Sparse series direction | `SeriesDirection` accepted artifact | accepted Series Direction | journey, map/focus/review prerequisites | Separate accepted plane; it does not directly ingest `SeriesIdentity`. |
| Book direction | `BookPlan` / `BookDirection` | accepted Book Direction | journey and planning context | Book 1 accepted through proposal/acceptance. |
| Book outcome/state transitions | `AcceptedRealizationBundle` / `StateTransition` | accepted realization bundle | canonical state, Global Map, history | Book 1 accepted atomically and rebuilt successfully. |
| Current state/history/relevance | accepted bundles | accepted-history store | `CanonicalState`, Global Map, repeated context, Focus | Book-1 endpoint produced fresh canonical state and Global Map. |
| Continuity review/planning intent | `BookPlanningIntent` plus `SeriesProductizationService` | accepted artifacts and derived reports | review/focus | Book-2 review/focus require explicit planning intent and were not entered in Session A. |

The frozen audit is confirmed with one qualification: the current productization
path composes accepted-history artifacts through the vertical-slice service and
does not directly consume the rich `SeriesIdentity` narrative collections. This
is an integration/projection observation, not a representation failure.

## Narrative facts

### Series

**The Cartographers of Salt** is an original mystery trilogy about the Tidebound
Republic, whose usable maps depend on erasing inconvenient coast settlements.
The intended experience moves from belonging and wonder through institutional
fracture toward provisional interdependence.

### Cast

The 16 recurring characters are:

- Protagonist: Mara Venn, surveyor turned accountable dissident.
- Other main characters: Ion Vale, Sela Orun, Tamsin Rusk, Osric Pell, and Vey Nhal.
- Supporting characters: Rhea Sorn, Cal Dorr, Jori Pell, Nera Quill, Brann Ede,
  Lio Marr, Fen Aster, Ysolde Kett, Pavel Ro, and Uma Sen.

The supporting cast carries duties, loyalties, institutional roles, knowledge,
and delayed consequences; it is not a name-only roster.

### Factions / institutions

Tidebound Admiralty; Marsh Commons; House of Names; Ferrymen's Union.

### Important locations

The salt marsh and its erased settlements; the drowned bell reef; the Admiralty
chart office; the House of Names archive; the winter convoy channel.

### Persistent pressures / subplots

The erased-coast mystery; the bell-reef signal; Nera's witness-protection oath;
Lio's copied archive deletion; Mara and Ion's trust path; Sela's split archival
duty; the Ferrymen's winter strike leverage; and the Admiralty's declining
legitimacy.

### Future direction

Books 2 and 3 contain only directional scaffolding: function, target experience,
broad engine, scope, and deliberately non-detailed answers. No later event chain,
betrayal, revelation, relationship outcome, supporting-character role, or
subplot resolution was pre-solved.

### Book 1 architecture and lived consequences

Mara discovers that the sanctioned channel chart erases inhabited settlements.
She signs a witness-backed counter-chart, making the coast publicly contested;
Ion's report splits the Admiralty; Sela opens a counter-ledger; Tamsin refuses
the false route; Nera actively protects a fever survivor; Cal creates a winter
strike threat; and the House of Names divides. Brann's bell-reef report and
Lio's copied deletion are intentionally preserved as lower-salience knowledge.
Book 1 ends with the republic's geography, legitimacy, and personal alliances
meaningfully changed, while the two mysteries and witness obligation remain open.

## Worker actions and command evidence

Commands were run from the isolated worktree with `PYTHONPATH=src` so the live
code came from the exact baseline checkout. The bare `auteur` executable was
identified as an unrelated editable-worktree environment and was not used for
the evidence run.

- `python -m auteur.cli series validate .../series_identity.yaml` — PASS.
- `python -m auteur.cli series diagnose .../series_identity.yaml --output .../series_diagnostics.json` — PASS; 3 warnings (two unresolved future mysteries and one Book-2-deadline setup), no errors.
- `python -m auteur.cli series graph .../series_identity.yaml --output .../dependency_graph.yaml` — PASS; YAML and Mermaid graph written.
- `python -m auteur.cli series bible .../series_identity.yaml --output .../series_bible.json` — PASS.
- `journey propose-series` / `accept-series` — PASS; accepted artifact revision 1.
- `journey propose-book` / `accept-book` — PASS; accepted Book 1 Direction revision 1.
- `journey propose-outcome` / `accept-outcome` — PASS after correcting an
  initially unsupported `before` state; the rejected attempt is workflow
  evidence that canonical transitions cannot invent prior state.
- `series review --book 2` — expected refusal: explicit Book-2 planning intent required.
- `series focus --book 2` — expected refusal: Book planning intent required.
- `series impact` — PASS; no stale downstream artifacts detected.

## Artifacts

Canonical / author-edited:

- `series_identity.yaml`
- `.auteur/series/vertical-slice/accepted/series-direction.yaml`
- `.auteur/series/vertical-slice/accepted/book-1-direction.yaml`
- `.auteur/series/vertical-slice/accepted/realization/realization-bundle-book-1-sounding-line-outcome.yaml`

Proposed / provenance-bearing inputs:

- `series_direction.yaml`
- `book_1_direction.yaml`
- `book_1_outcome.yaml`
- `.auteur/series/vertical-slice/proposals/**`

Derived / rebuildable:

- `series_diagnostics.json`
- `dependency_graph.yaml`
- `dependency_graph.mmd`
- `series_bible.json`
- `.auteur/series/vertical-slice/derived/canonical-state.yaml`
- `.auteur/series/vertical-slice/derived/global-map-book-2.yaml`

The accepted Book-1 realization contains 12 state transitions. Canonical state
is version 1 with no conflicts; the Global Map is fresh, clear, and references
the accepted Series Direction, Book Direction, and realization revision.

## Interpretation and limits

- Representation is sufficient for this Session-A fixture's tested families.
- The rich canonical Series path is not directly projected into the accepted
  continuity-review path; this remains a candidate `INTEGRATION_PROJECTION`
  observation for later evaluation, not a demonstrated defect in Session A.
- Broad manual reconstruction: not applicable; Session A created the seed and
  Book 1 and did not simulate a fresh later-book worker.
- No Book-2 or Book-3 conclusions are permitted from this evidence.
- No production source or schema files changed.
- No chapter outline, scene outline, or prose artifact exists.
