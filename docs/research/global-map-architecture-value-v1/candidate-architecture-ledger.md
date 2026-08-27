# Global Map Architecture Value V1 — Candidate Architecture Ledger (Condition C)

**Purpose:** Research-only, source-backed experimental architecture for Condition C. Deterministically disposable; **not** a production schema, not Pydantic, not ontology, no universal field names.

**Construction rule:** Golden ledger — carefully built from frozen sources listed in `source-manifest.md`. Isolates *value of representation* from *quality of automatic extraction*. Every entry is traceable.

**Authority tags:** `ACCEPTED` = explicitly accepted artifact; `DETERMINISTIC_DERIVATION` = rebuildable from accepted sources via stated rule; `INTERPRETIVE` = researcher phrasing of accepted material (must not be treated as canon).

---

## A. Identity & Direction

| id | plain-language statement | category | source | authority | relationships |
|---|---|---|---|---|---|
| DIR-S1 | Series is `Archive of Lies`, `ongoing`, promise *Each recovered account reveals who profits when history is controlled*, pressure *Every public correction gives hidden archivists reason to erase another witness*, open question *Can truth survive without becoming instrument of power?* | Series Direction | `series_direction.yaml` lines 1-6 | ACCEPTED | Series pressure → governs all Books |
| DIR-SC1 | Commitment `contested-history`: *Every Book must expose conflict between official history and lived memory* | commitment | `series_direction.yaml` commitment `contested-history` | ACCEPTED | active in Books 1-3 (see carried-by refs in `r1-r3-history.yaml`) |
| DIR-SC2 | Commitment `commitment-falsifier`: *Person who falsified founding record must be identified* | commitment | `series_direction.yaml` `commitment-falsifier` | ACCEPTED | unresolved Book1 → resolved by Book2 realization |
| DIR-B1 | Book 1 `The Missing Ledger`: core answer *Telling truth requires protecting erased people*; want *Recover ledger*; resistance *custodians erase witnesses*; conflict *authenticate while choosing witnesses*; stakes *publish too soon destroys witnesses / waiting erases truth* | Book Direction | `book_1_direction.yaml` | ACCEPTED | carries DIR-SC1; generates founding-record setup |
| DIR-B2 | Book 2 `The Council's Retraction`: want *Identify falsifier and force council to answer*; resistance *council can admit then retract*; conflict *name falsifier without discrediting witnesses* | Book Direction | `book_2_direction.yaml` | ACCEPTED | carries DIR-SC1; open question *Will admission survive?* |
| DIR-B3 | Book 3 `The Protected Archive`: want *Protect archive after retraction*; resistance *evidence vulnerable to seizure*; conflict *secure evidence without silencing witnesses* | Book Direction | `book_3_direction.yaml` | ACCEPTED | carries DIR-SC1; responds to retraction |
| DIR-INT2 | Book 2 planning intent: *Make forged founding record matter to lived memory* (relevance_ref `founding-record`) | planning intent | `r1-r3-history.yaml` planning_intents[0] | NON-AUTHORITATIVE trigger | activates founding-record relevance |
| DIR-INT3 | Book 3 planning intent: *Respond to council's accepted retraction* (relevance_ref `admission-retracted`) | planning intent | `r1-r3-history.yaml` planning_intents[1] | NON-AUTHORITATIVE trigger | activates retraction currentness |
| DIR-INT4 | Book 4 planning intent: *Return to monastery testimony without breaking protected archive* (relevance_refs `monastery-testimony` + `archive-protected`) | planning intent | `book_4_planning_intent.yaml` | NON-AUTHORITATIVE trigger | reactivates dormant testimony; requires treaty preservation |

## B. Current State & Transitions (accepted facts)

| id | statement | category | source | authority | relationships |
|---|---|---|---|---|---|
| ST-F1 | `archive.founding_record = forged` — ledger proves founding record forged | transition `founding-record` | `book_1_realization.yaml` | ACCEPTED | setup → enables falsifier investigation; grouped under DIR-SC1 |
| ST-F2 | `monastery.testimony = preserved` — sealed testimony at remote monastery, initially dormant | transition `monastery-testimony` | `book_1_realization.yaml` | ACCEPTED | setup → payoff candidate in Book4 via DIR-INT4 |
| ST-I1 | `archive_lantern.condition = broken` — lantern broken during search | transition `broken-lantern` | `book_1_realization.yaml` | ACCEPTED | irrelevant — never supports active continuity |
| ST-F3 | `archive.falsifier = named` — evidence identifies falsifier | transition `named-falsifier` | `book_2_realization.yaml` | ACCEPTED | payoff of DIR-SC2; resolves `commitment-falsifier` |
| ST-F4 | `council.archive_position = admitted fraud` — council publicly admits falsification | transition `public-admission` | `book_2_realization.yaml` | ACCEPTED (superseded) | superseded by ST-F5 |
| ST-F5 | `council.archive_position = retracted admission` — council retracts admission | transition `admission-retracted` | `book_2_realization.yaml` (before adm→after retr) | ACCEPTED | current at Book3/4; supersedes ST-F4; cause → treaty |
| ST-F6 | `archive.protection = treaty protected` — treaty protects archive as only evidentiary chain | transition `archive-protected` | `book_3_realization.yaml` | ACCEPTED | current at Book4; causal dependency of evidentiary chain |
| ST-I2 | `archive_lantern.condition = repaired` — lantern repaired | transition `repaired-lantern` | `book_3_realization.yaml` | ACCEPTED | irrelevant — recent but not relevant |
| ST-P1 | `archive.condition = burned` — *would* burn archive (rejected alternative) | transition `burn-archive` (unaccepted candidate `book-2-burn-archive`) | `r1-r3-history.yaml` unaccepted_realizations[0] | PROPOSED NOT ACCEPTED | **forbidden** — contradicts ST-F6 |
| ST-P2 | `archive_allies.response = militia raised` — *would* raise militia (rejected) | `ally-militia` | `r1-r3-history.yaml` unaccepted_realizations[1] | PROPOSED NOT ACCEPTED | must remain excluded |

## C. Derived Relationships (explicit, research-only)

| id | statement | category | derivation rule | source trace | relationships |
|---|---|---|---|---|---|
| REL-01 | Series pressure `contested-history` manifests as active conflict in each Book via carried `series_commitment_ids` | thread / commitment trajectory | carry: `book_N.direction.series_commitment_ids` contains `contested-history` | `book_1/2/3_direction.yaml` + `r1-r3-history.yaml` series_commitment_ids | DIR-SC1 → DIR-B1/B2/B3 → ST-F1/F5/F6 |
| REL-02 | `founding-record forged` is causal setup for `named-falsifier` investigation | setup → payoff | Book1 realization enables Book2 falsifier question | ST-F1 → DIR-SC2 → ST-F3 | cause → consequence |
| REL-03 | `named-falsifier` resolves commitment `commitment-falsifier`; question closed | commitment resolution | `resolved_commitment_ids` in `book_2_realization.yaml` + `r1-r3-history.yaml` `resolved: commitment-falsifier` | ST-F3 ↔ DIR-SC2 | resolved, not active |
| REL-04 | `public-admission` superseded by `retracted admission` (ordered transitions in same bundle) | supersession / currentness | later transition on same `subject.attribute` overwrites earlier; `CurrentStateEvidence` picks latest | ST-F4 → ST-F5 (book_2_realization transitions ordered) | superseded lineage |
| REL-05 | `admission-retracted` causes `archive-protected` (treaty) — retraction makes evidence vulnerable → protection | causal dependency | Book3 direction `want: Protect archive after retraction` + realization `archive-protected` explanation | ST-F5 → DIR-B3 → ST-F6 | cause → current constraint |
| REL-06 | `monastery-testimony` dormant (Book1) → reactivated (Book4) when DIR-INT4 explicitly references it | dormant reactivation | `disposition = reactivated` iff `source_ref ∈ planning_intent.relevance_refs` and older book | ST-F2 ↔ DIR-INT4 (`book_4_planning_intent.yaml` relevance_refs) | accepted fact × intent trigger |
| REL-07 | `archive-protected` is current-state constraint that forbids `burn-archive` | state-compatibility / incompatibility | `incompatible_with_state_refs` in `decision_seeds.yaml` book_four_burn_archive; `validate_repeated_decision_proposal` rejects | ST-F6 ⊘ ST-P1 | forbids option |
| REL-08 | Irrelevant chain `broken-lantern` → `repaired-lantern` supports neither active continuity nor current decision | irrelevance / false recency | disposition `irrelevant` when latest book but older history exists and not in trigger; `dormant` otherwise | ST-I1, ST-I2 | must be excluded from Decision Map |
| REL-09 | Consequences `founding-record` + `admission-retracted` + `archive-protected` instantiate single pressure `contested-history` and should be grouped | pressure grouping | `_group_active_consequences` groups multiple active facts whose Book Directions carry same active commitment | DIR-SC1 + ST-F1/F5/F6 | group `contested-history` |
| REL-10 | Thematic tension *official history vs lived memory* persists via pressure; future payoff requires preserving evidentiary chain (`archive-protected`) to authenticate testimony | thematic / reveal relationship | Series pressure statement + Book4 rationale in `decision_seeds.yaml` | DIR-S1 pressure + ST-F6 + ST-F2 | Series direction → Book pressure → current tradeoff |

## D. Unresolved / Future-intent

| id | statement | category | source | authority |
|---|---|---|---|---|
| FUT-01 | Open question Book1: *Who falsified founding record?* → answered Book2 | unresolved → resolved | `book_1_direction.yaml` open_questions vs ST-F3 | DETERMINISTIC_DERIVATION (resolution tracked) |
| FUT-02 | Open question Book2: *Will council admission survive scrutiny?* → answered by retraction (no) | unresolved → superseded | `book_2_direction.yaml` vs ST-F5 | DETERMINISTIC_DERIVATION |
| FUT-03 | Open question Book3: *How can protected evidence restore witness authority?* → points to Book4 testimony use | unresolved → forward intent | `book_3_direction.yaml` vs DIR-INT4 | INTERPRETIVE linkage (source-backed) |
| FUT-04 | Book4 intent: re-center lived memory via authenticated testimony without severing chain | future intended direction | `book_4_planning_intent.yaml` + `decision_seeds.yaml` book_four rationale | NON-AUTHORITATIVE intent (not canon) |

## Global Map representation (research-readable projection)

The Global Map is the whole-story projection of A–D above, grouped for inspection:

- **What is this story?** DIR-S1 + DIR-SC1 (Archive of Lies, ongoing, official history vs lived memory)
- **Where is it going?** DIR-S1 open question + FUT-03/04 (truth surviving as protected lived memory)
- **Important trajectories:** REL-01 commitment trajectory; REL-02→03 falsifier arc; REL-04→05 council admission→retraction→treaty causal chain; REL-06 dormant→reactivated testimony
- **What has been established?** ST-F1, ST-F3, ST-F5, ST-F6 (current/history), plus grouped history cluster
- **What remains unresolved?** FUT-03 (how protected evidence restores witness)
- **What relationships connect?** REL-01 through REL-10

No entry introduces narrative facts unavailable to Condition A; all are from `source-manifest.md` rows.

## Decision Map derivation (per probe)

For each probe, Decision Map = relevance-selected subset of this ledger filtered by `_ACTIVE_DISPOSITIONS = {active, reactivated}` plus current-state evidence, trigger refs, and grouping, per `repeated_map_focus.py` disposition rules. See `decision-probes.md` for per-probe slices. Categorical counts per ledger: Direction 9, State 10, Derived relationships 10, Future 4 = 33 items total.
