# DENSE TRILOGY NARRATIVE ARCHITECTURE STRESS TEST V1 — SESSION C EVIDENCE

## Freeze identity and controls

- Frozen protocol commit: `2ecb94b3eef3794f51063fe2761b111a7ad2ca05`.
- Session-A frozen commit: `d6c722ff781a56447ca7c880f6c3e80351bbe52c`.
- Session-B frozen commit: `67e49d9664627d6d2d0de7bf5eb49d6d8162618d`.
- Session-C starting commit: `67e49d9664627d6d2d0de7bf5eb49d6d8162618d`.
- Expected branch: `experiment/dense-trilogy-architecture-stress-test-v1`.
- Expected linked worktree: `H:\GithubRepositories\auteur-dense-trilogy-architecture-stress-test-v1`.
- Persisted project used for every story command: `experiments/dense-trilogy-architecture-stress-test-v1`.
- Workspace gate: PASS. HEAD matched Session B; HEAD descended from Session A; worktree was clean before Session-C artifacts; project and `.auteur` state existed; `src` had no diff from authorized baseline `588fb1ef88184be9246d406fd1c90737b7c09cf6`.
- Runtime: repository source via `PYTHONPATH=src`; import verification under that environment resolved `auteur` to the Session-C worktree source.
- Fresh-context control: PASS for the story phase. No Session-A or Session-B evidence/summary file was read. No parallel story sub-agent was used.
- Session-A evidence read: NO.
- Session-B evidence read: NO.
- Revision stress: NOT STARTED.

## System facts

### Pre-source intended surfaces (category A)

Before raw story inspection, `series journey accepted-facts <project> --book 3` surfaced 24 accepted facts: 12 Book-1 and 12 Book-2 facts. The compact surface exposed Mara Venn, Ion Vale, Nera Quill, Sela Orun, Tamsin Rusk, Brann Ede, Lio Marr, the Tidebound Admiralty, House of Names, Ferrymen's Union, erased-coast status, and winter-convoy status. It exposed the Mara/Ion relationship path, Nera's continuing protection obligation, and the Brann/Lio anomaly/evidence thread.

Before planning intent, `journey map`, top-level `focus`, and top-level `review` all gated with explicit Book-3-planning-intent errors. This gate was recorded and not bypassed.

### Pre-source reconstruction

Frozen at `session-c-pre-source-reconstruction-snapshot.md` before raw story inspection. The surfaced history was compact and not materially overloaded, but did not expose detailed causal links, explicit commitments, Book-3 direction, belief asymmetry, or broad cast/faction/location inventory.

### Direction lookup (category B)

After the snapshot, only the Book-3-relevant directional fields were inspected in `.auteur/series/vertical-slice/accepted/series-direction.yaml`. They supplied the Series promise, pressure, open question, and three commitments: `contested-map`, `visible-disagreement`, and `witness-protection`. This was one targeted lookup; the canonical Series file was not used for this lookup.

### Relevance selection and planning

The smallest defensible selected set was:

- `B2-03~FE047F` / `mara-ion-trust`: the Book-2 current relationship state, whose Book-1-to-Book-2 path was explicitly surfaced and needed for a path-dependent Book-3 decision.
- `B2-04~18726E` / `nera-testimony-risk`: the current protected-witness/public-claim obligation, tied directly to the Series witness-protection commitment.
- `B2-10~5ACEFE` / `brann-anomaly-corrobation`: a low-salience Book-1 anomaly that was visibly reactivated as Book-2 corroborating reef-signal evidence.

Intent entered through `series journey plan-next-book`:

> Book 3 must make the republic answerable to erased-coast testimony by deciding whether the reef signal and endangered witness evidence can reopen the official map, while Mara and Ion's costly mutual reliance is tested by the food-route and legal-identity consequences of shared authority.

### Continuity / map / focus after intent

Default and detail variants showed:

- the current intent;
- all three active Series commitments;
- current Book-2 states for Mara/Ion, Nera, and Brann;
- Book-1 history as historical context;
- superseded states distinguishable in detailed map output;
- three persistent pressure groups (`contested-map`, `visible-disagreement`, `witness-protection`);
- provenance for Series direction, Book directions, and accepted realization bundles;
- no continuity warnings before Book-3 realization.

The repeated Focus surface accepted caller-supplied bounded seeds and returned recommendations without making them canon. A seed-shape error (`description` instead of required `summary`/`tradeoff`) and an initial misuse of `--choice` were corrected before recording the successful probe results. These are WORKFLOW/EXPERIMENT observations, not product architecture failures.

### Decision probes

1. **Relationship path history** — Question: should Book 3 bind Mara and Ion's costly mutual reliance to a public map correction, separate their institutional exposure, or defer? Category A evidence supplied Book-1 conditional alliance and Book-2 costly mutual reliance; current state alone would be insufficient. Focus recommended `bind-testimony`, explaining that the path from alliance to shared risk must affect civic authority. The recommended choice was recorded as a non-canonical planning action.

2. **Obligation / knowledge** — Question: should Book 3 protect Nera while testing the reef evidence, disclose and risk the witness, or defer? Category A evidence supplied Nera's Book-1 active protection, Book-2 protected public claim, and Brann's reactivated evidence. Current state alone would not preserve the delayed obligation's origin. Focus recommended `protect-and-test`, explicitly keeping Nera protected while testing the map evidence.

3. **Supporting character / old thread** — Question: should Brann and Lio's anomaly/evidence custody become decision-critical, remain background, or defer? Category A evidence supplied Brann's low-salience Book-1 anomaly, Book-2 corroboration, and Lio's changed custody risk. Current state alone would not explain why the supporting thread deserves renewed relevance. Focus recommended `elevate-custodians`.

The surface supported all three probes and did not surface an important missing item that prevented the decisions. Lio was not selected as a separate trigger, but his history was visible in the accepted context and was used in the supporting-character probe.

## Narrative facts and worker actions

### Ground-truth comparison (post-freeze)

After all pre-source, intent, continuity, map/focus, and probe observations were frozen, broader authoritative inspection was performed. The canonical Series representation confirms a 16-character recurring cast, four meaningful factions, multiple locations/systems, the erased-coast and bell-reef mysteries, the Nera obligation, and the Mara/Ion path dependency. Accepted Book-2 realization confirms the detailed transitions behind the surfaced facts.

Broad manual reconstruction count: **1 event**, post-freeze only. It consisted of reading the canonical `series_identity.yaml`, accepted Book-2 direction/realization, and derived state/map artifacts to compare surfaced behavior with ground truth. It was not hidden, and no previous worker evidence was read. Source-code inspection was operational and not counted as story reconstruction.

### Book-3 architecture

Book 3, **The Common Horizon**, was entered and accepted through normal Auteur authority. Its accepted realization contains 12 architecture-level transitions and no chapters, scenes, or prose. Major pressures materially inherit earlier consequences: Mara/Ion public interdependence; Nera's protected living account; Brann's delayed anomaly; Lio's evidence custody; Admiralty legitimacy; House-of-Names plurality; Ferrymen route governance; erased-coast civic status; winter-convoy audit; and the bell-reef delayed setup. The intended result is provisional shared governance that preserves visible disagreement rather than producing total closure.

The accepted Book-3 artifact was `realization-bundle-book-3-common-horizon-outcome`, with no Series commitment marked resolved. That preserves the experiment's intentionally provisional ending.

## Findings by failure class

- REPRESENTATION: none demonstrated. Existing accepted transitions, commitments, current-state values, mysteries, and dependencies represented the tested meanings.
- PERSISTENCE: none observed. Accepted Book-1 and Book-2 history survived into the surfaced context and canonical rebuild.
- INTEGRATION_PROJECTION: bounded finding. `series diagnose` on canonical `SeriesIdentity` still warns that `erased-coast` and `bell-reef` have no actual payoff book and that `copied-anomaly` is unresolved, although accepted lived-history carries the Book-3 reef/map consequences. The canonical Series path and accepted-history path remain divergent; no bridge was implemented.
- CURRENT_STATE: no error observed. Rebuilt canonical state has 14 values and zero conflicts, with Book-3 current transitions applied.
- IDENTITY: no systemic confusion observed. The ground-truth cast remains 16 recurring characters; the tested surfaced subset stayed identifiable.
- SELECTION: bounded observation only. The selected triggers reached the Book-3 context; several nonselected Book-2 facts were explicitly marked irrelevant or dormant rather than silently treated as current.
- OVERLOAD: none observed. Default accepted-facts and review outputs remained manageable; detailed map output is large but usable for this single case.
- REASONING: no incorrect product-derived connection demonstrated in the three probes. Creative outcomes were author decisions, not automated truth claims.
- EXPLANATION: probe recommendations included relevant rationale and tradeoffs. No material explanation failure observed.
- AUTHORITY: no derived output was accepted as canonical; decisions remained non-canonical and Book-3 direction/realization used proposal/acceptance paths.
- WORKFLOW: bounded errors were recorded and corrected: seed schema mismatch, recommendation-choice syntax, realization source reference, and a null-before transition for an uninitialized bell-reef field.
- EXPERIMENT: the initial mistaken output location was cleaned through exact generated-file deletion; all later project outputs used the verified persisted project directory. No contamination resulted.

## Final system state

### Accepted / canonical artifacts

- `.auteur/series/vertical-slice/accepted/book-3-direction.yaml`
- `.auteur/series/vertical-slice/accepted/realization/realization-bundle-book-3-common-horizon-outcome.yaml`
- `.auteur/series/vertical-slice/accepted/realization-revisions/realization-bundle-book-3-common-horizon-outcome/000001.yaml`
- `.auteur/series/vertical-slice/derived/canonical-state.yaml`

Prior accepted Book-1 and Book-2 artifacts were preserved unchanged.

### Derived artifacts

- `.auteur/series/vertical-slice/derived/global-map-book-3.yaml` — rebuilt with 27 entries and 3 pressure groups for the Book-3 planning horizon.
- `series/diagnostics/series_report.json`
- `series/dependency_graph.yaml`
- `series/dependency_graph.mmd`
- `series_bible.json`

### Validation and diagnostics

- `series validate`: PASS — SeriesIdentity valid.
- `series diagnose`: completed with three warnings: missing actual payoff markers for `erased-coast` and `bell-reef`, and unresolved `copied-anomaly` deadline. These are preserved evidence, not repaired.
- `series graph`: completed; YAML and Mermaid graph written.
- `series bible`: completed.
- `series impact`: no affected accepted artifacts; no review order required.
- canonical state: state version 3; 14 current values; 3 applied realization bundles; zero conflicts.
- continuity review: no revision/continuity warnings; all three Books appear in Series Direction impact; accepted downstream material remains accepted.
- status: the generic project status reports missing StoryIdentity/blueprint because this experiment uses the Series vertical-slice artifacts; this is a product-surface boundary observation, not a trilogy-state failure.

## Invariants and stop

- Production code/schema changes: NONE.
- Chapters: NONE.
- Scenes: NONE.
- Prose: NONE.
- Book-1 revision: NOT STARTED.
- Extraction, ontology, and scale implementation: NONE.
- Previous accepted history silently rewritten: NO.
- Revision stress: NOT STARTED.
- Primary normal-accumulation evidence: FROZEN by this file and its supporting artifacts.
- Session status: FROZEN.
- Required next action: end this coding-agent chat; return the clean trilogy result to the owner/controller; do not start revision stress.
