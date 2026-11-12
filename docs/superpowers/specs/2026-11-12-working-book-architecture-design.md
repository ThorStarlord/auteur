# Working Book Architecture: design

**Status:** provisional engineering design for owner review. Not canonical. It does not amend the five semantic layers, the accepted `SeriesIdentity`, `BookPlan`, `BookDirection`, realization, or Global Map contracts, and it does not canonize any Book 24 material.
**Date:** 2026-11-12. **Baseline:** `origin/main` at `8b53b32f` (PR #556, the bridge `apply-review` lifecycle).
**Evidence:** [worked example, probe, and challenge reconciliation](../../qualification-evidence/working-book-architecture-design-20261112/README.md). Claims below are marked **verified** (read in source or measured by the probe), **demonstrated** (measured on the Book 24 fixture), **assumed**, or **decided** (provisional engineering choice).

## 1. The capability

A **Working Book Architecture** is a provisional, Book-scoped construction. It holds the detailed function of one Book: what the Book is for, the conditions it inherits, the engines that drive its conflict, the agents who want things, the choices and their costs, its local closure, its consequences for the Series, its provisional assumptions, its rejected alternatives, and what remains unknown. It may develop from the Whole-Series working architecture, but it is never an accepted Book plan and never canon.

The product gap is this. A Series-level working architecture can hold mechanisms, but **Book 24 showed it cannot hold a Book's function**. The fresh agent produced an 11-part, roughly 17,000-character Book function, and the Studio candidate kept two nodes, eight links, one emotion target, and a summary sentence. The rest was lost into prose, and the Series candidate had no room left for it (**demonstrated**, see the worked example). The gap is a durable, revisable, provenance-tagged Book artifact that a fresh agent can resume without the original conversation.

## 2. Verified existing capability

Existing owners already satisfy parts of this. Nothing here is a missing feature in the abstract.

| Capability | Where (verified) | Satisfies | Does not satisfy |
|---|---|---|---|
| Series working architecture | `ArchitectureCandidate` (`src/auteur/beginner/studio_architecture.py`, class at line 154) | Series engines, threads, phases, emotion targets, open questions, as working material | Book scope; per-element provenance (only emotion targets have it); Book-sized prose |
| Working-revision lifecycle | `prepare_architecture` (952), `complete_architecture` (1026), `apply_architecture_review` (1101), `_root` (234, `store.directory / "architecture"`) | Requests, a latest-request pointer that supersedes older requests, review before apply, freshness fingerprints, a filesystem lock, `resume` | Any Book-specific schema, diff, or packet |
| Host-agent request and response | `src/auteur/host_agent.py` (`HostAgentRequest` 64, `load_host_agent_request` 137, `validate_host_agent_response` 187, `write_host_agent_response` 209) | Generic request and response records shared with other operations | Nothing Book-specific |
| Accepted Series plan | `SeriesIdentity` (`src/auteur/series/models.py`, 213); `DependencyType` (23) with ADR 013 semantics | Accepted cross-book dependency edges; typed relation vocabulary (`sets_up`, `pays_off`, `depends_on`, `pressures`, `contradicts`, `transforms`) | Sparse Book sequences: `_validate_series_shape` (240) requires book numbers to be contiguous from 1 for every series type (257–259) |
| Accepted per-Book plan | `BookPlan` (58) | Book number, function, one central engine, carried threads as strings | Multiple engines; detail beyond fixed fields; provenance; any working status (`extra="forbid"`) |
| Accepted Book identity | `BookDirection` (`vertical_slice_models.py`, 80) with a full `StoryIdentity` and `series_commitment_ids`; `propose_book_direction` (`vertical_slice_service.py`, 161) and `accept_book_direction` (189) | An acceptance path with source-revision equality checks. Its author gate is a CLI call that passes a constant author label (`src/auteur/series/cli.py`, 289–291), so it is an invocation, not a confirmation | Working use: acceptance is canonical, and the identity object is heavy |
| Carry-forward context | `derive_book_context` (1233); `CarryForwardItem` (`vertical_slice_models.py`, 440) | Commitment carry-forward from accepted Book N−1 | State changes come only from `_BOOK_CONTEXT_STATE_TRANSITIONS` (service lines 66–77), a table hard-coded to the `archive-of-lies` fixture |
| Accepted history and focus | `GlobalMapSnapshot` (`vertical_slice_models.py`, 255), `realization_impact` (service 1000), `series_impact` (1056) | Derived continuity views; health, freshness and semantic-impact reports | A store for prospective Book function |
| Lifecycle and provenance | `Lifecycle` (`src/auteur/provenance/store.py`, 18: draft, proposed, accepted, replaced, rejected, archived); `ArtifactStore.accept` (346) | Authority states; dependency records with revisions and hashes | Non-accepted write paths are not used by the Series slice |
| Source references | `ArtifactRef`, `AcceptedFactRef` (`vertical_slice_models.py`, 17, 24) | Stable references to accepted revisions and facts | References to working elements |
| Staleness vocabulary | `docs/revision-staleness-contract.md`; `realization_impact` returns `health`, `freshness`, `semantic_impact` | A three-dimension vocabulary already used by code | Working artifacts |
| Provenance labels | `EmotionTarget.provenance` (`studio_architecture.py`, 84): `author_declared` or `agent_proposed` | The labelling pattern | Enforcement (see gap G8) |

## 3. Demonstrated gaps

Each gap comes from the worked example (`probe-output.json`) or from direct source reading, as noted.

- **G1. No Book scope.** The schema has no Book node. Book 24 used a free-text scope string (`book 24`) on two nodes. *(verified: `ArchitectureNode.scope` is free text, max 100 characters.)*
- **G2. Caps reached.** Phase narrative is capped at 1000 characters (the Arc V phase is at the cap). Open questions are capped at 16 (the candidate has 16). Summary is capped at 3000. Node summary is capped at 2000 (the largest Book 24 node is 1559). *(verified against the schema.)*
- **G3. Provenance is not recoverable from prose.** 27 of 74 Book 24 items carry no provenance tag in the source. *(demonstrated.)*
- **G4. Reversal conditions are mostly missing.** Only 2 of 10 provisional assumptions state a reversal. *(demonstrated.)*
- **G5. Consequences are not typed.** The 8 Book-to-Series links are free text (≤120 characters). The craft-mark trace reaches 14 Series nodes through links but **none** of the three finale alternatives, though section 8 says the record bears on the finale. *(demonstrated.)*
- **G6. Decision pointers do not resolve.** The Book text points to 13 distinct `01 §…` locations in a prose document that is not in the artifact. Series open questions have no identifiers. *(demonstrated.)*
- **G7. Some named characters have no candidate source.** `Idrun Sallow` and `Oona Brisk` appear in neither the Series candidate nor the Book candidate. Their sourcing is prose-only. *(verified by grep.)*
- **G8. Authority gap.** An agent response can declare `author_declared` provenance and it is accepted. The probe passed a candidate with that label through the production validator. The label is documented as author-only but nothing enforces that. *(demonstrated: `authority_probe`.)* The Increment 0 guard covers host-agent responses that pass through `complete_architecture`. It does not cover direct edits to the stored candidate file.
- **G9. A fixture special case in production code.** `_BOOK_CONTEXT_STATE_TRANSITIONS` hard-codes one fixture series and Book, against the repository's no-special-cases invariant. *(verified.)*
- **G10. Revision narration in the Series summary.** The Book 24 candidate appends a revision note to the whole-Series summary. Provenance is carried in prose. *(verified: the summary extends the W6 summary.)*
- **G11. Sparse Books are invalid in the accepted schema.** Working Book development cannot be represented as a valid `SeriesIdentity`, because numbering must be contiguous. *(verified, see §2.)*
- **G12. The acceptance gate is a constant.** `accept-book` calls `accept_book_direction` with a fixed author label (`src/auteur/series/cli.py`, 289–291), and `ArtifactStore.accept` defaults to `author` (`src/auteur/provenance/store.py`, 352). An author action here means running a command. The design inherits this and does not strengthen it. *(verified.)*

## 4. Options compared

The criteria are the twelve in the mission. Each assessment is qualitative and grounded in the items above.

| Criterion | A. Extend the Studio candidate | B. Extend `BookPlan` / `BookDirection` | C. Working Book artifact composed with existing owners |
|---|---|---|---|
| 1. Faithful preservation | Poor. Caps (G2), no Book scope (G1), two nodes survived of eleven sections | Poor. One central engine, fixed fields, no provenance | Good, measured: 11 of 11 sections, all id references resolve, coverage ≥ 0.955 |
| 2. Reuse | High. Lifecycle is already there | Medium. Accepted validators are reusable, working use is not | High. Lifecycle, host-agent, typed vocabulary, staleness and refs are reused |
| 3. Working vs accepted | Blurred: the candidate is working, but it grows into a de facto plan | Blocked: acceptance is the only path, and sparse working use is invalid (G11) | Explicit: acceptance only through the existing propose/accept path |
| 4. Independent Book revision | Poor. Inferred from the lifecycle: any Book change re-emits the whole candidate (34 nodes, 42 links) | Poor. A Book change is a Series-schema change | Good. A change targets one Book artifact and its own elements |
| 5. Cross-Book consequence | Only as untyped links | Good for accepted dependency edges only | Medium. Typed Book-to-Series edges now; Book-to-Book in Increment 4 |
| 6. Reversible proposals | Medium. Supersession works, but the unit is the whole Series | Low. Accepted contract | Good. Elements carry status and can be rejected without touching the Series |
| 7. Fresh-agent resume | Medium. A large candidate resumes, but Book detail is not addressable | Medium | Good for orientation (measured 10,055 characters). Insufficient for revision on its own (see §5.7) |
| 8. Series compatibility | Native | Native but constrained | Native. The Book artifact references Series nodes and never writes them |
| 9. Implementation cost | Lowest | Highest, and it changes accepted contracts | Medium. One new schema and validator, plus the extracted pointer and record handling. The lock and atomic writer are reused as they are |
| 10. Duplication risk | Low | High, since BookPlan and the Book artifact would overlap | Controlled. Owners are kept distinct (§5.1); the lifecycle is extracted, not copied |
| 11. Author usability | Familiar, but dense | Hard to read as prose | Better: sections map to the author's questions |
| 12. Path to Chapter and Scene | Would grow the Series candidate | Would grow accepted contracts | Can add a Chapter-scope artifact later, referencing the Book artifact |

**Decision.** C. A and B fail on preservation and on working authority, which are the two requirements the mission treats as primary. A cannot represent the Book without the caps being raised (measured: Book 24 needed new nodes because the phase narrative was at its cap). Raising the caps would enlarge every Series revision; that cost is inferred, not measured. B cannot represent sparse working development without weakening accepted validation, which the mission forbids.

## 5. The selected design (provisional)

### 5.1 Ownership

| Owner | Owns | Does not own | Relation to the Book artifact |
|---|---|---|---|
| Studio working Series architecture | Series-level engines, threads, phases, emotion targets, Series open questions, as working material | Book detail; accepted story authority | Referenced by node id. Never written by a Book operation |
| **Working Book Architecture (new)** | One Book's function, inherited conditions, Book-level engines, agents, choices, local closure, Series consequences, assumptions, alternatives, unresolved items | Accepted identity, accepted realization, prose, chapters, scenes | Builds on the Series working architecture. Acceptance is never performed by it |
| Accepted Series Direction and accepted `BookDirection` | Accepted Series and Book identity and commitments | Working detail | Receives a proposal drafted from the working artifact, then the author accepts it. Apply never does this |
| Accepted realization and Global Map | Accepted history, current state, derived views | Prospective function | Read-only inputs to inheritance in Increment 3 |
| Cross-cutting | Lifecycle vocabulary, `ArtifactRef`, typed relation vocabulary, staleness dimensions | Content | Used as they are. No new authority system |

**Placement.** The module that owns Book-scope planning is `auteur.series`, next to `BookDirection`. The lock (`_FilesystemLock`, `src/auteur/beginner/persistence.py`) and the atomic JSON writer (`_atomic_json_write`, `src/auteur/host_agent.py`) are already shared helpers, so the Book artifact uses them directly. What is extracted from `studio_architecture.py` into a neutral module, `auteur.working_revision`, is smaller: the latest-request pointer and the request, review and current handling around `prepare_architecture`, `complete_architecture` and `apply_architecture_review`. The artifact's records are stored under the canvas directory, `architecture/books/<n>/`, because its freshness depends on the canvas's working Series candidate and it must share that canvas's lock. **Decided**, with the reasoning in §4.

### 5.2 Artifact identity (7.1)

- **Identity.** `(canvas_id, book_number)` names the artifact. Its revision is recorded per apply, as the Studio candidate records its request.
- **Series association.** Each request records `base_series`: the Studio candidate's `request_sha256` at prepare time, and a fingerprint of each Series node the Book references. Series identity is therefore a recorded lineage, not a copied object.
- **Revision and source identity.** Each apply records the request SHA, the prior request SHA, the author-source fingerprint (vision and working items), the intention fingerprint, the design-guidance fingerprint, and the artifact content SHA-256. These are the same fingerprints the Studio lifecycle already computes, plus the Series-node fingerprint.
- **Locating the current version.** `book-resume --book N` reads `architecture/books/<n>/current.json`. A fresh process needs only the canvas and the book number.

### 5.3 Creative content (7.2)

The artifact is a structured record with one list per source section. Each element has a stable id, a provenance label, verbatim prose, and machine-readable references. **Schema v1 (decided):**

| Source section | Structured fields (stable id, provenance) | Verbatim prose | Outside this artifact |
|---|---|---|---|
| 1. Question and pressure | `function.question`, `function.pressure`; `function.reader_experience_refs` (typed references to Series `rx_*` nodes; no new free-text field) | Yes | Series reader-experience nodes, by reference |
| 2. Inherited conditions | `inherited[]` with refs and provenance (7 items) | Yes | Accepted facts (Increment 3) |
| 3. Engines and interaction | `engines[]` with `condition`, `choice`, `consequence`, `changed_state`, `new_possibility` (4 blocks); typed `transforms` edges between engines and Book elements | Yes | Series engine nodes, by reference |
| 4. Agency | `agents[]` with motive, planned constraints, refs, and `name_source` (8 items). Structure-level planning, not character commitments (see §5.4) | Yes | Character commitments (Identity owner) and character instances (other operations) |
| 5. Choice and transformation | `choice` with three `options`, `chosen` (agent-proposed), `costs_kept_visible[]`, `transformation` | Yes | None |
| 6. Local resolution | `local_resolution[]` with `closure` flag and provenance (5 items) | Yes | The Right's final condition (author-reserved) |
| 7. Changes to the Series | `series_consequences[]` with kind and typed edges (6 items) | Yes | Series node summaries, by reference |
| 8. Later possibilities | `later_possibilities[]` with kind (`enabled` or `closed`) and a typed target (**none in the probe**, gap G5) | Yes | Books 25 and later, not written here |
| 9. Assumptions | `assumptions[]` with id (P1–P10), `reversal`, provenance (10 items) | Yes | None |
| 10. Alternatives | `alternatives[]` with status `hypothetical` and a rationale (five alternatives and the closing rationale paragraph) | Yes | None |
| 11. Unknowns | `unresolved[]` (6 items) and `open_author_decisions[]` referencing Series open-question ids | Yes | The prose 01 document, not an artifact |

**Limits (decided).** No cap on prose length, because a cap destroys the content the artifact exists to hold. Sanity bounds only, for example 8000 characters per element, as a guard against runaway output. The whole artifact is not capped. The resume packet is bounded by selection instead (§5.7).

**Validation (decided).** The validator enforces: unique ids; every typed reference resolves against the referenced Series revision; provenance uses only the agreed enum, and `unlabelled` is an ingest state that a schema write may not carry; an agent response cannot declare `author_declared` (G8); each agent-proposed assumption states a reversal condition; decision references identify a Series open question by its index and the SHA-256 of its text, both checked against the referenced Series revision (§8); agents create no character commitments, and each named agent carries a `name_source` pointing to the Story Vision, the Series candidate, or the accepted Identity; and the artifact's typed edges use the existing `DependencyType` vocabulary.

**Migration note.** Under these rules, the Book 24 candidate as written would fail on the eight assumptions without reversals and on the 13 unresolvable decision pointers. The design does not relax the rules to admit it. A revision must supply the missing reversals and resolve the pointers. This is the intended behaviour: the gap is then visible instead of silently stored.

### 5.4 Dependencies (7.3)

| Dependency | Representation | Why |
|---|---|---|
| Series engines, threads, phases, emotion targets | Typed edge to a Series node id, validated against the referenced Series revision | Resolvable and structurally checkable (demonstrated: all 8 edge targets resolve) |
| Prior Book outcomes | Inherited condition with an `AcceptedFactRef`, or a `ArtifactRef` to a working predecessor revision (Increment 3) | Accepted history stays authoritative; working predecessors are referenced by revision |
| Long-range promises | Typed `sets_up` and `pays_off` edges to Series nodes or open questions | Uses the existing vocabulary |
| Characters and relationships | Structure-level motives that refer to named characters through `name_source`. The Book artifact creates no character commitments, character nodes, arcs or relationship states. A name with no source is flagged (G7) | The Studio validator forbids character and relationship nodes in architecture-only proposals (`src/auteur/beginner/studio_architecture.py`, 197–199), and the character contract (`docs/character-and-relationship-architecture.md`) assigns character commitments to Identity |
| Institutional and physical constraints | Reference to Series institution and structure nodes | Same as Series engines |
| Unresolved author decisions | `open_author_decisions[]` referencing a Series open question by index and text SHA-256 (§8) | Open questions are free text with no ids. The index-and-hash reference resolves now, without a Studio schema change |
| Series change proposed by a Book revision | A Studio revision request whose instruction cites the Book consequence ids. The Series changes only through its existing lifecycle, after author review | Keeps the Series owner authoritative. The Book artifact never writes the Series |
| Downstream consequences | Typed edges from the Book artifact to later Book artifacts (Increment 4) | Uses ADR 013 semantics: source affects target |

**Typed or prose.** Typed: references, edge types, provenance, decision ids. Prose: motives, choices, costs, transformations, and the reasoning behind them. There is no universal semantic dependency engine. The `reach` traversal in the probe is a measurement tool, not a proposed component.

### 5.5 Working state and authority (7.4)

**Element provenance** (the same vocabulary across the artifact):

- `author_fixed`: set only by an author action. Taken from Story Vision or intention records. The agent cannot write it.
- `derived`: references a source, and says so.
- `agent_proposed`: the default for agent output. Reversible.
- `hypothetical`: an alternative considered and not taken.
- `unresolved`: an open question or missing information.
- `accepted`: set only by an accepted owner (the Book Direction path). The Book artifact never writes it.

**Artifact states and transitions:**

| From | Operation | To | Guard |
|---|---|---|---|
| none | develop (`book-prepare`, then `book-complete-file`) | `working` (applied at once, as the Studio candidate does for a first develop) | Series revision current; references resolve; validation passes |
| `working` | revise (`book-prepare --instruction`, `book-complete-file`) | `review_ready` | As above; the response is retained as evidence |
| `review_ready` | `book-apply-review --request-sha256` | `working` (new revision) | The request is the latest; the baseline is unchanged; freshness fingerprints still match |
| any | a newer `book-prepare` | older request `superseded` | Enforced by the latest-request pointer, as in Studio |
| `review_ready` or `working` | withdraw one element (Increment 2) | element `rejected`, with a rationale | Changes only the Book artifact |
| `working` | propose a Book Direction draft, then `accept_book_direction` | accepted Book Direction (accepted owner) | Author action only. Apply never does this |

**No silent canon.** Apply writes only `architecture/books/<n>/current.json`. The Series candidate, the accepted directories, and the ArtifactStore sidecars are not written. Increment 1 includes a test that asserts this by comparing file digests before and after an apply.

**Open authority decision (owner).** Whether an author may set `author_declared` on a working element through a dedicated author-only operation. The default is no for v1. See §5.8 (O2). The existing acceptance gate is a constant author label (G12). The design does not strengthen it, and any acceptance UI depends on O1 and on an interactive confirmation that the owner must specify.

### 5.6 Revision behaviour (7.5)

| Behaviour | Design | Reused from | New |
|---|---|---|---|
| Bounded local revision | `book-prepare` takes target element ids. The validator requires every non-target element to be unchanged by id and content hash. A change outside the targets is flagged in the review | Review structure and preserved-element reporting in `studio_architecture_review.py` | Section-level diff and the preserved-set check |
| Holistic revision | Allowed, with a full review of every section | Same as above | None beyond the diff |
| Source freshness | Author source and intention fingerprints, as Studio does. Plus a per-referenced-node fingerprint for Series nodes. A changed node makes the Book artifact `suspect`; a removed node makes it `contradictory`; an unchanged reference set keeps it `clear` | `realization_impact` vocabulary; `revision-staleness-contract.md` | The Series-node fingerprint |
| Superseded proposals | Latest-request pointer | Studio lifecycle | None |
| Preserved elements | Diff by id and content hash | `candidate_diff` pattern | Book sections |
| Consequence inspection | Typed Book-to-Series edges, then a directed traversal over Series links. The output is a list for review and is never applied | `reach` pattern in the probe; ADR 013 direction | Packaging as an operation |
| Cross-Book review | Increment 4: when Book N changes, Book N+1 working artifacts that reference Book N elements are reported. Accepted Book directions hold no working elements, so they are reported only when a Series commitment they carry is affected through a changed Series node | `series_impact` pattern (service 1056) | Book-to-Book edges |
| Book change that needs a Series change | A Studio revision request citing the Book consequence ids; the Series lifecycle then reviews and applies it | Studio prepare, complete and apply | None. The Book artifact never writes the Series |
| Recovery after interruption | Request written before the pointer; response written before `current`; filesystem lock; fresh-process `resume` | Studio ordering and `_FilesystemLock`; the PR #556 apply CLI test | None |

**Reuse.** The lock and the atomic writer are reused as they are. The latest-request pointer and the request, review and current handling are extracted from Studio. The schema, validator, section diff, packet and reference traversal are new.

### 5.7 Fresh-agent continuation (7.6)

**Resume packet (decided):**

1. Identity: book number, title, the function question.
2. Series constraints: the Series nodes referenced by the Book's typed edges and by its inherited conditions, each with id and summary. Book-internal ids are excluded.
3. Current Book artifact, as exported items only: section 7 consequences, section 8 enabled and closed items, and the ten assumptions with their reversals.
4. Author-fixed commitments: Story Vision excerpt and intentions, by reference.
5. Unresolved questions and open author decisions (section 11).
6. Applicable alternatives: section 10 items, shown by title and status.
7. Source and revision identity: Book revision, request SHA, Series request SHA, and the content hash.
8. Consequential downstream commitments: typed outgoing edges (Increment 4).

**Measured (demonstrated).** The naive packet is 10,055 characters. That is 31.7% of the full Book artifact JSON (31,708 characters) and 24.4% of the full Series-plus-Book candidate JSON (41,189). Its largest component is the Series-constraint block at 4,354 characters, which includes the Book's own node summary (1,559 characters). **Revision adequacy (demonstrated).** The packet omits 6 of the 12 craft-mark revision targets: `s3_engine_04`, `s5_06`, `s5_07`, `s5_08`, `s6_01` and `s6_05`. The packet orients a fresh agent but cannot carry a revision. A revision request therefore carries the full text of every target and its dependents.

**Decided target:** remove Book-internal ids from the constraint block and show alternatives by title. The expected reduction is the duplicated node summary, but that has not been measured. The probe does not claim it.

### 5.8 Owner-reserved decisions and engineering defaults

**Owner-reserved** (escalated; the design does not decide them):

- **O1.** Whether a Book's working detail should eventually become accepted Book Direction content, or stay working with only the accepted identity accepted. The existing accepted path is available either way.
- **O2.** Whether an author may set `author_declared` on individual working elements, and through what operation. Default: not in v1.
- **O3.** Whether finale-alternative enablement should be modelled as typed Series edges. The repository's coverage assessment places this behind an evidence gate, and the probe shows the gap (G5). Owner decision on priority, not a technical default.

**Engineering defaults** (agent-selected, reversible):

- Storage under `architecture/books/<n>/` in the canvas.
- The neutral lifecycle module in `auteur.working_revision`.
- No caps on prose beyond sanity bounds.
- Reversal required for agent-proposed assumptions.
- Decision references resolved against stable Series open-question ids.
- Typed vocabulary from `DependencyType`.
- Packet selection as in §5.7.

## 6. What the design does not do

- It does not write accepted Series, Book, realization or Global Map state.
- It does not add a sixth semantic layer, a universal narrative graph, or a graph database.
- It does not change `SeriesIdentity`, `BookPlan`, or the contiguity rule.
- It does not canonize Book 24, the craft-mark, the Right's review, or any finale alternative.
- It does not write Chapter or Scene artifacts.
- It does not score creative quality. The validator checks structure and provenance only.
- It does not design the Studio UI. That is Increment 5, and it depends on O1.

## 7. Risks and reconciliation

The independent challenge and its reconciliation are recorded in the [worked example README](../../qualification-evidence/working-book-architecture-design-20261112/README.md#challenge-and-reconciliation). The main risks are: the schema could grow into a second Series architecture; the Book artifact could be read as more authoritative than it is; the lifecycle extraction could change Studio behaviour; and a fresh agent could still depend on the original conversation if the packet omits a needed element. The mitigations are in the implementation plan, each with a test.

## 8. Related decisions that need no change now

- **Open-question references.** The Series candidate's open questions are free text with no ids. The Book artifact references them by index and by the SHA-256 of their text (§5.4). Stable ids remain a later Studio schema change, to be reviewed separately. Until then, a reworded open question changes its hash, so the reference becomes stale rather than silently wrong.
- **G10.** The revision note in the Series summary should move to revision provenance, not summary prose. This is a Studio change, deferred.
- **Named-character sourcing (G7).** Whether a named character must appear in the candidate or in the Story Vision is a product rule. Escalate if it matters before Increment 1.
