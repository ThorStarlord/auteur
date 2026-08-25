# Series Vertical Slice V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Implement and qualify the smallest end-to-end Series journey in which a beginner accepts sparse Series Direction, accepts one local Book Direction, accepts one realized Book 1 consequence, explicitly starts planning Book 2, receives source-linked relevant context and one non-authoritative next decision.

**Architecture:** Keep the existing full SeriesIdentity / BookPlan workflow unchanged. Add a narrow sparse Series journey boundary with typed artifacts, explicit acceptance records, a deterministic Canonical State rebuild, explicit carry-forward references, and a thin CLI presentation of the frozen Map/Focus grammar. Use existing StoryIdentity, proposal, acceptance, and provenance mechanisms through adapters where they already fit; do not generalize them for hypothetical future slices.

**Tech Stack:** Python >=3.11, Pydantic v2, PyYAML, pytest, existing argparse CLI, and the existing file-backed .auteur state/provenance conventions.

---

## Frozen inputs and constraints

Implementation must be checked against these documents before each capability is started:

- docs/acceptance/series-vertical-slice-capability-contract-v1.md
- docs/design/series-vertical-slice-implementation-boundary-v1.md
- docs/adr/065-domain-model-v1-scope-and-closure.md
- docs/adr/066-series-vertical-slice-ux-v1.md
- docs/adr/067-sparse-series-direction-boundary.md
- docs/adr/068-series-vertical-slice-cli-surface.md
- docs/adr/069-bounded-book-two-decision-actions.md
- docs/adr/070-sparse-series-storage-boundary.md
- docs/narrative-architecture.md

The behavioral contract is the authority for this plan. The following are explicitly not implementation targets:

- relaxing SeriesIdentity validation or changing the meaning of BookPlan;
- a complete future-Series roadmap;
- Episode support or Book/Episode unification;
- universal Direction inheritance, Author Decision, dependency inference, or revision propagation;
- full StoryBible replacement;
- LLM calls in the deterministic relevance, state-rebuild, or acceptance paths;
- production implementation of the throwaway HTML prototype;
- final navigation decisions about whether Map and Focus are screens, panels, or one responsive surface.

## File map

The implementation should add focused files rather than turn series/models.py or series/cli.py into a second domain framework.

| File | Responsibility |
|---|---|
| src/auteur/series/vertical_slice_models.py | Typed sparse Direction, Book Direction, realization/state, context, and next-decision payloads. No file I/O. |
| src/auteur/series/vertical_slice_store.py | Atomic persistence for proposal history, accepted artifacts, derived context, and workflow-entry records; delegates shared artifact metadata to ArtifactStore. |
| src/auteur/series/vertical_slice_service.py | Application operations and authority barriers: propose, accept, rebuild, enter Book 2 planning, derive context, and record non-canonical decision actions. |
| src/auteur/series/vertical_slice_formatters.py | Beginner-facing Map and Focus text; no domain mutation and no internal provenance dump by default. |
| src/auteur/series/cli.py | Register and dispatch the narrow series journey commands while preserving all existing full-Series commands. |
| tests/test_series_vertical_slice_models.py | Model validation and serialization tests. |
| tests/test_series_vertical_slice_service.py | Focused authority, rebuildability, source-reference, and relevance tests. |
| tests/test_series_vertical_slice_cli.py | CLI parser/formatter behavior and legacy Series CLI compatibility. |
| tests/fixtures/archive_of_lies_vertical_slice/ | Small deterministic fixture inputs and expected Book 2 context/decision output. |
| tests/test_series_vertical_slice_e2e.py | One reload-and-rebuild journey through the production command surface. |
| docs/engineering/series-vertical-slice-qualification-v1.md | Exact candidate SHA, environment identity, test categories, and Archive of Lies evidence after implementation. |

Do not modify src/auteur/series/models.py, compiler.py, bible.py, graph.py, or the existing full-Series validators unless a focused regression test proves an integration defect. The default plan assumes no change to those files.

## Dependency order

~~~text
0  workspace/import qualification
   ↓
1  sparse Series Direction + acceptance
   ↓
2  local Book Direction + acceptance
   ↓
3  accepted outcome + Canonical State rebuild
   ↓
4  explicit Book 2 planning entry + carry-forward context
   ↓
5  non-authoritative next decision
   ↓
6  thin Map/Focus production surface
   ↓
7  Archive of Lies end-to-end fixture and qualification tests
   ↓
8  exact-candidate qualification record and handoff
~~~

Every capability task follows the same TDD loop: add the smallest failing behavioral test, run that test and record the failure, implement only the behavior needed to turn it green, run the focused suite plus the relevant existing regression suite, then commit the slice.

---

### Task 0: Establish trustworthy workspace and import qualification

**Files:**

- Read: AGENTS.md
- Read: docs/engineering/release-qualification.md
- Run: scripts/verify-agent-workspace.ps1
- No product source changes in this task.

- [x] **Step 1: Record repository identity before any implementation.**

Run from H:\GithubRepositories\auteur:

~~~powershell
git rev-parse --show-toplevel
git rev-parse --git-common-dir
git rev-parse HEAD
(Get-Command python).Source
~~~

Expected: the root is H:/GithubRepositories/auteur, the common directory is .git, and the recorded HEAD is the candidate being implemented. Stop if the shell is pointed at another Git universe.

- [x] **Step 2: Prove the active import resolves to this checkout.**

Run with the checkout source explicitly selected for the command:

~~~powershell
$auteurSliceRoot = (git rev-parse --show-toplevel)
$auteurSliceSrc = Join-Path $auteurSliceRoot 'src'
$auteurSliceCode = "import sys; from pathlib import Path; sys.path.insert(0, r'$auteurSliceSrc'); import auteur; p=Path(auteur.__file__).resolve(); expected=Path(r'$auteurSliceSrc').resolve(); assert expected in p.parents, f'{p} is not under {expected}'; print(p)"
python -c $auteurSliceCode
~~~

Expected: the printed module path is under H:\GithubRepositories\auteur\src\auteur. The previously observed H:\scratch\auteur-pr44-final import must not be used as implementation evidence.

- [x] **Step 3: Capture a known-good current-source baseline.**

Run the full collection and the existing Series-focused tests with the same explicit source insertion:

~~~powershell
$auteurSliceSrc = Join-Path (git rev-parse --show-toplevel) 'src'
python -c "import sys; sys.path.insert(0, r'$auteurSliceSrc'); import pytest; raise SystemExit(pytest.main(['--collect-only','-q']))"
python -c "import sys; sys.path.insert(0, r'$auteurSliceSrc'); import pytest; raise SystemExit(pytest.main(['tests/test_series_models.py','tests/test_series_cli.py','tests/test_series_compile.py','tests/test_series_boundaries.py','tests/test_series_graph.py','tests/test_series_bible.py','tests/test_series_cli_continuity_integration.py','-q']))"
~~~

Expected baseline: full current-source collection exits 0; the focused Series suite passes 39 tests unless the exact candidate has changed for an unrelated reason. Record collected, passed, skipped, xfailed, xpassed, failed, and error counts separately.

- [x] **Step 4: Do not proceed on an unqualified import.**

If the import still resolves outside the checkout, fix the execution environment or make the explicit-source runner the only qualification command. Do not change package code to compensate for a stale or foreign import.

**Done evidence:** a text record containing root, common directory, HEAD, Python executable, resolved auteur.__file__, collection result, and focused baseline result.

**Commit:** none; this is a qualification gate.

**Checkpoint recorded 2026-08-23:** workspace preflight passed for
`H:/GithubRepositories/auteur` with standalone Git topology and HEAD
`5d3dcbf1fce2a1124401f6c29b8d48b0ff29dd98`. The active Python executable is
`C:\Python314\python.exe`; explicit current-source import resolves to
`H:\GithubRepositories\auteur\src\auteur\__init__.py`. Full current-source
pytest collection exited 0, and the existing Series-focused baseline passed
39 tests. The implementation worktree is
`.worktrees/series-vertical-slice-v1` on branch
`feat/series-vertical-slice-v1`.

---

### Task 1: Add sparse Series Direction and explicit acceptance

**Files:**

- Create: src/auteur/series/vertical_slice_models.py
- Create: src/auteur/series/vertical_slice_store.py
- Create: src/auteur/series/vertical_slice_service.py
- Create: tests/test_series_vertical_slice_models.py
- Create: tests/test_series_vertical_slice_service.py
- Create: tests/fixtures/archive_of_lies_vertical_slice/series_direction.yaml
- Do not modify: src/auteur/series/models.py or src/auteur/series/cli.py yet.

The first model boundary must be concrete rather than a generic Direction base. Define these typed payloads in vertical_slice_models.py:

~~~python
class ArtifactRef(BaseModel):
    artifact_id: str
    revision: int

class DirectionCommitment(BaseModel):
    commitment_id: str
    statement: str
    scope: Literal["series", "book"]

class SeriesDirection(BaseModel):
    series_id: str
    title: str
    series_type: Literal["ongoing"]
    promise: str
    pressure: str
    open_question: str
    commitments: list[DirectionCommitment] = Field(min_length=1)

class SeriesDirectionProposal(BaseModel):
    proposal_id: str
    revision: int = Field(ge=1)
    direction: SeriesDirection
    source_refs: list[ArtifactRef] = Field(default_factory=list)

class AcceptedSeriesDirection(BaseModel):
    artifact_id: str
    proposal_id: str
    direction: SeriesDirection
~~~

The stored accepted record is authoritative only after accept_series_direction succeeds. A proposal revision remains recoverable, but its presence or editing must not affect the accepted record or any Canonical State. `ArtifactStore` owns acceptance actor/time, artifact revision, hash, dependencies, and freshness; the payload stores semantic content and artifact identity only. Any service read that needs acceptance metadata must read the matching `ArtifactStore` record rather than a second mutable copy.

- [x] **Step 1: Write model and authority tests first.**

Add tests with these exact names and behaviors:

- `test_ongoing_series_direction_requires_no_future_books`: validate a sparse ongoing Direction document with no `book_plans`.
- `test_series_direction_requires_at_least_one_commitment`: reject an empty commitment list.
- `test_proposal_round_trips_without_becoming_accepted`: save and reload a proposal, then assert no accepted record exists.
- `test_acceptance_round_trip_preserves_author_and_source_revision`: accept, reload, and compare author and source revision.

The test fixture must contain no book_plans field. Use model_validate, YAML serialization, reload, and an explicit assertion that no SeriesIdentity is constructed by this path.

- [x] **Step 2: Run the new tests and verify the intended red state.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_models.py tests/test_series_vertical_slice_service.py -q
~~~

Expected: collection succeeds but the new imports/operations are absent or fail; do not weaken the assertions to obtain a false green result.

- [x] **Step 3: Implement the smallest typed persistence seam.**

VerticalSliceStore should persist sparse journey files below the project, for example:

~~~text
.auteur/series/vertical-slice/
  proposals/series-direction/<proposal-id>.yaml
  accepted/series-direction.yaml
~~~

Use temp-file-then-replace writes. Store accepted artifact metadata through ArtifactStore with explicit dependencies only; do not use its current story/blueprint dependency inference for these new artifact types. The accepted payload must not become a second owner of ArtifactMetadata.revision, acceptance actor/time, hash, dependencies, or freshness.

- [x] **Step 4: Implement propose/save/load and explicit accept.**

Expose only these initial operations from the service boundary:

~~~python
propose_series_direction(direction: SeriesDirection) -> SeriesDirectionProposal
load_series_direction_proposal(proposal_id: str) -> SeriesDirectionProposal
accept_series_direction(proposal_id: str, *, accepted_by: str, rationale: str | None = None) -> AcceptedSeriesDirection
load_accepted_series_direction() -> AcceptedSeriesDirection | None
load_series_direction_metadata() -> ArtifactMetadata | None
~~~

Acceptance must fail for an unknown proposal and must write the accepted record atomically. It must not create Book Plans or modify any legacy Series file.

- [x] **Step 5: Run focused and legacy tests.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_models.py tests/test_series_vertical_slice_service.py tests/test_series_models.py tests/test_series_cli.py -q
~~~

Expected: new tests pass and existing full-Series tests retain their previous behavior.

**Capability coverage:** contract scenario 1 and the negative rule that unaccepted alternatives have no authority.

**Commit:** feat: add sparse series direction acceptance boundary

**Checkpoint recorded 2026-08-23:** Task 1 was implemented in the isolated
worktree, reviewed for specification compliance and code quality, and
integrated into `main` as commits `bef94c5`, `0b58dbd`, and `1e9ed65`. The
focused Task 1, provenance, and legacy Series suite passed 75 tests with no
failures, skips, or errors. The final review required and verified metadata
correspondence, UTC acceptance timestamps, and rollback-preserving atomic
acceptance.

---

### Task 2: Add one local Book Direction with explicit acceptance

**Files:**

- Modify: src/auteur/series/vertical_slice_models.py
- Modify: src/auteur/series/vertical_slice_store.py
- Modify: src/auteur/series/vertical_slice_service.py
- Modify: tests/test_series_vertical_slice_service.py
- Create: tests/fixtures/archive_of_lies_vertical_slice/book_1_direction.yaml

Use existing auteur.identity.StoryIdentity as the Book Direction payload where its semantics fit. Do not copy Series Direction fields into StoryIdentity, and do not synthesize a future BookPlan list. Add only a Book-scoped wrapper containing the Book number, the StoryIdentity, and explicit accepted Series commitment references.

The intended typed boundary is:

~~~python
class BookDirection(BaseModel):
    book_number: int = Field(ge=1)
    identity: StoryIdentity
    series_commitment_ids: list[str] = Field(min_length=1)

class BookDirectionProposal(BaseModel):
    proposal_id: str
    revision: int = Field(ge=1)
    direction: BookDirection
    source_refs: list[ArtifactRef]

class AcceptedBookDirection(BaseModel):
    artifact_id: str
    proposal_id: str
    direction: BookDirection
~~~

- [x] **Step 1: Write failing tests for Series/Book authority separation.**

Add these tests:

- `test_book_direction_requires_accepted_series_direction`: reject proposal creation before Series acceptance.
- `test_accepting_book_direction_does_not_mutate_series_direction`: snapshot Series content before and after Book acceptance.
- `test_unaccepted_book_direction_has_no_authority`: confirm the candidate is reloadable but not accepted.
- `test_book_direction_reload_preserves_book_number_commitment_refs_and_source`: compare the Book number, commitment references, and source revision after reload.

The first test must attempt Book 1 proposal creation without an accepted Series Direction and assert the domain-level failure. The second must snapshot the accepted Series Direction before Book acceptance and compare it after acceptance.

- [x] **Step 2: Run the focused tests and verify red.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_service.py -k "book_direction or series_direction" -q
~~~

- [x] **Step 3: Implement Book Direction proposal and acceptance.**

Add:

~~~python
propose_book_direction(book_direction: BookDirection) -> BookDirectionProposal
accept_book_direction(proposal_id: str, *, accepted_by: str, rationale: str | None = None) -> AcceptedBookDirection
load_accepted_book_direction(book_number: int) -> AcceptedBookDirection | None
~~~

Validate every referenced commitment against the accepted Series Direction before proposal creation. Persist the Book artifact separately from the Series artifact. Use explicit provenance references to the accepted Series artifact and its ArtifactStore revision. Do not copy accepted actor/time or revision fields into the Book payload.

- [x] **Step 4: Run new tests plus the identity and full-Series regressions.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_service.py tests/test_story_discovery.py tests/test_series_models.py tests/test_series_compile.py -q
~~~

**Capability coverage:** contract scenario 2 and the negative rule that accepting Book 1 does not revise Series Direction.

**Commit:** feat: add accepted local book direction

**Checkpoint recorded 2026-08-23:** Task 2 was implemented in the isolated
worktree and passed both specification and code-quality re-review at exact
HEAD `b85b766fa34d4af10d9ab7d4baafc8ad80063119`. The review fixes verify the
exact accepted Series revision before Book authority is persisted, preserve
historical Book loadability after later Series revisions while ArtifactStore
reports staleness, and preserve Book payload/metadata/revisions on failure.
The reviewed commits were integrated into `main` as `5af1e41`, `6497da7`, and
`211a886`. The integrated Task 1–2, provenance, and legacy Series suite passed
133 tests with no failures, skips, or errors. Ruff and `git diff --check`
passed.

---

### Task 3: Accept one outcome and rebuild Canonical State

**Files:**

- Modify: src/auteur/series/vertical_slice_models.py
- Modify: src/auteur/series/vertical_slice_store.py
- Modify: src/auteur/series/vertical_slice_service.py
- Modify: tests/test_series_vertical_slice_service.py
- Create: tests/fixtures/archive_of_lies_vertical_slice/book_1_outcome.yaml

Keep the mutable StoryBible out of this authority path. Add only the bounded Book outcome structures needed by the fixture:

~~~python
class StateTransition(BaseModel):
    transition_id: str
    subject: str
    attribute: str
    before: str | None = None
    after: str
    explanation: str

class RealizationCandidate(BaseModel):
    candidate_id: str
    book_number: int = Field(ge=1)
    summary: str
    transitions: list[StateTransition] = Field(min_length=1)
    source_refs: list[ArtifactRef] = Field(min_length=1)

class AcceptedRealizationBundle(BaseModel):
    artifact_id: str
    bundle_id: str
    candidate_id: str
    book_number: int
    transitions: list[StateTransition]

class CanonicalState(BaseModel):
    state_version: int = Field(ge=0)
    values: dict[str, str] = Field(default_factory=dict)
    applied_bundle_ids: list[str] = Field(default_factory=list)
~~~

rebuild_canonical_state() must read accepted realization bundles in stable ArtifactStore revision order, apply their transitions deterministically, and write the derived state atomically. It must never read an unaccepted candidate. `derived/canonical-state.yaml` is a rebuildable projection; accepted realization bundles remain the authoritative historical basis.

- [x] **Step 1: Write failing authority and rebuild tests.**

Add these exact tests:

- `test_unaccepted_outcome_does_not_change_canonical_state`: compare state before and after proposal-only persistence.
- `test_accepting_outcome_creates_bundle_and_state_transition`: assert the accepted bundle and changed state value.
- `test_reloading_rebuilds_same_state_from_accepted_bundles`: construct a fresh service/store and rebuild.
- `test_state_rebuild_ignores_unaccepted_outcome_files`: add an unaccepted candidate and assert it is absent from the reduction.
- `test_accepted_outcome_preserves_source_revisions`: inspect accepted source references after reload.

Use a before/after assertion on a concrete Archive of Lies state value. The test must inspect the accepted bundle and state after a fresh service/store instance is created.

- [x] **Step 2: Run the outcome tests and verify red.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_service.py -k "outcome or state or realization" -q
~~~

- [x] **Step 3: Implement accepted bundle persistence and pure reduction.**

Expose:

~~~python
propose_realization(candidate: RealizationCandidate) -> RealizationCandidate
accept_realization(candidate_id: str, *, accepted_by: str, rationale: str | None = None) -> AcceptedRealizationBundle
rebuild_canonical_state() -> CanonicalState
load_canonical_state() -> CanonicalState
~~~

Require an accepted Book Direction for the candidate's Book. The accept operation must persist the accepted bundle through the shared metadata boundary and then rebuild the derived state; if either write fails, the service must not report success. Deleting the materialized state file must leave accepted bundles and their ArtifactStore metadata intact. Do not mutate StoryBible or any existing bible.json file.

- [x] **Step 4: Run focused state/provenance regressions.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_service.py tests/test_provenance_pilot.py tests/test_story_state_manager.py tests/test_story_state_commands.py -q
~~~

**Capability coverage:** contract scenario 3 and the negative rule that an unaccepted outcome cannot appear in Canonical State.

**Commit:** feat: add accepted realization and canonical state rebuild

**Checkpoint recorded 2026-08-23:** Task 3 was implemented at isolated
worktree HEAD `32ad5e446f2ef4ba92214686a142deffbb1a37ce`, then passed both
specification and code-quality re-review with no findings. The corrective
review verified fail-closed realization history, per-bundle provenance
identity, deterministic state-order reduction, enforced transition
preconditions, and rollback of accepted authority plus derived state. The
reviewed commits were integrated into `main` as `930d166` and `09dac10`.
The integrated Task 1–3, provenance, story-state, identity, and legacy Series
suite passed 179 tests with no failures, skips, xfails, xpasses, or errors.
Ruff and `git diff --check` passed in the reviewed worktree.

---

### Task 4: Enter Book 2 planning and derive compact relevant context

**Files:**

- Modify: src/auteur/series/vertical_slice_models.py
- Modify: src/auteur/series/vertical_slice_store.py
- Modify: src/auteur/series/vertical_slice_service.py
- Modify: tests/test_series_vertical_slice_service.py
- Create: tests/fixtures/archive_of_lies_vertical_slice/book_2_context_expected.yaml

The transition into later-Book planning must be explicit and non-authoritative. Persist a small workflow-entry record so reloading can distinguish “the author chose to plan Book 2” from merely having a Book 2 number in a file. Do not create a Book 2 Direction or append a Book 2 BookPlan.

Define only the projection shape required by the contract:

~~~python
class PlanningEntry(BaseModel):
    book_number: int = Field(gt=1)
    entered_by: str
    entered_at: datetime

class CarryForwardItem(BaseModel):
    item_id: str
    kind: Literal["series_commitment", "state_change"]
    summary: str
    why_matters_now: str
    source_refs: list[ArtifactRef] = Field(min_length=1)

class BookPlanningContext(BaseModel):
    book_number: int = Field(gt=1)
    generated_from: list[ArtifactRef] = Field(min_length=1)
    items: list[CarryForwardItem] = Field(min_length=1)
    derivation_version: str
~~~

V1 relevance is explicit and deterministic. For the Archive of Lies fixture, the rules select the accepted Series commitment referenced by the accepted Book 1 Direction and the accepted Book 1 state transition referenced by the fixture's carry-forward rule. They exclude unrelated material even if it is newer. The rule must be represented as ordinary application code or fixture data, not as a generalized inferred dependency graph.

- [x] **Step 1: Write failing tests for explicit transition, relevance, explanations, and rebuild.**

Add these tests:

- `test_book_2_planning_requires_explicit_author_entry`: reject derivation before the planning-entry action.
- `test_book_2_entry_does_not_create_book_2_direction_or_canon`: assert the entry is workflow state only.
- `test_context_contains_only_explicitly_relevant_accepted_sources`: exclude the unrelated recent datum.
- `test_every_context_item_has_why_now_and_source_revisions`: validate both explanation and source references.
- `test_deleted_context_rebuilds_semantically_equivalent_from_accepted_sources`: delete the derived file and compare rebuilt content excluding timestamps.
- `test_rebuilding_context_does_not_change_authority_or_canonical_state`: compare accepted artifacts and state before and after rebuild.

The rebuild test must delete only the derived context file before calling derive_book_context(2) again. It must compare serialized item IDs, explanations, and source references, not timestamps.

- [x] **Step 2: Run the context tests and verify red.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_service.py -k "planning or context or relevance or rebuild" -q
~~~

- [x] **Step 3: Implement the explicit planning entry and deterministic projection.**

Expose:

~~~python
enter_book_planning(book_number: int, *, entered_by: str) -> PlanningEntry
derive_book_context(book_number: int) -> BookPlanningContext
delete_derived_book_context(book_number: int) -> None
~~~

derive_book_context must refuse to run before the corresponding planning entry exists. It must load accepted artifacts and their current ArtifactMetadata.revision values each time; cached context is never a source. Its output may be deleted and rebuilt without touching accepted Direction, accepted realization history, or the derived Canonical State projection. ArtifactRef revision values in the context are references to ArtifactStore-owned revisions, not a second metadata authority.

- [x] **Step 4: Run context, Series, and provenance regressions.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_service.py tests/test_series_bible.py tests/test_series_graph.py tests/test_provenance_pilot.py -q
~~~

**Capability coverage:** contract scenarios 4, 5, and 7, including explicit Book 2 entry, compact source-linked context, and rebuildability.

**Commit:** feat: derive rebuildable book planning context

**Checkpoint recorded 2026-08-23:** Task 4 was implemented at isolated
worktree HEAD `6e91af94ef8dd82ee9b6ac94d2edf96ff5509e01` and passed final
specification and code-quality review with no findings. The reviewed history
includes the corrective commits `6ecc1d2` and `6e91af9`, which enforce current
ArtifactStore revision provenance, planning-entry identity, exact source
coordinates for relevance, idempotent workflow entry, and unique transition
IDs. The reviewed commits were integrated into `main` as `9ebf980`, `7816fbd`,
and `6302520`. The integrated Task 1–4, provenance, story-state, identity, and
legacy Series suite passed 191 tests with no failures, skips, xfails, xpasses,
or errors.

---

### Task 5: Present and record one non-authoritative next decision

**Files:**

- Modify: src/auteur/series/vertical_slice_models.py
- Modify: src/auteur/series/vertical_slice_store.py
- Modify: src/auteur/series/vertical_slice_service.py
- Modify: tests/test_series_vertical_slice_service.py
- Create: tests/fixtures/archive_of_lies_vertical_slice/book_2_decision_expected.yaml

Reuse the author-facing fields and explanation style from story_discovery_recommend.py, but do not reuse StructureProposal.apply, because that function materializes a changed Blueprint and would make choosing a Book 2 recommendation look canonical.

Define a context-bound proposal, not a universal recommendation abstraction:

~~~python
class DecisionOption(BaseModel):
    option_id: str
    label: str
    summary: str
    tradeoff: str

class NextDecisionProposal(BaseModel):
    proposal_id: str
    book_number: int
    question: str
    recommended_option_id: str
    options: list[DecisionOption] = Field(min_length=2)
    rationale: str
    accepted_input_refs: list[ArtifactRef] = Field(min_length=1)
    status: Literal["proposed", "resolved", "deferred"] = "proposed"

class DecisionAction(BaseModel):
    proposal_id: str
    action: Literal["choose_recommended", "choose_other", "defer"]
    selected_option_id: str | None = None
    recorded_at: datetime
~~~

The proposal must identify accepted context inputs, state why the recommended option is preferred, and state its principal tradeoff. Choosing the recommended option, another option from this exact proposal, or defer records workflow history only. None of those actions accepts Book 2 Direction or changes Book 2 Canonical State. The beginner-facing wording is “Choose another option”; `choose_other` is an internal action value.

- [x] **Step 1: Write failing decision tests.**

Add these tests:

- `test_next_decision_cites_context_inputs_and_tradeoff`: require accepted input references, rationale, and tradeoff.
- `test_choose_recommended_does_not_accept_book_2_direction`: record the action while keeping Book 2 non-canonical.
- `test_choose_another_presented_option_is_non_canonical`: select another option from this exact proposal without creating authority.
- `test_defer_preserves_open_decision_without_canonical_mutation`: record defer and leave the proposal unresolved.
- `test_unknown_decision_option_is_rejected`: reject an option ID not in the proposal.

- [x] **Step 2: Run the decision tests and verify red.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_service.py -k "decision or recommendation" -q
~~~

- [x] **Step 3: Implement deterministic proposal and three author actions.**

Expose:

~~~python
propose_next_decision(book_number: int) -> NextDecisionProposal
record_decision_action(
    proposal_id: str,
    *,
    action: Literal["choose_recommended", "choose_other", "defer"],
    selected_option_id: str | None = None,
) -> DecisionAction
~~~

For the first fixture, the recommendation is deterministic from the two explicit context items. Validate the selected option against the exact proposal being acted on. Do not call an LLM and do not write to accepted Book 2 Direction, Series Direction, realization bundles, or Canonical State.

- [x] **Step 4: Run decision and recommendation regressions.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_service.py tests/test_story_discovery_recommend_adapter.py tests/test_story_discovery_recommend_phase_b_surface.py tests/test_structure_proposals.py tests/test_proposal_accept_apply.py -q
~~~

**Capability coverage:** contract scenario 6 and all three non-canonical decision actions.

**Commit:** feat: add non-authoritative book two decision

**Checkpoint recorded 2026-08-23:** Task 5 was implemented at isolated
worktree HEAD `49d609c4382d3be2948e846b1aacc59dda5156bb` and passed final
specification and code-quality review with no findings. The reviewed history
includes corrective commits `c63ac08`, `35e83ef`, `7c13f02`, and `49d609c`,
which enforce exact proposal identity, current-input revalidation, option and
Book 2 invariants, coherent action/status history, idempotent terminal retries,
and create-only proposal persistence. The reviewed commits were integrated
into `main` as `828b18d`, `cbb7fa0`, `b545d97`, `445675a`, and `c838827`.
The integrated Task 1–5, provenance, story-state, identity, and legacy Series
suite passed 220 tests with no failures, skips, xfails, xpasses, or errors.

---

### Task 6: Add the thin CLI Map/Focus production surface

**Files:**

- Create: src/auteur/series/vertical_slice_formatters.py
- Modify: src/auteur/series/cli.py
- Modify: tests/test_series_vertical_slice_cli.py
- Modify: tests/test_series_cli.py only for parser/regression assertions.

The repository is currently CLI-led, so the smallest production surface is a guided text surface. ADR 068 freezes this as the first production expression of Map/Focus, not as a permanent frontend decision. It must preserve the prototype's interaction meaning without making the prototype's HTML an implementation dependency.

Add a series journey command family with these explicit operations:

~~~text
auteur series journey propose-series <project> --input <yaml>
auteur series journey accept-series <project> <proposal-id>
auteur series journey propose-book <project> --input <yaml>
auteur series journey accept-book <project> <proposal-id>
auteur series journey propose-outcome <project> --input <yaml>
auteur series journey accept-outcome <project> <candidate-id>
auteur series journey plan-next-book <project> --book 2
auteur series journey map <project> --book 2
auteur series journey focus <project> --book 2
auteur series journey decide <project> <proposal-id> --choice recommended|<option-id>|defer
~~~

The exact command names may be shortened only if the same authority boundaries remain visible and existing series validate|compile|diagnose|graph|bible parsing remains unchanged.

- [x] **Step 1: Write formatter and CLI contract tests.**

Test that:

- `test_map_shows_established_context_and_next_available_decision`: Map contains established context, why-now explanation, and next decision.
- `test_focus_shows_recommendation_rationale_tradeoff_and_choices`: Focus contains recommendation, rationale, tradeoff, and author choices.
- `test_default_surface_hides_revision_ids_but_deep_output_can_show_sources`: default output is beginner-readable while detail output exposes sources.
- `test_existing_full_series_commands_are_still_registered`: legacy command parsing remains unchanged.
- `test_cli_proposal_commands_do_not_accept_on_generation`: proposal commands do not create accepted records.

The default Map output must answer “what is established?”, “why does it matter now?”, and “what can I decide next?”. Focus must show the recommendation, rationale, tradeoff, and the three author choices. Raw provenance IDs are available only through an explicit detail flag or inspection operation.

- [x] **Step 2: Run CLI tests and verify red.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_cli.py tests/test_series_cli.py -q
~~~

- [x] **Step 3: Implement formatters and dispatch only through the service.**

vertical_slice_formatters.py must be pure formatting. series/cli.py must parse arguments and translate errors into existing CLI exit behavior; it must not write artifacts directly. Proposal commands save only proposals, accept commands perform explicit acceptance, and map/focus perform reads/derived rebuilds.

- [x] **Step 4: Run CLI and full Series regressions.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_cli.py tests/test_series_cli.py tests/test_series_models.py tests/test_series_compile.py tests/test_series_bible.py tests/test_series_graph.py -q
~~~

**Capability coverage:** the beginner-facing progressive-disclosure contract and the negative rule that presentation or proposal generation cannot silently make canon.

**Commit:** feat: expose series journey map and focus workflow

**Checkpoint recorded 2026-08-23:** Task 6 was implemented at isolated
worktree HEAD `e4930dd49885c653c4b0b875dec95919fd3c4b6a` and passed final
specification and code-quality review with no findings. The corrective commit
adds item-level Map provenance, progressive-disclosure help, and focused
coverage for outcome/planning/choice/error dispatch. The reviewed commits
were integrated into `main` as `3a2a3af` and `0d0f02d`. The integrated
Task 1–6, provenance, story-state, identity, legacy Series, and CLI suite
passed 234 tests with no failures, skips, xfails, xpasses, or errors.

---

### Task 7: Qualify the complete Archive of Lies journey

**Files:**

- Modify: tests/fixtures/archive_of_lies_vertical_slice/series_direction.yaml
- Modify: tests/fixtures/archive_of_lies_vertical_slice/book_1_direction.yaml
- Modify: tests/fixtures/archive_of_lies_vertical_slice/book_1_outcome.yaml
- Modify: tests/fixtures/archive_of_lies_vertical_slice/book_2_context_expected.yaml
- Modify: tests/fixtures/archive_of_lies_vertical_slice/book_2_decision_expected.yaml
- Create: tests/test_series_vertical_slice_e2e.py

Use one small, deterministic story fixture. The fixture must contain:

- an ongoing Series Direction with no future Book Plans;
- one Series commitment that can remain relevant beyond Book 1;
- a local Book 1 StoryIdentity and explicit commitment reference;
- one bounded Book 1 outcome with one accepted transition;
- one unrelated Book 1 datum that must not be surfaced solely because it is recent;
- two Book 2 decision options with distinct summaries and tradeoffs.

The fixture is not a complete roadmap and must not be made to satisfy the legacy SeriesIdentity ongoing-count validator.

- [x] **Step 1: Write one end-to-end test before adding fixture data.**

The test must execute this sequence through the service and CLI-facing read model:

~~~text
propose sparse Series Direction
accept sparse Series Direction
propose Book 1 Direction
accept Book 1 Direction
propose Book 1 outcome
assert Canonical State unchanged
accept Book 1 outcome
assert accepted transition and changed Canonical State
reload service/store
enter Book 2 planning explicitly
derive context
assert compact relevant items, why-now explanations, and source revisions
delete derived context
rebuild context
assert semantic equivalence and unchanged authority/state
propose next decision
choose recommended, another, and defer in isolated copies
assert Book 2 remains non-canonical in all three cases
render Map and Focus
assert the next useful decision is visible with rationale and tradeoff
~~~

- [x] **Step 2: Run the end-to-end test and verify red.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_e2e.py -q
~~~

- [x] **Step 3: Add the smallest Archive of Lies fixture that satisfies the test.**

Do not add future Book plans, chapters, scenes, prose, inferred dependency edges, or unrelated world-building merely to make the fixture look complete.

- [x] **Step 4: Run the complete vertical-slice suite.**

~~~powershell
python -m pytest tests/test_series_vertical_slice_models.py tests/test_series_vertical_slice_service.py tests/test_series_vertical_slice_cli.py tests/test_series_vertical_slice_e2e.py -q
~~~

- [x] **Step 5: Run all existing Series and authority regressions.**

~~~powershell
python -m pytest tests/test_series_*.py tests/test_provenance_pilot.py tests/test_structure_proposals.py tests/test_proposal_accept_apply.py -q
~~~

**Capability coverage:** the complete capability contract and all negative authority criteria.

**Commit:** test: qualify archive of lies series vertical slice

**Checkpoint recorded 2026-08-23:** Task 7 was implemented at isolated
worktree HEAD `c88a38b9cf0e1d6c86f05819a7ea5cc4852d46c8` and passed final
specification and code-quality review with no findings. The reviewed E2E
strengthens proof of projection deletion/rebuild, proposal-generation
immutability, persisted recommended/other/defer actions, and default-vs-detail
disclosure. The reviewed commits were integrated into `main` as `84efe2f` and
`f619ccf`. The integrated current-source suite passed 235 tests with no
failures, skips, xfails, xpasses, or errors.

---

### Task 8: Produce exact-candidate qualification evidence and handoff

**Files:**

- Create: docs/engineering/series-vertical-slice-qualification-v1.md
- Read/update only if needed: CONTEXT.md, docs/acceptance/series-vertical-slice-capability-contract-v1.md
- Read: docs/engineering/release-qualification.md

- [x] **Step 1: Freeze and record the candidate SHA.**

Run git rev-parse HEAD after all implementation and test changes. Qualification evidence is invalidated by any later source, test, packaging, version, or packaged-resource change.

- [x] **Step 2: Run source-qualified focused tests with the verified import.**

Record separate counts for collection, passed, skipped, xfailed, xpassed, failed, and errors. A timeout or terminated command is incomplete evidence.

- [x] **Step 3: Build and test the exact installed artifact.**

Follow docs/engineering/release-qualification.md to build from the frozen SHA and run the installed qualification path. Include the Archive of Lies journey and the existing full-Series regression set. Do not call the result release-ready; this task qualifies the vertical slice only.

- [x] **Step 4: Write the qualification report.**

The report must include:

- candidate SHA and workspace/Git identity;
- Python executable and resolved auteur.__file__;
- commands and exact categorized results;
- evidence that the sparse journey used SeriesDirection and did not create future BookPlan entries;
- evidence for each accepted authority transition;
- evidence that the rejected/alternative proposal, unaccepted outcome, derived-context deletion, and Book 2 decision actions did not mutate canon;
- the remaining deferred machinery;
- any environment or baseline failures classified according to AGENTS.md.

- [x] **Step 5: Update CONTEXT.md only with the completed slice and next bounded work.**

Do not rewrite Domain Model V1 or claim that Series architecture is complete. State that this slice is implemented/qualified only to the level supported by the evidence.

**Commit:** docs: record series vertical slice qualification

**Checkpoint recorded 2026-08-24:** Candidate
`e5236763949107424cb71f7102f5c800c1347bea` was qualified from the verified
linked checkout with Python `C:\Python314\python.exe` and an import resolving
to that checkout's `src/auteur`. The complete structured suite reported 4,421
collected, 4,393 passed, 1 skipped, 27 xfailed, 0 xpassed, 0 failed, and 0
errors. The focused seven-file matrix passed 156 serial and 156 with two
workers. The exact `auteur-0.37.1` wheel passed all 11 installed qualification
checks; SHA-256 was
`e50f952b6ef73cedca3bc6e6b4bc452b8c736101dc4c9408cfa007bbe6c0fd71`.
Qualification is bounded to this vertical slice and does not claim release
readiness or completion of Series architecture. `CONTEXT.md` was left
unchanged because no Domain Model V1 revision was warranted.

---

## Capability-to-task coverage

| Contract capability | Primary tasks | Required evidence |
|---|---:|---|
| Establish sparse Series Direction | 0-1 | accepted ongoing Direction with no future Books; proposals remain non-authoritative; reload preserves source revision |
| Establish local Book Direction | 2 | accepted Book 1 scope; Series Direction unchanged; unaccepted Book alternative inert |
| Make an outcome true | 3 | unaccepted candidate leaves state unchanged; accepted bundle rebuilds state with source refs |
| Carry relevant context into Book 2 | 4, 7 | explicit planning entry; compact selected items; why-now explanation; accepted source revisions; deterministic rebuild |
| Present next useful decision | 5-7 | recommendation, rationale, tradeoff, choose recommended/other/defer; no Book 2 canon |
| Progressive Map/Focus disclosure | 6-7 | default beginner-facing output plus optional deeper source inspection |
| Exact-candidate qualification | 0, 7-8 | trusted import, frozen SHA, categorized tests, installed-artifact evidence |

## Compatibility and migration policy

The V1 implementation has no data migration for existing SeriesIdentity documents. Compatibility is achieved by keeping the paths separate:

1. Existing full-Series commands continue to call load_series() and SeriesIdentity.from_yaml().
2. Sparse journey commands load the new journey artifact path and never pass it through the legacy loader.
3. Existing full-Series fixtures and tests are run as regressions.
4. No sparse artifact is auto-expanded into placeholder BookPlan objects.
5. No full-Series document is auto-reduced into sparse Direction.
6. A future export/migration can be added only with a separate acceptance contract and evidence that authors need it.

## Approval ledger

The following decisions were identified as material implementation choices:

1. **Resolved — thin production surface:** ADR 068 approves the existing CLI as the first production surface for Map/Focus. The prototype remains interaction evidence rather than production UI, and the eventual browser/TUI/editor surface remains open.
2. **Resolved — bounded decision actions:** ADR 069 defines “Choose another option” as selecting an option from the exact current `NextDecisionProposal`. Unknown options are rejected; all three actions remain non-authoritative; free-form Book 2 Direction authoring is deferred.
3. **Resolved — storage boundary:** ADR 070 approves `.auteur/series/vertical-slice/` for sparse journey payloads and the existing `.auteur/state/artifacts/` store as the sole shared provenance metadata authority. Accepted realization history, not `derived/canonical-state.yaml`, is authoritative; derived files are rebuildable.

The deterministic explicit carry-forward rule, non-authoritative decision proposal, separate sparse/full Series boundary, and no-generalized-machinery policy are already settled by the handoff and are not reopened here.

## Self-review

- **Spec coverage:** all five capabilities, explicit acceptance, accepted state change, Book 2 transition, relevance explanations, next decision, rebuildability, negative authority rules, compatibility, qualification, and deferred machinery map to tasks above.
- **Placeholder scan:** no task is left as an unnamed future action. Where the exact application code is new, the plan gives the file, type boundary, operation signature, test name/behavior, command, and expected result.
- **Type consistency:** ArtifactRef, SeriesDirection, BookDirection, StateTransition, RealizationCandidate, AcceptedRealizationBundle, CanonicalState, PlanningEntry, CarryForwardItem, BookPlanningContext, DecisionOption, NextDecisionProposal, and DecisionAction are introduced once and reused consistently across Tasks 1-7.
