# Pressure-Group Map→Focus Eligibility Conformance Audit V0

## Status

**Evidence status:** EVIDENCE COMPLETE / OWNER GATE CLOSED
**Responsibility type:** Research + Architecture Conformance Audit
**Campaign layer:** Reasoning / Derived Projection
**Implementation:** NOT AUTHORIZED

This record reports a bounded conformance audit. It does not add a pressure
entity, lifecycle, group-status field, ontology, extraction path, scale work, or
product-value claim.

## Research question

Given existing commitment disposition, pressure-group target, member
status/currentness, accepted planning triggers, relation disposition and
provenance, and revision state, can the current accepted-history → Global Map →
Focus composition decide whether a pressure group belongs in the current
bounded planning decision without inventing narrative semantics?

The audit keeps two questions separate:

1. May a derived group remain reconstructable in the neutral Global Map?
2. What evidence, if any, makes that group eligible for the current Focus?

## Owner authorization

The owner approved this exact responsibility and authorized repository
documentation only.

| Boundary | Decision |
| --- | --- |
| Implementation | NO |
| Ontology | NO |
| New pressure entity, lifecycle, or group-status schema | NO |
| Extraction | GATE NOT CROSSED |
| Scale | NO |
| Author-value claim | NO |
| Prospective native case | NO |
| Next step | CAMPAIGN-LEVEL REASSESSMENT; no automatic implementation |

## Baseline and isolation

The required baseline commands were run in the original checkout before any
worktree change.

| Check | Result |
| --- | --- |
| Repository root | `H:/GithubRepositories/auteur` |
| Git common directory | `.git` (standalone repository) |
| Original branch | `main` |
| Original local HEAD | `7544b5c6ff4ef6d9520b544cd92de4807aacc84e` |
| `origin/main` after fetch | `30691088c54e1d721bec91f26264d9414e044fb1` |
| Known closure commit ancestor check | PASS, exit 0 |
| Original checkout status | Pre-existing untracked files only; untouched |

The research worktree was created from `origin/main` at the exact closure
commit:

```text
H:/GithubRepositories/auteur-pressure-group-focus-eligibility-conformance-v0
research/pressure-group-focus-eligibility-conformance-v0
30691088c54e1d721bec91f26264d9414e044fb1
```

No source, test, fixture, or existing campaign artifact was edited in the
original `main` worktree.

## Scope and non-goals

In scope are the accepted `Archive of Lies` fixture, the existing direct
selector precedent, `SeriesVerticalSliceService.build_global_map`,
`select_focus_from_global_map`, D13 preservation, and the existing revision and
freshness checks.

Out of scope are production fixes, new tests or fixtures, schema changes,
pressure lifecycle design, ontology, extraction, model inference, scale,
author dogfood, prospective validation, and any claim about author value.

## Normative contract ledger

| Claim | Authoritative source | Status | Implication for Global Map | Implication for Focus | Implementation assumption |
| --- | --- | --- | --- | --- | --- |
| Derivation order is accepted history → current-state projection → relation/group index → Global Map → Focus. | `docs/architecture/detailed-narrative-architecture-v1.md`, Global Map section | ESTABLISHED | Build a full derived map before selection. | Focus consumes the map, not canonical sources directly. | NONE |
| Global Map and Focus are derived, rebuildable, and non-canonical. | Architecture authority matrix; ADR 019 | ESTABLISHED | Preserve refs, revisions, and derivation metadata. | Omission cannot delete accepted history. | NONE |
| Active commitments and current constraints are Focus inputs. | Architecture Focus section | ESTABLISHED | Keep commitment disposition and current-state evidence available. | These are independent possible eligibility bases. | NONE |
| Explicit accepted refs can reactivate old facts. | Architecture Focus section; D7 | ESTABLISHED for fact-level selection | Preserve exact fact refs. | A referenced historical fact may be relevant without becoming current. | NONE |
| A historical or superseded member may remain in a relevant group without becoming current. | Architecture Global Map section; D13 | ESTABLISHED | Keep the member, role, status, and evidence ref. | Project status separately from relevance. | NONE |
| Explicit resolution removes a commitment from direct active continuity while retaining history. | Commitment model; `select_repeated_continuity`; existing resolution test | PARTIAL | Map may show a resolved trajectory and its evidence. | Direct commitment selection excludes the resolved entry, but group-level projection is not specified. | Do not equate commitment status with relation status. |
| A pressure-group target's commitment status determines group-level Focus eligibility. | No exact rule in the accepted architecture | UNKNOWN | The target ref and map commitment entry are available. | No deterministic group predicate can be cited from the docs. | NONE |
| Relation `active` / `stale` / `rejected` disposition has a defined independent meaning for Focus. | Relation models and architecture origin model | PARTIAL | Preserve relation disposition and provenance. | The selector's use of relation disposition is not specified. | Do not treat relation disposition as commitment disposition. |
| A stale map must fail closed before Focus. | Architecture freshness rules; current selector guard | ESTABLISHED | Rebuild from current source revisions. | `select_focus_from_global_map` rejects stale maps. | NONE |
| Ordered adjacency is not semantic causation, and relation relevance is not proof of author meaning. | DSR and D19 guardrails | ESTABLISHED | Keep deterministic relation evidence labelled. | Do not promote a derived group to canon or universal semantics. | NONE |

The contract therefore establishes preservation and fact-level status behavior,
but it does not establish the predicate that lifts member-level evidence to a
Focus-level pressure group.

## Architecture evidence

`build_global_map` loads accepted Series, Book, and realization revisions,
derives current-state evidence, records map commitment entries as `active` or
`resolved`, builds typed causal relations, and then derives pressure groups from
qualifying accepted members. Each pressure group carries a commitment or fact
target, member refs and roles, relation origin, relation disposition, source
revision refs, evidence refs, and a named rule version.

The pressure-group loop does not visibly filter out a resolved target. That is
not, by itself, a Map defect. The architecture says that a derived Map may
retain historical evidence and that deleting a derived view must not delete
history. The Map contains enough information to distinguish the resolved map
commitment entry from the relation and to rebuild the view.

The direct selector supplies useful precedent. It changes an explicitly
resolved commitment to `resolved`, keeps it in history, and excludes it from
active continuity. Its grouping helper groups only active commitments and
active/reactivated facts. This is implementation precedent, not a replacement
for the accepted architecture. It agrees with the architecture on commitment
history and currentness, but it does not define the Global Map group predicate.

## Global Map derivation audit

For Book 4 over accepted Books 1–3, the runtime Map contains:

- `pressure-group-contested-history`, target `series-direction@1/contested-history`, target commitment `active`, relation origin `DETERMINISTIC_DERIVATION`, relation disposition `active`, seven member refs, and all Series/Book/realization revision refs.
- `pressure-group-commitment-falsifier`, target `series-direction@1/commitment-falsifier`, target commitment `resolved`, relation origin `DETERMINISTIC_DERIVATION`, relation disposition `active`, five member refs, and the same accepted revision set.

The Map preserves currentness separately from relation membership. In the
repeated fixture, `founding-record`, `monastery-testimony`, `named-falsifier`,
`admission-retracted`, `archive-protected`, and `repaired-lantern` are current;
`broken-lantern` and `public-admission` are historical or superseded facts.
`public-admission` is retained in the Map but is not a pressure-group member
in this exact derived run because it has no qualifying cross-Book member role.
`broken-lantern` is a historical member with role `originating_history`.

The Map is fresh when all source revisions match. The service records source
revisions, current-state lineage, relation evidence, and the derivation
fingerprint. No Map deletion or historical-member removal is warranted by this
audit.

**Global Map result:** CONFORMS for accepted-history preservation, currentness,
relation provenance, target commitment disposition, and revision/freshness
handling. The group-level eligibility rule remains a downstream contract
question.

## Focus derivation audit

`select_focus_from_global_map` first rejects a stale map or a mismatched planning
book. It then iterates every `snapshot.pressure_groups` relation and immediately
creates a `ContinuityGroup`. That construction copies relation evidence refs,
member entry IDs, member roles, and a generic explanation:

```text
This accepted pressure group remains relevant through its derived evidence.
```

The selector does not check target commitment disposition, relation
disposition, planning `relevance_refs`, or member currentness before adding a
group. It filters fact-level entries separately. Explicit fact refs become
`active` or `reactivated`; unreferenced current facts become `irrelevant`; and
superseded facts retain their historical disposition. A group can therefore be
present even when none of its fact entries is active. The productization seam
passes `context.groups` through as `persistent_pressures`, so the collection is
author-facing, but the accepted architecture does not say whether it is a
strict eligibility list or a structural group projection.

The selector's generic explanation is too weak to identify the actual basis
for a particular group. It is not enough evidence to claim that the group is
false or that a new explanation field is required. The conformance question is
whether group inclusion itself has a deterministic predicate. The current
architecture does not provide one.

## Runtime characterization

The probes used the existing `tests/fixtures/repeated_map_focus_v2/` files and
the existing test helper APIs. Temporary accepted state was created outside
repository-controlled source paths. The source import path was pinned to this
clean worktree. No fixture, test, or source file was changed.

### Case matrix

| Case and exact group/target | Commitment status | Relation origin / disposition | Member status and currentness | Explicit trigger | Revision / freshness | Expected eligibility | Actual Map behavior | Actual Focus behavior | Conforms? | Overclaim check | Provenance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. `pressure-group-contested-history` → `series-direction@1/contested-history` | active | `DETERMINISTIC_DERIVATION` / active | Current: `founding-record`, `monastery-testimony`, `named-falsifier`, `admission-retracted`, `archive-protected`, `repaired-lantern`. Historical/superseded: `broken-lantern`. | Yes: Book 4 refs `monastery-testimony` and `archive-protected`. | All accepted rev. 1 refs; fresh. | `CURRENT_CONSTRAINT`, with explicit member refs as additional support. | Group exists with seven exact members, roles, evidence refs, and source revisions. | Group exists with all seven member IDs and roles. Triggered facts are active; `broken-lantern` remains superseded/history. | UNKNOWN for the formal group predicate; member/currentness behavior conforms. | Generic why-now omits the current-constraint and trigger basis. It does not prove a false group claim. | `series_direction.yaml`; `r1-r3-history.yaml`; `book_4_planning_intent.yaml`; realization refs listed above. |
| B. `pressure-group-commitment-falsifier` → `series-direction@1/commitment-falsifier` | resolved by Book 2 accepted realization | `DETERMINISTIC_DERIVATION` / active | Current: `founding-record`, `monastery-testimony`, `named-falsifier`, `admission-retracted`. Historical/superseded: `broken-lantern`. | Yes at member level: Book 4 explicitly references `monastery-testimony`, which is a member of this group. No direct commitment ref. | All accepted rev. 1 refs; fresh. | `UNKNOWN` at group level. Resolution removes the active-commitment basis, but the explicit member ref, current member roles, and active relation remain independent bases. | Group exists with five exact members; map commitment entry is `resolved`. | Group still appears. `commitment-falsifier` is a resolved history entry; the explicitly referenced member is active. | UNKNOWN. | It would overclaim to say "no trigger references this group." The trigger reaches a member. It would also overclaim to treat resolved commitment as proof that all related history is irrelevant. | Same fixture refs as A; `book_2_realization.yaml` resolution and exact member refs. |
| C. D13 historical-member guard: `pressure-group-contested-history` with `broken-lantern` | active | `DETERMINISTIC_DERIVATION` / active | `broken-lantern` is `originating_history`, historical/superseded; current members remain current. | Yes: `monastery-testimony` and `archive-protected`. | Fresh rev. 1 Map; rebuild reproduces the same result. | Group may be `CURRENT_CONSTRAINT` or `EXPLICITLY_TRIGGERED_HISTORICAL_SUPPORT`; the member itself is `OMIT_FROM_FOCUS` as current material while remaining relation-relevant. | Group preserves the historical member, role, and exact evidence ref. | D13 projection preserves the group and member role; the historical member remains superseded/history and is not promoted current. | YES for D13 preservation and currentness separation. | No currentness overclaim. The generic group explanation is not a per-member status claim. | `tests/test_series_vertical_slice_global_map.py::test_global_map_focus_d13_and_rebuild_survive_historical_member`; exact fixture refs above. |
| D1. Trigger absent, `pressure-group-contested-history` → active target | active | `DETERMINISTIC_DERIVATION` / active | Current members remain current; `broken-lantern` remains historical/superseded. | No `relevance_refs` in accepted Book 4 planning input. | Fresh rev. 1 Map. | `CURRENT_CONSTRAINT` is plausible because active commitments and current constraints are independent Focus inputs. | Group remains in Map with seven members. | Group remains in `focus.groups`; fact entries are inactive/history except the active commitment entry. | UNKNOWN for group-level projection, not a failed currentness check. | No claim that lack of a trigger makes an active current constraint irrelevant. | Existing accepted `BookPlanningIntent(book_number=4, relevance_refs=[])`; same fixture. |
| D2. Trigger absent, `pressure-group-commitment-falsifier` → resolved target | resolved | `DETERMINISTIC_DERIVATION` / active | Current members include `founding-record`, `monastery-testimony`, `named-falsifier`, and `admission-retracted`; `broken-lantern` is historical/superseded. | No planning refs in this control. | Fresh rev. 1 Map. | `UNKNOWN`. There is no direct active-commitment basis, but current member roles and relation disposition remain. | Group remains in Map as derived evidence. | Group remains in `focus.groups`; all fact entries are history/irrelevant/superseded and the resolved commitment is history. | UNKNOWN. | It would overclaim to call the group an active pressure or to require omission without a specified group predicate. | Existing accepted `BookPlanningIntent(book_number=4, relevance_refs=[])`; same fixture. |

## Counterfactual analysis

The initial provisional defect hypothesis used this counterfactual:

> Hold accepted history, members, refs, revisions, and planning intent constant;
> change only `commitment-falsifier` from active to explicitly resolved; expect
> its Focus group eligibility to change from active to omitted.

The independent critic rejected that counterfactual. It removes one basis, but
it does not remove every basis. `monastery-testimony` remains an explicitly
referenced current member of the resolved group, and the relation remains
independently `active`. The accepted architecture lists explicit refs and
current constraints as separate Focus inputs and does not couple commitment
resolution to relation disposition.

No smaller valid counterfactual is available in the existing accepted cases.
Constructing one would require changing accepted facts/currentness or inventing
a group-level predicate. Therefore the audit does **not** claim a deterministic
composition gap.

**Smallest admissible counterfactual:** NONE.

## Provisional disposition before critique

The runtime initially suggested `DETERMINISTIC_COMPOSITION_GAP` at
`FOCUS_SELECTION` because the selector includes a resolved-target group without
an explicit group filter. That provisional result depended on the invalid
assumption that the resolved group had no independent trigger or current
constraint.

## Independent conformance critic

One fresh independent critic reviewed the full normative, source, runtime, and
counterfactual ledger. The critic was instructed to assume that an
implementation difference was not automatically an architecture defect.

**Critic disposition:** REPLACE.

Strongest objection: the resolved-group counterfactual was false because Book 4
references `monastery-testimony`, which is a member of the resolved group and
retains a current role. Resolution removes the active-commitment reason but does
not establish omission when explicit refs, current constraints, or an active
relation remain. D13 preserves relevant groups with historical members but does
not define group eligibility. The critic also separated relation disposition
from commitment disposition, treated the legacy selector as precedent rather
than authority, rejected fixture-wide lifecycle claims, and found the singular
`group_id` overwrite to be a separate issue because the group objects retain
both memberships.

## Critic reconciliation

| Objection | Assessment | Evidence | Effect |
| --- | --- | --- | --- |
| The resolved/no-trigger counterfactual ignores `monastery-testimony`. | VALID | Book 4 planning refs include the fact; runtime shows it in both groups and as current. | Remove the deterministic active→omit claim. |
| Commitment resolution does not imply relation rejection or group deletion. | VALID | `GlobalMapEntry.disposition=resolved`; `PressureGroupRelation.disposition=active`; no coupling rule in architecture. | Keep the group in the Map; do not infer a lifecycle. |
| D13 is a preservation contract, not a universal group-eligibility rule. | VALID | D13 requires historical-member preservation after a relevant group is selected. | Case C passes; it cannot settle B or D group lifting. |
| Legacy direct selector is not architecture authority. | VALID | Direct tests agree on resolved commitment history, but do not specify Map group projection. | Use as supporting precedent only. |
| The selector's singular `group_id` can overwrite shared membership. | PARTIAL | Runtime shows group objects preserve both member sets; entry-level pointer is last-relation-wins. | Record as separate projection ambiguity, not this audit's primary result. |
| Fixture behavior must not become universal pressure semantics or product evidence. | VALID | All evidence is one designed mechanical fixture; Superhero material is guardrail only. | No author-value, lifecycle, extraction, or scale claim. |

## Final disposition

**PRIMARY DISPOSITION: `INCONCLUSIVE`**

**PRIMARY SEAM: `FOCUS_SELECTION` contract boundary.**

The audit found no deterministic Map→Focus conformance defect. Global Map
preservation conforms, and fact-level Focus behavior preserves currentness,
explicit reactivation, and historical-member status.

Current Focus exposes pressure groups unconditionally, but the accepted
architecture does not define the group-level eligibility predicate needed to
judge that behavior as correct or incorrect. The existing cases also do not
establish that group-level eligibility is necessarily interpretive.

The result is an underspecified group-level Focus contract, not a demonstrated
implementation defect and not proof that no deterministic rule could exist.
Decision-specific pressure meaning may remain interpretive, consistent with
prior campaign evidence, but this audit does not prove that group-level
eligibility itself must be interpretive.

The claim boundary is explicit:

```text
CURRENT CODE HAS NO GROUP-LEVEL ELIGIBILITY FILTER
!=
CURRENT CODE VIOLATES A SPECIFIED ELIGIBILITY RULE

NO SPECIFIED DETERMINISTIC RULE
!=
NO DETERMINISTIC RULE COULD EVER EXIST
```

This is not a recommendation to delete resolved groups, drop historical
members, add a pressure lifecycle, or persist Decision Relevance. The current
code having no group-level eligibility filter is not equivalent to violating a
specified filter. Group existence in the Global Map remains distinct from
being warranted as current author-facing pressure, and a resolved target does
not make all associated history irrelevant.

## Implementation boundary

No implementation candidate is authorized. Do not modify
`build_global_map`, `select_focus_from_global_map`, `PressureGroupRelation`,
Pydantic models, fixtures, tests, extraction, ontology, scale, or product
explanations from this audit. Any future rule would require a separate owner
decision that first specifies whether `focus.groups` is an eligibility result
or a structural projection and how explicit member triggers, current member
roles, target commitment disposition, and relation disposition combine.

## Owner Gate closure

**OWNER GATE: CLOSED.**

The owner accepts the Global Map conformance result, the fact-level Focus
conformance result, the critic's rejection of the deterministic-gap hypothesis,
and the absence of a valid counterfactual. The owner revises the primary
disposition from `INTERPRETIVE_BOUNDARY` to `INCONCLUSIVE` because the evidence
establishes contract underspecification, not the impossibility of a
deterministic composition rule.

The group-level eligibility contract follow-up is **NOT SELECTED**. The
successor responsibility is **NONE SELECTED**. The next checkpoint is
**CAMPAIGN-LEVEL REASSESSMENT**.

| Field | Result |
| --- | --- |
| Primary disposition | `INCONCLUSIVE` |
| Primary seam | `FOCUS_SELECTION` contract boundary |
| Normative contract | Global Map may preserve derived pressure history and historical members; fact-level Focus preserves currentness and explicit triggers; group-level eligibility is not specified. |
| Active-pressure result | `contested-history` is an active derived group with current constraints and explicit Book 4 refs; preservation conforms, but the exact group predicate is not established. |
| Resolved-commitment result | `commitment-falsifier` remains a resolved Map entry and a derived group; its explicitly referenced current member prevents an omit conclusion. |
| Historical-member result | D13 conforms: `broken-lantern` remains a superseded historical member without becoming current. |
| Trigger-absent result | Both groups remain in the structural group collection; existing cases do not settle whether that collection is strict eligibility or structural projection. |
| Current Map behavior | Preservation and provenance conform; no Map deletion is warranted. |
| Current Focus behavior | Fact-level filtering conforms with current/relevant semantics; pressure-group inclusion is unconditional and contractually underspecified. |
| Smallest counterfactual | NONE. The active→resolved toggle leaves explicit member-trigger and current-member bases intact. |
| Independent critic | `REPLACE`; validly rejected the deterministic-gap counterfactual. |
| Architecture change required | NOT ESTABLISHED |
| Interpretive necessity | NOT DEMONSTRATED at the group-eligibility level |
| Implementation candidate | NO |
| Implementation authorized | NO |

## Qualification evidence

The source-qualified commands were run with `PYTHONPATH` pinned to the clean
research worktree so imports exercised this branch rather than the dirty main
checkout.

| Command | Exit | Evidence |
| --- | ---: | --- |
| `git diff --check` | 0 | No source/test edits were made. Git emitted only the normal LF-to-CRLF working-copy warning for the campaign-state file. |
| `python scripts/check.py --skip-pytest` | 0 | Validator suite 24/24 passed, 0 failed; repository validator passed with six non-critical workflow warnings; vendored contract OK; Ruff passed. |
| `pytest tests/test_series_repeated_map_focus.py -q` | 0 | 69 collected, 69 passed, 0 skipped, 0 xfailed, 0 xpassed, 0 failed, 0 errors. |
| `pytest tests/test_series_vertical_slice_global_map.py -q` | 0 | 19 collected, 19 passed, 0 skipped, 0 xfailed, 0 xpassed, 0 failed, 0 errors. |

An unqualified first run of the global-map test collected against the editable
package in the dirty main checkout and failed at import because that package
lacked the closure-era relation model. The pinned rerun above passed and is the
branch evidence. This is an environment-resolution issue, not a source
regression in the clean worktree.

## Next checkpoint

Return to campaign-level reassessment. Do not select a separate group-level
eligibility contract responsibility, implementation, ontology work, extraction,
scale work, author-value study, or prospective case from this audit.

OWNER_GATE_CLOSED
