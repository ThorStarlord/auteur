# Repeated Map/Focus V2 — Probe-Enabling Surface Implementation Plan (Boundary 2)

Status: revised per author approval (approval points 1–3 resolved below); awaiting
implementation approval. No production code has been written.

Scope anchor: [Boundary 2 design note](../design/repeated-map-focus-v2-probe-enabling-surface-boundary.md)
and the [Human Validation Contract](../product-validation/series-repeated-map-focus-v2-human-validation-contract.md).

## Base identities

```text
branch                         main
HEAD (verified this session)   1d92803a49133a1d18d0b3674eda4ff9c9cd25c1
qualified V2 capability SHA    2e066108db51ff4b42b41316d5ea5e8d627eef71  (ancestor; evidence preserved, never rewritten)
```

## 0. Independent blocker confirmation (read-only, on current main)

- **Blocker A — planning-intent entry:** `series journey plan-next-book`
  (`src/auteur/series/cli.py:237-242`) calls only `service.enter_book_planning(...)`.
  The service method `enter_repeated_book_planning(book_number, *, entered_by,
  intent, relevance_refs)` exists and fully validates (`vertical_slice_service.py:513-543`),
  but **no CLI path reaches it**. Confirmed gap.
- **Blocker B — accepted-fact discovery:** no accepted-fact listing/selector exists
  in the CLI, service, formatter, or tests. Confirmed gap.
- **Reuse anchors (no new concept):**
  - `SeriesVerticalSliceService.load_repeated_history_for_book(book)` already returns
    `AcceptedHistorySnapshot.accepted_fact_refs` — the exact revisioned accepted set
    through Book `N-1` (`vertical_slice_service.py:333-429`, refs built at 404-414).
  - `enter_repeated_book_planning` already enforces exact membership of relevance refs
    in accepted history (`vertical_slice_service.py:526-540`).
  - `load_accepted_realization_bundles` iterates deterministically (`sorted` artifact ids,
    `vertical_slice_store.py:958`); accepted realization refs are always revision 1
    (`vertical_slice_store.py:976-978`) — accepted bundles are immutable.
  - Accepted realization transition data is the plain-language source:
    `f"{subject}.{attribute} is {after}."` (already the Map summary form, `repeated_map_focus.py:401-403`).

## 1. Revised CLI interaction

### 1a. `journey accepted-facts` (read-only discovery)

```text
auteur series journey accepted-facts <project> --book N [--detail]
```

- Lists only **accepted** facts through Book `N-1`, in deterministic order
  (by Book, then realization bundle artifact id, then transition order).
- Default output per fact (selection token is user-facing, never hidden):

```text
[B1-02~K7M4Q9] monastery.testimony is preserved.
  Accepted in Book 1
```

- `--detail` additionally reveals the exact internal provenance
  (artifact id, revision, fact id) — opt-in only, mirroring `map`/`focus`.
- Read-only: nothing is written; proposed/unaccepted candidates
  (`burn-archive`, `ally-militia`, …) can never appear.

### 1b. `journey plan-next-book` — frozen argument invariant

```text
auteur series journey plan-next-book <project> --book N
    [--intent "plain-language Book-N planning intent"]
    [--relevance <selection-token>]        # repeatable, optional
```

| arguments                                    | behavior                                   |
|----------------------------------------------|--------------------------------------------|
| no `--intent`, no `--relevance`              | legacy `enter_book_planning` (unchanged)    |
| `--intent` with zero or more `--relevance`   | `enter_repeated_book_planning`              |
| `--relevance` without `--intent`             | clear CLI error, exit 1, **no persistence** |

No `enter-intent` command is added.

### 1c. Example journey (Book 4, the reactivation case)

```text
auteur series journey accepted-facts <project> --book 4
[B1-02~K7M4Q9] monastery.testimony is preserved.
  Accepted in Book 1
...
[B3-01~A9F2C1] archive.protection is treaty protected.
  Accepted in Book 3

auteur series journey plan-next-book <project> --book 4 \
  --intent "Return to the monastery testimony without breaking the protected archive." \
  --relevance B1-02~K7M4Q9 --relevance B3-01~A9F2C1
Entered planning intent for Book 4.

auteur series journey map <project> --book 4
Series Map: Book 4
... monastery.testimony is preserved.  (reactivated — why-now cites Book 4 intent)

auteur series journey focus <project> --book 4 --input <seed>
Series Focus: Book 4
This is a planning choice, not Book 4 canon.
```

## 2. Selection-token algorithm and invariants

**Role:** the selection token is a *presentation locator*, not an identity.
`AcceptedFactRef` remains the only identity/provenance. The token is computed,
never persisted, and rebuilt against the current accepted snapshot on every
listing/resolution. No registry exists.

**Shape:** `B{book_number}-{position:02d}~{fingerprint}` (e.g. `B1-02~K7M4Q9`).

- `book_number` + `position` = human-readable display position (per Book, 01-based,
  in the deterministic listing order). Orientation only — lookup uses the full token string.
- `fingerprint` = deterministic 6-char digest of the **exact revisioned ref**:

```python
fingerprint = sha256(f"{artifact_id}\0{revision}\0{fact_id}".encode()).hexdigest()[:6].upper()
```

- Position + fingerprint are both derived; the token string is unique per fact
  for a given accepted snapshot.

**Resolution (fail closed, no fuzzy fallback):**

```text
map = { selection_token_for(ref): [ref, ...] for ref in list_accepted_facts(book) }
resolve(token):
    refs = map.get(token, [])
    len(refs) == 0  -> ValueError: selection no longer identifies a current accepted fact
    len(refs) == 1  -> return refs[0]
    len(refs)  > 1  -> ValueError: selection is ambiguous (defensive; cannot occur by construction)
```

**Invariants (all required):**

1. Deterministic: same accepted snapshot ⇒ same tokens, same listing.
2. Token → exactly one exact `AcceptedFactRef` (revision included).
3. Current accepted-history snapshot is the **only** lookup source.
4. Source/revision change ⇒ old token resolves to 0 matches ⇒ invalid; it never
   silently points at a newer fact.
5. 0 matches fails; >1 matches/collision fails closed; no fuzzy matching, no
   aliases, no name parsing, no label inference (consistent with the standing
   authority invariant: exact equality only, never inferred identity).
6. Never persisted as narrative identity or authority; internal artifact id,
   revision, and fact id appear only under `--detail`.

**Naming:** helpers use `selection_token` terminology (never `friendly_key`):
`selection_token_for(ref)` (pure), `list_accepted_facts(book)`,
`resolve_accepted_fact_selection_token(book, token)`,
`format_accepted_facts(snapshot, *, detail)`.

## 3. Progressive disclosure contract (corrected)

```text
DEFAULT
  selection token      shown          (user needs it for --relevance)
  human summary        shown          (transition-derived: "subject.attribute is after.")
  source Book          shown

--detail
  artifact id          shown
  revision             shown
  fact id              shown
```

The selection token must **not** be hidden behind `--detail`.

## 4. Dependency-ordered TDD tasks

Each task lists expected files, the behavioral RED test first, existing
implementation to reuse, the smallest GREEN change, V1/V2 regressions, and
completion evidence.

### Task 0 — Books 2/3/4 CLI acceptance test (RED from the start)

**Files:** `tests/test_series_repeated_map_focus.py` — one top-level test,
`test_cli_books_2_3_4_probe_surface_journey`.

**RED first:** written before any production change. Initially it fails at the
surface layer (argparse `SystemExit` / non-zero return — the `accepted-facts`
command and the `--intent/--relevance` arguments do not exist yet). It stays RED
while Tasks 1–5 land and goes GREEN at Task 6.

**Behavior (through the real CLI, `main([...])`, reusing existing test helpers
`build_repeated_ledger`, `repeated_authority_snapshot`, `write_repeated_decision_seed`):**

- **Book 2** (ledger accepted through Book 1; fixture intent = founding-record):
  1. `accepted-facts --book 2` → exit 0; lists only Book 1 facts (tokens for
     `founding-record`, `monastery-testimony`, `broken-lantern`); no internal IDs.
  2. `plan-next-book --book 2 --intent "Make the forged founding record matter to lived memory." --relevance <founding-record token>` → exit 0.
  3. `map --book 2` → exit 0; `focus --book 2` → exit 0 (Book 2 uses the
     existing journey routes — surface reachability is the claim here).
  4. Assert persisted intent == `[founding-record@1]`; `load_accepted_book_direction(2) is None`;
     canonical state byte-identical.
- **Book 3** (ledger accepted through Book 2; fixture intent = admission-retracted):
  1. `accepted-facts --book 3` → exit 0; lists Book 1+2 facts only.
  2. `plan-next-book --book 3 --intent "Respond to the council's accepted retraction." --relevance <admission-retracted token>` → exit 0.
  3. `map --book 3` → exit 0, `Series Map: Book 3`, current retraction summary
     present (`council.archive_position is retracted admission.`), `public-admission`
     not presented as current.
  4. `focus --book 3 --input <seed>` → exit 0, `Series Focus: Book 3`,
     `This is a planning choice, not Book 3 canon.`
  5. Assert persisted intent == `[admission-retracted@1]`; no Book 3 Direction; canonical unchanged.
- **Book 4** (ledger accepted through Book 3; the reactivation case):
  1. `accepted-facts --book 4` → exit 0; **obtain the monastery token and the
     archive-protected token from the output** (`[B1-02~…] monastery.testimony is preserved.`,
     `[B3-01~…] archive.protection is treaty protected.`).
  2. `plan-next-book --book 4 --intent "Return to the monastery testimony without breaking the protected archive." --relevance <monastery token> --relevance <archive-protected token>` → exit 0.
  3. `map --book 4` → exit 0; `Series Map: Book 4`; `monastery.testimony is preserved.`
     present in active continuity with a why-now citing Book 4 planning
     (reactivated — the V2-qualified R3 disposition).
  4. `focus --book 4 --input <seed>` → exit 0; `Series Focus: Book 4`;
     `This is a planning choice, not Book 4 canon.`
  5. Assert persisted intent refs == `[monastery-testimony@1 (Book 1), archive-protected@1 (Book 3)]`;
     no Book 4 Direction; canonical byte-identical.
- **Authority non-mutation throughout:** `repeated_authority_snapshot(service)`
  (accepted/ + canonical + artifact-store roots) equal before the journey and
  after each step; workflow diff is limited to the expected planning entry +
  intent; proposals/derived writes (Focus proposal, derived context) are
  non-authoritative and outside the snapshot roots.
- Do **not** artificially reactivate the monastery in Books 2/3 — each Book uses
  its fixture-appropriate trigger; Book 4 is the reactivation case.

**Completion evidence:** test exists and is RED at Task 0; final GREEN at Task 6.

### Task 1 — selection token generation + resolution (service layer)

**Files:**
- `src/auteur/series/repeated_map_focus.py` — pure `selection_token_for(ref: AcceptedFactRef) -> str`.
- `src/auteur/series/vertical_slice_service.py` — `list_accepted_facts(book_number) -> list[AcceptedFactRef]`;
  `resolve_accepted_fact_selection_token(book_number, token) -> AcceptedFactRef`.
- `tests/test_series_repeated_map_focus.py` — unit tests.

**RED first:**
```python
def test_selection_token_resolves_to_exact_revisioned_ref(service):
    token = repeated_map_focus.selection_token_for(accepted_monastery_fact_ref())
    assert service.resolve_accepted_fact_selection_token(4, token) == accepted_monastery_fact_ref()

def test_list_accepted_facts_excludes_unaccepted_and_is_deterministic(service):
    facts = service.list_accepted_facts(4)
    fact_ids = {ref.fact_id for ref in facts}
    assert "burn-archive" not in fact_ids and "ally-militia" not in fact_ids
    assert service.list_accepted_facts(4) == facts          # deterministic
```
Also RED: an unknown token raises a clear invalid-selection error; a token for a
ref not in accepted history raises.

**Reuse:** `load_repeated_history_for_book(book).accepted_fact_refs`
(`vertical_slice_service.py:404-414`); `_fact_entry_id` helper style
(`repeated_map_focus.py:89-93`).

**Smallest GREEN:** `selection_token_for` = sha256 digest over
`f"{artifact_id}\0{revision}\0{fact_id}"`, first 6 uppercase hex chars;
`list_accepted_facts` returns snapshot `accepted_fact_refs` in snapshot order;
`resolve_accepted_fact_selection_token` builds the token→ref map per Section 2
and raises `ValueError` (clear message) for 0 matches, `ValueError` for >1 (defensive).

**Regressions:** `test_book_n_history_includes_only_accepted_sources_through_previous_book`,
`test_book_n_history_rejects_unaccepted_sources`,
`test_recent_and_unaccepted_material_never_enters_corrected_map`,
`test_current_state_evidence_does_not_mutate_canonical_state`.

**Completion evidence:** focused pytest selection green.

### Task 2 — accepted-facts listing formatter

**Files:**
- `src/auteur/series/vertical_slice_formatters.py` —
  `format_accepted_facts(snapshot: AcceptedHistorySnapshot, *, detail: bool = False) -> str`.
- `tests/test_series_repeated_map_focus.py`.

**RED first:**
```python
def test_format_accepted_facts_default_shows_token_summary_book(service):
    text = format_accepted_facts(service.load_repeated_history_for_book(4))
    assert "[B1-02~" in text and "monastery.testimony is preserved." in text and "Accepted in Book 1" in text
    assert "realization-bundle-book-1-realization" not in text   # internal artifact hidden
    assert "revision" not in text                                 # internal revision hidden
    assert "monastery-testimony" not in text                      # internal fact id hidden

def test_format_accepted_facts_detail_reveals_exact_provenance(service):
    text = format_accepted_facts(service.load_repeated_history_for_book(4), detail=True)
    assert "artifact realization-bundle-book-1-realization" in text
    assert "revision 1" in text and "fact monastery-testimony" in text
```
Also RED: `burn-archive` / `ally-militia` never appear (they are not in the snapshot).

**Reuse:** `AcceptedHistorySnapshot` realizations/refs; the transition summary form
`f"{subject}.{attribute} is {after}."` already used by the Map
(`repeated_map_focus.py:401-403`); `selection_token_for` (Task 1);
`_format_continuity_source_ref` for the detail branch (`vertical_slice_formatters.py:18-26`).

**Smallest GREEN:** iterate `snapshot.realizations` (deterministic order) and their
transitions; emit per fact:

```text
[{token}] {subject}.{attribute} is {after}.
  Accepted in Book {book_number}
```

`detail=True` appends `  Accepted source: artifact {artifact_id}, revision {revision}, fact {fact_id}`.
The selection token is part of the **default** output (Section 3).

**Regressions:** `test_format_repeated_map_groups_current_book_why_now_and_hides_history`,
`test_format_repeated_map_detail_preserves_provenance_and_history`,
`test_cli_repeated_map_uses_real_service_context`.

**Completion evidence:** formatter-focused pytest selection green, including the `--detail` branch.

### Task 3 — CLI `journey accepted-facts`

**Files:** `src/auteur/series/cli.py`; `tests/test_series_repeated_map_focus.py`.

**RED first:**
```python
def test_cli_accepted_facts_lists_books_123_without_detail(tmp_path, capsys):
    service = build_repeated_ledger(tmp_path)
    code = main(["series", "journey", "accepted-facts", str(tmp_path), "--book", "4"])
    assert code == 0
    out = capsys.readouterr().out
    assert "[B1-02~" in out and "monastery.testimony is preserved." in out
    assert "revision" not in out and "realization-bundle-book-1-realization" not in out
    assert "burn-archive" not in out
```
Also RED: `--detail` reveals provenance; after the command, authority snapshot and
canonical state are unchanged and `load_accepted_book_direction(4) is None`.

**Reuse:** the `journey` subparser/dispatch pattern (`cli.py:70-157`, `handle_series_journey_command`);
`format_accepted_facts` (Task 2); `load_repeated_history_for_book`; existing try/except → `Error: …`, exit 1.

**Smallest GREEN:** register `accepted-facts` parser (`project`, `--book` required int,
`--detail` flag, mirroring `map`); dispatch branch calls
`service.load_repeated_history_for_book(args.book)` → `format_accepted_facts(snapshot, detail=args.detail)` → return 0.

**Regressions:** `test_cli_repeated_map_uses_real_service_context`,
`test_cli_repeated_focus_requires_explicit_seed_input`.

**Completion evidence:** CLI pytest selection green; non-mutation asserted.

### Task 4 — CLI `plan-next-book --intent/--relevance` (frozen invariant)

**Files:** `src/auteur/series/cli.py`; `tests/test_series_repeated_map_focus.py`.

**RED first:**
```python
def test_cli_plan_next_book_accepts_intent_and_selection_token(tmp_path, capsys):
    service = build_repeated_ledger(tmp_path)
    token = repeated_map_focus.selection_token_for(accepted_monastery_fact_ref())
    code = main(["series", "journey", "plan-next-book", str(tmp_path), "--book", "4",
                 "--intent", "Return to the monastery testimony as a route back to lived memory.",
                 "--relevance", token])
    assert code == 0
    intent = service.store.load_book_planning_intent(4)
    assert intent.intent == "Return to the monastery testimony as a route back to lived memory."
    assert intent.relevance_refs == [accepted_monastery_fact_ref()]
    assert service.load_accepted_book_direction(4) is None

def test_cli_plan_next_book_relevance_without_intent_fails_closed(tmp_path, capsys):
    code = main(["series", "journey", "plan-next-book", str(tmp_path), "--book", "4",
                 "--relevance", "B1-02~K7M4Q9"])
    assert code == 1
    assert "requires --intent" in capsys.readouterr().out
    assert service.store.load_book_planning_intent(4) is None
    assert service.store.load_planning_entry(4) is None          # no partial write
```
Also RED: no args → legacy behavior preserved (only a `PlanningEntry`, no intent file).

**Reuse:** `enter_repeated_book_planning` (`vertical_slice_service.py:513-543` — entry +
intent persistence + accepted-history membership validation); `enter_book_planning`
(legacy path); `resolve_accepted_fact_selection_token` (Task 1).

**Smallest GREEN:** add `--intent` (optional str) and `--relevance` (optional,
`action="append"`). Dispatch:
```python
if args.relevance and args.intent is None:
    raise ValueError("--relevance requires --intent")
if args.intent is not None:
    refs = [service.resolve_accepted_fact_selection_token(args.book, token)
            for token in (args.relevance or [])]
    intent = service.enter_repeated_book_planning(
        args.book, entered_by=_CLI_AUTHOR, intent=args.intent, relevance_refs=refs)
    print(f"Entered planning intent for Book {args.book}.")
else:
    entry = service.enter_book_planning(args.book, entered_by=_CLI_AUTHOR)
    print(f"Entered exploratory planning for Book {entry.book_number}.")
```
All tokens resolve **before** any persistence (no partial writes on failure).

**Regressions:** `test_book_n_planning_intent_references_accepted_fact_without_authority`,
`test_planning_intent_rejects_fact_outside_accepted_history`,
`test_r3_book_four_reactivates_old_fact_from_planning_intent`,
`test_r5_map_focus_does_not_mutate_authority`.

**Completion evidence:** CLI tests green, including the frozen-invariant cases.

### Task 5 — stale / unknown / unaccepted / ambiguous barrier

**Files:** `src/auteur/series/vertical_slice_service.py` (resolution error surface);
`tests/test_series_repeated_map_focus.py`.

**RED first (negative scenarios, each asserted with exit 1, a clear message, and
no `BookPlanningIntent`, no planning entry, no Book Direction, canonical unchanged):**

- **Unknown token:** fabricated string (`B1-99~ZZZZZZ`) → invalid-selection error.
- **Unaccepted candidate:** unaccepted material can never produce a token (listing
  excludes it); feeding a bare candidate-like string → error, no write.
- **Genuine stale — source revision changed (supported mechanics):**
  1. `accepted-facts --book 4`, capture a valid token T;
  2. change the accepted source via the existing sidecar-revision bump pattern
     (`corrupt_book_two_metadata`, `tests/test_series_repeated_map_focus.py:310-318`)
     applied to the Book 1 realization bundle (or the Book 3 bundle for the
     archive-protected token);
  3. `plan-next-book --book 4 --intent … --relevance T` → clear error, exit 1,
     **no planning intent written**.
     Accepted realization refs are always revision 1 and immutable
     (`vertical_slice_store.py:976-978`), so a changed revision cannot silently
     re-point the old token: history validation fails closed with a clear message,
     or resolution fails with 0 matches — either layer, the CLI surfaces a specific
     error and writes nothing.
- **Genuine stale — snapshot-bound token:** build ledger L1, capture T for
  `monastery-testimony`; build ledger L2 where the Book 1 realization was accepted
  under a **different candidate id** (different `artifact_id`, same-named fact —
  supported fixture mechanics via `model_copy` on the loaded `RealizationCandidate`,
  same accept flow as `build_repeated_ledger`); `resolve_accepted_fact_selection_token(4, T)`
  against L2 raises invalid (0 matches) — proves the token is bound to the exact
  revisioned ref, not to a name.
- **Collision fail-closed (defensive):** unit test monkeypatches
  `selection_token_for` to return one token for two different refs and asserts
  resolution raises an ambiguity error (>1 matches).

**Reuse:** `enter_repeated_book_planning` membership validation; `corrupt_book_two_metadata`;
`repeated_authority_snapshot`; Section 2 fail-closed matrix.

**Smallest GREEN:** ensure `resolve_accepted_fact_selection_token` raises
`ValueError` with a specific message for 0 matches and for >1 matches; dispatch
resolves all tokens before persisting (Task 4 already guarantees ordering);
no other source change expected.

**Regressions:** `test_stale_repeated_focus_proposal_cannot_be_exercised`,
`test_planning_intent_rejects_fact_outside_accepted_history`,
`test_fact_identity_distinguishes_duplicate_ids_across_accepted_bundles`,
`test_current_book_proposal_store_rejects_leading_zero_identity_alias`.

**Completion evidence:** stale + unknown + unaccepted + collision tests green with
zero-write assertions.

### Task 6 — final GREEN integration proof (no new RED)

**Files:** `tests/test_series_repeated_map_focus.py` — the Task 0 acceptance test.

**Behavior:** the top-level Books 2/3/4 CLI journey test now passes end-to-end
through `main(...)` for all three Books, with authority non-mutation assertions.
This proves the required statement:

> The Books 2–4 repeated journey is reachable through the shipped CLI without
> knowledge of internal identifiers.

**Regressions (full gate before qualification):** the complete
`tests/test_series_repeated_map_focus.py` suite (R-series, formatter, CLI,
authority, stale/ambiguous), plus the V1/V2 suites in Section 6.

**Completion evidence:** full focused suite + acceptance test green.

## 5. RED→GREEN sequence summary

```text
Task 0: full Books 2–4 CLI acceptance test        -> RED (surface does not exist)
Task 1: selection_token_for / list / resolve       -> unit RED -> GREEN
Task 2: format_accepted_facts                      -> unit RED -> GREEN
Task 3: CLI accepted-facts                         -> CLI RED -> GREEN
Task 4: plan-next-book --intent/--relevance        -> CLI RED -> GREEN (frozen invariant)
Task 5: stale/unknown/unaccepted/ambiguous barrier -> RED -> GREEN (fail closed)
Task 6: acceptance proof                           -> GREEN (Task 0 test passes; no new RED)
```

## 6. Regression and qualification strategy

**Focused Boundary-2 tests (new):** all additions to
`tests/test_series_repeated_map_focus.py` from Tasks 0–5 (token registry, listing
formatter, `accepted-facts` CLI, `plan-next-book` invariant, stale/ambiguous
barrier, Books 2/3/4 CLI journey).

**V2 / V1 regression gates (run in full before qualification):**
`tests/test_series_repeated_map_focus.py`, `tests/test_series_vertical_slice_service.py`,
`tests/test_series_vertical_slice_models.py`, `tests/test_series_vertical_slice_cli.py`,
`tests/test_series_vertical_slice_e2e.py`, `tests/test_provenance_pilot.py`,
`tests/test_story_state_commands.py`, `tests/test_story_state_manager.py`.

**Complete source qualification (new exact candidate):** fresh worktree off
`1d92803`; full `pytest`; `scripts/check.py` (validators + ruff — ruff is required
on the merge path) with baseline classification against `1d92803` per the
baseline-failure policy (KNOWN BASELINE vs REGRESSION vs SHIFTED);
`scripts/release_evidence.py` produces a new evidence JSON naming the **new** SHA.

**Installed-wheel qualification (same new SHA):** `scripts/verify_wheel.py` builds
and installs the wheel from the exact new candidate and runs the installed checks
(import/version, pack list/inspect, recommendation + durability, zero
pre-acceptance mutation, explicit acceptance mutation, restart persistence,
pack version/hash, genre validation/diagnosis).

**Evidence boundary preserved:** `2e066108…` remains the historical **V2
application capability** qualification and is never rewritten. The new evidence
file records the **probe-enabled production surface** qualification at the new
SHA — because production CLI/service seams change, the brief's distinction between
the two qualifications is preserved.

## 7. Approval decisions (resolved)

1. **CLI shape — approved:** extend `plan-next-book` with `--intent` +
   repeatable `--relevance`; frozen invariant per Section 1b; no `enter-intent`.
2. **Selection token — approved (replaces the earlier `artifact_id#fact_id`
   friendly key):** Section 2 design; internal provenance visible only under
   `--detail`; helpers renamed to `selection_token` terminology.
3. **Progressive disclosure — approved:** Section 3; the token is user-facing and
   never hidden behind `--detail`.

## 8. Explicitly deferred machinery (non-goals, unchanged)

No general history browser; no full-text/semantic/fuzzy search; no relevance
ranking; no universal fact registry or second identity scheme; no new Domain
Model entities for the CLI; no finite/uncertain Series extent; no
recommendation-content generation; no free-form Book-N Direction; no intra-Book
Map/Focus; no browser/TUI/editor redesign; no universal
lifecycle/dependency/recommendation machinery; no ADR/domain-model cleanup
unrelated to the two blockers.

Pre-existing user-dirty tracked and untracked files are left untouched; the work
lands only on the files listed above and is developed in a fresh worktree so the
dirty `main` checkout is never modified in place.

## 9. Plan path

```text
docs/superpowers/plans/2026-08-25-repeated-map-focus-v2-probe-enabling-surface-implementation.md
```
