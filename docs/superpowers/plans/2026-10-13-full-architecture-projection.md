# Full Architecture Evidence Projection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Assemble one source-honest, read-only Book Identity + Structure projection that distinguishes genre morphology, candidate interpretations, author working additions, and accepted commitments.

**Architecture:** Implement a pure deterministic projector and review-state derivation using existing `ArchitectureCandidate`, `GenrePack` and CanvasStore shapes as inputs, not a new persistent story model. Preserve each source's authority, SHA/revision, genre-local identity and relation verb. Return one typed projection that both the prototype and live Studio can display.

**Tech Stack:** Vanilla ES modules, Node `node:test`, existing Python/Pydantic schema fixtures, no network or provider calls.

**Spec:** `docs/superpowers/specs/2026-10-12-full-narrative-architecture-synthesis-design.md`

## Global Constraints

- Complete design means **Book-level Identity + Structure**. Scene-by-scene Realization and prose remain optional.
- Canonical layers and scope are owned by `docs/narrative-architecture.md`; do not add a new narrative authority or write to CanvasStore.
- The Studio `ArchitectureCandidate` schema in `src/auteur/beginner/studio_architecture.py` has at most **80 nodes, 180 links, 14 genre contracts, 32 phases** and the six basic emotions `joy|sadness|fear|anger|disgust|surprise`.
- `GenrePack` evidence is only verified when supplied with actual `pack_id`, `version`, `content_hash`, applicability and rule strength from `src/auteur/genre_packs/models.py`. The projector must not invent a pack or treat a Studio candidate `genre_contracts[].trope_functions` as a verified rule.
- `CanvasItem.architecture_role`/`proposal_origin` are optional, and currently exist only on unmerged Studio #408+; preserve old items with no metadata.
- Accepted Identity/Structure input is optional and **read-only**; never derive acceptance from working adoption.
- No guessed graph links from matching titles, accidental trope→emotion causality, global originality scores, or silent host-agent invocations.
- Keep each PR <=500 diff lines and <=12 changed files; use local L1 tests without paid CI.

## Review Focus

1. **No verified Pack for Progression Fantasy:** morphology coverage must be `unknown`, while candidate-contract trope and engine remain visibly `candidate_genre_interpretation` (Task 1).
2. **Same trope phrase in two genres:** preserve distinct `genreId/sourceRef` records; never merge by title or imply identical strength (Task 2).
3. **Novel-looking author working item without a genre match:** classify as `author_added_relative_to_available_sources` or `unattributed_or_unknown`, not as proven original (Task 2).
4. **An emotion target referenced by a genre:** it is a genre-level proposed target, not automatically a causal link from an individual trope (Task 3).
5. **Source revision changes or two contradictory sources:** projection marks source mismatch/contradiction for review; never silently rebinds an identical title or mutates authored work (Task 4).

---

## Exact file map

- Create `docs/prototypes/full-architecture/projection.mjs` — pure `projectFullArchitecture` and `sourceFingerprint`, exact-source genre/working/structure/emotion assembly.
- Create `docs/prototypes/full-architecture/review.mjs` — pure `reviewFullArchitecture` readiness item derivation and recommendation of actionable next focus, no scoring.
- Create `docs/prototypes/full-architecture/projection.test.mjs` and `review.test.mjs` — Node regression suites.
- Create `docs/prototypes/full-architecture/fixtures/paladin.json` and `fixtures/empty-evidence.json` — explicitly synthetic contract-shaped examples, including missing Pack coverage.
- Reuse production `ArchitectureCandidate` and `GenrePack` schemas as validation references; avoid changing them to fit the visual design.

## Shared interfaces and authority labels

`projectFullArchitecture({candidate,requestSha,workingItems=[],canvasRevision=null,genreEvidence=[],legacyEvidence=[],acceptedIdentity=null,acceptedStructure=null}) -> Projection`

- `Projection.fingerprint`: exact request SHA, canvas revision, accepted-owner reference and supplied pack IDs/versions/hashes.
- `Projection.identity`: `{working,accepted,readerExperience,genres}`; never flatten working and accepted.
- `Projection.genreViews[]`: one per candidate/accepted referenced genre, with `{genreId,title,role,packCoverage,morphology[],candidateInterpretations[],usage[]}`.
- `Projection.storySpecific[]`: `{itemId,title,role,classification,authority,sourceRef,reason,linkedRefs}` where classification makes **only relative** claims to attached evidence.
- `Projection.structure`: `{engines,phases,interactions,explicitLinks}`; each source-local link retains its verb and ref.
- `Projection.emotionalDesign`: `{basicTargets,richExperiences,trajectory}`, respecting Identity/Structure/Realization boundaries.
- `Projection.typedLinks[]`: exact endpoints, verb, source type, authority and source fingerprint; never synthesize trope→emotion edges.
- `Projection.issues[]`: missing author decisions, source gaps, conflicts, stale refs, including direct focus targets.

`reviewFullArchitecture(projection) -> {status:"draft"|"ready_for_author_review",items:ReviewItem[],summary:string}`. Each `ReviewItem` has `{id,kind,state,why,sourceRefs,focusTarget?}` where `state` is one of `not_applicable|not_established|open_author_decision|specified|integrated|reviewed|intentionally_deferred`. This review **does not accept canon**.

### Task 1: Genre evidence and per-genre morphology

**Files:** Create `projection.mjs`, `projection.test.mjs`, and both fixture files.
**Consumes:** the exact `GenrePack`/legacy contract and Studio candidate fields.
**Produces:** `sourceFingerprint(inputs)`, `projectFullArchitecture(inputs).genreViews[]`.

- [ ] **Step 1: RED tests.** Add `test('missing pack is unknown, not genre noncompliance')`, `test('versioned pack keeps exact strength and content hash')`, and `test('legacy contract stays legacy')` to `projection.test.mjs`. Use `paladin.json` without Progression/Heroic pack; attach a separately labelled mock GenrePack with an actual version/hash for the evidence branch.
- [ ] **Step 2: Run red.** `node --test docs/prototypes/full-architecture/projection.test.mjs` must fail for missing projection export/behaviors.
- [ ] **Step 3: Implement.** In `projection.mjs`, export `sourceFingerprint(inputs)` and `projectFullArchitecture(inputs)`, first materializing per-genre records by **genre ID** and only displaying genuine Pack/legacy evidence under its exact status. `genre_contracts[].trope_functions` belongs under candidate interpretation.
- [ ] **Step 4: Run green.** Same Node command passes the three tests; no fixture field is mutated.
- [ ] **Step 5: Commit.** `git add docs/prototypes/full-architecture/{projection.mjs,projection.test.mjs,fixtures} && git commit -m "feat(studio): derive genre-relative architecture evidence"`

### Task 2: Source-local story additions and comparison

**Files:** Modify `projection.mjs`, `projection.test.mjs`.
**Consumes:** Task 1 `genreViews[]`, optional `workingItems[]`.
**Produces:** `Projection.storySpecific[]`, each genre's `usage[]` with exact source status.

- [ ] **Step 1: RED tests.** `same_phrase_two_genres_remains_two_source_records`, `candidate_trope_is_not_pack_convention`, `adopted_working_item_not_accepted`, `unlinked_working_addition_is_not_globally_original`, `old_item_without_role_is_safe`.
- [ ] **Step 2: Run red.** `node --test docs/prototypes/full-architecture/projection.test.mjs` fails only on missing new behavior.
- [ ] **Step 3: Implement.** Match by explicit source-local IDs/provenance, **never title similarity**. Known adaptation/subversion requires an explicit author decision/edge; otherwise label it `unattributed_or_unknown` and expose the missing relation.
- [ ] **Step 4: Run green.** Same Node command passes; a changed working title retains historical provenance but is not treated as unmodified source text.
- [ ] **Step 5: Commit.** `git add docs/prototypes/full-architecture/{projection.mjs,projection.test.mjs} && git commit -m "feat(studio): compare source-local genre uses with author additions"`

### Task 3: Reader emotional intentions and integrated Structure

**Files:** Modify `projection.mjs`, `projection.test.mjs`.
**Consumes:** `candidate.emotion_targets[]`, `genre_contracts[]`, `phases[]`, `links[]` and optional accepted Identity/Structure.
**Produces:** `Projection.emotionalDesign`, `Projection.structure`, `typedLinks[]`.

- [ ] **Step 1: RED tests.** `six_basic_targets_keep_role_provenance`, `rich_hope_awe_not_coerced_into_basic_emotion`, `genre_emotion_is_not_trope_causality`, `phase_genre_activation_retains_role_and_order`, `only_explicit_links_get_function_verbs`, `accepted_vs_working_remain_distinct`.
- [ ] **Step 2: Run red.** Focused Node test command fails as expected.
- [ ] **Step 3: Implement.** Preserve `reader promise -> structure progression` as proposed explicit links only; keep character felt state and prose out of this Book-level projection. Sort phases by recorded `order`, but preserve `parallel_with`.
- [ ] **Step 4: Run green.** All projection tests pass; no new cross-source link is synthesized.
- [ ] **Step 5: Commit.** `git add docs/prototypes/full-architecture/{projection.mjs,projection.test.mjs} && git commit -m "feat(studio): project emotional intent and Book structure"`

### Task 4: Review states and source staleness

**Files:** Create `review.mjs`, `review.test.mjs`; modify `projection.mjs` only for missing source signals.
**Consumes:** `Projection` from Tasks 1–3.
**Produces:** `reviewFullArchitecture(projection)`.

- [ ] **Step 1: RED tests.** `missing_pack_is_not_author_failure`, `missing_primary_reader_goal_yields_open_author_decision`, `unlinked_engine_is_specified_not_integrated`, `optional_scenes_can_be_intentionally_deferred`, `stale_sha_blocks_false_readiness`, `review_never_marks_accepted`.
- [ ] **Step 2: Run red.** `node --test docs/prototypes/full-architecture/review.test.mjs` fails for missing export.
- [ ] **Step 3: Implement.** Deterministic coverage/status decisions from actual fields and explicit author acknowledgement. No creativity scores, guessed Pack rule or automatic canonical write.
- [ ] **Step 4: Run green.** Run both Node test files; validate frozen inputs are unchanged.
- [ ] **Step 5: Commit.** `git add docs/prototypes/full-architecture/{review.mjs,review.test.mjs} && git commit -m "feat(studio): derive author-decision review without canonization"`

### Task 5: Dense and adversarial projection qualification

**Files:** Extend `projection.test.mjs`, `review.test.mjs`, fixtures only as needed.
**Consumes:** frozen exact projection APIs.
**Produces:** tested handoff contract for the Full UI plan.

- [ ] **Step 1: RED adversarial cases.** `80_nodes_180_links_14_genres_stay_bounded`, `deleted_or_replaced_source_is_unavailable_not_title_rebound`, `contradictory_genre_claims_remain_distinct`, `empty_draft_still_renders_open_review`, `bad_pack_hash_is_not_verified`.
- [ ] **Step 2: RED run.** `node --test docs/prototypes/full-architecture/*.test.mjs`.
- [ ] **Step 3: Implement smallest repairs.** Avoid schema expansion or external lookups; if no explicit source exists, expose an unknown source-status record.
- [ ] **Step 4: GREEN run.** Same command plus `node --check docs/prototypes/full-architecture/projection.mjs` and `node --check docs/prototypes/full-architecture/review.mjs`.
- [ ] **Step 5: Commit and hand off.** Commit targeted fixtures/tests; open reviewable PR(s) <=500 diff lines/12 files. Report that **pure projection passing is not a real Studio or accepted-Identity qualification**.

**Completion boundary:** This plan produces a trustworthy read-only data contract, not a UI, accepted story, or live Studio feature.
