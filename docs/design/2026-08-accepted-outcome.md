# Implementation Design — Accepted-Outcome: `chosen` membership field (M1)

> Phase: implementation design. Mechanism **M1 — optional `chosen: list[alternative_id]`
> on AuthorDecision**, agent-selected under the standing delegated-authority envelope.
> Discovery @ `3620d9e` on `discovery/accepted-outcome`. Base SHA: d9926b1 (origin/main,
> PR #73 merged). Human-demonstrated value: explicit outcome materially improves
> continuity (reaction recorded verbatim in the discovery). Reuse/extension of shipped
> AuthorDecision; no escalation triggers.

## 0. Design hypothesis (binding)

An accepted decision record should be able to answer "what did I decide?" The smallest
explicit, author-controlled representation is a `chosen` membership list — the author
states which alternative(s) they selected; combined with the existing authored
`combination_direction`, the full kept/cut outcome is unambiguous. Absent `chosen` = the
decision is still open (unchanged, backward compatible).

## 1. Field (binding): `chosen: list[str] | None`

On `AuthorDecision` (`models.py`), default `None` (unresolved — status quo). Closed
validation (fail-closed, in `_validate_semantics`):

1. `chosen` may be `None`/absent (open decision) or a non-empty list of distinct refs.
2. Every member must be a declared `alternative_id` (no invention, no inference).
3. Cardinality matches the combination rule:
   - `one_of` → exactly 1 member;
   - `choose_k_of_n` → exactly `k` members (the chosen set).
4. `combination_direction` is NOT required by `chosen` (membership is meaningful without
   a kept/cut operation — e.g. one_of where the author has not yet stated kept-vs-cut);
   and `combination_direction` alone never implies membership (existing invariant
   preserved: operation ≠ member).

## 2. Consumer behavior (binding): echo-only, provenance-labeled

- The consumer surfaces `chosen` as a provenance-labeled authored fact; it does NOT
  mutate canonical Identity/Blueprint, does NOT drive propagation, does NOT rank.
- `decision view` gains an authored line: `Chosen (authored): [...]` and JSON
  `authored.chosen`.
- `evaluate`/consequences are unchanged except: composed per-alternative findings are
  NOT filtered or ranked by `chosen`. The chosen fact is surfaced, never applied.
- Acceptance: `accept` records the chosen members into the acceptance record
  (`write_acceptance_record` gains `chosen: [...]`), so the resolved outcome survives
  acceptance provenance. No canonical mutation.

## 3. Controls and golden discriminators (binding for qualification)

1. **Parse chosen one_of** — `chosen: [signe_marriage]` on a `one_of` cut decision parses;
   view shows it; JSON carries it.
2. **Parse chosen choose_k_of_n** — exactly-k set parses (e.g. k=2 → two members).
3. **Absent chosen** — `None` (open decision); existing artifacts byte-identical; no
   behavior change (regression).
4. **Fail-closed: unknown member** — a `chosen` ref not in `alternative_ids` rejected.
5. **Fail-closed: cardinality** — `one_of` with 2 members; `choose_k_of_n` with k≠size;
   duplicate members — all rejected.
6. **Direction ≠ membership** — `combination_direction: cut` alone (no `chosen`) does
   NOT surface any member; membership is never inferred.
7. **Central invariant** — composed consequences byte-identical with/without `chosen`
   (echo-only); `chosen` adds only the provenance-labeled authored fact.
8. **Acceptance provenance** — accepting a decision with `chosen` records it in the
   acceptance record; accepting an open decision (no `chosen`) is unchanged.
9. **Backward compat** — existing fixtures (case-d/e/one-of/goal-significance) parse and
   evaluate byte-identical (none carry `chosen`).

## 4. Out of scope (binding)

Downstream propagation/application of `chosen`; automatic Blueprint mutation;
supersession/revision semantics; ranking/recommendation; prose inference; canonical
promotion of decision-local significance.

## 5. Verification plan

- TDD: RED tests first (controls 1–9); full author-decisions suite for regression.
- Full verification stack on the merge path: pytest (categories separately), ruff,
  `scripts/check.py`.
- Independent review; autonomous merge when scope matches, CI passes, review has no
  unresolved substantive finding, backward-compat + anti-inference controls pass, exact
  reviewed head == merged head.

## 6. Stop point

None (delegated authority). Proceed to construction.
