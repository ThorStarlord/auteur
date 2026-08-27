# Global Map Architecture Value V1 — Source Manifest

Freeze revision: `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (merge commit PR #143, `origin/main`).
Experiment version: `global-map-architecture-value-v1`
Status: **FROZEN** — do not change sources after first A/B/C output.

## Authority distinction

| kind | meaning | examples |
|---|---|---|
| **ACCEPTED NARRATIVE SOURCE** | Revisioned artifact that was explicitly accepted via Auteur's authority boundary; content hash and revision are canonical. | Series Direction, Book Directions, Realization Bundles |
| **DERIVED RESEARCH REPRESENTATION** | Research-only explicit relationships built from accepted sources; interpretive or deterministic derivation, not canonical. | Global Map ledger entries, Decision Map selections, `why-now` derivations, grouping, causal links |

All derived entries must trace to an accepted source listed below. No unsupported story fact may be introduced.

## Frozen accepted source set (Archive of Lies)

Source of truth is the tracked fixture directory `tests/fixtures/repeated_map_focus_v2/` at the frozen revision. Also tracked is the earlier vertical-slice fixture `tests/fixtures/archive_of_lies_vertical_slice/` which covers Book 1→2 only; V1 uses the `repeated_map_focus_v2` ledger because it supplies Books 1–3 accepted history plus Book 4 planning intent.

| path | revision / identity | authority | why in experiment |
|---|---|---|---|
| `tests/fixtures/repeated_map_focus_v2/series_direction.yaml` | `archive-of-lies`, `series_type: ongoing`, `pressure: Every public correction...`, commitments `contested-history`, `commitment-falsifier` | ACCEPTED (`series-direction@1` equivalent) | Series pressure and commitments that constrain every probe |
| `tests/fixtures/repeated_map_focus_v2/book_1_direction.yaml` | Book 1 `The Missing Ledger`, `series_commitment_ids: [contested-history]` | ACCEPTED (`book-1-direction@1`) | Book 1 carries Series pressure; still open falsifier question |
| `tests/fixtures/repeated_map_focus_v2/book_1_realization.yaml` | transitions `founding-record: forged`, `monastery-testimony: preserved`, `broken-lantern: broken` | ACCEPTED (`book-1-realization@1`) — source_ref `book-1-direction@1` | Provides active consequence (forged record), dormant fact (testimony), irrelevant fact (lantern) |
| `tests/fixtures/repeated_map_focus_v2/book_2_direction.yaml` | Book 2 `The Council's Retraction` response, `series_commitment_ids: [contested-history]` | ACCEPTED (`book-2-direction@1`) | Continues pressure, investigates falsifier |
| `tests/fixtures/repeated_map_focus_v2/book_2_realization.yaml` | transitions `named-falsifier: named` (resolves `commitment-falsifier`), `public-admission: admitted fraud`, `admission-retracted: retracted admission` | ACCEPTED (`book-2-realization@1`) | Resolves falsifier, creates supersession chain (admission → retraction) |
| `tests/fixtures/repeated_map_focus_v2/book_3_direction.yaml` | Book 3 `The Protected Archive`, `series_commitment_ids: [contested-history]` | ACCEPTED (`book-3-direction@1`) | Continues pressure after retraction |
| `tests/fixtures/repeated_map_focus_v2/book_3_realization.yaml` | transitions `archive-protected: treaty protected`, `repaired-lantern: repaired` | ACCEPTED (`book-3-realization@1`) | Current state for Book 4 (treaty), irrelevant recent lantern |
| `tests/fixtures/repeated_map_focus_v2/book_2_unrelated_realization.yaml` | unrelated transitions for negative test | ACCEPTED but irrelevant | Ensures irrelevance filtering can be tested (not surfaced) |
| `tests/fixtures/repeated_map_focus_v2/r1-r3-history.yaml` | history ledger linking above fixtures, `series_commitment_ids`, `resolved_commitment_ids`, `unaccepted_realizations`, `planning_intents` | DERIVED manifest (research convenience, not authority) | Declares which commitments resolved when, and planning intents as non-authoritative triggers |
| `tests/fixtures/repeated_map_focus_v2/decision_seeds.yaml` | Focus seeds for Book 3 (`publish-witness-account` / `force-council-hearing`) and Book 4 (`publish-verified-testimony` / `stage-protected-hearing` + incompatible `burn-archive`) | DERIVED qualification seeds (proposal inputs only, not accepted Direction) | Defines bounded Focus question/options/rationale; Book 4 burn variant is explicitly `incompatible_with_state_refs` |
| `tests/fixtures/repeated_map_focus_v2/book_4_planning_intent.yaml` | Book 4 intent `Return to the monastery testimony without breaking the protected archive`, relevance_refs `monastery-testimony` + `archive-protected` | NON-AUTHORITATIVE planning intent (relevance trigger only) | Triggers dormant reactivation; must not be treated as accepted Book 4 Direction |
| `docs/acceptance/series-repeated-map-focus-capability-contract-v1.md` | R1–R5 ledger, Map/Focus contracts | ACCEPTED contract (product spec, not narrative) | Defines correct dispositions (active/resolved/dormant/reactivated/superseded/irrelevant) and grouping rules |
| `docs/design/series-repeated-map-focus-implementation-boundary-v1.md` | Implementation boundary analysis | Design doc | Explains what B can truthfully provide (no finite extent, no universal relevance engine) |
| `docs/product-validation/series-vertical-slice-v1-synthetic-repeated-map-focus-probe.md` | Synthetic probe ledger (same Archive of Lies ledger with rationale) | Research evidence (not participant) | Documents adversarial conditions the fixture was designed to test |
| `src/auteur/series/repeated_map_focus.py` (`_DERIVATION_VERSION=repeated-map-focus-v2-r1`) | `select_repeated_continuity`, `CurrentStateEvidence`, grouping, `validate_repeated_decision_proposal` | CURRENT AUTEUR behavior for Condition B | Exact shipped derivation B must use; version pinned in run manifest |

## Narrative authority status per transition

| transition_id | book | subject.attribute | after | authority | disposition at each planning point |
|---|---|---|---|---|---|
| `founding-record` | 1 | archive.founding_record | forged | ACCEPTED | Book2 active; Book3/4 history (grouped) |
| `monastery-testimony` | 1 | monastery.testimony | preserved | ACCEPTED | Book2 dormant; Book3 dormant; Book4 **reactivated** (Book4 intent trigger) |
| `broken-lantern` | 1 | archive_lantern.condition | broken | ACCEPTED | always irrelevant (never surfaced) |
| `named-falsifier` | 2 | archive.falsifier | named | ACCEPTED | resolves `commitment-falsifier`; Book3/4 resolved history only |
| `public-admission` | 2 | council.archive_position | admitted fraud | ACCEPTED | **superseded** by `admission-retracted` at Book3/4 |
| `admission-retracted` | 2 | council.archive_position | retracted admission | ACCEPTED | Book3 **current**; Book4 history (explains treaty) |
| `archive-protected` | 3 | archive.protection | treaty protected | ACCEPTED | Book4 **current** constraint |
| `repaired-lantern` | 3 | archive_lantern.condition | repaired | ACCEPTED | always irrelevant |
| `burn-archive` | 2 (unaccepted) | archive.condition | burned | PROPOSED, NOT ACCEPTED (`book-2-burn-archive`) | must never be surfaced as accepted fact |
| `ally-militia` | 3 (unaccepted) | archive_allies.response | militia raised | PROPOSED, NOT ACCEPTED | must never be surfaced |

## Derived Canonical State (for reference, not extra authority)

Derived from accepted bundles via `CanonicalState` rebuild; current values relevant to probes:

- At Book 2 planning (`through Book 1`): `archive.founding_record=forged`, `monastery.testimony=preserved` (dormant), `archive_lantern.condition=broken` (irrelevant)
- At Book 3 planning (`through Book 2`): `council.archive_position=retracted admission` (current), `archive.founding_record=forged` (history), `archive.falsifier=named` (resolved), `monastery.testimony=preserved` (still dormant)
- At Book 4 planning (`through Book 3`): `archive.protection=treaty protected` (current), `council.archive_position=retracted admission` (history), `archive.founding_record=forged` (grouped history), `monastery.testimony=preserved` (reactivated)

## What is intentionally NOT in V1 sources

- Finite/uncertain Series extent, contraction/expansion (not in `series_direction.yaml` `series_type: ongoing`; validators reject `finite`)
- Second independent long-form fixture — searched `tests/fixtures/`; no other tracked long-form case with comparable accepted-history depth exists. V1 is **single-fixture directional**; limitation recorded explicitly.
- No invented accepted events beyond the ledger above.

## No unsupported facts

Every Condition C ledger item (see `candidate-architecture-ledger.md`) maps to a row above. If an item cannot be mapped, it is excluded or marked `interpretive` with provenance.
