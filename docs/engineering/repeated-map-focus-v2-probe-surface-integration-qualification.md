# Repeated Map/Focus V2 — Probe Surface Integration Qualification

Date: 2026-08-26

## Qualification boundary

This report qualifies the exact NEW remote-main integration candidate
`cba545f89e4bb07551e938eae9e4b3db2ab38e13` (M5), constructed by merging the
historical Probe Surface tip `38e5b11e4bd370a099610441447bbc428c487cc7` into
current remote main `6aa4abef1f69ff471f51fa77ae45cabcbc0b5b94`.

This is a NEW integration candidate and is qualified independently from the
historical standalone qualification.

## Historical vs integration candidates

| Role | SHA |
|---|---|
| Historical standalone candidate | `092bd48f5728e7b1f2d6dfac16e40f7bf3850665` |
| Historical evidence tip | `38e5b11e4bd370a099610441447bbc428c487cc7` |
| NEW integration base | `6aa4abef1f69ff471f51fa77ae45cabcbc0b5b94` |
| NEW integration candidate (M5) | `cba545f89e4bb07551e938eae9e4b3db2ab38e13` |

Historical qualification lineage preserved:
- `5e1f293...` (C4 tip) → `092bd48...` → `38e5b11...` verified
- All 7 Campaign-5 commits ancestors of M5 verified
- Campaigns 1–4 ancestry preserved in M5 verified

## Integration scope

8 files changed, +1212/−5 against current main:

Source files (4 modified):
- `src/auteur/series/cli.py` — accepted-facts CLI, plan-next-book --intent/--relevance
- `src/auteur/series/repeated_map_focus.py` — selection_token_for, list_accepted_facts
- `src/auteur/series/vertical_slice_formatters.py` — format_accepted_facts
- `src/auteur/series/vertical_slice_service.py` — list_accepted_facts, resolve_accepted_fact_selection_token, enter_repeated_book_planning

Test files (1 modified):
- `tests/test_series_repeated_map_focus.py` — +774 lines, 15 Boundary-2 tests

Docs/evidence (3 added/modified):
- `docs/engineering/repeated-map-focus-v2-probe-surface-qualification.md`
- `docs/qualification-evidence/092bd48f5728e7b1f2d6dfac16e40f7bf3850665.json`
- `docs/superpowers/plans/2026-08-25-repeated-map-focus-v2-probe-enabling-surface-implementation.md` (modified)

No scope expansion. All within the frozen two-blocker boundary.

## Focused qualification results

### Boundary-2 + Repeated Map/Focus V2

```
tests/test_series_repeated_map_focus.py  69 passed (54 V2 + 15 Boundary-2)
```

### V1 regressions

```
tests/test_series_vertical_slice_service.py     passed
tests/test_series_vertical_slice_models.py      passed
tests/test_series_vertical_slice_cli.py         passed
Total V1 regressions: 113 passed
```

### Provenance / story-state

```
tests/test_provenance_pilot.py          passed
tests/test_story_state_commands.py      passed
tests/test_story_state_manager.py       passed
Total provenance/story-state: 44 passed
```

### Complete source qualification

Complete local source suite timed out after 600 seconds at ~46% progress.
All tests passing through timeout point — this is an environmental limitation
(timeout too short for full suite on this machine), not a test failure.

Focused qualification covers the complete Boundary-2 + Probe Surface surface
plus all V1 regressions and provenance/story-state paths. GitHub exact-head CI
is the required authoritative complete-source merge gate.

### Repository checks

```
scripts/check.py --skip-pytest     24/24 validators PASS
scripts/validate-repo.py           PASS
scripts/verify_vendored_contract.py PASS
ruff check src tests               All checks passed
```

## Installed-wheel qualification

| Field | Value |
|---|---|
| Filename | `auteur-0.37.1-py3-none-any.whl` |
| Package version | `0.37.1` |
| Wheel file count | 414 |
| SHA-256 | `2ed02fb1fe5d91f004dcd36e067d38116d64f9a2a51965eeb5837573379e4da2` |

Installed-wheel qualification matrix (11/11 passed):

| Check | Result |
|---|---|
| Import from site-packages (version 0.37.1) | PASS |
| Pack list | PASS |
| Pack inspect | PASS |
| Opinionated recommendation | PASS |
| Recommendation artifact durability across process restart | PASS |
| Zero pre-acceptance mutation | PASS |
| Explicit acceptance updates Identity | PASS |
| Restart persistence | PASS |
| Pack version and hash persist | PASS |
| Genre validation | PASS |
| Genre diagnosis | PASS |

## Behavioral verification

Confirmed:
- accepted-facts discovery works (CLI + service + formatter)
- deterministic selection-token generation works
- tokens remain presentation locators only
- token resolution fails closed (0 matches, >1 matches)
- revision prevents silent repointing
- --intent planning path works
- zero-relevance intent works
- --relevance without --intent fails with no persistence
- legacy planning path remains intact
- planning intent remains non-authoritative
- Map/Focus authority invariants remain intact

## Evidence topology

M5 = `cba545f89e4bb07551e938eae9e4b3db2ab38e13` (exact qualified integration source/test candidate)

This document is the evidence-only publication tip. No E5 commit is created —
the evidence is this document itself, committed after M5 if the publication
model requires it.

## Explicit non-claims

- No human usability evidence yet
- No human-validation result
- No release-readiness claim
- No generalized history/search/ranking system
- No free-form Book-N Direction capability
- No complete local source qualification (environmental timeout limitation)

## Publication readiness

READY FOR CAMPAIGN-5 PR AUTHORIZATION (pending GitHub exact-head CI as
authoritative complete-source merge gate)
