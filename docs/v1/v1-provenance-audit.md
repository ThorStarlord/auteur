# Auteur V1 Authority / Provenance Closure Audit

**Audit baseline:** V1 closure branch derived from `main @ 2182da50f56df5a9bc139eb0b310cc18fd1d7e4a`.  
**Question:** Does V1 require a new provenance architecture, or only bounded reconciliation/qualification of existing authority paths?

## Conclusion

**No new provenance architecture is warranted for V1.** The current repository already has the mechanisms needed by the V1 promise: explicit owning-workflow acceptance, durable revisions/history, content/source hashes, currentness/staleness checks, fail-closed proposal/revision preconditions, accepted-source Expression composition, and ArtifactStore-backed accepted history for the contemporary Series vertical slice.

The closure audit did uncover two concrete defects in existing cross-cutting behavior, and both were fixed at their owning boundaries rather than by adding a second provenance system:

1. non-YAML semantic hashing trimmed trailing spaces by iterating characters rather than lines, so canonically equivalent Markdown/Unicode/line-ending forms could hash differently;
2. Book freshness checked accepted Chapter revision/hash but did not propagate a Chapter's own stale/invalid upstream Scene dependencies, allowing a byte-identical accepted Book to remain apparently fresh for publication.

V1 now normalizes non-YAML content by lines before NFC hashing, propagates accepted Chapter health/freshness into Book inspection, and makes publication reject a transitively stale accepted Book until it is reconciled/recomposed/reaccepted.

Repository-wide normalization of every derived report/session/map into one lifecycle store remains explicitly unnecessary.

## Classification

| Artifact family | Classification | V1 rationale / evidence seam |
| --- | --- | --- |
| StoryIdentity | `A — ALREADY_IMPLEMENTED` | explicit Story Discovery/Identity acceptance; Golden Path asserts no canonical mutation before acceptance |
| Blueprint / Structure | `A — ALREADY_IMPLEMENTED` | proposal selection and plans remain noncanonical; `RevisionService` owns explicit application with currentness preconditions |
| Chapter Structure / Outline | `B — SEMANTICALLY_EQUIVALENT` | existing accepted outline/provenance semantics and structural revision/impact paths satisfy the bounded V1 contract without one universal store |
| Scene Realization | `A — ALREADY_IMPLEMENTED` | ArtifactStore revision/currentness plus deterministic state/knowledge validation; V1 topology exercises 60 accepted Scenes and restart |
| Scene Expression | `A — ALREADY_IMPLEMENTED` | source Scene revision/hash, candidate lifecycle, explicit acceptance, stale/review/divergence states, plus V1 structured boundary evidence service |
| Chapter Expression | `B — SEMANTICALLY_EQUIVALENT` | accepted Scene/transition dependencies and Chapter Expression lifecycle/reconciliation use their established dedicated store |
| Book Expression / Manuscript | `B — SEMANTICALLY_EQUIVALENT` | dedicated Book lifecycle remains valid; closure adds transitive Chapter freshness propagation and stale-publication blocking |
| Series Direction / accepted Series state | `B — SEMANTICALLY_EQUIVALENT / BOUNDED` | contemporary Series vertical-slice store delegates accepted artifact revision history to ArtifactStore; Global Map/Focus remain derived |
| Universe | `E — OUTSIDE AUTHORITY-COMPLETE V1 CLAIM` | optional supporting context is retained, but V1 does not claim a provenance-normalized Universe authoring vertical |
| Tutor sessions / Decision Cards / handoffs | `D — DERIVED_NOT_REQUIRED` | local/derived by contract; source fingerprints/currentness protect actionability without granting narrative authority |
| proposals / revision plans / previews / reassessment | `D — DERIVED_NOT_REQUIRED` | durable and currentness-bound where needed, but remain noncanonical until the existing owning authority action |
| maps / dashboards / reports | `D — DERIVED_NOT_REQUIRED` | rebuildable/read-only projections; persistence never grants authority |

## V1-specific closure additions

1. Structure proposal selection is extracted into `ProposalReviewService`, shared by CLI and browser adapters.
2. `AuthorActionService` centralizes the browser's bounded decision-loop operations over existing authority services.
3. `ExpressionBoundaryService` persists structured Realization evidence against draft prose candidates; blocking contradictions cannot be accepted and cannot mutate Scene Realization.
4. `recover_interrupted_revisions()` fail-closes plans stranded in `applying`: only hash-proven unchanged targets may return to `ready`; ambiguous changed targets become `failed`; no automatic authority replay occurs.
5. Provider failures use a stable provider-independent vocabulary; invalid generated Tutor proposal JSON/schema/patches use `structured_output_invalid` without changing story authority.
6. Semantic non-YAML hashing now normalizes by line, trailing spaces, line endings, and Unicode NFC before hashing.
7. `BookExpressionStore.inspect()` now treats an accepted Chapter that is stale/invalid from its own upstream dependencies as a stale Book source.
8. `PublishingSnapshot` refuses to promote a transitively stale accepted Book even when the Book manuscript bytes still match their accepted hash.
9. A continuous 20-Chapter/60-Scene V1 fixture now traverses accepted Scene Expression → Chapter Expression → Book Expression → HTML/EPUB publication, restarts/reloads, then changes one accepted Scene and proves Chapter → Book staleness plus publication rejection.
10. Corruption/rebuildability tests distinguish authoritative Book corruption (block) from loss of derived publishing records (rebuild without authority mutation).

## Residual evidence gates

These are qualification gates, not missing provenance architecture:

- exact-head CI across the supported OS/Python matrix;
- installed-wheel qualification;
- hermetic V1 author-journey bundle;
- opt-in live Anthropic and OpenAI adapter smoke using authorized credentials;
- bounded beginner owner dogfood of Workspace V2.

If any of those gates exposes a concrete authority defect, fix the smallest owning path. Do not respond by creating a second canon database or generic workflow engine.
