# Repeated Map/Focus V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Implement and qualify the smallest repeated Series Map/Focus capability that derives a compact, accepted-source-backed continuity view and one state-compatible bounded next decision when an author begins planning Book N > 1.

**Architecture:** Preserve accepted Series Direction, accepted Book Direction, accepted realization, and Canonical State as the only narrative authority. Add a deterministic accepted-history read seam, a local projection-only relevance selector with pressure grouping, and a current-Book bounded proposal seam. Keep relevance dispositions local to this projection; do not introduce universal lifecycle, dependency, or recommendation frameworks, and do not relax the existing full-Series SeriesIdentity/BookPlan path.

**Tech Stack:** Python >=3.11, Pydantic v2, PyYAML, pytest, existing argparse CLI, file-backed .auteur storage, and existing ArtifactStore provenance/revision/dependency mechanisms.

---

## Frozen inputs and planning-horizon rule

Behavioral authority:

    docs/acceptance/series-repeated-map-focus-capability-contract-v1.md

Repository constraint:

    docs/design/series-repeated-map-focus-implementation-boundary-v1.md

Also preserve:

    docs/adr/065-domain-model-v1-scope-and-closure.md
    docs/adr/066-series-vertical-slice-ux-v1.md
    docs/adr/067-sparse-series-direction-boundary.md
    docs/adr/068-series-vertical-slice-cli-surface.md
    docs/adr/069-bounded-book-two-decision-actions.md
    docs/adr/070-sparse-series-storage-boundary.md
    docs/narrative-architecture.md
    docs/engineering/release-qualification.md

Qualified V1 code candidate:

    d3bb1eb37d065b34c132771cf19a0856e60d0cea

The current main checkout contains documentation commits after that candidate.
Source and test bytes must be compared explicitly before implementation and
before final qualification.

Freeze this planning horizon:

    Opening Book N Map/Focus uses accepted narrative authority only through
    Book N - 1.

    Present Book-N planning intent or a non-authoritative proposal may trigger
    relevance, but is not narrative authority.

    Accepted Book-N Direction or realization is not required to derive the
    opening Book-N Map/Focus.

    Repeated intra-Book planning checkpoints remain deferred.

Therefore:

    Book 2 opening -> accepted history through Book 1
    Book 3 opening -> accepted history through Book 2
    Book 4 opening -> accepted history through Book 3

The current acceptance contract uses some future Book Direction and realization
references as if they were already accepted at the opening checkpoint. Task 1
corrects that chronology in the acceptance document before production
implementation. The historical synthetic probe report remains historical
evidence; it is not silently rewritten.

## Scope and stop conditions

This plan does not implement:

- finite, uncertain, expanding, or contracting Series extent;
- intra-Book Map/Focus checkpoints;
- a universal Lifecycle abstraction for narrative entities;
- universal Direction or inheritance;
- semantic text inference, LLM relevance ranking, or numerical attention;
- a general dependency/event graph;
- a universal recommendation engine or Author Decision aggregate;
- free-form Book Direction from Focus;
- a browser/editor redesign; or
- changes to SeriesIdentity, BookPlan, compiler, Bible, graph, or legacy
  full-Series CLI semantics.

Stop and return to architecture review if implementation requires:

1. changing the meaning of ArtifactStore Lifecycle;
2. making continuity relevance authoritative;
3. relaxing or reinterpreting SeriesIdentity/BookPlan;
4. inventing accepted Book-N authority before the opening Map/Focus;
5. inferring resolution, reactivation, pressure membership, or compatibility
   from prose instead of explicit references/rules; or
6. creating universal lifecycle, dependency, relevance, or recommendation
   machinery for this ledger.

## File map

    docs/acceptance/series-repeated-map-focus-capability-contract-v1.md
        Correct R1-R3 chronology to the frozen planning horizon.

    src/auteur/series/vertical_slice_models.py
        Add only narrow payload fields/DTOs for explicit resolution, planning
        intent, and proposal compatibility.

    src/auteur/series/repeated_map_focus.py
        Pure/read-side accepted-history snapshot, current-state evidence, local
        dispositions, selector, grouping, why-now, and compatibility checks.
        No file I/O and no authority mutation.

    src/auteur/series/vertical_slice_store.py
        Persist workflow intent and derived repeated context under the existing
        vertical-slice store; delegate artifact metadata to ArtifactStore.

    src/auteur/series/vertical_slice_service.py
        Orchestrate accepted-history loading, planning intent, repeated context,
        bounded Focus, freshness, and non-authoritative actions.

    src/auteur/series/vertical_slice_formatters.py
        Render grouped current-Book Map/Focus with progressive disclosure.

    src/auteur/series/cli.py
        Dispatch the capability only; no relevance or authority logic.

    tests/test_series_repeated_map_focus.py
        Contract-level red/green tests for R1-R5 and the horizon boundary.

    tests/test_series_vertical_slice_models.py
    tests/test_series_vertical_slice_service.py
    tests/test_series_vertical_slice_cli.py
    tests/test_series_vertical_slice_e2e.py
        V1 compatibility and regression coverage.

    tests/fixtures/repeated_map_focus_v2/
        Corrected chronological ledger, expected projections, and deterministic
        decision seeds.

    docs/engineering/series-repeated-map-focus-qualification-v2.md
        Exact candidate and qualification evidence.

Proposed structure classification:

| Structure | Classification | Boundary |
|---|---|---|
| Accepted-history snapshot DTO | Pure generalization | Read-only input; never authority. |
| AcceptedFactRef | Narrow representation required by R2/R3 | Points to an accepted fact/transition for projection or trigger validation. |
| BookPlanningIntent | Narrow representation required by the horizon rule | Workflow input; never accepted Book Direction. |
| Local relevance disposition | Narrow representation required by R1-R3 | One derivation only; not ArtifactStore Lifecycle. |
| Continuity entry/group | Narrow representation required by grouping | Projection output; not a universal PressureGroup. |
| Current-state evidence | Narrow representation required by supersession | Derived from accepted history; does not alter CanonicalState. |
| Current-Book proposal path | Pure generalization | Reuses bounded non-authoritative decision semantics. |
| Universal lifecycle/dependency/recommendation framework | Machinery to defer | Stop if required. |

## Dependency order

    0  baseline identity and V1 preflight
       |
    1  correct acceptance-contract chronology
       |
    2  accepted-history read seam
       |
    3  explicit resolution and Book-N planning intent
       |
    4  current-state evidence and supersession
       |
    5  lifecycle-aware local selector
       |
    6  pressure grouping and why-now
       |
    7  derived-context persistence and rebuild
       |
    8  current-Book Focus proposal seam
       |
    9  compatibility and freshness barrier
       |
    10 current-Book Map/Focus presentation and CLI
       |
    11 adversarial R1-R5 end-to-end qualification
       |
    12 exact-candidate qualification and handoff

Every production implementation task begins with a specific failing behavioral
test, records red, implements the smallest behavior, runs focused and relevant
regression tests, and commits only its bounded slice. Tasks 0 and 1 are
qualification/documentation gates, not production implementation tasks.

---

## Task 0: Establish the qualified V1 baseline and implementation worktree

Files:

- Read: AGENTS.md
- Read: docs/engineering/release-qualification.md
- Run: scripts/verify-agent-workspace.ps1
- No production source or test changes.

Reuse the exact qualified V1 candidate and prior qualification evidence.

- [ ] Step 1: Verify repository identity.

Run from H:\GithubRepositories\auteur:

    git rev-parse --show-toplevel
    git rev-parse --git-common-dir
    git rev-parse HEAD
    git branch --show-current

Expected: root H:/GithubRepositories/auteur, common directory .git, and the
current main HEAD recorded. Stop if another Git universe is active.

- [ ] Step 2: Create an isolated implementation worktree.

    git worktree add '.worktrees/repeated-map-focus-v2' -b 'feat/repeated-map-focus-v2' main

Record:

    git rev-parse HEAD
    git merge-base HEAD d3bb1eb37d065b34c132771cf19a0856e60d0cea
    git diff --exit-code d3bb1eb37d065b34c132771cf19a0856e60d0cea -- src tests

Expected: source/test diff is empty. Documentation commits after the qualified
code candidate do not invalidate code baseline bytes.

- [ ] Step 3: Prove the active import path.

    $repeatedMapRoot = (git rev-parse --show-toplevel)
    $repeatedMapSrc = Join-Path $repeatedMapRoot 'src'
    $repeatedMapCode = "import sys; from pathlib import Path; sys.path.insert(0, r'$repeatedMapSrc'); import auteur; p=Path(auteur.__file__).resolve(); expected=Path(r'$repeatedMapSrc').resolve(); assert expected in p.parents, f'{p} is not under {expected}'; print(p)"
    & 'C:\Python314\python.exe' -c $repeatedMapCode

Expected: auteur.__file__ is under the implementation worktree src.

- [ ] Step 4: Rerun the relevant V1 baseline before mutation.

    $env:PYTHONPATH = "$repeatedMapRoot;$repeatedMapSrc"
    & 'C:\Python314\python.exe' -m pytest tests/test_series_vertical_slice_cli.py tests/test_series_vertical_slice_e2e.py tests/test_series_vertical_slice_models.py tests/test_series_vertical_slice_service.py tests/test_provenance_pilot.py tests/test_story_state_commands.py tests/test_story_state_manager.py -ra

Record collected, passed, skipped, xfailed, xpassed, failed, and errors
separately. The prior candidate produced 156 passed in the parallel focused
matrix and 97 passed in the service/e2e subset; record actual current counts.

- [ ] Step 5: Freeze baseline evidence.

Record root, common directory, HEAD, branch, Python executable, import path,
qualified code ancestor, source/test diff result, and focused test categories.
Do not commit a qualification claim yet.

Done evidence: isolated worktree/import identity verified; relevant V1 baseline
rerun before mutation; source/test baseline matches the qualified candidate.

Commit: none.

---

## Task 1: Correct the acceptance-contract chronology before implementation

Files:

- Modify: docs/acceptance/series-repeated-map-focus-capability-contract-v1.md
- Read: docs/product-validation/series-vertical-slice-v1-synthetic-repeated-map-focus-probe.md
- No production source changes.

Classification: documentation correction required by the frozen planning-horizon
rule; not a new domain abstraction.

- [ ] Step 1: Correct R1 to stop at accepted Book 1 history.

At opening Book 2:

    accepted: series-direction@1
    accepted: book-1-direction@1
    accepted: book-1-realization@1/*
    not accepted: book-2-direction
    not accepted: book-2-burn-archive

Book 2 Direction may be a proposal after Map/Focus, but cannot be required to
derive opening Book 2 Map/Focus.

- [ ] Step 2: Correct R2 to stop at accepted Book 2 history.

Put the council admission and later retraction in accepted Book 2 realization
history, as ordered transitions in one accepted Book 2 realization bundle or
as ordered accepted Book 2 bundles only if existing state-order rules allow it
without introducing intra-Book planning.

At opening Book 3:

    accepted through Book 2: Book 2 Direction and realization history
    not accepted: Book 3 Direction
    not accepted: Book 3 realization

Book 3 planning intent may point to the accepted retraction but is not accepted
Book 3 Direction.

- [ ] Step 3: Correct R3 to use a non-authoritative Book 4 trigger.

At opening Book 4:

    accepted through Book 3: Book 3 Direction and realization history
    not accepted: Book 4 Direction
    present trigger: Book 4 planning intent or non-authoritative proposal

The trigger explicitly references accepted monastery testimony.

- [ ] Step 4: Add the contract invariant.

Add:

    Opening Book-N Map/Focus uses accepted narrative authority only through
    Book N - 1. Present Book-N planning intent may trigger relevance but cannot
    be used as accepted Book-N authority.

Do not rewrite the historical probe report. Note in the contract that this is a
planning-horizon correction.

- [ ] Step 5: Review the corrected scenarios against Domain Model V1.

Confirm:

    authority != relevance
    currentness != relevance
    old != irrelevant
    derived continuity != canon
    Focus action != Book Direction acceptance

Done evidence: R1-R3 are temporally executable without accepted Book-N Direction
or realization; no code changed.

Commit:

    docs: correct repeated map focus planning horizon

### Test harness defined before Task 2

Create these helpers in `tests/test_series_repeated_map_focus.py` before the
first red test. They are test fixtures, not production service methods:

    def build_repeated_ledger(tmp_path: Path) -> SeriesVerticalSliceService:
        service = SeriesVerticalSliceService(tmp_path)
        accept_fixture_series_direction(service)
        accept_fixture_book_one_and_realization(service)
        accept_fixture_book_two_and_realization(service)
        accept_fixture_book_three_and_realization(service)
        enter_fixture_planning_intents(service)
        return service

    def derive_repeated_context(
        service: SeriesVerticalSliceService, book_number: int
    ) -> RepeatedBookPlanningContext:
        return service.derive_repeated_book_context(book_number)

    def accepted_monastery_fact_ref() -> AcceptedFactRef:
        return AcceptedFactRef(
            artifact_id="book-1-realization",
            revision=1,
            fact_id="monastery-testimony",
        )

    def authority_snapshot(service: SeriesVerticalSliceService) -> tuple[object, ...]:
        return (
            service.load_accepted_series_direction(),
            service.store.load_accepted_realization_bundles(),
            service.load_canonical_state(),
        )

The fixture helpers load the corrected YAML ledger and call only existing
explicit proposal/acceptance service operations. `enter_fixture_planning_intents`
stores Book 2, Book 3, and Book 4 workflow intent, with the Book 4 intent
referencing `accepted_monastery_fact_ref()`. It never accepts Book 4 Direction.

Add these mutation helpers for negative tests, each operating on a temporary
project and using the public test fixture/service boundary:

    write_unaccepted_book_direction_proposal(service, book_number=3)
    corrupt_book_two_metadata(service)
    accept_unrelated_outcome(service)
    accept_additional_book_three_state(service)

The first writes a proposal only, the second makes source metadata fail the
existing validator, the third accepts an outcome with no resolution ID, and the
fourth changes an accepted Book 3 state so an existing Book 4 proposal becomes
stale. They must not be added as production methods.

Decision helpers load deterministic fixture seeds:

    book_three_decision_seed()
    book_four_decision_seed()
    book_four_burn_archive_recommendation_seed()

Each returns `RepeatedDecisionSeed` with at least two options, a recommendation,
rationale, and a distinct tradeoff per option.

---

## Task 2: Add the accepted-history read seam

Files:

- Modify: src/auteur/series/vertical_slice_service.py
- Modify: src/auteur/series/vertical_slice_store.py
- Create: src/auteur/series/repeated_map_focus.py
- Test: tests/test_series_repeated_map_focus.py
- Fixtures: tests/fixtures/repeated_map_focus_v2/

Classification: read-only accepted-history snapshot; no authority aggregate.

Reuse _accepted_series_source, _accepted_book_source,
load_accepted_realization_bundles, validate_book_context_source, ArtifactRef,
ArtifactStore revision/hash checks, and rebuild_canonical_state.

- [ ] Step 1: Write failing tests.

    def test_book_n_history_includes_only_accepted_sources_through_previous_book(tmp_path):
        service = build_repeated_ledger(tmp_path)
        snapshot = service.load_repeated_history_for_book(3)
        assert [book.direction.book_number for book in snapshot.books] == [1, 2]
        assert all(bundle.book_number <= 2 for bundle in snapshot.realizations)
        assert snapshot.planning_book_number == 3

    def test_book_n_history_rejects_unaccepted_sources(tmp_path):
        service = build_repeated_ledger(tmp_path)
        write_unaccepted_book_direction_proposal(service, book_number=3)
        snapshot = service.load_repeated_history_for_book(3)
        assert all(book.direction.book_number <= 2 for book in snapshot.books)
        assert snapshot.planning_book_number == 3

    def test_book_n_history_validates_current_source_revisions(tmp_path):
        service = build_repeated_ledger(tmp_path)
        corrupt_book_two_metadata(service)
        with pytest.raises(ValueError, match='accepted.*revision|source metadata'):
            service.load_repeated_history_for_book(3)

- [ ] Step 2: Run the tests and verify red.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k history -q

Expected: FAIL because no repeated-history snapshot operation exists.

- [ ] Step 3: Add the smallest read-only snapshot.

    @dataclass(frozen=True)
    class AcceptedHistorySnapshot:
        planning_book_number: int
        series: AcceptedSeriesDirection
        series_ref: ArtifactRef
        books: tuple[AcceptedBookDirection, ...]
        book_refs: tuple[ArtifactRef, ...]
        realizations: tuple[AcceptedRealizationBundle, ...]
        realization_refs: tuple[ArtifactRef, ...]
        canonical_state: CanonicalState

The snapshot contains only accepted history through planning_book_number - 1.

- [ ] Step 4: Implement the service operation.

    def load_repeated_history_for_book(
        self, book_number: int
    ) -> AcceptedHistorySnapshot:
        """Load accepted authority through book_number - 1 only."""

Use existing store loaders and metadata validation. Do not create a second
metadata or acceptance store. Do not use the legacy SeriesIdentity loader.

- [ ] Step 5: Run focused and V1 service regressions.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k history tests/test_series_vertical_slice_service.py -q -ra

Expected: new history tests pass and existing V1 service tests remain green.

Done evidence: snapshot excludes current Book authority and validates exact
accepted source revisions.

Commit:

    feat: add repeated accepted history read seam

---

## Task 3: Add explicit resolution references and planning intent

Files:

- Modify: src/auteur/series/vertical_slice_models.py
- Modify: src/auteur/series/vertical_slice_store.py
- Modify: src/auteur/series/vertical_slice_service.py
- Modify: src/auteur/series/repeated_map_focus.py
- Test: tests/test_series_repeated_map_focus.py
- Test: tests/test_series_vertical_slice_models.py

Classification: narrow representations required by R2/R3; not universal
lifecycle or Direction abstractions.

Reuse ArtifactRef, accepted realization dependency validation, PlanningEntry,
and explicit proposal/acceptance separation.

- [ ] Step 1: Write failing tests.

    def test_accepted_outcome_can_explicitly_resolve_a_series_commitment(tmp_path):
        service = build_repeated_ledger(tmp_path)
        bundle = service.load_accepted_realization_bundles()[1][0]
        assert 'commitment-falsifier' in bundle.resolved_commitment_ids

    def test_resolution_is_not_inferred_from_similar_text(tmp_path):
        service = build_repeated_ledger(tmp_path)
        accept_unrelated_outcome(service)
        snapshot = service.load_repeated_history_for_book(3)
        assert 'commitment-falsifier' not in snapshot.explicitly_resolved_commitment_ids

    def test_book_n_planning_intent_references_accepted_fact_without_book_n_authority(tmp_path):
        service = build_repeated_ledger(tmp_path)
        intent = service.enter_repeated_book_planning(
            4, entered_by='author', intent='Return to the monastery testimony.',
            relevance_refs=[accepted_monastery_fact_ref()],
        )
        assert intent.book_number == 4
        assert service.load_accepted_book_direction(4) is None
        assert service.load_accepted_book_direction(3) is not None

- [ ] Step 2: Run tests and verify red.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py tests/test_series_vertical_slice_models.py -k 'resolve or planning_intent' -q

Expected: FAIL because outcomes have no resolution field and planning entry has
no non-authoritative fact trigger.

- [ ] Step 3: Add the smallest explicit references.

    class AcceptedFactRef(BaseModel):
        artifact_id: str
        revision: int
        fact_id: str

Add defaulted resolved_commitment_ids to candidate and accepted outcome
payloads. Add:

    class BookPlanningIntent(BaseModel):
        book_number: int = Field(gt=1)
        intent: str
        relevance_refs: list[AcceptedFactRef] = Field(default_factory=list)

Validate resolution IDs against accepted Series commitments and fact references
against accepted history. Do not create Book-N authority.

- [ ] Step 4: Persist intent only in workflow storage.

    .auteur/series/vertical-slice/workflow/book-planning-intent/book-4.yaml

Do not send planning intent through ArtifactStore.accept.

- [ ] Step 5: Run focused and legacy tests.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py tests/test_series_vertical_slice_models.py tests/test_series_vertical_slice_service.py -q -ra

Expected: new tests pass; existing V1 payloads round-trip with default empty
fields; existing acceptance remains unchanged.

Done evidence: resolution is explicit, reactivation can be triggered by workflow
intent referencing an accepted fact, and no Book-N authority is created.

Commit:

    feat: add explicit continuity resolution and planning intent

---

## Task 4: Derive current-state evidence without a state lifecycle

Files:

- Modify: src/auteur/series/repeated_map_focus.py
- Modify: src/auteur/series/vertical_slice_service.py
- Test: tests/test_series_repeated_map_focus.py
- Regression: tests/test_series_vertical_slice_service.py

Classification: narrow current-state evidence required by R2/R3. Derived lineage
does not replace CanonicalState and does not add a universal state lifecycle.

Reuse accepted realization ordering, StateTransition before/after,
rebuild_canonical_state, and accepted bundle metadata.

- [ ] Step 1: Write failing tests.

    def test_current_state_evidence_keeps_latest_transition_current(tmp_path):
        service = build_repeated_ledger(tmp_path)
        evidence = service.derive_current_state_evidence(3)
        assert evidence['archive.public_status'].current_value == 'retracted'
        assert evidence['archive.public_status'].current_fact_id == 'admission-retracted'

    def test_superseded_state_is_not_selected_as_current_map_evidence(tmp_path):
        service = build_repeated_ledger(tmp_path)
        evidence = service.derive_current_state_evidence(3)
        assert evidence['archive.public_status'].current_fact_id != 'public-admission'
        assert 'public-admission' in evidence['archive.public_status'].superseded_fact_ids

    def test_current_state_evidence_does_not_mutate_canonical_state(tmp_path):
        service = build_repeated_ledger(tmp_path)
        before = service.load_canonical_state()
        service.derive_current_state_evidence(4)
        assert service.load_canonical_state() == before

- [ ] Step 2: Run and record red.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'current_state or superseded' -q

Expected: FAIL because V1 exposes current values and applied bundle IDs, not
transition-level current/superseded evidence.

- [ ] Step 3: Add the projection-local evidence type.

    @dataclass(frozen=True)
    class CurrentStateEvidence:
        key: str
        current_value: str
        current_fact_id: str
        current_source_ref: AcceptedFactRef
        superseded_fact_ids: tuple[str, ...]

Replay accepted transitions in the same order as CanonicalState rebuild. Retain
transition identity in memory only.

- [ ] Step 4: Run current-state and V1 rebuild regressions.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'current_state or superseded' tests/test_series_vertical_slice_service.py -k 'rebuild or canonical_state' -q -ra

Expected: new evidence tests pass and existing state-rebuild invariants remain
green.

Done evidence: latest current state is distinct from superseded state without
changing CanonicalState.

Commit:

    feat: derive current state evidence for repeated continuity

---

## Task 5: Implement the projection-local lifecycle-aware selector

Files:

- Modify: src/auteur/series/repeated_map_focus.py
- Modify: src/auteur/series/vertical_slice_service.py
- Test: tests/test_series_repeated_map_focus.py
- Fixture: tests/fixtures/repeated_map_focus_v2/r1-r3-history.yaml

Classification: disposition values are narrow R1-R3 projection semantics, not
ArtifactStore Lifecycle.

Reuse AcceptedHistorySnapshot, BookPlanningIntent, CurrentStateEvidence,
explicit resolution IDs, accepted commitment refs, and source validation.

- [ ] Step 1: Write failing R1-R3 selector tests.

    def test_selector_keeps_active_series_pressure_and_current_consequence(tmp_path):
        context = derive_repeated_context(build_repeated_ledger(tmp_path), 2)
        assert 'series-pressure-official-history' in context.active_ids
        assert 'founding-record' in context.active_fact_ids

    def test_selector_omits_resolved_commitment_from_book_three_active_items(tmp_path):
        context = derive_repeated_context(build_repeated_ledger(tmp_path), 3)
        assert 'commitment-falsifier' not in context.active_ids
        assert 'commitment-falsifier' in context.resolved_history_ids

    def test_selector_reactivates_old_fact_from_current_book_four_intent(tmp_path):
        service = build_repeated_ledger(tmp_path)
        service.enter_repeated_book_planning(
            4, entered_by='author', intent='Return to the monastery testimony.',
            relevance_refs=[accepted_monastery_fact_ref()],
        )
        context = derive_repeated_context(service, 4)
        assert 'monastery-testimony' in context.active_fact_ids
        assert context.dispositions['monastery-testimony'] == 'reactivated'

    def test_selector_omits_superseded_and_recent_irrelevant_material(tmp_path):
        context = derive_repeated_context(build_repeated_ledger(tmp_path), 3)
        assert 'public-admission' not in context.active_fact_ids
        assert 'repaired-lantern' not in context.active_fact_ids

    def test_selector_excludes_unaccepted_proposals_even_when_recent(tmp_path):
        context = derive_repeated_context(build_repeated_ledger(tmp_path), 4)
        assert 'burn-archive' not in context.active_fact_ids
        assert 'ally-militia' not in context.active_fact_ids

- [ ] Step 2: Run selector tests and verify red.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k selector -q

Expected: FAIL because no selector or local dispositions exist.

- [ ] Step 3: Define local disposition rules.

Use a literal/local enum in repeated_map_focus.py, not provenance Lifecycle:

    ContinuityDisposition = Literal[
        'active', 'resolved', 'dormant', 'reactivated',
        'superseded', 'irrelevant',
    ]

Rules, in order:

1. discard sources not accepted through Book N - 1;
2. identify explicit resolution IDs and remove them from active items;
3. identify latest current state per key and suppress superseded states;
4. retain commitments explicitly carried by accepted history;
5. retain current accepted state that constrains/enables the decision;
6. reactivate only fact refs named by current planning intent/proposal;
7. exclude accepted but irrelevant recent material; and
8. pass only active/reactivated candidates to grouping while retaining resolved/
   superseded explanations as optional support.

No rule may compare prose similarity to infer resolution or reactivation.

- [ ] Step 4: Add the service operation.

    def derive_repeated_book_context(
        self, book_number: int
    ) -> RepeatedBookPlanningContext:
        """Derive opening Book-N continuity from accepted history through N-1."""

Require explicit Book-N planning entry/intent, but not accepted Book-N Direction
or realization.

- [ ] Step 5: Run selector and V1 regressions.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k selector tests/test_series_vertical_slice_service.py -q -ra

Expected: R1-R3 behavior passes and existing V1 context selection remains
unchanged.

Done evidence: all six local dispositions are demonstrable for one derivation
without treating any as source authority.

Commit:

    feat: add local repeated continuity selector

---

## Task 6: Add pressure grouping and specific why-now

Files:

- Modify: src/auteur/series/repeated_map_focus.py
- Modify: src/auteur/series/vertical_slice_models.py only if typed serialization
  is required
- Test: tests/test_series_repeated_map_focus.py

Classification: narrow projection grouping required by R1-R3; no universal
PressureGroup domain entity.

Reuse SeriesDirection.pressure, commitment IDs, ArtifactRef, and existing
why-now/progressive-disclosure grammar.

- [ ] Step 1: Write failing tests.

    def test_grouping_keeps_one_group_for_multiple_consequences_of_one_pressure(tmp_path):
        context = derive_repeated_context(build_repeated_ledger(tmp_path), 4)
        assert context.group_ids.count('pressure-official-history-lived-memory') == 1
        assert {'founding-record', 'admission-retracted', 'archive-protected'} <= set(
            context.group_source_fact_ids('pressure-official-history-lived-memory')
        )

    def test_grouping_preserves_exact_supporting_sources(tmp_path):
        context = derive_repeated_context(build_repeated_ledger(tmp_path), 4)
        group = context.group('pressure-official-history-lived-memory')
        assert group.source_refs
        assert 'book-1-realization' in {ref.artifact_id for ref in group.source_refs}
        assert 'book-3-realization' in {ref.artifact_id for ref in group.source_refs}

    def test_grouped_item_has_specific_why_now(tmp_path):
        service = build_repeated_ledger(tmp_path)
        service.enter_repeated_book_planning(
            4, entered_by='author', intent='Return to the monastery testimony.',
            relevance_refs=[accepted_monastery_fact_ref()],
        )
        testimony = service.derive_repeated_book_context(4).item('monastery-testimony')
        assert 'Book 4' in testimony.why_matters_now
        assert 'monastery' in testimony.why_matters_now.lower()
        assert testimony.source_refs

- [ ] Step 2: Run tests and verify red.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'group or why_now' -q

Expected: FAIL because V1 CarryForwardItem is flat and Map has no grouping.

- [ ] Step 3: Add projection-local entries/groups.

Define the serializable `ContinuityEntry`, `ContinuityGroup`, and
`RepeatedBookPlanningContext` models in `src/auteur/series/vertical_slice_models.py`;
keep selector and grouping functions in `src/auteur/series/repeated_map_focus.py`.

    class ContinuityEntry(BaseModel):
        entry_id: str
        summary: str
        why_matters_now: str
        source_refs: list[ArtifactRef] = Field(min_length=1)
        disposition: ContinuityDisposition
        group_id: str | None
        is_current_constraint: bool

    class ContinuityGroup(BaseModel):
        group_id: str
        summary: str
        why_matters_now: str
        source_refs: list[ArtifactRef] = Field(min_length=1)
        entry_ids: list[str] = Field(min_length=1)

    class RepeatedBookPlanningContext(BaseModel):
        book_number: int = Field(gt=1)
        generated_from: list[ArtifactRef] = Field(min_length=1)
        groups: list[ContinuityGroup]
        entries: list[ContinuityEntry]
        history_entries: list[ContinuityEntry] = Field(default_factory=list)
        derivation_version: str

        @property
        def active_ids(self) -> set[str]:
            return {
                entry.entry_id
                for entry in self.entries
                if entry.disposition in {"active", "reactivated"}
            }

        @property
        def active_fact_ids(self) -> set[str]:
            return self.active_ids

        @property
        def resolved_history_ids(self) -> set[str]:
            return {
                entry.entry_id
                for entry in self.history_entries
                if entry.disposition in {"resolved", "superseded"}
            }

        @property
        def dispositions(self) -> dict[str, ContinuityDisposition]:
            return {
                entry.entry_id: entry.disposition for entry in self.entries
            } | {
                entry.entry_id: entry.disposition
                for entry in self.history_entries
            }

        @property
        def group_ids(self) -> list[str]:
            return [group.group_id for group in self.groups]

        def item(self, entry_id: str) -> ContinuityEntry:
            return next(entry for entry in self.entries if entry.entry_id == entry_id)

        def group(self, group_id: str) -> ContinuityGroup:
            return next(group for group in self.groups if group.group_id == group_id)

        def group_source_fact_ids(self, group_id: str) -> set[str]:
            return {
                entry.entry_id
                for entry in self.entries
                if entry.group_id == group_id
            }

Group by an existing commitment ID or explicit local rule key. Retain the union
of exact accepted source references. Keep current constraints as entries even
when history is grouped.

- [ ] Step 4: Implement deterministic why-now rules.

Use specific reasons such as:

    Book 4 planning names the accepted monastery testimony as a present route
    back to lived memory, so this older fact is relevant again now.

Do not use a generic “recently changed” explanation when the real reason is a
planning trigger, current state constraint, or active Series commitment.

- [ ] Step 5: Run grouping and V1 Map detail regressions.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'group or why_now' tests/test_series_vertical_slice_cli.py -k 'detail_map or map_shows' -q -ra

Expected: grouping tests pass and V1 flat Map output remains compatible.

Done evidence: grouping preserves provenance, current constraints remain visible,
and surfaced entries have specific why-now explanations.

Commit:

    feat: group repeated continuity with source-backed why-now

---

## Task 7: Persist and rebuild derived repeated context

Files:

- Modify: src/auteur/series/vertical_slice_store.py
- Modify: src/auteur/series/vertical_slice_service.py
- Modify: src/auteur/series/repeated_map_focus.py
- Test: tests/test_series_repeated_map_focus.py

Classification: pure generalization of V1 derived-projection storage with a
separate path so V1 context semantics remain frozen.

Reuse .auteur/series/vertical-slice/derived/, atomic YAML writes, ArtifactStore
source metadata, and existing delete/rebuild behavior.

- [ ] Step 1: Write failing tests.

    def test_repeated_context_round_trips_as_derived_data(tmp_path):
        service = build_repeated_ledger(tmp_path)
        expected = service.derive_repeated_book_context(4)
        reloaded = SeriesVerticalSliceService(tmp_path)
        assert reloaded.load_repeated_book_context(4) == expected
        assert reloaded.load_accepted_book_direction(4) is None

    def test_deleted_repeated_context_rebuilds_equivalently(tmp_path):
        service = build_repeated_ledger(tmp_path)
        original = service.derive_repeated_book_context(4)
        authority_before = authority_snapshot(service)
        service.delete_repeated_book_context(4)
        rebuilt = service.derive_repeated_book_context(4)
        assert rebuilt == original
        assert authority_snapshot(service) == authority_before

- [ ] Step 2: Run tests and verify red.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'round_trip or rebuild' -q

Expected: FAIL because V1 has no repeated projection serialization.

- [ ] Step 3: Add the derived path and version.

    .auteur/series/vertical-slice/derived/repeated-book-4-context.yaml
    repeated-map-focus-v2-r1

The version belongs to projection derivation, not accepted artifact revision.

- [ ] Step 4: Add the store/service operations.

Add store methods `load_repeated_book_context(book_number)`,
`delete_repeated_book_context(book_number)`, and the service method
`derive_repeated_book_context(book_number) -> RepeatedBookPlanningContext`.

Rebuild from accepted history and workflow intent. Never use the stored projection
as an authority source.

- [ ] Step 5: Run projection and V1 storage regressions.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'round_trip or rebuild' tests/test_series_vertical_slice_service.py -k 'context or rebuild' -q -ra

Expected: repeated projection tests pass and V1 context rebuild tests remain green.

Done evidence: derived repeated context round-trips/rebuilds equivalently and
cannot change authority or Canonical State.

Commit:

    feat: persist rebuildable repeated continuity context

---

## Task 8: Generalize Focus to a bounded current-Book proposal seam

Files:

- Modify: src/auteur/series/vertical_slice_service.py
- Modify: src/auteur/series/vertical_slice_models.py only if a red test proves
  a defaulted proposal field is necessary
- Modify: src/auteur/series/repeated_map_focus.py
- Test: tests/test_series_repeated_map_focus.py
- Regression: tests/test_series_vertical_slice_service.py

Classification: pure generalization of NextDecisionProposal, DecisionOption,
and non-authoritative actions. No universal recommender.

The contract defines proposal shape but not a universal way to invent Book 3/4
creative content. Use deterministic fixture decision seeds until a separate
product decision supplies a broader content source.

- [ ] Step 1: Write failing tests.

    def test_book_three_focus_proposal_uses_current_book_and_context(tmp_path):
        service = build_repeated_ledger(tmp_path)
        proposal = service.propose_repeated_next_decision(
            3, decision_seed=book_three_decision_seed()
        )
        assert proposal.book_number == 3
        assert proposal.accepted_input_refs
        assert len(proposal.options) >= 2
        assert proposal.rationale
        assert all(option.tradeoff for option in proposal.options)

    def test_repeated_focus_action_does_not_accept_current_book_direction(tmp_path):
        service = build_repeated_ledger(tmp_path)
        proposal = service.propose_repeated_next_decision(
            3, decision_seed=book_three_decision_seed()
        )
        service.record_decision_action(
            proposal.proposal_id,
            action='choose_other',
            selected_option_id=proposal.options[1].option_id,
        )
        assert service.load_accepted_book_direction(3) is None

    def test_repeated_focus_uses_current_book_language(tmp_path):
        service = build_repeated_ledger(tmp_path)
        proposal = service.propose_repeated_next_decision(
            4, decision_seed=book_four_decision_seed()
        )
        output = format_repeated_series_focus(proposal)
        assert 'Book 4' in output
        assert 'Book 2 canon' not in output
        assert 'not Book 4 canon' in output

- [ ] Step 2: Run tests and verify red.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'focus or current_book' -q

Expected: FAIL because V1 proposal construction is exact Book 2 and hard-coded.

- [ ] Step 3: Add a narrow deterministic decision seed.

    @dataclass(frozen=True)
    class RepeatedDecisionSeed:
        question: str
        recommended_option_id: str
        options: tuple[DecisionOption, ...]
        rationale: str

Add:

    def propose_repeated_next_decision(
        self, book_number: int, *, decision_seed: RepeatedDecisionSeed
    ) -> NextDecisionProposal:
        """Build a bounded proposal from the current repeated context."""

The seed is a non-authoritative proposal input. The service derives the current
context, copies bounded fields, and sets accepted_input_refs to exact source refs.

- [ ] Step 4: Reuse existing action persistence.

Allow book_number > 2 only through shared validation. Retain:

    choose_recommended
    choose_other
    defer

Actions remain workflow history and do not create Book-N Direction or alter
Canonical State.

- [ ] Step 5: Run Focus and V1 action regressions.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'focus or current_book' tests/test_series_vertical_slice_service.py -k 'decision or action' -q -ra

Expected: repeated proposal tests pass and V1 decision/action assertions remain
green.

Done evidence: current-Book bounded proposals work without creating authority.

Commit:

    feat: generalize bounded focus to the current book

---

## Task 9: Add recommendation/state compatibility and freshness

Files:

- Modify: src/auteur/series/vertical_slice_models.py only if needed
- Modify: src/auteur/series/repeated_map_focus.py
- Modify: src/auteur/series/vertical_slice_service.py
- Test: tests/test_series_repeated_map_focus.py
- Regression: tests/test_series_vertical_slice_service.py

Classification: narrow option compatibility required by R3; freshness is a pure
generalization of existing accepted-input comparison.

- [ ] Step 1: Write failing tests.

    def test_contradictory_recommended_option_is_rejected(tmp_path):
        service = build_repeated_ledger(tmp_path)
        proposal = service.propose_repeated_next_decision(
            4, decision_seed=book_four_burn_archive_recommendation_seed()
        )
        with pytest.raises(ValueError, match='incompatible|current accepted state'):
            service.validate_repeated_decision_proposal(proposal)

    def test_stale_repeated_focus_proposal_cannot_be_exercised(tmp_path):
        service = build_repeated_ledger(tmp_path)
        proposal = service.propose_repeated_next_decision(
            4, decision_seed=book_four_decision_seed()
        )
        accept_additional_book_three_state(service)
        with pytest.raises(ValueError, match='stale'):
            service.record_decision_action(
                proposal.proposal_id, action='choose_recommended'
            )

- [ ] Step 2: Run tests and verify red.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'contradictory or stale' -q

Expected: FAIL because V1 has no repeated option/state compatibility check.

- [ ] Step 3: Add explicit conflict evidence only if the red test requires it.

If a proposal cannot express the R3 contradiction without inference, add these
defaulted proposal-local fields to DecisionOption:

    incompatible_with_state_refs: list[ArtifactRef] = Field(default_factory=list)
    incompatibility_reason: str | None = None

A non-empty conflict list makes an option unavailable as a valid recommendation.
This is not a lifecycle or dependency framework and preserves existing V1
options through empty defaults.

- [ ] Step 4: Implement the same freshness boundary for proposal and action.

    def validate_repeated_decision_proposal(
        proposal: NextDecisionProposal,
        context: RepeatedBookPlanningContext,
    ) -> None:
        """Reject stale or state-incompatible repeated proposals."""

Verify accepted_input_refs against a freshly derived context, reject a
recommended option incompatible with current accepted state, and reject actions
after accepted input/state changes. Prefer explicit rejection and recomputation
over mutating the old proposal.

Expose a service wrapper with `service.validate_repeated_decision_proposal(proposal)`
that derives the current context and delegates to this pure validator.

- [ ] Step 5: Run compatibility and V1 stale-input regressions.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'contradictory or stale' tests/test_series_vertical_slice_service.py -k 'stale or decision' -q -ra

Expected: contradictory and stale actions are rejected; V1 stale-input tests
remain green.

Done evidence: no repeated recommendation crosses the action boundary against
changed or contradictory accepted state.

Commit:

    feat: enforce repeated focus state compatibility and freshness

---

## Task 10: Generalize Map/Focus presentation and keep CLI thin

Files:

- Modify: src/auteur/series/vertical_slice_formatters.py
- Modify: src/auteur/series/cli.py only for dispatch/wiring
- Test: tests/test_series_repeated_map_focus.py
- Test: tests/test_series_vertical_slice_cli.py
- Regression: tests/test_series_vertical_slice_e2e.py

Classification: presentation generalization; no relevance or authority logic in
CLI.

- [ ] Step 1: Write failing tests.

    def test_repeated_map_renders_groups_and_current_book_why_now(tmp_path):
        service = build_repeated_ledger(tmp_path)
        context = service.derive_repeated_book_context(4)
        output = format_repeated_series_map(context)
        assert 'Series Map: Book 4' in output
        assert 'Why it matters now' in output
        assert 'monastery' in output.lower()
        assert 'Source references' not in output

    def test_repeated_map_detail_preserves_group_sources(tmp_path):
        service = build_repeated_ledger(tmp_path)
        context = service.derive_repeated_book_context(4)
        output = format_repeated_series_map(context, detail=True)
        assert 'Source references' in output
        assert 'book-1-realization' in output
        assert 'book-3-realization' in output

    def test_repeated_focus_uses_current_book_noncanonical_language(tmp_path):
        service = build_repeated_ledger(tmp_path)
        proposal = service.propose_repeated_next_decision(
            3, decision_seed=book_three_decision_seed()
        )
        output = format_repeated_series_focus(proposal)
        assert 'Series Focus: Book 3' in output
        assert 'not Book 3 canon' in output
        assert 'Book 2 canon' not in output

- [ ] Step 2: Run tests and verify red.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'format or presentation' -q

Expected: FAIL because V1 formatters are flat and hard-code Book 2 wording.

- [ ] Step 3: Add separate repeated formatters.

    def format_repeated_series_map(
        context: RepeatedBookPlanningContext, *, detail: bool = False
    ) -> str:
        """Render the compact repeated current-Book Map."""

    def format_repeated_series_focus(
        proposal: NextDecisionProposal, *, detail: bool = False
    ) -> str:
        """Render the repeated current-Book Focus proposal."""

Default output shows compact groups, current constraints, why-now, question,
recommendation, rationale, tradeoff, and bounded choices. Detail adds exact
accepted refs, proposal ID, and option IDs. Default output does not dump all
history or internal dispositions.

- [ ] Step 4: Use current-Book clarification.

    This is a planning choice, not Book {proposal.book_number} canon.
    Choosing an option records what you want to explore next. You can change or
    develop it before accepting a Book {proposal.book_number} direction.

Existing V1 Book 2 assertions must remain compatible.

- [ ] Step 5: Wire CLI only after service tests are green.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -k 'format or presentation' tests/test_series_vertical_slice_cli.py tests/test_series_vertical_slice_e2e.py -q -ra

Expected: repeated presentation passes and existing V1 CLI/e2e remains green.

Done evidence: grouped current-Book output is progressive-disclosure friendly
and CLI is only an adapter.

Commit:

    feat: present repeated current-book map and focus

---

## Task 11: Add corrected R1-R5 fixtures and end-to-end qualification tests

Files:

- Create: tests/fixtures/repeated_map_focus_v2/series_direction.yaml
- Create: tests/fixtures/repeated_map_focus_v2/book_1_direction.yaml
- Create: tests/fixtures/repeated_map_focus_v2/book_1_realization.yaml
- Create: tests/fixtures/repeated_map_focus_v2/book_2_direction.yaml
- Create: tests/fixtures/repeated_map_focus_v2/book_2_realization.yaml
- Create: tests/fixtures/repeated_map_focus_v2/book_3_direction.yaml
- Create: tests/fixtures/repeated_map_focus_v2/book_3_realization.yaml
- Create: tests/fixtures/repeated_map_focus_v2/book_4_planning_intent.yaml
- Create: tests/fixtures/repeated_map_focus_v2/decision_seeds.yaml
- Create/modify: tests/test_series_repeated_map_focus.py
- Regression: tests/test_series_vertical_slice_e2e.py

Classification: narrow concrete acceptance evidence, not universal story schema.

- [ ] Step 1: Write failing end-to-end tests before final wiring.

    def test_r1_book_two_surfaces_active_pressure_and_new_consequence(tmp_path):
        service = build_repeated_ledger(tmp_path)
        context = service.derive_repeated_book_context(2)
        assert "founding-record" in context.active_fact_ids
        assert "broken-lantern" not in context.active_fact_ids

    def test_r2_book_three_omits_resolved_and_superseded_items(tmp_path):
        service = build_repeated_ledger(tmp_path)
        context = service.derive_repeated_book_context(3)
        assert "commitment-falsifier" not in context.active_ids
        assert "public-admission" not in context.active_fact_ids

    def test_r3_book_four_reactivates_old_fact_from_planning_intent(tmp_path):
        service = build_repeated_ledger(tmp_path)
        context = service.derive_repeated_book_context(4)
        assert "monastery-testimony" in context.active_fact_ids
        assert context.dispositions["monastery-testimony"] == "reactivated"

    def test_r4_context_delete_rebuild_is_equivalent(tmp_path):
        service = build_repeated_ledger(tmp_path)
        original = service.derive_repeated_book_context(4)
        service.delete_repeated_book_context(4)
        rebuilt = service.derive_repeated_book_context(4)
        assert rebuilt.model_dump(mode="json") == original.model_dump(mode="json")

    def test_r5_map_focus_and_actions_do_not_mutate_authority(tmp_path):
        service = build_repeated_ledger(tmp_path)
        before = authority_snapshot(service)
        service.derive_repeated_book_context(4)
        assert authority_snapshot(service) == before

    def test_recent_and_unaccepted_material_never_enters_map(tmp_path):
        service = build_repeated_ledger(tmp_path)
        context = service.derive_repeated_book_context(4)
        assert "repaired-lantern" not in context.active_fact_ids
        assert "ally-militia" not in context.active_fact_ids

    def test_grouping_preserves_all_supporting_provenance(tmp_path):
        service = build_repeated_ledger(tmp_path)
        group = service.derive_repeated_book_context(4).group(
            "pressure-official-history-lived-memory"
        )
        assert {ref.artifact_id for ref in group.source_refs} >= {
            "book-1-realization",
            "book-3-realization",
        }

    def test_contradictory_book_four_recommendation_cannot_be_accepted(tmp_path):
        service = build_repeated_ledger(tmp_path)
        proposal = service.propose_repeated_next_decision(
            4, decision_seed=book_four_burn_archive_recommendation_seed()
        )
        with pytest.raises(ValueError, match="incompatible"):
            service.validate_repeated_decision_proposal(proposal)

    def test_stale_repeated_focus_proposal_is_rejected(tmp_path):
        service = build_repeated_ledger(tmp_path)
        proposal = service.propose_repeated_next_decision(
            4, decision_seed=book_four_decision_seed()
        )
        accept_additional_book_three_state(service)
        with pytest.raises(ValueError, match="stale"):
            service.record_decision_action(
                proposal.proposal_id, action="choose_recommended"
            )

Assertions must include:

    assert service.load_accepted_book_direction(4) is None
    assert service.load_canonical_state() == state_before_map_focus
    assert 'broken-lantern' not in map_output
    assert 'book-2-burn-archive' not in map_output
    assert rebuilt.model_dump(mode='json') == original.model_dump(mode='json')

- [ ] Step 2: Run tests and record remaining red integration boundaries.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py -q -ra

Expected: failures identify missing integration, not a reason to weaken the
horizon or authority assertions.

- [ ] Step 3: Populate the corrected chronological ledger.

    Book 2 opening: accepted through Book 1; Book 2 Direction absent
    Book 3 opening: accepted through Book 2; Book 3 Direction absent
    Book 4 opening: accepted through Book 3; Book 4 Direction absent

Use explicit resolution IDs, explicit AcceptedFactRef triggers, ordered admission
-> retraction state transitions, and unaccepted proposal records. The
broken/repaired lanterns remain accepted but irrelevant, while burn-archive and
ally-militia remain unaccepted.

- [ ] Step 4: Run all repeated and V1 matrices.

    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py tests/test_series_vertical_slice_models.py tests/test_series_vertical_slice_service.py tests/test_series_vertical_slice_cli.py tests/test_series_vertical_slice_e2e.py -q -ra

Expected: R1-R5 pass; existing V1 authority, provenance, CLI, and e2e tests remain
green; Map, Focus, choose-other, and defer do not mutate authority.

Done evidence: R1-R5 are executable against corrected chronology with positive
and negative relevance, provenance, freshness, and authority assertions.

Commit:

    test: qualify repeated map focus ledger scenarios

---

## Task 12: Exact-candidate qualification and evidence handoff

Files:

- Create: docs/engineering/series-repeated-map-focus-qualification-v2.md
- Read: docs/engineering/release-qualification.md
- Run: scripts/verify-agent-workspace.ps1
- Run: scripts/release_evidence.py
- Run: scripts/verify_wheel.py

Classification: qualification evidence only.

- [ ] Step 1: Freeze the exact candidate.

    git status --short
    git rev-parse HEAD
    git rev-parse --show-toplevel
    git rev-parse --git-common-dir
    git diff --check

Source/test paths must be clean for the candidate. Do not stage unrelated
changes.

- [ ] Step 2: Run focused serial and parallel matrices.

Serial:

    $env:PYTHONPATH = "$repeatedMapRoot;$repeatedMapSrc"
    & 'C:\Python314\python.exe' -m pytest tests/test_series_repeated_map_focus.py tests/test_series_vertical_slice_models.py tests/test_series_vertical_slice_service.py tests/test_series_vertical_slice_cli.py tests/test_series_vertical_slice_e2e.py tests/test_provenance_pilot.py tests/test_story_state_commands.py tests/test_story_state_manager.py -ra

Parallel:

    & 'C:\Python314\python.exe' -m pytest -n 2 tests/test_series_repeated_map_focus.py tests/test_series_vertical_slice_models.py tests/test_series_vertical_slice_service.py tests/test_series_vertical_slice_cli.py tests/test_series_vertical_slice_e2e.py tests/test_provenance_pilot.py tests/test_story_state_commands.py tests/test_story_state_manager.py -ra

Record all pytest categories and serial/parallel reconciliation. Timeout or
termination is incomplete evidence.

- [ ] Step 3: Run complete source qualification from the exact SHA.

    $env:PYTHONPATH = "$repeatedMapRoot;$repeatedMapSrc"
    & 'C:\Python314\python.exe' scripts/release_evidence.py --skip-wheel

Record candidate SHA, generated JSON, all categories, baseline comparison, and
any known baseline-identical failures.

- [ ] Step 4: Run installed artifact qualification.

    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    & 'C:\Python314\python.exe' scripts/verify_wheel.py

Record wheel filename, package version, SHA-256, file count, and every installed
check.

- [ ] Step 5: Write the qualification report.

It must state:

    candidate SHA and worktree identity
    source/test import path
    focused serial and parallel categories
    full source categories
    wheel filename/hash and installed checks
    R1-R5 result summary
    no finite-Series/general architecture claim
    no human usability/participant claim
    remaining human evidence boundary

Use implemented, source-qualified, and artifact-qualified only in their precise
evidence-bounded meanings. Do not claim release readiness.

- [ ] Step 6: Review final scope.

    git diff --check
    git diff --name-only d3bb1eb37d065b34c132771cf19a0856e60d0cea HEAD -- src tests
    git status --short

Expected: only intended implementation/test files changed; unrelated user
changes remain untouched and are reported separately.

Done evidence: exact candidate source-qualified and artifact-qualified; R1-R5
pass; full regressions are accounted for; no broader Series architecture claim.

Commit:

    docs: record repeated map focus v2 qualification

---

## Red -> green test sequence

1. Baseline green: verified workspace/import and qualified V1 focused matrix.
2. History red -> green: Book-N snapshot includes accepted sources only through
   N-1.
3. Resolution/intent red -> green: explicit resolution and non-authoritative
   current planning trigger.
4. State evidence red -> green: latest state is current; superseded state is
   not current; CanonicalState unchanged.
5. Selector red -> green: active/resolved/dormant/reactivated/superseded/
   irrelevant behavior.
6. Grouping red -> green: pressure grouping, exact source refs, specific
   why-now.
7. Projection red -> green: delete/rebuild semantic equivalence.
8. Focus red -> green: current-Book bounded proposal and non-authoritative
   actions.
9. Compatibility red -> green: contradictory and stale proposals rejected.
10. Presentation red -> green: current-Book wording and progressive disclosure.
11. R1-R5 red -> green: corrected chronological integration fixture.
12. Qualification green: focused, legacy, full source, and installed artifact
    gates from one exact SHA.

## Compatibility and regression strategy

- retain SeriesIdentity/BookPlan untouched;
- retain existing sparse V1 authority paths and acceptance behavior;
- keep BookPlanningContext and existing Book 2 behavior available through a V1
  adapter rather than changing its semantics in place;
- keep NextDecisionProposal and DecisionAction as the authority boundary;
- generalize only validation needed for Book N > 2;
- preserve current V1 default/detail CLI disclosure;
- run V1 vertical-slice, provenance, story-state, legacy Series, full source,
  and installed-wheel tests after relevant tasks; and
- never treat passing R1-R3 as evidence of finite-Series or full architecture.

## Unresolved human approvals

1. Hide, collapse, or show resolved history as a milestone.
2. Maximum tolerable Map group density.
3. Whether pressure grouping matches writers’ mental models.
4. Whether compatibility warnings say unavailable, stale, or reconsider.
5. Concrete Book 3/4 creative decision content beyond bounded proposal shape.

Plan recommendation: default to compact grouping, keep resolved/superseded
history behind detail or a collapsed explanation, reject stale/incompatible
actions and require explicit recomputation, and use deterministic fixture
decision seeds until richer content is separately approved.

## Explicit deferred machinery

- universal narrative lifecycle/status;
- universal dependency/event graph;
- numerical or learned relevance ranking;
- general PressureGroup taxonomy;
- universal recommendation engine;
- generic Author Decision aggregate;
- free-form Book-N Direction authoring;
- intra-Book checkpoints;
- finite Series extent and evolution;
- cross-Series continuity federation; and
- browser/TUI/editor redesign.

## Definition of done

Repeated Map/Focus V2 is Implemented only when:

- corrected planning-horizon contract is recorded;
- R1-R5 executable tests pass;
- opening Book-N Map/Focus uses accepted history only through N-1;
- planning intent can trigger relevance without creating Book-N authority;
- explicit resolution, currentness, supersession, dormant reactivation,
  irrelevant exclusion, and pressure grouping pass;
- every surfaced item/group has exact accepted refs and specific why-now;
- Focus has one bounded current-Book proposal with recommendation, rationale,
  tradeoff, refs, and non-authoritative actions;
- incompatible recommendations and stale proposals cannot cross the action
  boundary;
- projections delete/rebuild equivalently;
- current-Book presentation and progressive disclosure pass; and
- no deferred machinery or out-of-scope authority mutation was introduced.

It is source-qualified only when the exact candidate passes focused, relevant
legacy, complete source, and baseline-comparison gates with all pytest categories
recorded separately.

It is artifact-qualified only when a wheel built from that same candidate passes
the installed matrix in a fresh environment with its hash recorded.

The final report must say:

    Repeated Map/Focus V2 is implemented/source-qualified/artifact-qualified
    only for opening Book-N planning through the accepted R1-R5 behavior. It is
    not a claim of finite-Series support, complete Series architecture, human
    usability validation, or release readiness.

## Self-review

Spec coverage:

- baseline/preflight: Task 0;
- chronology and planning horizon: Task 1;
- accepted-history read seam: Task 2;
- explicit resolution and present relevance: Task 3;
- current-state evidence/supersession: Task 4;
- lifecycle-aware selector: Task 5;
- grouping/why-now: Task 6;
- persistence/rebuild: Task 7;
- current-Book Focus: Task 8;
- compatibility/freshness: Task 9;
- Map/Focus and CLI: Task 10;
- adversarial R1-R5: Task 11;
- exact qualification: Task 12.

Every production task starts with a named failing behavioral test, exact files,
reusable V1 seams, smallest implementation, relevant regressions, and done
evidence. The only non-TDD tasks are the baseline and documentation chronology
gates.

Plan complete and saved to docs/superpowers/plans/2026-08-24-repeated-map-focus-v2.md.
