# Working Book Architecture: implementation plan

**Status:** plan for the design in [2026-11-12-working-book-architecture-design.md](../specs/2026-11-12-working-book-architecture-design.md). It is not authorization to implement. Each increment is a separate responsibility, and the owner-reserved decisions in the design (O1–O3) must be settled before the increments that depend on them.
**Baseline:** `origin/main` at `8b53b32f`.
**Revised** after the independent challenge. The dispositions are in the [worked example README](../../qualification-evidence/working-book-architecture-design-20261112/README.md#challenge-and-reconciliation).

## Sequence

| # | Increment | Depends on | Owner decision needed first? | Retained value |
|---|---|---|---|---|
| 0 | Authority guard | none | No | Closes gap G8 for host-agent responses that pass through `complete_architecture` |
| 1 | Durable Working Book Architecture (develop and resume) | 0 | No | One Book's full function survives a fresh process. A fresh-agent develop trial is the exit gate |
| 2 | Book revision lifecycle (review, apply, withdraw, Book-to-Series proposal) | 1 | No | A Book change is bounded, reviewable and reversible |
| 3 | Series-to-Book inheritance from accepted sources | 2 | Partly (the carry-forward rule; see below) | Inherited conditions come from accepted history, not a fixture table |
| 4 | Cross-Book consequence inspection | 2, and the working-predecessor reference introduced in 1 | No | A Book change lists the later Book artifacts it may affect |
| 5 | Author-facing integration | 1 at least; 2 for revision views | Yes (O1) | The author can inspect and revise the Book artifact in the Studio |

Increments 3 and 4 can proceed in parallel after 2. Increment 5 waits for the owner's decision on O1.

## Increment 0: authority guard

**Objective.** An agent response that passes through `complete_architecture` cannot declare `author_declared` provenance.

**Retained value.** The label that means "an author wrote this" can only be produced by an author action, for host-agent responses. This is the sharpest authority gap in the investigation (the probe, `authority_probe`).

**Reuse.** The existing `EmotionTarget.provenance` field and the `new_host_agent_response` context, which already distinguish agent responses.

**Files.**
- `src/auteur/beginner/studio_architecture.py`: `ArchitectureCandidate.valid_graph` (the `context.get("new_host_agent_response")` branch) rejects any emotion target whose provenance is `author_declared`.
- A test in the existing Studio architecture test set.

**Interfaces.** None. Behaviour changes only for agent responses that carry `author_declared`.

**Authority safeguards.** The check fails closed. Accepted artifacts are untouched, because this validator is used only for host-agent responses. Direct edits to the stored candidate file are outside this guard, and the design does not rely on it for those.

**Tests (TDD).**
1. Red: the probe's `authority_probe` case, as a unit test, expects a `ValueError` for an agent response with `author_declared`. It fails today.
2. Green: add the check.
3. Regression: existing Studio architecture tests and `tests/test_beginner_studio_architecture_apply_cli.py` still pass.

**Evidence of completion.** The probe rerun reports `author_declared_accepted_from_agent_response: false`. The focused tests pass.

**Validation.** L1 focused. No boundary change beyond the validator.

**Deferred.** An author-only operation to set `author_declared` (O2).

## Increment 1: durable Working Book Architecture (develop and resume)

**Objective.** One Book's function can be developed for a Book, stored, and recovered by a fresh process, with the sections the spike measured preserved as verbatim text and the structured fields the design specifies populated.

**Retained value.** Book 24's detailed function survives as a structured artifact that a fresh agent can resume. This is the first point at which Book-level work has a durable home.

**Reuse.**
- The lock (`_FilesystemLock`, `src/auteur/beginner/persistence.py`, line 377) and the atomic JSON writer (`_atomic_json_write`, `src/auteur/host_agent.py`, line 38) are used directly, not moved.
- The latest-request pointer and the request, review and current handling are extracted from `prepare_architecture`, `complete_architecture` and `apply_architecture_review` (`src/auteur/beginner/studio_architecture.py`, lines 952, 1026 and 1101) into `auteur.working_revision`. Studio then calls the extracted module. The change is behaviour-preserving.
- `src/auteur/host_agent.py` for request and response records.
- `ArtifactRef` and `AcceptedFactRef` (`src/auteur/series/vertical_slice_models.py`) for references to accepted sources. Increment 1 uses only the Series candidate and the working predecessor, so this reuse is minimal.
- The `DependencyType` vocabulary (`src/auteur/series/models.py`, line 23).

**Files.**
- New: `src/auteur/working_revision.py`. The extracted pointer and record handling. No Studio or Series imports.
- Changed: `src/auteur/beginner/studio_architecture.py`. Calls the extracted module. The Studio candidate's behaviour and records are unchanged.
- New: `src/auteur/series/working_book_architecture.py`. Schema v1 (sections as in the design §5.3), validator, `book_prepare`, `book_complete`, `book_resume`, and the resume packet builder.
- Changed: `src/auteur/beginner/studio_architecture.py` `main()`, or a sibling dispatcher, to expose `book-prepare --book N`, `book-complete-file --book N --candidate FILE` and `book-resume --book N`. The bridge doc `docs/agents/studio-architecture-bridge.md` gains a Book section.
- New tests under `tests/`, one file for the Book artifact and one for the extracted lifecycle.
- New fixture: a reduced Book artifact (three sections) under `tests/fixtures/`. The full Book 24 artifact is not committed as a fixture, because it is a noncanonical experiment.

**Interfaces.**
- `WorkingBookArchitecture` (Pydantic, `extra="forbid"`): `book_number`, `title`, `function` (question, pressure, `reader_experience_refs`), `inherited`, `engines`, `agents`, `choice`, `local_resolution`, `series_consequences`, `later_possibilities`, `assumptions`, `alternatives`, `unresolved`, `open_author_decisions`, `typed_edges`.
- Each element has `id`, `provenance` (the enum in design §5.5, where `unlabelled` is not a valid schema-write value), `text`, `refs`.
- `inherited[]` elements take `source` `working_predecessor` (with a revision reference) or `accepted_fact` and `accepted_direction` (added in Increment 3).
- `open_author_decisions[]` reference a Series open question by its index and the SHA-256 of its text, checked against the referenced Series revision.
- `agents[]` carry `name_source`. A named agent without one is flagged.
- `BookRevisionRecord`: `request_sha256`, `base_series` (Series request SHA and referenced node fingerprints), `source_sha256`, `design_guidance_sha256`, `intention_sha256`, `content_sha256`.

**Authority safeguards.**
- Apply writes only `architecture/books/<n>/current.json`. The test compares digests of every other file before and after.
- No Book command reaches `ArtifactStore.accept` or `accept_book_direction`. A test patches both to raise and runs every Book command.
- The validator rejects `author_declared` from agents (Increment 0), rejects a reference that does not resolve in the referenced Series revision, and rejects `unlabelled` provenance on a schema write.
- An agent-proposed assumption without a reversal is a validation error (design §5.3).
- A stale Series revision at completion is refused and the response is retained as stale evidence, as in Studio.
- An agent creates no character commitments, character nodes, arcs or relationship states. Named agents need a `name_source`.

**Tests (TDD).**
1. Schema accepts the reduced fixture. It rejects unknown ids, unknown provenance, `author_declared`, `unlabelled` on a schema write, and an agent-proposed assumption without a reversal.
2. Develop: `book-prepare` writes a request and the latest pointer; `book-complete-file` writes `current.json`; both are idempotent for the same response.
3. Fresh process: `book-resume` in a new process returns the packet, with all required sections and the revision identity.
4. Authority: after develop, the accepted directories, the Series candidate and the ArtifactStore sidecars are byte-identical to before.
5. No accept path: every Book command runs with the accept functions patched to raise, and none is reached.
6. Stale Series: change a referenced Series node after prepare. Completion is refused and the response is retained.
7. Open-question reference: change the text of a referenced Series open question after prepare. The reference is refused as stale.
8. Named agent without a `name_source` is flagged.
9. Regression: the Studio candidate's develop, revise, apply and resume tests still pass after the extraction.
10. Packet budget: the packet for the reduced fixture is within a stated bound, and its constraint block contains no Book-internal ids.

**Dependencies.** Increment 0.

**Exit gate (required).** Increment 1 is not complete until a fresh-context agent, given only the resume packet for Book 24, develops the Book artifact through the CLI, and a separate reviewer checks the result against the source for section coverage, provenance, reversal conditions, decision references and character-commitment boundaries. The result is recorded whatever it shows. This is the test of whether the artifact works for an agent, and it is untested today. A lost-content finding is a result, not a reason to omit the gate.

**Evidence of completion.** All tests above pass at a recorded commit. A CLI walkthrough across separate processes, with the reduced fixture, produces a transcript (the lifecycle evidence folder is the model). The exit gate's result is recorded.

**Validation.** L1 focused for the new modules. L2 targeted integration for the named changed boundary, which is the Studio architecture extraction: the Studio architecture tests, the apply CLI test file, and the Studio server route for architecture (`src/auteur/beginner/server.py`, the apply call at line 749, under `api/beginner/studio/canvases/<id>/architecture/apply`). L3 is not triggered.

**Deferred.** Revision (Increment 2). Inheritance from accepted sources (Increment 3). UI (Increment 5).

## Increment 2: Book revision lifecycle

**Objective.** A Book artifact can be revised as a bounded change to named elements, reviewed, applied, and withdrawn, with preserved elements verified. A Book change that needs a Series change is proposed to the Series owner, not written.

**Retained value.** The craft-mark case from the design becomes an executable test: one element changes, the others are preserved by hash, the consequence list is produced, and the Series is untouched unless its own lifecycle applies a change.

**Reuse.** `apply_architecture_review` (`studio_architecture.py`, line 1101) is generalized through the extracted module. The freshness fingerprints and the superseded-request rule are reused. `candidate_diff` and `build_architecture_review` (`src/auteur/beginner/studio_architecture_review.py`) provide the review pattern.

**Files.**
- Changed: `src/auteur/working_revision.py`. Apply and review are generalized to take a diff function.
- Changed: `src/auteur/series/working_book_architecture.py`. `book_prepare` with `--instruction` and `--target` element ids; a section-level diff; the preserved-set check; `book_withdraw` for one element; `book_series_proposal`, which prepares a Studio revision request citing the Book's consequence ids.
- Changed: the bridge dispatcher (`book-apply-review --request-sha256`, `book-withdraw --element ID --rationale TEXT`, `book-series-proposal --book N`).
- Tests and a walkthrough under `docs/qualification-evidence/`.

**Interfaces.** `BookReviewRecord`: `changes` (added, changed and removed, by element id), `preserved` (ids whose content hash is unchanged), `unexpected_changes` (changes outside the targets), `consequence_candidates` (the typed edges and the Series-link reach in this increment; Increment 4 adds cross-Book candidates).

**Revision request contents (decided).** A revision request carries the full text of every target element and of each element that depends on a target. It does not carry only the resume packet. The packet orients; it does not revise (design §5.7).

**Authority safeguards.**
- A change outside the declared targets is reported as an unexpected change. It is not applied silently.
- Apply is refused unless the review exists, is for the latest request, and the baseline and freshness fingerprints still match.
- `book-withdraw` marks an element `rejected` with a rationale. It changes only the Book artifact.
- `book-series-proposal` prepares a Studio revision request. It does not write the Series. The Series changes only through its existing lifecycle, after author review.

**Tests (TDD).**
1. Bounded revision: a change to one target preserves every other element by hash, and the review lists the change and the preserved set.
2. Unexpected change: a change outside the target is reported and blocks apply unless the request was holistic.
3. Unreviewed, superseded, baseline-changed and stale-Series requests are each refused, with a clear message.
4. Apply writes only the Book's `current.json`. The digest test from Increment 1 still passes.
5. Withdraw: the element is `rejected`, the rationale is recorded, the other elements are unchanged, and the Series is untouched.
6. Series change after apply: the Book's freshness becomes `stale` and its semantic impact `suspect` (for a changed node) or `contradictory` (for a removed node).
7. Book-to-Series proposal: a Book revision that needs a Series change produces a Studio revision request that cites the consequence ids, and does not write the Series.
8. Craft-mark adequacy: the revision request for the craft-mark carries all twelve target elements and their dependents, including the six that the packet omits (`s3_engine_04`, `s5_06`, `s5_07`, `s5_08`, `s6_01`, `s6_05`).

**Dependencies.** Increment 1.

**Evidence of completion.** The tests pass. A lifecycle walkthrough reproduces the craft-mark counterfactual (design, Demonstrations B and D) across separate processes, and its transcript records the preserved-element counts. The counts should match the probe's twelve changed items and their preserved complement, or explain any difference.

**Validation.** L1 focused. L2 for the named boundary, which is the generalized apply: the Studio architecture apply tests and the apply CLI test file.

**Deferred.** A holistic revision UI. Branch-keyed storage for two complete Book alternatives (the design shows that recorded alternatives within one artifact are sufficient for now).

## Increment 3: Series-to-Book inheritance from accepted sources

**Objective.** A Book's inherited conditions can reference accepted history explicitly, instead of depending on a fixture table.

**Retained value.** A later Book inherits accepted outcomes through typed references that the validator checks for currency. The hard-coded table is no longer needed.

**Reuse.** `derive_book_context` (`src/auteur/series/vertical_slice_service.py`, line 1233), `CarryForwardItem` (`vertical_slice_models.py`, line 440), `validate_book_context_source` (`vertical_slice_store.py`, line 637), `AcceptedFactRef`, and `GlobalMapSnapshot` (for focus, not for storage).

**Files.**
- Changed: `src/auteur/series/vertical_slice_service.py`. `_BOOK_CONTEXT_STATE_TRANSITIONS` (lines 66–77) is removed. Its archive-of-lies behaviour is reproduced by an explicit inherited-condition reference in the fixture, not by a table.
- Changed: `src/auteur/series/working_book_architecture.py`. `inherited[]` elements can carry an `AcceptedFactRef` (`accepted_fact`) or an `ArtifactRef` to an accepted Book direction (`accepted_direction`). The validator checks currency with `validate_book_context_source`.
- Tests: the existing archive-of-lies context tests must still pass unchanged.

**Interfaces.** `InheritedCondition` sources `accepted_fact` and `accepted_direction`, each with `source_ref` and a currency check at completion. (`working_predecessor` is introduced in Increment 1.)

**Authority safeguards.**
- No automatic selection rule. The inheriting Book lists the references it uses, and each is checked for currency.
- Accepted sources are read only. No accepted record is written.

**Owner decision needed first.** The carry-forward selection rule. The design's default is explicit selection in the Book artifact, with no automatic rule. If the owner wants an automatic rule, that is a product decision and must be escalated, not inferred.

**Tests (TDD).**
1. The archive-of-lies context derivation produces the same items without the table (regression).
2. A Book with an explicit `accepted_fact` reference is refused if the fact is superseded or the revision is stale.
3. A Book with an explicit `accepted_direction` reference is refused if the direction's revision has changed.
4. No accepted file is written by any Book operation.

**Dependencies.** Increment 2.

**Evidence of completion.** Regression tests pass. A worked example shows Book N inheriting from an accepted predecessor through explicit references.

**Validation.** L1 focused, plus L2 for the changed boundary: the Series vertical-slice context and acceptance tests, since the table removal is a boundary change.

**Deferred.** Any automatic carry-forward rule. Inheritance from predecessors that exist only as working artifacts beyond one step.

## Increment 4: cross-Book consequence inspection

**Objective.** When a Book artifact changes, the inspection lists the later Book artifacts that reference its elements, and their freshness. It also lists accepted Book directions whose Series commitments are affected through a changed Series node.

**Retained value.** The consequence trace in the design (Demonstration B) extends across Books, not only to the Series.

**Reuse.** The `series_impact` pattern (`vertical_slice_service.py`, line 1056), the transitive-dependent algorithm in `realization_impact` (line 1000), ADR 013 edge semantics, and the `Lifecycle` and freshness vocabulary.

**Files.**
- Changed: `src/auteur/series/working_book_architecture.py`. `book_impact --book N` traverses typed edges from Book N's elements to later Book artifacts' `inherited[]` and `typed_edges` targets, and to accepted Book directions through the Series commitments they carry.
- Changed: the bridge dispatcher.

**Interfaces.** `ImpactEntry`: `book_number`, `element_id`, `dependency` (the typed edge or inherited reference), `freshness`, `semantic_impact`, `reconciliation_required`.

**Authority safeguards.** The output is a list for review. Nothing is applied, rewritten, or accepted.

**Tests (TDD).**
1. A change to a Book N element lists the Book N+1 artifact that references it, and no others.
2. A Book N+1 whose referenced element is unchanged is `fresh`.
3. An accepted Book direction whose Series commitment references a Series node that changed is reported, and is not modified. Accepted directions hold no working elements, so they are reported only through the Series commitments they carry.
4. The report is deterministic: the same inputs produce the same output.

**Dependencies.** Increment 2, and the working-predecessor reference introduced in Increment 1.

**Evidence of completion.** Tests pass. A worked example shows the Book 24 to Book 25 consequence list, with no Book 25 artifact written.

**Validation.** L1 focused. No accepted boundary is changed.

**Deferred.** Automatic reconciliation. Chapter and Scene scope.

## Increment 5: author-facing integration

**Objective.** The author can inspect the Book artifact's elements, their provenance, the missing reversals, the freshness and the consequence list, and can revise it through the existing Studio interface.

**Retained value.** The artifact is reviewable by the author, not only by agents.

**Owner decision needed first.** O1: whether Book detail may become accepted Book Direction content. The UI's acceptance affordance depends on it. Without that decision, the UI can show and revise working material but cannot offer acceptance.

**Files (indicative, not planned in detail).** `src/auteur/beginner/server.py` (routes near the architecture apply route at line 749), a new Studio panel, and tests for the routes. The UI design is a separate responsibility.

**Authority safeguards.** No acceptance action is exposed unless O1 is decided. Any acceptance goes through the existing `propose_book_direction` and `accept_book_direction` path. The existing gate is a constant author label (G12), so an acceptance UI must add an interactive confirmation that the owner specifies, before it is offered.

**Deferred.** Everything not needed to inspect and revise.

## Deferred across all increments

- Chapter and Scene scope. The design leaves room for a Chapter artifact that references the Book artifact.
- A universal narrative graph, a graph database, numerical quality scores, and LLM-based name checks.
- Author-only `author_declared` operations (O2).
- Typed finale-alternative edges (O3). The evidence gate is the Demonstration B gap (G5): the trace reaches no finale alternative. The owner decides whether this matters enough to type.
- Changes to `SeriesIdentity`, `BookPlan`, or the contiguity rule.
- Stable open-question identifiers in the Studio candidate (design §8). A separate Studio change. Until then, open questions are referenced by index and text hash.
- Revision-note provenance (design G10). A separate Studio change.
- Branch-keyed storage for complete alternative Book artifacts.
- Structured fidelity for sections 4–8 beyond verbatim text. The design's §5.3 fields for those sections are a target. Whether an agent fills them faithfully is tested by the Increment 1 exit gate, not assumed.

## Verification budget

- Increment 0: L1.
- Increment 1: L1 for the new modules, L2 for the Studio extraction boundary, and the fresh-agent exit gate.
- Increment 2: L1, plus L2 for the generalized apply.
- Increment 3: L1, plus L2 for the table removal in the Series context boundary.
- Increment 4: L1.
- Increment 5: L1 and route tests. A product walkthrough is a separate qualification.
- L3 is not required by any increment. Release qualification is not part of this plan.

## Completion language

- "Implemented" means the code exists.
- "Focused tests pass" means only the named L1 tests passed.
- "Boundary tests pass" means the named L2 boundary passed.
- "Works for an agent" is not claimed until the Increment 1 exit gate has been run and recorded.
- "Integrated" is claimed only after a merged commit is verified on `origin/main`.
