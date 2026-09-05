# DENSE TRILOGY V1 — Session R revision evidence

## Freeze identity

- Frozen protocol: `2ecb94b3eef3794f51063fe2761b111a7ad2ca05`
- Clean normal-accumulation freeze: `6575e93f9bb849f399cd5ae766fc7bac26187837`
- Experiment worktree: `H:/GithubRepositories/auteur-dense-trilogy-architecture-stress-test-v1`
- Branch: `experiment/dense-trilogy-architecture-stress-test-v1`
- Runtime: repository source through `PYTHONPATH=src`.

This revision pass is subsequent evidence. It does not modify or reinterpret
the already-recorded clean normal-accumulation conclusion.

## System facts

The bootstrap gate passed: the isolated worktree was at the clean Session-C
freeze, the branch was correct, Session B was an ancestor, and production
source had no diff from the authorized baseline.

The target was verified from accepted repository state:

- artifact: `realization-bundle-book-1-sounding-line-outcome`
- transition: `mara-ion-trust`
- original revision: 1
- new revision: 2

The existing realization revision service preserved revision 1, created
revision 2, and retained the same artifact lineage. The only semantic change
was:

`conditional alliance` → `strained cooperation under unresolved distrust`

Book 2 and Book 3 accepted payloads were not rewritten. Their accepted
metadata and content hashes remained unchanged.

Canonical rebuild succeeded with state version 3. The final current Mara/Ion
value remained Book 3's accepted `public interdependence with protected
dissent`, while the rebuild emitted the expected conflict against Book 2's
former `conditional alliance` before-state.

The revision-impact surface identified Book 2 as stale/contradictory and Book 3
as stale/contradictory, with Book 1 fresh/contradictory. Review order was
Book 1, Book 2, Book 3. The service explicitly stated that affected accepted
artifacts remain accepted and no downstream artifact was rewritten.

Continuity Review and Global Map used Book-1 revision 2 in historical
provenance, kept revision 1 inspectable, surfaced the revised relationship,
retained Book 2's accepted current relationship, and emitted the contradictory
semantic-impact warning. This distinguishes affected-by-revision from the
review/reconciliation boundary without authoring a repair.

SeriesIdentity validate/diagnose/bible/graph surfaces were run observationally.
Validation passed. Diagnostics remained the three previously recorded warnings:
missing payoff for `erased-coast`, missing payoff for `bell-reef`, and unresolved
`copied-anomaly`. No new SeriesIdentity diagnostic appeared. The canonical
Series plane does not consume the revised accepted-history relationship in this
surface; this is classified as integration/projection evidence.

## Narrative facts

The revision changes only the Mara/Ion Book-1 relationship outcome. Books 2 and
3 remain accepted narrative artifacts. Book 2 still expects the old Book-1
state, and Book 3 still builds from Book 2's accepted relationship state.

## Worker actions

The worker used the existing service API, rebuilt derived state, ran existing
impact and continuity/map/focus surfaces, and ran SeriesIdentity diagnostics.
No downstream repair, new creative decision, chapter outline, scene outline,
or prose was created.

## Researcher interpretation

| Category | Result |
|---|---|
| REVISION_LINEAGE | PASS — append-only revision history; same artifact lineage |
| CURRENT_STATE | PASS with explicit conflict — deterministic rebuild retains Book-3 current value and records mismatch |
| DIRECT_IMPACT | PASS — Book 2 is stale/contradictory through its direct state-order dependency |
| TRANSITIVE_IMPACT | PASS — Book 3 is stale/contradictory downstream of Book 2 |
| SEMANTIC_CONTRADICTION | PASS — Book-2 before-state mismatch is detected |
| REVIEW_SELECTION | BOUNDED — affected artifacts and review boundary are distinguished; no repair is selected automatically |
| FALSE_POSITIVE_IMPACT | NONE observed in accepted-artifact impact; Series diagnostics are unchanged pre-existing warnings |
| INTEGRATION_PROJECTION | OBSERVED — SeriesIdentity diagnostics do not consume revised accepted-history state |
| AUTHORITY | PASS — Books 2/3 remain accepted and untouched |
| WORKFLOW | PASS via existing service API; no public CLI accept-revision command was exposed |

## Scope exclusions verified

- production code/schema changes: none;
- Book-2/Book-3 repairs: none;
- chapters: none;
- scenes: none;
- prose: none;
- Session D: not started.

## Supporting raw evidence

See `session-r-pre-revision-snapshot.md`,
`session-r-revision-candidate-and-acceptance.md`,
`session-r-post-revision-state.md`, and the raw output files listed there.

## Verification

Focused tests passed: `pytest -q tests/test_series_vertical_slice_global_map.py tests/test_series_productization.py`.
Pytest reported an exit-time Windows permission warning while cleaning its
temporary directory; this did not affect the passing test result and is an
environment cleanup issue.
