# Auteur V1 Authority / Provenance Closure Audit

**Audit baseline:** V1 closure branch derived from `main @ 2182da50f56df5a9bc139eb0b310cc18fd1d7e4a`.  
**Question:** Does V1 require a new provenance architecture, or only bounded reconciliation/qualification of existing authority paths?

## Conclusion

**No new provenance architecture is warranted for V1.** The current repository already has the mechanisms needed by the V1 promise: explicit owning-workflow acceptance, durable revisions/history, content/source hashes, currentness/staleness checks, fail-closed proposal/revision preconditions, accepted-source Expression composition, and ArtifactStore-backed accepted history for the contemporary Series vertical slice.

The remaining closure work is to qualify the promised paths together and keep unsupported scope outside the claim ceiling. Repository-wide normalization of every derived report/session/map into one lifecycle store is explicitly unnecessary.

## Classification

| Artifact family | Classification | V1 rationale / evidence seam |
| --- | --- | --- |
| StoryIdentity | `A — ALREADY_IMPLEMENTED` | explicit Story Discovery/Identity acceptance; Golden Path asserts no canonical mutation before acceptance |
| Blueprint / Structure | `A — ALREADY_IMPLEMENTED` | proposal selection and plans remain noncanonical; `RevisionService` owns explicit application with currentness preconditions |
| Chapter Structure / Outline | `B — SEMANTICALLY_EQUIVALENT` | existing accepted outline/provenance semantics and structural revision/impact paths satisfy the bounded V1 contract without one universal store |
| Scene Realization | `A — ALREADY_IMPLEMENTED` | ArtifactStore revision/currentness plus deterministic state/knowledge validation; V1 topology test exercises 60 accepted Scenes and restart |
| Scene Expression | `A — ALREADY_IMPLEMENTED` | source Scene revision/hash, candidate lifecycle, explicit acceptance, stale/review/divergence states, plus V1 structured boundary evidence service |
| Chapter Expression | `B — SEMANTICALLY_EQUIVALENT` | accepted Scene/transition dependencies and Chapter Expression lifecycle/reconciliation use their established dedicated store |
| Book Expression / Manuscript | `B — SEMANTICALLY_EQUIVALENT` | Book assembly/reconciliation/accepted-source rules and publishing have dedicated immutable/atomic contracts and release tests |
| Series Direction / accepted Series state | `B — SEMANTICALLY_EQUIVALENT / BOUNDED` | contemporary Series vertical-slice store delegates accepted artifact revision history to ArtifactStore; Global Map/Focus remain derived |
| Universe | `E — OUTSIDE AUTHORITY-COMPLETE V1 CLAIM` | optional supporting context is retained, but V1 does not claim a provenance-normalized Universe authoring vertical |
| Tutor sessions / Decision Cards / handoffs | `D — DERIVED_NOT_REQUIRED` | local/derived by contract; source fingerprints/currentness protect actionability without granting narrative authority |
| proposals / revision plans / previews / reassessment | `D — DERIVED_NOT_REQUIRED` | durable and currentness-bound where needed, but remain noncanonical until the existing owning authority action |
| maps / dashboards / reports | `D — DERIVED_NOT_REQUIRED` | rebuildable/read-only projections; persistence never grants authority |

## V1-specific closure additions

1. Structure proposal selection has been extracted into `ProposalReviewService`, shared by CLI and browser adapters.
2. `AuthorActionService` centralizes the browser's bounded decision-loop operations over the existing authority services.
3. `ExpressionBoundaryService` persists structured Realization evidence against draft prose candidates; blocking contradictions cannot be accepted and cannot mutate Scene Realization.
4. `recover_interrupted_revisions()` fail-closes plans stranded in `applying`: only hash-proven unchanged targets may return to `ready`; ambiguous changed targets become `failed`; no automatic authority replay occurs.
5. Provider failures use a stable provider-independent vocabulary; failure/retry behavior does not itself grant story authority.

## Residual evidence gates

These are qualification gates, not missing provenance architecture:

- exact-head CI across the supported OS/Python matrix;
- installed-wheel qualification;
- hermetic V1 author-journey bundle;
- opt-in live Anthropic and OpenAI adapter smoke using authorized credentials;
- bounded beginner owner dogfood of Workspace V2.

If any of those gates exposes a concrete authority defect, fix the smallest owning path. Do not respond by creating a second canon database or generic workflow engine.
